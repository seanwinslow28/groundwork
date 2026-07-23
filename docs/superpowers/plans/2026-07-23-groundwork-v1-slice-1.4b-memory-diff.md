# groundwork V1 — Slice 1.4b: `--diff` memory-immutability mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship #7's stateful `--diff <base>` mode — the mechanical backstop for "org-memory records are never edited." It compares the working tree's memory records against a git base ref and ERRORs on immutable-field changes (frozen body/`valid_at`, provenance downgrades, non-append `source`, altered supersession fields, deleted records). The default validator run stays stateless.

**Architecture:** A pure function `check_memory_diff(old_text, new_text, path)` holds all the immutability rules and is unit-tested without git. A thin git layer (`memory_diff_findings(root, base)`) fetches each record's base version via `git show <base>:<path>` and detects deletions via `git ls-tree`. The CLI grows a `--diff <base>` flag that runs the normal `validate()` **and** appends the diff findings (one PR/CI invocation, full picture). This is the last piece of the #7 memory story before governance.

**Tech Stack:** Python 3.9+ standard library only (adds `subprocess`); stdlib `unittest` (integration test shells out to `git`); Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only** (this slice adds `subprocess`). **Add `subprocess` to `TestZeroDep`'s allowlist** (`tests/test_validate.py`, currently `{"os", "sys", "re", "ast", "math", "fnmatch", "collections", "pathlib", "datetime"}`).
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **#7 mutability (verbatim):** frozen = body + `valid_at`; mutable-as-governance = `owner` (reassignable), `review_by` (bumpable), `source` (**append-only**), provenance label (**forward only**: `observed`/`inferred` → `confirmed`; → `superseded` via the invariants; **no downgrades**), `invalid_at`/`superseded_by` (**set once**, at supersession). Records are **superseded, never deleted**.
- **#7 diff scope:** the `--diff` mode is **scoped to the memory folder**; it checks immutability of records that existed at `<base>`. New records (adds) are fine.
- **The default (no-`--diff`) run stays stateless** — nothing about this slice changes the plain `validate()` behavior.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.4 merged to `main` (done: `fc3d719`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.4b-memory-diff`.

---

## File Structure

- `scripts/validate.py` — **modify.** Add `import subprocess`; add `_frontmatter_and_body`, `_as_list`, `_PROV_FORWARD`, `check_memory_diff`, `memory_diff_findings`; extend `main()` to parse `--diff <base>`.
- `tests/test_validate.py` — **modify.** Pure-function diff tests + one git integration test; extend `TestZeroDep`'s allowlist.
- `memory/README.md` — **modify.** Document the `--diff` mode.

> **Design note.** The immutability rules live in the **pure** `check_memory_diff` (git-free, exhaustively unit-testable); git is confined to `memory_diff_findings` (fetch base versions, detect deletions) with a single integration test. This keeps the hard-to-test git surface thin. The `--diff` diff infrastructure (`git show <base>:<path>`) is deliberately reusable — Slice 1.5's #18 consent-gate blast-radius tripwire diffs escalating changes the same way.

---

## Task 1: The pure immutability diff function

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`
- Modify: `memory/README.md`

**Interfaces:**
- Produces:
  - `_frontmatter_and_body(text) -> (dict, str)` — the parsed frontmatter and the body after the closing `---`.
  - `_as_list(v) -> list` — `None`/`[]` → `[]`; a scalar → `[scalar]`; a list → itself.
  - `_PROV_FORWARD` — allowed provenance transitions (each set includes the same value, i.e. "no change").
  - `check_memory_diff(old_text, new_text, path) -> list[Finding]` — all ERRORs, one per violated immutability rule.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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

    def test_supersession_field_set_once(self):
        old = (MEM_OK.replace("provenance: observed", "provenance: superseded")
               .replace("review_by: 2099-10-15",
                        "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/new.md"))
        new = old.replace("invalid_at: 2026-08-01", "invalid_at: 2026-09-01")
        self.assertTrue(any(f.level == "ERROR" and "invalid_at" in f.message
                            for f in validate.check_memory_diff(old, new, "m.md")))

    def test_unchanged_record_clean(self):
        self.assertEqual(validate.check_memory_diff(MEM_OK, MEM_OK, "m.md"), [])
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestMemoryDiff -v`
Expected: FAIL — no attribute `check_memory_diff`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
_PROV_FORWARD = {
    "observed": {"observed", "confirmed", "superseded"},
    "inferred": {"inferred", "confirmed", "superseded"},
    "confirmed": {"confirmed", "superseded"},
    "superseded": {"superseded"},
}


def _frontmatter_and_body(text):
    data, _ = parse_frontmatter(text)
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return data, "\n".join(lines[i + 1:])
    return data, text


def _as_list(v):
    if v is None or v == []:
        return []
    return v if isinstance(v, list) else [v]


def check_memory_diff(old_text, new_text, path):
    """#7 immutability rules between a record's base version and its new version.
    Pure (no git). All findings are ERROR — an immutable field changed."""
    findings = []
    old_fm, old_body = _frontmatter_and_body(old_text)
    new_fm, new_body = _frontmatter_and_body(new_text)

    if old_body.strip() != new_body.strip():
        findings.append(Finding("ERROR", path, None, "immutable: body changed (frozen at commit)"))
    if old_fm.get("valid_at") != new_fm.get("valid_at"):
        findings.append(Finding("ERROR", path, None, "immutable: valid_at changed (frozen at commit)"))

    op, np = old_fm.get("provenance"), new_fm.get("provenance")
    if isinstance(op, str) and isinstance(np, str) and op in _PROV_FORWARD and np not in _PROV_FORWARD[op]:
        findings.append(Finding("ERROR", path, None,
                                "provenance downgrade / illegal transition: %s -> %s (forward only)" % (op, np)))

    old_src, new_src = _as_list(old_fm.get("source")), _as_list(new_fm.get("source"))
    if new_src[:len(old_src)] != old_src:
        findings.append(Finding("ERROR", path, None,
                                "source is append-only (existing entries cannot be altered or removed)"))

    for field in ("invalid_at", "superseded_by"):
        ov = old_fm.get(field)
        if not _blank(ov) and new_fm.get(field) != ov:
            findings.append(Finding("ERROR", path, None,
                                    "supersession field '%s' is set once and cannot change" % field))
    return findings
```

- [ ] **Step 4: Document the mode** — append to `memory/README.md`:

```markdown

## Checking immutability at PR time

The default `validate` run is stateless (it checks each record's shape). At PR/CI
time, run the diff mode to enforce that records are never edited:

```
python3 scripts/validate.py --diff <base>   # e.g. --diff main
```

It ERRORs on any change to a frozen field (body, `valid_at`), a provenance downgrade,
a non-append `source` change, an altered supersession field, or a **deleted** record
(records are superseded, never deleted). The four-verb reconciliation
(add / update / supersede / discard) stays a human review practice; the diff mode is
its mechanical backstop.
```

- [ ] **Step 5: Run to verify pass**

Run: `python3 -m unittest tests.test_validate.TestMemoryDiff -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py memory/README.md
git commit -m "feat(validate): pure #7 memory-immutability diff function + docs

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The `--diff <base>` git plumbing + CLI wiring

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Produces: `memory_diff_findings(root, base) -> list[Finding]` — fetches each memory record's base version via git, runs `check_memory_diff`, and detects deletions. `main()` parses `--diff <base>` and appends these findings to the normal `validate()` run.

- [ ] **Step 1: Add tests** to `tests/test_validate.py` (a git integration test + the zero-dep allowlist update):

```python
import subprocess as _sp


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
```

Also **update `TestZeroDep`'s allowlist** to include `subprocess`:

```python
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections", "pathlib", "datetime", "subprocess"}
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestMemoryDiffCLI -v`
Expected: FAIL — no attribute `memory_diff_findings`.

- [ ] **Step 3: Implement** — in `scripts/validate.py`, add `import subprocess` to the imports, then add:

```python
def memory_diff_findings(root, base):
    """Compare working-tree memory records against <base> (a git ref). Scoped to
    the memory folder. New records are fine; deletions and immutable-field edits
    are ERRORs."""
    try:
        toplevel = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [Finding("ERROR", root, None, "--diff requires a git repository")]
    findings = []
    for abspath in _memory_record_files(root):
        rel_top = os.path.relpath(abspath, toplevel).replace("\\", "/")
        try:
            old = subprocess.run(["git", "-C", toplevel, "show", "%s:%s" % (base, rel_top)],
                                 capture_output=True, text=True, check=True).stdout
        except subprocess.CalledProcessError:
            continue  # absent at base = a new record (add) — allowed
        with open(abspath, encoding="utf-8") as fh:
            new = fh.read()
        findings += check_memory_diff(old, new, os.path.relpath(abspath, root))
    # deletions: a record present at base but gone now
    try:
        base_files = subprocess.run(["git", "-C", toplevel, "ls-tree", "-r", "--name-only", base],
                                    capture_output=True, text=True, check=True).stdout.splitlines()
    except subprocess.CalledProcessError:
        base_files = []
    for bf in base_files:
        parts = bf.split("/")
        if "memory" in parts and bf.endswith(".md") and os.path.basename(bf) not in {"_index.md", "README.md"}:
            if not os.path.isfile(os.path.join(toplevel, bf)):
                findings.append(Finding("ERROR", bf, None,
                                        "memory record deleted (records are superseded, never deleted)"))
    return findings
```

- [ ] **Step 4: Wire `--diff` into `main()`** — replace `main()` with:

```python
def main(argv):
    args = argv[1:]
    diff_base = None
    if "--diff" in args:
        i = args.index("--diff")
        if i + 1 >= len(args):
            print("ERROR  --diff requires a <base> git ref")
            return 2
        diff_base = args[i + 1]
        args = args[:i] + args[i + 2:]
    root = args[0] if args else "."
    findings = validate(root)
    if diff_base is not None:
        findings += memory_diff_findings(root, diff_base)
    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]
    for f in findings:
        loc = f.path + ((":%d" % f.line) if f.line else "")
        print("%-5s %s  %s" % (f.level, loc, f.message))
    print("\n%d error(s), %d warning(s)" % (len(errors), len(warns)))
    return 1 if errors else 0
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (all classes, including `TestZeroDep` with `subprocess` allowlisted).

- [ ] **Step 6: Prove it on the real repo** (no false positives against `main`)

Run: `python3 scripts/validate.py . && python3 scripts/validate.py --diff main`
Expected: both exit 0. The plain run is unchanged; `--diff main` finds no immutability violations (this branch has not edited the committed memory record).

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): --diff <base> memory-immutability mode (git-backed) + deletion check

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next plans)

- **Slice 1.5 (governance):** constitution rule + #8 typed-rule checks (no-rung-six / orphan / missing-owner), the fixed Claude-Code hook set, version pin (#21), proposal schema (#17), the #18 consent-gate blast-radius `--diff` tripwire (which **reuses this slice's diff infrastructure**), demo canon (#16). This one will split into sub-slices.
- **Not in scope here:** applying `--diff` to non-memory artifacts (the #18 tripwire generalizes it in 1.5); the four-verb reconciliation as anything but human review practice.

## Self-Review

- **Ticket coverage (#7 `--diff`):** stateless-default preserved (main only adds behavior under `--diff`); memory-scoped (only `_memory_record_files`); frozen body/`valid_at` → Task 1; provenance forward-only → Task 1 `_PROV_FORWARD`; append-only `source` → Task 1 prefix check; supersession set-once → Task 1; deleted-record ERROR → Task 2; new records allowed → Task 2 test. Covered.
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; complete code and content; verification commands have expected output.
- **Type consistency:** `Finding`, `_blank`, `parse_frontmatter`, `_memory_record_files` reused with existing signatures; `check_memory_diff(old_text, new_text, path)` and `memory_diff_findings(root, base)` match their call sites (tests + `main`); `_PROV_FORWARD` values are sets, `_as_list` always returns a list so the `source` prefix comparison is list-vs-list.
- **Zero-dep:** `subprocess` is stdlib and added to `TestZeroDep`'s allowlist in Task 2 Step 1 — the self-check stays green.
- **Git-surface containment:** all immutability logic is in the pure `check_memory_diff` (unit-tested without git); `memory_diff_findings` is the only git-touching function and has a temp-repo integration test.
```

