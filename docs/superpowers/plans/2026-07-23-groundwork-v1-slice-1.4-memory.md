# groundwork V1 — Slice 1.4: Org-memory schema + #7 checks + provisioning gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the org-memory layer of the vertical slice — the #7 typed-record schema (six field groups, provenance/supersession invariants), the worked pre-provisioning onboarding baseline record + its index, the #7 validator checks, and the #5 provisioning-gate check (no skill provisions without a captured baseline) — then flip the onboarding skill to `provisioned: yes`, closing the loop on real content.

**Architecture:** An org-memory record is one `.md` file under a `memory/` directory, carrying flat-frontmatter provenance/governance fields (#7); the body + `valid_at` are the frozen fact, other fields are mutable as governance acts. Records are never edited — a fact is *superseded* by a new record (bi-temporal). A per-`memory/` `_index.md` lists **live records only**. The validator gains a stateless #7 shape layer (record-level, nothing silent) plus the #5 provisioning-gate check that ties a provisioned skill to its baseline record. This is the fourth vertebra of the walking skeleton, built for the same onboarding activity.

**Tech Stack:** Python 3.9+ standard library only (`datetime` already imported in Slice 1.3); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **#7 field inventory — six groups, no more:** `provenance` (`observed`/`inferred`/`confirmed`/`superseded`), `owner`, `valid_at`/`invalid_at`, `review_by`, `superseded_by`, `source`.
- **#7 severity (verbatim):**
  - **ERROR:** `provenance` missing or not one of the four enum values; `valid_at` missing or unparseable; `owner` missing; broken supersession invariants (`superseded` without `superseded_by`/`invalid_at`; supersession fields on a live record; dangling `superseded_by` pointer); a `confirmed` record with no `source`.
  - **WARN:** missing `source` on `observed`/`inferred`; missing or overdue `review_by`.
  - **Nothing is silent at record level** — a record exists only because someone wrote it; there is no "untouched worksheet" state (contrast #5/#6).
- **#7 mutability:** frozen = body + `valid_at`; supersession fields (`invalid_at`, `superseded_by`) are **forbidden on live records**, set once at supersession. (Enforcement of *edits* is the `--diff` mode — Slice 1.4b, not here.)
- **#7 identity/index:** one record per file; `superseded_by` is a repo-relative file path; the index lists **live records only** (live record not in index → WARN; superseded record not in index → silent; index entry → missing file → ERROR, already covered by the referential-integrity check).
- **#5 provisioning gate:** no skill provisions for an activity without a captured baseline. Encoded as a `baseline:` field on a provisioned `SKILL.md` that must resolve to an existing memory record.
- **Honesty rule:** no capability claim precedes the capability. The onboarding skill's compatibility notes must NOT claim hook enforcement (the hook set is Slice 1.5).
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.3 merged to `main` (done: `d43a3c1`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.4-memory`.

---

## File Structure

- `memory/README.md` — **create.** The org-memory schema convention (human doc).
- `scripts/validate.py` — **modify.** Add `PROVENANCE`, `check_memory(root)`, and the provisioning-gate check (extend `check_owner_cards`); wire `check_memory` into `validate()`.
- `tests/test_validate.py` — **modify.** Memory shape + index + provisioning-gate tests (tempdir fixtures).
- `memory/onboarding-baseline.md` — **create.** The worked pre-provisioning baseline record.
- `memory/_index.md` — **create.** The live-records index.
- `skills/onboarding-orchestration/SKILL.md` — **modify.** Flip `provisioned: no` → `yes`; add `baseline:` (the flagged decision).

> **Design notes — load-bearing craft calls (review carefully).**
> 1. **Memory location:** org-memory is company-instance data; in a real adoption it lives in the company repo. For the engine's walking-slice exemplar it sits at root `memory/`, consistent with the root `ontologies/` and `skills/` exemplars. The validator discovers records under **any** `memory/` directory, so `demo/**/memory/` and `your-company/memory/` are picked up later with no change.
> 2. **The provisioning gate is encoded on the skill:** a `provisioned: yes` `SKILL.md` must carry a `baseline:` path resolving to a memory record (the skill is what provisions; requiring it to cite its baseline enforces #5). An alternative was to put `baseline:` on the ontology deep record — rejected to keep this slice off the 1.2 schema.
> 3. **The `provisioned: no` → `yes` flip** (Task 5) reverses the maintainer-accepted 1.3 deviation, now that its stated reason (no baseline) is resolved. It is an isolated final sub-step; drop it to keep `no` (the provisioning gate is then exercised by tests only, not real content).

---

## Task 1: The org-memory schema convention doc + `PROVENANCE`

**Files:**
- Create: `memory/README.md`
- Modify: `scripts/validate.py` (add the `PROVENANCE` constant only)

**Interfaces:**
- Produces: `PROVENANCE = {"observed", "inferred", "confirmed", "superseded"}`.

- [ ] **Step 1: Create `memory/README.md`:**

```markdown
# Org memory

What this organization remembers, with what provenance, owned by whom, and how an
observation becomes policy. Files + validator checks — no engine (session recall and
retrieval belong to the harness). One record per file under a `memory/` folder; the
index lists live records only.

## Record schema (six field groups, no more)

| Field | Meaning | Required |
|---|---|---|
| `provenance` | `observed` / `inferred` / `confirmed` / `superseded` | always |
| `owner` | who is accountable for this record | always |
| `valid_at` | ISO date the fact became true (frozen) | always |
| `invalid_at` | ISO date the fact stopped being true | iff superseded |
| `review_by` | ISO date the record should be re-checked | soft (WARN) |
| `superseded_by` | repo-relative path to the record that replaces this one | iff superseded |
| `source` | the evidence behind the record | always (ERROR only for `confirmed`) |

## Rules

- **Never edited — superseded.** A fact that stops being true is not deleted or
  rewritten; a new record supersedes it, and the old one gets `invalid_at` +
  `superseded_by`. Doubt without a replacement fact = supersession by a record whose
  body states the retraction. (Bi-temporal, Zep's pattern.)
- **Frozen at commit:** the body and `valid_at`. **Mutable as governance acts:** `owner`
  (reassignable), `review_by` (bumpable), `source` (append-only), the provenance label
  (**forward only**: `observed`/`inferred` → `confirmed`; → `superseded` only via the
  supersession rules; no downgrades).
- **Supersession fields are forbidden on live records** — `invalid_at`/`superseded_by`
  appear only on a superseded record.
- **The index lists live records only.** Superseded records live in history, reachable
  via `superseded_by` chains (and that is how the index stays inside the load budget).
- **Promotion path** (observation → working note → decision) is carried by folder
  placement, not a frontmatter field.
```

- [ ] **Step 2: Add the constant** — in `scripts/validate.py`, near the other vocabularies:

```python
PROVENANCE = {"observed", "inferred", "confirmed", "superseded"}
```

- [ ] **Step 3: Verify the doc validates**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 scripts/validate.py memory`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add memory/README.md scripts/validate.py
git commit -m "docs: org-memory schema convention (#7) + PROVENANCE constant

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: `check_memory` — record-level #7 shape checks

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Produces:
  - `_memory_record_files(root) -> list[str]` — absolute paths of `.md` files under any `memory/` directory, excluding `_index.md` and `README.md`.
  - `check_memory(root) -> list[Finding]` — for this task, the per-record shape checks (index cross-check added in Task 3).

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
            findings = validate.check_memory(d) if False else None
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
            rec = (MEM_OK.replace("provenance: observed", "provenance: superseded")
                   + "")  # add supersession fields
            rec = rec.replace("review_by: 2099-10-15",
                              "review_by: 2099-10-15\ninvalid_at: 2026-08-01\nsuperseded_by: memory/nope.md")
            _write(d, "memory/x.md", rec)
            self.assertTrue(any(f.level == "ERROR" and "dangling" in f.message.lower()
                                for f in validate.check_memory(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestMemory -v`
Expected: FAIL — no attribute `check_memory`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
def _memory_record_files(root):
    out = []
    for abspath in iter_files(root, load_gitignore(root)):
        rel = os.path.relpath(abspath, root).replace("\\", "/")
        parts = rel.split("/")
        if "memory" in parts and abspath.endswith(".md") \
                and os.path.basename(abspath) not in {"_index.md", "README.md"}:
            out.append(abspath)
    return out


def check_memory(root):
    """#7 record-level shape checks. Nothing is silent at record level."""
    findings = []
    for abspath in _memory_record_files(root):
        rel = os.path.relpath(abspath, root)
        with open(abspath, encoding="utf-8") as fh:
            data, fm = parse_frontmatter(fh.read(), rel)
        findings += fm

        prov = data.get("provenance")
        if _blank(prov):
            findings.append(Finding("ERROR", rel, None, "missing 'provenance'"))
        elif not (isinstance(prov, str) and prov in PROVENANCE):
            findings.append(Finding("ERROR", rel, None,
                                    "invalid 'provenance' %r (one of %s)" % (prov, sorted(PROVENANCE))))

        if _blank(data.get("owner")):
            findings.append(Finding("ERROR", rel, None, "missing 'owner' (an unowned memory is ungoverned drift)"))

        if _blank(data.get("valid_at")) or _parse_date(data.get("valid_at")) is None:
            findings.append(Finding("ERROR", rel, None, "missing or unparseable 'valid_at' (ISO date)"))

        source_blank = _blank(data.get("source"))
        if source_blank and prov == "confirmed":
            findings.append(Finding("ERROR", rel, None, "'confirmed' record has no 'source' (confirmation must cite evidence)"))
        elif source_blank:
            findings.append(Finding("WARN", rel, None, "missing 'source' (push toward evidence)"))

        if _blank(data.get("review_by")):
            findings.append(Finding("WARN", rel, None, "missing 'review_by' (staleness)"))
        else:
            rb = _parse_date(data.get("review_by"))
            if rb is not None and rb < datetime.date.today():
                findings.append(Finding("WARN", rel, None, "'review_by' has passed (staleness)"))

        # supersession invariants
        is_sup = prov == "superseded"
        has_sb = not _blank(data.get("superseded_by"))
        has_ia = not _blank(data.get("invalid_at"))
        if is_sup and not (has_sb and has_ia):
            findings.append(Finding("ERROR", rel, None,
                                    "superseded record must carry both 'superseded_by' and 'invalid_at'"))
        if not is_sup and (has_sb or has_ia):
            findings.append(Finding("ERROR", rel, None,
                                    "supersession fields (invalid_at/superseded_by) are forbidden on a live record"))
        if has_ia and _parse_date(data.get("invalid_at")) is None:
            findings.append(Finding("ERROR", rel, None, "unparseable 'invalid_at' (ISO date)"))
        if has_sb:
            target = data.get("superseded_by")
            if isinstance(target, str) and not os.path.isfile(os.path.join(root, target.strip())):
                findings.append(Finding("ERROR", rel, None, "dangling 'superseded_by' pointer: %s" % target))
    return findings
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_validate.TestMemory -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #7 org-memory record shape checks (provenance, supersession invariants)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: Memory index cross-check + wire into `validate()`

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Extends `check_memory`: a live record not linked from its `memory/_index.md` → WARN (superseded records are silent). Index-entry-to-missing-file is already an ERROR via the referential-integrity check.
- `validate(root)` now calls `check_memory(root)`.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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

    def test_validate_wires_memory(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "memory/x.md", MEM_OK.replace("provenance: observed", "provenance: guessed"))
            self.assertTrue(any(f.level == "ERROR" and "provenance" in f.message
                                for f in validate.validate(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestMemoryIndex -v`
Expected: FAIL — index cross-check not present; `validate` does not call `check_memory`.

- [ ] **Step 3: Implement the index cross-check** — at the END of `check_memory(root)`, before `return findings`, add:

```python
    # index cross-check: live records must appear in their memory/_index.md
    for abspath in iter_files(root, load_gitignore(root)):
        if os.path.basename(abspath) != "_index.md":
            continue
        rel = os.path.relpath(abspath, root).replace("\\", "/")
        if "memory" not in rel.split("/"):
            continue
        mem_dir = os.path.dirname(abspath)
        with open(abspath, encoding="utf-8") as fh:
            index_text = fh.read()
        linked = {os.path.normpath(os.path.join(mem_dir, t.split("#", 1)[0]))
                  for t in _LINK.findall(index_text)
                  if not t.startswith(("http://", "https://", "mailto:", "#"))}
        for rec in _memory_record_files(root):
            if os.path.dirname(rec) != mem_dir and not rec.startswith(mem_dir + os.sep):
                continue
            with open(rec, encoding="utf-8") as fh:
                data, _ = parse_frontmatter(fh.read(), rec)
            if data.get("provenance") == "superseded":
                continue  # history, silent
            if os.path.normpath(rec) not in linked:
                findings.append(Finding("WARN", os.path.relpath(rec, root), None,
                                        "live record not in the index (dark, not lying)"))
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_owner_cards(root)`, add:

```python
    findings += check_memory(root)
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #7 memory index cross-check (live-not-in-index WARN) + wire in

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The #5 provisioning-gate check (baseline gates provisioning)

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Extends `check_owner_cards`: a `provisioned: yes` skill must carry a `baseline:` field resolving to an existing file; else ERROR.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestProvisioningGate -v`
Expected: FAIL — no baseline check yet.

- [ ] **Step 3: Implement** — in `check_owner_cards`, inside the `for name` loop, right after `provisioned = ...` is computed, add:

```python
        if provisioned:
            baseline = skill_fm.get("baseline")
            if _blank(baseline):
                findings.append(Finding("ERROR", rel_skill, None,
                                        "provisioned skill must cite a captured 'baseline' (#5 provisioning gate)"))
            elif isinstance(baseline, str) and not os.path.isfile(os.path.join(root, baseline.strip())):
                findings.append(Finding("ERROR", rel_skill, None,
                                        "baseline record not found: %s" % baseline.strip()))
```

- [ ] **Step 4: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #5 provisioning gate — a provisioned skill must cite its baseline

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: Author the baseline record + index; flip onboarding to provisioned (the vertical proof)

**Files:**
- Create: `memory/onboarding-baseline.md`
- Create: `memory/_index.md`
- Modify: `skills/onboarding-orchestration/SKILL.md`

**Interfaces:** the whole repo must pass `python3 scripts/validate.py .` with zero ERRORs — the loop closing: ontology → skill (now provisioned) → card → baseline memory record, consistent and gated.

- [ ] **Step 1: Create `memory/onboarding-baseline.md`:**

```markdown
---
provenance: observed
owner: Head of People
valid_at: 2026-07-15
review_by: 2026-10-15
source: The People team's Q2 2026 onboarding tracker (12 hires, Apr–Jun 2026)
---
# Onboarding baseline (pre-provisioning)

Captured before the onboarding-orchestration skill was provisioned, so its
improvement can be proven rather than assumed (#5 provisioning gate).

- Median time-to-day-one-ready: **4 business days** after offer signature.
- Day-one readiness (accounts + equipment + schedule all present on the first
  morning): **7 of 12** hires.
- Most common gap: system access not granted before the first morning.
```

- [ ] **Step 2: Create `memory/_index.md`:**

```markdown
# Org memory — index

Live records only. Superseded records live in history, reachable via `superseded_by`
chains (that is how this index stays inside the load budget).

- [Onboarding baseline (pre-provisioning)](onboarding-baseline.md) — Head of People — observed
```

- [ ] **Step 3: Flip the onboarding skill to provisioned + cite the baseline.** In `skills/onboarding-orchestration/SKILL.md` frontmatter, change `provisioned: no` to `provisioned: yes` and add a `baseline:` line, so the frontmatter reads:

```markdown
---
name: onboarding-orchestration
description: Provision a new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
baseline: memory/onboarding-baseline.md
ontology: ontologies/people-hr/onboarding-orchestration.md
---
```

Do **not** touch the compatibility notes — they must remain honest that hook
enforcement is not yet present (the hook set is Slice 1.5). If the current notes were
rewritten in Slice 1.3 to avoid a hook-enforcement claim, keep them as-is.

- [ ] **Step 4: Validate the whole repo**

Run: `python3 scripts/validate.py .`
Expected: exit 0, zero ERRORs. Specifically: the now-provisioned skill passes the #6 card strictness path (its card is complete from Slice 1.3) and the #5 provisioning gate (baseline resolves); the baseline record passes #7; it is listed in the index.

- [ ] **Step 5: Confirm the loop is closed**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0. The onboarding activity now runs, on real content, ontology → provisioned work-package skill → Owner's Card → captured baseline, checked end-to-end at #5/#6/#7 strictness.

- [ ] **Step 6: Commit**

```bash
git add memory/onboarding-baseline.md memory/_index.md skills/onboarding-orchestration/SKILL.md
git commit -m "feat(memory): onboarding baseline + index; provision the onboarding skill (#5/#7 loop closed)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next plans)

- **Slice 1.4b (`--diff` mode):** the stateful `--diff <base>` memory-immutability mode (#7) — body/`valid_at` frozen, no provenance downgrades, append-only `source`, altered supersession fields ERROR. Core as a pure function `check_memory_diff(old, new)`; the CLI wires `git show <base>:<path>` around it. Separate increment (git coupling + immutability rules).
- **Slice 1.5 (governance):** constitution rule + #8 typed-rule checks (no-rung-six / orphan / missing-owner), the fixed Claude-Code hook set, version pin (#21), proposal schema (#17), consent-gate tripwire (#18), demo canon (#16).
- **Not cross-checked yet:** the skill's Memory row against the actual memory record's read/write declarations (a later hardening); topic-folder nuance in the index cross-check (this slice assumes one index per `memory/` tree).

## Self-Review

- **Ticket coverage (#7):** six-group schema → Task 1 doc + Task 2 checks; required tiers (provenance/owner/valid_at always ERROR; source ERROR-for-confirmed/WARN-else; review_by soft WARN) → Task 2; supersession invariants (missing pointer, fields-on-live, dangling) → Task 2; index lists-live-only (live-not-in-index WARN, superseded silent, entry→missing ERROR via referential integrity) → Task 3; one-record-per-file + path-as-identity → the discovery + `superseded_by`-as-path logic. `--diff` explicitly deferred (Scope note). #5 provisioning gate → Task 4 + the flip in Task 5.
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; complete code and content throughout; verification commands have expected output.
- **Type consistency:** `Finding(level, path, line, message)`, `_blank`, `_parse_date`, `iter_files(root, ignore)`, `load_gitignore`, `_LINK`, `parse_frontmatter` all reused with their existing signatures; `PROVENANCE` is a set; `check_memory(root)` and the extended `check_owner_cards(root)` match their call sites in `validate()`.
- **Real-content consistency:** the baseline record's `owner: Head of People` matches the skill/card/ontology owner; `next_review` on the card (2026-10-20) and `review_by` on the record (2026-10-15) are future, so no freshness/staleness WARN; the flipped skill's `baseline:` resolves to the created record. The loop is green on real content.
```

