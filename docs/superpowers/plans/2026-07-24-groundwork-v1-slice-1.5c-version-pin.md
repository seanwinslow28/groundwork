# groundwork V1 — Slice 1.5c: Version pin + skew gate (#21) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the #21 version-skew *contract* the generator will depend on — the `SCHEMA_VERSION` engine constant, the company-root pin file, the `MIGRATIONS.md` guarantee, and the skew-gate check (skew 0 = safe; skew ≥ 1 = one migration error; reverse-skew = warn). Plus the deferred stateless-walker symlinked-directory hardening.

**Architecture:** The engine carries a single integer `SCHEMA_VERSION` (V1 = `1`), bumped **only** on a breaking schema change. Each generated company root carries a `groundwork.pin` (frontmatter: `schema_version` + `generated_by_commit`), independent of `interview/`. `check_version_pin` finds every pin, computes `skew = SCHEMA_VERSION − pin.schema_version`, and applies the pull promise: pull never ERRORs content for being old, breaks are one clean migration gate. **Scoping note (maintainer decision, 2026-07-24):** the invasive per-check `since:` retrofit is **deferred** — at `SCHEMA_VERSION=1` it can never demote anything (all checks are `since: 1`, all content pins at `1`). This slice ships the contract + gate logic; `since:` tagging waits for the first real v2. The pin is company-instance metadata, so its real-content proof lands with `demo/` (Phase 2.3); here it is proven by fixtures.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports this slice. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **The pull promise (#21, verbatim spine):** `git pull` never invents a new requirement that ERRORs old content. `skew == 0` → pull is always safe (each check's declared severity stands). `skew ≥ 1` → **one** clean migration-boundary ERROR, not a scatter. Reverse-skew (engine older than the pin) → WARN "pull the engine," and validity is not asserted.
- **Skew is a coarse integer**, measured in breaking `SCHEMA_VERSION` versions — never commits or days. `generated_by_commit` is provenance only and is **never** used for skew math.
- **Migration contract (#21):** every breaking bump ships a `MIGRATIONS.md` note + the validator points precisely; a transform script is a bonus; full re-interview is V3.
- **Deferred (maintainer decision):** per-check `since:` tags + the new-requirement demotion + scatter-suppression at skew ≥ 1. Documented as the forward convention in `MIGRATIONS.md`; not built now.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.5b merged to `main` (done: `035fa59`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.5c-version-pin`.

---

## File Structure

- `scripts/validate.py` — **modify.** Add `SCHEMA_VERSION`; add `check_version_pin(root)` and `check_symlinked_dirs(root)`; wire both into `validate()`.
- `tests/test_validate.py` — **modify.** Skew-gate tests + symlink-hardening tests (tempdir fixtures).
- `MIGRATIONS.md` — **create** (repo root). The migration contract + the pin-file format + the deferred-`since:` note.

> **Design notes.**
> 1. **No real pin in this engine repo.** The engine's root `ontologies/`, `skills/`, `governance/`, `memory/` are *engine templates/exemplars*, not a generated company — they carry no pin. `check_version_pin` is therefore silent on this repo (like `check_memory` with no `memory/`) and activates on `demo/` (Phase 2.3) and `your-company/` (the generator). It is proven here by fixtures. This is honest, not inert: the gate logic is exercised, and the pin format now exists for the generator to emit.
> 2. **Scatter-suppression at skew ≥ 1 is not built.** #21 wants "one migration gate instead of a scatter of field errors." At `SCHEMA_VERSION=1` a valid pin can never produce skew ≥ 1 (that needs `pin < 1`), so suppression is moot until a real v2. Building it now would be dormant control-flow surgery. Deferred with the `since:` work; documented.
> 3. **Symlinked-directory hardening (Task 2) is folded-in, unrelated to #21.** It closes the gap Fable flagged after 1.4b: the stateless walker silently skips symlinked directories. The fix makes the skip *loud* (a WARN), so a symlinked `memory/` can't hide records unnoticed.

---

## Task 1: `SCHEMA_VERSION` + the pin + the skew gate + `MIGRATIONS.md`

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`
- Create: `MIGRATIONS.md`

**Interfaces:**
- Produces: `SCHEMA_VERSION = 1`; `check_version_pin(root) -> list[Finding]`, wired into `validate(root)`.
- Pin file: `groundwork.pin` at a company root — frontmatter `schema_version: <int>` (required) + `generated_by_commit: <sha>` (provenance; WARN if missing).

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
PIN_OK = """---
schema_version: 1
generated_by_commit: 0123456789abcdef0123456789abcdef01234567
---
"""


class TestVersionPin(unittest.TestCase):
    def test_current_pin_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK)
            self.assertEqual([f for f in validate.check_version_pin(d) if f.level == "ERROR"], [])

    def test_skew_forward_is_migration_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "your-company/groundwork.pin", PIN_OK.replace("schema_version: 1", "schema_version: 0"))
            errs = [f for f in validate.check_version_pin(d) if f.level == "ERROR"]
            self.assertTrue(any("MIGRATIONS" in f.message for f in errs))

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
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestVersionPin -v`
Expected: FAIL — no attribute `check_version_pin`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
SCHEMA_VERSION = 1  # bumped ONLY on a breaking schema change (#21). Never on additive commits.


def check_version_pin(root):
    """#21 skew gate. A company root carries groundwork.pin; skew = engine - pinned.
    Pull never ERRORs content for being old; a breaking gap is one migration ERROR."""
    findings = []
    for abspath in iter_files(root, load_gitignore(root)):
        if os.path.basename(abspath) != "groundwork.pin":
            continue
        rel = os.path.relpath(abspath, root)
        with open(abspath, encoding="utf-8") as fh:
            data, fm = parse_frontmatter(fh.read(), rel)
        findings += fm

        sv = data.get("schema_version")
        if _blank(sv):
            findings.append(Finding("ERROR", rel, None, "version pin missing 'schema_version'"))
            continue
        if not isinstance(sv, str):
            findings.append(Finding("ERROR", rel, None,
                                    "version pin 'schema_version' must be a single integer"))
            continue
        try:
            pinned = int(sv.strip())
        except ValueError:
            findings.append(Finding("ERROR", rel, None,
                                    "version pin 'schema_version' is not an integer: %r" % sv))
            continue

        if _blank(data.get("generated_by_commit")):
            findings.append(Finding("WARN", rel, None,
                                    "version pin missing 'generated_by_commit' (provenance)"))

        skew = SCHEMA_VERSION - pinned
        if skew >= 1:
            findings.append(Finding("ERROR", rel, None,
                                    "content is schema v%d, engine is v%d — see MIGRATIONS.md for v%d->v%d"
                                    % (pinned, SCHEMA_VERSION, pinned, SCHEMA_VERSION)))
        elif skew < 0:
            findings.append(Finding("WARN", rel, None,
                                    "engine is schema v%d but this content is pinned at v%d — pull the engine; "
                                    "validity is not asserted against a newer schema" % (SCHEMA_VERSION, pinned)))
        # skew == 0: content is current; each check's own severity stands (silent here)
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_hooks(root)`, add:

```python
    findings += check_version_pin(root)
```

- [ ] **Step 5: Create `MIGRATIONS.md`** (repo root):

```markdown
# Migrations

groundwork's content schema is versioned by a single integer, **`SCHEMA_VERSION`**,
bumped **only on a breaking change** — a change to the shape a running agent actually
needs. Additive commits do not bump it.

Each generated company repo records the schema version it was built against in a
`groundwork.pin` file at its root. When you pull a newer engine and `validate` reports
a **migration gate** — *"content is schema vN, engine is vM; see MIGRATIONS.md for
vN→vM"* — find the note below.

## The pull promise

- **Same schema version** (engine merely has more commits): pull is always safe. You
  can pull indefinitely; mere age never makes pull dangerous.
- **A breaking bump landed**: one clean migration-boundary error, never a scatter of
  field errors. Max skew is **one** breaking version.
- **Engine older than the pin** (you forgot to pull, or newer content arrived from
  elsewhere): a warning to pull the engine — validity is not asserted against a schema
  the engine doesn't yet know.

## The migration contract

Every breaking bump ships, here, a note: **what changed, what to change, why.** The
validator points precisely at each offending file and field. Where a change is
mechanical, a transform script *may* ship — a bonus, never the thing the promise rests
on. Full re-interview is a V3 capability, not a migration step.

## The pin file (`groundwork.pin`)

```
---
schema_version: <int>          # what skew compares (integer to integer)
generated_by_commit: <sha>     # provenance only — never used for skew math
---
```

It lives at the company-repo root, independent of `interview/`.

## Deferred: per-check `since:` demotion

At `SCHEMA_VERSION = 1` there is no older schema to be lenient toward, so the
per-check `since:` mechanism (demoting a genuinely-new requirement to a "new since
your pin" warning) is **not yet wired**. When the first breaking bump to v2 is authored,
each new check declares the `since:` version it was introduced at, and a new-requirement
check demotes to WARN for content pinned before it. Until then this is documented intent,
not code.

## Current schema version: 1

Schema **v1** is the first released schema. There are no migrations yet.
```

- [ ] **Step 6: Run tests + validate**

Run: `python3 -m unittest tests.test_validate.TestVersionPin -v && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0 (this engine repo has no `groundwork.pin`, so `check_version_pin` is silent; `MIGRATIONS.md` introduces no ERRORs).

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py MIGRATIONS.md
git commit -m "feat(validate): #21 version pin + skew gate (SCHEMA_VERSION=1) + MIGRATIONS.md contract

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Stateless-walker symlinked-directory hardening (folded-in, from the 1.4b deferral)

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Produces: `check_symlinked_dirs(root) -> list[Finding]`, wired into `validate(root)`. A symlinked directory in the scanned content tree (not a dot-dir, `SKIP_DIRS`, `SKIP_RELPATHS`, or gitignored) → WARN, so the skip is loud rather than silent.

> Why WARN and here: the stateless walker (`os.walk`, `followlinks=False`) silently skips symlinked directories, so a symlinked `memory/` could hide records from the stateless checks. The `--diff` layer (base-file-driven) already catches memory records regardless; this makes the *stateless* skip visible everywhere else. A legitimate symlink is not an error — but a silent unchecked subtree is exactly the quiet gap the project keeps closing.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestSymlinkedDirs -v`
Expected: FAIL — no attribute `check_symlinked_dirs`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
def check_symlinked_dirs(root):
    """Make the stateless walker's skip of symlinked directories LOUD. os.walk does
    not descend into symlinked dirs, so their contents would go unchecked silently."""
    findings = []
    ignore = load_gitignore(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        kept = []
        for d in dirnames:
            rel = os.path.normpath(os.path.join(rel_dir, d))
            if d in SKIP_DIRS or d.startswith(".") or rel in SKIP_RELPATHS or _ignored(d, ignore):
                continue  # legitimately not scanned
            if os.path.islink(os.path.join(dirpath, d)):
                findings.append(Finding("WARN", rel, None,
                                        "symlinked directory is not traversed by the stateless validator; "
                                        "its contents are unchecked (the --diff layer backstops memory records)"))
            else:
                kept.append(d)
        dirnames[:] = kept  # do not descend into skipped or symlinked dirs
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_version_pin(root)`, add:

```python
    findings += check_symlinked_dirs(root)
```

- [ ] **Step 5: Run the full suite + the real gate**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

Run: `python3 scripts/validate.py .`
Expected: exit 0 — the engine repo has no symlinked content directories (the only symlink convention, `.claude/skills/<name>` per #19, lives under the skipped `.claude/` dot-dir and does not yet exist).

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): make the stateless walker's symlinked-dir skip loud (1.4b deferral)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next sub-slices)

- **Slice 1.5d:** proposal schema (#17) + consent gate (#18) + the blast-radius match tripwire (reuses 1.4b `--diff`) + the governance changelog. This closes governed self-improvement — and is the last Phase-1 governance piece.
- **Phase 2.3:** demo canon (#16) + synthetic-identifier check; the meeting-challenger runnable exemplar (#8 item 3); and the **real pin file** for the demo company (this slice's `check_version_pin` activates on it).
- **Deferred with a documented home (`MIGRATIONS.md`):** per-check `since:` tags + new-requirement demotion + skew-≥1 scatter-suppression — all wired at the first real v2 breaking bump.
- **Move 2 (Phase 1→2 boundary):** author `AGENTS.md` + collapse `CLAUDE.md`; the AGENTS.md-chain context-budget check (#13).

## Self-Review

- **Ticket coverage (#21):** `SCHEMA_VERSION` engine constant → Task 1; pin file (`schema_version` + `generated_by_commit`, root-level, independent of `interview/`) → Task 1 + `MIGRATIONS.md`; skew integer math (never commits/days) → `check_version_pin`; pull promise (skew 0 safe, skew ≥ 1 one migration gate, reverse WARN) → `check_version_pin`; migration contract (doc-guaranteed) → `MIGRATIONS.md`; per-check `since:` **explicitly deferred** per the maintainer decision, documented in `MIGRATIONS.md`. Folded-in 1.4b symlink deferral → Task 2.
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; complete code and content; verification commands have expected output.
- **Type consistency:** `Finding`, `_blank`, `parse_frontmatter`, `iter_files`, `load_gitignore`, `_ignored`, `SKIP_DIRS`, `SKIP_RELPATHS` reused with existing signatures; `SCHEMA_VERSION` is an int; `check_version_pin(root)` and `check_symlinked_dirs(root)` match their call sites in `validate()`.
- **Non-inert honesty:** `check_version_pin` is silent on this repo (no pin — the engine is not a generated company) but is exercised by fixtures and activates on real content at `demo/` (Phase 2.3); the pin format now exists for the generator (Phase 3) to emit. Stated in Design note 1.
- **Zero-dep:** no new imports; `int()` is a builtin; `TestZeroDep` unchanged and green.
```

