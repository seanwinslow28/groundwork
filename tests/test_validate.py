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
        # A complete provisioned package includes the #5 baseline citation
        # (Slice 1.4 provisioning gate).
        with tempfile.TemporaryDirectory() as d:
            skill = SKILL_OK.replace(
                "provisioned: yes",
                "provisioned: yes\nbaseline: memory/onboarding-baseline.md")
            _write_package(d, skill=skill)
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
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


MEM_OK = """---
provenance: observed
owner: Head of People
valid_at: 2026-07-15
review_by: 2099-10-15
source: The People team's Q2 onboarding tracker (12 hires)
---
# Onboarding baseline
Median time-to-day-one-ready: 4 business days.
"""


class TestMemory(unittest.TestCase):
    def test_valid_record_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            self.assertEqual([f for f in validate.check_memory(d) if f.level == "ERROR"], [])

    def test_bad_provenance_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("provenance: observed", "provenance: guessed"))
            self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                                for f in validate.check_memory(d)))

    def test_missing_owner_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("owner: Head of People\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "owner" in f.message
                                for f in validate.check_memory(d)))

    def test_unparseable_valid_at_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("valid_at: 2026-07-15", "valid_at: last Tuesday"))
            self.assertTrue(any(f.level == "ERROR" and "valid_at" in f.message
                                for f in validate.check_memory(d)))

    def test_confirmed_without_source_errors(self):
        with tempfile.TemporaryDirectory() as d:
            rec = MEM_OK.replace("provenance: observed", "provenance: confirmed").replace(
                "source: The People team's Q2 onboarding tracker (12 hires)\n", "")
            _write(d, "memory/x.md", rec)
            self.assertTrue(any(f.level == "ERROR" and "source" in f.message
                                for f in validate.check_memory(d)))

    def test_observed_without_source_warns(self):
        with tempfile.TemporaryDirectory() as d:
            rec = MEM_OK.replace("source: The People team's Q2 onboarding tracker (12 hires)\n", "")
            _write(d, "memory/x.md", rec)
            findings = validate.check_memory(d)
            self.assertTrue(any(f.level == "WARN" and "source" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "source" in f.message for f in findings))

    def test_supersession_fields_on_live_record_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("review_by: 2099-10-15",
                                                    "review_by: 2099-10-15\ninvalid_at: 2026-08-01"))
            self.assertTrue(any(f.level == "ERROR" and "live record" in f.message
                                for f in validate.check_memory(d)))

    def test_superseded_missing_pointer_errors(self):
        with tempfile.TemporaryDirectory() as d:
            rec = MEM_OK.replace("provenance: observed", "provenance: superseded")
            _write(d, "memory/x.md", rec)  # no invalid_at / superseded_by
            self.assertTrue(any(f.level == "ERROR" and "supersed" in f.message.lower()
                                for f in validate.check_memory(d)))

    def test_dangling_superseded_by_errors(self):
        with tempfile.TemporaryDirectory() as d:
            rec = MEM_OK.replace("provenance: observed", "provenance: superseded")
            rec = rec.replace("review_by: 2099-10-15",
                              "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/nope.md")
            _write(d, "memory/x.md", rec)
            self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message.lower()
                                for f in validate.check_memory(d)))

    def test_non_utf8_memory_record_errors_instead_of_crashing(self):
        # Codex review: unreadable records must yield findings, not exceptions.
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "memory/x.md", b"\xff\xfe")
            errs = [f for f in validate.check_memory(d) if f.level == "ERROR"]
            self.assertTrue(any("UTF-8" in f.message for f in errs))

    def test_non_scalar_owner_errors(self):
        # Codex review: a list-valued owner must not pass as non-blank.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md",
                   MEM_OK.replace("owner: Head of People", "owner:\n  - Head of People"))
            self.assertTrue(any(f.level == "ERROR" and "owner" in f.message
                                and "single value" in f.message
                                for f in validate.check_memory(d)))

    def test_unparseable_review_by_warns(self):
        # Codex review: nothing is silent — a present-but-unparseable review_by WARNs.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("review_by: 2099-10-15", "review_by: someday"))
            self.assertTrue(any(f.level == "WARN" and "review_by" in f.message
                                and "ISO date" in f.message
                                for f in validate.check_memory(d)))

    def test_non_scalar_superseded_by_errors(self):
        # Codex review: a list-valued superseded_by must not satisfy the invariant silently.
        with tempfile.TemporaryDirectory() as d:
            rec = MEM_OK.replace("provenance: observed", "provenance: superseded")
            rec = rec.replace("review_by: 2099-10-15",
                              "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by:\n  - memory/new.md")
            _write(d, "memory/x.md", rec)
            self.assertTrue(any(f.level == "ERROR" and "superseded_by" in f.message
                                and "single value" in f.message
                                for f in validate.check_memory(d)))

    def test_superseded_by_non_memory_target_errors(self):
        # Codex review: the pointer must resolve to a memory record, not just any file.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# not a memory record\n")
            rec = MEM_OK.replace("provenance: observed", "provenance: superseded")
            rec = rec.replace("review_by: 2099-10-15",
                              "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: README.md")
            _write(d, "memory/x.md", rec)
            self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message.lower()
                                for f in validate.check_memory(d)))

    def test_superseded_by_absolute_or_reentering_path_errors(self):
        # Codex review: the schema says repo-relative — an absolute path or a
        # ../ alias that re-enters the repo must not satisfy the pointer even
        # when it resolves to a real record.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/new.md", MEM_OK)
            for target in (os.path.join(d, "memory/new.md"),
                           "../%s/memory/new.md" % os.path.basename(d)):
                with self.subTest(target=target):
                    rec = MEM_OK.replace("provenance: observed", "provenance: superseded")
                    rec = rec.replace(
                        "review_by: 2099-10-15",
                        "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: %s" % target)
                    _write(d, "memory/x.md", rec)
                    self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message.lower()
                                        for f in validate.check_memory(d)))

    def test_symlinked_memory_record_errors_and_poisons_nothing(self):
        # Codex review: a symlinked record is an ERROR, and its external target
        # must not enter the reference allowlist.
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as outside:
                target = _write(outside, "escaped.md", MEM_OK)
                os.makedirs(os.path.join(d, "memory"))
                os.symlink(target, os.path.join(d, "memory", "x.md"))
                findings = validate.check_memory(d)
                self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                    for f in findings))

    def test_record_ref_rejects_drive_relative_and_unc_literals(self):
        # Codex review: Windows drive-relative ('C:..\\repo\\...') and UNC
        # literals dodge both the POSIX isabs and '../' checks; the guard is
        # literal and platform-independent, so unit-test the helper directly.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK)
            for ref in (r"C:..\%s\memory\x.md" % os.path.basename(d),
                        "C:memory/x.md",
                        r"\\server\share\memory\x.md",
                        "//server/share/memory/x.md"):
                with self.subTest(ref=ref):
                    self.assertIsNone(validate._record_ref_realpath(d, ref))
            self.assertIsNotNone(validate._record_ref_realpath(d, "memory/x.md"))

    def test_valid_supersession_chain_is_clean(self):
        # A well-formed supersession (both records exist, repo-relative
        # pointer) must produce zero ERRORs.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/new.md", MEM_OK)
            sup = MEM_OK.replace("provenance: observed", "provenance: superseded")
            sup = sup.replace("review_by: 2099-10-15",
                              "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/new.md")
            _write(d, "memory/old.md", sup)
            errs = [f for f in validate.check_memory(d) if f.level == "ERROR"]
            self.assertEqual(errs, [])

    def test_symlinked_record_cannot_be_a_supersession_target(self):
        # Codex review: a symlinked record is excluded from the allowlist, so
        # pointing superseded_by at it must be a dangling ERROR.
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as outside:
                target = _write(outside, "escaped.md", MEM_OK)
                os.makedirs(os.path.join(d, "memory"))
                os.symlink(target, os.path.join(d, "memory", "new.md"))
                sup = MEM_OK.replace("provenance: observed", "provenance: superseded")
                sup = sup.replace("review_by: 2099-10-15",
                                  "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/new.md")
                _write(d, "memory/old.md", sup)
                self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message.lower()
                                    for f in validate.check_memory(d)))

    def test_list_valued_review_by_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md",
                   MEM_OK.replace("review_by: 2099-10-15", "review_by:\n  - 2099-10-15"))
            self.assertTrue(any(f.level == "WARN" and "review_by" in f.message
                                and "ISO date" in f.message
                                for f in validate.check_memory(d)))


class TestMemoryIndex(unittest.TestCase):
    def test_live_record_not_in_index_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/_index.md", "# Index\n\n(no entries)\n")
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            warns = [f for f in validate.check_memory(d) if f.level == "WARN"]
            self.assertTrue(any("not in the index" in f.message for f in warns))

    def test_listed_live_record_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/_index.md", "# Index\n\n- [baseline](onboarding-baseline.md)\n")
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            self.assertFalse(any("not in the index" in f.message for f in validate.check_memory(d)))

    def test_superseded_record_not_in_index_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/_index.md", "# Index\n\n- [new](new.md)\n")
            _write(d, "memory/new.md", MEM_OK)
            sup = (MEM_OK.replace("provenance: observed", "provenance: superseded")
                   .replace("review_by: 2099-10-15",
                            "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/new.md"))
            _write(d, "memory/old.md", sup)
            self.assertFalse(any("not in the index" in f.message and "old.md" in f.path
                                 for f in validate.check_memory(d)))

    def test_non_utf8_index_errors_instead_of_crashing(self):
        # Codex review: an unreadable index must yield a finding, not an exception.
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "memory/_index.md", b"\xff\xfe")
            _write(d, "memory/x.md", MEM_OK)
            findings = validate.check_memory(d)
            self.assertTrue(any(f.level == "ERROR" and "UTF-8" in f.message for f in findings))

    def test_validate_wires_memory(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("provenance: observed", "provenance: guessed"))
            self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                                for f in validate.validate(d)))


class TestProvisioningGate(unittest.TestCase):
    def _pkg(self, d, skill):
        _write(d, "skills/onboarding-orchestration/SKILL.md", skill)
        _write(d, "skills/onboarding-orchestration/owner-card.md", CARD_OK)
        _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)

    def test_provisioned_without_baseline_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, SKILL_OK)  # provisioned: yes, no baseline field
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("baseline" in f.message for f in errs))

    def test_provisioned_with_missing_baseline_file_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, SKILL_OK.replace("provisioned: yes",
                                          "provisioned: yes\nbaseline: memory/nope.md"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("baseline" in f.message and "not found" in f.message for f in errs))

    def test_provisioned_with_baseline_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, SKILL_OK.replace("provisioned: yes",
                                          "provisioned: yes\nbaseline: memory/onboarding-baseline.md"))
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR" and "baseline" in f.message]
            self.assertEqual(errs, [])

    def test_draft_skill_needs_no_baseline(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, SKILL_OK.replace("provisioned: yes", "provisioned: no"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR" and "baseline" in f.message]
            self.assertEqual(errs, [])

    def test_non_scalar_baseline_errors(self):
        # Codex review: a list-valued baseline must not pass the gate.
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, SKILL_OK.replace(
                "provisioned: yes",
                "provisioned: yes\nbaseline:\n  - memory/onboarding-baseline.md"))
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("baseline" in f.message and "single value" in f.message
                                for f in errs))

    def test_baseline_must_resolve_to_a_memory_record(self):
        # Codex review: an existing file outside memory/ (or an escaping path)
        # does not satisfy the gate.
        for target in ("README.md", "../outside.md"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as d:
                _write(d, "README.md", "# not a memory record\n")
                self._pkg(d, SKILL_OK.replace("provisioned: yes",
                                              "provisioned: yes\nbaseline: %s" % target))
                errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
                self.assertTrue(any("baseline" in f.message and "not found" in f.message
                                    for f in errs))

    def test_absolute_or_reentering_baseline_errors(self):
        # Codex review: absolute paths and ../ aliases that re-enter the repo
        # must not satisfy the gate even when they resolve to a real record.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            for target in (os.path.join(d, "memory/onboarding-baseline.md"),
                           "../%s/memory/onboarding-baseline.md" % os.path.basename(d)):
                with self.subTest(target=target):
                    self._pkg(d, SKILL_OK.replace("provisioned: yes",
                                                  "provisioned: yes\nbaseline: %s" % target))
                    errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
                    self.assertTrue(any("baseline" in f.message and "not found" in f.message
                                        for f in errs))

    def test_symlinked_baseline_target_does_not_satisfy_the_gate(self):
        # Codex review: a symlinked "record" must not let an out-of-tree file
        # satisfy the provisioning gate.
        with tempfile.TemporaryDirectory() as d:
            with tempfile.TemporaryDirectory() as outside:
                target = _write(outside, "escaped.md", MEM_OK)
                os.makedirs(os.path.join(d, "memory"))
                os.symlink(target, os.path.join(d, "memory", "onboarding-baseline.md"))
                self._pkg(d, SKILL_OK.replace(
                    "provisioned: yes",
                    "provisioned: yes\nbaseline: memory/onboarding-baseline.md"))
                errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
                self.assertTrue(any("baseline" in f.message and "not found" in f.message
                                    for f in errs))


class TestMemoryDiff(unittest.TestCase):
    def test_body_frozen(self):
        new = MEM_OK.replace("Median time-to-day-one-ready: 4 business days.", "Median: 2 days.")
        self.assertTrue(any(f.level == "ERROR" and "body" in f.message
                            for f in validate.check_memory_diff(MEM_OK, new, "m.md")))

    def test_valid_at_frozen(self):
        new = MEM_OK.replace("valid_at: 2026-07-15", "valid_at: 2026-07-16")
        self.assertTrue(any(f.level == "ERROR" and "valid_at" in f.message
                            for f in validate.check_memory_diff(MEM_OK, new, "m.md")))

    def test_provenance_forward_ok(self):
        new = MEM_OK.replace("provenance: observed", "provenance: confirmed")
        self.assertEqual([f for f in validate.check_memory_diff(MEM_OK, new, "m.md")
                          if "provenance" in f.message], [])

    def test_provenance_downgrade_errors(self):
        old = MEM_OK.replace("provenance: observed", "provenance: confirmed")
        new = MEM_OK.replace("provenance: observed", "provenance: inferred")
        self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                            for f in validate.check_memory_diff(old, new, "m.md")))

    def test_source_append_ok(self):
        new = MEM_OK.replace("source: The People team's Q2 onboarding tracker (12 hires)",
                             "source: The People team's Q2 onboarding tracker (12 hires); plus the IT log")
        self.assertEqual([f for f in validate.check_memory_diff(MEM_OK, new, "m.md")
                          if "source" in f.message], [])

    def test_source_alteration_errors(self):
        new = MEM_OK.replace("source: The People team's Q2 onboarding tracker (12 hires)",
                             "source: A different tracker")
        self.assertTrue(any(f.level == "ERROR" and "source" in f.message
                            for f in validate.check_memory_diff(MEM_OK, new, "m.md")))

    def test_source_list_append_ok(self):
        # Regression (plan fix): appending a NEW list entry is an append.
        new = MEM_OK.replace(
            "source: The People team's Q2 onboarding tracker (12 hires)",
            "source:\n  - The People team's Q2 onboarding tracker (12 hires)\n  - The IT provisioning log")
        old = MEM_OK.replace(
            "source: The People team's Q2 onboarding tracker (12 hires)",
            "source:\n  - The People team's Q2 onboarding tracker (12 hires)")
        self.assertEqual([f for f in validate.check_memory_diff(old, new, "m.md")
                          if "source" in f.message], [])

    def test_source_entry_removal_errors(self):
        # Regression (plan fix): dropping an existing entry is not an append.
        old = MEM_OK.replace(
            "source: The People team's Q2 onboarding tracker (12 hires)",
            "source:\n  - The People team's Q2 onboarding tracker (12 hires)\n  - The IT provisioning log")
        new = MEM_OK.replace(
            "source: The People team's Q2 onboarding tracker (12 hires)",
            "source:\n  - The People team's Q2 onboarding tracker (12 hires)")
        self.assertTrue(any(f.level == "ERROR" and "source" in f.message
                            for f in validate.check_memory_diff(old, new, "m.md")))

    def test_source_earlier_entry_alteration_errors(self):
        # Regression (plan fix): only the FINAL existing entry may be extended
        # in place; earlier entries are frozen.
        old = MEM_OK.replace(
            "source: The People team's Q2 onboarding tracker (12 hires)",
            "source:\n  - The People team's Q2 onboarding tracker (12 hires)\n  - The IT provisioning log")
        new = MEM_OK.replace(
            "source: The People team's Q2 onboarding tracker (12 hires)",
            "source:\n  - The People team's Q2 onboarding tracker (12 hires); edited\n  - The IT provisioning log")
        self.assertTrue(any(f.level == "ERROR" and "source" in f.message
                            for f in validate.check_memory_diff(old, new, "m.md")))

    def test_supersession_field_set_once(self):
        old = (MEM_OK.replace("provenance: observed", "provenance: superseded")
               .replace("review_by: 2099-10-15",
                        "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/new.md"))
        new = old.replace("invalid_at: 2026-08-01", "invalid_at: 2026-09-01")
        self.assertTrue(any(f.level == "ERROR" and "invalid_at" in f.message
                            for f in validate.check_memory_diff(old, new, "m.md")))

    def test_unchanged_record_clean(self):
        self.assertEqual(validate.check_memory_diff(MEM_OK, MEM_OK, "m.md"), [])


if __name__ == "__main__":
    unittest.main()
