# groundwork V1 — Slice 2.3d: the demo's skills + governance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Umbercress the machinery its ontologies already point at. Four work packages (`SKILL.md` + `owner-card.md`) for renewal preparation, feature-request triage, onboarding orchestration, and performance-review prep — each citing its already-committed baseline under `demo/memory/`. The demo constitution: three typed rules on three different rungs, including the **rung-5 human-decision rule** that fires in demo query 3 and blocks an agent from drafting a performance assessment. And the **meeting-challenger runnable exemplar** (#8 item 3) — one hand-authored, worked, runnable rung-3 reminder, compatibility-noted, a copy-me reference, never generated.

**Architecture:** `demo/` already is an instance (2.3a). Adding `skills/` and `governance/` puts `_check_owner_cards_instance` and `_check_constitution_instance` on demo content for the first time, with every reference resolving inside `demo/`. No schema changes. One test-only change (Task 3, flagged below) so the repo's zero-dependency guarantee actually covers the new runnable artifact.

**Tech Stack:** Markdown + one Python 3 stdlib-only script. No `scripts/validate.py` changes.

## Global Constraints

- **No validator changes.** If demo content trips a check, the content is wrong — fix the content. If a check is genuinely wrong, stop and report it rather than editing it inside a content slice.
- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task. Sixteen new files must add nothing. A new WARN is a real finding.
- **Test count is an invariant too:** `610 tests, OK (skipped=1)`. Task 3 *renames and widens* an existing test; it does not add one. If the count moves, something else changed.
- **Instance-relative references** (2.3a): inside `demo/`, a skill's `baseline:` is `memory/<record>.md` and its `ontology:` is `ontologies/<function>/<activity>.md`. Nothing may climb out of `demo/` — a demo skill citing an engine exemplar's baseline is exactly the borrowing 2.3a closed.
- **Exact-match drift fields:** a card's `owner` must equal its ontology's `accountable_owner` **character for character**, and the card's `source_of_truth` must equal the ontology's `gate_source_of_truth` **character for character**. These are the two ontology drift checks in `_check_owner_cards_instance`. Copy them; do not retype them.
- **Everything must trace to the canon** (2.3b): only `umbercress.example`, `555-01xx`, TEST-NET IPs — and this slice introduces none of them. **Avoid bare 7- and 10-digit number runs**, including inside the Python file and the JSON snippet: `check_synthetic_identifiers` scans *every* file under `demo/`, not just Markdown.
- **Dates:** cards use `last_reviewed: 2026-07-28` (today, never the future, never >90 days old) and `next_review: 2026-10-28`. Rules use `sunset: 2027-06-30`. A past `sunset` or `next_review` is a WARN and breaks the invariant.
- **Pronouns:** no person in `demo/canon.md` has stated pronouns. Use they/them for every named person, everywhere in this slice.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.3c merged and pushed (`28d3eba`; 610 tests with 1 designed skip, gate + `--diff main` exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.3d-demo-skills-governance
```

---

## Design calls flagged for the maintainer

**1. The meeting-challenger is a `defer` + `additionalContext` hook, not an `ask` — because that is what a rung-3 reminder *is*.**
This is the first artifact in the repo that renders a **rung** as a **mechanism**, so the mapping is load-bearing. The Claude Code hooks documentation was fetched live on 2026-07-28 (it now lives at `code.claude.com/docs/en/hooks`; the old `docs.claude.com` path 301s), and it confirms four `permissionDecision` values — `allow` / `deny` / `ask` / `defer` — plus an `additionalContext` string inside `hookSpecificOutput`, plus a universal top-level `systemMessage`.

That gives an exact ladder mapping: rung 4 (**hard-block**) is `deny` — what `action_class_gate.py` already emits. Rung 3 (**reminder**) is `defer` ("use normal permission flow") *plus* the reminder text: the action is not blocked, not auto-approved, and the permission outcome is untouched; the agent gets `additionalContext` and the human gets `systemMessage`. Using `ask` instead would have been **rung inflation** — machinery quietly claiming more authority than the rule was granted, which is the exact failure the five-rung ladder exists to prevent. Counter-argument: `additionalContext` is documented alongside `allow` in the reference example, not explicitly alongside `defer`, so there is a residual chance the agent-facing half is dropped on a `defer`. That is why the reminder is emitted **twice**, once as `additionalContext` and once as `systemMessage` (documented as universal to all events) — the human-facing half is contract-guaranteed either way, and the README says so plainly rather than claiming a rendering we cannot verify from here.

**2. The exemplar lives in `demo/governance/reminders/`, and it ships NO `settings.snippet.json`.**
`check_hooks` is **root-only by design** (locked in 2.3a: "a per-instance version would invite a `demo/governance/hooks/` whose registration claim nothing could satisfy"). So anything the demo puts under a `hooks/` directory gets zero existence-checking — and a registration file that nothing verifies is precisely the named-but-unwired guard this repo has refused to ship twice (1.5b made `check_hooks` verify the registration; 2.1's §6 drift check was made structural for the same reason). Two consequences: the directory is named `reminders/` after its **rung**, not `hooks/`, so it makes no registration claim by its name; and the registration JSON lives in a **fenced block inside the exemplar's `README.md`**, next to the verification command, rather than as a `settings.snippet.json` file. The README also links the script with a relative Markdown link, so `check_links` catches path rot — the one gate that *does* reach this directory.
*Counter-argument:* a fenced block is less copy-pasteable than a file, and the engine's own hook set does ship a snippet file. The difference is that the engine's snippet is validated; the demo's would not be. I would rather ship a slightly less convenient artifact than an unverified one. If you disagree, the alternative is to extend `check_hooks` to per-instance — a validator change, in a content slice, reopening a locked 2.3a decision. **Your call; I recommend the fenced block.**

**3. Performance-review prep is `reversible-write`, not track 2 — and I want you to see the argument I rejected.**
Every other classification in this repo has been made **by mechanism** (2.2a: "the classification is only as honest as the scoping"). Mechanically, the review-prep skill files an evidence pack in the People workspace where the manager fetches it; nothing is sent, nothing reaches the employee, and a wrong pack is corrected by regenerating it before the conversation. That is `reversible-write`, structurally identical to renewal-prep.
*The argument against:* this is the highest-stakes activity in the demo — the ontology's own `gate_error_cost` says so — and it is the one the demo's emotional peak is built on. Classifying it track 1 could read as under-classifying, and there is a reading where handing a manager attributed peer feedback about a named person is not "reversible" in the sense that matters. I rejected it because that is a **harm** argument, and the action taxonomy is a **mechanism** taxonomy; letting harm drive classification would eventually reclassify everything sensitive as track 2 and destroy the distinction. The restraint story is carried where it is enforceable — the rung-5 rule and the card's `forbidden_actions` — not by inflating the action class. Note the cost is small either way: the card fills all three track-2 fields regardless, because a blank track-2 field WARNs even on track 1.

**4. The demo constitution ships three rules, on three different rungs — one of which declares a repeal.**
Three rules is the smallest set that shows the ladder is a ladder: `every-meeting-names-a-decision` at **reminder** (rung 3, the runnable exemplar's paired rule), `no-agent-contacts-a-customer` at **hard-block** (rung 4, holding the boundary that keeps renewal-prep and triage on track 1), and `performance-assessment-is-human-owned` at **human-decision** (rung 5, #4's governance block). Each one is bound to a real boundary in a real card, so no rule is decorative. The meeting rule additionally declares `repeals: The Monday all-hands status round` with a `reassigned_to`, which puts **orphan-prohibition on real content for the first time** — every other exercise of that branch has been a fixture. Same logic as 2.2b's `Motion: hire` record: a branch nothing real has ever run is a branch you do not know works.

**5. One test-only change, and it is not optional.** See Task 3 Step 3. `AGENTS.md` claims "`scripts/validate.py` and every shipped script import the Python standard library only," but `TestZeroDep` only scans `governance/hooks/*.py`. This slice ships the repo's first Python file outside that directory, so the claim would become true-by-luck instead of true-by-check. The fix widens the existing test to every shipped `.py` in the repo — a rename plus a wider glob, no new test, no `validate.py` change. This is a deliberate exception to "content slices change no code," taken because the alternative is shipping an enforcement claim that no longer covers what it names (§2.4 of the standing review discipline). Flagging it rather than sliding it in.

---

## File Structure

**Create (16 files):**

- `demo/skills/README.md`
- `demo/skills/renewal-prep/{SKILL.md,owner-card.md}`
- `demo/skills/feature-request-triage/{SKILL.md,owner-card.md}`
- `demo/skills/onboarding-orchestration/{SKILL.md,owner-card.md}`
- `demo/skills/performance-review-prep/{SKILL.md,owner-card.md}`
- `demo/governance/README.md`
- `demo/governance/changelog.md`
- `demo/governance/constitution/every-meeting-names-a-decision.md`
- `demo/governance/constitution/no-agent-contacts-a-customer.md`
- `demo/governance/constitution/performance-assessment-is-human-owned.md`
- `demo/governance/reminders/meeting-challenger/README.md`
- `demo/governance/reminders/meeting-challenger/meeting_challenger.py`

**Modify (3 files):** `demo/README.md`, `AGENTS.md`, `tests/test_validate.py`.

---

## Task 1: The four work packages

**Files:** Create `demo/skills/README.md` and eight files across four package directories.

> **Ordering rule for this task:** create each package's `SKILL.md` and `owner-card.md` **together**, then run the gate. A `SKILL.md` with `provisioned: yes` and no card is an ERROR, so committing them separately produces a deliberate-looking red gate for no reason.

- [ ] **Step 1: Create `demo/skills/README.md`:**

```markdown
# Umbercress — skills

The four activities Umbercress has acted on, each shipped as a work package: a
`SKILL.md` that says what the agent does, and an `owner-card.md` that says who
answers for it. The convention itself is documented in the engine
([work-package spec](../../skills/work-package-spec.md)); this directory is what it
looks like filled in for one company.

| Package | Action class | Owner | Ontology record |
|---|---|---|---|
| [renewal-prep](renewal-prep/SKILL.md) | reversible-write | Marcus Bell | [Renewal preparation](../ontologies/customer-success/renewal-preparation.md) |
| [feature-request-triage](feature-request-triage/SKILL.md) | reversible-write | Dana Whitfield | [Feature-request triage](../ontologies/product/feature-request-triage.md) |
| [onboarding-orchestration](onboarding-orchestration/SKILL.md) | external-side-effect | Ruth Okafor | [Onboarding orchestration](../ontologies/people-hr/onboarding-orchestration.md) |
| [performance-review-prep](performance-review-prep/SKILL.md) | reversible-write | Ruth Okafor | [Performance-review prep](../ontologies/people-hr/performance-review-prep.md) |

Three of the four are track 1 — everything they write is a document a person reads and
can rewrite. Onboarding is track 2 because it creates accounts, orders equipment, and
sends messages: side effects that leave the workspace. That difference is not a label,
it is what the Owner's Cards and the constitution are shaped around.
```

> Note: this table is in `skills/`, not `ontologies/`, so the canonical exec-view grammar does not apply to it. `parse_exec_table` only reads `_executive-view.md` files.

- [ ] **Step 2: Create `demo/skills/renewal-prep/SKILL.md`:**

```markdown
---
name: renewal-prep
description: Assemble a sourced renewal brief 45 days before an Umbercress contract renewal so the CSM walks in prepared
action_class: reversible-write
provisioned: yes
baseline: memory/renewal-prep-baseline.md
ontology: ontologies/customer-success/renewal-preparation.md
---
# Renewal preparation

Forty-five days before a contract renewal, assemble a brief for the account's CSM:
contract terms and dates from the CRM, the last 90 days of Relay usage read against
the account's own history, open and recently closed support tickets, and the notes
from the most recent quarterly check-in. Name the risks you can see and give an
expansion-or-contraction read. Every number carries a link to the record it came from.

Halt rather than guess. A missing or contradictory contract record, or usage data more
than seven days stale, stops the brief and routes to Marcus Bell. A brief with an
unmarked gap is worse than no brief, because it will be trusted.

This skill stops at a brief filed in the customer-success workspace. It does not decide
the renewal, price it, edit the contract or CRM opportunity record, or contact the
customer ([ontology record](../../ontologies/customer-success/renewal-preparation.md);
[the rule that holds the customer boundary](../../governance/constitution/no-agent-contacts-a-customer.md)).

## Harness requirements
- The governed pre-provisioning baseline for brief lead time and sourcing
  completeness: [memory/renewal-prep-baseline.md](../../memory/renewal-prep-baseline.md)
  (the `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the CRM contract and opportunity records, the Relay usage warehouse,
  the support-ticket system, and the quarterly check-in notes.
- Write access to the customer-success workspace location where briefs are filed, and
  nowhere else.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. Its writes are confined to the brief
  document, which is why it is `reversible-write`: a wrong brief is corrected by
  rewriting the file, and nothing reaches the customer. Widening it to write CRM fields
  or send the brief to a customer would make it track 2, and the classification and
  Owner's Card would have to change with it.
- Read-only access to the four source systems is a hard requirement, not a preference.
  A deployment that grants write access to the CRM breaks the claim above.

## Memory row
- **Reads:** the pre-provisioning renewal-prep baseline, and the at-risk-renewal record
  for the account when one exists.
- **Writes:** a per-renewal note recording which sources were available and which were
  stale at brief time (observed provenance).
- **Run-only:** the intermediate query results behind the brief.

## Portability check

*If I had to move this skill tomorrow, what would break?* The CRM, usage-warehouse,
support-system, and check-in-notes connectors; the governed baseline record; the
customer-success workspace write location; and the CSM review gate named in the
Owner's Card.
```

- [ ] **Step 3: Create `demo/skills/renewal-prep/owner-card.md`:**

```markdown
---
owner: Marcus Bell
backup_owner: Nina Sokolova
job: Assemble a sourced renewal brief 45 days before each contract renewal
action_class: reversible-write
allowed_actions: read CRM contract and opportunity records, Relay usage data, support tickets, and quarterly check-in notes; write and revise the renewal brief in the customer-success workspace
proposed_only_actions: flag an account as a churn risk on the CRM record after the account's CSM confirms the read
forbidden_actions: edit contract or opportunity records; propose or quote pricing; contact the customer; send the brief outside the customer-success workspace
pause_condition: the contract record is missing or contradicts the CRM opportunity; usage data is more than seven days stale; the support system is unreachable
retirement_condition: the CRM ships a renewal-brief view the team trusts more, or renewals stop starting from a written brief
source_of_truth: The CRM contract record for terms and dates; the Relay usage warehouse for product adoption
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; a brief assembled from a partially stale warehouse can look complete, which is why staleness halts rather than annotates
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every renewal has a sourced brief in its CSM's hands 45 days ahead with every number resolving to a source record, measured against the pre-provisioning baseline of eight days' median lead time and fifteen briefs in twenty-six renewals
evidence_required: The brief itself with its per-claim source links, and the source-availability note recorded for the run
sources_must_not_use: A chat thread, an email, or a CSM's recollection as a source of truth for contract terms or usage numbers
review_sample: The account's CSM reads every brief before the renewal conversation; Marcus Bell reviews two briefs a month against their source records
---
# Owner's Card — Renewal preparation

**Marcus Bell** owns this skill; **Nina Sokolova** is the backup. It assembles a sourced
renewal brief and stops there — it may not touch contract or opportunity records,
propose pricing, or contact a customer. Flagging an account as a churn risk is
proposed-only and waits on the CSM's confirmation.

The boundary is what keeps this skill track 1: everything it writes is a document a
person reads and can rewrite. If it is ever given write access to the CRM or a path to
the customer, it becomes an external-side-effect skill and this card must be rewritten
before that ships. The rule at
[no agent contacts a customer](../../governance/constitution/no-agent-contacts-a-customer.md)
holds that boundary from the other side.

It pauses rather than papering over a gap, because a brief that looks complete is
trusted. The CSM's read before every renewal conversation is the review gate; Marcus
Bell's twice-monthly sample against source records is the quality check.
```

- [ ] **Step 4: Create `demo/skills/feature-request-triage/SKILL.md`:**

```markdown
---
name: feature-request-triage
description: File, deduplicate, and route each week's incoming feature requests to the owning product manager with the accounts that asked
action_class: reversible-write
provisioned: yes
baseline: memory/triage-baseline.md
ontology: ontologies/product/feature-request-triage.md
---
# Feature-request triage

Once a week, collect every feature request raised in support tickets, in CRM
opportunity and check-in notes, and by the customer-success team. For each one: check
whether the tracker already knows it and link the duplicate if so, tag it by theme,
attach the accounts that asked and the annual contract value they represent, and assign
it to the product manager who owns that theme.

Leave what you cannot place. A request matching no existing theme and no owning product
manager stays unassigned and goes to Dana Whitfield. Forcing it into the nearest tag is
how a signal disappears — an unassigned request is visible, a mis-tagged one is not.

This skill decides where a request goes, never whether it gets built. It does not set or
change roadmap priority, close a request, or reply to whoever raised it
([ontology record](../../ontologies/product/feature-request-triage.md);
[the rule that holds the customer boundary](../../governance/constitution/no-agent-contacts-a-customer.md)).

## Harness requirements
- The governed pre-provisioning baseline for triage latency and attribution
  completeness: [memory/triage-baseline.md](../../memory/triage-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the support-ticket system, CRM opportunities and their notes, and the
  customer-success team's check-in notes.
- Write access to the product tracker limited to creating items, editing tags and
  assignees, and adding duplicate links and triage notes.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. It is `reversible-write` because
  every write lands on an internal tracker item and is undone by retagging or
  unlinking, and nothing it writes reaches the person who raised the request. Giving it
  the ability to reply to a requester, close a request, or change priority would make it
  track 2, and the classification and Owner's Card would have to change first.
- Read-only access to the three source systems is a hard requirement, not a preference.
  A deployment that lets it edit CRM records breaks the claim above.

## Memory row
- **Reads:** the pre-provisioning triage baseline, and the at-risk-renewal records, so a
  request from an at-risk account carries that context into the tracker item.
- **Writes:** a weekly note recording how many requests were filed, deduplicated, and
  left unassigned (observed provenance).
- **Run-only:** the per-request candidate-duplicate scores.

## Portability check

*If I had to move this skill tomorrow, what would break?* The tracker, support-system,
and CRM connectors; the governed baseline record; the theme-to-manager ownership map the
assignment step reads; and the confirmation gate named in the Owner's Card.
```

- [ ] **Step 5: Create `demo/skills/feature-request-triage/owner-card.md`:**

```markdown
---
owner: Dana Whitfield
backup_owner: Jae-won Park
job: File, deduplicate, and route each week's feature requests to the product manager who owns the theme
action_class: reversible-write
allowed_actions: read support tickets, CRM opportunity and check-in notes, and customer-success submissions; create tracker items; set themes, tags, and assignees; add duplicate links and triage notes
proposed_only_actions: merge two existing tracker items as duplicates after the owning product manager confirms
forbidden_actions: set or change roadmap priority; close a request; reply to the person who raised a request; edit CRM records
pause_condition: the tracker or the CRM is unreachable; a request matches no existing theme and no owning product manager; the theme-to-manager ownership map is stale or missing
retirement_condition: the tracker ships deduplication and attribution the team trusts more, or requests stop arriving through three separate systems
source_of_truth: The product tracker for what is already known; the CRM for account and contract-value attribution
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; near-duplicate requests written in different vocabulary can be filed twice, which is why the weekly note reports the unassigned and duplicate counts
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days with its asking accounts attached, measured against the pre-provisioning baseline of nine business days' median latency and forty-four of one hundred and forty-one requests filed on time
evidence_required: The weekly triage note with filed, deduplicated, and unassigned counts, and the per-request duplicate links
sources_must_not_use: A product manager's recollection or a chat thread as evidence that a request is already tracked
review_sample: The owning product manager confirms theme and duplicate link on every request reaching their queue; Dana Whitfield reviews the unassigned pile weekly
---
# Owner's Card — Feature-request triage

**Dana Whitfield** owns this skill; **Jae-won Park** is the backup. It routes requests
and stops there — it may not set priority, close a request, or reply to whoever raised
it. Merging two existing items is proposed-only and waits on the owning product manager.

The boundary is what keeps this skill track 1: every write lands on an internal tracker
item and is undone by retagging or unlinking, and nothing reaches the requester. If it
is ever given a path to the requester or the ability to close requests, it becomes an
external-side-effect skill and this card must be rewritten before that ships.

It leaves what it cannot place rather than guessing, because an unassigned request is
visible and a mis-tagged one is not. The product manager's confirmation on each request
is the review gate; Dana Whitfield's weekly pass over the unassigned pile is the quality
check.
```

- [ ] **Step 6: Create `demo/skills/onboarding-orchestration/SKILL.md`:**

```markdown
---
name: onboarding-orchestration
description: Provision a new Umbercress hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
baseline: memory/onboarding-baseline.md
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Onboarding orchestration

Provision every new hire before their start date: create standard-role accounts, order
approved standard equipment, send the day-one schedule, and notify the hiring manager
and the buddy. Work from the signed offer and the IT intake form, and record every
access in the IT provisioning tracker as it lands.

Pause rather than improvise. A non-standard role, a non-standard access request, or
missing intake data stops and routes to Ruth Okafor; a contractor-to-employee conversion
routes to outside counsel first. On day one the hiring manager confirms the completed
checklist against the hire's actual readiness
([ontology record](../../ontologies/people-hr/onboarding-orchestration.md)).

## Harness requirements
- The governed pre-provisioning baseline for time-to-day-one-ready and day-one
  readiness: [memory/onboarding-baseline.md](../../memory/onboarding-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read/write access to the HR information system, the IT provisioning tracker, and the
  standard-role account-provisioning systems.
- Permission to order approved standard equipment and to send calendar invites and
  onboarding messages to people inside the company.
- No permissions for non-standard access grants, discretionary spend, compensation,
  offers, or record deletion (see the Owner's Card).

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This is the one Umbercress package on **track 2**: it creates accounts, spends money
  on equipment, and sends messages, and none of that is undone by editing a document.
- This package ships no runtime action-class hook of its own. Its external-side-effect
  gate is a review instruction on every harness — a person confirms before accounts are
  created, equipment is ordered, or messages go out. The engine's fixed action-class
  gate is where runtime enforcement lives when a company installs it.

## Memory row
- **Reads:** the pre-provisioning onboarding baseline (time-to-day-one-ready).
- **Writes:** an onboarding-completed note per hire (observed provenance).
- **Run-only:** the per-run checklist state, which is not persisted to org memory.

## Portability check

*If I had to move this skill tomorrow, what would break?* The HR information system, IT
tracker, account-provisioning, equipment-ordering, calendar, and messaging connectors;
the governed baseline record; and the day-one confirmation gate named in the Owner's
Card.
```

- [ ] **Step 7: Create `demo/skills/onboarding-orchestration/owner-card.md`:**

```markdown
---
owner: Ruth Okafor
backup_owner: Priya Raman
job: Provision every new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
allowed_actions: create standard-role accounts in approved systems and record status in the IT provisioning tracker; order approved standard equipment; send the day-one schedule; notify the hiring manager and the buddy
proposed_only_actions: grant a non-standard system access after Ruth Okafor approves; convert a contractor to an employee after outside counsel reviews
forbidden_actions: approve compensation; sign offer letters; delete employee records; contact anyone outside the company
pause_condition: the HR information system or the IT tracker is unreachable; required intake data is missing; a non-standard role or access is requested; a contractor-to-employee conversion is in scope
retirement_condition: onboarding moves to a workflow inside the HR information system that the team trusts more
source_of_truth: The HR information system record for the hire; the IT provisioning tracker for access state
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package, so every harness relies on the human review gate for external side effects; an account created against a stale intake form looks identical to a correct one until day one
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every new hire is day-one-ready — accounts, equipment, and schedule — before their start date, measured against the pre-provisioning baseline of five business days' median time-to-ready and five of nine hires ready on the first morning
evidence_required: The completed onboarding checklist with per-item timestamps, and the provisioning log showing who approved each non-standard access
sources_must_not_use: A personal email account or a chat thread as a source of truth for an access grant
review_sample: The hiring manager confirms every checklist on day one; Ruth Okafor spot-checks one onboarding a week against the provisioning log
---
# Owner's Card — Onboarding orchestration

**Ruth Okafor** owns this skill; **Priya Raman** is the backup — at twenty people, one
person runs People operations and the CEO is the fallback, which is worth writing down
rather than discovering during a holiday.

It provisions against the HR information system record and pauses non-standard roles or
access to Ruth Okafor, and contractor conversions to outside counsel. It may *propose*
those exceptions and never perform them. It may never touch compensation, offers, or
record deletion, and it may not contact anyone outside the company.

This is the company's only track-2 skill, so the card carries the full evidence trio:
what the run must produce, what it may never treat as a source, and who reads a sample.
The hiring manager's day-one confirmation is the review gate. It should be retired once
the HR information system does this natively and the team trusts it more.
```

- [ ] **Step 8: Create `demo/skills/performance-review-prep/SKILL.md`:**

```markdown
---
name: performance-review-prep
description: Assemble an attributed evidence pack for each review conversation so the manager arrives with the record in front of them
action_class: reversible-write
provisioned: yes
baseline: memory/review-prep-baseline.md
ontology: ontologies/people-hr/performance-review-prep.md
---
# Performance-review prep

For each employee in the cycle, assemble an evidence pack for their manager: goals
against recorded outcomes, submitted peer feedback grouped by theme with every
attribution intact, and the previous cycle's commitments with their status. File it in
the review workspace one week before the review conversation. Every item links to the
submission it came from.

**Gather and stop.** This skill does not rate, rank, score, summarize the evidence into
a verdict, or draft any assessment language. Evaluating a person is a human-owned
decision, and it is not a matter of instruction: the rule at
[writing a performance assessment is a human-owned decision](../../governance/constitution/performance-assessment-is-human-owned.md)
sits on the human-decision rung and refuses the request when it is made, naming its
owner and the appeal path.

Halt rather than fill a gap. Missing goals, fewer than two peer submissions, or an
employee who changed manager mid-cycle stops the pack and routes to Ruth Okafor. Peer
feedback is carried verbatim; paraphrasing it is the failure the pack format exists to
stop ([ontology record](../../ontologies/people-hr/performance-review-prep.md)).

## Harness requirements
- The governed pre-provisioning baseline for pack lead time and evidence completeness:
  [memory/review-prep-baseline.md](../../memory/review-prep-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the HR information system, the goal tracker, peer-feedback
  submissions, and the previous cycle's records.
- Write access to the review workspace location where packs are filed, and nowhere
  else.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. It is `reversible-write` on the
  mechanism: it files a document that a manager fetches, nothing is sent, nothing
  reaches the employee, and a wrong pack is corrected by regenerating it before the
  conversation. The care in this activity lives in its *scope*, not in its action class
  — which is why the boundary is written into the card's forbidden actions and into a
  constitution rule, where it can be enforced rather than merely intended.
- Giving this skill a path to the employee, or the ability to write into the review
  record itself, would make it track 2 and would need the card rewritten first.

## Memory row
- **Reads:** the pre-provisioning review-prep baseline (pack lead time, attribution
  completeness).
- **Writes:** a per-cycle note recording how many packs were assembled and how many
  halted for missing evidence (observed provenance).
- **Run-only:** the per-employee source-document extracts behind the pack.

## Portability check

*If I had to move this skill tomorrow, what would break?* The HR information system,
goal-tracker, and peer-feedback connectors; the governed baseline record; the review
workspace write location; the manager confirmation gate named in the Owner's Card; and
the constitution rule that keeps the assessment itself out of scope.
```

- [ ] **Step 9: Create `demo/skills/performance-review-prep/owner-card.md`:**

```markdown
---
owner: Ruth Okafor
backup_owner: Priya Raman
job: Assemble an attributed evidence pack for each review conversation one week ahead
action_class: reversible-write
allowed_actions: read the HR information system, the goal tracker, peer-feedback submissions, and the previous cycle's records; assemble and file the evidence pack in the review workspace; group peer feedback by theme with attribution intact
proposed_only_actions: flag an employee's pack as incomplete and propose which evidence is missing, for Ruth Okafor to resolve
forbidden_actions: rate, rank, or score an employee; summarize the evidence into a verdict or a recommendation; draft or edit assessment language; paraphrase a peer submission; share a pack with anyone other than the employee's manager
pause_condition: an employee has no recorded goals; fewer than two peer submissions have been received; the employee changed manager mid-cycle; the goal tracker or the feedback system is unreachable
retirement_condition: reviews stop starting from an evidence pack, or the HR information system assembles one the team trusts more
source_of_truth: The goal tracker for goals and outcomes; peer-feedback submissions verbatim, never paraphrased
review_cadence: each review cycle, and after any change to what the pack contains
known_failure_modes: no runtime action-class hook ships with this package; a pack that silently omits a late peer submission looks identical to a complete one, which is why a pack with fewer than two submissions halts instead of shipping short
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every employee in the cycle has an attributed evidence pack in their manager's hands one week before the conversation, measured against the pre-provisioning baseline of eleven days' median lead time and six of nineteen packs delivered a week ahead
evidence_required: The pack itself with a link from every item to the submission it came from, and the halt log for any employee whose pack did not ship
sources_must_not_use: A manager's recollection, a chat thread, or a paraphrase of a peer submission as evidence of anything
review_sample: The employee's manager reads and confirms every pack before the conversation; Ruth Okafor reviews two packs a cycle for attribution integrity
---
# Owner's Card — Performance-review prep

**Ruth Okafor** owns this skill; **Priya Raman** is the backup. It gathers the record
for a review conversation and stops. It may not rate, rank, score, summarize into a
verdict, or draft assessment language — those are the same act under four names, and
all four are forbidden here.

That boundary is not left to good behaviour. The rule at
[writing a performance assessment is a human-owned decision](../../governance/constitution/performance-assessment-is-human-owned.md)
sits on the human-decision rung and refuses the request at the moment it is made, naming
Priya Raman as the appeal. Restraint that lives only in a card is a hope; restraint that
lives in a rule is machinery.

Peer feedback travels verbatim with its attribution, because the whole point of a pack
is that the manager reads what was actually written. The pack halts rather than shipping
short: a pack missing a late submission looks exactly like a complete one, and the
person it is about cannot tell the difference either.
```

- [ ] **Step 10: Gate + the drift-check probe (a deliberate red, then revert)**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

Now prove the demo's cards are actually being checked rather than merely present. "Zero findings" from a check that never reached `demo/skills/` looks identical to "zero findings" from clean content, so plant a violation:

```bash
python3 - <<'PY'
import re, subprocess, sys, pathlib
card = pathlib.Path("demo/skills/renewal-prep/owner-card.md")
orig = card.read_text()
card.write_text(orig.replace("owner: Marcus Bell", "owner: Nobody Atall", 1))
out = subprocess.run([sys.executable, "scripts/validate.py", "."],
                     capture_output=True, text=True).stdout
card.write_text(orig)
hits = [l for l in out.splitlines() if "demo/skills/renewal-prep" in l]
print("PLANTED-VIOLATION FINDINGS:", len(hits))
for l in hits:
    print("   ", l)
assert any("drifts from ontology accountable_owner" in l for l in hits), \
    "the demo instance is NOT being checked — the owner drift check never fired"
print("OK: demo/skills/ is governed by _check_owner_cards_instance")
PY
```

Expected: at least one line containing `card owner 'Nobody Atall' drifts from ontology accountable_owner 'Marcus Bell'`, then `OK: demo/skills/ is governed…`. **If this prints zero findings, stop** — the card content is not being validated and everything after this is unverified.

Then re-run `python3 scripts/validate.py .` and confirm it is back to `0 error(s), 7 warning(s)` — the probe must leave no trace.

- [ ] **Step 11: Commit**

```bash
git add demo/skills
git commit -m "feat(demo): four Umbercress work packages with their Owner's Cards

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The demo constitution

**Files:** Create `demo/governance/README.md`, `demo/governance/changelog.md`, and three rules under `demo/governance/constitution/`.

- [ ] **Step 1: Create `demo/governance/README.md`:**

```markdown
# Umbercress — governance

Three rules Umbercress kept, each one compiled from a ritual somebody named. The engine
documents the compiler ([governance/README.md](../../governance/README.md)); this
directory is the output for one company.

| Rule | Rung | Governs |
|---|---|---|
| [Every recurring meeting names a decision](constitution/every-meeting-names-a-decision.md) | reminder (3) | Scheduling a recurring meeting |
| [No agent contacts a customer](constitution/no-agent-contacts-a-customer.md) | hard-block (4) | Anything that would reach a customer |
| [Writing a performance assessment is a human-owned decision](constitution/performance-assessment-is-human-owned.md) | human-decision (5) | Evaluating a person |

The rungs are the point. A reminder nudges and gets out of the way. A hard block stops
the action. A human-owned decision never terminates in automation at all — which is why
that rule carries a named appeal path. There is no rung six.

## What is runnable here

One of the three ships as working machinery:
[the meeting challenger](reminders/meeting-challenger/README.md) is a real Claude Code
hook that fires the reminder rule at the moment somebody schedules a recurring meeting.
It is hand-authored and copied, never generated — the interview does not write hooks.
The other two rules are typed records that the Owner's Cards and review gates enforce.

## The changelog

[changelog.md](changelog.md) is the append-only index of changes an agent applied to a
track-1 skill body without asking. It is empty because nothing has been auto-applied
yet, which is the honest state of a company that just switched this on.
```

- [ ] **Step 2: Create `demo/governance/changelog.md`:**

```markdown
# Umbercress governance changelog

Append-only. One line per auto-applied change to a track-1 skill body, so the
maintainer's reconciliation pass is one glance rather than a diff hunt. Everything else
— rules, Owner's Cards, descriptions, governance frontmatter, any track-2 skill —
escalates to a proposal instead and never appears here.

Format: `- date | skills/<name>/SKILL.md | one-line gist | agent | commit sha`

<!-- entries below, newest last -->
```

> The trailing HTML comment is deliberate: `_check_changelog_instance` only parses lines beginning `- `, so a comment is inert, and it tells the next writer where to append.

- [ ] **Step 3: Create `demo/governance/constitution/every-meeting-names-a-decision.md`:**

```markdown
---
owner: Priya Raman
rung: reminder
action_class: reversible-write
sunset: 2027-06-30
value: A recurring meeting spends the company's scarcest resource, so it should exist to make a decision somebody owns
value_owner: Priya Raman
runtime_check: When an agent schedules or extends a recurring meeting, it is reminded — not blocked — to state the decision the series exists to make and the person who owns that decision. The reminder ships as a Claude Code hook and as a review-gate instruction elsewhere
runtime_check_owner: Priya Raman
human_appeal: Anyone who thinks the reminder is wrong for a given series says so in the invite and schedules it anyway. Nobody at Umbercress has to justify a meeting to an agent
human_appeal_owner: Priya Raman
repeals: The Monday all-hands status round
reassigned_to: Priya Raman
ritual: The Monday all-hands status round — thirty minutes, everyone, no decision on the agenda
scarcity: Uninterrupted engineering and support time
surviving_job: Making sure the whole company hears what it needs to hear, which moved to a written Monday note Priya Raman posts
---
# Every recurring meeting names a decision

**The rule.** A recurring meeting states the decision it exists to make and the person
who owns that decision. If it has neither, it is a broadcast, and a broadcast is cheaper
written down.

**Why it sits at the reminder rung.** The failure this catches is drift, not danger. A
meeting that has outlived its decision is a slow tax, and the fix is a person noticing —
so the machinery nudges at the moment of scheduling and then gets out of the way. Making
this a hard block would put an agent in charge of the company's calendar, which is a
larger transfer of authority than the problem justifies.

**What it repealed.** The Monday all-hands status round. Its surviving job — making sure
the whole company hears what it needs to hear — moved to a written Monday note, and
Priya Raman owns it; a ritual is not repealed until its surviving job has somewhere to
live. Engineering had already run this argument once and written down what it cost:
[the move to asynchronous standups](../../memory/async-standups.md) records both the
saved hours and the incidental conversation that was given up.

**Appeal.** Say so in the invite. The reminder is a question, not a gate.

**The machinery.** [The meeting challenger](../reminders/meeting-challenger/README.md)
is the runnable form of this rule.
```

- [ ] **Step 4: Create `demo/governance/constitution/no-agent-contacts-a-customer.md`:**

```markdown
---
owner: Marcus Bell
rung: hard-block
action_class: external-side-effect
sunset: 2027-06-30
value: A customer hears from a person at Umbercress, not from a process
value_owner: Priya Raman
runtime_check: No skill may send a message, ticket reply, or post that reaches a customer. The renewal brief is filed in the customer-success workspace and the triage queue lives in the product tracker; both are internal documents that a person acts on. On Claude Code the action-class gate blocks outbound sends, and everywhere else the same rule ships as a review-gate instruction
runtime_check_owner: Marcus Bell
human_appeal: A CSM who needs something to reach a customer faster than a person can send it raises it with Marcus Bell, who either sends it themselves or approves a written exception naming the message and the recipient
human_appeal_owner: Marcus Bell
ritual: Every customer-facing message being drafted and sent by the account's own CSM
scarcity: CSM time — sixty accounts across three people
surviving_job: Deciding what a customer is told, and saying it in a named person's voice
---
# No agent contacts a customer

**The rule.** An agent may assemble anything that helps a person talk to a customer. It
may not talk to the customer. Messages, ticket replies, and posts that leave the company
are sent by a named person, every time.

**Why it sits at the hard-block rung.** A message to a customer cannot be recalled, and
the harm is not that it is wrong — it is that it is nobody's. Umbercress sells to
operators who know their CSM by name; a message that turns out to have come from a
process costs more than the time it saved. Blocking is proportionate because the
workaround is trivial: a person presses send.

**What it makes possible.** This rule is why
[renewal preparation](../../skills/renewal-prep/SKILL.md) and
[feature-request triage](../../skills/feature-request-triage/SKILL.md) are track-1
skills at all. Their writes stay inside internal documents, so a mistake is corrected by
rewriting a file. Remove this boundary and both become external-side-effect skills whose
Owner's Cards would have to be rewritten before they shipped.

**Appeal.** Marcus Bell can send it, or approve a written exception naming the message
and the recipient. The exception is written down so that a pattern of exceptions is
visible rather than gradual.
```

- [ ] **Step 5: Create `demo/governance/constitution/performance-assessment-is-human-owned.md`:**

```markdown
---
owner: Ruth Okafor
rung: human-decision
action_class: high-risk
sunset: 2027-06-30
value: Judging a person's work is a judgment a person owns and answers for
value_owner: Priya Raman
runtime_check: The review-prep skill assembles the evidence pack and stops. A request to rate, rank, score, summarize the evidence into a verdict, or draft assessment language is refused at the moment it is made, and the refusal names this rule, its owner, and the appeal path rather than simply declining
runtime_check_owner: Ruth Okafor
human_appeal: A manager who believes the boundary is wrong for their case raises it with Priya Raman, who decides within one business day and records the decision. The answer can be yes about the process and is never yes about the assessment
human_appeal_owner: Priya Raman
ritual: Managers assembling the evidence and writing the first draft of the assessment in one sitting, with no record of which was which
scarcity: Manager attention during review season
surviving_job: Forming and writing the assessment itself, which stays human permanently
---
# Writing a performance assessment is a human-owned decision

**The rule.** An agent may gather, organize, and attribute the evidence for a
performance review. It may not evaluate. Rating, ranking, scoring, summarizing the
evidence into a verdict, and drafting assessment language are the same act under five
names, and all five stop here.

**Why it sits at the human-decision rung.** Evaluating a person is `high-risk`: it
changes what happens to somebody, and it cannot be undone by editing a file. So it can
never terminate in automation. **There is no rung six** — the agent's authority ends at
the evidence, and a person decides. That is also why this rule carries a named appeal
path: a block with no appeal is a dead end, and dead ends get routed around.

**What it protects, concretely.** The pack that
[performance-review prep](../../skills/performance-review-prep/SKILL.md) assembles is
deliberately shaped to be useful and not conclusive: goals against outcomes, peer
feedback verbatim and attributed, last cycle's commitments with their status. Ask it for
a rating and it will not produce one — not because it was asked nicely in a prompt, but
because this rule refuses, names Ruth Okafor as the owner, and points at Priya Raman as
the appeal.

**Appeal.** Priya Raman, within one business day, recorded. A manager can win an
argument about the *process* — what evidence belongs in the pack, how it is grouped. No
one wins the argument about who writes the assessment.
```

- [ ] **Step 6: Gate + the constitution probe (a deliberate red, then revert)**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Three rules, zero findings — every active rule carries its owner, all four owned objects, ritual provenance, a future sunset, and (for the high-risk one) an appeal path with an owner.

Now prove `_check_constitution_instance` reaches `demo/`, and that the safety spine is live on it. Blank the appeal on the high-risk rule and confirm the no-rung-six ERROR fires:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
rule = pathlib.Path("demo/governance/constitution/performance-assessment-is-human-owned.md")
orig = rule.read_text()
broken = "\n".join(l for l in orig.split("\n") if not l.startswith("human_appeal:"))
rule.write_text(broken)
out = subprocess.run([sys.executable, "scripts/validate.py", "."],
                     capture_output=True, text=True).stdout
rule.write_text(orig)
hits = [l for l in out.splitlines() if "demo/governance/constitution" in l]
print("PLANTED-VIOLATION FINDINGS:", len(hits))
for l in hits:
    print("   ", l)
assert any("there is no rung six" in l for l in hits), \
    "the demo constitution is NOT being checked — the safety spine never fired"
print("OK: demo/governance/constitution/ is governed by _check_constitution_instance")
PY
```

Expected: two findings (the missing four-object field and the no-rung-six ERROR), then `OK: …`. **Zero findings means the demo's rules are unchecked** — stop and investigate.

Also confirm orphan-prohibition is genuinely exercised rather than merely present, by breaking the reassignment on the repealing rule:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
rule = pathlib.Path("demo/governance/constitution/every-meeting-names-a-decision.md")
orig = rule.read_text()
rule.write_text("\n".join(l for l in orig.split("\n") if not l.startswith("reassigned_to:")))
out = subprocess.run([sys.executable, "scripts/validate.py", "."],
                     capture_output=True, text=True).stdout
rule.write_text(orig)
assert any("orphan-prohibition" in l for l in out.splitlines()), \
    "the repeal branch never ran — 'repeals:' is not being read as a declared repeal"
print("OK: orphan-prohibition fires on real content for the first time")
PY
```

Re-run `python3 scripts/validate.py .` and confirm `0 error(s), 7 warning(s)`.

- [ ] **Step 7: Commit**

```bash
git add demo/governance/README.md demo/governance/changelog.md demo/governance/constitution
git commit -m "feat(demo): the Umbercress constitution — three rules on three rungs

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The meeting-challenger runnable exemplar (#8 item 3)

**Files:** Create `demo/governance/reminders/meeting-challenger/{meeting_challenger.py,README.md}`; modify `tests/test_validate.py`.

- [ ] **Step 1: Create `demo/governance/reminders/meeting-challenger/meeting_challenger.py`:**

```python
#!/usr/bin/env python3
"""Umbercress meeting challenger — a worked, runnable rung-3 (reminder) rule.

Pairs with governance/constitution/every-meeting-names-a-decision.md: when an agent
schedules or extends a recurring meeting, remind it to name the decision the series
exists to make and the person who owns that decision.

RUNG 3 IS NOT RUNG 4. A reminder does not change what happens. This hook emits
`permissionDecision: "defer"` — Claude Code's "use the normal permission flow" — and
carries the reminder in `additionalContext` (for the agent) and `systemMessage` (for
the person). It never denies and never auto-approves. A reminder that blocks is rung
inflation: machinery claiming more authority than the rule was granted.

IT FIRES ON SHAPE, NEVER ON CONTENT. It does not try to decide whether an invite
"already names a decision" — that would be a guess about text nobody controls, with an
unbounded supply of ways to be wrong. It nudges every recurring-meeting-shaped call and
says so; a person decides whether the nudge applies.

Hand-authored and copied, never generated. Hooks are a Claude-Code-only surface; on
Codex / Cursor / Gemini this file is silently ignored and the same rule ships as the
review-gate paragraph in README.md.

Python 3 standard library only.
"""
import json
import re
import sys

RULE = "governance/constitution/every-meeting-names-a-decision.md"

REMINDER = (
    "Umbercress rule (rung 3, reminder): every recurring meeting names the decision it "
    "exists to make and the person who owns that decision. This is a reminder, not a "
    "block — the meeting still gets scheduled. If this series has no decision and no "
    "owner, say so in the invite, or send a written note instead. "
    "Rule: %s. Owner: Priya Raman. Disagree? Say so in the invite." % RULE
)

# Two independent signals, both required: the call must look like a MEETING and like it
# RECURS. Either alone is too broad — 'weekly report' is not a meeting, and a one-off
# invite is not the ritual this rule is about.
_RECURRING = re.compile(
    r"\b(recurring|recurrence|repeats?|repeating|weekly|bi-?weekly|fortnightly|monthly|"
    r"daily|standing|series|every\s+(?:week|month|other\s+week|"
    r"mon|tues?|wednes|thurs?|fri)\w*)\b", re.I)
_MEETING = re.compile(
    r"\b(meeting|invite|invitation|stand-?up|sync|check-?in|all-?hands|retro\w*|"
    r"one-on-one|1:1|calendar\s+event)\b", re.I)


def _text(tool_name, tool_input):
    """Flatten a tool call into one searchable string: the tool's name plus every
    string value in its input, one level deep plus strings inside lists. Anything
    unreadable contributes nothing rather than raising."""
    parts = []
    if isinstance(tool_name, str):
        parts.append(tool_name)
    if isinstance(tool_input, dict):
        for value in tool_input.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(v for v in value if isinstance(v, str))
    return "\n".join(parts)


def challenges(tool_name, tool_input):
    """Pure: does this tool call look like scheduling or extending a recurring meeting?"""
    blob = _text(tool_name, tool_input)
    if not blob:
        return False
    return bool(_RECURRING.search(blob) and _MEETING.search(blob))


def decide(payload):
    """Map a PreToolUse payload to a reminder dict, or None for 'say nothing'.

    Unreadable input is SILENT here — the opposite of the action-class gate, which
    escalates to 'ask'. That gate stands between an agent and a consequential action,
    so its failure mode must be loud. This is a nudge about a calendar entry: turning
    an unreadable payload into a prompt would make a rung-3 rule interrupt people on
    input it never understood. A missed nudge is recoverable; a reminder that becomes
    a gate is not the rule the company agreed to.
    """
    if not isinstance(payload, dict):
        return None
    if not challenges(payload.get("tool_name"), payload.get("tool_input")):
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            # 'defer' = use the normal permission flow. The reminder changes what the
            # agent and the human KNOW, never what they are ALLOWED to do.
            "permissionDecision": "defer",
            "additionalContext": REMINDER,
        },
        # A universal field, so the person sees the reminder regardless of how
        # additionalContext is rendered alongside a deferred decision.
        "systemMessage": REMINDER,
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # unreadable input: a reminder stays silent rather than interrupting
    reminder = decide(payload)
    if reminder is not None:
        print(json.dumps(reminder))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Create `demo/governance/reminders/meeting-challenger/README.md`:**

```markdown
# The meeting challenger — one runnable rule

This is the one piece of Umbercress's constitution that is **working machinery** rather
than a typed record. It is the runnable form of
[every recurring meeting names a decision](../../constitution/every-meeting-names-a-decision.md),
a rung-3 rule: when an agent schedules or extends a recurring meeting, it gets reminded
to name the decision the series exists to make and who owns it.

It is **hand-authored and copied, never generated**. groundwork's interview does not
write hooks. This exists so the shape of a runnable rule is concrete and copyable —
take it, change the rule text, ship your own.

## What a rung-3 hook looks like

The five-rung ladder is `value` → `instruction` → `reminder` → `hard-block` →
`human-decision`, and the rung a rule sits on should be visible in what its machinery
*does*:

| Rung | What the hook returns |
|---|---|
| hard-block (4) | `permissionDecision: "deny"` — the action does not run |
| **reminder (3)** | **`permissionDecision: "defer"` plus the reminder text** — the action runs as it otherwise would; only what the agent and the human *know* changes |

A reminder that returns `"ask"` has quietly become a gate. That is rung inflation, and
it is how a company ends up with machinery nobody agreed to.

## Install (Claude Code, in your company repo)

Merge this into `.claude/settings.json`, keeping any hooks already there:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/governance/reminders/meeting-challenger/meeting_challenger.py\"",
            "timeout": 30,
            "statusMessage": "Checking the meeting rule..."
          }
        ]
      }
    ]
  }
}
```

The matcher is `*` on purpose: a meeting gets scheduled through whatever calendar tool
the company has connected, and the hook decides from the call rather than from a tool
name it would have to guess.

## Verify it

A recurring-meeting-shaped call gets the reminder:

```
echo '{"hook_event_name":"PreToolUse","tool_name":"calendar_create_event","tool_input":{"title":"Weekly ops sync","recurrence":"weekly"}}' \
  | python3 governance/reminders/meeting-challenger/meeting_challenger.py
```

You should see JSON containing `"permissionDecision": "defer"` and the reminder text.
Anything else prints nothing at all:

```
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"npm test"}}' \
  | python3 governance/reminders/meeting-challenger/meeting_challenger.py
```

(The paths above are written as they resolve inside a company repo, where this
directory sits at the root. Inside this engine repo, prefix them with `demo/`.)

## Install (Codex / Cursor / Gemini CLI)

These harnesses **silently ignore** hooks — no warning, no rejection. Copy this
paragraph into the harness's instruction file instead:

> **Umbercress meeting rule.** Before scheduling or extending a recurring meeting,
> state the decision the series exists to make and the person who owns that decision.
> If it has neither, it is a broadcast — send a written note instead. This is a
> reminder, not a block: if the person disagrees, schedule the meeting.

Same rule, weaker enforcement. That asymmetry is stated rather than papered over, and
cross-harness runtime parity is a named later graduation, not something V1 claims.

## What it does and does not do

- **Does:** remind, on every tool call that looks like scheduling or extending a
  recurring meeting, and stay completely silent otherwise.
- **Does:** leave the permission outcome exactly as it found it.
- **Does not:** judge whether an invite already names a decision. It fires on *shape*,
  never on content — guessing at the meaning of text nobody controls has an unbounded
  supply of ways to be wrong, and a reminder that fires on a well-formed invite is
  cheap while a reminder suppressed by a bad guess is invisible.
- **Does not:** run anywhere in this repository. Nothing here registers it; it is an
  artifact to copy into a company repo. `demo/` is a worked example, not an installed
  system.
- **Does not:** import anything outside the Python standard library — checked by the
  repo's test suite along with every other shipped script.
```

- [ ] **Step 3: Widen the zero-dependency guarantee to cover it.** In `tests/test_validate.py`, replace `test_shipped_hook_scripts_only_stdlib` (currently scanning only `governance/hooks/*.py`) with a repo-wide scan. This is a rename plus a wider glob — **no new test**, so the suite stays at 610.

Replace this method:

```python
    def test_shipped_hook_scripts_only_stdlib(self):
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections",
                   "pathlib", "datetime", "subprocess", "unicodedata", "json"}
        hooks_dir = REPO / "governance" / "hooks"
        if not hooks_dir.is_dir():
            self.skipTest("no shipped hooks")
        for py in sorted(hooks_dir.glob("*.py")):
            tree = ast.parse(py.read_text())
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        mods.add(n.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertEqual(mods - allowed, set(), "%s imports non-stdlib: %s" % (py.name, mods - allowed))
```

with this one:

```python
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
```

> `shlex` joins the allowed set because the repo-wide scan now includes `scripts/validate.py`, which already imports it (the first test in this class allows it). Everything else is unchanged.

- [ ] **Step 4: Prove the hook works, in both directions**

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"calendar_create_event","tool_input":{"title":"Weekly ops sync","recurrence":"weekly"}}' \
  | python3 demo/governance/reminders/meeting-challenger/meeting_challenger.py
```
Expected: one JSON line containing `"permissionDecision": "defer"`, `"additionalContext"`, `"systemMessage"`, and the rule path.

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"npm test"}}' \
  | python3 demo/governance/reminders/meeting-challenger/meeting_challenger.py ; echo "[exit $?]"
```
Expected: **no output at all**, `[exit 0]`.

```bash
printf 'not json' | python3 demo/governance/reminders/meeting-challenger/meeting_challenger.py ; echo "[exit $?]"
```
Expected: **no output**, `[exit 0]` — unreadable input is silent for a reminder.

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo weekly standup invite"}}' \
  | python3 demo/governance/reminders/meeting-challenger/meeting_challenger.py
```
Expected: the reminder JSON — the hook reads the *call*, not the tool name. A false positive here is the documented, cheap direction.

- [ ] **Step 5: Prove the zero-dep scan actually reaches the new script** (deliberate red, then revert)

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
p = pathlib.Path("demo/governance/reminders/meeting-challenger/meeting_challenger.py")
orig = p.read_text()
p.write_text(orig.replace("import json", "import json\nimport requests", 1))
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestZeroDep.test_shipped_scripts_only_stdlib"],
                   capture_output=True, text=True)
p.write_text(orig)
print(r.stderr.strip().splitlines()[-1])
assert r.returncode != 0, "the zero-dep scan did NOT see the new script"
print("OK: the shipped-script scan covers demo/.../meeting_challenger.py")
PY
```

Expected: `FAILED (failures=1)` then `OK: …`. A pass here would mean the guarantee is still scoped to a directory.

- [ ] **Step 6: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 610 tests`, `OK (skipped=1)` — the count is unchanged because the test was renamed, not added.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Note this includes `check_synthetic_identifiers` reading the `.py` and the fenced JSON — neither carries a domain, phone, or IP.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. `demo/` still has no `groundwork.pin`, so the #18 tripwire stays dormant until 2.3e; every file here is an addition.

- [ ] **Step 7: Commit**

```bash
git add demo/governance/reminders tests/test_validate.py
git commit -m "feat(demo): the meeting-challenger runnable rung-3 exemplar (#8 item 3)

The one worked runnable rule: a Claude Code PreToolUse hook that defers to the
normal permission flow and carries the reminder, because rung 3 changes what
people know, not what they may do. Widens the zero-dep scan from
governance/hooks/ to every shipped script, so the guarantee covers it.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Status honesty and the full gate

**Files:** Modify `demo/README.md`, `AGENTS.md`.

- [ ] **Step 1: Update `demo/README.md`.** Replace the opening paragraph and the "What is here now" / "What is coming" sections with:

```markdown
# demo — the pre-installed example company

A fictional company OS, being filled in slice by slice. When it is complete you will
be able to read it without configuring anything, inspect the shape a company OS takes
before generating your own, and watch the validator run against real content. Today it
holds the canon, the company's ontologies, its org memory, its four work packages, and
its constitution.

Read [canon.md](canon.md) first: it declares the fictional world, and it is also the
allowlist the validator checks every identifier in this directory against.

## What is here now

- `canon.md` — the fictional world and the identifier allowlist.
- [`ontologies/`](ontologies/README.md) — all eight functions' executive views, deep
  records for renewal preparation, feature-request triage, onboarding orchestration,
  and performance-review prep, and finance's three recorded decisions *not* to
  automate.
- `memory/` — the company's org memory: why engineering moved to asynchronous standups
  (and the superseded decision it replaced), two at-risk renewals and what they are
  blocked on, and the four captured baselines.
- [`skills/`](skills/README.md) — the four work packages, each a `SKILL.md` plus an
  Owner's Card naming a real person, citing the baseline captured before it was
  provisioned.
- [`governance/`](governance/README.md) — three rules on three rungs, including the one
  that stops an agent from writing a performance assessment, and
  [one runnable rule](governance/reminders/meeting-challenger/README.md) you can pipe
  JSON into today.

## What is coming

- The 15-minute walkthrough script, the version pin that puts this directory under the
  same governance the validator applies to a real company repo, and one live pending
  proposal.

The walkthrough is not usable yet: there is no script to follow, and the three queries
it will run are not written. Everything above is content you can read and check —
`python3 scripts/validate.py .` from the repository root validates this directory as
its own instance — not a demo you can run.
```

> Leave the "What this is not" section exactly as it is.

- [ ] **Step 2: Update `AGENTS.md`.** Replace the `demo/` bullet under "Built and working" with:

```markdown
- `demo/` — the pre-installed example company (**Umbercress**, ~20 people). Its canon
  declares the fictional world and doubles as the validator's identifier allowlist. Its
  ontologies, org memory, four work packages, and constitution are complete, including
  one runnable rung-3 reminder (#8 item 3). The 15-minute walkthrough and the version
  pin are still to come — `demo/README.md` says what is there today.
```

And in "Not built yet", replace the `demo/` walkthrough bullet with:

```markdown
- `demo/` walkthrough — the 15-minute 3-query script. The company's content is in place;
  the script that walks you through it is not written, so there is nothing to follow yet.
```

- [ ] **Step 3: The full gate and the instance probe**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 610 tests`, `OK (skipped=1)`.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0.

Run the instance probe — the demo must be governed as its own instance, not merely present:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
ig = validate.load_gitignore('.')
print("instances:", validate._instance_roots('.', ig))
for name in ("check_ontology", "check_owner_cards", "check_constitution",
             "check_proposals", "check_changelog", "check_memory",
             "check_synthetic_identifiers"):
    fn = getattr(validate, name)
    f = fn('.', ig) if name != "check_memory" else fn('.')
    print("%-28s %d finding(s)" % (name, len(f)))
import os
demo_pkgs = sorted(os.listdir('demo/skills'))
demo_rules = sorted(os.listdir('demo/governance/constitution'))
print("demo skill packages:", demo_pkgs)
print("demo rules:", demo_rules)
assert './demo' in validate._instance_roots('.', ig)
PY
```

Expected: `instances:` contains both `.` and `./demo`; all checks report 0 findings; four skill packages and three rules are listed. Zero findings from a check that never entered `demo/` is indistinguishable from zero findings on clean content — the planted-violation probes in Tasks 1–3 are what tell them apart, and this prints the corpus so a silently empty directory is visible.

- [ ] **Step 4: Commit**

```bash
git add demo/README.md AGENTS.md
git commit -m "docs: demo status — skills and constitution landed, walkthrough still to come

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No `demo/groundwork.pin` and no proposals.** Slice **2.3e**, the capstone: the
  15-minute 3-query script, the pin that makes `demo/` a governed root, and one live
  pending proposal. The pin lands last on purpose — once it exists, every *addition* of
  a demo skill or rule is an escalating change the #18 tripwire requires a matching
  proposal for, so authoring this slice under the pin would mean a proposal per file.
- **No walkthrough script.** Query 3's rung-5 block is *made possible* here — the rule
  exists and the skill's boundary is written — but the query that fires it is 2.3e's.
- **No validator changes.** One test-only change (Task 3 Step 3), flagged as design call
  5. If a check misfires on this content, report it rather than editing it here.
- **No `demo/governance/hooks/`.** `check_hooks` is root-only by design (2.3a); the
  exemplar lives under `reminders/` and makes no registration claim a check could not
  verify.
- **Still open for the maintainer:** three Slice 1.5d-ii deferrals (dot-directory
  classification, case-variant authorization, the path-style nit), the `SKIP_RELPATHS`
  gate-scoping sign-off, the standing re-review rule, and confirmation of the
  `Motion: assist` reading implemented in 2.3c.

## Self-Review

- **Ticket coverage.** #6: all four cards carry the 14-field spine and the track-2 trio,
  the owner and `source_of_truth` drift checks are satisfied by copying the ontology's
  `accountable_owner` and `gate_source_of_truth` verbatim, and every card's
  `success_standard` is drafted *from the captured baseline* as the drafting split
  requires — the numbers in each one come from that skill's baseline record. #8: item 1
  (guided content) is the three typed rules; item 2 (the fixed hook set) is the engine's
  and untouched; **item 3 (one runnable exemplar, compatibility-noted, copy-me, not
  generated) is Task 3**; item 4 (validator strictness) is exercised by the planted-
  violation probes, including no-rung-six and orphan-prohibition. #4: People/HR carries
  the trust story, review prep's evaluation is forbidden on the card *and* in a rule, and
  the rung-5 block is now installable — 2.3e fires it in-query.
- **Design calls surfaced, not buried.** Five, each with the option I rejected and why:
  the rung-3 mechanism (`defer`, not `ask`), the exemplar's location and the absent
  snippet file, review prep's action class, three rules across three rungs with one
  repeal, and the one test-only change. Three of them (2, 3, 5) are places where I chose
  the less convenient option to avoid an unverified claim.
- **Live contract fetched, and it changed the design** (wwf5d §1.3). The Claude Code
  hooks reference was read on 2026-07-28 at its current home (`code.claude.com/docs/en/hooks`;
  `docs.claude.com` now 301s). It confirmed a fourth `permissionDecision` value —
  `defer` — plus `additionalContext` inside `hookSpecificOutput` and a universal
  `systemMessage`. Without that fetch this exemplar would almost certainly have shipped
  as `ask`, which is a rung-4 mechanism wearing a rung-3 label.
- **Anti-hollow probes, in the negative direction.** Four planted violations, each with
  an assertion that *fails* if the check never ran: an owner drift on a demo card, a
  missing appeal path on the high-risk rule, a missing `reassigned_to` on the repealing
  rule, and a non-stdlib import in the new script. The 2.3b lesson is the reason — "this
  valid input passes" is satisfied trivially by a scanner that scans nothing, and only a
  planted violation can tell the two apart. Each probe reverts the file and re-runs the
  gate.
- **Deliberate reds are labelled.** Every probe in Tasks 1–3 makes the gate red on
  purpose. Each is written with its expected finding and an explicit revert, so a red
  mid-slice is not mistaken for a mistake.
- **The invariants are stated as tripwires:** `0 error(s), 7 warning(s)` after every
  task, and `610 tests, OK (skipped=1)` — the test count deliberately does not move,
  because Task 3 renames a test rather than adding one.
- **Placeholder scan:** no TBD/TODO anywhere. All sixteen files are given in full, with
  exact commands and expected output.
- **Pre-empts the recurring findings.** (a) *Non-scalar frontmatter* — every card and
  rule field is a single scalar string; no bare `key:` appears, which would parse as `[]`
  and trip the `_blank` guards. (b) *Alias laundering* — every `baseline:`, `ontology:`,
  and Markdown link is a plain repo-relative literal inside `demo/`; nothing uses `../`
  to climb out of the instance, which `_record_ref_realpath` and the `ontologies/`
  containment check would reject anyway. (c) *Fail-open on malformed input* — the hook's
  unreadable-input path is silence, and the reason that is the strict outcome *for a
  reminder* is written in the docstring where a reviewer will look for it, because the
  opposite choice is correct one directory away in `action_class_gate.py`. (d)
  *Synthetic identifiers* — `check_synthetic_identifiers` scans every file under `demo/`,
  including the `.py` and the fenced JSON; neither contains a domain, a phone-shaped
  number run, or an IP, and the `555-01xx` range is not needed by any file in this slice.
  (e) *Pronouns* — no named person in the canon has stated pronouns, so every reference
  uses they/them or the person's name.
- **Type consistency:** no `validate.py` signatures move. Frontmatter keys match
  `CARD_REQUIRED` + `CARD_TRACK2` and `_RULE_OBJECT_FIELDS` exactly; `action_class`
  values come from `ACTION_CLASSES`; `rung` values come from `RUNGS`.
