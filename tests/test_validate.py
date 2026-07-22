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
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections", "pathlib"}
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


if __name__ == "__main__":
    unittest.main()
