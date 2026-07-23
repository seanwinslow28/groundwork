# groundwork V1 — Slice 1.3: Work packages + Owner's Cards + #6 checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the skills-as-work-packages layer of the vertical slice — the work-package convention (§6), the Owner's Card schema (#6), the worked onboarding-orchestration skill + its filled card, and the #6 validator checks (required-spine strictness at provisioning, the track-2 trio, and the three drift checks that keep card ↔ skill ↔ ontology consistent).

**Architecture:** A skill is a **work package**: a directory `skills/<name>/` holding `SKILL.md` (the skill core + frontmatter: `action_class`, `provisioned`, and the `ontology` path it was generated for; plus harness requirements, compatibility notes, and a Memory row) and `owner-card.md` (the Owner's Card — human-owned accountability fields). Files that change together live together. Provisioning status is single-homed on `SKILL.md`; card strictness follows it (ERROR when provisioned, WARN while drafting). The validator gains a #6 layer that checks each card's required spine, the track-2 trio (keyed on action class), and three cross-file drift checks. This is the third vertebra of the walking skeleton, built for the same activity the Slice 1.2 ontology already describes.

**Tech Stack:** Python 3.9+ standard library only (adds `datetime` for the freshness check); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only** (this slice adds `datetime`). Keep `TestZeroDep`'s allowlist current.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **#6 severity doctrine (verbatim intent):** strictness attaches **at provisioning**. ERROR marks *inconsistent machinery*, never *insufficient diligence* — staleness only WARNs, even on high-risk. A validator must not start failing purely because time passed.
- **#6 field placement (from ticket #6 resolution):**
  - **Always required (spine):** owner, backup_owner, job, allowed_actions, proposed_only_actions, forbidden_actions, pause_condition, retirement_condition, source_of_truth, review_cadence, known_failure_modes (truthful "none observed yet" passes; blank doesn't), last_reviewed, next_review, success_standard.
  - **Track-2 trio (required at external-side-effect / high-risk; WARN below):** evidence_required, sources_must_not_use, review_sample.
  - **Optional (silent):** users, other_allowed_sources.
- **Generator refuses to draft (human-only, from interview):** backup_owner, forbidden_actions, pause_condition, retirement_condition. (The exemplar fills them as if a human answered — that is what the interview supplies.)
- **Action taxonomy (§5.3):** read-only / reversible-write / external-side-effect / high-risk.
- **Honesty rule:** no README/product claim precedes the capability. This slice touches only `skills/` + the validator, not README capability copy.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges. Fable 5 builds.
- **Commit trailer:** use the builder's own identity honestly (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` when Fable builds).

## Prerequisite

Slice 1.2 merged to `main` (done: `e5eebc2`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.3-skills`.

---

## File Structure

- `skills/work-package-spec.md` — **create.** The work-package + Owner's Card convention (human doc; the generator implements it in Phase 3).
- `scripts/validate.py` — **modify.** Add card/skill vocabularies, a `_blank` helper, and `check_owner_cards(root)`; wire into `validate()`.
- `tests/test_validate.py` — **modify.** Card checks + drift checks (tempdir fixtures).
- `skills/onboarding-orchestration/SKILL.md` — **create.** The worked work-package skill.
- `skills/onboarding-orchestration/owner-card.md` — **create.** Its filled Owner's Card.

> **Design notes — load-bearing craft calls (review carefully).**
> 1. **Skill + card co-located in `skills/<name>/`; provisioning single-homed on `SKILL.md`.** The card's strictness follows the skill's `provisioned` flag, so there is one home for "is this live."
> 2. **The engine's `skills/` holds the worked *exemplar* (§10).** The `.agents/skills/<name>/` + `.claude/skills/` symlink runtime layout (#19) is *documented* in `work-package-spec.md` and *demonstrated* later in `demo/` (Phase 2.3) — not reproduced in the engine exemplar. This keeps 1.3 about the work-package + card schema, not runtime delivery.
> 3. **Onboarding-orchestration is classified `external-side-effect`** (it creates accounts, orders equipment, sends schedules within bounded onboarding; access-granting steps route through the exception path + review gate). This exercises the track-2 trio without pulling in the high-risk "no rung six" appeal-path rule (that's governance, Slice 1.5). If you judge account/access provisioning to be `high-risk`, raise it before changing — it would pull a governance dependency into this slice.

---

## Task 1: The work-package + Owner's Card convention doc

**Files:**
- Create: `skills/work-package-spec.md`

**Interfaces:** none (human doc; establishes the field names Tasks 2–4 use).

- [ ] **Step 1: Create `skills/work-package-spec.md`:**

```markdown
# Skills as work packages

A groundwork skill is never a bare `SKILL.md`. Copying a SKILL.md alone fails across harnesses — loading rules differ, hooks become prose, sub-agents don't exist, MCP configs vanish (§6). So every generated skill ships as a **work package**: a directory `skills/<name>/` (engine exemplars) — or `.agents/skills/<name>/` with a `.claude/skills/<name>` symlink when delivered to a company (#19) — containing:

- **`SKILL.md`** — the skill core, with frontmatter:
  - `name` — the skill's directory name.
  - `description` — the **selection surface**, reviewed like landing-page copy: outcome-oriented and **non-overlapping** with other skills (agents mis-select at 30+ overlapping tools). One outcome, stated plainly.
  - `action_class` — one of `read-only` / `reversible-write` / `external-side-effect` / `high-risk` (§5.3). Declared everywhere; enforced by hooks where the harness supports them, by review gates where it doesn't.
  - `provisioned` — `yes` once the skill is live for a company; `no` while drafting. The validator's card strictness follows this flag.
  - `ontology` — the path to the ontology deep record this skill was generated for (referential-integrity- and drift-checked).
- **Harness requirements** — the tools, permissions, scripts, and connectors the skill needs to run.
- **Compatibility notes** — "tested in X; here is what breaks in Y." Honesty as a feature. Seeds the card's `known_failure_modes`.
- **A Memory row** — what the skill may **read** from org memory, **write** back, or keep **run-only** (required now that harnesses write memory by default; the constitution must say what agents may persist).
- **`owner-card.md`** — the Owner's Card (below). The owner lives here, not in the skill body.

The one-question test ships with every package: *"if I had to move this skill tomorrow, what would break?"*

## The Owner's Card

Human-owned accountability. Required-ness of a field is a property of the skill's **action class**, atop a spine no card may lack (#6). The generator **refuses** to invent the owner, the forbidden actions, and the death conditions — those come only from a human's interview answers.

**Always required (the spine), every card:**
`owner`, `backup_owner`, `job` (one sentence), `allowed_actions`, `proposed_only_actions`, `forbidden_actions`, `pause_condition`, `retirement_condition`, `source_of_truth`, `review_cadence`, `known_failure_modes` (a truthful "none observed yet" passes; blank does not), `last_reviewed`, `next_review`, `success_standard`.

**Required at `external-side-effect` / `high-risk` (review track 2); a WARN below:**
`evidence_required`, `sources_must_not_use`, `review_sample` — exactly what a track-2 reviewer physically needs.

**Optional, silent:** `users`, `other_allowed_sources`.

**Generator drafts (human confirms at PR review):** `job`, `source_of_truth`, `review_cadence`, `success_standard` (from the captured baseline), `last_reviewed`/`next_review`, `allowed_actions` + `proposed_only_actions` (observable from the skill just written), `owner` (surfaced from the ontology's accountability owner — drift-checked), and seeded `known_failure_modes` (from the compatibility notes).

**Interview must ask a human (per provisioned skill):** `backup_owner`, `forbidden_actions`, `pause_condition`, `retirement_condition`. These never appear in generator template output.

Doctrine: *shared use is fine; shared responsibility is often no responsibility* — and *some agents should die* (the death conditions are only meaningful because a human named the trigger).
```

- [ ] **Step 2: Verify the doc validates** (no broken links, no secrets):

Run: `cd "$(git rev-parse --show-toplevel)" && python3 scripts/validate.py skills`
Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add skills/work-package-spec.md
git commit -m "docs: work-package + Owner's Card convention (§6, #6)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Card vocabularies + required-spine, track-2, and freshness checks

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Produces:
  - Constants `ACTION_CLASSES`, `TRACK2_CLASSES`, `CARD_REQUIRED` (list), `CARD_TRACK2` (list).
  - `_blank(v) -> bool` — True for `None`, `[]`, or whitespace-only string (the #11 reader returns `[]` for a bare `key:`).
  - `check_owner_cards(root) -> list[Finding]` — for this task, the single-file checks (required spine, track-2 trio, action-class validity, freshness). Cross-file drift is added in Task 3.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestOwnerCard -v`
Expected: FAIL — no attribute `check_owner_cards`.

- [ ] **Step 3: Implement** — in `scripts/validate.py`, add `import datetime` to the imports, then add:

```python
ACTION_CLASSES = {"read-only", "reversible-write", "external-side-effect", "high-risk"}
TRACK2_CLASSES = {"external-side-effect", "high-risk"}
CARD_REQUIRED = ["owner", "backup_owner", "job",
                 "allowed_actions", "proposed_only_actions", "forbidden_actions",
                 "pause_condition", "retirement_condition",
                 "source_of_truth", "review_cadence", "known_failure_modes",
                 "last_reviewed", "next_review", "success_standard"]
CARD_TRACK2 = ["evidence_required", "sources_must_not_use", "review_sample"]


def _blank(v):
    """A field is blank if absent, an empty list (a bare 'key:'), or whitespace."""
    return v is None or v == [] or (isinstance(v, str) and v.strip() == "")


def _parse_date(v):
    if not isinstance(v, str):
        return None
    try:
        return datetime.date.fromisoformat(v.strip())
    except ValueError:
        return None


def check_owner_cards(root):
    """#6 checks over skills/<name>/ work packages. Strictness follows the
    skill's `provisioned` flag. Cross-file drift checks are added in Task 3."""
    findings = []
    base = os.path.join(root, "skills")
    if not os.path.isdir(base):
        return findings
    today = datetime.date.today()
    for name in sorted(os.listdir(base)):
        sdir = os.path.join(base, name)
        skill_path = os.path.join(sdir, "SKILL.md")
        if not (os.path.isdir(sdir) and os.path.isfile(skill_path)):
            continue
        rel_skill = os.path.relpath(skill_path, root)
        with open(skill_path, encoding="utf-8") as fh:
            skill_fm, sfm_findings = parse_frontmatter(fh.read(), rel_skill)
        findings += sfm_findings
        provisioned = isinstance(skill_fm.get("provisioned"), str) and \
            skill_fm["provisioned"].strip().lower() == "yes"
        action_class = skill_fm.get("action_class")
        if isinstance(action_class, str) and action_class not in ACTION_CLASSES:
            findings.append(Finding("ERROR", rel_skill, None,
                                    "invalid action_class %r (one of %s)" % (action_class, sorted(ACTION_CLASSES))))

        card_path = os.path.join(sdir, "owner-card.md")
        if not os.path.isfile(card_path):
            if provisioned:
                findings.append(Finding("ERROR", os.path.join(os.path.relpath(sdir, root), "owner-card.md"),
                                        None, "provisioned skill has no Owner's Card"))
            continue
        rel_card = os.path.relpath(card_path, root)
        with open(card_path, encoding="utf-8") as fh:
            card, cfm_findings = parse_frontmatter(fh.read(), rel_card)
        findings += cfm_findings
        miss = "ERROR" if provisioned else "WARN"

        for field in CARD_REQUIRED:
            if _blank(card.get(field)):
                findings.append(Finding(miss, rel_card, None, "missing required card field '%s'" % field))

        is_track2 = isinstance(action_class, str) and action_class in TRACK2_CLASSES
        for field in CARD_TRACK2:
            if _blank(card.get(field)):
                level = "ERROR" if (is_track2 and provisioned) else "WARN"
                findings.append(Finding(level, rel_card, None,
                                        "track-2 field '%s' blank (required at external-side-effect/high-risk)" % field))

        nr = _parse_date(card.get("next_review"))
        if nr is not None and nr < today:
            findings.append(Finding("WARN", rel_card, None, "next_review date has passed (freshness)"))
        lr = _parse_date(card.get("last_reviewed"))
        if lr is not None and (today - lr).days > 90:
            findings.append(Finding("WARN", rel_card, None, "last_reviewed is over 90 days old (freshness)"))
    return findings
```

- [ ] **Step 4: Run to verify pass**

Run: `python3 -m unittest tests.test_validate.TestOwnerCard -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #6 Owner's Card checks — required spine, track-2 trio, freshness

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The three drift checks + wire into `validate()`

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `check_owner_cards` (extend it), `parse_frontmatter`.
- Produces: `check_owner_cards` now also emits the three #6 drift ERRORs; `validate(root)` calls `check_owner_cards(root)`.

The three drift checks (all ERROR — inconsistent machinery): (a) card `action_class` ≠ skill `action_class`; (b) card `owner` ≠ the referenced ontology's `accountable_owner`; (c) card `source_of_truth` ≠ the ontology's `gate_source_of_truth`. Plus: a skill's `ontology` reference must resolve.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestCardDrift -v`
Expected: FAIL — drift ERRORs not yet emitted (and `validate` does not yet call the card checks).

- [ ] **Step 3: Implement** — in `check_owner_cards`, **after** the freshness block and **before** the loop's end (still inside the `for name` loop, after `card` is parsed), add the drift checks:

```python
        # --- drift: card action_class vs skill action_class ---
        card_ac = card.get("action_class")
        if isinstance(action_class, str) and isinstance(card_ac, str) and card_ac.strip() != action_class.strip():
            findings.append(Finding("ERROR", rel_card, None,
                                    "card action_class %r drifts from skill action_class %r" % (card_ac, action_class)))
        # --- drift: card owner / source_of_truth vs the referenced ontology ---
        ont_ref = skill_fm.get("ontology")
        if isinstance(ont_ref, str) and ont_ref.strip():
            ont_abs = os.path.join(root, ont_ref.strip())
            if not os.path.isfile(ont_abs):
                findings.append(Finding("ERROR", rel_skill, None,
                                        "ontology reference not found: %s" % ont_ref.strip()))
            else:
                with open(ont_abs, encoding="utf-8") as fh:
                    ont, _ = parse_frontmatter(fh.read(), ont_ref.strip())
                acc = ont.get("accountable_owner")
                if isinstance(acc, str) and isinstance(card.get("owner"), str) \
                        and card["owner"].strip() != acc.strip():
                    findings.append(Finding("ERROR", rel_card, None,
                                            "card owner %r drifts from ontology accountable_owner %r"
                                            % (card["owner"], acc)))
                gsot = ont.get("gate_source_of_truth")
                if isinstance(gsot, str) and isinstance(card.get("source_of_truth"), str) \
                        and card["source_of_truth"].strip() != gsot.strip():
                    findings.append(Finding("ERROR", rel_card, None,
                                            "card source_of_truth drifts from ontology gate_source_of_truth"))
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_ontology(root)`, add:

```python
    findings += check_owner_cards(root)
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (all classes).

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #6 drift checks (card<->skill action_class; card<->ontology owner/source) + wire in

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Author the worked onboarding work package (the vertical proof)

**Files:**
- Create: `skills/onboarding-orchestration/SKILL.md`
- Create: `skills/onboarding-orchestration/owner-card.md`

**Interfaces:** the content must pass `check_owner_cards` with zero ERRORs — the slice closing its loop against the Slice 1.2 ontology.

> The card's `owner` and `source_of_truth` must match `ontologies/people-hr/onboarding-orchestration.md` **exactly** (the drift check uses stripped string equality): `owner: Head of People`; `source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state`.

- [ ] **Step 1: Create `skills/onboarding-orchestration/SKILL.md`:**

```markdown
---
name: onboarding-orchestration
description: Provision a new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Onboarding orchestration

Provision every new hire before their start date: create accounts, order standard
equipment, send the day-one schedule, and notify the manager and buddy — pausing to
a human on any exception. Generated for the People/HR onboarding-orchestration
activity ([ontology record](../../ontologies/people-hr/onboarding-orchestration.md)).

## Harness requirements
- Read/write access to the HRIS and the IT provisioning tracker.
- Permission to send calendar invites and onboarding emails.
- No spend and no deletion permissions (see the Owner's Card forbidden actions).

## Compatibility notes
- Tested in Claude Code (action-class hooks enforce the external-side-effect gate).
- On Codex / Cursor / Gemini CLI the action-class hook is absent; the same gate
  ships as a review-gate instruction (#19) — a human confirms before accounts are
  created. What breaks silently otherwise: nothing structural, but the hard-block
  becomes advisory, so the review gate is mandatory there.

## Memory row
- **Reads:** the pre-provisioning onboarding baseline (time-to-day-one-ready).
- **Writes:** an onboarding-completed note per hire (observed provenance).
- **Run-only:** the per-run checklist state (not persisted to org memory).
```

- [ ] **Step 2: Create `skills/onboarding-orchestration/owner-card.md`:**

```markdown
---
owner: Head of People
backup_owner: People Ops Lead
job: Provision every new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
allowed_actions: create accounts in the HRIS/IT tracker; order standard equipment; send the day-one schedule; notify manager and buddy
proposed_only_actions: grant non-standard system access; convert a contractor to an employee
forbidden_actions: approve compensation; sign offer letters; delete employee records
pause_condition: the HRIS or IT tracker is unreachable, or required intake data is missing
retirement_condition: onboarding moves to a dedicated HRIS-native workflow the team trusts more
source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
review_cadence: monthly
known_failure_modes: none observed yet; on other harnesses the action-class hard-block degrades to an advisory review gate (#19)
last_reviewed: 2026-07-20
next_review: 2026-10-20
success_standard: Every new hire is day-one-ready (accounts + equipment + schedule) before their start date, measured against the pre-provisioning baseline
evidence_required: The completed onboarding checklist with per-item timestamps and the provisioning log
sources_must_not_use: Personal email or chat threads as a source of truth for access grants
review_sample: One onboarding per week spot-checked by the hiring manager
---
# Owner's Card — Onboarding orchestration

The **Head of People** owns this skill; the **People Ops Lead** is the backup. It
runs the onboarding runbook as an agent that provisions against the HRIS record and
pauses to a human on any exception. It may propose — never unilaterally perform —
non-standard access grants and contractor conversions, and it may never touch
compensation, offers, or record deletion. It pauses when its sources of truth are
unreachable, and it should be retired once a trusted HRIS-native workflow supersedes it.
```

- [ ] **Step 3: Validate the real content end-to-end**

Run: `python3 scripts/validate.py .`
Expected: exit 0, zero ERRORs (no missing-field, track-2, drift, or ontology-ref ERROR against the new files). The card owner/source_of_truth match the Slice 1.2 ontology; `next_review` is in the future so no freshness WARN.

- [ ] **Step 4: Confirm the slice proves the layer**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0. The onboarding activity now runs ontology → work-package skill → Owner's Card, consistent across all three files under #6 strictness.

- [ ] **Step 5: Commit**

```bash
git add skills/onboarding-orchestration/
git commit -m "feat(skills): onboarding-orchestration work package + Owner's Card (#6 slice proof)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next plans)

- **Deferred here (was bundled in the spec's 1.3):** the fixed Claude-Code hook set (#8) that *enforces* the action taxonomy — a global, hand-authored artifact, moved to sit with the constitution in Slice 1.5.
- **Slice 1.4 (memory):** the captured-baseline org-memory record the Memory row + the ontology Accountability section reference (#7); the `--diff` mode.
- **Slice 1.5 (governance):** the constitution rule + the #8 typed-rule checks (no-rung-six / orphan / missing-owner), the fixed hook set, version pin (#21), proposal schema (#17), consent-gate tripwire (#18), demo canon (#16).
- **Not cross-checked yet:** the Memory row against real memory records (needs #7 — Slice 1.4); the `.agents/skills/` + symlink runtime layout (#19), demonstrated in `demo/` (Phase 2.3).

## Self-Review

- **Spec / ticket coverage:** work-package structure (§6: SKILL.md + harness requirements + compatibility notes + Memory row + owner) → Task 1 + Task 4; Owner's Card spine/track-2/optional placement (#6) → Task 2; generator-refuses-vs-drafts split → documented in Task 1, embodied by the exemplar in Task 4; strictness-at-provisioning + staleness-only-WARN (#6) → Task 2 severity logic; the three drift checks + provisioned-needs-card (#6 ERROR list) → Task 3; action taxonomy (§5.3) → vocabularies in Task 2. Covered. Hook set (#8 item 2) explicitly deferred (Scope note).
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; every code step shows complete code; content files are complete; verification commands have expected output.
- **Type consistency:** `Finding(level, path, line, message)` used identically; `_blank`, `_parse_date`, `check_owner_cards(root)` signatures match call sites; `CARD_REQUIRED`/`CARD_TRACK2` are lists, `ACTION_CLASSES`/`TRACK2_CLASSES` are sets, used accordingly; the exemplar card's `owner` and `source_of_truth` strings match `AUTOMATE_OK` / the Slice 1.2 ontology exactly, so the drift checks pass on real content.
- **Frontmatter compatibility:** all skill and card fields are flat `key: value` scalars within the #11 reader's grammar; multi-item fields (allowed_actions, etc.) are single semicolon-joined strings, not YAML lists, so the reader returns strings (not `[]`) and `_blank` behaves. Consistent.
```

