# groundwork V1 — Slice 1.5a: Constitution rule schema + #8 typed-rule checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the first governance vertebra — the constitution rule schema (#8/§5.1: typed records, not runnable), the #8 validator checks (no-rung-six, orphan-prohibition, missing-owner-at-provisioning, plus the sunset/rung WARNs), and one worked compiled rule that governs the onboarding skill's riskiest proposed action.

**Architecture:** V1's constitution compiler ships **guided content, not generated automation** (#8). A rule is one `.md` file under `governance/constitution/`, its flat frontmatter carrying the four owned governance objects (value / rule / runtime-check / human-appeal — each with an owner), its **rung** on the five-rung ladder (`value` → `instruction` → `reminder` → `hard-block` → `human-decision`; there is no rung six), its `action_class`, a `sunset` date, and the ritual provenance (ritual / scarcity / surviving_job) that makes the orphan-prohibition checkable. The validator gains a #8 layer matching the #5/#6/#7 doctrine: strict where a rule backs a safety invariant, WARN on incomplete thinking, and the runnable enforcement (the hook set) is a separate slice (1.5b). The worked rule ties to the onboarding activity: it governs the "grant non-standard system access" action the onboarding skill may only *propose*.

**Tech Stack:** Python 3.9+ standard library only; stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** Keep `TestZeroDep` green (no new imports this slice).
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **#8 severity (verbatim), matching the #5/#6/#7 spine:**
  - **ERROR (blocks provisioning):** **no-rung-six** — a `high-risk` rule must carry a human-appeal path (never terminates in automation); **orphan-prohibition** — a repealed ritual's surviving job must be reassigned before the repeal ships; **missing owner** on an active (rung-placed) rule.
  - **WARN:** missing/overdue `sunset` date; a rule typed but **not yet placed on a rung** (draft).
  - **Silent:** there is no silent case at the rule-file level — a rule file exists because someone wrote it (like memory #7). "Untouched worksheet" silence is for rituals with no rule file at all.
- **The five-rung ladder (no rung six):** `value` → `instruction` → `reminder` → `hard-block` → `human-decision`. Consequential (high-risk) actions never terminate in automation.
- **Guided content only (#8):** rules are typed records; runnable per-rule automation is V2. The fixed hook set (the V1 runnable floor) is Slice 1.5b — NOT this slice.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.4b merged to `main` (done: `c310d4f`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.5a-constitution`.

---

## File Structure

- `governance/README.md` — **create.** The constitution-compiler convention (human doc).
- `scripts/validate.py` — **modify.** Add `RUNGS` + `check_constitution(root)`; wire into `validate()`.
- `tests/test_validate.py` — **modify.** Constitution checks (tempdir fixtures).
- `governance/constitution/access-grants-need-human-signoff.md` — **create.** The worked compiled rule.

> **Design notes — load-bearing craft calls (review carefully).**
> 1. **"Four objects / four owners" (§5.1) is interpreted as four owned fields inline on the rule record** — `value`/`value_owner`, the rule statement (the file's H1 + body), `runtime_check`/`runtime_check_owner`, `human_appeal`/`human_appeal_owner`. The alternative — four separate object files cross-referenced — was rejected as heavier than V1's "guided typed records" posture. If you read §5.1 as mandating separate objects, raise it before changing; every governance sub-slice inherits this shape.
> 2. **No-rung-six is enforced as "high-risk ⇒ human_appeal present"** (with an owner). The stronger reading — "high-risk must sit at the `human-decision` rung" — is *not* enforced, because a `hard-block` with a live appeal path also never terminates in automation (a human can override). Flagged; tighten only on your call.
> 3. **Active vs draft:** a rule with a `rung` is active (strict); a rule with no `rung` is a draft (WARN "not yet placed on a rung"). This is how #8's "unowned is fine while drafting, blocks at provisioning" maps to files, mirroring #6's provisioning gate.

---

## Task 1: The constitution convention doc + `RUNGS`

**Files:**
- Create: `governance/README.md`
- Modify: `scripts/validate.py` (add the `RUNGS` constant)

**Interfaces:**
- Produces: `RUNGS = {"value", "instruction", "reminder", "hard-block", "human-decision"}`.

- [ ] **Step 1: Create `governance/README.md`:**

```markdown
# Governance — the constitution compiler

groundwork's governance layer generates **machinery, not documents**. V1's constitution
compiler ships **guided content**: each surviving rule is a typed, validator-checked
record. (Runnable per-rule automation is V2; the fixed action-class hook set — the V1
runnable floor — ships separately.)

## Compiling a rule (the five-question worksheet)

For each ritual: name the ritual → name the scarcity it protected → is that scarcity
still real, and what job survives → rewrite it as a rule a person can verify → decide
the machinery (trigger, evidence, action, owner, appeal). Start with the rule everyone
resents.

## A rule is four owned objects, on a rung, with a sunset

Every kept rule is one file under `governance/constitution/`, carrying four governance
objects — each with its own owner:

- **value** — the principle it protects (`value`, `value_owner`).
- **rule** — the verifiable statement (the file's title + body; `owner` owns it).
- **runtime check** — the machinery: trigger, evidence, action (`runtime_check`,
  `runtime_check_owner`).
- **human appeal** — the escalation path (`human_appeal`, `human_appeal_owner`).

It is placed on the **five-rung enforcement ladder** — `value` → `instruction` →
`reminder` → `hard-block` → `human-decision`. **There is no rung six:** a consequential
(`high-risk`) action never terminates in automation, so it must carry a human-appeal
path. Every rule gets a **sunset** date. When a ritual is repealed, its **surviving
job** must be reassigned before the repeal ships (orphan-prohibition).

## What the validator enforces

- **ERROR:** a `high-risk` rule with no human-appeal path (no rung six); a repeal
  (`repeals`) whose `surviving_job` is not `reassigned_to` someone; an active rule
  (placed on a rung) with no `owner`.
- **WARN:** a missing or overdue `sunset`; a rule not yet placed on a rung (draft).
```

- [ ] **Step 2: Add the constant** — in `scripts/validate.py`, near the other vocabularies:

```python
RUNGS = {"value", "instruction", "reminder", "hard-block", "human-decision"}
```

- [ ] **Step 3: Verify the doc validates**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 scripts/validate.py governance`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add governance/README.md scripts/validate.py
git commit -m "docs: constitution-compiler convention (§5.1, #8) + RUNGS constant

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: `check_constitution` — the #8 typed-rule checks

**Files:**
- Modify: `scripts/validate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Consumes: `parse_frontmatter`, `_blank`, `_parse_date`, `ACTION_CLASSES`, `RUNGS`.
- Produces: `check_constitution(root) -> list[Finding]`, wired into `validate(root)`.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
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
            self._rule(d, RULE_OK.replace("owner: Head of IT\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "owner" in f.message
                                for f in validate.check_constitution(d)))

    def test_draft_rule_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            # no rung → draft; also drop owner (fine while drafting)
            self._rule(d, RULE_OK.replace("rung: human-decision\n", "").replace("owner: Head of IT\n", ""))
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

    def test_validate_wires_constitution(self):
        with tempfile.TemporaryDirectory() as d:
            self._rule(d, RULE_OK.replace("rung: human-decision", "rung: rung-six"))
            self.assertTrue(any(f.level == "ERROR" and "rung" in f.message for f in validate.validate(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestConstitution -v`
Expected: FAIL — no attribute `check_constitution`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`:

```python
def check_constitution(root):
    """#8 typed-rule checks. Strict where a rule backs a safety invariant; WARN on
    incomplete thinking. The runnable hook set is a separate artifact (Slice 1.5b)."""
    findings = []
    base = os.path.join(root, "governance", "constitution")
    if not os.path.isdir(base):
        return findings
    today = datetime.date.today()
    for name in sorted(os.listdir(base)):
        if not name.endswith(".md") or name in {"README.md", "_index.md"}:
            continue
        abspath = os.path.join(base, name)
        rel = os.path.relpath(abspath, root)
        with open(abspath, encoding="utf-8") as fh:
            data, fm = parse_frontmatter(fh.read(), rel)
        findings += fm

        rung = data.get("rung")
        active = not _blank(rung)
        if not active:
            findings.append(Finding("WARN", rel, None, "rule not yet placed on a rung (draft)"))
        else:
            if not (isinstance(rung, str) and rung in RUNGS):
                findings.append(Finding("ERROR", rel, None,
                                        "invalid rung %r (one of %s)" % (rung, sorted(RUNGS))))
            if _blank(data.get("owner")):
                findings.append(Finding("ERROR", rel, None, "active rule has no owner"))
            ac = data.get("action_class")
            if not _blank(ac) and not (isinstance(ac, str) and ac in ACTION_CLASSES):
                findings.append(Finding("ERROR", rel, None,
                                        "invalid action_class %r (one of %s)" % (ac, sorted(ACTION_CLASSES))))
            if isinstance(ac, str) and ac == "high-risk" \
                    and (_blank(data.get("human_appeal")) or _blank(data.get("human_appeal_owner"))):
                findings.append(Finding("ERROR", rel, None,
                                        "high-risk rule must carry a human-appeal path with an owner "
                                        "(there is no rung six)"))
            sunset = data.get("sunset")
            if _blank(sunset):
                findings.append(Finding("WARN", rel, None, "missing sunset date"))
            else:
                sd = _parse_date(sunset)
                if sd is not None and sd < today:
                    findings.append(Finding("WARN", rel, None, "sunset date has passed"))

        if not _blank(data.get("repeals")):
            if _blank(data.get("surviving_job")) or _blank(data.get("reassigned_to")):
                findings.append(Finding("ERROR", rel, None,
                                        "orphan-prohibition: a repealed ritual's surviving job must be "
                                        "reassigned ('surviving_job' + 'reassigned_to') before the repeal ships"))
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_memory(root)`, add:

```python
    findings += check_constitution(root)
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #8 constitution checks (no-rung-six, orphan, owner-at-provisioning) + wire in

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: Author the worked constitution rule (the governance vertebra)

**Files:**
- Create: `governance/constitution/access-grants-need-human-signoff.md`

**Interfaces:** must pass `check_constitution` with zero ERRORs; it governs the onboarding skill's `proposed_only_actions: grant non-standard system access`.

- [ ] **Step 1: Create `governance/constitution/access-grants-need-human-signoff.md`:**

```markdown
---
owner: Head of IT
rung: human-decision
action_class: high-risk
sunset: 2027-07-01
value: Least-privilege access protects the company and its customers' data
value_owner: CISO
runtime_check: The onboarding agent may propose a non-standard access grant but must halt for a named approver; the provisioning log records who approved and when
runtime_check_owner: Head of IT
human_appeal: A denied or delayed grant can be escalated to the CISO, who decides within one business day
human_appeal_owner: CISO
ritual: IT manually provisioning every access request by ticket
scarcity: Security-review time — every access grant used to get a human's eyes
surviving_job: Deciding whether a non-standard grant is warranted (kept human)
---
# Non-standard system access requires human sign-off

**The rule.** An agent may *propose* a non-standard system-access grant; it may never
*perform* one. Every such grant halts for a named human approver, who is recorded in
the provisioning log.

**Why it sits at the human-decision rung.** Granting access is `high-risk` — it can
expose company and customer data — so it can never terminate in automation. There is
no rung six: the agent's authority stops at *proposing*, and a human decides. This is
the rule behind the onboarding skill's `proposed-only` action "grant non-standard
system access" ([Owner's Card](../../skills/onboarding-orchestration/owner-card.md)).

**Appeal.** A denied or delayed grant escalates to the CISO, who decides within one
business day — so the block never becomes a silent dead end.
```

- [ ] **Step 2: Validate the whole repo**

Run: `python3 scripts/validate.py .`
Expected: exit 0, zero ERRORs. The rule is active (rung `human-decision`), owned, high-risk with a human-appeal path present, sunset in the future, no repeal — so no #8 ERROR/WARN fires against it.

- [ ] **Step 3: Confirm the governance vertebra**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0. The onboarding activity now carries a typed constitution rule governing its riskiest proposed action, checked at #8 strictness — governance joins ontology → skill → card → baseline.

- [ ] **Step 4: Commit**

```bash
git add governance/constitution/access-grants-need-human-signoff.md
git commit -m "feat(governance): constitution rule — access grants need human sign-off (#8 slice)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next sub-slices)

- **Slice 1.5b:** the fixed Claude-Code hook set (#8 item 2) enforcing the four action classes (high-risk hard-blocks), degrading to a review-gate instruction on other harnesses (#19). A global, hand-authored artifact — not this slice.
- **Slice 1.5c:** version pin (#21) + skew checks (`SCHEMA_VERSION`, `MIGRATIONS.md`, per-check `since:` tags, migration gate) + the deferred stateless-walker symlink-directory hardening.
- **Slice 1.5d:** proposal schema (#17) + consent gate (#18) + the blast-radius match tripwire (reuses 1.4b `--diff` infra) + the governance changelog.
- **Phase 2.3:** demo canon (#16) + the synthetic-identifier check (scoped to `demo/`, inert until the demo exists).
- **Not enforced (flagged design note 2):** high-risk-must-sit-at-`human-decision`-rung; only human-appeal-presence is enforced.

## Self-Review

- **Ticket coverage (#8 item 4):** no-rung-six (high-risk ⇒ human-appeal) → Task 2 + Task 3 content; orphan-prohibition → Task 2; missing-owner-at-provisioning (active rule) → Task 2; sunset WARN + not-placed-on-rung WARN → Task 2; silent-only-for-no-file → the file-exists-means-active model. Guided-content-only (typed records, no runnable) → the schema is records; the hook set is deferred (Scope note).
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; complete code and content; verification commands have expected output.
- **Type consistency:** `Finding`, `_blank`, `_parse_date`, `ACTION_CLASSES`, `parse_frontmatter` reused with existing signatures; `RUNGS` is a set; `check_constitution(root)` matches its call site in `validate()`; non-scalar guards (`isinstance(..., str)`) applied on `rung`/`action_class` per the crash/fail-open precedent from prior slices.
- **Real-content consistency:** the rule's `action_class: high-risk` + present `human_appeal`/`human_appeal_owner` pass no-rung-six; `sunset: 2027-07-01` is future; no `repeals` field, so the orphan check does not fire; it references the onboarding Owner's Card by a valid relative path (referential-integrity clean).
```

