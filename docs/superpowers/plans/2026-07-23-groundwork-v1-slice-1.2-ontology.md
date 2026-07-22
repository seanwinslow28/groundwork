# groundwork V1 — Slice 1.2: Ontology schema + #5 checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two carryover items from Phase 0 (validator gate hygiene; a README headline honesty reframe), then land the ontology schema as files (#5 two-tier) with the People/HR onboarding-orchestration deep record and the #5 "machinery-follows" validator checks — the second increment of the vertical slice.

**Architecture:** The ontology is the brief's "primary artifact." It is represented as **one directory per function** under `ontologies/`. Each function dir holds a presentable `_executive-view.md` (a markdown table: every activity + its Direction, acted-on ones linking to a deep record) and one **deep-record `.md` file per acted-on activity** whose flat frontmatter carries the structured, machine-checked fields (#5 common core, plus automation-path fields + the Describability Gate). The presence of a deep-record file *is* the "acted-on" signal; an activity in the exec view with no deep record is an untouched worksheet the validator stays silent on. The validator gains a #5 semantic layer over its generic Phase-0 checks.

**Tech Stack:** Python 3.9+ standard library only (`os`, `sys`, `re`, `ast`, `math`, `fnmatch`, `collections`); stdlib `unittest` for tests. Markdown for ontology content.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No third-party deps, no `requirements.txt`. `TestZeroDep` enforces it — keep its allowlist current (this slice adds `fnmatch`).
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail (exit 0).
- **#5 severity doctrine — "machinery follows" (verbatim intent):** ERROR exactly when a field is about to back (or already backs) a running agent; WARN on incomplete thinking about an acted-on activity; silent on untouched worksheets. Operationalized in this plan as: a deep-record file exists ⇒ acted-on; `motion ∈ {automate, build}` ⇒ automation path ⇒ its skill-backing fields are **ERROR** if missing; a non-automation acted-on record with incomplete common core is **WARN**; an activity with no deep-record file is silent.
- **Describability Gate:** all 8 fields must be *answered*; a truthful "none" is valid, `N/A`/blank/`TBD` is not; **no waiver** (#5).
- **Depth doctrine (3–5 acted-on first run) is doctrine, NOT a validator rule** (#5) — do not add a count check.
- **Honesty rule:** no README claim about what groundwork *does* may precede the capability. The interview + generator are Phase 3; the headline must not read as shipped.
- **Gate hygiene decision (locked this session, Option A):** keep `SKIP_RELPATHS={tests, docs/superpowers}`; respect `.gitignore`; document the limitation. #16 "global secrets" is read as "all **content** trees"; Gitleaks is the backstop for the skipped harness trees.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → Sean merges. Fable 5 builds.
- **Commit trailer:** `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

## Prerequisite

Phase 0 (`build/v1-sequence-plan`, green + Codex-reviewed) is merged to `main`. Branch this slice from `main`: `git checkout main && git pull && git checkout -b build/slice-1.2-ontology`.

---

## File Structure

- `scripts/validate.py` — **modify.** Add `.gitignore`-awareness to the walker; add the ontology field vocabularies, the exec-view table parser, and the #5 check functions.
- `tests/test_validate.py` — **modify.** Add gitignore + ontology-check tests (tempdir fixtures — no committed test ontologies).
- `docs/known-limitations.md` — **create.** Durable home for the gate-hygiene Known Limitation (Phase 4 extends it).
- `README.md` — **modify.** One-line headline honesty reframe.
- `ontologies/people-hr/_executive-view.md` — **create.** People/HR executive view.
- `ontologies/people-hr/onboarding-orchestration.md` — **create.** The automate-path deep record (the slice's activity).

> **Design note — the primary-artifact shape (review this carefully).** Tasks 3–6 lock the on-disk shape of the ontology, which every later slice (skills reference activities, cards attach to skills, memory records baselines, governance rules govern them) and the generator (Phase 3) inherit. Changing it after Phase 2/3 is expensive. The shape is: structured fields in **flat frontmatter** on one-activity-per-file deep records (so the #11 frontmatter reader can check them, satisfying #5's "strict where a field backs machinery"); human-readable Direction + presentation in the **exec-view table**; Direction lives canonically in the exec view (not duplicated on the deep record) to avoid a two-home seam. Scrutinize at plan review before Fable executes.

---

## Task 1: Validator gate hygiene — respect `.gitignore` + document the limitation

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`
- Create: `docs/known-limitations.md`

**Interfaces:**
- Consumes: `iter_files(root)`, `validate(root)` from Phase 0.
- Produces: `load_gitignore(root) -> set[str]`; `iter_files(root, ignore=())` now skips gitignored names.

- [ ] **Step 1: Add a failing test** to `tests/test_validate.py`:

```python
import os
import tempfile


class TestGitignore(unittest.TestCase):
    def test_gitignored_file_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, ".gitignore"), "w").write(".env\n*.log\n")
            open(os.path.join(d, ".env"), "w").write("SECRET=AKIAIOSFODNN7EXAMPLE\n")
            open(os.path.join(d, "app.log"), "w").write("AKIAIOSFODNN7EXAMPLE\n")
            open(os.path.join(d, "keep.md"), "w").write("# clean\n")
            findings = validate.validate(d)
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestGitignore -v`
Expected: FAIL — the `.env` and `app.log` AWS-example keys are scanned and ERROR.

- [ ] **Step 3: Implement** — in `scripts/validate.py`, add `import fnmatch` to the imports, then add:

```python
def load_gitignore(root):
    """Minimal .gitignore reader: exact names and simple globs (e.g. '*.log').
    Enough to skip .env-style files so the gate scans (roughly) what's tracked.
    NOT full git ignore semantics (no negation, nesting, or path anchoring) —
    documented in docs/known-limitations.md."""
    patterns = set()
    gi = os.path.join(root, ".gitignore")
    if os.path.isfile(gi):
        with open(gi, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line.rstrip("/"))
    return patterns


def _ignored(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)
```

- [ ] **Step 4: Thread `ignore` through the walker.** Replace `iter_files` with:

```python
def iter_files(root, ignore=()):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")
                       and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS
                       and not _ignored(d, ignore)]
        for fn in filenames:
            if _ignored(fn, ignore):
                continue
            yield os.path.join(dirpath, fn)
```

And in `validate(root)`, change the loop header to load and pass patterns:

```python
    ignore = load_gitignore(root)
    for abspath in iter_files(root, ignore):
```

- [ ] **Step 5: Create `docs/known-limitations.md`:**

```markdown
# Known limitations

Honest limits of the current build. This file grows as the product does (brief §7 — the finished-artifact bar). Overclaiming is trust debt; this is where the claims get their asterisks.

## Validator

- **The gate skips its own harness.** `scripts/validate.py .` does not scan `tests/` or `docs/superpowers/` — the validator's own fixtures and build specs necessarily quote example secret and broken-link patterns. A real secret committed *into those two trees* is therefore not caught by the gate; [Gitleaks](https://github.com/gitleaks/gitleaks) is the documented global backstop (#16). Everywhere else — all product content (`ontologies/`, `skills/`, `governance/`, `demo/`, `your-company/`, root files) — the secret scan runs at full strictness.
- **`.gitignore` matching is minimal.** The walker honors simple `.gitignore` entries (exact names and `*.ext` globs) so gitignored files like `.env` are not scanned. It does not implement full git ignore semantics (negation, nested ignores, path anchoring).
- **The secret floor is high-signal, not exhaustive** (#16): a curated regex set plus an entropy heuristic. Gitleaks is the real guarantee.
```

- [ ] **Step 6: Run the gitignore test + the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (including `TestGitignore` and the still-green `TestZeroDep` — `fnmatch` is stdlib; add it to that test's `allowed` set if the test lists imports explicitly).

- [ ] **Step 7: Confirm the live repo no longer scans `.env`**

Run: `python3 scripts/validate.py . | grep -c '\.env'`
Expected: `0`.

- [ ] **Step 8: Commit**

```bash
git add scripts/validate.py tests/test_validate.py docs/known-limitations.md
git commit -m "fix(validate): respect .gitignore; document gate-skip Known Limitation (#16)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: README headline honesty reframe

**Files:**
- Modify: `README.md`

**Interfaces:** none.

The headline currently reads as a shipped fact ("Point your coding agent at this repo and it interviews… then generates…") though the interview + generator are Phase 3. Reframe to unmistakable design-intent without gutting the pitch.

- [ ] **Step 1: Replace the description paragraph** ([README.md:5]) with:

```markdown
An open-source, harness-agnostic Company OS. **The idea:** you point your coding agent at this repo and it interviews your company about the work each function actually does — what should get **more** human time, what should get **automated away**, and under **what rules** — then generates your operating system from that map: folder-per-function ontologies, skills with named owners, a compiled constitution, and organizational memory that learns under governance instead of rewriting itself. *(In active build — see [Status](#status-building-v1) for what's real today.)*
```

- [ ] **Step 2: Verify the present-tense claim is now framed as intent.**

Run: `grep -nE 'The idea:|In active build' README.md`
Expected: both phrases present on the description line.

- [ ] **Step 3: Verify no broken link introduced** (the anchor points at the Status heading):

Run: `python3 scripts/validate.py README.md 2>/dev/null; python3 scripts/validate.py .`
Expected: exit 0 (the `#status-building-v1` anchor is skipped by the link checker — anchors are not resolved).

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README headline reframed as design-intent (honesty; interview/generator are Phase 3)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Ontology vocabularies + executive-view table parser

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Produces:
  - Constants: `DIRECTIONS`, `MOTIONS`, `AUTOMATION_MOTIONS`, `WORK_TYPES`, `SHAPES`, `SCORE_FIELDS` (list), `SCORE_VALUES`, `GATE_FIELDS` (list).
  - `parse_exec_table(text) -> list[(activity, direction, deep_link_or_None, line_no)]` — parses the first markdown table whose header contains "Direction". `direction` is lowercased; `deep_link` is the link target from the third column or `None`.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestExecTable -v`
Expected: FAIL — no attribute `parse_exec_table`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py` (near the other ontology code):

```python
DIRECTIONS = {"up", "down"}
MOTIONS = {"automate", "build", "buy", "hire", "wait"}
AUTOMATION_MOTIONS = {"automate", "build"}
WORK_TYPES = {"routing", "sensemaking", "accountability"}
SHAPES = {"chat", "single-agent", "agent-team", "dont-bother"}
SCORE_FIELDS = ["score_repetition", "score_risk", "score_judgment",
                "score_company_specificity", "score_market_maturity"]
SCORE_VALUES = {"low", "medium", "high"}
GATE_FIELDS = ["gate_inputs", "gate_output", "gate_standard", "gate_source_of_truth",
               "gate_exception_path", "gate_error_cost", "gate_owner", "gate_review_gate"]


def parse_exec_table(text):
    """Parse the first markdown table whose header row contains 'Direction'.
    Returns [(activity, direction_lower, deep_link_or_None, line_no)]."""
    rows = []
    lines = text.split("\n")
    header_idx = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("|") and "direction" in line.lower():
            header_idx = idx
            break
    if header_idx is None:
        return rows
    for j in range(header_idx + 1, len(lines)):
        line = lines[j]
        if not line.lstrip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue  # the |---|---| separator row
        activity = cells[0] if len(cells) > 0 else ""
        direction = cells[1].lower() if len(cells) > 1 else ""
        link = None
        if len(cells) > 2:
            m = _LINK.search(cells[2])
            if m:
                link = m.group(1)
        rows.append((activity, direction, link, j + 1))
    return rows
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_validate.TestExecTable -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): ontology vocabularies + executive-view table parser (#5)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Deep-record #5 checks (`check_deep_record`)

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `parse_frontmatter`, `Finding`, the Task-3 vocabularies.
- Produces: `check_deep_record(abspath, root) -> list[Finding]`.

**Behavior (the #5 doctrine, made exact):**
- File has no frontmatter → WARN "acted-on activity has no structured fields yet (incomplete thinking)".
- `motion` absent → WARN; present-but-not-in `MOTIONS` → ERROR.
- Common core (`work_type`, `accountable_owner`, the 5 `score_*`): missing → **ERROR if on automation path**, else **WARN**; present-but-invalid-enum → always ERROR.
- Automation path (`motion ∈ {automate, build}`) additionally requires `substrate`, `shape` (∈ `SHAPES`), and all 8 `GATE_FIELDS`: missing/blank → ERROR; a gate field equal to `n/a`/`na`/`tbd` (case-insensitive) → ERROR "must be answered ('none' is valid; 'N/A' is not, no waiver)"; a non-string value → ERROR "must be a single value".

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
gate_source_of_truth: the HRIS record
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

    def test_non_automation_incomplete_is_warn_not_error(self):
        with tempfile.TemporaryDirectory() as d:
            rec = "---\nactivity: Comp review\nmotion: hire\n---\n# x\n"  # missing common core
            p = _write(d, "ontologies/people-hr/x.md", rec)
            findings = validate.check_deep_record(p, d)
            self.assertTrue(any(f.level == "WARN" for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestDeepRecord -v`
Expected: FAIL — no attribute `check_deep_record`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
def check_deep_record(abspath, root):
    """#5 machinery-follows checks for one acted-on activity's deep record."""
    rel = os.path.relpath(abspath, root)
    with open(abspath, encoding="utf-8") as fh:
        text = fh.read()
    data, findings = parse_frontmatter(text, rel)
    findings = list(findings)
    if not data:
        findings.append(Finding("WARN", rel, None,
                                "acted-on activity has no structured fields yet (incomplete thinking)"))
        return findings

    motion = data.get("motion")
    if motion is None:
        findings.append(Finding("WARN", rel, None, "missing 'motion' (incomplete thinking)"))
    elif motion not in MOTIONS:
        findings.append(Finding("ERROR", rel, None,
                                "invalid motion %r (one of %s)" % (motion, sorted(MOTIONS))))
    on_automation = motion in AUTOMATION_MOTIONS

    def require(field, valid=None):
        v = data.get(field)
        missing_level = "ERROR" if on_automation else "WARN"
        if v is None or (isinstance(v, str) and v.strip() == ""):
            findings.append(Finding(missing_level, rel, None, "missing '%s'" % field))
        elif valid is not None and v not in valid:
            findings.append(Finding("ERROR", rel, None,
                                    "invalid '%s' %r (one of %s)" % (field, v, sorted(valid))))

    require("work_type", WORK_TYPES)
    require("accountable_owner")
    for sf in SCORE_FIELDS:
        require(sf, SCORE_VALUES)

    if on_automation:
        require("substrate")
        require("shape", SHAPES)
        for gf in GATE_FIELDS:
            v = data.get(gf)
            if not isinstance(v, str):
                findings.append(Finding("ERROR", rel, None,
                                        "Describability Gate: '%s' must be a single answered value" % gf))
            elif v.strip() == "":
                findings.append(Finding("ERROR", rel, None,
                                        "Describability Gate: '%s' must be answered ('none' is valid; blank is not)" % gf))
            elif v.strip().lower() in {"n/a", "na", "tbd"}:
                findings.append(Finding("ERROR", rel, None,
                                        "Describability Gate: '%s' is %r — must be answered "
                                        "('none' is valid; 'N/A' is not, no waiver)" % (gf, v)))
    return findings
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_validate.TestDeepRecord -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #5 deep-record checks (common core, automation path, Describability Gate)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Function + executive-view #5 checks (`check_ontology`), wired into `validate()`

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `parse_exec_table`, `check_deep_record`, `DIRECTIONS`, `Finding`.
- Produces: `check_ontology(root) -> list[Finding]`, called from `validate(root)`.

**Behavior:**
- For each subdirectory of `ontologies/`: if it has deep-record `.md` files but no `_executive-view.md` → ERROR "function ontology has no executive view".
- Parse the exec view; each row's Direction ∉ `DIRECTIONS` → ERROR.
- Run `check_deep_record` on every `<activity>.md` (not `_executive-view.md`).
- A deep-record file not linked from the exec view → WARN "deep record not listed in the executive view".

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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

    def test_unlisted_deep_record_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "ontologies/people-hr/offboarding.md", AUTOMATE_OK)  # not in exec view
            warns = [f for f in validate.check_ontology(d) if f.level == "WARN"]
            self.assertTrue(any("not listed" in f.message for f in warns))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestOntology -v`
Expected: FAIL — no attribute `check_ontology`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
def check_ontology(root):
    """#5 structural checks over ontologies/<function>/ directories."""
    findings = []
    base = os.path.join(root, "ontologies")
    if not os.path.isdir(base):
        return findings
    for fn in sorted(os.listdir(base)):
        fdir = os.path.join(base, fn)
        if not os.path.isdir(fdir):
            continue
        rel_fdir = os.path.relpath(fdir, root)
        exec_path = os.path.join(fdir, "_executive-view.md")
        deep_files = sorted(f for f in os.listdir(fdir)
                            if f.endswith(".md") and f != "_executive-view.md")
        linked = set()
        if not os.path.isfile(exec_path):
            if deep_files:
                findings.append(Finding("ERROR", os.path.join(rel_fdir, "_executive-view.md"),
                                        None, "function ontology has no executive view (_executive-view.md)"))
        else:
            with open(exec_path, encoding="utf-8") as fh:
                rows = parse_exec_table(fh.read())
            rel_exec = os.path.relpath(exec_path, root)
            for activity, direction, link, ln in rows:
                if direction not in DIRECTIONS:
                    findings.append(Finding("ERROR", rel_exec, ln,
                                            "Direction must be 'up' or 'down', got %r" % direction))
                if link:
                    linked.add(os.path.basename(link))
        for df in deep_files:
            findings += check_deep_record(os.path.join(fdir, df), root)
            if df not in linked:
                findings.append(Finding("WARN", os.path.join(rel_fdir, df), None,
                                        "deep record not listed in the executive view"))
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, before `return findings`, add:

```python
    findings += check_ontology(root)
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (all classes).

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #5 ontology checks (exec view required, Direction valid, orphan warn) + wire in

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Author the People/HR ontology content (the vertical proof)

**Files:**
- Create: `ontologies/people-hr/_executive-view.md`
- Create: `ontologies/people-hr/onboarding-orchestration.md`

**Interfaces:** the content must pass `check_ontology` (Task 5) with zero ERRORs — this is the slice closing its loop.

- [ ] **Step 1: Create `ontologies/people-hr/_executive-view.md`:**

```markdown
# People/HR — executive view

Every activity this function does, with its Direction — **up** (deserves more human
time) or **down** (should stop being hand-run). Deep records exist only for the
activities the company has chosen to act on first (they link below); the rest are
listed but not yet worked (depth is earned by acting, not by planning to act).

| Activity | Direction | Deep record |
|---|---|---|
| Onboarding orchestration | down | [deep record](onboarding-orchestration.md) |
| Performance-review prep | up | — |
| Headcount & workforce planning | up | — |
| Recruiting & candidate screening | down | — |
| Benefits & leave administration | down | — |
| Compensation review | up | — |
| Employee-relations casework | up | — |
| Compliance & policy tracking | down | — |
| Learning & development | up | — |
| Offboarding | down | — |
```

- [ ] **Step 2: Create `ontologies/people-hr/onboarding-orchestration.md`:**

```markdown
---
activity: Onboarding orchestration
function: People/HR
motion: automate
score_repetition: high
score_risk: low
score_judgment: low
score_company_specificity: medium
score_market_maturity: high
work_type: routing
accountable_owner: Head of People
substrate: HRIS + IT provisioning tracker + the onboarding checklist doc
shape: single-agent
gate_inputs: The new hire's start date, role, manager, equipment needs, and required system accesses, from the signed offer and the IT intake form
gate_output: A completed onboarding checklist — accounts provisioned, equipment ordered, the day-one schedule sent, manager and buddy notified
gate_standard: Every new hire has working accounts, equipment en route, and a scheduled first week before their start date
gate_source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
gate_exception_path: A non-standard role or missing intake data pauses to the Head of People; contractor-to-employee conversions route to Legal first
gate_error_cost: A missed access or late laptop delays a hire's first day — recoverable within a day, embarrassing, not dangerous
gate_owner: Head of People
gate_review_gate: The hiring manager confirms the checklist is complete on day one
---
# Onboarding orchestration

**Direction: down.** The manual coordination of accounts, equipment, and day-one
logistics should stop being hand-run — it is high-repetition, low-judgment routing
work with a clear source of truth, which is exactly what should be automated so the
People team's time goes to the human parts of joining a company.

**Motion: automate.** Repetition is high, risk and judgment are low, the workflow is
only moderately company-specific, and the market for onboarding automation is mature.

## Accountability

Which business process runs differently: the pre-start onboarding runbook stops being
a person hand-working a checklist and becomes an agent that provisions, orders, and
schedules against the HRIS record, pausing to a human on any exception.

Who is accountable for proving it improved: the **Head of People**, measured against a
baseline of time-to-day-one-ready and day-one readiness captured **before** provisioning
(the captured baseline is a governed org-memory record — Slice 1.4 — and no skill
provisions for this activity without one).
```

- [ ] **Step 3: Validate the real content**

Run: `python3 scripts/validate.py .`
Expected: exit 0, zero ERRORs. (Warnings for benign high-entropy strings elsewhere are fine; there must be **no** ERROR and no `not listed` / `Direction` / `Describability Gate` WARN/ERROR against the new files.)

- [ ] **Step 4: Confirm the slice proves the schema end-to-end**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0. The ontology schema now exists as files, is instantiated for one real automate-path activity, and is checked at #5 strictness — the walking skeleton's second vertebra.

- [ ] **Step 5: Commit**

```bash
git add ontologies/people-hr/
git commit -m "feat(ontology): People/HR executive view + onboarding-orchestration deep record (#5 slice)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next plans)

- **Slice 1.3 (skills):** work-package spec + Owner's Card template + the worked onboarding skill + action taxonomy + the fixed Claude-Code hook set (#8) + #6 checks. The onboarding-orchestration record authored here is the activity that slice generates a skill *for*.
- **Slice 1.4 (memory):** the captured-baseline org-memory record this ontology's Accountability section references (#7).
- **Slice 1.5 (governance):** constitution rule + version pin (#21) + proposal schema (#17) + consent-gate tripwire (#18) + demo canon (#16).
- **Not added (by #5 doctrine):** any depth-count check (3–5 acted-on is doctrine, not a rule); Substrate/Shape/Gate requirements on non-automation activities.

## Self-Review

- **Spec coverage:** gate-hygiene decision (Option A) → Task 1; README honesty flag → Task 2; #5 two-tier schema-as-files → Tasks 3–6; executive view (name + Direction) → Tasks 3/5/6; common core + automation path + Describability-Gate-no-waiver → Task 4; machinery-follows ERROR/WARN/silent split → Task 4 severity logic + Task 5 orphan WARN; depth doctrine deliberately un-checked → Scope note. Covered.
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; every code step shows complete code; content tasks provide full file bodies; verification commands have expected output.
- **Type consistency:** `Finding(level, path, line, message)` used identically; `check_deep_record(abspath, root)` and `check_ontology(root)` signatures match their call sites and Interfaces; `parse_exec_table` return shape `(activity, direction, link, line_no)` consumed consistently in Tasks 3 and 5; `SCORE_FIELDS`/`GATE_FIELDS` are lists, `DIRECTIONS`/`MOTIONS`/`WORK_TYPES`/`SHAPES`/`SCORE_VALUES` are sets, used accordingly.
- **Frontmatter-reader compatibility:** all deep-record fields are flat `key: value` scalars (no nesting), within the #11 reader's grammar; the 5 scores and 8 gate parts are separate flat keys precisely because the reader has no nested-object support. Consistent.
