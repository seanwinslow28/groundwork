# groundwork V1 — Phase 0 + Validator Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the repo from charting-workbench to build-workbench, pay down the two live README honesty debts, land the locked positioning/attribution content, and build the zero-dep validator foundation that gates all later content.

**Architecture:** groundwork is a *content* repo (markdown schema files, ontologies, cards) with a single executable artifact, `scripts/validate.py`, that is both a deliverable and the test harness for all content. Phase 0 tasks author markdown; the validator-foundation tasks build the generic checks (frontmatter parsing, secrets, context-budget, referential integrity) using TDD. Schema-specific checks (#5/#6/#7/#8) and the content they gate are a *separate, later* plan.

**Tech Stack:** Python 3.9+ standard library only (`os`, `sys`, `re`, `ast`, `math`, `collections`, `pathlib`). Tests use stdlib `unittest` (no pytest — the whole repo stays install-free). Markdown for all content.

## Global Constraints

- **`scripts/validate.py` imports nothing outside the Python standard library.** No `requirements.txt`, no third-party deps. This is an enforced invariant with a self-check test. (#11)
- **Python floor: 3.9+.** (#11)
- **Tests use stdlib `unittest` only**, runnable via `python3 -m unittest discover -s tests`.
- **Findings have two levels:** `ERROR` fails the gate (process exits 1); `WARN` prints but does not fail (exit 0). (#5/#7 doctrine.)
- **Honesty rule (brief §9, CLAUDE.md #8):** no README claim about what groundwork *does* may precede the capability existing. Facts about the world/design may go in now.
- **Per-session gate (build phase):** every increment ends with `python3 scripts/validate.py` green → Codex review → Sean merges. Fable 5 builds; this plan is its task list.
- **Commit style:** end commit messages with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

---

## File Structure

- `docs/agents/build-sessions.md` — **create.** Build-phase session rules (migrated out of the charting `CLAUDE.md`).
- `CLAUDE.md` — **modify.** Retire charting/wayfinder language; point build agents at `build-sessions.md`. (Stays a full file until Phase 1 Move 2 collapses it to `@AGENTS.md`.)
- `README.md` — **modify** (Tier 0 then Tier 1).
- `scripts/validate.py` — **create.** The validator foundation.
- `tests/test_validate.py` — **create.** stdlib `unittest` suite.
- `tests/fixtures/stub/` — **create.** Minimal content tree so every check runs against real input (not inert).

---

## Task 1: Workbench migration (Phase 0.1a)

**Files:**
- Create: `docs/agents/build-sessions.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Produces: `docs/agents/build-sessions.md` as the durable home of build-session rules; later tasks and sessions reference it.

- [ ] **Step 1: Create `docs/agents/build-sessions.md`** with this content:

```markdown
# Build-session rules (groundwork build phase)

> Replaces the wayfinder charting rules now that the map is complete. These are workbench rules for build sessions; they are NOT product content and never ship to adopters.

## Session shape
1. **One increment per session.** Build it, `validate` green, Codex-review, record what it revealed, stop. The pull to keep going is the signal to stop.
2. **One increment ends green:** `python3 scripts/validate.py` passes (zero ERRORs) before a session is done.
3. **Review gate:** Fable 5 builds; the Codex plugin reviews at session end (`/codex` review or `codex:codex-rescue`); the maintainer (Sean) lands the merge — the commit bit is the governance teeth (#18).
4. **Claim before work:** branch before touching the tree (never build on `main`).

## Standing rules (carried from charting)
5. **Explain before Sean decides.** Before each decision he owns, explain in plain terms: what it is, the options, the recommendation, and the honest counter-argument. Never accept "go with your recommendation" as a substitute for understanding.
6. **Honesty rules:** claims match what is verified/built; no capability claim precedes the capability; overclaiming is trust debt.
7. **Source of truth:** the approved design brief and CONTEXT.md (the resolved-decision glossary). Locked decisions are not reopened without new evidence.

## Where the plan lives
- Design: `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md`
- Plans: `docs/superpowers/plans/` (this file's siblings), one per phase-slice.
```

- [ ] **Step 2: Retire charting language from `CLAUDE.md`.** Open `CLAUDE.md`. Replace the `## Session rules (wayfinder)` section and the "TEMPORARY FILE / charting phase" framing with a short build-phase pointer. Keep the "What this repo is" orientation but update it to say charting is complete and build is underway. Add near the top:

```markdown
## Build phase
Charting is complete (all 19 wayfinder decisions resolved — see CONTEXT.md and issue #1). Build sessions follow **[docs/agents/build-sessions.md](docs/agents/build-sessions.md)**. This file is replaced by the product's one-line `@AGENTS.md` import once the vertical slice proves the structure (design doc, Decision 2, Move 2).
```

Delete the numbered wayfinder session-rules list (1–9) and the "Process notes" wayfinder-specific bullets. Preserve the `explain-before-deciding` rule by pointing to `build-sessions.md` §5 (do not lose it).

- [ ] **Step 3: Verify no charting-only language remains where it would mislead a build agent.**

Run: `grep -niE 'one ticket per session|wayfinder map-working|grilling tickets|charting phase\.' CLAUDE.md`
Expected: no matches (the wayfinder session-rules are gone; any remaining "charting" mention is historical, e.g. "charting is complete").

- [ ] **Step 4: Commit**

```bash
git add docs/agents/build-sessions.md CLAUDE.md
git commit -m "chore: migrate build rules to build-sessions.md; retire charting CLAUDE.md language

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: README Tier 0 — pay down live honesty debt (Phase 0.1b)

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing.
- Produces: a README whose License and status facts are correct (unblocks Tier 1 in Task 3).

The current README says License is "TBD" (wrong — #3 locked Apache-2.0) and "Nothing is built yet" (wrong — build has started). Fix exactly those two facts; do not add capability claims yet.

- [ ] **Step 1: Replace the `## Status: charting` section** with:

```markdown
## Status: building V1

The design is fully charted — all 19 [wayfinder decisions](../../issues/1) are resolved and recorded (see [CONTEXT.md](CONTEXT.md)). Build is underway; capabilities are described here only as they become real.
```

- [ ] **Step 2: Replace the `## License` section** with:

```markdown
## License

[Apache-2.0](LICENSE) — chosen for its patent grant (enterprise-counsel comfort). Content generated into `your-company/` is the adopter's own and is **not** covered by this license (an explicit README/NOTICE carve-out ships with the generator).
```

(The `LICENSE` file itself is authored in Phase 4; linking it now is acceptable — it is a near-term deliverable, and the license *decision* is final. If a reviewer objects to linking a not-yet-created file, unlink to plain text `Apache-2.0` until Phase 4.)

- [ ] **Step 3: Verify the stale facts are gone.**

Run: `grep -niE 'TBD|all rights reserved|nothing is built' README.md`
Expected: no matches.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README Tier 0 — Apache-2.0 license + building-V1 status (fix stale facts)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: README Tier 1 — positioning + prior art (Phase 0.2)

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Tier 0 README (Task 2); CONTEXT.md "Positioning (#15)" and "Attribution (#14)" clusters (the verbatim vocabulary and `Avoid` guardrails).
- Produces: a positioning section and a bottom prior-art section.

This is authored prose, gated by the guardrails below (not ghostwritten here). The build session writes the copy; these are the required claims and the forbidden phrasings. **Every `Avoid` item is a review-rejection trigger.**

### 3A — Positioning subsection (#15)

Add a `## How groundwork compares` (or fold into an existing positioning section) with a compact comparison and an "On the two active projects" prose subsection (**prose is the single source of truth**; a table row may summarize but must not carry the nuance).

**Required claims:**
- Name **Sylph** ([getnao/sylph](https://github.com/getnao/sylph)) and **clawcompany** ([Claw-Company/clawcompany](https://github.com/Claw-Company/clawcompany)) — the two active same-category projects.
- Concede, *in the same breath as each contrast:* Sylph shipped the self-improving-company-brain-as-git-repo **shape** first (May 2026) — groundwork did not invent the loop. clawcompany's 4-layer compressed memory is real context-budget prior art.
- The one fully-owned contrast against both: **governance** — typed rules + owners + appeals + a validator; vs Sylph specifically, review of the *rule change itself* (Sylph's rewrite fires automatically, unreviewed — README line 53), not just the output.
- Frame clawcompany as a **category difference**: a fat runtime you adopt (multi-*provider*) vs files any agent already reads — **never** "we support more harnesses."

**Avoid (rejection triggers, from CONTEXT.md #15):** `differentiator` before checking it isn't shared; "we invented / first to"; "abandoned" / commit-count / star-count digs / "hobby project"; "self-improving" as a groundwork-unique claim (the loop is shared — only its *governance* is ours); "we're more portable / more harnesses" for clawcompany.

### 3B — Prior-art & inspiration block (#14)

Add `## Prior art & inspiration` at the **bottom** of the README, in **prose bullets** (not a table — a table reframes gratitude as competitive scoring).

**Required — the 5 load-bearing sources, each with what-we-took / how-we-differ / free-or-paid:**
- **JZ / Jiaona Zhang / Laurel** — ontology→skills→delivery, captain model, two-track review, maturity levels. Free editorial, no product; we reimplement, not fork.
- **Aakash Gupta + Hannah Stulberg** — Team OS pattern + consent-gated classification ("share only on positive evidence; no leak-by-default"). **Name Hannah Stulberg as the DoorDash origin.** Guide is paid; a public starter repo exists (Team OS is **not** fully closed).
- **Nate B. Jones** — work-packages, SOUL.md elicitation, "every agent needs an owner," agent-shaped-work test. **Open Skills is *paid*; his open artifact is Open Brain / OB1.**
- **dswh / company-os** — closest interview-install prior art; coined "self-installing AI-native company operating system"; source-available seed. governed/compiled is our delta.

**The 3 brief-fact corrections must be visibly correct in the copy:** (1) Nate's Open Skills = paid, open artifact = Open Brain/OB1; (2) Aakash's Team OS is not fully closed (public starter repo; Hannah Stulberg origin); (3) the "5 structural tests" is likely his **7-row control map** — describe the verified mechanic, not the unverified coinage.

**Paid-content posture (A−):** name the source, link the paywalled original, send the traffic, say "the idea is theirs / this open implementation is ours." **No "worth buying" endorsement.**

**Avoid (rejection triggers, from CONTEXT.md #14):** top-of-README credit; a comparison table for credits; `NOTICE` for inspiration-credit (Apache term-of-art); "a free alternative to X" / "everything in their kit, open"; "worth buying"; quoting an unverified slogan ("Shared Discipline" / "Classify→Consent→Enforce" / "constitution machinery") as someone's coinage; an exhaustive "also surveyed" wall of names (thin tail — Workflowsio/gbrain/beevibe/skill-libraries — stays landscape in the positioning section, not repeated in credits).

- [ ] **Step 1:** Author subsection 3A per the guardrails above.
- [ ] **Step 2:** Author the bottom block 3B per the guardrails above.
- [ ] **Step 3: Verify the load-bearing names and the corrections are present.**

Run: `grep -ciE 'Hannah Stulberg|Open Brain|OB1|Apache-2.0' README.md`
Expected: ≥ 3 matches (Hannah Stulberg, Open Brain/OB1, and the corrections are present).

Run: `grep -niE 'worth buying|free alternative|first to|we invented' README.md`
Expected: no matches (forbidden phrasings absent).

- [ ] **Step 4: Codex review** the positioning + credit copy against the `Avoid` lists before merge (this content is honesty-critical).

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: README Tier 1 — positioning (#15) + prior-art credit (#14) + brief-fact corrections

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Validator foundation — Finding, frontmatter reader, CLI gate, stub fixture (Phase 1.1a)

**Files:**
- Create: `scripts/validate.py`
- Create: `tests/test_validate.py`
- Create: `tests/fixtures/stub/good.md`, `tests/fixtures/stub/linked.md`

**Interfaces:**
- Produces:
  - `Finding = namedtuple("Finding", ["level", "path", "line", "message"])`, `level in {"ERROR","WARN"}`.
  - `parse_frontmatter(text: str, path: str="<unknown>") -> (dict, list[Finding])` — flat frontmatter only; every scalar is a **raw string** (no type coercion); ERRORs (with line no.) on unsupported syntax.
  - `validate(root: str) -> list[Finding]` — walks `root`, runs all checks, returns findings.
  - `main(argv: list[str]) -> int` — exit 1 if any ERROR, else 0.

- [ ] **Step 1: Write the failing tests** in `tests/test_validate.py`:

```python
import ast
import pathlib
import sys
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
        allowed = {"os", "sys", "re", "ast", "math", "collections", "pathlib"}
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


class TestGate(unittest.TestCase):
    def test_clean_stub_fixture_passes(self):
        findings = validate.validate(str(REPO / "tests" / "fixtures" / "stub"))
        errors = [f for f in findings if f.level == "ERROR"]
        self.assertEqual(errors, [], "unexpected errors: %s" % errors)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Create the stub fixture** so `validate()` has real, clean input:

`tests/fixtures/stub/good.md`:
```markdown
---
owner: Ada Lovelace
allowed:
  - read
---
# Good stub
A clean file. See [the linked note](linked.md).
```

`tests/fixtures/stub/linked.md`:
```markdown
# Linked note
Nothing to see here.
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'validate'` (or AttributeErrors) because `scripts/validate.py` does not exist yet.

- [ ] **Step 4: Write `scripts/validate.py`** (foundation only — checks are added in Tasks 5–7):

```python
#!/usr/bin/env python3
"""groundwork validator — Python stdlib only (zero third-party deps, enforced).

Walks a repo tree and reports ERROR/WARN Findings. ERROR fails the gate.
Schema-specific checks (#5/#6/#7/#8) live in a later build slice; this module
is the generic foundation: frontmatter parsing, secrets, context budget,
referential integrity.
"""
import os
import re
import sys
from collections import namedtuple

Finding = namedtuple("Finding", ["level", "path", "line", "message"])

SKIP_DIRS = {".git", ".remember", "__pycache__"}


def parse_frontmatter(text, path="<unknown>"):
    """Parse a restricted frontmatter block. Returns (dict, list[Finding]).

    Grammar (flat subset only): a leading '---' line, then lines that are
    'key: value', 'key:' (introducing a list), '- item' list elements, blank,
    or '# comment', terminated by a closing '---'. Every scalar is returned as
    a RAW STRING (no type coercion — field validators own all typing, which
    sidesteps the Norway/date-coercion problems). Any other syntax ERRORs.
    """
    findings = []
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, findings  # no frontmatter block is not itself an error
    data = {}
    current_key = None
    closed = False
    i = 1
    while i < len(lines):
        raw = lines[i]
        line_no = i + 1
        stripped = raw.strip()
        if stripped == "---":
            closed = True
            break
        if stripped == "" or stripped.startswith("#"):
            i += 1
            continue
        if stripped.startswith("- "):
            if current_key is None:
                findings.append(Finding("ERROR", path, line_no, "list item with no preceding key"))
            elif not isinstance(data.get(current_key), list):
                findings.append(Finding("ERROR", path, line_no,
                                        "list item under scalar key '%s'" % current_key))
            else:
                data[current_key].append(stripped[2:].strip())
            i += 1
            continue
        if raw.startswith((" ", "\t")):
            findings.append(Finding("ERROR", path, line_no,
                                    "unsupported indented frontmatter syntax: %r" % raw))
            i += 1
            continue
        if ":" in raw:
            key, _, value = raw.partition(":")
            key, value = key.strip(), value.strip()
            if key == "":
                findings.append(Finding("ERROR", path, line_no, "empty frontmatter key"))
            elif value == "":
                data[key] = []          # a list is expected to follow
                current_key = key
            else:
                data[key] = value       # raw string, no coercion
                current_key = key
            i += 1
            continue
        findings.append(Finding("ERROR", path, line_no,
                                "unsupported frontmatter syntax: %r" % raw))
        i += 1
    if not closed:
        findings.append(Finding("ERROR", path, len(lines),
                                "frontmatter block opened with '---' but never closed"))
    return data, findings


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def validate(root):
    """Walk root, run every check, return a flat list[Finding]."""
    root = os.path.abspath(root)
    findings = []
    for abspath in iter_files(root):
        rel = os.path.relpath(abspath, root)
        try:
            data_bytes = open(abspath, "rb").read()
        except OSError:
            continue
        # (context-budget check added in Task 6)
        try:
            text = data_bytes.decode("utf-8")
        except UnicodeDecodeError:
            continue
        # (secrets check added in Task 5; link check added in Task 7)
    return findings


def main(argv):
    root = argv[1] if len(argv) > 1 else "."
    findings = validate(root)
    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]
    for f in findings:
        loc = f.path + ((":%d" % f.line) if f.line else "")
        print("%-5s %s  %s" % (f.level, loc, f.message))
    print("\n%d error(s), %d warning(s)" % (len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate -v`
Expected: PASS (all tests in `TestFrontmatter`, `TestZeroDep`, `TestGate`).

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py tests/fixtures/stub/
git commit -m "feat(validate): foundation — Finding, frontmatter reader, CLI gate, stub fixture

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Secrets floor check (Phase 1.1b)

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `Finding`, `validate()` from Task 4.
- Produces: `check_secrets(text, path) -> list[Finding]` (ERROR, global) and `check_entropy(text, path) -> list[Finding]` (WARN). Both labeled "high-signal, not exhaustive."

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestSecrets -v`
Expected: FAIL — `AttributeError: module 'validate' has no attribute 'check_secrets'`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py` (after `parse_frontmatter`, add `import math` to the import block at top):

```python
SECRET_PATTERNS = [
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP |DSA )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("OpenAI-style API key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
]
_HIGH_ENTROPY = re.compile(r"[A-Za-z0-9+/=_-]{40,}")


def check_secrets(text, path):
    """High-signal, not exhaustive. Global ERROR — a leaked credential is
    dangerous everywhere (unlike the demo-only synthetic rule, #16)."""
    findings = []
    for lineno, line in enumerate(text.split("\n"), 1):
        for label, pat in SECRET_PATTERNS:
            if pat.search(line):
                findings.append(Finding("ERROR", path, lineno,
                                        "possible %s (high-signal, not exhaustive)" % label))
    return findings


def _shannon_entropy(s):
    if not s:
        return 0.0
    return -sum((s.count(c) / len(s)) * math.log2(s.count(c) / len(s)) for c in set(s))


def check_entropy(text, path):
    findings = []
    for lineno, line in enumerate(text.split("\n"), 1):
        for tok in _HIGH_ENTROPY.findall(line):
            if _shannon_entropy(tok) >= 4.0:
                findings.append(Finding("WARN", path, lineno,
                                        "high-entropy string (possible secret; high-signal, not exhaustive)"))
    return findings
```

- [ ] **Step 4: Wire the checks into `validate()`** — inside the `for abspath` loop, after the `text = data_bytes.decode(...)` line, replace the `# (secrets check ...)` comment with:

```python
        findings += check_secrets(text, rel)
        findings += check_entropy(text, rel)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_validate -v`
Expected: PASS (including the still-passing `TestGate.test_clean_stub_fixture_passes` — the stub fixture has no secrets).

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): global secrets floor (regex ERROR + entropy WARN), high-signal

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Context-budget check (Phase 1.1c)

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `Finding`, `validate()`.
- Produces: `est_tokens(num_bytes) -> int`; `check_context_budget(path, data_bytes) -> list[Finding]`. Thresholds (#13): WARN ≥ 20,000 est. tokens, ERROR ≥ 50,000 est. tokens; est. tokens = bytes // 4.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestBudget -v`
Expected: FAIL — no attribute `check_context_budget`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
WARN_TOKENS = 20_000
ERROR_TOKENS = 50_000


def est_tokens(num_bytes):
    """Measure bytes, report estimated tokens (stdlib len/4 heuristic, #13)."""
    return num_bytes // 4


def check_context_budget(path, data_bytes):
    toks = est_tokens(len(data_bytes))
    if toks >= ERROR_TOKENS:
        return [Finding("ERROR", path, None,
                        "context budget: ~%d est. tokens (>= %d ERROR)" % (toks, ERROR_TOKENS))]
    if toks >= WARN_TOKENS:
        return [Finding("WARN", path, None,
                        "context budget: ~%d est. tokens (>= %d WARN)" % (toks, WARN_TOKENS))]
    return []
```

- [ ] **Step 4: Wire into `validate()`** — replace the `# (context-budget check added in Task 6)` comment with:

```python
        findings += check_context_budget(rel, data_bytes)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_validate -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): context-budget check (bytes measured, est. tokens WARN 20k/ERROR 50k)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Referential-integrity check (Phase 1.1d)

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`
- Create: `tests/fixtures/broken/has_broken_link.md`

**Interfaces:**
- Consumes: `Finding`, `validate()`.
- Produces: `check_links(abspath, text, root) -> list[Finding]` — ERROR on a broken *relative* markdown link; http(s)/mailto/anchor-only links are skipped.

- [ ] **Step 1: Add a broken-link fixture** `tests/fixtures/broken/has_broken_link.md`:

```markdown
# Broken
This points at [a missing file](does-not-exist.md).
```

- [ ] **Step 2: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestLinks -v`
Expected: FAIL — no attribute `check_links` (and the broken-link test does not yet error).

- [ ] **Step 4: Implement** — add to `scripts/validate.py`:

```python
_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_links(abspath, text, root):
    """ERROR on broken relative markdown links. External and anchor-only
    links are skipped (referential integrity, brief §10 validator)."""
    findings = []
    base = os.path.dirname(abspath)
    for lineno, line in enumerate(text.split("\n"), 1):
        for target in _LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = os.path.normpath(os.path.join(base, path_part))
            if not os.path.exists(resolved):
                findings.append(Finding("ERROR", os.path.relpath(abspath, root), lineno,
                                        "broken relative link: %s" % target))
    return findings
```

- [ ] **Step 5: Wire into `validate()`** — replace the `# (secrets check added in Task 5; link check added in Task 7)` comment (now just the link portion) with a markdown-gated call. Inside the loop, after the secrets/entropy/budget calls, add:

```python
        if abspath.endswith(".md"):
            findings += check_links(abspath, text, root)
```

- [ ] **Step 6: Run the full suite to verify it passes**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (all classes).

- [ ] **Step 7: Run the validator on the real repo to confirm the gate is honest**

Run: `python3 scripts/validate.py .`
Expected: exits 0 (no ERRORs) OR reports only genuine issues to fix before merge. Any ERROR must be resolved before the session is done (per the per-session gate).

- [ ] **Step 8: Commit**

```bash
git add scripts/validate.py tests/test_validate.py tests/fixtures/broken/
git commit -m "feat(validate): referential-integrity check (broken relative links ERROR)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Scope note — what this plan deliberately excludes

Deferred to the **next** plan (`Phase 1.2–1.5`), because each is content that the validator built here will gate, and each benefits from Sean's eyes as the schema files emerge:
- Ontology schema files + #5 machinery-follows checks (1.2)
- Work-package spec + Owner's Card + fixed Claude-Code hook set + #6 checks (1.3)
- Org-memory schema + baseline record + memory `--diff` mode + #7 checks (1.4)
- Constitution templates + one compiled rule + version pin (#21) + proposal schema (#17) + consent-gate `--diff` tripwire (#18) + demo canon + synthetic-identifier check (#16) (1.5)
- **D2 Move 2** (author `AGENTS.md`, collapse `CLAUDE.md` to `@AGENTS.md`, add `.cursor/rules/`) fires at the end of Phase 1.

The AGENTS.md context-budget *chain* check (#13, >32 KiB hard ERROR over the `@import` chain) is deferred to Move 2, when an `AGENTS.md` exists to measure — implementing it now would be an inert check against an absent file.

## Self-Review

- **Spec coverage (Phase 0 + 1.1):** 0.1a → Task 1; 0.1b (Tier 0) → Task 2; 0.2 (Tier 1) → Task 3; 1.1 frontmatter+gate → Task 4; secrets floor → Task 5; context-budget → Task 6; referential integrity → Task 7. Zero-dep self-check → Task 4 `TestZeroDep`. Stub-fixture-so-not-inert → Tasks 4 & 7 fixtures. All covered.
- **Placeholder scan:** no "TBD/TODO/handle edge cases"; content tasks carry exact copy or exact guardrails + verification greps; code tasks carry complete code.
- **Type consistency:** `Finding(level, path, line, message)` used identically across all tasks; `validate()`, `check_secrets`, `check_entropy`, `check_context_budget`, `est_tokens`, `check_links`, `parse_frontmatter` signatures match their `Interfaces` blocks and their call sites in `validate()`.
- **Deviation from spec (flagged, not silent):** the AGENTS.md-chain budget check moves from 1.1 to Move 2 to avoid an inert check; referential integrity is kept in 1.1 but exercised by a real fixture (stub valid link + broken fixture) so it is not inert — matching the spec's "paired with a stub so it isn't inert" language.
