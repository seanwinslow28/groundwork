import ast
import contextlib
import datetime
import io
import os
import pathlib
import re
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "governance" / "hooks"))
import action_class_gate  # noqa: E402

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
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections", "pathlib",
                   "datetime", "subprocess", "unicodedata", "json", "shlex"}
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

    def test_shipped_scripts_only_stdlib(self):
        """Every shipped Python file imports the standard library only — the
        validator, the action-class gate, and any runnable exemplar under demo/.

        Scoped by directory this would have kept passing while a new script shipped
        outside governance/hooks/, which is how an enforcement claim goes quietly
        stale. AGENTS.md says 'every shipped script'; so does this scan.
        """
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections",
                   "pathlib", "datetime", "subprocess", "unicodedata", "json", "shlex"}
        skip = {"__pycache__", "tests"}
        scripts = sorted(
            p for p in REPO.rglob("*.py")
            if not any(part in skip or part.startswith(".")
                       for part in p.relative_to(REPO).parts))
        rels = {str(p.relative_to(REPO)) for p in scripts}
        # Anti-hollow: an empty or near-empty scan passes vacuously, so name what
        # must be in it. Add to this list when a new script ships.
        for expected in ("scripts/validate.py",
                         "governance/hooks/action_class_gate.py",
                         "demo/governance/reminders/meeting-challenger/meeting_challenger.py"):
            self.assertIn(expected, rels, "the shipped-script scan is not finding %s" % expected)
        for py in scripts:
            tree = ast.parse(py.read_text())
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        mods.add(n.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertEqual(mods - allowed, set(), "%s imports non-stdlib: %s"
                             % (py.relative_to(REPO), mods - allowed))


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
        self.assertEqual(validate.check_context_budget("f.md", 5), [])

    def test_warn_threshold(self):
        findings = validate.check_context_budget("f.md", 20_000 * 4)
        self.assertTrue(any(f.level == "WARN" for f in findings))
        self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_error_threshold(self):
        findings = validate.check_context_budget("f.md", 50_000 * 4)
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
        rows, findings = validate.parse_exec_table(self.TABLE)
        self.assertEqual(findings, [])
        self.assertEqual(len(rows), 2)
        act, direction, link, _ = rows[0]
        self.assertEqual(act, "Onboarding orchestration")
        self.assertEqual(direction, "down")
        self.assertEqual(link, "onboarding-orchestration.md")

    def test_row_without_link(self):
        _, direction, link, _ = validate.parse_exec_table(self.TABLE)[0][1]
        self.assertEqual(direction, "up")
        self.assertIsNone(link)

    def test_no_table_returns_empty(self):
        self.assertEqual(validate.parse_exec_table("# just prose\n"), ([], []))


EXEC_CANON = (
    "# Sales — executive view\n\n"
    "Frame paragraph.\n\n"
    "| Activity | Direction | Deep record |\n"
    "|---|---|---|\n"
    "| Discovery calls | up | — |\n"
    "| Forecast roll-up | down | [deep record](forecast.md) |\n"
)


class TestCanonicalExecTable(unittest.TestCase):
    def _parse(self, text):
        return validate.parse_exec_table(text, "x.md")

    def test_canonical_table_parses(self):
        rows, findings = self._parse(EXEC_CANON)
        self.assertEqual(findings, [])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][:3], ("Discovery calls", "up", None))
        self.assertEqual(rows[1][2], "forecast.md")

    def test_spaced_delimiter_is_accepted(self):
        rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|",
                                                        "| --- | --- | --- |"))
        self.assertEqual(findings, [])
        self.assertEqual(len(rows), 2)

    # --- the round-32 six, now unreachable rather than handled ---

    def test_alignment_colons_are_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|",
                                                         "|:---|---:|---|"))
        self.assertTrue(any(f.level == "ERROR" and "delimiter" in f.message
                            for f in findings))

    def test_wrong_delimiter_arity_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|", "|---|---|"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_missing_delimiter_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|\n", ""))
        self.assertTrue(any(f.level == "ERROR" and "delimiter" in f.message
                            for f in findings))

    def test_boundary_double_pipe_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "|| Discovery calls | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_duplicate_direction_column_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Activity | Direction | Deep record |",
                               "| Activity | Direction | Direction |"))
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_deleted_activity_column_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Activity | Direction | Deep record |",
                               "| Direction | Deep record |"))
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_indented_table_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "    | Discovery calls | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    # --- the earlier classes, likewise ---

    def test_second_table_anywhere_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON + "\n| Other | table |\n")
        self.assertTrue(any(f.level == "ERROR" and "exactly one" in f.message
                            for f in findings))

    def test_fenced_example_table_is_rejected(self):
        # No fence awareness: any '|' outside the one table is an error, so a
        # fenced example cannot shadow or decoy anything.
        _rows, findings = self._parse(
            EXEC_CANON + "\n```\n| Activity | Direction |\n```\n")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_blockquoted_row_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON + "\n> | a | b | c |\n")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_no_leading_pipe_row_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "Discovery calls | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_html_comment_in_a_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| <!--x--> | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_escaped_pipe_in_a_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| Quote \\| order | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_code_span_in_a_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| `Discovery` | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_image_in_deep_record_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("[deep record](forecast.md)",
                               "![img](forecast.md)"))
        self.assertTrue(any(f.level == "ERROR" and "Deep record" in f.message
                            for f in findings))

    # --- Codex review of slice 2.2a: the grammar was looser than its own
    # documentation claimed. Each of these was ACCEPTED before the fix. ---

    def test_en_dash_deep_record_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("| up | — |", "| up | – |"))
        self.assertTrue(any(f.level == "ERROR" and "Deep record" in f.message
                            for f in findings))

    def test_hyphen_deep_record_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("| up | — |", "| up | - |"))
        self.assertTrue(any(f.level == "ERROR" and "Deep record" in f.message
                            for f in findings))

    def test_empty_deep_record_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("| up | — |", "| up |  |"))
        self.assertTrue(any(f.level == "ERROR" and "Deep record" in f.message
                            for f in findings))

    def test_image_in_activity_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls |", "| ![img](../README.md) |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_link_in_activity_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls |", "| [link](../README.md) |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_emphasis_in_activity_cell_is_rejected(self):
        for cell in ("**Discovery calls**", "_Discovery calls_"):
            _rows, findings = self._parse(
                EXEC_CANON.replace("| Discovery calls |", "| %s |" % cell))
            self.assertTrue(any(f.level == "ERROR" for f in findings), cell)

    def test_plain_text_activity_names_are_not_over_restricted(self):
        # Codex re-review: the plain-text rule bans link/image/emphasis SYNTAX,
        # not the characters those syntaxes happen to use. A first pass banned
        # '[', ']' and '_' outright and rejected legitimate activity names.
        # CommonMark does not read INTRAWORD '_' as emphasis, so "SOC_2" is text.
        for cell in ("Coverage [EMEA]", "SOC_2 compliance", "P&L review",
                     "Q3/Q4 planning", "Renewal prep (EMEA)", "Café onboarding",
                     "Customer's escalation", "Pricing: tier review"):
            rows, findings = self._parse(
                EXEC_CANON.replace("| Discovery calls |", "| %s |" % cell))
            self.assertEqual(findings, [], cell)
            self.assertEqual(rows[0][0], cell)

    def test_lowercased_header_is_rejected(self):
        # "must be exactly" has to mean exactly, case included.
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Activity | Direction | Deep record |",
                               "| activity | DIRECTION | deep record |"))
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_short_delimiter_cell_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|",
                                                         "|--|--|--|"))
        self.assertTrue(any(f.level == "ERROR" and "delimiter" in f.message
                            for f in findings))

    def test_canonical_header_and_delimiter_with_no_rows_is_rejected(self):
        _rows, findings = self._parse(
            "# Sales\n\n| Activity | Direction | Deep record |\n|---|---|---|\n")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_stray_pipe_before_the_table_names_the_block(self):
        # The offending line must be findable: reporting the LAST pipe line
        # sent the author to a legitimate table row instead of the stray.
        text = ("stray | pipe on line 1\n\n"
                "| Activity | Direction | Deep record |\n"
                "|---|---|---|\n"
                "| Forecast | up | — |\n")
        _rows, findings = self._parse(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 3)      # first line outside the block
        self.assertIn("line 1", findings[0].message)  # ...and the block it found

    def test_empty_activity_still_parses_as_a_row(self):
        # The empty-Activity ERROR belongs to check_ontology; the row must reach it.
        rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |", "|  | up | — |"))
        self.assertEqual(findings, [])
        self.assertEqual(rows[0][0], "")

    def test_no_table_at_all_is_not_a_parse_error(self):
        # Absence is check_ontology's call (an untouched worksheet stays silent).
        rows, findings = self._parse("# Sales\n\nProse only.\n")
        self.assertEqual((rows, findings), ([], []))

    def test_link_reference_definition_is_rejected(self):
        # A definition makes every bracket in the file a potential link, so the
        # file — not the cell — is what gets constrained.
        _rows, findings = self._parse(
            "[r]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_link_reference_definition_after_the_table_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON + "\n[r]: https://example.com\n")
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_indented_link_reference_definition_is_rejected(self):
        _rows, findings = self._parse("   [r]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_reference_link_cell_is_literal_text(self):
        # With definitions banned, this renders as text — so it parses, and the
        # Activity string is exactly what was written.
        rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| [Renewals][r] | up | — |"))
        self.assertEqual(findings, [])
        self.assertEqual(rows[0][0], "[Renewals][r]")

    def test_real_world_bracket_names_still_parse(self):
        for name in ("Coverage [EMEA]", "SOC_2 compliance", "Tier 1 [P0] escalations"):
            rows, findings = self._parse(
                EXEC_CANON.replace("| Discovery calls | up | — |",
                                   "| %s | up | — |" % name))
            self.assertEqual(findings, [], name)
            self.assertEqual(rows[0][0], name)

    def test_a_colon_in_prose_is_not_a_definition(self):
        _rows, findings = self._parse(
            "See the note [below]. Ratio 3:1 applies.\n\n" + EXEC_CANON)
        self.assertEqual(findings, [])

    # --- Codex review of slice 2.2b: a line-anchored regex missed definitions
    # wrapped in a container block or across lines. Each was ACCEPTED before
    # the signature rule; every definition's label-closing line carries "]:",
    # whatever wraps it, so THAT is what gets banned outside the table. ---

    def test_blockquoted_link_reference_definition_is_rejected(self):
        _rows, findings = self._parse("> [r]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_list_item_link_reference_definition_is_rejected(self):
        _rows, findings = self._parse("- [r]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_wrapped_label_link_reference_definition_is_rejected(self):
        # A label may wrap across lines; the line that CLOSES it carries "]:".
        _rows, findings = self._parse("[foo\nbar]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_two_line_definition_is_rejected(self):
        # "[r]:" alone is a definition when its destination sits on the next
        # line — which is why a destinationless "[r]:" line stays banned.
        _rows, findings = self._parse("[r]:\nhttps://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_bracket_colon_inside_a_cell_still_parses(self):
        # The signature rule binds lines OUTSIDE the table; a cell stays
        # governed by the cell rules, so "]:"-bearing names are not collateral.
        rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| Coverage [EMEA]: north | up | — |"))
        self.assertEqual(findings, [])
        self.assertEqual(rows[0][0], "Coverage [EMEA]: north")


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

    def test_links_inside_a_code_fence_are_still_checked(self):
        # Deliberate and load-bearing: check_links is line-based and fence
        # UNAWARE, so a link in a documentation example must resolve from the
        # file it is written in. Slice 2.2a's canonical-table example in
        # ontologies/README.md broke the gate on exactly this. Anyone tempted
        # to make this check fence-aware has to delete this test first.
        findings = validate.check_links(
            str(REPO / "README.md"),
            "```\n| A | up | [deep record](no-such-file.md) |\n```\n",
            str(REPO))
        self.assertTrue(any(f.level == "ERROR" and "broken" in f.message
                            for f in findings))


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

    def test_provenance_removal_errors(self):
        # Codex re-review: removing the label (entirely or to a bare key) is as
        # illegal as a downgrade — forward-only has no exit.
        for new in (MEM_OK.replace("provenance: observed\n", ""),
                    MEM_OK.replace("provenance: observed", "provenance:")):
            with self.subTest(new=new):
                self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                                    for f in validate.check_memory_diff(MEM_OK, new, "m.md")))

    def test_duplicate_provenance_key_in_new_version_errors(self):
        # Codex re-review: malformed NEW frontmatter must fail closed in the
        # diff layer — a duplicate-key trick must not smuggle a transition
        # past a record the stateless walker never sees.
        new = MEM_OK.replace("provenance: observed",
                             "provenance: observed\nprovenance: confirmed")
        self.assertTrue(any(f.level == "ERROR" and "duplicate" in f.message
                            for f in validate.check_memory_diff(MEM_OK, new, "m.md")))

    def test_supersession_field_set_once(self):
        old = (MEM_OK.replace("provenance: observed", "provenance: superseded")
               .replace("review_by: 2099-10-15",
                        "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/new.md"))
        new = old.replace("invalid_at: 2026-08-01", "invalid_at: 2026-09-01")
        self.assertTrue(any(f.level == "ERROR" and "invalid_at" in f.message
                            for f in validate.check_memory_diff(old, new, "m.md")))

    def test_unchanged_record_clean(self):
        self.assertEqual(validate.check_memory_diff(MEM_OK, MEM_OK, "m.md"), [])


import subprocess as _sp  # noqa: E402


def _git(d, *args):
    _sp.run(["git", "-C", d, *args], check=True, capture_output=True, text=True)


class TestMemoryDiffCLI(unittest.TestCase):
    def _repo(self, d):
        _git(d, "init", "-q")
        _git(d, "config", "user.email", "t@t.t")
        _git(d, "config", "user.name", "t")
        _write(d, "memory/onboarding-baseline.md", MEM_OK)
        _write(d, "memory/_index.md", "# Index\n\n- [b](onboarding-baseline.md)\n")
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "base")

    def test_body_edit_flagged_against_base(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/onboarding-baseline.md",
                   MEM_OK.replace("Median time-to-day-one-ready: 4 business days.", "Median: 2 days."))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "body" in f.message for f in findings))

    def test_deleted_record_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "memory", "onboarding-baseline.md"))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "deleted" in f.message for f in findings))

    def test_new_record_is_fine(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/second.md", MEM_OK)
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if "second.md" in f.path], [])

    def test_unchanged_repo_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            self.assertEqual(validate.memory_diff_findings(d, "HEAD"), [])

    def test_not_a_git_repo_errors(self):
        # A tmpdir under the system temp root is not a git work tree.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "git repository" in f.message
                                for f in findings))

    def test_unknown_base_ref_errors_not_silently_passes(self):
        # A typo'd base must not report a clean bill of health.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            findings = validate.memory_diff_findings(d, "no-such-ref")
            self.assertTrue(any(f.level == "ERROR" and "base ref" in f.message
                                for f in findings))

    def test_nested_memory_folder_diffed(self):
        # Records in nested memory folders are inside the diff scope too.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "teams/people/memory/note.md", MEM_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "nested")
            _write(d, "teams/people/memory/note.md",
                   MEM_OK.replace("valid_at: 2026-07-15", "valid_at: 2026-07-16"))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "valid_at" in f.message
                                and "note.md" in f.path for f in findings))

    def test_non_utf8_record_fails_closed_without_crashing(self):
        # Codex review: an unreadable working-tree record must yield an ERROR
        # (immutability cannot be verified), not a crash or a silent pass.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write_bytes(d, "memory/onboarding-baseline.md", b"\xff\xfe")
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "cannot verify" in f.message
                                for f in findings))

    def test_non_utf8_base_version_fails_closed(self):
        # Codex review: replacing a committed non-UTF-8 record with a valid one
        # must not report clean — the base version is unverifiable.
        with tempfile.TemporaryDirectory() as d:
            _git(d, "init", "-q")
            _git(d, "config", "user.email", "t@t.t")
            _git(d, "config", "user.name", "t")
            _write_bytes(d, "memory/x.md", b"\xff\xfe")
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "base")
            _write(d, "memory/x.md", MEM_OK)
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "cannot verify" in f.message
                                for f in findings))

    def test_gitignored_committed_record_still_diffed(self):
        # Codex review: a .gitignore entry must not exempt a committed record
        # from the immutability check (the base list drives the scan).
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, ".gitignore", "onboarding-baseline.md\n")
            _write(d, "memory/onboarding-baseline.md",
                   MEM_OK.replace("Median time-to-day-one-ready: 4 business days.", "Median: 2 days."))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "body" in f.message for f in findings))

    def test_root_inside_memory_folder_still_diffed(self):
        # Codex review: running with root = the memory folder itself must not
        # blind the check (memory-ness is judged repo-relative).
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/onboarding-baseline.md",
                   MEM_OK.replace("valid_at: 2026-07-15", "valid_at: 2026-07-16"))
            findings = validate.memory_diff_findings(os.path.join(d, "memory"), "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "valid_at" in f.message for f in findings))

    def test_non_ascii_record_name_deletion_flagged(self):
        # Codex review: core.quotePath C-quotes non-ASCII names in porcelain
        # output; the -z path list must still see the deletion.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/café.md", MEM_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "accent")
            os.remove(os.path.join(d, "memory", "café.md"))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "deleted" in f.message
                                and "caf" in f.path for f in findings))

    def test_case_only_rename_flagged_as_deletion(self):
        # Codex re-review: on a case-folding filesystem os.path.isfile resolves
        # the renamed file, hiding that the committed path is gone. The exact
        # directory-listing check must flag it on every platform.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/Foo.md", MEM_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "cased")
            os.rename(os.path.join(d, "memory", "Foo.md"),
                      os.path.join(d, "memory", "foo.md"))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "deleted" in f.message
                                and "Foo.md" in f.path for f in findings))

    def test_memory_dir_replaced_by_symlink_mirror_fails(self):
        # Codex re-review: a symlinked memory folder pointing at a
        # byte-identical mirror must not stand in for the committed one.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.rename(os.path.join(d, "memory"), os.path.join(d, "mirror"))
            os.symlink(os.path.join(d, "mirror"), os.path.join(d, "memory"))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                for f in findings))

    def test_record_replaced_by_symlink_fails(self):
        # Codex re-review: a record swapped for a symlink (even to identical
        # content) is not the committed regular file.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            rec = os.path.join(d, "memory", "onboarding-baseline.md")
            os.rename(rec, os.path.join(d, "copy.md"))
            os.symlink(os.path.join(d, "copy.md"), rec)
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                for f in findings))

    def test_case_variant_root_still_diffed(self):
        # Codex re-review: invoking with a case-variant root (Memory vs memory)
        # must not blind the scope filter — the scope comes from git's
        # canonical --show-prefix, not from lexical path math.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            variant = os.path.join(d, "Memory")
            if not os.path.isdir(variant):
                self.skipTest("case-sensitive filesystem")
            _write(d, "memory/onboarding-baseline.md",
                   MEM_OK.replace("Median time-to-day-one-ready: 4 business days.", "Median: 2 days."))
            findings = validate.memory_diff_findings(variant, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "body" in f.message for f in findings))

    def test_ancestor_dir_case_rename_flagged_as_deletion(self):
        # Codex re-review: a case-only rename of an ANCESTOR directory
        # (memory/Team -> memory/team) must flag the committed path as gone.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/Team/note.md", MEM_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "cased-dir")
            os.rename(os.path.join(d, "memory", "Team"),
                      os.path.join(d, "memory", "team"))
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "deleted" in f.message
                                and "Team/note.md" in f.path for f in findings))

    def test_newline_in_repo_path_fails_closed(self):
        # Codex re-review: a newline inside the repo path mis-splits the
        # rev-parse output; the scan must refuse rather than mis-scope.
        with tempfile.TemporaryDirectory() as outer:
            d = os.path.join(outer, "repo\nnewline")
            os.makedirs(d)
            self._repo(d)
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "unsupported path" in f.message
                                for f in findings))

    def test_nfd_on_disk_nfc_in_git_unchanged_record_is_clean(self):
        # Codex final pass: git core.precomposeunicode reports NFC names while
        # the filesystem may list NFD entries; an UNCHANGED record must not be
        # falsely reported as deleted.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _git(d, "config", "core.precomposeunicode", "true")
            _write(d, "memory/cafe\u0301.md", MEM_OK)  # explicit NFD on disk
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "nfd")
            findings = validate.memory_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if "deleted" in f.message], [])

    def test_crlf_base_version_of_unchanged_record_is_clean(self):
        # Codex review: a CRLF blob at base vs an LF working read must not
        # report a phantom body edit.
        crlf = MEM_OK.replace("\n", "\r\n")
        self.assertEqual(validate.check_memory_diff(crlf, MEM_OK, "m.md"), [])


class TestDiffCLIWiring(unittest.TestCase):
    def _main(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = validate.main(["validate.py"] + argv)
        return code, out.getvalue()

    def _repo(self, d):
        TestMemoryDiffCLI._repo(self, d)

    def test_missing_base_arg_exits_2(self):
        code, out = self._main(["--diff"])
        self.assertEqual(code, 2)
        self.assertIn("--diff requires", out)

    def test_clean_repo_diff_exits_0(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            code, _ = self._main([d, "--diff", "HEAD"])
            self.assertEqual(code, 0)

    def test_frozen_edit_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/onboarding-baseline.md",
                   MEM_OK.replace("Median time-to-day-one-ready: 4 business days.", "Median: 2 days."))
            code, out = self._main([d, "--diff", "HEAD"])
            self.assertEqual(code, 1)
            self.assertIn("body changed", out)

    def test_plain_run_ignores_diff_findings(self):
        # The stateless default: the same edited repo passes without --diff.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "memory/onboarding-baseline.md",
                   MEM_OK.replace("Median time-to-day-one-ready: 4 business days.", "Median: 2 days."))
            code, _ = self._main([d])
            self.assertEqual(code, 0)


RULE_OK = """---
owner: Head of IT
rung: human-decision
action_class: high-risk
sunset: 2099-07-01
value: Least-privilege access protects the company and its customers' data
value_owner: CISO
runtime_check: The onboarding agent may propose a grant but halts for a named approver; the provisioning log records who approved
runtime_check_owner: Head of IT
human_appeal: A denied or delayed grant escalates to the CISO, who decides within one business day
human_appeal_owner: CISO
ritual: IT manually provisioning every access request by ticket
scarcity: Security-review time — every grant got a human's eyes
surviving_job: Deciding whether a non-standard grant is warranted
---
# Non-standard system access requires human sign-off

An agent may propose a grant; a named human approves it and is logged.
"""


class TestConstitution(unittest.TestCase):
    def _rule(self, d, text=RULE_OK, name="access.md"):
        _write(d, "governance/constitution/%s" % name, text)

    def test_valid_rule_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d)
            self.assertEqual([f for f in validate.check_constitution(d) if f.level == "ERROR"], [])

    def test_high_risk_without_appeal_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "human_appeal: A denied or delayed grant escalates to the CISO, who decides within one business day\n", "")
                .replace("human_appeal_owner: CISO\n", ""))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("rung six" in f.message for f in errs))

    def test_invalid_rung_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision", "rung: rung-six"))
            self.assertTrue(any(f.level == "ERROR" and "rung" in f.message
                                for f in validate.check_constitution(d)))

    def test_active_rule_without_owner_errors(self):
        with tempfile.TemporaryDirectory() as d:
            # count=1: only the top-level 'owner' line — a bare replace would also
            # eat the tail of 'runtime_check_owner: Head of IT' and mangle the fixture
            self._rule(d, RULE_OK.replace("owner: Head of IT\n", "", 1))
            self.assertTrue(any(f.level == "ERROR" and "owner" in f.message
                                for f in validate.check_constitution(d)))

    def test_draft_rule_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            # no rung → draft; also drop owner (fine while drafting)
            self._rule(d, RULE_OK.replace("rung: human-decision\n", "").replace("owner: Head of IT\n", "", 1))
            findings = validate.check_constitution(d)
            self.assertTrue(any(f.level == "WARN" and "rung" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "owner" in f.message for f in findings))

    def test_missing_sunset_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("sunset: 2099-07-01\n", ""))
            self.assertTrue(any(f.level == "WARN" and "sunset" in f.message
                                for f in validate.check_constitution(d)))

    def test_orphan_repeal_without_reassignment_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "ritual: IT manually provisioning every access request by ticket",
                "ritual: IT manually provisioning every access request by ticket\nrepeals: The weekly access-review meeting"))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("orphan" in f.message for f in errs))

    def test_draft_high_risk_without_appeal_still_errors(self):
        # Codex P1 regression: the safety spine runs on drafts too — a high-risk
        # rule with no appeal path must ERROR even before it is placed on a rung.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision\n", "")
                .replace("human_appeal: A denied or delayed grant escalates to the CISO, who decides within one business day\n", "")
                .replace("human_appeal_owner: CISO\n", ""))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("rung six" in f.message for f in errs))

    def test_draft_missing_sunset_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision\n", "")
                .replace("sunset: 2099-07-01\n", ""))
            self.assertTrue(any(f.level == "WARN" and "sunset" in f.message
                                for f in validate.check_constitution(d)))

    def test_unparseable_sunset_warns(self):
        # Codex P2 regression: `sunset: never` must not silently disable staleness.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("sunset: 2099-07-01", "sunset: never"))
            self.assertTrue(any(f.level == "WARN" and "sunset" in f.message
                                for f in validate.check_constitution(d)))

    def test_active_rule_missing_action_class_errors(self):
        # Codex round 2: action_class drives no-rung-six, so an active rule
        # cannot omit it (a high-risk rule would bypass the safety spine).
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("action_class: high-risk\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "action_class" in f.message
                                for f in validate.check_constitution(d)))

    def test_draft_missing_action_class_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision\n", "")
                .replace("action_class: high-risk\n", ""))
            findings = validate.check_constitution(d)
            self.assertTrue(any(f.level == "WARN" and "action_class" in f.message
                                for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "action_class" in f.message
                                 for f in findings))

    def test_list_valued_owner_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("owner: Head of IT\n",
                                          "owner:\n  - Head of IT\n  - CISO\n", 1))
            self.assertTrue(any(f.level == "ERROR" and "single value" in f.message
                                for f in validate.check_constitution(d)))

    def test_list_valued_appeal_owner_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("human_appeal_owner: CISO\n",
                                          "human_appeal_owner:\n  - CISO\n  - Head of IT\n"))
            self.assertTrue(any(f.level == "ERROR" and "rung six" in f.message
                                for f in validate.check_constitution(d)))

    def test_gitignored_rule_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision", "rung: rung-six"))
            _write(d, ".gitignore", "access.md\n")
            self.assertEqual(
                validate.check_constitution(d, validate.load_gitignore(d)), [])

    def test_placeholder_appeal_errors(self):
        # Codex round 3: `human_appeal: none` / `human_appeal_owner: TBD` are
        # explicit non-answers and must not satisfy the no-rung-six invariant.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "human_appeal: A denied or delayed grant escalates to the CISO, who decides within one business day",
                "human_appeal: none")
                .replace("human_appeal_owner: CISO", "human_appeal_owner: TBD"))
            self.assertTrue(any(f.level == "ERROR" and "rung six" in f.message
                                for f in validate.check_constitution(d)))

    def test_list_valued_reassigned_to_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "ritual: IT manually provisioning every access request by ticket",
                "ritual: IT manually provisioning every access request by ticket\n"
                "repeals: The weekly access-review meeting\n"
                "reassigned_to:\n  - Head of IT\n  - CISO"))
            self.assertTrue(any(f.level == "ERROR" and "orphan" in f.message
                                for f in validate.check_constitution(d)))

    def test_active_rule_missing_object_fields_errors(self):
        # Codex round 3: the four-object/four-owner schema is required in full
        # once a rule is active — a bare owner+rung+action_class+sunset record
        # is not a typed rule.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK
                .replace("runtime_check: The onboarding agent may propose a grant but halts for a named approver; the provisioning log records who approved\n", "")
                .replace("value_owner: CISO\n", ""))
            errs = [f.message for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("runtime_check" in m for m in errs))
            self.assertTrue(any("value_owner" in m for m in errs))

    def test_draft_missing_object_fields_no_error(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision\n", "")
                .replace("runtime_check: The onboarding agent may propose a grant but halts for a named approver; the provisioning log records who approved\n", ""))
            self.assertFalse(any(f.level == "ERROR" and "runtime_check" in f.message
                                 for f in validate.check_constitution(d)))

    def test_active_rule_without_h1_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "# Non-standard system access requires human sign-off\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "rule statement" in f.message
                                for f in validate.check_constitution(d)))

    def test_placeholder_owner_errors(self):
        # Codex round 4: the placeholder policy applies at provisioning, not
        # just to high-risk appeals — `owner: TBD` is an explicitly unowned rule.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("owner: Head of IT\n", "owner: TBD\n", 1))
            self.assertTrue(any(f.level == "ERROR" and "owner" in f.message
                                for f in validate.check_constitution(d)))

    def test_placeholder_object_field_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "value: Least-privilege access protects the company and its customers' data",
                "value: TBD"))
            self.assertTrue(any(f.level == "ERROR" and "value" in f.message
                                for f in validate.check_constitution(d)))

    def test_placeholder_repeal_fields_error(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "surviving_job: Deciding whether a non-standard grant is warranted",
                "surviving_job: TBD\nrepeals: The weekly access-review meeting\nreassigned_to: Head of IT"))
            self.assertTrue(any(f.level == "ERROR" and "orphan" in f.message
                                for f in validate.check_constitution(d)))

    def test_title_only_rule_errors(self):
        # Codex round 4: the rule statement is H1 + body; a bare title is not a rule.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "\nAn agent may propose a grant; a named human approves it and is logged.\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "rule statement" in f.message
                                for f in validate.check_constitution(d)))

    def test_quoted_placeholder_appeal_errors(self):
        # Codex round 5: quoting a placeholder does not answer it.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "human_appeal: A denied or delayed grant escalates to the CISO, who decides within one business day",
                'human_appeal: "TBD"')
                .replace("human_appeal_owner: CISO", 'human_appeal_owner: "TBD"'))
            self.assertTrue(any(f.level == "ERROR" and "rung six" in f.message
                                for f in validate.check_constitution(d)))

    def test_repeals_none_is_not_a_repeal(self):
        # Codex round 5: `repeals: none` is an explicit no-repeal answer and
        # must not demand reassignment fields.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "ritual: IT manually provisioning every access request by ticket",
                "ritual: IT manually provisioning every access request by ticket\nrepeals: none"))
            self.assertFalse(any("orphan" in f.message
                                 for f in validate.check_constitution(d)))

    def test_placeholder_only_body_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "An agent may propose a grant; a named human approves it and is logged.",
                "TBD\n\n---\n\n<!-- fill in -->"))
            self.assertTrue(any(f.level == "ERROR" and "rule statement" in f.message
                                for f in validate.check_constitution(d)))

    def test_markup_placeholder_appeal_errors(self):
        # Codex round 6: markdown/comment formatting must not launder a placeholder.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "human_appeal: A denied or delayed grant escalates to the CISO, who decides within one business day",
                "human_appeal: **TBD**")
                .replace("human_appeal_owner: CISO", "human_appeal_owner: # TODO"))
            self.assertTrue(any(f.level == "ERROR" and "rung six" in f.message
                                for f in validate.check_constitution(d)))

    def test_comment_only_body_errors(self):
        # Codex round 6: a commented-out template body (including its heading)
        # renders nothing and is not a rule statement.
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace(
                "# Non-standard system access requires human sign-off\n\n"
                "An agent may propose a grant; a named human approves it and is logged.",
                "<!--\n# Non-standard system access requires human sign-off\nTODO: write the rule\n-->"))
            self.assertTrue(any(f.level == "ERROR" and "rule statement" in f.message
                                for f in validate.check_constitution(d)))

    def test_unreadable_rule_errors_not_crashes(self):
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "governance/constitution/access.md", b"---\nowner: \xff\xfe\n---\n")
            self.assertTrue(any(f.level == "ERROR" and "UTF-8" in f.message
                                for f in validate.check_constitution(d)))

    def test_validate_wires_constitution(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision", "rung: rung-six"))
            self.assertTrue(any(f.level == "ERROR" and "rung" in f.message for f in validate.validate(d)))


class TestConstitutionProvenance(unittest.TestCase):
    def test_active_rule_missing_provenance_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/access.md",
                   RULE_OK.replace("scarcity: Security-review time — every grant got a human's eyes\n", ""))
            findings = validate.check_constitution(d)
            self.assertTrue(any(f.level == "WARN" and "scarcity" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "scarcity" in f.message for f in findings))

    def test_complete_rule_has_no_provenance_warn(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/access.md", RULE_OK)
            self.assertFalse(any("incomplete thinking" in f.message
                                 for f in validate.check_constitution(d)))

    def test_worksheets_dir_is_not_scanned_as_rules(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/worksheets/blank.md", "# Blank worksheet\n\nNothing filled in.\n")
            self.assertEqual(validate.check_constitution(d), [])


class TestActionClassGate(unittest.TestCase):
    def test_destructive_delete_blocked(self):
        cat, _ = action_class_gate.classify("rm -rf /var/data")
        self.assertEqual(cat, "delete")

    def test_force_push_blocked(self):
        cat, _ = action_class_gate.classify("git push --force origin main")
        self.assertEqual(cat, "delete")

    def test_external_send_blocked(self):
        cat, _ = action_class_gate.classify("curl -X POST https://api.example.com/pay -d '{}'")
        self.assertEqual(cat, "external-send")

    def test_benign_command_not_blocked(self):
        self.assertEqual(action_class_gate.classify("npm test")[0], None)
        self.assertEqual(action_class_gate.classify("git status")[0], None)

    def test_decide_denies_high_risk(self):
        out = action_class_gate.decide(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": "rm -rf /"}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")

    def test_decide_defers_on_benign(self):
        self.assertIsNone(action_class_gate.decide(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": "ls"}}))

    def test_decide_asks_on_malformed_input(self):
        out = action_class_gate.decide({"hook_event_name": "PreToolUse", "tool_name": "Bash"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_rm_standard_spellings_blocked(self):
        # Codex round 1 (P1): -R / --recursive / --force are standard forms, not
        # obfuscation — the hard-block must catch them.
        self.assertEqual(action_class_gate.classify("rm -R /var/data")[0], "delete")
        self.assertEqual(action_class_gate.classify("rm --recursive /var/data")[0], "delete")
        self.assertEqual(action_class_gate.classify("rm --force stale.lock")[0], "delete")
        self.assertEqual(action_class_gate.classify("rm --preserve-root -rf /")[0], "delete")
        self.assertEqual(action_class_gate.classify("rm -rv /var/data")[0], "delete")

    def test_rm_benign_forms_not_blocked(self):
        self.assertEqual(action_class_gate.classify("rm notes.txt")[0], None)
        self.assertEqual(action_class_gate.classify("rm -i notes.txt")[0], None)
        self.assertEqual(action_class_gate.classify("rm --verbose notes.txt")[0], None)

    def test_stripe_read_only_not_blocked(self):
        # Codex round 1 (P2): the taxonomy is action-based — read-only payment
        # queries are not spend.
        self.assertEqual(action_class_gate.classify("stripe charges list")[0], None)
        self.assertEqual(action_class_gate.classify("stripe refunds retrieve re_123")[0], None)

    def test_stripe_mutating_blocked(self):
        self.assertEqual(action_class_gate.classify("stripe charges create --amount 100")[0], "spend")
        self.assertEqual(action_class_gate.classify("stripe payment_intents confirm pi_123")[0], "spend")
        self.assertEqual(action_class_gate.classify("stripe refunds create --charge ch_1")[0], "spend")

    def test_decide_asks_when_bash_payload_has_no_command(self):
        # Codex round 1 (P2): the shipped snippet matches Bash only, so a Bash
        # payload without a command string is unexpected input — fail loud.
        out = action_class_gate.decide(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")
        out = action_class_gate.decide(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": None}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_global_options_before_subcommand_blocked(self):
        # Codex round 3 (P1): global CLI options are standard automation forms,
        # not obfuscation — they must not break the subcommand match.
        self.assertEqual(action_class_gate.classify("git -C repo push --force origin main")[0], "delete")
        self.assertEqual(action_class_gate.classify("git -c user.name=x reset --hard")[0], "delete")
        self.assertEqual(action_class_gate.classify("terraform -chdir=infra apply")[0], "spend")

    def test_curl_write_option_forms_blocked(self):
        # Codex round 3 (P1): attached short args and long request/body options
        # are standard curl spellings.
        self.assertEqual(action_class_gate.classify("curl -d'{}' https://example.com")[0], "external-send")
        self.assertEqual(action_class_gate.classify("curl --request DELETE https://example.com/item")[0], "external-send")
        self.assertEqual(action_class_gate.classify("curl --data-raw '{}' https://example.com")[0], "external-send")

    def test_curl_read_only_not_blocked(self):
        self.assertEqual(action_class_gate.classify("curl https://example.com")[0], None)
        self.assertEqual(action_class_gate.classify("curl -sSL -o out.html https://example.com")[0], None)

    def test_rm_value_bearing_safety_option_blocked(self):
        # Codex round 3 (P1): a value-bearing option before -rf must not
        # disable detection.
        self.assertEqual(action_class_gate.classify("rm --preserve-root=all -rf /var/data")[0], "delete")

    def test_git_clean_force_always_blocked(self):
        # Codex rounds 3→7: the dry-run exemption was laundered three times
        # (later command's -n, comment text, --exclude=--dry-run). Removed —
        # a denied dry run fails safe; a laundered force-clean does not.
        self.assertEqual(action_class_gate.classify("git clean -fd")[0], "delete")
        self.assertEqual(action_class_gate.classify("git clean -nf")[0], "delete")
        self.assertEqual(action_class_gate.classify("git clean --exclude=--dry-run -f")[0], "delete")
        self.assertEqual(action_class_gate.classify("git clean -n")[0], None)

    def test_curl_attached_payload_arguments_blocked(self):
        # Codex round 4 (P1): short-option payloads attached without a
        # separator are standard curl spellings.
        self.assertEqual(action_class_gate.classify("curl -dname=value https://example.com")[0], "external-send")
        self.assertEqual(action_class_gate.classify("curl -Ffile=@payload https://example.com")[0], "external-send")
        self.assertEqual(action_class_gate.classify("curl -Tbackup.tar https://example.com")[0], "external-send")

    def test_quoted_global_option_values_blocked(self):
        # Codex round 4 (P1): quoted option values containing whitespace must
        # not break subcommand adjacency.
        self.assertEqual(action_class_gate.classify('git -C "/tmp/my repo" push --force origin main')[0], "delete")
        self.assertEqual(action_class_gate.classify('git -c user.name="A B" reset --hard')[0], "delete")

    def test_force_push_refspec_blocked(self):
        # Codex round 4 (P1): the leading-plus refspec is git's documented
        # force-update syntax — a force push without --force.
        self.assertEqual(action_class_gate.classify("git push origin +main")[0], "delete")
        self.assertEqual(action_class_gate.classify("git push origin main")[0], None)

    def test_line_continuations_normalized_before_matching(self):
        # Codex round 5 (P1): bash joins backslash-newline continuations before
        # executing — classify what runs, not the raw text.
        self.assertEqual(action_class_gate.classify("rm \\\n -rf /tmp/x")[0], "delete")
        self.assertEqual(action_class_gate.classify("git push \\\n --force origin main")[0], "delete")

    def test_curl_json_option_blocked(self):
        # Codex round 5 (P1): --json implies an HTTP POST.
        self.assertEqual(action_class_gate.classify("curl --json '{}' https://example.com")[0], "external-send")

    def test_reset_hard_after_other_options_blocked(self):
        # Codex round 5 (P1): git accepts reset options before --hard.
        self.assertEqual(action_class_gate.classify("git reset -q --hard HEAD")[0], "delete")
        self.assertEqual(action_class_gate.classify("git reset --soft HEAD~1")[0], None)

    def test_clean_dry_run_exemption_ignores_comments(self):
        # Codex round 5 (P1): '--dry-run' inside a shell comment must not
        # launder a real force-clean. (Round 7 removed the exemption entirely,
        # so a dry-run force-clean now also denies — fail safe.)
        self.assertEqual(action_class_gate.classify("git clean -fd # not a --dry-run")[0], "delete")
        self.assertEqual(action_class_gate.classify("git clean -n -f # cleanup")[0], "delete")

    def test_hash_in_clean_argument_does_not_hide_force(self):
        # Codex round 6 (P1): '#' inside an argument is data, not a comment —
        # it must not truncate the force scan (that would fail open).
        self.assertEqual(action_class_gate.classify("git clean --exclude=#keep -fd")[0], "delete")
        self.assertEqual(action_class_gate.classify('git clean -e "#keep" -fd')[0], "delete")

    def test_clustered_push_force_blocked(self):
        # Codex round 6 (P1): git accepts -f inside a short-option cluster.
        self.assertEqual(action_class_gate.classify("git push -fu origin main")[0], "delete")
        self.assertEqual(action_class_gate.classify("git push -u origin main")[0], None)

    def test_quoted_dd_device_blocked(self):
        # Codex round 6 (P1): quoting the device is a standard spelling.
        self.assertEqual(action_class_gate.classify('dd if=image.iso of="/dev/sda"')[0], "delete")
        self.assertEqual(action_class_gate.classify("dd if=image.iso of='/dev/sda'")[0], "delete")

    def test_curl_clustered_payload_flags_blocked(self):
        # Codex round 6 (P1): payload flags may end a short-option cluster.
        self.assertEqual(action_class_gate.classify("curl -sd x=1 https://example.com")[0], "external-send")
        self.assertEqual(action_class_gate.classify("curl -sTbackup.tar https://example.com")[0], "external-send")

    def test_backslash_escaped_spaces_in_option_values(self):
        # Codex round 6 (P1): shell-escaped spaces keep the value one token.
        self.assertEqual(action_class_gate.classify("git -C /tmp/my\\ repo push --force origin main")[0], "delete")

    def test_terraform_destroy_blocked(self):
        # Codex round 7 (P1): destroy is the delete class, plainly.
        self.assertEqual(action_class_gate.classify("terraform destroy -auto-approve")[0], "spend")
        self.assertEqual(action_class_gate.classify("terraform plan")[0], None)

    def test_quoted_force_refspec_blocked(self):
        # Codex round 7 (P1): the shell strips quotes before git sees +main.
        self.assertEqual(action_class_gate.classify("git push origin '+main'")[0], "delete")

    def test_quoted_curl_methods_blocked(self):
        # Codex round 7 (P1): quoting the method is a standard spelling.
        self.assertEqual(action_class_gate.classify('curl -X "DELETE" https://example.com/item')[0], "external-send")
        self.assertEqual(action_class_gate.classify("curl --request='POST' https://example.com")[0], "external-send")

    def test_truncate_without_table_keyword_blocked(self):
        # Codex round 7 (P1): TABLE is optional in PostgreSQL.
        self.assertEqual(action_class_gate.classify("psql -c 'TRUNCATE users'")[0], "delete")
        self.assertEqual(action_class_gate.classify("truncate -s 0 app.log")[0], None)

    def test_stripe_global_options_and_post_blocked(self):
        # Codex round 7 (P1): global options precede the resource; the generic
        # post command is a raw API mutation.
        self.assertEqual(
            action_class_gate.classify('stripe --api-key "$KEY" refunds create --charge ch_1')[0], "spend")
        self.assertEqual(action_class_gate.classify("stripe post /v1/charges -d amount=100")[0], "spend")

    def test_wget_method_write_requests_blocked(self):
        # Codex round 7 (P1): --method/--body-* are wget's standard write forms.
        self.assertEqual(action_class_gate.classify("wget --method=DELETE https://example.com/x")[0], "external-send")
        self.assertEqual(
            action_class_gate.classify("wget --method=POST --body-data=x https://example.com")[0], "external-send")
        self.assertEqual(action_class_gate.classify("wget https://example.com/file.tar.gz")[0], None)

    def test_mail_binary_blocked_in_command_position(self):
        # Codex round 7 (P1): plain `mail` sends email; matched only in command
        # position so text mentioning mail (cat mail.log) stays benign.
        self.assertEqual(
            action_class_gate.classify("printf body | /usr/bin/mail -s subject user@example.com")[0],
            "external-send")
        self.assertEqual(action_class_gate.classify("mail -s hi user@example.com")[0], "external-send")
        self.assertEqual(action_class_gate.classify("cat mail.log")[0], None)

    def test_mail_after_newline_blocked(self):
        # Codex round 8 (P1): a newline is a command boundary in a multiline
        # Bash payload.
        self.assertEqual(action_class_gate.classify("echo ready\nmail -s hi user@example.com")[0],
                         "external-send")

    def test_reset_hard_after_revision_blocked(self):
        # Codex round 8 (P1): git accepts the revision before --hard.
        self.assertEqual(action_class_gate.classify("git reset HEAD~1 --hard")[0], "delete")

    def test_rm_flags_after_operands_blocked(self):
        # Codex round 8 (P1): GNU argument permutation makes trailing -rf
        # options; after a standalone `--` they are operands.
        self.assertEqual(action_class_gate.classify("rm /tmp/cache -rf /tmp/data")[0], "delete")
        self.assertEqual(action_class_gate.classify("rm -- -rf")[0], None)

    def test_decide_asks_on_blank_command(self):
        # Codex round 2 (P2): a blank command string is unusable input, not a
        # benign command — fail loud, don't defer.
        for cmd in ("", "   "):
            out = action_class_gate.decide(
                {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                 "tool_input": {"command": cmd}})
            self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask",
                             "no ask for command %r" % cmd)


SNIPPET_OK = """{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command",
                  "command": "python3 ${CLAUDE_PROJECT_DIR}/governance/hooks/action_class_gate.py"}]}
    ]
  }
}
"""

SNIPPET_QUOTED = """{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command",
                  "command": "python3 \\"${CLAUDE_PROJECT_DIR}/governance/hooks/action_class_gate.py\\""}]}
    ]
  }
}
"""


class TestHooks(unittest.TestCase):
    def _set(self, d, snippet=SNIPPET_OK, script=True, review=True):
        _write(d, "governance/hooks/settings.snippet.json", snippet)
        if script:
            _write(d, "governance/hooks/action_class_gate.py", "# hook\n")
        if review:
            _write(d, "governance/hooks/review-gate.md", "# review gate\n")

    def test_wired_hook_set_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d)
            self.assertEqual([f for f in validate.check_hooks(d) if f.level == "ERROR"], [])

    def test_unwired_command_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, script=False)
            errs = [f for f in validate.check_hooks(d) if f.level == "ERROR"]
            self.assertTrue(any("not found" in f.message for f in errs))

    def test_invalid_json_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet="{ not json ")
            self.assertTrue(any(f.level == "ERROR" and "JSON" in f.message
                                for f in validate.check_hooks(d)))

    def test_missing_review_gate_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, review=False)
            findings = validate.check_hooks(d)
            self.assertTrue(any(f.level == "WARN" and "review-gate" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "review-gate" in f.message for f in findings))

    def test_no_hooks_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_hooks(d), [])

    def test_non_object_snippet_json_errors(self):
        # Codex round 1 (P2): valid JSON with a non-object top level parsed
        # clean — a completely unusable snippet must not pass silently.
        for payload in ("[]\n", "null\n", '"hooks"\n'):
            with tempfile.TemporaryDirectory() as d:
                self._set(d, snippet=payload)
                self.assertTrue(any(f.level == "ERROR" and "JSON object" in f.message
                                    for f in validate.check_hooks(d)),
                                "no ERROR for snippet %r" % payload)

    def test_quoted_command_resolves_in_root_with_spaces(self):
        # Codex round 1 (P1): the shipped snippet quotes ${CLAUDE_PROJECT_DIR};
        # the checker must parse shell quoting, and a root with spaces must work.
        with tempfile.TemporaryDirectory() as d:
            root = os.path.join(d, "my company os")
            os.makedirs(root)
            self._set(root, snippet=SNIPPET_QUOTED)
            self.assertEqual([f for f in validate.check_hooks(root) if f.level == "ERROR"], [])

    def test_wrong_event_registration_errors(self):
        # Codex round 2 (P2): a gate registered under PostToolUse cannot block
        # a command before it runs — the registration itself is the claim.
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet=SNIPPET_OK.replace("PreToolUse", "PostToolUse"))
            self.assertTrue(any(f.level == "ERROR" and "PreToolUse" in f.message
                                for f in validate.check_hooks(d)))

    def test_non_bash_matcher_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet=SNIPPET_OK.replace('"matcher": "Bash"', '"matcher": "Edit"'))
            self.assertTrue(any(f.level == "ERROR" and "PreToolUse" in f.message
                                for f in validate.check_hooks(d)))

    def test_missing_snippet_errors(self):
        # Codex round 4 (P2): a hooks dir with no registration snippet is the
        # most unwired guard of all — nothing can be installed.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/hooks/action_class_gate.py", "# hook\n")
            _write(d, "governance/hooks/review-gate.md", "# review gate\n")
            self.assertTrue(any(f.level == "ERROR" and "settings.snippet.json" in f.message
                                for f in validate.check_hooks(d)))

    def test_pre_bash_hook_must_target_the_gate(self):
        # Codex round 4 (P2): an unrelated PreToolUse/Bash hook must not stand
        # in for the gate when the gate itself is registered under PostToolUse.
        snip = """{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/governance/hooks/other.py"}]}
    ],
    "PostToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/governance/hooks/action_class_gate.py"}]}
    ]
  }
}
"""
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet=snip)
            _write(d, "governance/hooks/other.py", "# other\n")
            self.assertTrue(any(f.level == "ERROR" and "PreToolUse" in f.message
                                for f in validate.check_hooks(d)))

    def test_redirected_hook_command_errors(self):
        # Codex round 8 (P2): a redirection discards the decision JSON — the
        # hook runs but Claude never receives a deny.
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet=SNIPPET_OK.replace(
                "action_class_gate.py",
                "action_class_gate.py >/dev/null"))
            self.assertTrue(any(f.level == "ERROR" and "runnable command" in f.message
                                for f in validate.check_hooks(d)))

    def test_dangling_hooks_dir_symlink_errors(self):
        # Codex round 8 (P2): a dangling governance/hooks symlink must not be
        # treated as an absent hook set.
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "governance"))
            os.symlink(os.path.join(d, "no-such-target"),
                       os.path.join(d, "governance", "hooks"))
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                for f in validate.check_hooks(d)))

    def test_symlinked_gate_script_errors(self):
        # Codex round 7 (P2): a symlinked artifact is not the committed,
        # auditable file the enforcement claim names.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/hooks/settings.snippet.json", SNIPPET_OK)
            _write(d, "governance/hooks/review-gate.md", "# review gate\n")
            _write(d, "elsewhere.py", "# external\n")
            os.symlink(os.path.join(d, "elsewhere.py"),
                       os.path.join(d, "governance", "hooks", "action_class_gate.py"))
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                for f in validate.check_hooks(d)))

    def test_empty_hooks_object_errors(self):
        # Codex round 3 (P2): a snippet with no command hooks at all is a
        # completely unwired guard — an ERROR, not just a WARN.
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet='{"hooks": {}}\n')
            self.assertTrue(any(f.level == "ERROR" and "PreToolUse" in f.message
                                for f in validate.check_hooks(d)))

    def test_regex_matcher_covering_bash_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet=SNIPPET_OK.replace('"matcher": "Bash"', '"matcher": "Bash|Edit"'))
            self.assertEqual([f for f in validate.check_hooks(d) if f.level == "ERROR"], [])

    def test_unbalanced_quote_in_command_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet=SNIPPET_OK.replace(
                "python3 ${CLAUDE_PROJECT_DIR}/governance/hooks/action_class_gate.py",
                "python3 \\\"unclosed"))
            self.assertTrue(any(f.level == "ERROR" and "no runnable command" in f.message
                                for f in validate.check_hooks(d)))


PIN_OK = """---
schema_version: 1
generated_by_commit: 0123456789abcdef0123456789abcdef01234567
---
"""


class TestVersionPin(unittest.TestCase):
    def test_current_pin_is_exactly_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK)
            self.assertEqual(validate.check_version_pin(d), [])

    def test_skew_forward_is_exactly_one_migration_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK.replace("schema_version: 1", "schema_version: 0"))
            errs = [f for f in validate.check_version_pin(d) if f.level == "ERROR"]
            self.assertEqual(len(errs), 1)
            self.assertIn("MIGRATIONS", errs[0].message)

    def test_reverse_skew_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK.replace("schema_version: 1", "schema_version: 2"))
            findings = validate.check_version_pin(d)
            self.assertTrue(any(f.level == "WARN" and "pull the engine" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_missing_schema_version_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin",
                   "---\ngenerated_by_commit: abc123\n---\n")
            self.assertTrue(any(f.level == "ERROR" and "schema_version" in f.message
                                for f in validate.check_version_pin(d)))

    def test_non_integer_schema_version_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK.replace("schema_version: 1", "schema_version: v1"))
            self.assertTrue(any(f.level == "ERROR" and "integer" in f.message
                                for f in validate.check_version_pin(d)))

    def test_list_schema_version_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin",
                   "---\nschema_version:\n- 1\n- 2\n---\n")
            self.assertTrue(any(f.level == "ERROR" and "integer" in f.message
                                for f in validate.check_version_pin(d)))

    def test_non_utf8_pin_errors_not_crashes(self):
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "your-company/groundwork.pin", b"---\nschema_version: 1\n---\n\xff\xfe")
            self.assertTrue(any(f.level == "ERROR" for f in validate.check_version_pin(d)))

    def test_empty_pin_file_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", "")
            self.assertTrue(any(f.level == "ERROR" and "schema_version" in f.message
                                for f in validate.check_version_pin(d)))

    def test_unclosed_frontmatter_pin_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", "---\nschema_version: 1\n")
            self.assertTrue(any(f.level == "ERROR" and "never closed" in f.message
                                for f in validate.check_version_pin(d)))

    def test_duplicate_schema_version_key_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin",
                   "---\nschema_version: 1\nschema_version: 0\n---\n")
            self.assertTrue(any(f.level == "ERROR" and "duplicate" in f.message
                                for f in validate.check_version_pin(d)))

    def test_missing_commit_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", "---\nschema_version: 1\n---\n")
            findings = validate.check_version_pin(d)
            self.assertTrue(any(f.level == "WARN" and "generated_by_commit" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_validate_wires_pin(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK.replace("schema_version: 1", "schema_version: 0"))
            self.assertTrue(any(f.level == "ERROR" and "MIGRATIONS" in f.message for f in validate.validate(d)))


class TestSymlinkedDirs(unittest.TestCase):
    def test_symlinked_content_dir_warns(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "real_memory"))
            _write(d, "real_memory/rec.md", "# a record\n")
            os.symlink(os.path.join(d, "real_memory"), os.path.join(d, "memory"))
            warns = [f for f in validate.check_symlinked_dirs(d) if f.level == "WARN"]
            self.assertTrue(any("symlinked directory" in f.message for f in warns))

    def test_no_symlinks_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/x.md", "# x\n")
            self.assertEqual(validate.check_symlinked_dirs(d), [])

    def test_skip_set_symlinks_are_silent(self):
        """Skip-set parity with iter_files: symlinks under SKIP_DIRS, dot-dirs,
        SKIP_RELPATHS, and gitignored names are legitimately unscanned — no WARN."""
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "real"))
            _write(d, "real/x.md", "# x\n")
            _write(d, ".gitignore", "ignored-link\n")
            os.makedirs(os.path.join(d, ".claude"))
            os.symlink(os.path.join(d, "real"), os.path.join(d, ".claude", "skills"))
            os.makedirs(os.path.join(d, "tests"))
            os.symlink(os.path.join(d, "real"), os.path.join(d, "tests", "fixtures"))
            os.makedirs(os.path.join(d, "__pycache__"))
            os.symlink(os.path.join(d, "real"), os.path.join(d, "__pycache__", "cached"))
            os.symlink(os.path.join(d, "real"), os.path.join(d, "ignored-link"))
            self.assertEqual(validate.check_symlinked_dirs(d), [])

    def test_validate_wires_symlink_warn(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "real_memory"))
            _write(d, "real_memory/rec.md", "# a record\n")
            os.symlink(os.path.join(d, "real_memory"), os.path.join(d, "memory"))
            self.assertTrue(any(f.level == "WARN" and "symlinked directory" in f.message
                                for f in validate.validate(d)))


PROPOSAL_OK = """---
target: skills/onboarding-orchestration/SKILL.md
blast_radius: escalating
reason: Tighten the description so it stops overlapping the offboarding skill
evidence:
  - memory/onboarding-baseline.md
status: pending
---
# Proposal: sharpen onboarding description

## Diff
(elided)

## Why
The two descriptions overlap and misroute selection.
"""


class TestProposals(unittest.TestCase):
    def _prop(self, d, text=PROPOSAL_OK, name="p1.md"):
        _write(d, "proposals/%s" % name, text)
        _write(d, "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
        _write(d, "memory/onboarding-baseline.md", MEM_OK)

    def test_valid_proposal_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d)
            self.assertEqual([f for f in validate.check_proposals(d) if f.level == "ERROR"], [])

    def test_missing_target_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("target: skills/onboarding-orchestration/SKILL.md\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "target" in f.message
                                for f in validate.check_proposals(d)))

    def test_target_outside_domain_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("skills/onboarding-orchestration/SKILL.md",
                                              "ontologies/people-hr/onboarding-orchestration.md"))
            self.assertTrue(any(f.level == "ERROR" and "skill" in f.message.lower()
                                for f in validate.check_proposals(d)))

    def test_invalid_blast_radius_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("blast_radius: escalating", "blast_radius: trivial"))
            self.assertTrue(any(f.level == "ERROR" and "blast_radius" in f.message
                                for f in validate.check_proposals(d)))

    def test_rule_target_cannot_be_track1_body(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "proposals/p.md",
                   PROPOSAL_OK.replace("skills/onboarding-orchestration/SKILL.md",
                                       "governance/constitution/access.md")
                   .replace("blast_radius: escalating", "blast_radius: track1-body"))
            _write(d, "governance/constitution/access.md", RULE_OK)
            self.assertTrue(any(f.level == "ERROR" and "never auto-apply" in f.message
                                for f in validate.check_proposals(d)))

    def test_rule_target_via_path_alias_cannot_be_track1_body(self):
        # Codex 1.5d-i round 1: skills/../governance/... must not launder a
        # rule into the skills/ bucket and dodge rules-never-auto-apply.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "proposals/p.md",
                   PROPOSAL_OK.replace("skills/onboarding-orchestration/SKILL.md",
                                       "skills/../governance/constitution/access.md")
                   .replace("blast_radius: escalating", "blast_radius: track1-body"))
            _write(d, "governance/constitution/access.md", RULE_OK)
            self.assertTrue(any(f.level == "ERROR" and "never auto-apply" in f.message
                                for f in validate.check_proposals(d)))

    def test_non_scalar_status_errors(self):
        # Codex 1.5d-i round 1: a list-valued status must not slip past the
        # pending-only lifecycle check (fail closed, not fail open).
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("status: pending", "status:\n  - applied"))
            self.assertTrue(any(f.level == "ERROR" and "pending-only" in f.message
                                for f in validate.check_proposals(d)))

    def test_symlinked_target_cannot_launder_rule(self):
        # Codex 1.5d-i round 2: a symlink named SKILL.md pointing at a rule
        # must classify by where it RESOLVES, not how it is spelled.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/access.md", RULE_OK)
            os.makedirs(os.path.join(d, "skills", "onboarding-orchestration"))
            os.symlink(os.path.join(d, "governance", "constitution", "access.md"),
                       os.path.join(d, "skills", "onboarding-orchestration", "SKILL.md"))
            _write(d, "proposals/p.md",
                   PROPOSAL_OK.replace("blast_radius: escalating", "blast_radius: track1-body"))
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            findings = validate.check_proposals(d)
            self.assertTrue(any(f.level == "ERROR" and "resolves outside" in f.message
                                for f in findings))
            self.assertTrue(any(f.level == "ERROR" and "never auto-apply" in f.message
                                for f in findings))

    def test_track1_body_requires_skill_md_target(self):
        # Codex 1.5d-i round 2: an Owner's Card under skills/ is not the
        # SKILL.md body — track1-body on it is a contradiction.
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("skills/onboarding-orchestration/SKILL.md",
                                              "skills/onboarding-orchestration/owner-card.md")
                       .replace("blast_radius: escalating", "blast_radius: track1-body"))
            _write(d, "skills/onboarding-orchestration/owner-card.md", "# card\n")
            self.assertTrue(any(f.level == "ERROR" and "SKILL.md" in f.message
                                for f in validate.check_proposals(d)))

    def test_empty_body_warns(self):
        # Codex 1.5d-i round 2: the proposal file IS the review file — a
        # frontmatter-only proposal (no Diff / Why) is incomplete.
        with tempfile.TemporaryDirectory() as d:
            fm_only = PROPOSAL_OK.split("\n---\n")[0] + "\n---\n"
            self._prop(d, fm_only)
            findings = validate.check_proposals(d)
            self.assertTrue(any(f.level == "WARN" and "empty body" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_multiline_comment_body_warns(self):
        # Codex 1.5d-i round 3: a body that is only a MULTILINE HTML comment
        # (opener/closer on separate lines) is still empty.
        with tempfile.TemporaryDirectory() as d:
            fm_only = PROPOSAL_OK.split("\n---\n")[0] + "\n---\n"
            self._prop(d, fm_only + "<!--\nnot proposed yet\n-->\n")
            self.assertTrue(any(f.level == "WARN" and "empty body" in f.message
                                for f in validate.check_proposals(d)))

    def test_unterminated_comment_body_warns(self):
        # Codex 1.5d-i round 4: an unterminated <!-- opener hides everything
        # after it — the body is still empty.
        with tempfile.TemporaryDirectory() as d:
            fm_only = PROPOSAL_OK.split("\n---\n")[0] + "\n---\n"
            self._prop(d, fm_only + "<!--\nnot proposed yet\n")
            self.assertTrue(any(f.level == "WARN" and "empty body" in f.message
                                for f in validate.check_proposals(d)))

    def test_missing_diff_section_warns(self):
        # Codex 1.5d-i round 4: #17 completeness includes the diff itself —
        # prose with no '## Diff' content is incomplete.
        with tempfile.TemporaryDirectory() as d:
            fm_only = PROPOSAL_OK.split("\n---\n")[0] + "\n---\n"
            self._prop(d, fm_only + "## Why\nThe two descriptions overlap.\n")
            findings = validate.check_proposals(d)
            self.assertTrue(any(f.level == "WARN" and "Diff" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_empty_diff_section_warns(self):
        # Codex 1.5d-i round 4: a bare '## Diff' heading with no content is
        # not a carried diff.
        with tempfile.TemporaryDirectory() as d:
            fm_only = PROPOSAL_OK.split("\n---\n")[0] + "\n---\n"
            self._prop(d, fm_only + "## Diff\n\n## Why\nThe two descriptions overlap.\n")
            self.assertTrue(any(f.level == "WARN" and "Diff" in f.message
                                for f in validate.check_proposals(d)))

    def test_list_reason_counts_as_incomplete(self):
        # Codex 1.5d-i round 2: a list-valued reason is not the one scalar
        # line the schema asks for — still incomplete.
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace(
                "reason: Tighten the description so it stops overlapping the offboarding skill",
                "reason:\n  - because"))
            findings = validate.check_proposals(d)
            self.assertTrue(any(f.level == "WARN" and "reason" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_non_pending_status_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("status: pending", "status: applied"))
            self.assertTrue(any(f.level == "ERROR" and "pending-only" in f.message
                                for f in validate.check_proposals(d)))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "root ignores directory permissions")
    def test_unreadable_proposals_dir_fails_closed(self):
        # Codex 1.5d-i round 5: an unreadable proposals/ must ERROR, not crash.
        with tempfile.TemporaryDirectory() as d:
            pdir = os.path.join(d, "proposals")
            os.makedirs(pdir)
            os.chmod(pdir, 0)
            try:
                findings = validate.check_proposals(d)
            finally:
                os.chmod(pdir, 0o755)
            self.assertTrue(any(f.level == "ERROR" and "fail closed" in f.message
                                for f in findings))

    def test_incomplete_proposal_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("reason: Tighten the description so it stops overlapping the offboarding skill\n", ""))
            findings = validate.check_proposals(d)
            self.assertTrue(any(f.level == "WARN" and "working note" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "reason" in f.message for f in findings))


class TestChangelog(unittest.TestCase):
    def test_empty_changelog_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md", "# Governance changelog\n\n## Entries\n")
            self.assertEqual(validate.check_changelog(d), [])

    def test_valid_entry_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- 2026-07-26 | skills/onboarding-orchestration/SKILL.md | trimmed wording | scribe | a1b2c3d\n")
            self.assertEqual([f for f in validate.check_changelog(d) if f.level == "ERROR"], [])
            self.assertEqual(validate.check_changelog(d), [])

    def test_malformed_entry_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n- oops not a real entry\n")
            self.assertTrue(any(f.level == "WARN" for f in validate.check_changelog(d)))

    def test_bad_date_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- last-tuesday | skills/x/SKILL.md | gist | agent | a1b2c3d\n")
            self.assertTrue(any(f.level == "WARN" and "date" in f.message for f in validate.check_changelog(d)))

    def test_blank_gist_or_agent_warns(self):
        # Codex 1.5d-i round 1: five pipes with empty gist/agent fields is
        # not a well-formed entry.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- 2026-07-26 | skills/x/SKILL.md | | | a1b2c3d\n")
            self.assertTrue(any(f.level == "WARN" and "malformed changelog entry" in f.message
                                for f in validate.check_changelog(d)))

    def test_skill_path_alias_warns(self):
        # Codex 1.5d-i round 1: skills/../governance/... is not a skills/ path.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- 2026-07-26 | skills/../governance/changelog.md | gist | agent | a1b2c3d\n")
            self.assertTrue(any(f.level == "WARN" and "skills/" in f.message
                                for f in validate.check_changelog(d)))

    def test_non_skill_md_path_warns(self):
        # Codex 1.5d-i round 2: auto-apply is body-only SKILL.md edits — a
        # card path under skills/ is not a valid changelog subject.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- 2026-07-26 | skills/onboarding-orchestration/owner-card.md | gist | agent | a1b2c3d\n")
            self.assertTrue(any(f.level == "WARN" and "SKILL.md" in f.message
                                for f in validate.check_changelog(d)))

    def test_symlinked_skill_path_warns(self):
        # Codex 1.5d-i round 2: symlink parity with check_proposals — a
        # skills/ path resolving elsewhere in the tree is an alias.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/access.md", "# rule\n")
            os.makedirs(os.path.join(d, "skills", "onboarding-orchestration"))
            os.symlink(os.path.join(d, "governance", "constitution", "access.md"),
                       os.path.join(d, "skills", "onboarding-orchestration", "SKILL.md"))
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- 2026-07-26 | skills/onboarding-orchestration/SKILL.md | gist | agent | a1b2c3d\n")
            self.assertTrue(any(f.level == "WARN" and "alias" in f.message
                                for f in validate.check_changelog(d)))

    def test_no_changelog_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_changelog(d), [])


SKILL_T1 = """---
name: weekly-digest
description: Summarize the week's open threads for the team channel
action_class: read-only
provisioned: no
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Weekly digest

Collect the week's open threads and summarize them.
"""


class TestGovernedClassify(unittest.TestCase):
    def test_rule_paths_are_governed(self):
        self.assertEqual(validate._governed_class("governance/constitution/access.md"), "rule")
        self.assertEqual(validate._governed_class("governance/constitution/sub/access.md"), "rule")

    def test_skill_md_and_package_files(self):
        self.assertEqual(validate._governed_class("skills/weekly-digest/SKILL.md"), "skill-md")
        self.assertEqual(validate._governed_class("skills/weekly-digest/owner-card.md"), "skill-other")
        self.assertEqual(validate._governed_class("skills/weekly-digest/sub/SKILL.md"), "skill-other")

    def test_ungoverned_paths(self):
        self.assertIsNone(validate._governed_class("skills/work-package-spec.md"))
        self.assertIsNone(validate._governed_class("governance/changelog.md"))
        self.assertIsNone(validate._governed_class("memory/onboarding-baseline.md"))
        self.assertIsNone(validate._governed_class("README.md"))

    def test_any_rule_change_escalates(self):
        r, _d = validate.classify_governed_change("modified", "rule", RULE_OK, RULE_OK + "\nmore\n")
        self.assertEqual(r, "escalating")

    def test_owner_card_change_escalates(self):
        r, _d = validate.classify_governed_change("modified", "skill-other", CARD_OK, CARD_OK + "\nx\n")
        self.assertEqual(r, "escalating")

    def test_added_skill_escalates(self):
        r, _d = validate.classify_governed_change("added", "skill-md", None, SKILL_T1)
        self.assertEqual(r, "escalating")

    def test_track1_body_only_change(self):
        new = SKILL_T1.replace("Collect the week's open threads and summarize them.",
                               "Collect the week's open threads, summarize them, and note blockers.")
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "track1-body")

    def test_track2_body_only_change_escalates(self):
        new = SKILL_OK.replace("# Onboarding orchestration", "# Onboarding orchestration\n\nextra line")
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_OK, new)
        self.assertEqual(r, "escalating")
        self.assertIn("track-2", d)

    def test_description_change_escalates(self):
        new = SKILL_T1.replace("Summarize the week's open threads for the team channel",
                               "Summarize everything anyone said this week")
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")
        self.assertIn("frontmatter", d)

    def test_action_class_change_escalates(self):
        new = SKILL_T1.replace("action_class: read-only", "action_class: high-risk")
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")

    def test_unparseable_new_frontmatter_fails_closed(self):
        new = SKILL_T1.replace("provisioned: no", "  indented: bad")
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")
        self.assertIn("unparseable", d)

    def test_missing_action_class_fails_closed(self):
        base = SKILL_T1.replace("action_class: read-only\n", "")
        new = base.replace("Collect the week's open threads and summarize them.", "Different body.")
        r, d = validate.classify_governed_change("modified", "skill-md", base, new)
        self.assertEqual(r, "escalating")
        self.assertIn("action_class", d)

    def test_invalid_action_class_fails_closed(self):
        base = SKILL_T1.replace("action_class: read-only", "action_class: mostly-harmless")
        new = base.replace("Collect the week's open threads and summarize them.", "Different body.")
        r, _d = validate.classify_governed_change("modified", "skill-md", base, new)
        self.assertEqual(r, "escalating")

    def test_unchanged_file_classifies_as_nothing(self):
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, SKILL_T1)
        self.assertIsNone(r)
        self.assertIsNone(d)

    def test_whitespace_and_crlf_only_change_is_not_a_change(self):
        new = SKILL_T1.replace("\n", "\r\n") + "\n\n"
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertIsNone(r)

    def test_frontmatter_removed_entirely_escalates(self):
        new = SKILL_T1.split("---\n", 2)[2]
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")

    def test_unchanged_rule_classifies_as_nothing(self):
        # Regression (plan bug, fixed in-session): the caller's candidate set is
        # the whole base tree, so an UNTOUCHED rule must not read as escalating.
        r, d = validate.classify_governed_change("modified", "rule", RULE_OK, RULE_OK)
        self.assertIsNone(r)
        self.assertIsNone(d)

    def test_unchanged_owner_card_classifies_as_nothing(self):
        r, d = validate.classify_governed_change("modified", "skill-other", CARD_OK, CARD_OK)
        self.assertIsNone(r)
        self.assertIsNone(d)

    def test_crlf_only_rule_change_is_not_a_change(self):
        # A CRLF base blob against a text-mode working read is not a rewrite.
        r, _d = validate.classify_governed_change("modified", "rule",
                                                  RULE_OK.replace("\n", "\r\n"), RULE_OK)
        self.assertIsNone(r)


class TestChangelogAppendOnly(unittest.TestCase):
    BASE = ("# Governance changelog\n\n## Entries\n\n"
            "- 2026-07-26 | skills/a/SKILL.md | one | scribe | a1b2c3d\n")

    def test_append_is_allowed(self):
        new = self.BASE + "- 2026-07-27 | skills/a/SKILL.md | two | scribe | b2c3d4e\n"
        self.assertTrue(validate._changelog_append_only(self.BASE, new))

    def test_identical_is_allowed(self):
        self.assertTrue(validate._changelog_append_only(self.BASE, self.BASE))

    def test_edited_entry_rejected(self):
        new = self.BASE.replace("one", "something else entirely")
        self.assertFalse(validate._changelog_append_only(self.BASE, new))

    def test_removed_entry_rejected(self):
        new = "# Governance changelog\n\n## Entries\n\n"
        self.assertFalse(validate._changelog_append_only(self.BASE, new))

    def test_reordered_entries_rejected(self):
        base = self.BASE + "- 2026-07-27 | skills/a/SKILL.md | two | scribe | b2c3d4e\n"
        new = ("# Governance changelog\n\n## Entries\n\n"
               "- 2026-07-27 | skills/a/SKILL.md | two | scribe | b2c3d4e\n"
               "- 2026-07-26 | skills/a/SKILL.md | one | scribe | a1b2c3d\n")
        self.assertFalse(validate._changelog_append_only(base, new))

    def test_prepended_entry_rejected(self):
        new = ("# Governance changelog\n\n## Entries\n\n"
               "- 2026-07-20 | skills/a/SKILL.md | zero | scribe | 0a1b2c3\n"
               "- 2026-07-26 | skills/a/SKILL.md | one | scribe | a1b2c3d\n")
        self.assertFalse(validate._changelog_append_only(self.BASE, new))

    def test_crlf_base_is_not_a_phantom_rewrite(self):
        self.assertTrue(validate._changelog_append_only(self.BASE.replace("\n", "\r\n"), self.BASE))


PIN_OK = "---\nschema_version: 1\ngenerated_by_commit: abc1234\n---\n"

CHANGELOG_OK = ("# Governance changelog\n\n## Entries\n\n"
                "<!-- appended by the auto-apply track; none yet -->\n")


def _proposal(target, radius="escalating"):
    return ("---\ntarget: %s\nblast_radius: %s\n"
            "reason: The description overlaps another skill and misroutes selection\n"
            "evidence:\n  - memory/onboarding-baseline.md\nstatus: pending\n---\n"
            "# Proposal\n\n## Diff\n\n    -old\n    +new\n\n## Why\n\nBecause.\n"
            % (target, radius))


class TestBlastRadiusDiff(unittest.TestCase):
    """The #18 tripwire. Scoped to governed roots — a directory carrying a #21
    groundwork.pin — so every fixture repo plants one."""

    def _repo(self, d, pin_at=""):
        _git(d, "init", "-q")
        _git(d, "config", "user.email", "t@t.t")
        _git(d, "config", "user.name", "t")
        pre = (pin_at + "/") if pin_at else ""
        _write(d, pre + "groundwork.pin", PIN_OK)
        _write(d, pre + "skills/weekly-digest/SKILL.md", SKILL_T1)
        _write(d, pre + "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
        _write(d, pre + "governance/constitution/access.md", RULE_OK)
        _write(d, pre + "governance/changelog.md", CHANGELOG_OK)
        _write(d, pre + "memory/onboarding-baseline.md", MEM_OK)
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "base")
        return pre

    def test_unchanged_repo_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            self.assertEqual(validate.blast_radius_diff_findings(d, "HEAD"), [])

    def test_no_pin_means_dormant(self):
        # The engine repo carries no pin: the tripwire must not fire at all.
        with tempfile.TemporaryDirectory() as d:
            _git(d, "init", "-q")
            _git(d, "config", "user.email", "t@t.t")
            _git(d, "config", "user.name", "t")
            _write(d, "governance/constitution/access.md", RULE_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "base")
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            self.assertEqual(validate.blast_radius_diff_findings(d, "HEAD"), [])

    def test_rule_edit_without_proposal_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                and "access.md" in f.path for f in findings))

    def test_rule_edit_with_escalating_proposal_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            _write(d, "proposals/p1.md", _proposal("governance/constitution/access.md"))
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if f.level == "ERROR"], [])

    def test_declared_vs_actual_mismatch_errors(self):
        # The headline #18 case: a rule edit smuggled under a track1-body label.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            _write(d, "proposals/p1.md",
                   _proposal("governance/constitution/access.md", "track1-body"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "declared-vs-actual" in f.message
                                for f in findings))

    def test_track2_body_edit_needs_a_proposal(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/onboarding-orchestration/SKILL.md",
                   SKILL_OK.replace("# Onboarding orchestration",
                                    "# Onboarding orchestration\n\nAn added paragraph."))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_description_edit_under_track1_label_is_a_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Summarize the week's open threads for the team channel",
                                    "Summarize anything at all"))
            _write(d, "proposals/p1.md",
                   _proposal("skills/weekly-digest/SKILL.md", "track1-body"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "declared-vs-actual" in f.message
                                for f in findings))

    def test_owner_card_edit_escalates(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/owner-card.md", CARD_OK)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "owner-card.md" in f.path
                                for f in findings))

    def test_track1_body_edit_without_changelog_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Collect the week's open threads and summarize them.",
                                    "Collect the week's open threads and note blockers."))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            self.assertTrue(any(f.level == "WARN" and "changelog" in f.message for f in findings))

    def test_track1_body_edit_with_appended_changelog_line_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Collect the week's open threads and summarize them.",
                                    "Collect the week's open threads and note blockers."))
            _write(d, "governance/changelog.md", CHANGELOG_OK +
                   "- 2026-07-26 | skills/weekly-digest/SKILL.md | note blockers | scribe | a1b2c3d\n")
            self.assertEqual(validate.blast_radius_diff_findings(d, "HEAD"), [])

    def test_changelog_rewrite_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/changelog.md",
                   CHANGELOG_OK.replace("appended by the auto-apply track", "rewritten"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "append-only" in f.message
                                for f in findings))

    def test_changelog_deletion_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "governance", "changelog.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "changelog" in f.message
                                for f in findings))

    def test_new_rule_file_escalates(self):
        # git diff never lists an untracked file; the working-tree union must.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/new-rule.md", RULE_OK)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "new-rule.md" in f.path
                                for f in findings))

    def test_deleted_rule_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "governance", "constitution", "access.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            self.assertTrue(any(f.level == "WARN" and "deleted" in f.message for f in findings))

    def test_removing_the_pin_does_not_ungovern_the_change(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "groundwork.pin"))
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_proposal_target_escaping_the_governed_root_does_not_match(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="company")
            _write(d, "company/governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            _write(d, "company/proposals/p1.md",
                   _proposal("../governance/constitution/access.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_nested_governed_root_is_scoped(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="company")
            _write(d, "company/governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            _write(d, "company/proposals/p1.md",
                   _proposal("governance/constitution/access.md"))
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if f.level == "ERROR"], [])

    def test_symlinked_rule_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            p = os.path.join(d, "governance", "constitution", "access.md")
            os.remove(p)
            os.symlink(os.path.join(d, "memory", "onboarding-baseline.md"), p)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message for f in findings))

    def test_non_utf8_working_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write_bytes(d, "governance/constitution/access.md", b"---\nowner: x\n---\n\xff\xfe bad\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_unknown_base_ref_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            findings = validate.blast_radius_diff_findings(d, "no-such-ref")
            self.assertTrue(any(f.level == "ERROR" and "base ref" in f.message for f in findings))

    def test_workbench_trees_are_out_of_scope(self):
        # tests/ and docs/superpowers/ are the validator's own harness.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "tests/fixtures/governance/constitution/x.md", RULE_OK)
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if "tests/" in f.path], [])

    def test_cli_wires_the_tripwire(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            self.assertEqual(validate.main(["validate.py", d, "--diff", "HEAD"]), 1)

    # --- Codex round-1 regressions ---

    def test_nested_pin_cannot_shadow_the_governing_root(self):
        # Codex r1: a pin planted INSIDE a skill package makes the innermost
        # root's relative path unclassifiable; the outer root must still govern.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/groundwork.pin", PIN_OK)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Summarize the week's open threads for the team channel",
                                    "Summarize anything at all"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                and "SKILL.md" in f.path for f in findings))

    def test_case_variant_rule_dir_still_governed(self):
        # Codex r1: Governance/ must not launder a rule out of the routing
        # domain (on a case-folding filesystem it IS governance/).
        self.assertEqual(validate._governed_class("Governance/Constitution/access.md"), "rule")
        self.assertEqual(validate._governed_class("SKILLS/x/helper.md"), "skill-other")
        # Only the canonical SKILL.md spelling is auto-apply-eligible.
        self.assertEqual(validate._governed_class("skills/x/Skill.md"), "skill-other")
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "Governance/constitution/evil.md", RULE_OK)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "evil.md" in f.path for f in findings))

    def test_symlinked_proposal_file_does_not_authorize(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            _write(d, "elsewhere.md", _proposal("governance/constitution/access.md"))
            os.makedirs(os.path.join(d, "proposals"))
            os.symlink(os.path.join(d, "elsewhere.md"), os.path.join(d, "proposals", "p1.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_unreadable_ancestor_dir_fails_closed_not_deletion_warn(self):
        con = None
        try:
            with tempfile.TemporaryDirectory() as d:
                self._repo(d)
                con = os.path.join(d, "governance", "constitution")
                os.chmod(con, 0o000)
                findings = validate.blast_radius_diff_findings(d, "HEAD")
                os.chmod(con, 0o755)
                con = None
                self.assertTrue(any(f.level == "ERROR" and "unreadable" in f.message
                                    for f in findings))
                self.assertFalse(any(f.level == "WARN" and "deleted" in f.message
                                     for f in findings))
        finally:
            if con is not None:
                os.chmod(con, 0o755)

    def test_new_rule_hidden_in_unreadable_dir_errors(self):
        sub = None
        try:
            with tempfile.TemporaryDirectory() as d:
                self._repo(d)
                sub = os.path.join(d, "governance", "constitution", "sub")
                os.makedirs(sub)
                _write(d, "governance/constitution/sub/new-rule.md", RULE_OK)
                os.chmod(sub, 0o000)
                findings = validate.blast_radius_diff_findings(d, "HEAD")
                os.chmod(sub, 0o755)
                sub = None
                self.assertTrue(any(f.level == "ERROR" and "cannot scan" in f.message
                                    for f in findings))
        finally:
            if sub is not None:
                os.chmod(sub, 0o755)

    def test_fatal_context_error_printed_once(self):
        # Codex r1: both --diff modes resolve the context; the identical fatal
        # ERROR must reach the report once.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                validate.main(["validate.py", d, "--diff", "no-such-ref"])
            self.assertEqual(buf.getvalue().count("base ref not found"), 1)

    # --- Codex round-2 regressions ---

    def test_inner_pin_cannot_downgrade_an_outer_rule(self):
        # Codex r2: a pin planted at governance/constitution/ reshapes the
        # inner path of a nested rule into skills/x/SKILL.md (track-1 shaped).
        # The change must still be licensed under the OUTER root, where it is
        # a rule — enforcement runs under every containing governed root.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/skills/x/SKILL.md", SKILL_T1)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "nested rule")
            _write(d, "governance/constitution/groundwork.pin", PIN_OK)
            _write(d, "governance/constitution/skills/x/SKILL.md",
                   SKILL_T1.replace("Collect the week's open threads and summarize them.",
                                    "A quietly different body."))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_case_renamed_governed_root_still_governs(self):
        # Codex r2: renaming pinned company/ to Company/ (and dropping the pin)
        # must not walk the tree out of its governed root — containment
        # casefolds, and the base pin still governs.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="company")
            os.rename(os.path.join(d, "company"), os.path.join(d, "Company"))
            os.remove(os.path.join(d, "Company", "groundwork.pin"))
            _write(d, "Company/governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    # --- Codex round-3 regressions ---

    def test_length_changing_casefold_rename_still_governs(self):
        # Codex r3: ß casefolds to ss, so whole-string folding with an
        # unfolded-length slice misaligns the inner path. Component-wise
        # matching must still govern the renamed tree.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="straße")
            _write(d, "STRASSE/governance/constitution/new.md", RULE_OK)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_nfd_variant_of_governed_root_still_governs(self):
        # Codex r3: git reports NFC while a mac filesystem lists NFD; the two
        # spellings of the same root must not fall out of containment.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="café")
            _write(d, "cafe\u0301" + "/governance/constitution/new.md", RULE_OK)  # NFD on disk
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_distinct_case_sibling_roots_do_not_cross_demand(self):
        # Codex r3: on a case-sensitive filesystem, company/ and Company/ can
        # be two REAL pinned roots. The exact-match root is authoritative —
        # demanding the other root's proposal would be an unsatisfiable gate.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="company")
            try:
                os.makedirs(os.path.join(d, "Company"))
            except FileExistsError:
                self.skipTest("case-insensitive filesystem")
            if os.path.samefile(os.path.join(d, "Company"), os.path.join(d, "company")):
                self.skipTest("case-insensitive filesystem")
            _write(d, "Company/groundwork.pin", PIN_OK)
            _write(d, "Company/governance/constitution/access.md", RULE_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "sibling root")
            _write(d, "Company/governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            _write(d, "Company/proposals/p1.md",
                   _proposal("governance/constitution/access.md"))
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if f.level == "ERROR"], [])

    def test_git_launch_failure_is_a_finding_not_a_crash(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            real_run = validate.subprocess.run

            def broken_run(*a, **k):
                raise OSError("cannot spawn git")
            validate.subprocess.run = broken_run
            try:
                findings = validate.blast_radius_diff_findings(d, "HEAD")
            finally:
                validate.subprocess.run = real_run
            self.assertTrue(any(f.level == "ERROR" for f in findings))


class TestAgentsChain(unittest.TestCase):
    def test_no_agents_file_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# x\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_small_chain_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# Root\n")
            _write(d, "pkg/AGENTS.md", "# Pkg\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_oversized_root_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (32 * 1024 + 1))
            findings = validate.check_agents_chain(d)
            self.assertTrue(any(f.level == "ERROR" and "project_doc_max_bytes" in f.message
                                for f in findings))

    def test_chain_accumulates_across_levels(self):
        # Neither file is over the cap alone; concatenated they are.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (20 * 1024))
            _write(d, "pkg/AGENTS.md", "y" * (20 * 1024))
            findings = validate.check_agents_chain(d)
            self.assertTrue(any(f.level == "ERROR" and "pkg/AGENTS.md" in f.path
                                for f in findings))
            self.assertFalse(any(f.path == "AGENTS.md" for f in findings))

    def test_override_file_takes_precedence(self):
        # Codex reads AGENTS.override.md instead of AGENTS.md at each level.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (32 * 1024 + 1))
            _write(d, "AGENTS.override.md", "small\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_empty_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "")
            _write(d, "pkg/AGENTS.md", "# Pkg\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_workbench_trees_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "tests/AGENTS.md", "x" * (32 * 1024 + 1))
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_stat_able_but_unreadable_file_errors(self):
        # A bare stat succeeds on an unreadable file; the chain must still
        # fail closed — a file the check cannot open cannot be verified.
        # Stubbed open() rather than chmod(0): root and Windows both ignore
        # POSIX permission bits, which would make a chmod-based test vacuous.
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "AGENTS.md", "# a\n")
            real_open = open

            def broken_open(path, *a, **k):
                if os.path.realpath(path) == os.path.realpath(p):
                    raise PermissionError("unreadable")
                return real_open(path, *a, **k)
            validate.open = broken_open
            try:
                findings = validate.check_agents_chain(d)
            finally:
                del validate.open
            self.assertTrue(any(f.level == "ERROR" and "cannot size" in f.message
                                for f in findings))


CURSOR_ALWAYS = "---\ndescription: d\nalwaysApply: true\n---\n\nSee AGENTS.md.\n"
GEMINI_POINTER = "@./AGENTS.md\n"


class TestAlwaysLoadedBudget(unittest.TestCase):
    def test_small_repo_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# x\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_oversized_agents_file_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (21_000 * 4))
            findings = validate.check_always_loaded_budget(d)
            self.assertTrue(any(f.level == "WARN" for f in findings))

    def test_imports_are_followed_and_counted(self):
        # Imports do not reduce context: the imported file must be measured.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@big.md\n")
            _write(d, "big.md", "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_import_inside_backticks_is_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "Mention `@big.md` literally.\n")
            _write(d, "big.md", "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_import_cycle_terminates(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@a.md\n")
            _write(d, "a.md", "@CLAUDE.md\n")
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_always_apply_cursor_rule_counts(self):
        # .cursor/ is a dot-directory: iter_files never sees it, so this proves
        # the check reads it explicitly rather than scanning nothing.
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".cursor/rules/big.mdc",
                   "---\ndescription: d\nalwaysApply: true\n---\n" + "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_non_always_apply_cursor_rule_is_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".cursor/rules/big.mdc",
                   "---\ndescription: d\nalwaysApply: false\n---\n" + "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_path_scoped_claude_rule_is_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".claude/rules/scoped.md",
                   "---\npaths:\n  - \"src/**\"\n---\n" + "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_unscoped_claude_rule_counts(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".claude/rules/always.md", "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_skill_description_is_capped_not_summed_whole(self):
        # A huge SKILL.md body is NOT always-loaded; only its description is,
        # and only up to Claude Code's 1,536-char listing truncation.
        with tempfile.TemporaryDirectory() as d:
            _write_package(d, skill=SKILL_OK + "\n" + "x" * (60_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_skill_description_contribution_is_actually_measured(self):
        # Guards against the enumeration being deleted outright: the capped
        # description must appear as an aggregate item with its exact bytes.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/x/SKILL.md",
                   "---\nname: x\ndescription: %s\n---\nbody\n" % ("d" * 2000))
            items, findings = validate._always_loaded_bytes(d)
            self.assertEqual(findings, [])
            contrib = dict(items)[os.path.join("skills", "x", "SKILL.md") + " (description)"]
            self.assertEqual(contrib, validate.SKILL_DESCRIPTION_CAP)

    def test_multibyte_description_cap_is_characters_not_bytes(self):
        # Claude Code truncates the listing at 1,536 CHARACTERS. 2,000 'é's
        # survive truncation as 1,536 chars = 3,072 UTF-8 bytes; a bytes-side
        # min() would report only 1,536 and undercount the surface.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/x/SKILL.md",
                   "---\nname: x\ndescription: %s\n---\nbody\n" % ("é" * 2000))
            items, _findings = validate._always_loaded_bytes(d)
            contrib = dict(items)[os.path.join("skills", "x", "SKILL.md") + " (description)"]
            self.assertEqual(contrib, 2 * validate.SKILL_DESCRIPTION_CAP)

    def test_import_at_four_hops_is_counted(self):
        # "a maximum depth of four hops": a file four import edges from
        # CLAUDE.md still loads at launch and must be measured.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@a.md\n")
            _write(d, "a.md", "@b.md\n")
            _write(d, "b.md", "@c.md\n")
            _write(d, "c.md", "@d.md\n")
            _write(d, "d.md", "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_import_at_five_hops_is_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@a.md\n")
            _write(d, "a.md", "@b.md\n")
            _write(d, "b.md", "@c.md\n")
            _write(d, "c.md", "@d.md\n")
            _write(d, "d.md", "@e.md\n")
            _write(d, "e.md", "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_shared_import_is_expanded_at_its_shallowest_depth(self):
        # Diamond: shared.md is first declared via a 4-hop chain (its child
        # would land past the hop budget) and again at 2 hops. A depth-first
        # seen-set would lock in the deep visit and never count big.md; BFS
        # must expand shared.md at its shallowest depth.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@a.md\n@x.md\n")
            _write(d, "a.md", "@b.md\n")
            _write(d, "b.md", "@c.md\n")
            _write(d, "c.md", "@shared.md\n")
            _write(d, "x.md", "@shared.md\n")
            _write(d, "shared.md", "@big.md\n")
            _write(d, "big.md", "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_unreadable_root_agents_md_is_a_finding_in_the_aggregate(self):
        # The aggregate itself must fail closed on the root instruction file,
        # not rely on check_agents_chain being run alongside it.
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "AGENTS.md", "# a\n")
            real_open = open

            def broken_open(path, *a, **k):
                if os.path.realpath(path) == os.path.realpath(p):
                    raise PermissionError("unreadable")
                return real_open(path, *a, **k)
            validate.open = broken_open
            try:
                findings = validate.check_always_loaded_budget(d)
            finally:
                del validate.open
            self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_malformed_claude_rule_is_a_finding_not_silence(self):
        # Nothing else scans dot-directories, so a rule this check cannot
        # parse must surface here rather than silently leave the aggregate.
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".claude/rules/bad.md", "---\nnever closed\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_always_loaded_budget(d)))

    def test_error_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (50_000 * 4))
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_always_loaded_budget(d)))


class TestRootFiles(unittest.TestCase):
    def test_no_agents_md_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "# anything\n")
            self.assertEqual(validate.check_root_files(d), [])

    def test_import_satisfies_the_check(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", GEMINI_POINTER)
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])

    def test_missing_gemini_md_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            findings = validate.check_root_files(d)
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            gem = [f for f in findings if f.path == "GEMINI.md"]
            self.assertEqual(len(gem), 1, "one GEMINI finding, not several")
            self.assertEqual(gem[0].level, "WARN")
            self.assertIn("Gemini CLI reads GEMINI.md", gem[0].message)

    def test_gemini_pointer_satisfies_the_check(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", GEMINI_POINTER)
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])

    def test_bare_gemini_import_also_satisfies(self):
        # The invariant is 'this file imports the canonical instructions',
        # not 'it is spelled the way the engine spells it'.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])

    def test_gemini_md_that_only_mentions_agents_warns(self):
        # A mention imports nothing: Gemini concatenates the file it reads and
        # follows '@' imports. 'See AGENTS.md' loads no instructions.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "See AGENTS.md for how this repo works.\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                and "does not import" in f.message
                                for f in findings))

    def test_gemini_absolute_import_does_not_satisfy(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "@%s\n" % os.path.join(d, "AGENTS.md"))
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                for f in validate.check_root_files(d)))

    def test_gemini_parent_escape_does_not_satisfy(self):
        # Codex 4.2 r1: '@../AGENTS.md' has the right basename and imports a
        # file OUTSIDE the repo. The import must resolve to the root file,
        # not merely be named like it.
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "repo")
            _write(repo, "AGENTS.md", "# a\n")
            _write(repo, "CLAUDE.md", "@AGENTS.md\n")
            _write(repo, "GEMINI.md", "@../AGENTS.md\n")
            _write(repo, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            _write(d, "AGENTS.md", "# the outer file the import actually reaches\n")
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                and "does not import" in f.message
                                for f in validate.check_root_files(repo)))

    def test_gemini_nested_same_basename_does_not_satisfy(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "@nested/AGENTS.md\n")
            _write(d, "nested/AGENTS.md", "# not the canonical file\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                and "does not import" in f.message
                                for f in validate.check_root_files(d)))

    def test_gemini_import_of_a_missing_path_does_not_satisfy(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "@does-not-exist/AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                and "does not import" in f.message
                                for f in validate.check_root_files(d)))

    def test_symlinked_gemini_md_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            os.symlink(os.path.join(d, "AGENTS.md"), os.path.join(d, "GEMINI.md"))
            self.assertEqual(validate.check_root_files(d), [])

    def test_gemini_symlink_to_the_wrong_target_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "other.md", "# o\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            os.symlink(os.path.join(d, "other.md"), os.path.join(d, "GEMINI.md"))
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                for f in validate.check_root_files(d)))

    def test_unreadable_gemini_md_does_not_accuse(self):
        # Slice 4.1's lesson, the paired direction: a diagnostic that cannot
        # see must say nothing rather than assert a fact it did not inspect.
        # The read failure is its own finding; no drift claim rides on it.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            with open(os.path.join(d, "GEMINI.md"), "wb") as fh:
                fh.write(b"\xff\xfe not utf-8 \xff")
            findings = validate.check_root_files(d)
            # ERROR, asserted deliberately (Codex 4.2 r1): the pointer rule is
            # WARN-class, but a non-UTF-8 root markdown file is corrupt beyond
            # the pointer question and the corpus scans ERROR on it anyway.
            self.assertTrue(any(f.path == "GEMINI.md" and f.level == "ERROR"
                                and "UTF-8" in f.message
                                for f in findings), "the read failure is silent")
            self.assertFalse(any("does not import" in f.message for f in findings),
                             "the check accused a file it could not read")

    def test_oserror_reading_gemini_md_does_not_accuse(self):
        # The other unreadable direction (Codex 4.2 r1): the invalid-UTF-8
        # case exercises UnicodeError, so an actual I/O failure was untested.
        # Same rule — the read failure is its own finding, and no drift claim
        # rides on content nobody read.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", GEMINI_POINTER)
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            gem = os.path.join(d, "GEMINI.md")
            real_open = open
            def broken_open(path, *args, **kwargs):
                if os.path.abspath(str(path)) == os.path.abspath(gem):
                    raise OSError("simulated read failure")
                return real_open(path, *args, **kwargs)
            validate.open = broken_open
            try:
                findings = validate.check_root_files(d)
            finally:
                del validate.open
            self.assertTrue(any(f.path == "GEMINI.md" and f.level == "ERROR"
                                and "could not read" in f.message
                                for f in findings), "the I/O failure is silent")
            self.assertFalse(any("does not import" in f.message for f in findings),
                             "the check accused a file it could not read")

    def test_gemini_warn_fires_without_any_cursor_rules(self):
        # ORDERING PROBE, and it is the load-bearing one: the .cursor/rules
        # branch early-returns when the directory is absent. A GEMINI check
        # placed after it would be silent on exactly the repos that need it
        # most, with a green gate.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.path == "GEMINI.md" for f in findings),
                            "the GEMINI check sits after the .cursor early return")
            self.assertTrue(any("cursor" in f.path for f in findings))

    def test_engine_root_carries_its_gemini_pointer(self):
        # The 7-WARN trigger, asserted rather than assumed.
        self.assertEqual([f for f in validate.check_root_files(str(REPO))
                          if f.path == "GEMINI.md"], [])

    def test_missing_claude_md_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            self.assertTrue(any(f.level == "ERROR" and "CLAUDE.md" in f.path
                                for f in validate.check_root_files(d)))

    def test_claude_md_without_import_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "# separate instructions\n")
            self.assertTrue(any(f.level == "ERROR" and "drift" in f.message
                                for f in validate.check_root_files(d)))

    def test_import_in_backticks_does_not_satisfy(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "Write `@AGENTS.md` to import it.\n")
            self.assertTrue(any(f.level == "ERROR" and "drift" in f.message
                                for f in validate.check_root_files(d)))

    def test_symlinked_claude_md_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            os.symlink(os.path.join(d, "AGENTS.md"), os.path.join(d, "CLAUDE.md"))
            self.assertEqual([f for f in validate.check_root_files(d)
                              if f.level == "ERROR"], [])

    def test_symlink_to_the_wrong_target_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "other.md", "# o\n")
            os.symlink(os.path.join(d, "other.md"), os.path.join(d, "CLAUDE.md"))
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_missing_cursor_rules_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            findings = validate.check_root_files(d)
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            self.assertTrue(any(f.level == "WARN" and "cursor" in f.path for f in findings))

    def test_cursor_rule_without_always_apply_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc",
                   "---\ndescription: d\nalwaysApply: false\n---\n\nSee AGENTS.md.\n")
            self.assertTrue(any(f.level == "WARN" for f in validate.check_root_files(d)))

    def test_cursor_rule_not_referencing_agents_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc",
                   "---\ndescription: d\nalwaysApply: true\n---\n\nUnrelated guidance.\n")
            self.assertTrue(any(f.level == "WARN" for f in validate.check_root_files(d)))

    def test_wired_into_validate(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "# drifted\n")
            self.assertTrue(any(f.level == "ERROR" and "drift" in f.message
                                for f in validate.validate(d)))


class TestStripCode(unittest.TestCase):
    def _imports(self, text):
        return validate._IMPORT.findall(validate._strip_code(text))

    def test_plain_import_is_seen(self):
        self.assertEqual(self._imports("@AGENTS.md\n"), ["AGENTS.md"])

    def test_backtick_fence_is_stripped(self):
        self.assertEqual(self._imports("```\n@AGENTS.md\n```\n"), [])

    def test_tilde_fence_is_stripped(self):
        # The fail-open this fold closes: a ~~~ block is a CommonMark fenced
        # code block, so Claude Code imports nothing from it.
        self.assertEqual(self._imports("~~~\n@AGENTS.md\n~~~\n"), [])

    def test_four_backtick_fence_is_stripped(self):
        self.assertEqual(self._imports("````\n@AGENTS.md\n````\n"), [])

    def test_fence_with_info_string_is_stripped(self):
        self.assertEqual(self._imports("```markdown\n@AGENTS.md\n```\n"), [])

    def test_inner_shorter_fence_does_not_close_outer(self):
        self.assertEqual(self._imports("````\n```\n@AGENTS.md\n```\n````\n"), [])

    def test_single_backtick_span_is_stripped(self):
        self.assertEqual(self._imports("Write `@AGENTS.md` here.\n"), [])

    def test_double_backtick_span_is_stripped(self):
        self.assertEqual(self._imports("Write ``@AGENTS.md`` here.\n"), [])

    def test_unclosed_span_leaves_text(self):
        # An unterminated backtick run is literal text, so the import is real.
        self.assertEqual(self._imports("A ` stray tick then @AGENTS.md\n"), ["AGENTS.md"])

    def test_import_after_a_closed_fence_is_seen(self):
        self.assertEqual(self._imports("```\ncode\n```\n@AGENTS.md\n"), ["AGENTS.md"])

    def test_unclosed_fence_swallows_to_end(self):
        # Matches CommonMark: an unclosed fence runs to end of document.
        self.assertEqual(self._imports("```\n@AGENTS.md\n"), [])

    def test_multiline_span_is_stripped(self):
        # Codex round 1: a CommonMark code span may cross line endings within a
        # paragraph, so per-line span scanning was a fail-open on the drift check.
        self.assertEqual(self._imports("`documentation:\n@AGENTS.md\n`\n"), [])

    def test_span_does_not_cross_a_blank_line(self):
        # A blank line ends the paragraph, so the backticks never pair and the
        # import between them is real.
        self.assertEqual(
            self._imports("A ` stray\n\n@AGENTS.md\n\nanother ` tick\n"),
            ["AGENTS.md"])

    def test_longer_run_tail_is_not_a_closer(self):
        # Codex round 1: a 2-backtick opener must not be closed by the tail of
        # a 5-backtick run — the closer is the NEXT run of exactly N.
        self.assertEqual(self._imports("`` @AGENTS.md `````\n"), ["AGENTS.md"])

    def test_backtick_info_string_is_not_a_fence(self):
        # Codex round 1: a backtick fence's info string cannot contain a
        # backtick (CommonMark), so this line is a paragraph with a code span,
        # not a fence opener that swallows the rest of the file.
        self.assertEqual(
            self._imports("``` `x` ```\n@AGENTS.md\n"), ["AGENTS.md"])

    def test_stripped_span_does_not_join_its_neighbors(self):
        # Codex round 2: stripping the span out of "@`doc:\n`AGENTS.md" must
        # not synthesize a real-looking "@AGENTS.md" import from the fragments
        # on either side — that would satisfy the drift check while Claude Code
        # imported nothing (fail-open).
        self.assertEqual(self._imports("@`documentation:\n`AGENTS.md\n"), [])
        self.assertEqual(self._imports("x`span`@AGENTS.md\n"), [])

    def test_real_import_after_a_span_is_still_seen(self):
        # The placeholder must not hide a genuinely whitespace-separated import.
        self.assertEqual(self._imports("See `x` @AGENTS.md\n"), ["AGENTS.md"])

    def test_blockquoted_fence_is_stripped(self):
        # Codex round 3: a fence nested in a blockquote is a real CommonMark
        # fenced block, so the import inside it is documentation, not loaded.
        self.assertEqual(self._imports("> ~~~\n> @AGENTS.md\n> ~~~\n"), [])

    def test_list_item_fence_is_stripped(self):
        self.assertEqual(self._imports("- ```\n  @AGENTS.md\n  ```\n"), [])

    def test_quote_end_closes_its_fence(self):
        # Leaving the blockquote closes the fence (a code block cannot lazily
        # continue), and the NEW top-level fence then swallows the import.
        self.assertEqual(
            self._imports("> ~~~\ntext\n~~~\n@AGENTS.md\n~~~\n"), [])

    def test_import_after_a_closed_quoted_fence_is_seen(self):
        self.assertEqual(
            self._imports("> ~~~\n> code\n> ~~~\n@AGENTS.md\n"), ["AGENTS.md"])

    def test_quoted_fence_line_does_not_close_a_top_level_fence(self):
        # Inside a top-level fence, '> ```' is content, not a closer.
        self.assertEqual(
            self._imports("```\n> ```\n@AGENTS.md\n```\n"), [])

    def test_unquoted_fence_after_quoted_opener_reopens(self):
        # Codex round 4: '> ~~~' then bare '~~~' — the blockquote (and its
        # fence) end BEFORE the bare line, which then opens a NEW top-level
        # fence swallowing the import; consuming it as a closer failed open.
        self.assertEqual(self._imports("> ~~~\n~~~\n@AGENTS.md\n~~~\n"), [])

    def test_nested_quote_dedent_reopens_at_outer_level(self):
        # '> > ~~~' then '> ~~~': the inner quote ends, closing its fence, and
        # a new fence opens at the outer quote level — the import is inside it.
        self.assertEqual(
            self._imports("> > ~~~\n> ~~~\n> @AGENTS.md\n"), [])

    def test_deeper_quoted_fence_line_is_content(self):
        # Inside a '> ~~~' fence, a '> > ~~~' line is literal content; the
        # fence still closes at '> ~~~' and the later import is real.
        self.assertEqual(
            self._imports("> ~~~\n> > ~~~\n> ~~~\n@AGENTS.md\n"),
            ["AGENTS.md"])

    def test_list_boundary_in_quote_reopens(self):
        # Codex round 5: '> - ~~~' then '> ~~~' — the list item ends (no
        # continuation indent), so the bare fence line is a NEW opener at the
        # quote level, not the old fence's closer; the import is inside it.
        self.assertEqual(
            self._imports("> - ~~~\n> ~~~\n> @AGENTS.md\n> ~~~\n"), [])

    def test_ordered_list_quote_continuation_indent(self):
        # Codex round 5: '10. > ~~~' continues at four columns, so the quoted
        # fence stays open and the import inside it is documentation.
        self.assertEqual(
            self._imports("10. > ~~~\n    > @AGENTS.md\n    > ~~~\n"), [])

    def test_tabbed_quote_fence_is_stripped(self):
        # Tabs participate in block structure (tab stop 4).
        self.assertEqual(
            self._imports(">\t~~~\n>\t@AGENTS.md\n>\t~~~\n"), [])

    def test_blank_line_inside_a_list_fence_is_content(self):
        # A blank line does not end a fenced code block in a list item.
        self.assertEqual(
            self._imports("- ~~~\n  code\n\n  @AGENTS.md\n  ~~~\n"), [])

    def test_fence_in_open_list_item_is_stripped(self):
        # Codex round 6: the list item is opened by an EARLIER line; the
        # fence line itself carries only continuation indentation, and is
        # still a real CommonMark fence inside the item.
        self.assertEqual(
            self._imports("10. note\n\n    ~~~\n    @AGENTS.md\n    ~~~\n"),
            [])

    def test_import_in_list_continuation_text_is_seen(self):
        # Persistent list context alone strips nothing — only a fence does.
        self.assertEqual(
            self._imports("- step\n\n    @AGENTS.md\n"), ["AGENTS.md"])

    def test_two_spaces_after_list_marker(self):
        # Codex round 7: 1-4 spaces may follow a list marker, and the item's
        # continuation width includes them.
        self.assertEqual(
            self._imports("-  note\n\n   ~~~\n   @AGENTS.md\n   ~~~\n"), [])
        self.assertEqual(
            self._imports("-  note\n\n      ~~~\n      @AGENTS.md\n      ~~~\n"),
            [])

    def test_marker_only_list_item(self):
        # Codex round 7: a bare '10.' (or '-') opens an EMPTY list item whose
        # content starts on the next line at marker width + 1.
        self.assertEqual(
            self._imports("10.\n    ~~~\n    @AGENTS.md\n    ~~~\n"), [])
        self.assertEqual(
            self._imports("-\n  ~~~\n  @AGENTS.md\n  ~~~\n"), [])

    def test_marker_with_five_plus_spaces_resets_continuation(self):
        # Codex round 8: 5+ spaces after a marker start indented CODE inside
        # the item, and continuation resets to marker width + 1 — a fence at
        # that indent is genuine and its import is documentation.
        self.assertEqual(
            self._imports("10.     seed\n\n    ~~~\n    @AGENTS.md\n    ~~~\n"),
            [])
        self.assertEqual(
            self._imports("-      seed\n\n  ~~~\n  @AGENTS.md\n  ~~~\n"), [])

    def test_marker_only_with_trailing_spaces(self):
        # An empty item keeps marker + 1 continuation even when the marker
        # line carries trailing spaces.
        self.assertEqual(
            self._imports("10.    \n    ~~~\n    @AGENTS.md\n    ~~~\n"), [])

    def test_fence_looking_indented_code_is_not_an_opener(self):
        # Codex round 9: '10.     ~~~' — the 5+-space content is indented
        # CODE, not a fence opener; treating it as one consumed the later
        # GENUINE fence as its closer and exposed the import.
        self.assertEqual(
            self._imports("10.     ~~~\n\n    ~~~\n    @AGENTS.md\n    ~~~\n"),
            [])
        self.assertEqual(
            self._imports("-      ```\n\n  ```\n  @AGENTS.md\n  ```\n"), [])

    def test_stale_list_context_ends_at_dedent(self):
        # Codex round 10: after 'outside' ends the list, '    ~~~' is TOP-
        # LEVEL indented code (live text), and '  ~~~' is a genuine fence —
        # stale list context must not turn the code line into a false fence
        # that steals the genuine opener.
        self.assertEqual(
            self._imports("- item\n\noutside\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_lazy_continuation_keeps_the_item_open(self):
        # A paragraph line may lazily continue the item, so the indented
        # fence after it is still inside the item.
        self.assertEqual(
            self._imports("- note\nlazy line\n  ~~~\n  @AGENTS.md\n  ~~~\n"),
            [])

    def test_import_after_a_dedent_closed_list_is_seen(self):
        self.assertEqual(
            self._imports("- item\n\noutside @AGENTS.md\n"), ["AGENTS.md"])

    def test_fence_interrupts_a_list_paragraph(self):
        # Codex round 11: a fence line is never lazy paragraph continuation —
        # fenced code interrupts a paragraph (CommonMark).
        self.assertEqual(
            self._imports("- note\n~~~\n@AGENTS.md\n~~~\n"), [])
        self.assertEqual(
            self._imports("- note\n```\n@AGENTS.md\n````\n"), [])

    def test_indented_code_item_has_no_lazy_continuation(self):
        # Codex round 11: '-     seed' starts the item with indented CODE, so
        # no paragraph is open and 'outside' cannot lazily continue the item —
        # the list ends, '    ~~~' is top-level indented code, and '  ~~~' is
        # a genuine fence.
        self.assertEqual(
            self._imports("-     seed\noutside\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_heading_in_item_opens_no_paragraph(self):
        # Codex round 12: '- # heading' is an ATX heading, not a paragraph —
        # 'outside' cannot lazily continue the item.
        self.assertEqual(
            self._imports("- # heading\noutside\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_thematic_break_in_item_opens_no_paragraph(self):
        self.assertEqual(
            self._imports("- ***\noutside\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_heading_interrupts_a_list_paragraph(self):
        # A heading line is never lazy continuation either.
        self.assertEqual(
            self._imports("- note\n# heading\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_dash_run_is_a_thematic_break_not_nested_lists(self):
        # CommonMark precedence: '- - -' is a thematic break, not list
        # markers — it must not open a list context.
        self.assertEqual(
            self._imports("- - -\noutside\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_setext_underline_closes_the_paragraph(self):
        # Codex round 13: a setext underline turns the paragraph into a
        # heading and closes it — 'outside' cannot lazily continue the item.
        self.assertEqual(
            self._imports("- heading\n  ===\noutside\n\n    ~~~\n\n  ~~~\n"
                          "@AGENTS.md\n  ~~~\n"), [])

    def test_html_block_content_is_not_a_fence(self):
        # Codex round 13: a fence-looking line inside a type-6 HTML block
        # (which runs to the blank line) is raw HTML content, not a fence
        # opener; the genuine fence comes after the blank.
        self.assertEqual(
            self._imports("- <div>\n  ~~~\n\n  ~~~\n  @AGENTS.md\n  ~~~\n"),
            [])
        self.assertEqual(
            self._imports("- <div>\n  ```\n\n  ```\n  @AGENTS.md\n  ```\n"),
            [])

    def test_import_inside_html_block_is_live(self):
        # Scanner (budget-side) model: raw HTML stays live text, which can
        # only OVERcount the aggregate. The §6 drift check independently
        # distrusts everything at or below the first HTML-looking line —
        # Claude Code's import walker skips every HTML token (round 18).
        self.assertEqual(
            self._imports("<div>\n@AGENTS.md\n</div>\n"), ["AGENTS.md"])

    def test_type1_html_block_spans_blank_lines(self):
        # Codex round 14: <script>/<pre> blocks run through blank lines to
        # their closing tag — a fence-looking line inside one is raw content,
        # and the genuine fence comes after the block ends.
        self.assertEqual(
            self._imports("<script>\n\n~~~\n</script>\n\n~~~\n@AGENTS.md\n"
                          "~~~\n"), [])
        self.assertEqual(
            self._imports("<pre>\n\n```\n</pre>\n\n```\n@AGENTS.md\n```\n"),
            [])

    def test_html_block_interrupts_a_list_paragraph(self):
        # Codex round 14: a type-6 start is a block start, never lazy
        # continuation of the item's paragraph.
        self.assertEqual(
            self._imports("- note\n<div>\n~~~\n\n~~~\n@AGENTS.md\n~~~\n"), [])

    def test_inline_html_in_prose_is_a_paragraph(self):
        # Codex round 14: '<em> prose' is paragraph text (type 7 needs the
        # tag alone on the line), so the following fence is genuine.
        self.assertEqual(
            self._imports("<em> prose\n~~~\n@AGENTS.md\n~~~\n"), [])

    def test_html_comment_block_spans_blanks(self):
        # Codex round 15: types 2-5 (comment, processing instruction,
        # declaration, CDATA) end on their own marker, spanning blank lines.
        self.assertEqual(
            self._imports("<!--\n~~~\n-->\n\n~~~\n@AGENTS.md\n~~~\n"), [])
        self.assertEqual(
            self._imports("<?php\n~~~\n?>\n\n~~~\n@AGENTS.md\n~~~\n"), [])

    def test_type1_closes_on_its_opening_line(self):
        self.assertEqual(
            self._imports("<script></script>\n~~~\n@AGENTS.md\n~~~\n"), [])

    def test_type7_attribute_may_contain_gt(self):
        # CommonMark allows '>' inside a quoted attribute value.
        self.assertEqual(
            self._imports("<em title=\">\">\n~~~\n\n~~~\n@AGENTS.md\n~~~\n"),
            [])

    def test_html_block_ends_with_its_list_item(self):
        # An HTML block ends when its containing list item ends (dedent).
        self.assertEqual(
            self._imports("- <div>\noutside\n~~~\n@AGENTS.md\n~~~\n"), [])


class TestDriftFenceBelt(unittest.TestCase):
    # The ERROR-level drift check accepts exactly one form: the FIRST content
    # line after optional leading front matter is the standalone '@AGENTS.md'
    # at under 4 columns of indent. Anything richer bets on Markdown token
    # classification (code, HTML, comments, multiline destinations — Codex
    # rounds 15-21) and is rejected: loud false ERROR at worst, never a
    # silent pass.
    def test_import_after_fenceish_line_does_not_satisfy_drift(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "```\nexample\n```\n@AGENTS.md\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_import_before_fence_satisfies_drift(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n\n```\nexample\n```\n")
            self.assertEqual([f for f in validate.check_root_files(d)
                              if f.level == "ERROR"], [])

    def test_span_crossing_the_cut_cannot_expose_an_import(self):
        # Codex round 16: truncating at a fence-ish line broke span pairing
        # ('`code\n@AGENTS.md\n    ~~~\nclose`' is ONE multiline code span,
        # so Claude imports nothing) and exposed the spanned import — the cut
        # now also stops at the first backtick-bearing line.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "`code\n@AGENTS.md\n    ~~~\nclose`\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_multiline_destination_is_not_trusted(self):
        # Codex round 20: '[x]:\n@AGENTS.md' makes the import a link-
        # definition destination (never scanned); link/image forms likewise.
        # Only the FIRST content line being the canonical import counts.
        for body in ("[x]:\n@AGENTS.md\n",
                     "[x](\n@AGENTS.md\n)\n",
                     "![x](\n@AGENTS.md\n)\n"):
            with tempfile.TemporaryDirectory() as d:
                _write(d, "AGENTS.md", "# a\n")
                _write(d, "CLAUDE.md", body)
                self.assertTrue(any(f.level == "ERROR"
                                    for f in validate.check_root_files(d)),
                                body)

    def test_import_not_on_first_content_line_is_not_trusted(self):
        # Deliberately strict (loud): any line above the import could
        # re-token it, so the canonical line must be the first content line.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "Intro prose.\n\n@AGENTS.md\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_indented_import_is_not_trusted(self):
        # Codex round 19: a 4-column-indented import is an indented CODE
        # token, and Claude Code's walker skips all code tokens.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "    @AGENTS.md\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_link_definition_import_is_not_trusted(self):
        # '[x]: @AGENTS.md' lexes as a link-reference definition whose href
        # is never scanned for imports.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "[x]: @AGENTS.md\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_frontmatter_import_is_not_trusted(self):
        # Claude Code strips leading YAML front matter before lexing imports.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "---\n@AGENTS.md\n---\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_import_after_frontmatter_is_trusted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "---\ntitle: t\n---\n\n@AGENTS.md\n")
            self.assertEqual([f for f in validate.check_root_files(d)
                              if f.level == "ERROR"], [])

    def test_dot_delimiter_does_not_close_frontmatter(self):
        # Codex round 21: the consumer's front-matter regex recognizes only
        # '---' as the closer, so '...' keeps the block open and the import
        # is swallowed with it.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "---\ntitle: x\n...\n@AGENTS.md\n---\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_inline_frontmatter_closer_matches_the_consumer(self):
        # Codex round 22: the consumer's lazy front-matter regex can close
        # MID-LINE ('key: ---'), so the body starts earlier than a line-based
        # reading — and here begins with an HTML block that swallows the
        # import.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md",
                   "---\nkey: ---\n<script>\n---\n@AGENTS.md\n</script>\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_unclosed_frontmatter_is_not_trusted(self):
        # No closer anywhere: the consumer strips nothing, and the literal
        # '---' becomes the first content line (not the canonical import).
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "---\ntitle: x\n@AGENTS.md\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_python_only_whitespace_is_not_a_frontmatter_delimiter(self):
        # Codex round 23: Python's \s has characters ECMAScript's lacks (U+0085,
        # U+001C-001F). '---\x85' is NOT a front-matter opener to the
        # consumer, so nothing may be stripped here — and the import below
        # sits inside a fence.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "---\x85\n```\n---\n@AGENTS.md\n```\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_python_only_whitespace_on_the_import_line(self):
        # '@AGENTS.md\x1c': the consumer keeps U+001C in the import target
        # and resolves 'AGENTS.md\x1c', not AGENTS.md.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\x1c\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_indented_frontmatter_opener_is_not_frontmatter(self):
        # The consumer requires the opener at byte zero; ' ---' is body text,
        # so nothing here is the canonical first content line.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", " ---\n<script>\n---\n@AGENTS.md\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_prose_wrapped_import_is_not_trusted(self):
        # Deliberately over-strict (loud): only the standalone canonical
        # '@AGENTS.md' line counts — token classification of anything richer
        # is exactly what rounds 15-19 showed to be unprovable.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "See @AGENTS.md for details\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_import_inside_html_block_is_not_trusted(self):
        # Codex round 18: Claude Code's import walker skips every HTML token,
        # so an import wrapped in <script>/<pre>/any raw HTML loads nothing.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "<script>\n@AGENTS.md\n</script>\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_import_before_html_is_trusted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n\n<div>note</div>\n")
            self.assertEqual([f for f in validate.check_root_files(d)
                              if f.level == "ERROR"], [])

    def test_commented_import_is_not_trusted(self):
        # Codex round 17: Claude Code removes HTML comments before scanning
        # for imports, so '<!-- @AGENTS.md -->' loads nothing — nothing at or
        # after the first '<!--' is trusted.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "<!-- @AGENTS.md -->\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_backtick_before_import_is_not_trusted(self):
        # '# `' then '` @AGENTS.md `': the import sits in a code span, and
        # nothing after a backtick-bearing line is trusted.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "# `\n` @AGENTS.md `\n")
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))


class TestAggregateDedupe(unittest.TestCase):
    def test_agents_md_counted_once(self):
        # AGENTS.md is both the root instruction file and CLAUDE.md's import.
        # No harness loads it twice; double-counting can only push a legitimate
        # repo past an ERROR threshold.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * 4000)
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            items, _findings = validate._always_loaded_bytes(d)
            paths = [lbl for lbl, _n in items]
            self.assertEqual(len(paths), len(set(paths)))
            self.assertEqual(sum(n for _l, n in items), 4000 + len("@AGENTS.md\n"))

    def test_symlinked_duplicate_counted_once(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * 4000)
            _write(d, "CLAUDE.md", "@alias.md\n")
            os.symlink(os.path.join(d, "AGENTS.md"), os.path.join(d, "alias.md"))
            items, _findings = validate._always_loaded_bytes(d)
            total = sum(n for _l, n in items)
            self.assertEqual(total, 4000 + len("@alias.md\n"))


class TestExecTableHardening(unittest.TestCase):
    """The adversarial corpus of Codex rounds 24-32, CONVERTED.

    Every input below is kept verbatim from the round that found it. Under the
    canonical grammar (#11 applied to the exec table) none of them is *handled*
    any more — each is *refused*, which is the stronger property: there is
    nothing left to disambiguate when only one table shape is legal. The
    assertions therefore check for an ERROR and for zero silently-accepted rows,
    rather than for a particular parse of a non-canonical shape."""

    def _exec(self, d, body, fn="sales"):
        _write(d, "ontologies/%s/_executive-view.md" % fn, body)

    def _errs(self, d):
        return [f for f in validate.check_ontology(d) if f.level == "ERROR"]

    def test_misspelled_header_is_rejected(self):
        # Codex round 24's ancestor: a header typo must never pass silently.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Diretcion |\n|---|---|\n| Forecast | up |\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_missing_table_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\nProse only, no table.\n")
            self.assertTrue(any(f.level == "ERROR" and "activity table" in f.message
                                for f in validate.check_ontology(d)))

    def test_header_present_but_no_rows_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_empty_file_is_silent(self):
        # An untouched worksheet stays silent (#5): only a file with content
        # that fails to parse is a problem.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "")
            self.assertEqual(validate.check_ontology(d), [])

    def test_two_column_empty_activity_table_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n|  | up |\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_canonical_empty_activity_cell_still_errors(self):
        # The empty-Activity check is not lost with the two-column shape: in
        # canonical form the row parses and reaches check_ontology (#5).
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction | Deep record |\n"
                          "|---|---|---|\n|  | up | — |\n")
            self.assertTrue(any("Activity" in f.message for f in self._errs(d)))

    def test_escaped_pipe_is_rejected(self):
        # Was: an escaped pipe must not split a cell. Now: escapes are not
        # canonical at all, so the cell cannot be smuggled either way.
        rows, findings = validate.parse_exec_table(
            "| Activity | Direction |\n|---|---|\n| Quote \\| order handoff | down |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_good_table_still_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, EXEC_OK)
            self.assertEqual(self._errs(d), [])

    def test_misdirection_header_is_rejected(self):
        # Codex round 24: 'Misdirection' must not select the table. Under the
        # canonical grammar no header but the exact one selects anything.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Misdirection |\n|---|\n| Forecast | up |\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_decoy_table_is_rejected(self):
        # A header merely MENTIONING direction used to risk swallowing the
        # real table below it. A second table is now simply illegal.
        rows, findings = validate.parse_exec_table(
            "| Notes about direction here |\n|---|\n| prose |\n\n"
            "| Activity | Direction |\n|---|---|\n| Forecast | up |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" and "exactly one" in f.message
                            for f in findings))

    def test_reordered_columns_are_rejected(self):
        # Was: columns are found by header position. Now: only one order is
        # legal, so there is no position to resolve.
        rows, findings = validate.parse_exec_table(
            "| Direction | Activity |\n|---|---|\n| up | Forecast |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_second_direction_table_is_rejected(self):
        # Codex round 25: an earlier table with a real Direction cell must
        # not shadow a later one. Neither can exist now.
        rows, findings = validate.parse_exec_table(
            "| Report | Direction |\n|---|---|\n| Decoy row | up |\n\n"
            "| Activity | Direction | Deep record |\n|---|---|---|\n"
            "| Forecast | sideways | — |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" and "exactly one" in f.message
                            for f in findings))

    def test_double_backslash_before_pipe_is_rejected(self):
        # Codex round 26: backslash PARITY decided whether the pipe delimited.
        # Canonical cells carry no backslashes, so parity is moot.
        rows, findings = validate.parse_exec_table(
            "| Activity | Direction |\n|---|---|\n| A \\\\| sideways |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_zero_row_table_beside_a_valid_one_is_rejected(self):
        # Codex round 26: a headered-but-empty table must still ERROR when
        # another table in the file parses fine.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n\n"
                          "| Activity | Direction |\n|---|---|\n| F | up |\n")
            self.assertTrue(any("exactly one" in f.message for f in self._errs(d)))

    def test_all_empty_row_table_is_rejected(self):
        # '|  |  |' was a row with an empty Activity cell, not a separator.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n"
                          "|  |  |\n| F | up |\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_fenced_example_table_is_rejected(self):
        # A valid table inside a code fence used to need fence awareness to
        # avoid shadowing the live view. Any '|' outside the one table now
        # ERRORs, so there is no fence question left to get wrong.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n```\n| Activity | Direction |\n"
                          "|---|---|\n| F | up |\n```\n\n"
                          "| Activity | Diretcion |\n|---|---|\n| G | up |\n")
            self.assertTrue(any("exactly one" in f.message for f in self._errs(d)))

    def test_masked_misspelled_table_is_rejected(self):
        # Codex round 27: a valid table must not mask a second, misspelled
        # activity table.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n"
                          "| Good | up |\n\n"
                          "| Activity | Diretcion |\n|---|---|\n"
                          "| Hidden | sideways |\n")
            self.assertTrue(any("exactly one" in f.message for f in self._errs(d)))

    def test_list_nested_fenced_table_is_rejected(self):
        # Codex round 27: a '- ```' fenced example needed the container-aware
        # stripper so its closing line did not swallow the real table below.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "- ```\n  | Activity | Direction |\n  |---|---|\n"
                          "  | Example | up |\n  ```\n\n"
                          "| Activity | Diretcion |\n|---|---|\n"
                          "| Real | sideways |\n")
            self.assertTrue(any("exactly one" in f.message for f in self._errs(d)))

    def test_comment_wrapped_table_is_rejected(self):
        # Codex round 28: a table inside an HTML comment is documentation,
        # not a live activity table.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n<!--\n| Activity | Direction |\n"
                          "|---|---|\n| X | up |\n-->\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_stray_backticks_are_rejected(self):
        # Codex round 28: a stray backtick on one row must not pair with a
        # later row and erase the invalid Direction between them. A backtick
        # is not a canonical cell character, so no pairing can occur.
        rows, findings = validate.parse_exec_table(
            "| Activity | Direction |\n|---|---|\n"
            "| Hidden ` | up |\n| Bad | sideways |\n| tail ` | down |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_comment_wrapped_link_is_rejected(self):
        # A link inside an HTML comment renders as nothing — it must not
        # populate the listing set. The row is now refused outright, so the
        # record is still reported unlisted.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Deep record |\n|---|---|---|\n"
                   "| Renewal | down | <!-- [h](renewal.md) --> |\n")
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            findings = validate.check_ontology(d)
            self.assertTrue(any(f.level == "ERROR" and "canonical" in f.message
                                for f in findings))
            self.assertTrue(any(f.level == "WARN" and "not listed" in f.message
                                for f in findings))

    def test_no_leading_pipe_table_is_rejected(self):
        # GFM rows need not start with '|'; canonical rows must.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n"
                          "| Good | up |\n\n"
                          "Activity | Diretcion\n---|---\nHidden | sideways\n")
            self.assertTrue(any("exactly one" in f.message for f in self._errs(d)))

    def test_blockquoted_table_is_rejected(self):
        rows, findings = validate.parse_exec_table(
            "> | Activity | Direction |\n> |---|---|\n> | F | sideways |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_comment_only_activity_cell_is_rejected(self):
        # Codex round 29: '<!-- hidden -->' rendered as an EMPTY Activity
        # cell. HTML is not a canonical cell character, so the row is refused.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n"
                          "| <!-- hidden --> | up |\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_non_link_deep_record_cells_are_rejected(self):
        # Codex round 29: link-like text inside an HTML attribute, or
        # backslash-escaped link syntax, renders as no link at all.
        for cell in ('<a title="[h](renewal.md)">x</a>',
                     '\\[h\\](renewal.md)'):
            with tempfile.TemporaryDirectory() as d:
                _write(d, "ontologies/sales/_executive-view.md",
                       "| Activity | Direction | Deep record |\n"
                       "|---|---|---|\n| Renewal | down | %s |\n" % cell)
                _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
                findings = validate.check_ontology(d)
                self.assertTrue(any(f.level == "ERROR" and "canonical" in f.message
                                    for f in findings), cell)
                self.assertTrue(
                    any(f.level == "WARN" and "not listed" in f.message
                        for f in findings), cell)

    def test_missing_delimiter_row_is_rejected(self):
        # Codex round 31: without a delimiter row GFM renders NO table at all.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n"
                          "| Good | up |\n")
            self.assertTrue(any("header" in f.message for f in self._errs(d)))

    def test_image_syntax_is_rejected(self):
        # Codex round 30: '![h](renewal.md)' renders an IMAGE, not a link to
        # the record — a one-character typo must not silence the WARN.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Deep record |\n|---|---|---|\n"
                   "| Renewal | down | ![h](renewal.md) |\n")
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            findings = validate.check_ontology(d)
            self.assertTrue(any(f.level == "ERROR" and "Deep record" in f.message
                                for f in findings))
            self.assertTrue(any(f.level == "WARN" and "not listed" in f.message
                                for f in findings))

    def test_escaped_bang_link_is_rejected(self):
        # '\![d](r.md)' rendered a literal '!' followed by a real link — a
        # distinction the canonical cell never has to draw.
        rows, findings = validate.parse_exec_table(
            "| Activity | Direction | Deep record |\n|---|---|---|\n"
            "| R | down | \\![d](r.md) |\n")
        self.assertEqual(rows, [])
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_near_miss_deep_record_header_is_rejected(self):
        # Codex round 27: 'Not a Deep record' must not designate the link
        # column — the listing WARN would be suppressed by an unrelated link.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Not a Deep record |\n"
                   "|---|---|---|\n| Renewal | down | [a](renewal.md) |\n")
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            findings = validate.check_ontology(d)
            self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                                for f in findings))
            self.assertTrue(any(f.level == "WARN" and "not listed" in f.message
                                for f in findings))

    def test_attachment_column_header_is_rejected(self):
        # Codex round 26: without a 'Deep record' header cell, a link in an
        # unrelated column must not satisfy the listing check.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Attachment |\n|---|---|---|\n"
                   "| Renewal | down | [a](renewal.md) |\n")
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            findings = validate.check_ontology(d)
            self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                                for f in findings))
            self.assertTrue(any(f.level == "WARN" and "not listed" in f.message
                                for f in findings))


class TestAggregateListingFailures(unittest.TestCase):
    # Codex round 26: a contributor directory this check cannot LIST must
    # surface as a finding, not vanish from the aggregate (fail closed, #13).
    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "chmod(0) does not restrict root")
    def test_unlistable_rules_dir_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".claude/rules/r.md", "---\nx: y\n---\nbody\n")
            locked = os.path.join(d, ".claude", "rules")
            os.chmod(locked, 0)
            try:
                _items, findings = validate._always_loaded_bytes(d)
            finally:
                os.chmod(locked, 0o755)
            self.assertTrue(any(f.level == "ERROR" and "budget" in f.message
                                for f in findings))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "chmod(0) does not restrict root")
    def test_unstattable_skill_package_fails_closed(self):
        # Codex round 27: a mode-000 skill package made isfile() return False
        # and the skill silently vanished from the aggregate.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/locked/SKILL.md", "---\ndescription: x\n---\n")
            locked = os.path.join(d, "skills", "locked")
            os.chmod(locked, 0)
            try:
                _items, findings = validate._always_loaded_bytes(d)
            finally:
                os.chmod(locked, 0o755)
            self.assertTrue(any(f.level == "ERROR" and "budget" in f.message
                                for f in findings))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "chmod(0) does not restrict root")
    def test_unlistable_skills_dir_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/s/SKILL.md", "---\ndescription: x\n---\n")
            locked = os.path.join(d, "skills")
            os.chmod(locked, 0)
            try:
                _items, findings = validate._always_loaded_bytes(d)
            finally:
                os.chmod(locked, 0o755)
            self.assertTrue(any(f.level == "ERROR" and "budget" in f.message
                                for f in findings))


class TestOntologyFileSafety(unittest.TestCase):
    def test_directory_named_md_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md", EXEC_OK)
            os.makedirs(os.path.join(d, "ontologies", "sales", "notes.md"))
            findings = validate.check_ontology(d)  # must not raise
            self.assertTrue(any(f.level == "ERROR" and "regular file" in f.message
                                for f in findings))

    def test_non_utf8_deep_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md", EXEC_OK)
            _write_bytes(d, "ontologies/sales/bad.md", b"---\nmotion: automate\n---\n\xff\xfe\n")
            self.assertTrue(any(f.level == "ERROR" for f in validate.check_ontology(d)))

    def test_deep_record_linked_by_path_not_basename(self):
        # A link to another function's file must not satisfy the listing check.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Deep record |\n|---|---|---|\n"
                   "| Renewal | down | [d](../people-hr/renewal.md) |\n")
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/renewal.md", AUTOMATE_OK)
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            self.assertTrue(any(f.level == "WARN" and "not listed" in f.message
                                and "sales/renewal.md" in f.path.replace(os.sep, "/")
                                for f in validate.check_ontology(d)))

    def test_fragment_link_still_counts_as_listed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Deep record |\n|---|---|---|\n"
                   "| Renewal | down | [d](renewal.md#scores) |\n")
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            self.assertFalse(any("not listed" in f.message
                                 for f in validate.check_ontology(d)))


class TestAbsoluteImportMessage(unittest.TestCase):
    def test_absolute_import_gets_its_own_message(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@%s\n" % os.path.join(d, "AGENTS.md"))
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.level == "ERROR" and "absolute" in f.message
                                for f in findings))
            self.assertFalse(any("drifted" in f.message for f in findings))


class TestInstanceRoots(unittest.TestCase):
    def _rel(self, d, roots):
        return sorted(os.path.relpath(r, d) for r in roots)

    def test_root_with_content_is_an_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d)), ["."])

    def test_nested_instance_is_discovered(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "demo/ontologies/sales/_executive-view.md", EXEC_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d)), [".", "demo"])

    def test_instance_without_root_content(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/x/SKILL.md", SKILL_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d)), ["demo"])

    def test_every_content_dir_marks_an_instance(self):
        for cd, rel in (("ontologies", "ontologies/f/_executive-view.md"),
                        ("skills", "skills/x/SKILL.md"),
                        ("governance", "governance/constitution/r.md"),
                        ("proposals", "proposals/p.md"),
                        ("memory", "memory/m.md")):
            with tempfile.TemporaryDirectory() as d:
                _write(d, "demo/" + rel, "# x\n")
                self.assertIn("demo", self._rel(d, validate._instance_roots(d)), cd)

    def test_no_content_means_no_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# x\n")
            self.assertEqual(validate._instance_roots(d), [])

    def test_workbench_and_dot_dirs_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "tests/fixtures/ontologies/f/_executive-view.md", EXEC_OK)
            _write(d, "docs/superpowers/ontologies/f/_executive-view.md", EXEC_OK)
            _write(d, ".hidden/ontologies/f/_executive-view.md", EXEC_OK)
            self.assertEqual(validate._instance_roots(d), [])

    def test_gitignored_content_dir_does_not_mark_an_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "vendor/skills/x/SKILL.md", SKILL_OK)
            self.assertEqual(validate._instance_roots(d, ("vendor",)), [])

    def test_deeply_nested_instances(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a/b/c/memory/m.md", "# x\n")
            self.assertEqual(self._rel(d, validate._instance_roots(d)), ["a/b/c"])

    def test_root_first_and_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/x/SKILL.md", SKILL_OK)
            _write(d, "zeta/skills/x/SKILL.md", SKILL_OK)
            _write(d, "alpha/skills/x/SKILL.md", SKILL_OK)
            roots = validate._instance_roots(d)
            # unsorted: the actual walk order is root first, then name order
            self.assertEqual([os.path.relpath(r, d) for r in roots],
                             [".", "alpha", "zeta"])
            self.assertEqual(roots, validate._instance_roots(d))


# SKILL_OK carries no `baseline:` (the provisioning-gate tests add it); a clean
# provisioned instance needs it, so the miniature instance uses this variant.
SKILL_BASELINED = SKILL_OK.replace(
    "provisioned: yes",
    "provisioned: yes\nbaseline: memory/onboarding-baseline.md")


def _write_instance(d, prefix=""):
    """A complete miniature instance: one function, one provisioned skill with
    its card, and the baseline the skill cites."""
    _write(d, prefix + "ontologies/people-hr/_executive-view.md", EXEC_OK)
    _write(d, prefix + "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
    _write(d, prefix + "skills/onboarding-orchestration/SKILL.md", SKILL_BASELINED)
    _write(d, prefix + "skills/onboarding-orchestration/owner-card.md", CARD_OK)
    _write(d, prefix + "memory/onboarding-baseline.md", MEM_OK)
    _write(d, prefix + "memory/_index.md",
           "# Index\n\n- [b](onboarding-baseline.md)\n")


class TestNestedInstanceOntology(unittest.TestCase):
    def test_nested_ontology_is_checked(self):
        # The finding this whole slice exists for: before it, a broken demo
        # ontology produced NOTHING.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/ontologies/sales/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            findings = validate.check_ontology(d)
            self.assertTrue(any(f.level == "ERROR" and "Direction" in f.message
                                for f in findings))

    def test_finding_paths_stay_root_relative(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/ontologies/sales/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            self.assertTrue(any(f.path.startswith("demo/ontologies")
                                for f in validate.check_ontology(d)))

    def test_root_and_nested_instances_both_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            _write(d, "demo/ontologies/sales/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            paths = {f.path.split("/")[0] for f in validate.check_ontology(d)
                     if f.level == "ERROR"}
            self.assertEqual(paths, {"ontologies", "demo"})

    def test_clean_nested_instance_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_ontology(d)
                              if f.level == "ERROR"], [])


class TestNestedInstanceCards(unittest.TestCase):
    def test_nested_skill_package_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/x/SKILL.md", SKILL_OK)  # name mismatch: x vs the frontmatter
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_clean_nested_instance_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_ontology_ref_resolves_inside_its_own_instance(self):
        # demo/ has the ontology; root does not. Instance-relative resolution
        # must find it.
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_a_demo_skill_cannot_borrow_the_engine_ontology(self):
        # The ontology exists only at the ROOT; the demo skill must not reach it.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md", SKILL_BASELINED)
            _write(d, "demo/skills/onboarding-orchestration/owner-card.md", CARD_OK)
            _write(d, "demo/memory/onboarding-baseline.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "ontology" in f.message.lower()
                                for f in validate.check_owner_cards(d)))

    def test_baseline_resolves_inside_its_own_instance(self):
        # The baseline exists only at the root; a demo skill citing it must fail.
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            os.remove(os.path.join(d, "demo", "memory", "onboarding-baseline.md"))
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "baseline" in f.message.lower()
                                for f in validate.check_owner_cards(d)))


class TestNestedInstanceGovernance(unittest.TestCase):
    def test_nested_constitution_rule_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/governance/constitution/r.md",
                   RULE_OK.replace("rung: human-decision", "rung: rung-six"))
            self.assertTrue(any(f.level == "ERROR" and "demo/" in f.path
                                for f in validate.check_constitution(d)))

    def test_clean_nested_rule_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/governance/constitution/r.md", RULE_OK)
            self.assertEqual([f for f in validate.check_constitution(d)
                              if f.level == "ERROR"], [])

    def test_nested_proposal_is_schema_checked(self):
        # The 1.5d-ii deferral, closed.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/proposals/p1.md",
                   PROPOSAL_OK.replace("blast_radius: escalating",
                                       "blast_radius: trivial"))
            self.assertTrue(any(f.level == "ERROR" and "blast_radius" in f.message
                                for f in validate.check_proposals(d)))

    def test_nested_proposal_target_resolves_in_its_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/memory/onboarding-baseline.md", MEM_OK)
            _write(d, "demo/proposals/p1.md", PROPOSAL_OK)
            self.assertEqual([f for f in validate.check_proposals(d)
                              if f.level == "ERROR"], [])

    def test_a_demo_proposal_cannot_target_an_engine_skill(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/proposals/p1.md", PROPOSAL_OK)
            self.assertTrue(any(f.level == "ERROR" and "target" in f.message
                                for f in validate.check_proposals(d)))

    def test_nested_changelog_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n- oops not an entry\n")
            self.assertTrue(any(f.level == "WARN" and "demo/" in f.path
                                for f in validate.check_changelog(d)))

    def test_both_instances_checked_independently(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# c\n\n## Entries\n\n- bad root entry\n")
            _write(d, "demo/governance/changelog.md",
                   "# c\n\n## Entries\n\n- bad demo entry\n")
            tops = {f.path.split("/")[0] for f in validate.check_changelog(d)}
            self.assertEqual(tops, {"governance", "demo"})


MEM_SUPERSEDED = MEM_OK.replace(
    "provenance: observed",
    "provenance: superseded\nsuperseded_by: memory/new.md\ninvalid_at: 2026-07-01")


class TestNestedInstanceMemory(unittest.TestCase):
    # Codex review of this slice: `superseded_by` resolved against the
    # validated root, so a nested chain false-errored and a cross-instance
    # pointer was silently accepted.
    def test_nested_supersession_resolves_in_its_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/memory/old.md", MEM_SUPERSEDED)
            _write(d, "demo/memory/new.md", MEM_OK)
            self.assertEqual([f for f in validate.check_memory(d)
                              if f.level == "ERROR"], [])

    def test_supersession_cannot_cross_out_of_its_instance(self):
        # The successor exists only at the ROOT; the demo record must not
        # reach it.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/memory/old.md", MEM_SUPERSEDED)
            _write(d, "memory/new.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message
                                for f in validate.check_memory(d)))

    def test_root_supersession_still_resolves_at_root(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/old.md", MEM_SUPERSEDED)
            _write(d, "memory/new.md", MEM_OK)
            self.assertEqual([f for f in validate.check_memory(d)
                              if f.level == "ERROR"], [])

    def test_instance_nested_inside_a_memory_tree_resolves_inward(self):
        # Codex r2: the record's instance is the parent of the LAST 'memory'
        # component — memory/company/ is its own instance here, and its chain
        # must resolve inside it. No record exists at the outer root, so the
        # pre-fix root-relative resolution fails this test (Codex r3: with an
        # outer decoy present it passed both ways and discriminated nothing).
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/company/memory/old.md", MEM_SUPERSEDED)
            _write(d, "memory/company/memory/new.md", MEM_OK)
            self.assertEqual([f for f in validate.check_memory(d)
                              if f.level == "ERROR"], [])

    def test_memory_nested_instance_cannot_cite_the_outer_instance(self):
        # The successor exists only at the OUTER instance; the inner record
        # must not reach it (Codex r2 blocking edge).
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/company/memory/old.md", MEM_SUPERSEDED)
            _write(d, "memory/new.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message
                                for f in validate.check_memory(d)))

    def test_root_ignored_record_is_not_a_valid_baseline(self):
        # Codex review: the baseline allowlist must honor the validated
        # root's ignore set, not reload one from the nested instance.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/ontologies/people-hr/onboarding-orchestration.md",
                   AUTOMATE_OK)
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md",
                   SKILL_OK.replace(
                       "provisioned: yes",
                       "provisioned: yes\nbaseline: memory/secret-baseline.md"))
            _write(d, "demo/skills/onboarding-orchestration/owner-card.md",
                   CARD_OK)
            _write(d, "demo/memory/secret-baseline.md", MEM_OK)
            errs = [f for f in validate.check_owner_cards(d, ("secret*",))
                    if f.level == "ERROR" and "baseline" in f.message]
            self.assertTrue(errs)


CANON_OK = ("---\ncompany: Umbercress\nproduct: Umbercress Relay\n"
            "domains:\n  - umbercress.example\nexternal_domains:\n"
            "phone_range: 555-01\n---\n# The Umbercress world\n")


class TestSyntheticIdentifiers(unittest.TestCase):
    def _demo(self, d, body, name="notes.md", canon=CANON_OK):
        if canon is not None:
            _write(d, "demo/canon.md", canon)
        _write(d, "demo/" + name, body)

    def test_no_demo_directory_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "mail me at real.person@acme.com\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_canon_domain_email_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Ask ruth.okafor@umbercress.example about it.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_domain_email_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Ask ruth.okafor@acme-logistics.com about it.\n")
            self.assertTrue(any(f.level == "ERROR" and "acme-logistics.com" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_reserved_namespaces_pass(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "a@x.test b@y.invalid c@example.com d@sub.example.org\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_url_host_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "See https://status.acme-logistics.com/incidents for detail.\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_bare_public_domain_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Their site is acme-logistics.com and it is slow.\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_filenames_are_not_domains(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "See canon.md, SKILL.md, validate.py and config.json.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_fiction_phone_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 555-0142 or (555) 019-9 nonsense.\n")
            self.assertEqual([f for f in validate.check_synthetic_identifiers(d)
                              if "555-0142" in f.message], [])

    def test_real_phone_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 415-555-2671 for support.\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_testnet_ip_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "The relay runs at 192.0.2.14 and 203.0.113.7.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_ip_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "The relay runs at 8.8.8.8.\n")
            self.assertTrue(any(f.level == "ERROR" and "8.8.8.8" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_uppercase_url_host_errors(self):
        # Codex r1: the URL scheme was matched lowercase-only, so
        # 'HTTPS://ACME.COM' evaded the extractor entirely.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "See HTTPS://ACME.COM/STATUS for detail.\n")
            self.assertTrue(any(f.level == "ERROR" and "ACME.COM" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_uppercase_bare_domain_errors(self):
        # Codex r1: the bare-domain TLD alternation was lowercase-only.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Their site is ACME.COM and it is slow.\n")
            self.assertTrue(any(f.level == "ERROR" and "ACME.COM" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_seven_digit_real_phone_errors(self):
        # Codex r1: only 10-digit NANP forms were extracted, so 'Call 867-5309'
        # passed despite being outside the fiction range.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 867-5309 for support.\n")
            self.assertTrue(any(f.level == "ERROR" and "867-5309" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_fiction_phone_test_is_not_vacuous(self):
        # Codex r1: 555-0142 was never extracted, so the fiction-phone test
        # passed vacuously. This pair is the discriminator: same 7-digit shape,
        # one inside the range (no finding), one outside (finding).
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 555-0142 or, after hours, 555-9142.\n")
            findings = validate.check_synthetic_identifiers(d)
            self.assertTrue(any(f.level == "ERROR" and "555-9142" in f.message
                                for f in findings))
            self.assertEqual([f for f in findings if "555-0142" in f.message], [])

    def test_compact_ten_digit_phone_errors(self):
        # Codex r2: requiring a separator after the area code regressed the
        # compact 10-digit form the original pattern accepted.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 4155552671 now.\n")
            self.assertTrue(any(f.level == "ERROR" and "415-555-2671" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_compact_seven_digit_token_is_not_a_phone(self):
        # Codex r2: a bare 7-digit token ('Order 8675309') must not read as a
        # phone — the 7-digit form is only recognized separator-written.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Order 8675309 shipped yesterday.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_multi_label_public_suffix_canon_entry_errors(self):
        # Codex r2: '.co.uk' normalized to 'co.uk', which contains a dot and
        # slipped past the bare-TLD rule — laundering every .co.uk host.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Ask ceo@real-company.co.uk about it.\n",
                       canon=CANON_OK.replace("domains:\n  - umbercress.example",
                                              "domains:\n  - .co.uk"))
            findings = validate.check_synthetic_identifiers(d)
            self.assertTrue(any(f.level == "ERROR" and "canon" in f.path
                                for f in findings))
            self.assertTrue(any(f.level == "ERROR" and "real-company.co.uk" in f.message
                                for f in findings))

    def test_invalid_ip_shaped_url_host_errors(self):
        # Codex r2: '999.999.999.999' as a URL host was skipped as IPv4-shaped,
        # then discarded by the octet-validity carve-out — falling through both
        # rules. Only a VALID IPv4 host defers to the IP rule.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "See https://999.999.999.999/status for detail.\n")
            self.assertTrue(any(f.level == "ERROR" and "999.999.999.999" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_demo_inside_your_company_is_not_scoped(self):
        # Codex r1: the #16 scope matrix says NEVER your-company/ — including a
        # directory it happens to call demo.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/demo/notes.md",
                   "ceo@acme-logistics.com 8.8.8.8\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_bare_tld_canon_entry_errors_and_is_not_an_allowance(self):
        # Codex r1: 'domains: com' must not turn every .com host into a
        # subdomain of the canon (nor may a leading-dot '.com' entry).
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Ask ceo@real-company.com about it.\n",
                       canon=CANON_OK.replace("domains:\n  - umbercress.example",
                                              "domains:\n  - com"))
            findings = validate.check_synthetic_identifiers(d)
            self.assertTrue(any(f.level == "ERROR" and "canon" in f.path
                                for f in findings))
            self.assertTrue(any(f.level == "ERROR" and "real-company.com" in f.message
                                for f in findings))

    def test_testnet_ip_as_url_host_passes(self):
        # Codex r1: a TEST-NET IP used as a URL host was rejected as an
        # undeclared 'domain' before the IPv4 rule could bless it.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "The console is at https://192.0.2.14/status today.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_ip_as_url_host_still_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "The console is at https://8.8.8.8/status today.\n")
            self.assertTrue(any(f.level == "ERROR" and "8.8.8.8" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_localhost_apex_passes(self):
        # Codex r1: only '.localhost' subdomains passed; the reserved apex
        # 'localhost' itself was rejected.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Point it at http://localhost/relay for local runs.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_longer_dotted_chain_is_not_carved_into_an_ip(self):
        # Regression for the in-session _IPV4 fix: the plan's lookahead
        # (?![\d.]) missed a sentence-final IP ('… at 8.8.8.8.'), so it was
        # loosened to (?!\.?\d) — which must NOT start matching four octets
        # out of a five-part version string.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Upgrade from 1.2.3.4.5 to the next build.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_external_domain_declared_in_canon_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Source: https://github.com/x/y\n",
                       canon=CANON_OK.replace("external_domains:\n",
                                              "external_domains:\n  - github.com\n"))
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_missing_canon_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/notes.md", "nothing identifying here\n")
            self.assertTrue(any(f.level == "ERROR" and "canon" in f.message.lower()
                                for f in validate.check_synthetic_identifiers(d)))

    def test_unreadable_canon_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "demo/canon.md", b"---\ndomains:\n  - \xff\xfe\n---\n")
            _write(d, "demo/notes.md", "x\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_your_company_is_never_scoped(self):
        # #16 is explicit: real identifiers are legitimate in your-company/.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/canon.md", CANON_OK)
            _write(d, "your-company/notes.md", "ceo@acme-logistics.com 8.8.8.8\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_subdomain_of_a_canon_domain_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "app.umbercress.example is the console.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_lookalike_suffix_does_not_pass(self):
        # 'notumbercress.example' ends with the canon domain as a STRING but is
        # not a subdomain of it.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "notumbercress.example is someone else.\n")
            findings = validate.check_synthetic_identifiers(d)
            self.assertEqual(findings, [])  # .example is reserved regardless

    def test_lookalike_suffix_on_a_public_tld_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "notumbercress.com is someone else.\n",
                       canon=CANON_OK.replace("umbercress.example", "umbercress.com"))
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_wired_into_validate(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/canon.md", CANON_OK)
            _write(d, "demo/notes.md", "ceo@acme-logistics.com\n")
            self.assertTrue(any(f.level == "ERROR" for f in validate.validate(d)))


class TestMemoryInstanceOwnership(unittest.TestCase):
    def test_root_skill_cannot_borrow_a_nested_instance_baseline(self):
        # The asymmetry Slice 2.3a left open: containment held inward and
        # leaked outward, so an engine exemplar could take its baseline from
        # the demo company's numbers.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "skills/onboarding-orchestration/SKILL.md",
                   SKILL_BASELINED.replace("baseline: memory/onboarding-baseline.md",
                                           "baseline: demo/memory/onboarding-baseline.md"))
            _write(d, "skills/onboarding-orchestration/owner-card.md", CARD_OK)
            _write(d, "demo/memory/onboarding-baseline.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "baseline" in f.message.lower()
                                for f in validate.check_owner_cards(d)))

    def test_own_instance_baseline_still_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d)
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_nested_instance_baseline_still_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_memory_instance_base_picks_the_last_memory_component(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "memory", "company", "memory", "x.md")
            self.assertEqual(
                os.path.realpath(validate._memory_instance_base(d, p)),
                os.path.realpath(os.path.join(d, "memory", "company")))

    def test_memory_instance_base_at_root(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "memory", "x.md")
            self.assertEqual(os.path.realpath(validate._memory_instance_base(d, p)),
                             os.path.realpath(d))


class TestInstanceRootsSymlinkMarkers(unittest.TestCase):
    # Codex review: a dangling `skills` symlink stopped marking an instance,
    # silently dropping the pre-existing "must not be a symlink" ERROR.
    def test_dangling_content_symlink_still_marks_an_instance(self):
        with tempfile.TemporaryDirectory() as d:
            os.symlink(os.path.join(d, "nonexistent"), os.path.join(d, "skills"))
            self.assertEqual(validate._instance_roots(d), [d])

    def test_dangling_skills_symlink_still_errors(self):
        with tempfile.TemporaryDirectory() as d:
            os.symlink(os.path.join(d, "nonexistent"), os.path.join(d, "skills"))
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                for f in validate.check_owner_cards(d)))

    def test_nested_dangling_skills_symlink_errors_with_nested_path(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "demo"))
            os.symlink(os.path.join(d, "nonexistent"),
                       os.path.join(d, "demo", "skills"))
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "ERROR" and f.path == "demo/skills"
                                for f in findings))

    def test_file_symlink_named_as_content_dir_marks_an_instance(self):
        with tempfile.TemporaryDirectory() as d:
            target = _write(d, "somefile.md", "# x\n")
            os.symlink(target, os.path.join(d, "skills"))
            self.assertEqual(validate._instance_roots(d), [d])

    def test_plain_file_named_as_content_dir_is_not_a_marker(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills", "# just a file\n")
            self.assertEqual(validate._instance_roots(d), [])

    def test_ignored_symlink_marker_is_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            os.symlink(os.path.join(d, "nonexistent"), os.path.join(d, "skills"))
            self.assertEqual(validate._instance_roots(d, ("skills",)), [])


IV_MANIFEST_OK = """---
company: Umbercress
role: An organizational analyst mapping the work before proposing automation
phase: marketing
status: in-progress
open_question: q-story-bottleneck
last_checkpoint: 2026-06-15
layers:
  - 01-role-and-scope.md
  - 02-customer-success.md
---
# Interview manifest — Umbercress

Two layers confirmed, one turn in flight.
"""

IV_LAYER_OK = """---
provenance: confirmed
confirmed_by: Priya Raman
confirmed_at: 2026-05-11
source: Opening interview session 2026-05-04
---
# Layer 1 — The role, and what is in scope

The confirmed facts of the layer.
"""

IV_WORKING_OK = """---
provenance: observed
source: Marketing session 2026-06-22
open_question: q-story-bottleneck
---
# In flight — Marketing

Provisional facts nobody has approved.

## Open question

`q-story-bottleneck` — the question waiting on a human.
"""


def _iv_state(d, sub="interview", manifest=IV_MANIFEST_OK, working=IV_WORKING_OK):
    """A complete, correct interview-state directory: manifest, two confirmed
    layers, one turn in flight."""
    _write(d, "%s/00-manifest.md" % sub, manifest)
    _write(d, "%s/01-role-and-scope.md" % sub, IV_LAYER_OK)
    _write(d, "%s/02-customer-success.md" % sub,
           IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                               "# Layer 2 — Customer success"))
    if working is not None:
        _write(d, "%s/_working.md" % sub, working)


class TestInterviewState(unittest.TestCase):
    def test_happy_path_zero_findings(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            self.assertEqual(validate.check_interview_state(d), [])

    def test_no_manifest_is_silent(self):
        # Discovery is by CONTENT: markdown files with no 00-manifest.md are
        # documentation (the engine's own interview/), never state.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "interview/README.md", "# The format spec\n\nProse.\n")
            _write(d, "interview/01-role-and-scope.md", IV_LAYER_OK)
            self.assertEqual(validate.check_interview_state(d), [])

    def test_each_missing_manifest_field_errors(self):
        for field in ("company", "role", "phase", "status",
                      "open_question", "last_checkpoint"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                broken = "\n".join(ln for ln in IV_MANIFEST_OK.split("\n")
                                   if not ln.startswith(field + ":"))
                _iv_state(d, manifest=broken)
                self.assertTrue(any(f.level == "ERROR" and "'%s'" % field in f.message
                                    for f in validate.check_interview_state(d)))

    def test_bare_key_errors_not_crashes(self):
        # 'role:' with no value parses as [] — blank, not a crash.
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "role: An organizational analyst mapping the work before proposing automation",
                "role:"))
            self.assertTrue(any(f.level == "ERROR" and "'role'" in f.message
                                for f in validate.check_interview_state(d)))

    def test_bad_status_errors_naming_legal_values(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "status: in-progress", "status: paused"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "in-progress" in f.message
                                and "complete" in f.message for f in findings))

    def test_scalar_layers_errors_naming_required_shape(self):
        # Restricted grammar: a scalar is NOT read as a one-element list.
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "layers:\n  - 01-role-and-scope.md\n  - 02-customer-success.md",
                "layers: 01-role-and-scope.md"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "must be a list" in f.message
                                for f in findings))

    def test_listed_but_missing_layer_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            os.remove(os.path.join(d, "interview", "02-customer-success.md"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "does not exist" in f.message
                                and "02-customer-success.md" in f.message
                                for f in findings))

    def test_present_but_unlisted_layer_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write(d, "interview/03-people-hr.md",
                   IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                                       "# Layer 3 — People"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "not listed in the manifest" in f.message
                                and "03-people-hr.md" in f.path for f in findings))

    def test_duplicate_layer_entry_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "  - 02-customer-success.md",
                "  - 02-customer-success.md\n  - 02-customer-success.md"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "twice" in f.message
                                for f in findings))

    def test_shared_number_distinct_slugs_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "  - 02-customer-success.md",
                "  - 02-customer-success.md\n  - 02-people-hr.md"))
            _write(d, "interview/02-people-hr.md",
                   IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                                       "# Layer 2b — People"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "share a number" in f.message
                                for f in findings))

    def test_gap_in_numbering_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "  - 02-customer-success.md", "  - 03-customer-success.md"))
            os.rename(os.path.join(d, "interview", "02-customer-success.md"),
                      os.path.join(d, "interview", "03-customer-success.md"))
            findings = validate.check_interview_state(d)
            gap = [f for f in findings if "gap" in f.message]
            self.assertTrue(gap and all(f.level == "WARN" for f in gap))
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])

    def test_wrong_order_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "layers:\n  - 01-role-and-scope.md\n  - 02-customer-success.md",
                "layers:\n  - 02-customer-success.md\n  - 01-role-and-scope.md"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "WARN" and "ascending" in f.message
                                for f in findings))

    def test_bad_layer_filename_errors_naming_shape(self):
        for name in ("00-manifest.md", "1-role.md", "role-and-scope.md",
                     "01-Role.md", "../evil.md"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                    "  - 02-customer-success.md", "  - %s" % name))
                findings = validate.check_interview_state(d)
                self.assertTrue(any(f.level == "ERROR" and "NN-slug.md" in f.message
                                    for f in findings))

    def test_manifest_never_treated_as_layer(self):
        # 00 is reserved: the manifest itself must not be scanned as a layer or
        # reported as present-but-unlisted.
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            findings = validate.check_interview_state(d)
            self.assertEqual([f for f in findings if "00-manifest.md" in f.path], [])

    def test_layer_provenance_not_confirmed_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("provenance: confirmed", "provenance: inferred"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                                and "01-role-and-scope.md" in f.path for f in findings))

    def test_layer_missing_spine_fields_error(self):
        for field in ("confirmed_by", "confirmed_at", "source"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                _iv_state(d)
                broken = "\n".join(ln for ln in IV_LAYER_OK.split("\n")
                                   if not ln.startswith(field + ":"))
                _write(d, "interview/01-role-and-scope.md", broken)
                self.assertTrue(any(f.level == "ERROR" and "'%s'" % field in f.message
                                    for f in validate.check_interview_state(d)))

    def test_layer_with_no_body_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace(
                       "# Layer 1 — The role, and what is in scope\n\n"
                       "The confirmed facts of the layer.\n",
                       "# Layer 1 — The role, and what is in scope\n"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "no content" in f.message
                                for f in findings))

    def test_confirmed_at_unparseable_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("confirmed_at: 2026-05-11",
                                       "confirmed_at: last Tuesday"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "WARN" and "ISO date" in f.message
                                and "01-role-and-scope.md" in f.path for f in findings))

    def test_confirmed_at_in_future_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("confirmed_at: 2026-05-11",
                                       "confirmed_at: 2099-01-01"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "WARN" and "future" in f.message
                                for f in findings))

    def test_working_claiming_confirmed_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, working=IV_WORKING_OK.replace(
                "provenance: observed", "provenance: confirmed"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "promote" in f.message
                                and "_working.md" in f.path for f in findings))

    def test_working_invalid_provenance_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, working=IV_WORKING_OK.replace(
                "provenance: observed", "provenance: banana"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                                and "_working.md" in f.path for f in findings))

    def test_working_present_while_complete_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK
                      .replace("status: in-progress", "status: complete")
                      .replace("open_question: q-story-bottleneck",
                               "open_question: none"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "complete" in f.message
                                and "_working.md" in f.path for f in findings))

    def test_working_missing_while_question_open_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, working=None)
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "no _working.md" in f.message
                                for f in findings))

    def test_no_open_question_and_no_working_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "open_question: q-story-bottleneck", "open_question: none"),
                working=None)
            self.assertEqual(validate.check_interview_state(d), [])

    def test_question_drift_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, working=IV_WORKING_OK.replace(
                "open_question: q-story-bottleneck", "open_question: q-other"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "half-committed" in f.message
                                for f in findings))

    def test_working_question_while_manifest_says_none_errors(self):
        # Codex review (Slice 3.1): drift in the OTHER direction — a hidden
        # question the manifest never points at is as half-committed as a
        # mismatched one.
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "open_question: q-story-bottleneck", "open_question: none"))
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "half-committed" in f.message
                                for f in findings))

    def test_complete_with_open_question_errors(self):
        # Codex review (Slice 3.1): status: complete must not suppress the
        # open-question contradiction — a finished interview owes no answers.
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, manifest=IV_MANIFEST_OK.replace(
                "status: in-progress", "status: complete"), working=None)
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "open question" in f.message
                                and "complete" in f.message for f in findings))

    def test_working_without_source_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, working=IV_WORKING_OK.replace(
                "source: Marketing session 2026-06-22\n", ""))
            findings = validate.check_interview_state(d)
            src = [f for f in findings if "source" in f.message]
            self.assertTrue(src and all(f.level == "WARN" for f in src))
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])

    def test_symlinked_manifest_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            target = _write(d, "elsewhere.md", IV_MANIFEST_OK)
            man = os.path.join(d, "interview", "00-manifest.md")
            os.remove(man)
            os.symlink(target, man)
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                and "00-manifest.md" in f.path for f in findings))

    def test_symlinked_layer_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            target = _write(d, "elsewhere.md", IV_LAYER_OK)
            layer = os.path.join(d, "interview", "01-role-and-scope.md")
            os.remove(layer)
            os.symlink(target, layer)
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                and "01-role-and-scope.md" in f.path for f in findings))

    def test_symlinked_working_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            target = _write(d, "elsewhere.md", IV_WORKING_OK)
            work = os.path.join(d, "interview", "_working.md")
            os.remove(work)
            os.symlink(target, work)
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                and "_working.md" in f.path for f in findings))

    def test_non_utf8_manifest_fails_closed_without_crashing(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write_bytes(d, "interview/00-manifest.md", b"\xff\xfe")
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_non_utf8_layer_fails_closed_without_crashing(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write_bytes(d, "interview/01-role-and-scope.md", b"\xff\xfe")
            findings = validate.check_interview_state(d)
            self.assertTrue(any(f.level == "ERROR"
                                and "01-role-and-scope.md" in f.path
                                for f in findings))

    def test_gitignored_state_dir_not_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, sub="scratch")
            _write(d, "scratch/03-unlisted.md", IV_LAYER_OK)  # would ERROR if scanned
            self.assertEqual(validate.check_interview_state(d, ("scratch",)), [])

    def test_two_state_dirs_both_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d, sub="teams/a/interview")
            _iv_state(d, sub="teams/b/interview")
            _write(d, "teams/a/interview/03-unlisted.md",
                   IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                                       "# Layer 3 — Extra"))
            _write(d, "teams/b/interview/03-unlisted.md",
                   IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                                       "# Layer 3 — Extra"))
            findings = validate.check_interview_state(d)
            hit_dirs = {f.path.split(os.sep)[1] for f in findings
                        if "not listed" in f.message}
            self.assertEqual(hit_dirs, {"a", "b"})

    def test_wired_into_validate(self):
        # The check must run from validate(), not only when called directly.
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            _write(d, "interview/03-unlisted.md",
                   IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                                       "# Layer 3 — Extra"))
            findings = validate.validate(d)
            self.assertTrue(any(f.level == "ERROR" and "not listed" in f.message
                                for f in findings))


class TestInterviewDiff(unittest.TestCase):
    def _repo(self, d):
        _git(d, "init", "-q")
        _git(d, "config", "user.email", "t@t.t")
        _git(d, "config", "user.name", "t")
        _iv_state(d)
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "base")

    def test_unchanged_layers_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            self.assertEqual(validate.interview_diff_findings(d, "HEAD"), [])

    def test_edited_body_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("The confirmed facts of the layer.",
                                       "The rewritten facts of the layer."))
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "frozen at its checkpoint" in f.message
                                and "01-role-and-scope.md" in f.path for f in findings))

    def test_edited_frontmatter_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("confirmed_by: Priya Raman",
                                       "confirmed_by: Somebody Else"))
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "frozen" in f.message
                                for f in findings))

    def test_whitespace_only_change_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/01-role-and-scope.md", IV_LAYER_OK + "\n\n")
            self.assertEqual(validate.interview_diff_findings(d, "HEAD"), [])

    def test_crlf_base_blob_is_clean(self):
        # A CRLF blob at base vs an LF working read is not an edit.
        with tempfile.TemporaryDirectory() as d:
            _git(d, "init", "-q")
            _git(d, "config", "user.email", "t@t.t")
            _git(d, "config", "user.name", "t")
            _iv_state(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("\n", "\r\n"))
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "crlf")
            _write(d, "interview/01-role-and-scope.md", IV_LAYER_OK)
            self.assertEqual(validate.interview_diff_findings(d, "HEAD"), [])

    def test_deleted_layer_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "interview", "01-role-and-scope.md"))
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "deleted" in f.message
                                for f in findings))

    def test_new_layer_is_fine(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/03-people-hr.md",
                   IV_LAYER_OK.replace("# Layer 1 — The role, and what is in scope",
                                       "# Layer 3 — People"))
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if "03-people-hr.md" in f.path], [])

    def test_manifest_edit_is_fine(self):
        # The manifest is the pointer: it is rewritten every turn.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/00-manifest.md",
                   IV_MANIFEST_OK.replace("phase: marketing", "phase: sales"))
            self.assertEqual(validate.interview_diff_findings(d, "HEAD"), [])

    def test_working_edit_is_fine(self):
        # _working.md is provisional: it is dirty by design.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/_working.md",
                   IV_WORKING_OK + "\nA provisional note added this turn.\n")
            self.assertEqual(validate.interview_diff_findings(d, "HEAD"), [])

    def test_deleting_manifest_does_not_unfreeze_layers(self):
        # The dir was state AT BASE — removing the manifest in the same diff
        # must not exempt the layers beneath it.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "interview", "00-manifest.md"))
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("The confirmed facts of the layer.",
                                       "The rewritten facts of the layer."))
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "frozen" in f.message
                                for f in findings))

    def test_unknown_base_ref_errors_without_crash(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            findings = validate.interview_diff_findings(d, "no-such-ref")
            self.assertTrue(any(f.level == "ERROR" and "base ref" in f.message
                                for f in findings))

    def test_symlinked_layer_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            layer = os.path.join(d, "interview", "01-role-and-scope.md")
            os.rename(layer, os.path.join(d, "copy.md"))
            os.symlink(os.path.join(d, "copy.md"), layer)
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message
                                for f in findings))

    def test_non_utf8_base_blob_fails_closed(self):
        # An unreadable base version is never "unchanged".
        with tempfile.TemporaryDirectory() as d:
            _git(d, "init", "-q")
            _git(d, "config", "user.email", "t@t.t")
            _git(d, "config", "user.name", "t")
            _iv_state(d)
            _write_bytes(d, "interview/01-role-and-scope.md", b"\xff\xfe")
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "base")
            _write(d, "interview/01-role-and-scope.md", IV_LAYER_OK)
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "cannot verify" in f.message
                                for f in findings))

    def test_outside_a_repo_errors_without_crash(self):
        with tempfile.TemporaryDirectory() as d:
            _iv_state(d)
            findings = validate.interview_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "git repository" in f.message
                                for f in findings))

    def test_unknown_ref_prints_one_context_error_through_main(self):
        # Three diff passes resolve the git context independently; the `seen`
        # accumulator must collapse the identical fatal ERROR to ONE line.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = validate.main(["validate.py", d, "--diff", "no-such-ref"])
            self.assertEqual(code, 1)
            self.assertEqual(out.getvalue().count("base ref not found"), 1)

    def test_frozen_layer_edit_fails_main_gate(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "interview/01-role-and-scope.md",
                   IV_LAYER_OK.replace("The confirmed facts of the layer.",
                                       "The rewritten facts of the layer."))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = validate.main(["validate.py", d, "--diff", "HEAD"])
            self.assertEqual(code, 1)
            self.assertIn("frozen at its checkpoint", out.getvalue())


class TestInterviewDocExamples(unittest.TestCase):
    """The state-format doc ships example files. Nothing checked them, so they
    could drift from the schema silently — and the first person to notice would
    be an adopter copying an example that fails the gate. Extract them and run
    the real check."""

    # Blocks are labelled in the doc by the filename they demonstrate, in the
    # fence info string: ```markdown 00-manifest.md
    _BLOCK = re.compile(
        r"^```[a-z]*[ \t]+(00-manifest\.md|_working\.md|[0-9]{2}-[a-z0-9-]+\.md)[ \t]*\n"
        r"(.*?)^```[ \t]*$",
        re.S | re.M)

    def test_readme_examples_validate(self):
        doc = (REPO / "interview" / "README.md").read_text()
        matches = list(self._BLOCK.finditer(doc))
        blocks = dict((m.group(1), m.group(2)) for m in matches)
        # Two examples for one filename would silently collapse into the dict,
        # leaving the earlier one untested (Codex review of slice 3.2).
        self.assertEqual(len(matches), len(blocks),
                         "duplicate labelled example fences in interview/README.md")
        # Anti-hollow: an empty extraction validates an empty directory and passes.
        self.assertIn("00-manifest.md", blocks,
                      "no labelled manifest example found in interview/README.md — "
                      "the extractor found nothing, so this test proves nothing")
        self.assertGreaterEqual(len(blocks), 3, "expected manifest + layer + working")
        with tempfile.TemporaryDirectory() as d:
            state = os.path.join(d, "interview")
            os.makedirs(state)
            for name, body in blocks.items():
                with open(os.path.join(state, name), "w", encoding="utf-8") as fh:
                    fh.write(body)
            findings = validate.check_interview_state(d)
        self.assertEqual([f for f in findings if f.level == "ERROR"], [],
                         "the documented example does not satisfy the check it documents")


class TestQuestionSkeletonCoverage(unittest.TestCase):
    """The interview must be able to fill every field the validator requires. A
    schema field nobody asks about is a record the generator cannot complete;
    a question naming a field that does not exist is a question whose answer
    lands nowhere. Both directions are silent failures without this test.

    #5's 'all eight Gate fields must be answered, and there is no waiver' is
    enforced at the validator end. This is the same rule at the interview end."""

    # Fields the generator draws from what it already captured rather than
    # asking — #6's drafting split, encoded. Each entry needs a reason.
    NOT_ASKED = {
        "card:last_reviewed": "date stamp written at generation",
        "card:next_review": "date stamp written at generation",
        "memory:provenance": "set by how the fact was learned, not by asking",
    }

    # Mirrors check_memory's required spine. Update together — validate.py has
    # no constant for it (candidate for extraction next time memory changes).
    MEMORY_SPINE = ("provenance", "owner", "valid_at", "source", "review_by")

    def _fills(self):
        doc = (REPO / "interview" / "questions.md").read_text()
        fills, rows = set(), 0
        for line in doc.split("\n"):
            cells = validate._canonical_row(line)
            if cells is None:
                # A '|' outside a canonical row means the table grammar slipped.
                self.assertNotIn("|", line,
                                 "non-canonical table line in questions.md: %r" % line)
                continue
            if cells[0] in ("Ask", "") or set(cells[1]) <= set("- "):
                continue  # header or delimiter
            rows += 1
            for f in cells[1].split(","):
                f = f.strip()
                if f and f != "—":
                    fills.add(f)
        self.assertGreater(rows, 30, "the question table parsed almost nothing")
        return fills

    def test_every_named_field_exists(self):
        known = set()
        for f in validate.SCORE_FIELDS + validate.GATE_FIELDS:
            known.add("ontology:" + f)
        for f in ("motion", "work_type", "accountable_owner", "substrate", "shape"):
            known.add("ontology:" + f)
        for f in validate.CARD_REQUIRED + validate.CARD_TRACK2 + ["action_class"]:
            known.add("card:" + f)
        for f in validate._RULE_OBJECT_FIELDS + ["owner", "rung", "action_class",
                                                 "sunset", "ritual", "scarcity",
                                                 "surviving_job", "reassigned_to",
                                                 "repeals"]:
            known.add("rule:" + f)
        for f in self.MEMORY_SPINE:
            known.add("memory:" + f)
        known |= {"exec:activity", "exec:direction"}
        unknown = self._fills() - known
        self.assertEqual(unknown, set(),
                         "questions.md names fields the schema does not have: %s" % sorted(unknown))

    def test_every_required_field_is_asked(self):
        fills = self._fills()
        required = set()
        for f in validate.SCORE_FIELDS + validate.GATE_FIELDS:
            required.add("ontology:" + f)
        for f in ("motion", "work_type", "accountable_owner", "substrate", "shape"):
            required.add("ontology:" + f)
        # action_class is ERROR-required on a card and is the rule's safety
        # spine (no-rung-six); the exec pair is what the executive tier IS.
        # Omitting them here made the required direction quietly narrower than
        # the validator (Codex review of slice 3.2).
        for f in validate.CARD_REQUIRED + validate.CARD_TRACK2 + ["action_class"]:
            required.add("card:" + f)
        for f in validate._RULE_OBJECT_FIELDS + ["owner", "rung", "sunset",
                                                 "action_class"]:
            required.add("rule:" + f)
        for f in self.MEMORY_SPINE:
            required.add("memory:" + f)
        required |= {"exec:activity", "exec:direction"}
        missing = required - fills - set(self.NOT_ASKED)
        self.assertEqual(missing, set(),
                         "the schema requires fields no question asks for: %s — either "
                         "add the question or add it to NOT_ASKED with a reason"
                         % sorted(missing))


class TestDemoIsLiftable(unittest.TestCase):
    """demo/ is the shape the generator writes a company repo in, so a link that
    climbs out of demo/ is a link that would not resolve in a real one.

    Four such links exist today and are correct where they are — the demo teaches
    by pointing at the convention it instantiates. This test pins the set. A
    fifth makes the reference target less liftable, and that should be a decision
    somebody makes, not a thing that happens.

    The pinned unit is the (file, target) pair: a second copy of a known link in
    the same file is the same escape, not a new one — the invariant is which
    engine paths the demo references, and from where."""

    KNOWN_ESCAPES = {
        ("demo/README.md", "../AGENTS.md"),
        ("demo/canon.md", "../docs/known-limitations.md"),
        ("demo/governance/README.md", "../../governance/README.md"),
        ("demo/skills/README.md", "../../skills/work-package-spec.md"),
    }

    _LINK = re.compile(r"\]\(([^)\s#]+)")
    # A reference-style definition ([label]: target) escapes just as well as an
    # inline link and check_links would not flag it (the target resolves — in
    # the ENGINE), so the tripwire scans both forms. The pattern deliberately
    # over-approximates: blockquote/list nesting and angle-bracket destinations
    # are matched loosely, because a false catch here fails toward a human
    # look while a miss fails silent (Codex r2). Code is stripped first with
    # the validator's own scanner, so a refdef-shaped EXAMPLE in a fence is
    # not an escape (Codex r3). That scanner's documented over-stripping bias
    # is inherited: a live link bracketed by backslash-escaped backticks reads
    # as a code span and is missed (docs/known-limitations.md, Codex r4) —
    # accepted, because demo/ is repo-controlled, maintainer-reviewed prose.
    _REFDEF = re.compile(r"^[>\s*+\-\d.)]*\[[^\]]+\]:\s*<?([^\s>]+)", re.M)

    @classmethod
    def escapes(cls):
        found = set()
        demo = REPO / "demo"
        demo_real = os.path.realpath(str(demo))
        for dirpath, dirnames, filenames in os.walk(demo):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                with open(p, encoding="utf-8") as fh:
                    text = validate._strip_code(fh.read())
                targets = cls._LINK.findall(text) + cls._REFDEF.findall(text)
                for target in targets:
                    if target.startswith(("http:", "https:", "mailto:")):
                        continue
                    target = target.split("#", 1)[0]
                    if not target:
                        continue
                    # realpath, not normpath: a symlink inside demo/ must not
                    # smuggle a lexically-inside path to an engine file.
                    resolved = os.path.realpath(os.path.join(dirpath, target))
                    if os.path.commonpath([resolved, demo_real]) != demo_real:
                        found.add((os.path.relpath(p, REPO).replace(os.sep, "/"),
                                   target))
        return found

    def test_escaping_links_are_exactly_the_known_four(self):
        found = self.escapes()
        # Anti-hollow: a walker that finds nothing "passes" a subset check.
        self.assertGreater(len(found), 0, "the link scan found nothing at all")
        self.assertEqual(found, self.KNOWN_ESCAPES,
                         "demo/'s engine-pointing links changed. New ones make the "
                         "reference target less liftable; removed ones should be "
                         "dropped from KNOWN_ESCAPES.")


class TestGeneratedCompanyRepo(unittest.TestCase):
    """The adopter's required path, proven: a company repo in the shape
    interview/generate.md specifies passes the gate as its OWN root.

    Nothing else exercises validate(root) with root != this engine, so the four
    root-only checks — check_root_files, check_hooks, check_agents_chain,
    check_always_loaded_budget — have never run against company-shaped content.
    This is where a manifest that specifies something the validator rejects
    surfaces, in this repo's CI rather than in an adopter's afternoon."""

    AGENTS = """# Acme Logistics — company OS

This repository is the operating system for this company: what each function does,
which work is agent-run, who owns each agent, and the rules that bind them.

## Where things are

| What | Where |
|---|---|
| What each function does | `ontologies/` |
| The agents, and who owns each | `skills/` |
| The rules, and their appeals | `governance/constitution/` |
| What the company remembers | `memory/` |
| Proposed changes awaiting a human | `proposals/` |
| How this OS was decided | `interview/` |

## The functions

Every function's activity map is `ontologies/<function>/_executive-view.md`; an
acted-on activity carries a deep record beside it. The views hold the detail — this
file only routes.

## The skill roster

| Skill | Owner | Action class |
|---|---|---|
| `feature-request-triage` | Dana Whitfield | reversible-write |
| `onboarding-orchestration` | Ruth Okafor | external-side-effect |
| `performance-review-prep` | Ruth Okafor | reversible-write |
| `renewal-prep` | Marcus Bell | reversible-write |

## Proposing a change

An agent may propose a change to a skill or a rule by writing a file in `proposals/`.
Only the maintainer lands one. The rules that bind every agent, including the review
gate on high-risk actions, are in `governance/`.

## License

The contents of this repository are Acme Logistics' own work, generated with
groundwork and not covered by groundwork's Apache-2.0 license.
"""

    CURSOR = """---
alwaysApply: true
---
Read AGENTS.md for how this company OS is organized.
"""

    REVIEW_GATE = """# Review gate — high-risk actions

You may **propose** a high-risk action — spend, delete, external-send — but you may
not **perform** one. Stop, say what you would do in one line, name the owner on the
relevant Owner's Card, and wait for that person's explicit approval in the session.

This is an instruction, not runtime enforcement. The runnable gate stays in the
groundwork engine; installing it here is a maintainer act.
"""

    MANIFEST_BODY = """# Interview manifest — Umbercress

The interview is complete: five layers confirmed, committed, and generated from.
Sales, engineering, and legal have executive views and nothing deeper — depth is
earned by acting, not by planning to act.
"""

    def _unlink(self, dest, rel, target):
        """Rewrite [text](target) links in the copied file `rel` to plain text."""
        p = os.path.join(dest, rel)
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        new = re.sub(r"\[([^\]]+)\]\(" + re.escape(target) + r"\)", r"\1", text)
        self.assertNotEqual(new, text,
                            "no link to %s to neutralize in %s" % (target, rel))
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(new)

    def _materialize(self, dest):
        shutil.copytree(str(REPO / "demo"), dest)
        # generate.md's precondition 1: generation runs from a COMPLETE interview.
        # demo/ models a later moment — a second-pass turn in flight — so the
        # fixture promotes the copy to the post-generation shape: the fields AND
        # the body, so the manifest does not narrate an open turn while its
        # status says complete (Codex r2).
        man = os.path.join(dest, "interview", "00-manifest.md")
        with open(man, encoding="utf-8") as fh:
            text = fh.read()
        head, sep, body = text.partition("\n---\n")
        self.assertTrue(sep and body, "manifest has no frontmatter to preserve")
        new = head.replace("status: in-progress", "status: complete", 1)
        self.assertNotEqual(new, head, "manifest has no in-progress status to promote")
        head = new
        new = re.sub(r"open_question: \S+", "open_question: none", head, count=1)
        self.assertNotEqual(new, head, "manifest has no open question to close")
        with open(man, "w", encoding="utf-8") as fh:
            fh.write(new + sep + self.MANIFEST_BODY)
        os.remove(os.path.join(dest, "interview", "_working.md"))
        # generate.md: proposals/ is empty at generation. The pending proposal is
        # demo/'s lived-in story, not generated shape.
        os.remove(os.path.join(dest, "proposals", "refusal-names-next-step.md"))
        # The four teaching links point at engine paths that do not exist in a
        # company repo. Neutralize them to plain text — the same transform the
        # generation protocol tells a generator not to need in the first place.
        replaced = 0
        for rel, target in TestDemoIsLiftable.KNOWN_ESCAPES:
            self._unlink(dest, rel.split("/", 1)[1], target)
            replaced += 1
        self.assertEqual(replaced, 4)
        # generate.md's manifest lists no README.md, walkthrough.md, canon.md,
        # or per-directory narration READMEs. Those files are the demo's
        # narrative voice, and any sentence of it can contradict a generated
        # repo (Codex r3: the removed proposal was still narrated as pending).
        # The fixture keeps the demo's content and drops its narration —
        # removed AFTER the escape transform above, which must run against the
        # real files. Nothing that survives links to any of these five.
        for narration in ("README.md", "walkthrough.md", "canon.md",
                          os.path.join("governance", "README.md"),
                          os.path.join("skills", "README.md")):
            os.remove(os.path.join(dest, narration))
        with open(os.path.join(dest, "governance", "review-gate.md"),
                  "w", encoding="utf-8") as fh:
            fh.write(self.REVIEW_GATE)
        with open(os.path.join(dest, "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write(self.AGENTS)
        with open(os.path.join(dest, "CLAUDE.md"), "w", encoding="utf-8") as fh:
            fh.write("@AGENTS.md\n")
        with open(os.path.join(dest, "GEMINI.md"), "w", encoding="utf-8") as fh:
            fh.write("@./AGENTS.md\n")
        os.makedirs(os.path.join(dest, ".cursor", "rules"))
        with open(os.path.join(dest, ".cursor", "rules", "company.mdc"),
                  "w", encoding="utf-8") as fh:
            fh.write(self.CURSOR)

    def _provision(self, repo):
        """Section 1 of delivery/README.md, executed. Both symlinks point straight
        at skills/<name>; the guide says so and says it is the untested hop."""
        os.makedirs(os.path.join(repo, ".agents", "skills"))
        os.makedirs(os.path.join(repo, ".claude", "skills"))
        names = sorted(n for n in os.listdir(os.path.join(repo, "skills"))
                       if os.path.isdir(os.path.join(repo, "skills", n)))
        self.assertGreater(len(names), 0, "no skills to provision — fixture is empty")
        for n in names:
            for d in (".agents", ".claude"):
                os.symlink(os.path.join("..", "..", "skills", n),
                           os.path.join(repo, d, "skills", n))
        return names

    def test_provisioned_repo_still_validates_and_links_resolve(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            names = self._provision(repo)
            # every provisioned path must resolve to a real SKILL.md
            for n in names:
                for base in (".agents", ".claude"):
                    p = os.path.join(repo, base, "skills", n, "SKILL.md")
                    self.assertTrue(os.path.isfile(p),
                                    "%s/skills/%s does not resolve to a SKILL.md" % (base, n))
            errors = [f for f in validate.validate(repo) if f.level == "ERROR"]
            self.assertEqual([(f.path, f.message) for f in errors], [],
                             "the provisioning layer breaks the gate")

    def test_company_repo_validates_as_its_own_root(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            findings = validate.validate(repo)
            errors = [f for f in findings if f.level == "ERROR"]
            self.assertEqual(
                [(f.path, f.message) for f in errors], [],
                "a company repo built to the generate.md manifest does not pass "
                "the gate as its own root")

    def test_fixture_root_files_match_the_manifest(self):
        """The manifest in interview/generate.md is the contract this class
        claims to build (Codex 4.2 r1: the fixture hardcoded its root files,
        so the 'manifest' tests stayed green if the manifest changed; r2: a
        hardcoded expected tuple could not see a root file ADDED to the
        manifest either). The declared set is derived from the fenced tree —
        entries at the top indent level that are not directories — and
        compared against what the fixture actually produces, both ways."""
        text = (REPO / "interview" / "generate.md").read_text(encoding="utf-8")
        block = text.split("## What you write", 1)[1].split("```", 2)[1]
        declared = set()
        for line in block.splitlines():
            if line.startswith("  ") and not line.startswith("   "):
                entry = line.strip().split()[0]
                if not entry.endswith("/"):
                    declared.add(entry)
        self.assertGreaterEqual(
            declared,
            {"AGENTS.md", "CLAUDE.md", "GEMINI.md",
             ".cursor/rules/company.mdc", "groundwork.pin"},
            "the manifest parse lost a known root file — the tree's indent "
            "shape changed and this test's parser needs to follow it")
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            # Top-level plain files plus the .cursor rule; other dotfiles are
            # excluded so an incidental .DS_Store cannot flake the comparison.
            produced = {n for n in os.listdir(repo)
                        if os.path.isfile(os.path.join(repo, n))
                        and not n.startswith(".")}
            cdir = os.path.join(repo, ".cursor", "rules")
            if os.path.isdir(cdir):
                produced |= {".cursor/rules/" + n for n in os.listdir(cdir)}
            self.assertEqual(
                declared, produced,
                "the manifest's root-file set and the fixture's diverge — "
                "whichever side changed, the other must follow")

    def test_fixture_agents_carries_the_license_carveout(self):
        # generate.md's root-files step now requires the company AGENTS.md to
        # state that generated content is the company's own, outside
        # groundwork's license. The fixture models the manifest, so it
        # carries the line — and this couples the two so neither can drop it
        # alone (Codex 4.2 r1).
        gen = (REPO / "interview" / "generate.md").read_text(encoding="utf-8")
        self.assertIn("not covered by", gen)
        self.assertIn("not covered by groundwork's Apache-2.0 license", self.AGENTS)

    def test_manifest_repo_needs_no_gemini_warning(self):
        """Paired with the next test, which is what makes this one mean
        anything: a repo built to generate.md's manifest emits no
        harness-pointer WARN, and the same repo with GEMINI.md removed does."""
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            self.assertEqual(
                [f.message for f in validate.check_root_files(repo)
                 if f.path == "GEMINI.md"], [])

    def test_manifest_repo_without_gemini_md_warns(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            os.remove(os.path.join(repo, "GEMINI.md"))
            self.assertTrue(
                any(f.level == "WARN" and f.path == "GEMINI.md"
                    for f in validate.check_root_files(repo)),
                "the pointer check does not reach a company root")

    def test_the_root_only_checks_actually_ran(self):
        """Zero ERRORs from a check that never looked is indistinguishable from
        zero ERRORs from a clean repo. Break each root-only check's surface in
        turn and demand its specific ERROR, proving all four are live on this
        root."""

        def bad_claude(repo):
            with open(os.path.join(repo, "CLAUDE.md"), "w", encoding="utf-8") as fh:
                fh.write("# not an import\n")

        def oversized_agents(repo):
            # > 32 KiB chain, still < the ~200 KB always-loaded ERROR floor
            with open(os.path.join(repo, "AGENTS.md"), "a", encoding="utf-8") as fh:
                fh.write("x" * 40_000)

        def bloated_agents(repo):
            # ~250 KB -> ~62.5K est. tokens, over the 50K always-loaded ERROR
            with open(os.path.join(repo, "AGENTS.md"), "a", encoding="utf-8") as fh:
                fh.write("x" * 250_000)

        def empty_hooks(repo):
            # a hook set with nothing to install is a named-but-unwired guard
            os.makedirs(os.path.join(repo, "governance", "hooks"))

        probes = [
            ("check_root_files", bad_claude, "does not import AGENTS.md"),
            ("check_agents_chain", oversized_agents, "project_doc_max_bytes"),
            ("check_always_loaded_budget", bloated_agents, "context budget"),
            ("check_hooks", empty_hooks, "no settings.snippet.json"),
        ]
        for name, break_it, expect in probes:
            with tempfile.TemporaryDirectory() as d:
                repo = os.path.join(d, "acme-os")
                self._materialize(repo)
                break_it(repo)
                msgs = [f.message for f in validate.validate(repo)
                        if f.level == "ERROR"]
                self.assertTrue(any(expect in m for m in msgs),
                                "%s did not run against this root" % name)

    def test_pin_travels_with_the_repo(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            self.assertTrue(os.path.isfile(os.path.join(repo, "groundwork.pin")))
            self.assertEqual(validate.check_version_pin(repo), [],
                             "skew 0 must be silent on a company root")


class TestCompanyRoot(unittest.TestCase):
    """check_company_root: a root pin with no root AGENTS.md is a WARN — the
    one silent-on-absence gap left open at the entry point. Root pin ONLY:
    a nested pin (the engine's demo/) must never trip it."""

    def test_pinned_root_without_agents_md_warns_once(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", PIN_OK)
            findings = validate.check_company_root(d)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].level, "WARN")
            self.assertIn("no root AGENTS.md", findings[0].message)
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_pinned_root_with_agents_md_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", PIN_OK)
            _write(d, "AGENTS.md", "# a company OS\n")
            self.assertEqual(validate.check_company_root(d), [])

    def test_unpinned_root_is_silent_even_without_agents_md(self):
        # The engine case: no pin means no company-repo claim to check.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/README.md", "# content, no pin\n")
            self.assertEqual(validate.check_company_root(d), [])

    def test_nested_pin_does_not_trip_the_root_check(self):
        # The scoping bug class: the engine root has demo/groundwork.pin.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/groundwork.pin", PIN_OK)
            self.assertEqual(validate.check_company_root(d), [])

    def test_pin_as_directory_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "groundwork.pin"))
            self.assertEqual(validate.check_company_root(d), [])

    def test_engine_root_is_silent(self):
        # The 7-WARN invariant's trigger: this repo carries no root pin.
        self.assertEqual(validate.check_company_root(str(REPO)), [])

    def test_validate_wires_company_root(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", PIN_OK)
            findings = validate.validate(d)
            self.assertTrue(any(f.level == "WARN" and "no root AGENTS.md" in f.message
                                for f in findings),
                            "check_company_root is not wired into validate()")

    # -- the second finding: skills nothing can load (delivery/README.md §1) --

    def _pinned_with_skills(self, d, *skills):
        _write(d, "groundwork.pin", PIN_OK)
        _write(d, "AGENTS.md", "# a company OS\n")
        for name in skills:
            _write(d, "skills/%s/SKILL.md" % name, "# a skill\n")

    def test_pinned_skills_with_no_harness_path_warn_once_not_per_skill(self):
        with tempfile.TemporaryDirectory() as d:
            self._pinned_with_skills(d, "renewal-prep", "feature-request-triage")
            findings = validate.check_company_root(d)
            self.assertEqual(len(findings), 1,
                             "one WARN per repo, not one per skill")
            self.assertEqual(findings[0].level, "WARN")
            self.assertIn("no harness-visible path", findings[0].message)
            self.assertIn("2 skill package(s)", findings[0].message)
            self.assertIn("delivery/README.md", findings[0].message)

    def test_pinned_skills_with_agents_skills_entry_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self._pinned_with_skills(d, "renewal-prep")
            os.makedirs(os.path.join(d, ".agents", "skills", "renewal-prep"))
            self.assertEqual(validate.check_company_root(d), [])

    def test_pinned_skills_with_claude_skills_entry_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self._pinned_with_skills(d, "renewal-prep")
            os.makedirs(os.path.join(d, ".claude", "skills", "renewal-prep"))
            self.assertEqual(validate.check_company_root(d), [])

    def test_pinned_root_with_no_skills_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", PIN_OK)
            _write(d, "AGENTS.md", "# a company OS\n")
            self.assertEqual(validate.check_company_root(d), [])

    def test_unpinned_root_with_skills_is_silent(self):
        # The engine case: skills/ exists here, and no root pin means no claim.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/renewal-prep/SKILL.md", "# a skill\n")
            self.assertEqual(validate.check_company_root(d), [])

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "root ignores directory permission bits")
    def test_unlistable_dot_directory_does_not_false_warn(self):
        # An unreadable .agents/skills cannot prove the skills are invisible;
        # asserting "no harness-visible path" anyway is the false positive
        # this check fails away from (Codex 4.1 r1 finding 2).
        with tempfile.TemporaryDirectory() as d:
            self._pinned_with_skills(d, "renewal-prep")
            locked = os.path.join(d, ".agents", "skills")
            os.makedirs(locked)
            os.chmod(locked, 0)
            try:
                self.assertEqual(validate.check_company_root(d), [])
            finally:
                os.chmod(locked, 0o755)

    def test_empty_dot_directories_do_not_count_as_visible(self):
        # mkdir -p with no symlinks yet is not provisioning.
        with tempfile.TemporaryDirectory() as d:
            self._pinned_with_skills(d, "renewal-prep")
            os.makedirs(os.path.join(d, ".agents", "skills"))
            os.makedirs(os.path.join(d, ".claude", "skills"))
            findings = validate.check_company_root(d)
            self.assertEqual(len(findings), 1)
            self.assertIn("no harness-visible path", findings[0].message)


if __name__ == "__main__":
    unittest.main()
