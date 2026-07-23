import ast
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


class TestOwnerCard(unittest.TestCase):
    def _pkg(self, d, skill=SKILL_OK, card=CARD_OK):
        _write(d, "skills/onboarding-orchestration/SKILL.md", skill)
        if card is not None:
            _write(d, "skills/onboarding-orchestration/owner-card.md", card)
        # the ontology the drift check will look for (present so Task 3 stays green too)
        _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)

    def test_complete_provisioned_card_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d)
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertEqual(errs, [])

    def test_missing_spine_field_errors_when_provisioned(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace("pause_condition: HRIS or IT tracker unreachable, or intake data missing\n", ""))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("pause_condition" in f.message for f in errs))

    def test_blank_required_field_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace("backup_owner: People Ops Lead", "backup_owner:"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("backup_owner" in f.message for f in errs))

    def test_track2_trio_required_at_external_side_effect(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace("review_sample: One onboarding per week spot-checked by the hiring manager\n", ""))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("review_sample" in f.message for f in errs))

    def test_track2_blank_is_warn_for_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            skill = SKILL_OK.replace("action_class: external-side-effect", "action_class: read-only")
            card = (CARD_OK.replace("action_class: external-side-effect", "action_class: read-only")
                    .replace("review_sample: One onboarding per week spot-checked by the hiring manager\n", ""))
            self._pkg(d, skill=skill, card=card)
            findings = validate.check_owner_cards(d)
            self.assertFalse(any(f.level == "ERROR" and "review_sample" in f.message for f in findings))
            self.assertTrue(any(f.level == "WARN" and "review_sample" in f.message for f in findings))

    def test_overdue_next_review_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace("next_review: 2099-08-20", "next_review: 2020-01-01"))
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "WARN" and "next_review" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "next_review" in f.message for f in findings))


class TestCardDrift(unittest.TestCase):
    def _pkg(self, d, skill=SKILL_OK, card=CARD_OK, ont=AUTOMATE_OK):
        _write(d, "skills/onboarding-orchestration/SKILL.md", skill)
        _write(d, "skills/onboarding-orchestration/owner-card.md", card)
        _write(d, "ontologies/people-hr/onboarding-orchestration.md", ont)

    def test_owner_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace("owner: Head of People", "owner: Someone Else"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("owner" in f.message and "ontology" in f.message for f in errs))

    def test_action_class_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace("action_class: external-side-effect", "action_class: read-only"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("action_class" in f.message for f in errs))

    def test_source_of_truth_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, card=CARD_OK.replace(
                "source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state",
                "source_of_truth: A spreadsheet"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("source_of_truth" in f.message for f in errs))

    def test_unresolved_ontology_ref_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._pkg(d, skill=SKILL_OK.replace("ontology: ontologies/people-hr/onboarding-orchestration.md",
                                                "ontology: ontologies/people-hr/missing.md"))
            errs = [f for f in validate.check_owner_cards(d) if f.level == "ERROR"]
            self.assertTrue(any("ontology reference" in f.message for f in errs))

    def test_validate_wires_card_checks(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/x/SKILL.md", SKILL_OK.replace(
                "ontology: ontologies/people-hr/onboarding-orchestration.md", "ontology: ontologies/people-hr/onboarding-orchestration.md"))
            _write(d, "skills/x/owner-card.md", CARD_OK.replace("owner: Head of People", "owner: Wrong"))
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            errs = [f for f in validate.validate(d) if f.level == "ERROR"]
            self.assertTrue(any("owner" in f.message for f in errs))


if __name__ == "__main__":
    unittest.main()
