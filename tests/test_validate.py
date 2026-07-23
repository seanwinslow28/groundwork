import ast
import datetime
import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent


class TestFrontmatter(unittest.TestCase):
    def test_scalars_are_raw_strings_no_coercion(self):
        text = "---\nowner: Ada\ncount: 7\nswitch: yes\n---\nbody\n"
        data, findings = validate.parse_frontmatter(text)
        self.assertEqual(data["owner"], "Ada")
        self.assertEqual(data["count"], "7")     # NOT int 7
        self.assertEqual(data["switch"], "yes")   # NOT bool True (Norway problem)
        self.assertEqual(findings, [])

    def test_list_values(self):
        text = "---\nallowed:\n  - read\n  - write\n---\n"
        data, findings = validate.parse_frontmatter(text)
        self.assertEqual(data["allowed"], ["read", "write"])
        self.assertEqual(findings, [])

    def test_value_with_colon_keeps_full_value(self):
        text = "---\nsource: https://example.com/x\n---\n"
        data, _ = validate.parse_frontmatter(text)
        self.assertEqual(data["source"], "https://example.com/x")

    def test_unsupported_syntax_errors_with_line(self):
        text = "---\nowner: Ada\n\tnested: bad\n---\n"
        _, findings = validate.parse_frontmatter(text, "f.md")
        self.assertTrue(any(f.level == "ERROR" and f.line == 3 for f in findings))

    def test_unclosed_block_errors(self):
        text = "---\nowner: Ada\nbody with no close\n"
        _, findings = validate.parse_frontmatter(text, "f.md")
        self.assertTrue(any("never closed" in f.message for f in findings))

    def test_duplicate_key_errors_and_keeps_first_value(self):
        text = "---\nowner: Ada\nowner: Grace\n---\n"
        data, findings = validate.parse_frontmatter(text, "f.md")
        self.assertEqual(data["owner"], "Ada")
        self.assertTrue(any(f.level == "ERROR" and "duplicate" in f.message
                            and "owner" in f.message for f in findings))


class TestZeroDep(unittest.TestCase):
    def test_only_stdlib_imports(self):
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections", "pathlib", "datetime"}
        tree = ast.parse((REPO / "scripts" / "validate.py").read_text())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    mods.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        extra = mods - allowed
        self.assertEqual(extra, set(), "non-stdlib imports: %s" % extra)


class TestSecrets(unittest.TestCase):
    def test_aws_key_errors(self):
        # AWS's own documentation example key — safe to hardcode.
        findings = validate.check_secrets("key = AKIAIOSFODNN7EXAMPLE\n", "f.md")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_private_key_header_errors(self):
        findings = validate.check_secrets("-----BEGIN OPENSSH PRIVATE KEY-----\n", "f.md")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_clean_text_no_findings(self):
        self.assertEqual(validate.check_secrets("owner: Ada\n", "f.md"), [])

    def test_high_entropy_warns_not_errors(self):
        blob = "TOKEN=" + "aB3dE5fH7jK9mN1pQ3sU5wX7zA9cE1gI3kM5oQ7s"  # 40 chars
        findings = validate.check_entropy(blob + "\n", "f.md")
        self.assertTrue(all(f.level == "WARN" for f in findings))


class TestBudget(unittest.TestCase):
    def test_small_file_no_findings(self):
        self.assertEqual(validate.check_context_budget("f.md", b"hello"), [])

    def test_warn_threshold(self):
        payload = b"x" * (20_000 * 4)  # ~20k est. tokens
        findings = validate.check_context_budget("f.md", payload)
        self.assertTrue(any(f.level == "WARN" for f in findings))
        self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_error_threshold(self):
        payload = b"x" * (50_000 * 4)  # ~50k est. tokens
        findings = validate.check_context_budget("f.md", payload)
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_est_tokens(self):
        self.assertEqual(validate.est_tokens(4000), 1000)


class TestGate(unittest.TestCase):
    def test_missing_root_errors(self):
        findings = validate.validate(str(REPO / "tests" / "fixtures" / "no-such-dir"))
        self.assertTrue(any(f.level == "ERROR" and "not a directory" in f.message
                            for f in findings))

    def test_clean_stub_fixture_passes(self):
        findings = validate.validate(str(REPO / "tests" / "fixtures" / "stub"))
        errors = [f for f in findings if f.level == "ERROR"]
        self.assertEqual(errors, [], "unexpected errors: %s" % errors)


def _write(d, relpath, text):
    p = os.path.join(d, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def _write_bytes(d, relpath, data):
    p = os.path.join(d, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(data)
    return p


AUTOMATE_OK = """---
activity: Onboarding orchestration
motion: automate
score_repetition: high
score_risk: low
score_judgment: low
score_company_specificity: medium
score_market_maturity: high
work_type: routing
accountable_owner: Head of People
substrate: HRIS + IT tracker
shape: single-agent
gate_inputs: start date, role, manager, access needs
gate_output: completed onboarding checklist
gate_standard: accounts + equipment + schedule ready before start
gate_source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
gate_exception_path: non-standard role pauses to Head of People
gate_error_cost: a late day-one, recoverable, not dangerous
gate_owner: Head of People
gate_review_gate: hiring manager confirms on day one
---
# Onboarding orchestration
"""


class TestDeepRecord(unittest.TestCase):
    def test_valid_automate_record_clean(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            self.assertEqual(validate.check_deep_record(p, d), [])

    def test_automation_missing_gate_field_errors(self):
        with tempfile.TemporaryDirectory() as d:
            bad = AUTOMATE_OK.replace("gate_review_gate: hiring manager confirms on day one\n", "")
            p = _write(d, "ontologies/people-hr/x.md", bad)
            errs = [f for f in validate.check_deep_record(p, d) if f.level == "ERROR"]
            self.assertTrue(any("gate_review_gate" in f.message for f in errs))

    def test_gate_na_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            bad = AUTOMATE_OK.replace("gate_error_cost: a late day-one, recoverable, not dangerous",
                                      "gate_error_cost: N/A")
            p = _write(d, "ontologies/people-hr/x.md", bad)
            errs = [f for f in validate.check_deep_record(p, d) if f.level == "ERROR"]
            self.assertTrue(any("N/A" in f.message and "gate_error_cost" in f.message for f in errs))

    def test_invalid_motion_errors(self):
        with tempfile.TemporaryDirectory() as d:
            bad = AUTOMATE_OK.replace("motion: automate", "motion: teleport")
            p = _write(d, "ontologies/people-hr/x.md", bad)
            errs = [f for f in validate.check_deep_record(p, d) if f.level == "ERROR"]
            self.assertTrue(any("motion" in f.message for f in errs))

    def test_list_valued_enum_errors_not_crashes(self):
        # Codex review: 'motion:' + '- automate' parses as a list; membership
        # tests on sets must not raise TypeError.
        with tempfile.TemporaryDirectory() as d:
            bad = AUTOMATE_OK.replace("motion: automate", "motion:\n  - automate")
            p = _write(d, "ontologies/people-hr/x.md", bad)
            errs = [f for f in validate.check_deep_record(p, d) if f.level == "ERROR"]
            self.assertTrue(any("motion" in f.message and "single value" in f.message
                                for f in errs))

    def test_empty_list_field_is_missing(self):
        # 'work_type:' with no items parses as [] — that is a missing field.
        with tempfile.TemporaryDirectory() as d:
            bad = AUTOMATE_OK.replace("work_type: routing", "work_type:")
            p = _write(d, "ontologies/people-hr/x.md", bad)
            errs = [f for f in validate.check_deep_record(p, d) if f.level == "ERROR"]
            self.assertTrue(any("missing 'work_type'" in f.message for f in errs))

    def test_blank_free_text_field_errors_on_automation(self):
        # Codex review: 'accountable_owner:' (blank) parses as [] and must not
        # pass an automation-path record.
        with tempfile.TemporaryDirectory() as d:
            bad = AUTOMATE_OK.replace("accountable_owner: Head of People\n", "accountable_owner:\n")
            bad = bad.replace("substrate: HRIS + IT tracker\n", "substrate:\n")
            p = _write(d, "ontologies/people-hr/x.md", bad)
            errs = [f for f in validate.check_deep_record(p, d) if f.level == "ERROR"]
            self.assertTrue(any("missing 'accountable_owner'" in f.message for f in errs))
            self.assertTrue(any("missing 'substrate'" in f.message for f in errs))

    def test_non_automation_incomplete_is_warn_not_error(self):
        with tempfile.TemporaryDirectory() as d:
            rec = "---\nactivity: Comp review\nmotion: hire\n---\n# x\n"  # missing common core
            p = _write(d, "ontologies/people-hr/x.md", rec)
            findings = validate.check_deep_record(p, d)
            self.assertTrue(any(f.level == "WARN" for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))


class TestExecTable(unittest.TestCase):
    TABLE = (
        "# People/HR — executive view\n\n"
        "| Activity | Direction | Deep record |\n"
        "|---|---|---|\n"
        "| Onboarding orchestration | down | [deep record](onboarding-orchestration.md) |\n"
        "| Headcount planning | up | — |\n"
    )

    def test_parses_rows(self):
        rows = validate.parse_exec_table(self.TABLE)
        self.assertEqual(len(rows), 2)
        act, direction, link, _ = rows[0]
        self.assertEqual(act, "Onboarding orchestration")
        self.assertEqual(direction, "down")
        self.assertEqual(link, "onboarding-orchestration.md")

    def test_row_without_link(self):
        _, direction, link, _ = validate.parse_exec_table(self.TABLE)[1]
        self.assertEqual(direction, "up")
        self.assertIsNone(link)

    def test_no_table_returns_empty(self):
        self.assertEqual(validate.parse_exec_table("# just prose\n"), [])


EXEC_OK = (
    "# People/HR — executive view\n\n"
    "| Activity | Direction | Deep record |\n"
    "|---|---|---|\n"
    "| Onboarding orchestration | down | [deep record](onboarding-orchestration.md) |\n"
    "| Headcount planning | up | — |\n"
)


class TestOntology(unittest.TestCase):
    def test_clean_function_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            self.assertEqual([f for f in validate.check_ontology(d) if f.level == "ERROR"], [])

    def test_missing_exec_view_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            errs = [f for f in validate.check_ontology(d) if f.level == "ERROR"]
            self.assertTrue(any("executive view" in f.message for f in errs))

    def test_bad_direction_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md",
                   EXEC_OK.replace("| Headcount planning | up |", "| Headcount planning | sideways |"))
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            errs = [f for f in validate.check_ontology(d) if f.level == "ERROR"]
            self.assertTrue(any("Direction" in f.message for f in errs))

    def test_gitignored_deep_record_is_not_checked(self):
        # Codex review: the semantic checks must honor the same ignore set as
        # the generic walker.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "ontologies/people-hr/draft-notes.md", "---\nmotion: teleport\n---\n")
            findings = validate.check_ontology(d, ignore={"draft-*.md"})
            self.assertFalse(any("draft-notes" in f.path for f in findings))

    def test_unlisted_deep_record_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "ontologies/people-hr/offboarding.md", AUTOMATE_OK)  # not in exec view
            warns = [f for f in validate.check_ontology(d) if f.level == "WARN"]
            self.assertTrue(any("not listed" in f.message for f in warns))


class TestGitignore(unittest.TestCase):
    def test_gitignored_file_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, ".gitignore"), "w").write(".env\n*.log\n")
            open(os.path.join(d, ".env"), "w").write("SECRET=AKIAIOSFODNN7EXAMPLE\n")
            open(os.path.join(d, "app.log"), "w").write("AKIAIOSFODNN7EXAMPLE\n")
            open(os.path.join(d, "keep.md"), "w").write("# clean\n")
            findings = validate.validate(d)
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])


class TestLinks(unittest.TestCase):
    def test_broken_relative_link_errors(self):
        findings = validate.validate(str(REPO / "tests" / "fixtures" / "broken"))
        self.assertTrue(any(f.level == "ERROR" and "broken" in f.message.lower()
                            for f in findings))

    def test_stub_fixture_valid_link_ok(self):
        # good.md -> linked.md resolves; no link ERRORs in the clean stub.
        findings = validate.validate(str(REPO / "tests" / "fixtures" / "stub"))
        self.assertFalse(any("broken" in f.message.lower() for f in findings))

    def test_external_links_skipped(self):
        findings = validate.check_links(
            str(REPO / "README.md"),
            "see [x](https://example.com) and [y](#anchor)",
            str(REPO))
        self.assertEqual(findings, [])


SKILL_OK = """---
name: onboarding-orchestration
description: Provision a new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Onboarding orchestration
"""

CARD_OK = """---
owner: Head of People
backup_owner: People Ops Lead
job: Provision every new hire before day one
action_class: external-side-effect
allowed_actions: create accounts; order standard equipment; send the day-one schedule
proposed_only_actions: grant non-standard system access
forbidden_actions: approve compensation; sign offers; delete employee records
pause_condition: HRIS or IT tracker unreachable, or intake data missing
retirement_condition: onboarding moves to a dedicated HRIS-native workflow the team trusts
source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
review_cadence: monthly
known_failure_modes: none observed yet
last_reviewed: 2026-07-20
next_review: 2099-08-20
success_standard: Every new hire day-one-ready before start, against the pre-provisioning baseline
evidence_required: The completed checklist with per-item timestamps and the provisioning log
sources_must_not_use: Personal email or chat threads as a source of truth for access grants
review_sample: One onboarding per week spot-checked by the hiring manager
---
# Owner's Card — Onboarding orchestration
"""


def _drop_field(text, field):
    return "".join(
        line for line in text.splitlines(keepends=True)
        if not line.startswith(field + ":")
    )


def _replace_field(text, field, value):
    old_line = next(
        line for line in text.splitlines(keepends=True)
        if line.startswith(field + ":")
    )
    return text.replace(old_line, "%s: %s\n" % (field, value), 1)


def _replace_field_with_list(text, field, value):
    old_line = next(
        line for line in text.splitlines(keepends=True)
        if line.startswith(field + ":")
    )
    return text.replace(old_line, "%s:\n- %s\n" % (field, value), 1)


def _write_package(d, skill=SKILL_OK, card=CARD_OK, ont=AUTOMATE_OK,
                   name="onboarding-orchestration"):
    _write(d, "skills/%s/SKILL.md" % name, skill)
    if card is not None:
        _write(d, "skills/%s/owner-card.md" % name, card)
    _write(d, "ontologies/people-hr/onboarding-orchestration.md", ont)


class TestOwnerCard(unittest.TestCase):
    def test_complete_provisioned_card_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(d)
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertEqual(errs, [])

    def test_each_missing_spine_field_errors_when_provisioned(self):
        for field in validate.CARD_REQUIRED:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                _write_package(d, card=_drop_field(CARD_OK, field))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any(field in f.message for f in errors))

    def test_each_blank_spine_field_errors_when_provisioned(self):
        for field in validate.CARD_REQUIRED:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                _write_package(d, card=_replace_field(CARD_OK, field, ""))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any(field in f.message for f in errors))

    def test_missing_spine_field_warns_while_drafting(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "provisioned", "no")
            _write_package(d, skill=skill, card=_drop_field(CARD_OK, "pause_condition"))
            findings = validate.check_owner_cards(d)
            matching = [f for f in findings if "pause_condition" in f.message]
            self.assertTrue(any(f.level == "WARN" for f in matching))
            self.assertFalse(any(f.level == "ERROR" for f in matching))

    def test_non_scalar_spine_field_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(
                d, card=_replace_field_with_list(CARD_OK, "owner", "Head of People"))
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("owner" in f.message and "single value" in f.message
                                for f in errors))

    def test_missing_owner_card_errors_when_provisioned(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(d, card=None)
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "ERROR" and "no Owner's Card" in f.message
                                for f in findings))

    def test_missing_owner_card_warns_while_drafting(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "provisioned", "no")
            _write_package(d, skill=skill, card=None)
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "WARN" and "no Owner's Card" in f.message
                                for f in findings))

    def test_each_track2_field_errors_for_each_track2_class(self):
        for action_class in validate.TRACK2_CLASSES:
            for field in validate.CARD_TRACK2:
                with self.subTest(action_class=action_class, field=field):
                    with tempfile.TemporaryDirectory() as d:
                        skill = _replace_field(SKILL_OK, "action_class", action_class)
                        card = _replace_field(CARD_OK, "action_class", action_class)
                        _write_package(d, skill=skill, card=_drop_field(card, field))
                        errors = [f for f in validate.check_owner_cards(d)
                                  if f.level == "ERROR"]
                        self.assertTrue(any(field in f.message for f in errors))

    def test_each_track2_field_warns_for_each_track1_class(self):
        track1_classes = validate.ACTION_CLASSES - validate.TRACK2_CLASSES
        for action_class in track1_classes:
            for field in validate.CARD_TRACK2:
                with self.subTest(action_class=action_class, field=field):
                    with tempfile.TemporaryDirectory() as d:
                        skill = _replace_field(SKILL_OK, "action_class", action_class)
                        card = _replace_field(CARD_OK, "action_class", action_class)
                        _write_package(d, skill=skill, card=_drop_field(card, field))
                        findings = validate.check_owner_cards(d)
                        matching = [f for f in findings if field in f.message]
                        self.assertTrue(any(f.level == "WARN" for f in matching))
                        self.assertFalse(any(f.level == "ERROR" for f in matching))

    def test_track2_field_warns_while_drafting(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "provisioned", "no")
            _write_package(d, skill=skill,
                           card=_drop_field(CARD_OK, "evidence_required"))
            findings = validate.check_owner_cards(d)
            matching = [f for f in findings if "evidence_required" in f.message]
            self.assertTrue(any(f.level == "WARN" for f in matching))
            self.assertFalse(any(f.level == "ERROR" for f in matching))

    def test_overdue_next_review_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            _write_package(
                d, card=_replace_field(CARD_OK, "next_review", yesterday.isoformat()))
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "WARN" and "next_review" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "next_review" in f.message for f in findings))

    def test_stale_last_reviewed_warns_not_errors_for_high_risk(self):
        with tempfile.TemporaryDirectory() as d:
            old_date = datetime.date.today() - datetime.timedelta(days=91)
            future_date = datetime.date.today() + datetime.timedelta(days=30)
            skill = _replace_field(SKILL_OK, "action_class", "high-risk")
            card = _replace_field(CARD_OK, "action_class", "high-risk")
            card = _replace_field(card, "last_reviewed", old_date.isoformat())
            card = _replace_field(card, "next_review", future_date.isoformat())
            _write_package(d, skill=skill, card=card)
            findings = validate.check_owner_cards(d)
            matching = [f for f in findings if "last_reviewed" in f.message]
            self.assertTrue(any(f.level == "WARN" for f in matching))
            self.assertFalse(any(f.level == "ERROR" for f in matching))

    def test_freshness_boundaries_do_not_warn(self):
        with tempfile.TemporaryDirectory() as d:
            today = datetime.date.today()
            boundary = today - datetime.timedelta(days=90)
            card = _replace_field(CARD_OK, "last_reviewed", boundary.isoformat())
            card = _replace_field(card, "next_review", today.isoformat())
            _write_package(d, card=card)
            freshness = [f for f in validate.check_owner_cards(d)
                         if "freshness" in f.message]
            self.assertEqual(freshness, [])

    def test_invalid_review_dates_error_when_provisioned(self):
        for field in ("last_reviewed", "next_review"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                _write_package(d, card=_replace_field(CARD_OK, field, "not-a-date"))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any(field in f.message and "ISO date" in f.message
                                    for f in errors))

    def test_non_canonical_iso_review_dates_error(self):
        for value in ("20260720", "2026-W30-1"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as d:
                _write_package(
                    d, card=_replace_field(CARD_OK, "next_review", value))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any("next_review" in f.message
                                    and "ISO date" in f.message
                                    for f in errors))

    def test_invalid_review_date_warns_while_drafting(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "provisioned", "no")
            _write_package(
                d, skill=skill,
                card=_replace_field(CARD_OK, "next_review", "not-a-date"))
            matching = [f for f in validate.check_owner_cards(d)
                        if "next_review" in f.message and "ISO date" in f.message]
            self.assertTrue(any(f.level == "WARN" for f in matching))
            self.assertFalse(any(f.level == "ERROR" for f in matching))

    def test_future_last_reviewed_errors_when_provisioned(self):
        with tempfile.TemporaryDirectory() as d:
            future = datetime.date.today() + datetime.timedelta(days=1)
            _write_package(
                d, card=_replace_field(CARD_OK, "last_reviewed", future.isoformat()))
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("last_reviewed" in f.message and "future" in f.message
                                for f in errors))

    def test_required_skill_metadata_missing_or_non_scalar_errors(self):
        for field, value in (
                ("name", "onboarding-orchestration"),
                ("description", "Provision new hires before day one"),
                ("provisioned", "yes"),
                ("action_class", "external-side-effect"),
                ("ontology", "ontologies/people-hr/onboarding-orchestration.md")):
            variants = (
                _drop_field(SKILL_OK, field),
                _replace_field(SKILL_OK, field, ""),
                _replace_field_with_list(SKILL_OK, field, value),
            )
            for variant in variants:
                with self.subTest(field=field, variant=variant):
                    with tempfile.TemporaryDirectory() as d:
                        _write_package(d, skill=variant)
                        errors = [f for f in validate.check_owner_cards(d)
                                  if f.level == "ERROR"]
                        self.assertTrue(any(field in f.message for f in errors))

    def test_skill_name_must_match_package_directory(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "name", "different-name")
            _write_package(d, skill=skill)
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("name" in f.message and "directory" in f.message
                                for f in errors))

    def test_invalid_provisioned_value_errors_and_does_not_fail_open(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "provisioned", "yse")
            _write_package(d, skill=skill, card=_drop_field(CARD_OK, "owner"))
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("provisioned" in f.message for f in errors))

    def test_invalid_skill_action_class_errors(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "action_class", "side-effect-ish")
            _write_package(d, skill=skill)
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("action_class" in f.message for f in errors))

    def test_gitignored_skill_package_is_not_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".gitignore", "ignored-skill\n")
            _write_package(d, name="ignored-skill", card=None)
            findings = validate.validate(d)
            self.assertFalse(any("ignored-skill" in f.path for f in findings))

    def test_gitignored_package_artifacts_are_treated_as_missing(self):
        for ignored, expected in (
                ("SKILL.md", "SKILL.md"),
                ("owner-card.md", "no Owner's Card"),
                ("onboarding-orchestration.md", "ontology reference")):
            with self.subTest(ignored=ignored), tempfile.TemporaryDirectory() as d:
                _write(d, ".gitignore", ignored + "\n")
                _write_package(d)
                findings = validate.check_owner_cards(
                    d, validate.load_gitignore(d))
                self.assertTrue(any(f.level == "ERROR"
                                    and expected in f.message
                                    for f in findings))

    def test_package_directory_without_skill_errors(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "skills", "empty-package"))
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("empty-package" in f.path and "SKILL.md" in f.message
                                for f in errors))

    def test_symlinked_skills_directory_errors_without_following_it(self):
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as outside:
                _write(outside, "escaped/SKILL.md", SKILL_OK)
                os.symlink(os.path.join(outside, "escaped"),
                           os.path.join(d, "skills"))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any(f.path == "skills" and "symlink" in f.message
                                    for f in errors))

    def test_symlinked_package_directory_errors_without_following_it(self):
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as outside:
                os.makedirs(os.path.join(d, "skills"))
                _write(outside, "escaped/SKILL.md", SKILL_OK)
                os.symlink(os.path.join(outside, "escaped"),
                           os.path.join(d, "skills", "escaped"))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any("skills/escaped" in f.path
                                    and "symlink" in f.message for f in errors))

    def test_symlinked_skill_or_card_errors_without_reading_target(self):
        for component in ("SKILL.md", "owner-card.md"):
            with self.subTest(component=component):
                with tempfile.TemporaryDirectory() as d:
                    with tempfile.TemporaryDirectory() as outside:
                        if component == "SKILL.md":
                            os.makedirs(os.path.join(
                                d, "skills", "onboarding-orchestration"))
                            target = _write(
                                outside, "escaped.md",
                                "---\nmarker_without_colon\n---\n")
                            os.symlink(
                                target,
                                os.path.join(
                                    d, "skills", "onboarding-orchestration",
                                    component))
                        else:
                            _write_package(d, card=None)
                            target = _write(outside, "escaped.md", CARD_OK)
                            os.symlink(
                                target,
                                os.path.join(
                                    d, "skills", "onboarding-orchestration",
                                    component))
                        findings = validate.check_owner_cards(d)
                        self.assertTrue(any(f.level == "ERROR"
                                            and component in f.path
                                            and "symlink" in f.message
                                            for f in findings))
                        self.assertFalse(any(
                            "marker_without_colon" in f.message
                            for f in findings))

    def test_non_utf8_package_files_error_instead_of_crashing(self):
        for component, relpath in (
                ("skill", "skills/onboarding-orchestration/SKILL.md"),
                ("card", "skills/onboarding-orchestration/owner-card.md"),
                ("ontology", "ontologies/people-hr/onboarding-orchestration.md")):
            with self.subTest(component=component), tempfile.TemporaryDirectory() as d:
                _write_package(d)
                _write_bytes(d, relpath, b"\xff\xfe")
                errors = [f for f in validate.validate(d)
                          if f.level == "ERROR"]
                self.assertTrue(any(relpath in f.path and "UTF-8" in f.message
                                    for f in errors))

    def test_nul_in_ontology_reference_errors_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(
                SKILL_OK, "ontology", "ontologies/people-hr/\x00.md")
            _write_package(d, skill=skill)
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("ontology reference" in f.message
                                and "NUL" in f.message for f in errors))

    def test_duplicate_critical_skill_and_card_fields_error(self):
        skill = _replace_field(
            SKILL_OK, "provisioned", "yes\nprovisioned: no")
        card = _replace_field(
            CARD_OK, "owner", "Head of People\nowner: Someone Else")
        with tempfile.TemporaryDirectory() as d:
            _write_package(d, skill=skill, card=card)
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("duplicate" in f.message
                                and "provisioned" in f.message for f in errors))
            self.assertTrue(any("duplicate" in f.message
                                and "owner" in f.message for f in errors))


class TestCardDrift(unittest.TestCase):
    def test_owner_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(
                d, card=_replace_field(CARD_OK, "owner", "Someone Else"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("owner" in f.message and "ontology" in f.message for f in errs))

    def test_action_class_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(
                d, card=_replace_field(CARD_OK, "action_class", "read-only"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("action_class" in f.message for f in errs))

    def test_missing_or_non_scalar_card_action_class_errors(self):
        variants = (
            _drop_field(CARD_OK, "action_class"),
            _replace_field_with_list(
                CARD_OK, "action_class", "external-side-effect"),
        )
        for card in variants:
            with self.subTest(card=card), tempfile.TemporaryDirectory() as d:
                _write_package(d, card=card)
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any("card action_class" in f.message
                                    for f in errors))

    def test_invalid_card_action_class_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(
                d, card=_replace_field(CARD_OK, "action_class", "side-effect-ish"))
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("card action_class" in f.message for f in errors))

    def test_source_of_truth_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(
                d, card=_replace_field(
                    CARD_OK, "source_of_truth", "A spreadsheet"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("source_of_truth" in f.message for f in errs))

    def test_unresolved_ontology_ref_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write_package(
                d, skill=_replace_field(
                    SKILL_OK, "ontology", "ontologies/people-hr/missing.md"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("ontology reference" in f.message for f in errs))

    def test_ontology_ref_must_stay_under_ontologies(self):
        with tempfile.TemporaryDirectory() as d:
            outside = _write(d, "outside.md", AUTOMATE_OK)
            skill = _replace_field(SKILL_OK, "ontology", outside)
            _write_package(d, skill=skill)
            errors = [f for f in validate.check_owner_cards(d)
                      if f.level == "ERROR"]
            self.assertTrue(any("ontology reference" in f.message
                                and "under ontologies" in f.message
                                for f in errors))

    def test_referenced_ontology_requires_drift_source_fields(self):
        for field in ("accountable_owner", "gate_source_of_truth"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                _write_package(d, ont=_drop_field(AUTOMATE_OK, field))
                errors = [f for f in validate.check_owner_cards(d)
                          if f.level == "ERROR"]
                self.assertTrue(any(field in f.message for f in errors))

    def test_validate_wires_card_checks(self):
        with tempfile.TemporaryDirectory() as d:
            skill = _replace_field(SKILL_OK, "name", "x")
            _write_package(
                d, name="x", skill=skill,
                card=_replace_field(CARD_OK, "owner", "Wrong"))
            errs = [f for f in validate.validate(d) if f.level == "ERROR"]
            self.assertTrue(any("owner" in f.message for f in errs))


if __name__ == "__main__":
    unittest.main()
