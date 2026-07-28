# groundwork V1 — Slice 2.3c: the Umbercress ontologies + org memory — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the demo company its map and its memory. Eight executive views for Umbercress, deep records for the three deep functions (#4: customer success, product, People/HR) plus Finance's *shallow-but-opinionated* `Motion: wait` records, and the org-memory set the 15-minute script reads from — including the **async-standups supersession chain**, which is demo query 1's entire payload.

**Architecture:** `demo/` gains `ontologies/` and `memory/`, which makes it an instance (2.3a), so `check_ontology`, `check_deep_record`, `check_memory`, and `check_synthetic_identifiers` all begin governing it from the first file. No new schema and no validator changes: this slice is content authored against checks that are already live, and its success condition is that ~24 new files add **zero** findings.

**Tech Stack:** Markdown only. No `scripts/validate.py` changes.

## Global Constraints

- **No validator changes.** If demo content trips a check, the content is wrong — fix the content. If a check is genuinely wrong, stop and report it rather than editing it inside a content slice.
- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task. ~24 new files must add nothing. A new WARN is a real finding.
- **#5 severity contract:** deep records for acted-on activities; silence for activities with none. Automation path (`automate`/`build`) requires Substrate, Shape, and all eight Gate fields; `buy`/`hire`/`wait` require only the common core.
- **Instance-relative references** (2.3a): inside `demo/`, a `superseded_by` is `memory/<record>.md`, and an exec-view deep-record link is a bare filename. Nothing may climb out of `demo/`.
- **Canonical exec-view grammar** (2.2a): one table per file, `| Activity | Direction | Deep record |`, delimiter `|---|---|---|`, every row three cells with leading and trailing pipes, no other line in the file carrying a `|`, and no link reference definitions.
- **Everything must trace to the canon** (2.3b): only `umbercress.example`, `555-01xx`, TEST-NET IPs. **Also avoid bare 7- and 10-digit number runs** — the phone extractor matches compact forms, so write money as `$48,000` and identifiers as `UR-2291`, never `4800000` or `5550142`.
- **Dates:** every `review_by` must be in the future (today is 2026-07-28) or the record WARNs and breaks the invariant. Every demo record carries one.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.3b merged and pushed (`6e536c8`; 610 tests, 1 designed skip, gate exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.3c-demo-ontologies
```

---

## Design calls flagged for the maintainer

**1. `Motion: assist` does not exist — and this slice is where that collides.**
Ticket #4 specifies People/HR's second acted-on activity as *"performance-review prep (**Motion: assist** — the skill assembles the evidence pack; evaluation itself is **forbidden** on the Owner's Card)"*. But #5's locked Motion vocabulary is `automate` / `build` / `buy` / `hire` / `wait`, and `MOTIONS` in `validate.py` encodes exactly those five. There is no `assist`. Two resolved tickets, one contradiction, and this is the file that has to pick.

*My reading, and what the plan implements:* `assist` is informal shorthand in a parenthetical, not a sixth verdict. #4 glosses it immediately — "the skill assembles the evidence pack; evaluation itself is forbidden" — which is a **scoping** statement about what the skill may do, not a verdict on build-vs-buy-vs-automate. The Motion ladder answers "how should this work get done?"; "assist" answers "how far may the agent go?", which is the Owner's Card's job. So the record ships `motion: automate`, and #4's actual substance lands where it belongs: the deep record's body says the judgment stays human, and 2.3d's Owner's Card puts *writing or drafting an assessment* in `forbidden_actions`. This is exactly the renewal-prep shape already proven twice in Phase 2.2.

*The alternative, honestly:* add `assist` to `MOTIONS` as a sixth verdict. That is a schema change — it would need a `SCHEMA_VERSION` bump and a migration note under the rule you set in 2.2a, it would need its own pivot semantics (does `assist` require the Describability Gate?), and it would contradict #5's explicit "Motion is the pivot" framing, which sorts activities by *who does the work*, not by *how much rein the agent gets*. I do not recommend it, but it is your vocabulary and this is the moment it gets decided in code rather than in prose.

**2. The demo's executive views deliberately differ from the engine templates.**
Umbercress is a specific 20-person company: founder-led sales rather than a deal desk, no analyst relations, outside counsel rather than a legal team, a fractional CFO. Its activity lists and Directions are its own. That difference is the point — it shows concretely what the "engine templates are a starting map, not a claim about your company" frame in `ontologies/README.md` actually means. A demo that copied the engine's tables would quietly teach the opposite.

**3. Demo records name people; engine records name roles.**
Engine exemplars say `accountable_owner: Head of People` because they are templates. The demo says `accountable_owner: Ruth Okafor` because a company instance has actual people, and the canon names them. This also makes 2.3d's Owner's Card drift checks meaningful on real names. Finance's records name **Priya Raman** — at 20 people the CEO owns spend approval, and the fractional CFO and bookkeeper are unnamed in the canon.

**4. Finance gets three deep records, not empty worksheets.**
#4 says Finance stays "shallow but opinionated — high-risk activities (spend approval, payroll, vendor payments) pre-marked Motion `wait` / work-type `accountability` / high-risk action class, worksheets empty." Read literally, "pre-marked Motion" and "worksheets empty" pull against each other: Motion is a deep field. The resolution the schema already provides is the Motion pivot — a `wait` record carries **only the common core**, no Substrate, Shape, or Describability Gate. That is "opinionated" (a recorded verdict) and "shallow" (four answers) at once, and it makes the demo the second place the non-automation branch runs on real content. "High-risk action class" has no ontology field to live in — no skill exists — so it is stated in each record's body as the reason no skill will be generated.

---

## File Structure

**Create (24 files):**

- `demo/ontologies/README.md`
- `demo/ontologies/{customer-success,product,people-hr,finance,sales,marketing,engineering,legal}/_executive-view.md` — 8 files
- `demo/ontologies/customer-success/renewal-preparation.md`
- `demo/ontologies/product/feature-request-triage.md`
- `demo/ontologies/people-hr/onboarding-orchestration.md`
- `demo/ontologies/people-hr/performance-review-prep.md`
- `demo/ontologies/finance/{spend-approval,payroll-runs,vendor-payments}.md` — 3 files
- `demo/memory/{async-standups,daily-standups,cartwright-renewal-risk,belport-renewal-risk,onboarding-baseline,review-prep-baseline,renewal-prep-baseline,triage-baseline}.md` — 8 files
- `demo/memory/_index.md`

**Modify:** `demo/README.md`, `AGENTS.md`.

---

## Task 1: The eight executive views

**Files:** Create `demo/ontologies/README.md` and eight `_executive-view.md` files

- [ ] **Step 1: Create `demo/ontologies/README.md`:**

```markdown
# Umbercress — ontologies

What each function at Umbercress actually does, and which way the work should move.
One directory per function; each carries an `_executive-view.md`, and the activities
the company chose to act on carry a deep record beside it.

These are **not** the engine's starter templates copied in. Umbercress is a specific
20-person company: sales is founder-led, legal is outside counsel, finance is a
fractional CFO and a bookkeeper. Its map looks like its own company, which is what the
starter templates in the engine's `ontologies/` are meant to be edited into.

Four functions carry deep records:

- **customer-success** — renewal preparation.
- **product** — feature-request triage.
- **people-hr** — onboarding orchestration and performance-review prep.
- **finance** — spend approval, payroll, and vendor payments, recorded as deliberate
  `wait` verdicts: activities worked to the point of a decision *not* to automate.

The other four are executive views only. That is not an omission; depth is earned by
acting, not by planning to act.
```

- [ ] **Step 2: Create the eight executive views.** Each file is: an `# <Function> — executive view` heading, then this exact frame paragraph, then its table.

```markdown
Every activity this function does at Umbercress, with its Direction — **up** (deserves
more human time) or **down** (should stop being hand-run). Deep records exist only for
the activities the company has chosen to act on first.
```

**`demo/ontologies/customer-success/_executive-view.md`** — heading `# Customer success — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Renewal preparation | down | [deep record](renewal-preparation.md) |
| Health-score monitoring | down | — |
| Customer onboarding | down | — |
| Support-ticket triage | down | — |
| Escalation management | up | — |
| Churn-risk intervention | up | — |
| Quarterly check-in calls | up | — |
| Voice-of-customer synthesis | up | — |
```

**`demo/ontologies/product/_executive-view.md`** — `# Product — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Feature-request triage | down | [deep record](feature-request-triage.md) |
| Specification drafting | down | — |
| Release-notes authoring | down | — |
| Usage-analytics reporting | down | — |
| Launch coordination | down | — |
| Roadmap prioritization | up | — |
| Discovery and problem framing | up | — |
| Pricing and packaging decisions | up | — |
```

**`demo/ontologies/people-hr/_executive-view.md`** — `# People/HR — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Onboarding orchestration | down | [deep record](onboarding-orchestration.md) |
| Performance-review prep | down | [deep record](performance-review-prep.md) |
| Recruiting coordination | down | — |
| Benefits and leave administration | down | — |
| Policy and handbook upkeep | down | — |
| Offboarding | down | — |
| Compensation review | up | — |
| Employee-relations casework | up | — |
```

**`demo/ontologies/finance/_executive-view.md`** — `# Finance — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Spend approval | up | [deep record](spend-approval.md) |
| Payroll runs | up | [deep record](payroll-runs.md) |
| Vendor payments | up | [deep record](vendor-payments.md) |
| Month-end close | down | — |
| Invoice processing | down | — |
| Expense-report review | down | — |
| Budget-versus-actuals reporting | down | — |
| Board-reporting package | down | — |
```

**`demo/ontologies/sales/_executive-view.md`** — `# Sales — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Founder-led discovery calls | up | — |
| Competitive deal strategy | up | — |
| Pipeline hygiene and CRM updates | down | — |
| Proposal and quote generation | down | — |
| Lead qualification | down | — |
| Contract redlining coordination | down | — |
| Forecast roll-up | down | — |
| Renewal handoff to customer success | down | — |
```

**`demo/ontologies/marketing/_executive-view.md`** — `# Marketing — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Positioning and messaging | up | — |
| Customer-story production | up | — |
| Competitive intelligence | up | — |
| Content production | down | — |
| Campaign performance reporting | down | — |
| SEO and site hygiene | down | — |
| Email nurture operations | down | — |
| Conference and event logistics | down | — |
```

**`demo/ontologies/engineering/_executive-view.md`** — `# Engineering — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Architecture decisions | up | — |
| Incident response | up | — |
| Design review | up | — |
| Dependency and security patching | down | — |
| CI/CD pipeline maintenance | down | — |
| Post-incident review authoring | down | — |
| On-call rotation scheduling | down | — |
| Test-suite maintenance | down | — |
```

**`demo/ontologies/legal/_executive-view.md`** — `# Legal — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Non-standard contract negotiation | up | — |
| Data-processing agreement review | up | — |
| Standard contract review (NDAs, MSAs) | down | — |
| Compliance filings | down | — |
| Regulatory change tracking | down | — |
| Vendor and procurement review | down | — |
| IP and trademark administration | down | — |
| Privacy request handling | down | — |
```

- [ ] **Step 3: Verify — the deep-record links point at files that do not exist yet**

Run: `python3 scripts/validate.py . 2>&1 | tail -5`
Expected: **ERRORs** — broken relative links from the four exec views whose Deep record cells name records Tasks 2 and 3 create. That is the referential-integrity check working; it clears in Task 3. Confirm the errors are *only* broken links under `demo/ontologies/`, and that no Direction, header, or canonical-form error appears.

Run this to confirm all eight parse cleanly as tables:

```bash
python3 - <<'PY'
import sys, os; sys.path.insert(0, 'scripts'); import validate
base = 'demo/ontologies'
for fn in sorted(os.listdir(base)):
    p = os.path.join(base, fn, '_executive-view.md')
    if os.path.isfile(p):
        r, f = validate.parse_exec_table(open(p, encoding='utf-8').read(), p)
        print('%-18s %2d activities, %d findings' % (fn, len(r), len(f)))
PY
```

Expected: 8 functions, 8 activities each, **0 findings** each.

- [ ] **Step 4: Commit**

```bash
git add demo/ontologies
git commit -m "feat(demo): Umbercress executive views for all eight functions

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The four automation-path deep records

**Files:** Create four deep records under `demo/ontologies/`

- [ ] **Step 1: Create `demo/ontologies/customer-success/renewal-preparation.md`:**

```markdown
---
activity: Renewal preparation
function: Customer success
motion: automate
score_repetition: high
score_risk: low
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: sensemaking
accountable_owner: Marcus Bell
substrate: The CRM contract and opportunity records + the Relay usage warehouse + the support-ticket system
shape: single-agent
gate_inputs: The renewing account's contract terms and renewal date from the CRM, its last-90-day Relay usage, its open and recently closed support tickets, and the notes from its most recent quarterly check-in
gate_output: A renewal brief in the customer-success workspace — contract terms, usage trend against the account's own history, support history, named risks, and an expansion or contraction read — with every claim linked to the record it came from
gate_standard: Every renewal has a brief in its CSM's hands 45 days before the renewal date, and every number in it resolves to a source record
gate_source_of_truth: The CRM contract record for terms and dates; the Relay usage warehouse for product adoption
gate_exception_path: A missing or contradictory contract record, or usage data more than seven days stale, halts the brief and routes to Marcus Bell rather than shipping a brief with a gap in it
gate_error_cost: A wrong or missing brief sends a CSM into a renewal conversation underprepared — costly if unnoticed, but caught by the CSM's own review before any customer sees it
gate_owner: Marcus Bell
gate_review_gate: The account's CSM reads the brief and confirms it matches what they know before the renewal conversation
---
# Renewal preparation

**Direction: down.** With about 60 accounts on annual contracts and three people in
customer success, assembling the picture before a renewal is hours of gathering that
produces no judgment. It should stop being hand-run so CSM time goes to the renewal
conversation itself.

**Motion: automate.** Repetition is high and every source is a system of record.
Judgment scores **medium**, and the boundary is the point: the gathering is mechanical,
the decision is not. This activity ends at a brief a human reads. It never decides the
renewal, prices it, or contacts the customer.

## Accountability

Which business process runs differently: renewal prep stops being a CSM working
through three systems the week before a renewal and becomes an agent that assembles a
sourced brief 45 days out, halting to a human when a record is missing or stale rather
than filling the gap with an assumption.

Who is accountable for proving it improved: **Marcus Bell**, measured against a
baseline of brief lead time and sourcing completeness captured before provisioning
(the #5 provisioning gate — see [the captured baseline](../../memory/renewal-prep-baseline.md)).
```

- [ ] **Step 2: Create `demo/ontologies/product/feature-request-triage.md`:**

```markdown
---
activity: Feature-request triage
function: Product
motion: automate
score_repetition: high
score_risk: low
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: routing
accountable_owner: Dana Whitfield
substrate: The product tracker + the support-ticket system + CRM opportunity notes
shape: single-agent
gate_inputs: Every feature request raised in the last week in support tickets, in CRM opportunity and check-in notes, and by the customer-success team, plus the existing tracker items they might duplicate
gate_output: Each request filed in the tracker as a new item or linked to the one it duplicates, tagged by theme, carrying the accounts that asked and the annual contract value they represent, and assigned to its owning product manager
gate_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days, and every tracker item names the accounts it came from
gate_source_of_truth: The product tracker for what is already known; the CRM for account and contract-value attribution
gate_exception_path: A request that matches no existing theme and no owning product manager is left unassigned and raised to Dana Whitfield rather than being forced into the nearest tag
gate_error_cost: A misfiled or wrongly deduplicated request loses a customer signal until the next roadmap review — recoverable by refiling, invisible to the customer
gate_owner: Dana Whitfield
gate_review_gate: The owning product manager confirms the theme and the duplicate link when the request reaches their queue
---
# Feature-request triage

**Direction: down.** Reading every incoming request, checking whether it is already
known, attaching who asked and what they are worth, and routing it is high-volume
clerical work that produces no product judgment. With two people in product, it should
stop being hand-run.

**Motion: automate.** Repetition is high, the sources are systems of record, and the
failure mode is recoverable. Judgment scores **medium** and stays human: this activity
decides where a request *goes*, never whether it gets built.

## Accountability

Which business process runs differently: triage stops being a product manager working
through a week of tickets and call notes before they can think about the roadmap, and
becomes an agent that files, deduplicates, attributes, and routes — leaving anything it
cannot place unassigned and visible rather than guessing at a tag.

Who is accountable for proving it improved: **Dana Whitfield**, measured against a
baseline of triage latency and attribution completeness captured before provisioning
(see [the captured baseline](../../memory/triage-baseline.md)).
```

- [ ] **Step 3: Create `demo/ontologies/people-hr/onboarding-orchestration.md`:**

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
accountable_owner: Ruth Okafor
substrate: The HR information system + the IT provisioning tracker + the onboarding checklist
shape: single-agent
gate_inputs: The new hire's start date, role, manager, equipment needs, and required system accesses, from the signed offer and the IT intake form
gate_output: A completed onboarding checklist — accounts provisioned, equipment ordered, the first-week schedule sent, manager and buddy notified
gate_standard: Every new hire has working accounts, equipment en route, and a scheduled first week before their start date
gate_source_of_truth: The HR information system record for the hire; the IT provisioning tracker for access state
gate_exception_path: A non-standard role or missing intake data pauses to Ruth Okafor; contractor-to-employee conversions route to outside counsel first
gate_error_cost: A missed access or a late laptop delays a hire's first day — recoverable within a day, embarrassing, not dangerous
gate_owner: Ruth Okafor
gate_review_gate: The hiring manager confirms the checklist is complete on day one
---
# Onboarding orchestration

**Direction: down.** One person runs all of People operations at Umbercress. The
coordination of accounts, equipment, and first-week logistics is high-repetition,
low-judgment routing with a clear source of truth, and it should stop being hand-run
so that time goes to the human parts of someone joining a company.

**Motion: automate.** Repetition is high, risk and judgment are low, the workflow is
only moderately company-specific, and the market for onboarding automation is mature.

## Accountability

Which business process runs differently: the pre-start runbook stops being a person
hand-working a checklist and becomes an agent that provisions, orders, and schedules
against the HR system record, pausing to a human on any exception.

Who is accountable for proving it improved: **Ruth Okafor**, measured against a
baseline of time-to-day-one-ready and day-one readiness captured before provisioning
(see [the captured baseline](../../memory/onboarding-baseline.md)).
```

- [ ] **Step 4: Create `demo/ontologies/people-hr/performance-review-prep.md`.** This is the record demo query 3 lands on — read Design call 1 before writing it.

```markdown
---
activity: Performance-review prep
function: People/HR
motion: automate
score_repetition: high
score_risk: medium
score_judgment: high
score_company_specificity: medium
score_market_maturity: low
work_type: sensemaking
accountable_owner: Ruth Okafor
substrate: The HR information system + the goal tracker + peer-feedback submissions + the previous review cycle's records
shape: single-agent
gate_inputs: For each employee in the cycle: their goals and recorded outcomes, submitted peer feedback, their previous review, and their manager's running notes
gate_output: An evidence pack for the manager — goals against outcomes, peer feedback grouped by theme with attribution intact, and the previous cycle's commitments with their status. No rating, no summary judgment, no draft assessment
gate_standard: Every employee in the cycle has an evidence pack in their manager's hands one week before the review conversation, and every item in it links to the submission it came from
gate_source_of_truth: The goal tracker for goals and outcomes; peer-feedback submissions verbatim, never paraphrased
gate_exception_path: Missing goals, fewer than two peer submissions, or an employee who changed manager mid-cycle halts the pack and routes to Ruth Okafor
gate_error_cost: A pack that misattributes or omits feedback distorts a conversation about someone's job — the highest-stakes error in this ontology, which is why the manager reviews every pack and no assessment is ever drafted
gate_owner: Ruth Okafor
gate_review_gate: The employee's manager reads the pack and confirms it before the review conversation
---
# Performance-review prep

**Direction: down.** Assembling the evidence for a review — goals, outcomes, peer
feedback, last cycle's commitments — is hours of gathering per employee, repeated
twice a year by one person. The gathering should stop being hand-run.

**Motion: automate — and the scope is where the care lives.** Judgment scores **high**,
which would normally point away from automation. It does not here, because the activity
is deliberately drawn to *exclude* the judgment: the agent assembles evidence and stops.
It does not rate, rank, summarize, or draft an assessment. Evaluating a person is a
human-owned decision, and the constitution rule that governs this skill blocks the
agent from crossing that line rather than trusting it not to.

Ticket #4 described this activity's motion as "assist". That is the same idea expressed
as a verdict rather than a boundary: the Motion ladder records *how the work gets done*,
and the limit on *how far the agent may go* belongs on the Owner's Card and in the
constitution, where it can actually be enforced.

## Accountability

Which business process runs differently: review prep stops being one person assembling
twenty evidence packs by hand and becomes an agent that gathers and organizes, with the
assessment itself untouched and explicitly out of bounds.

Who is accountable for proving it improved: **Ruth Okafor**, measured against a
baseline of pack lead time and evidence completeness captured before provisioning
(see [the captured baseline](../../memory/review-prep-baseline.md)).
```

- [ ] **Step 5: Verify**

Run: `python3 scripts/validate.py . 2>&1 | grep -E "demo/ontologies/(customer-success|product|people-hr)" ; echo "---"`
Expected: no output — those three functions' exec views and deep records are complete and consistent. Broken-link ERRORs for `demo/ontologies/finance/` remain until Task 3.

- [ ] **Step 6: Commit**

```bash
git add demo/ontologies
git commit -m "feat(demo): deep records for the three deep functions (#4)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: Finance — three deliberate `wait` verdicts

**Files:** Create three deep records under `demo/ontologies/finance/`

> These are the second place the Motion pivot runs on real content: `wait` requires only the common core, so none of these carries Substrate, Shape, or a Describability Gate. That is correct, not incomplete.

- [ ] **Step 1: Create `demo/ontologies/finance/spend-approval.md`:**

```markdown
---
activity: Spend approval
function: Finance
motion: wait
score_repetition: medium
score_risk: high
score_judgment: high
score_company_specificity: high
score_market_maturity: low
work_type: accountability
accountable_owner: Priya Raman
---
# Spend approval

**Direction: up.** Approving spend is a judgment about what the company can afford and
what it is choosing to become. At twenty people, with a fractional CFO, that judgment
belongs to more human attention, not less.

**Motion: wait.** Repetition is only medium and everything else argues against
automating: risk is high, judgment is high, the thresholds are specific to this
company's runway, and the tooling market for a company this size is immature. The
verdict is to revisit when the company is larger and the thresholds have stopped
moving.

**No skill will be generated for this activity, and if one ever is it is high-risk.**
An agent that can approve spend can move money. That is the action class the fixed hook
set hard-blocks, and it is not a line worth approaching for a saving measured in
minutes a week.

**This record carries no Substrate, Shape, or Describability Gate, and that is
correct.** Those are required only on the automation path. A recorded `wait` is a
complete answer: this activity has been worked to the point of a deliberate decision
not to automate.

## Accountability

Nothing is automated here. What changes is that the decision is on the record with a
named owner, so the next person who proposes automating approvals can see why it was
declined and what would have to change first.

Who is accountable: **Priya Raman**.
```

- [ ] **Step 2: Create `demo/ontologies/finance/payroll-runs.md`:**

```markdown
---
activity: Payroll runs
function: Finance
motion: wait
score_repetition: high
score_risk: high
score_judgment: low
score_company_specificity: low
score_market_maturity: high
work_type: accountability
accountable_owner: Priya Raman
---
# Payroll runs

**Direction: up.** Not because payroll needs more human thought — it needs almost none
— but because it needs a human's name on it. Someone must be accountable for the run
having happened correctly.

**Motion: wait**, and this is the interesting case in this function. Repetition is
high, judgment is low, and the market is mature: on scores alone this looks like an
automation candidate. It is not, because **risk is high and the work is already bought**
— the payroll provider runs it. What is left at Umbercress is the twice-monthly review
and release, which is exactly the accountability half that should not be handed to an
agent.

**No skill will be generated for this activity, and if one ever is it is high-risk.**
An agent with release authority over payroll can pay the wrong people the wrong amount
before anyone looks.

**No Substrate, Shape, or Describability Gate** — `wait` requires only the common core.

## Accountability

Nothing is automated here. The record exists so that "why isn't payroll automated?" has
a written answer that is not "nobody got to it".

Who is accountable: **Priya Raman**.
```

- [ ] **Step 3: Create `demo/ontologies/finance/vendor-payments.md`:**

```markdown
---
activity: Vendor payments
function: Finance
motion: wait
score_repetition: medium
score_risk: high
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: accountability
accountable_owner: Priya Raman
---
# Vendor payments

**Direction: up.** Releasing money to an outside party is the smallest action in this
ontology with the largest irreversible consequence.

**Motion: wait.** Repetition is medium, risk is high, and the failure mode is one an
agent is especially bad at noticing: a payment to a plausible-looking wrong recipient
looks exactly like a payment to the right one. Revisit when there is a reconciliation
control that does not depend on someone remembering to look.

**No skill will be generated for this activity, and if one ever is it is high-risk** —
an outbound payment is not reversible by rewriting a file.

**No Substrate, Shape, or Describability Gate** — `wait` requires only the common core.

## Accountability

Nothing is automated here. The scored verdict is the deliverable: it says what would
have to be true before this is worth revisiting.

Who is accountable: **Priya Raman**.
```

- [ ] **Step 4: Verify the pivot, and that the whole ontology is now clean**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0 — every deep-record link now resolves and no `wait` record is asked for automation-path fields.

Run the pivot probe:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
for n in ("spend-approval", "payroll-runs", "vendor-payments"):
    p = "demo/ontologies/finance/%s.md" % n
    f = validate.check_deep_record(p, ".")
    data, _ = validate._load_frontmatter(p, p)
    print("%-16s findings=%s motion=%s gate_fields=%s"
          % (n, [x.message for x in f] or "none", data.get("motion"),
             [g for g in validate.GATE_FIELDS if g in data] or "none"))
PY
```

Expected for all three: `findings=none motion=wait gate_fields=none`. A finding naming `substrate`, `shape`, or a `gate_` field would mean the pivot is demanding automation-path fields of a `wait` record — a real validator bug. Stop and report it rather than adding the fields.

- [ ] **Step 5: Commit**

```bash
git add demo/ontologies/finance
git commit -m "feat(demo): finance as three deliberate wait verdicts (#4 shallow but opinionated)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The org memory

**Files:** Create eight records and `demo/memory/_index.md`

> **The supersession chain is demo query 1's whole payload** ("why did we move to async standups?"). It must show provenance, a named owner, and a reachable superseded predecessor. Get this one right before the rest.

- [ ] **Step 1: Create `demo/memory/async-standups.md`:**

```markdown
---
provenance: confirmed
owner: Tomás Iglesias
valid_at: 2026-03-02
review_by: 2026-12-01
source: Engineering retro notes 2026-02-26; the two-week trial thread in the engineering channel; the decision note Tomás Iglesias posted 2026-03-02
---
# Engineering standups are asynchronous

Since 2026-03-02, engineering runs standups asynchronously: a written update in the
team channel by 10:00 local time, plus one 20-minute synchronous call on Wednesdays.

**Why.** The team works across five time zones. A daily synchronous standup cost about
six engineer-hours a week and forced three people to start before 07:00 local. The
argument for keeping it was that blockers surface faster in a live call. A two-week
trial tested that directly: blockers surfaced within the same working day in nine of
ten cases, and the one that did not was raised in the Wednesday call.

**What was given up.** The incidental conversation that used to happen in the last two
minutes of the call. The Wednesday session exists to hold some of that; it does not
hold all of it, and that was accepted rather than papered over.

This supersedes [the daily synchronous standup decision](daily-standups.md).
```

- [ ] **Step 2: Create `demo/memory/daily-standups.md`:**

```markdown
---
provenance: superseded
owner: Tomás Iglesias
valid_at: 2025-09-15
invalid_at: 2026-03-02
review_by: 2026-12-01
superseded_by: memory/async-standups.md
source: The engineering handbook entry added 2025-09-15
---
# Engineering standups are daily and synchronous (superseded)

From 2025-09-15, engineering held a fifteen-minute synchronous standup every weekday
morning, on the reasoning that a small team catches blockers faster face to face.

This stopped being true on 2026-03-02, when the team moved to asynchronous updates —
see [the current decision](async-standups.md). The record is kept rather than deleted
so the reasoning that produced it stays readable: the argument was sound for a
co-located team of six and did not survive the move to five time zones.
```

- [ ] **Step 3: Create the two renewal-risk records** — demo query 2 ("which at-risk renewals are blocked on roadmap items?") is answered by these plus the product tracker items in the triage record.

`demo/memory/cartwright-renewal-risk.md`:

```markdown
---
provenance: observed
owner: Nina Sokolova
valid_at: 2026-07-14
review_by: 2026-09-30
source: Cartwright Haulage quarterly check-in notes 2026-07-14; support tickets UR-2291 and UR-2340
---
# Cartwright Haulage renewal is at risk on bulk shift-swap approvals

Cartwright Haulage renews on 2026-10-31 at $52,000 annual contract value. At the July
check-in their operations lead named one blocker: approving shift swaps one at a time
does not work at their depot volume, and they have asked twice for a bulk approval
flow.

The request is tracked in the product tracker as **bulk shift-swap approvals**, filed
from tickets UR-2291 and UR-2340. It is not on the current roadmap. Their team lead
said plainly that they are looking at one alternative vendor because of it.

Weekly Relay usage is otherwise healthy and has not declined; this is a feature gap,
not disengagement.
```

`demo/memory/belport-renewal-risk.md`:

```markdown
---
provenance: observed
owner: Nina Sokolova
valid_at: 2026-07-21
review_by: 2026-09-30
source: Belport Freight escalation thread 2026-07-09; quarterly check-in notes 2026-07-21
---
# Belport Freight renewal is at risk on overtime reporting

Belport Freight renews on 2026-09-30 at $31,000 annual contract value. Their finance
contact cannot reconcile Relay's overtime export against their payroll provider without
hand-editing it every fortnight, which they escalated in July.

The request is tracked in the product tracker as **payroll-ready overtime export**. It
is on the roadmap but unscheduled.

This is the second account this quarter to raise the same export, which is the kind of
pattern feature-request triage exists to make visible before a renewal conversation
rather than during one.
```

- [ ] **Step 4: Create the four captured baselines.** Each is a pre-provisioning measurement the corresponding skill will cite in 2.3d.

`demo/memory/onboarding-baseline.md`:

```markdown
---
provenance: observed
owner: Ruth Okafor
valid_at: 2026-06-30
review_by: 2026-10-31
source: The People operations onboarding tracker, H1 2026 (nine hires)
---
# Onboarding baseline (pre-provisioning)

Captured before the onboarding-orchestration skill was provisioned, so its improvement
can be proven rather than assumed (#5 provisioning gate).

- Median time-to-day-one-ready: **five business days** after offer signature.
- Day-one readiness — accounts, equipment, and schedule all present on the first
  morning: **five of nine** hires.
- Most common gap: a system access not granted before the first morning.
```

`demo/memory/review-prep-baseline.md`:

```markdown
---
provenance: observed
owner: Ruth Okafor
valid_at: 2026-07-06
review_by: 2026-10-31
source: The H1 2026 review cycle: nineteen employees, manager debrief notes
---
# Review-prep baseline (pre-provisioning)

Captured before the performance-review-prep skill was provisioned (#5 provisioning
gate).

- Median time from cycle open to a manager holding an evidence pack: **eleven days**.
- Packs delivered at least one week before the review conversation: **six of nineteen**.
- Packs where every peer comment carried its attribution intact: **eleven of nineteen**;
  the rest had been summarized by hand, which is the failure the pack format exists to
  stop.
```

`demo/memory/renewal-prep-baseline.md`:

```markdown
---
provenance: observed
owner: Marcus Bell
valid_at: 2026-07-02
review_by: 2026-10-31
source: The customer-success renewal log, H1 2026 (twenty-six renewals)
---
# Renewal-prep baseline (pre-provisioning)

Captured before the renewal-prep skill was provisioned (#5 provisioning gate).

- Median brief lead time: **eight days** before the renewal date.
- Renewals with a written brief at all: **fifteen of twenty-six**.
- Briefs whose usage numbers resolved to a source record: **six of fifteen**; the rest
  cited a number with no link back to the warehouse.
```

`demo/memory/triage-baseline.md`:

```markdown
---
provenance: observed
owner: Dana Whitfield
valid_at: 2026-07-07
review_by: 2026-10-31
source: The product tracker export, Q2 2026 (one hundred and forty-one requests)
---
# Feature-request-triage baseline (pre-provisioning)

Captured before the feature-request-triage skill was provisioned (#5 provisioning
gate).

- Median time from a request being raised to being filed and assigned: **nine business
  days**.
- Requests filed within five business days: **forty-four of one hundred and forty-one**.
- Filed requests naming the accounts that asked: **thirty-one**; the rest carried no
  attribution, so nobody could weigh them by contract value.
- Duplicates found only at the quarterly roadmap review rather than at triage:
  **seventeen**.
```

- [ ] **Step 5: Create `demo/memory/_index.md`.** Live records only — `daily-standups.md` is superseded and must **not** appear:

```markdown
# Umbercress org memory — index

Live records only. Superseded records stay in history, reachable through
`superseded_by` chains — which is how this index stays inside the load budget.

- [Engineering standups are asynchronous](async-standups.md) — Tomás Iglesias — confirmed
- [Cartwright Haulage renewal is at risk on bulk shift-swap approvals](cartwright-renewal-risk.md) — Nina Sokolova — observed
- [Belport Freight renewal is at risk on overtime reporting](belport-renewal-risk.md) — Nina Sokolova — observed
- [Onboarding baseline (pre-provisioning)](onboarding-baseline.md) — Ruth Okafor — observed
- [Review-prep baseline (pre-provisioning)](review-prep-baseline.md) — Ruth Okafor — observed
- [Renewal-prep baseline (pre-provisioning)](renewal-prep-baseline.md) — Marcus Bell — observed
- [Feature-request-triage baseline (pre-provisioning)](triage-baseline.md) — Dana Whitfield — observed
```

- [ ] **Step 6: Verify the chain and the index**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0. In particular: no "live record not in index" WARN (all seven live records are listed), no WARN for the superseded record (it is correctly absent), and no overdue-`review_by` WARN.

Run the supersession probe:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
f = [x for x in validate.check_memory('.') if 'demo/' in x.path]
print("demo memory findings:", [(x.level, x.path, x.message) for x in f] or "none")
d, _ = validate._load_frontmatter('demo/memory/daily-standups.md', 'x')
print("superseded_by:", d.get('superseded_by'), "| invalid_at:", d.get('invalid_at'))
print("instance base:", validate._memory_instance_base('.', 'demo/memory/daily-standups.md'))
PY
```

Expected: `none`; `superseded_by: memory/async-standups.md`; instance base `./demo`. An instance base of `.` would mean the pointer is resolving against the repo root instead of `demo/` — the exact bug 2.3a's Codex rounds closed.

- [ ] **Step 7: Commit**

```bash
git add demo/memory
git commit -m "feat(demo): Umbercress org memory — the async-standups chain, renewal risks, four baselines

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: Status honesty and the full gate

**Files:** Modify `demo/README.md`, `AGENTS.md`

- [ ] **Step 1: Update `demo/README.md`.** Replace the "What is here now" and "What is coming" sections with:

```markdown
## What is here now

- `canon.md` — the fictional world and the identifier allowlist.
- `ontologies/` — all eight functions' executive views, deep records for renewal
  preparation, feature-request triage, onboarding orchestration, and performance-review
  prep, and finance's three recorded decisions *not* to automate.
- `memory/` — the company's org memory: why engineering moved to asynchronous
  standups (and the superseded decision it replaced), two at-risk renewals and what
  they are blocked on, and the four captured baselines.

## What is coming

- The skills and Owner's Cards for the four acted-on activities, and the constitution
  — including the rule that stops an agent from writing a performance assessment.
- The 15-minute walkthrough script, and the version pin that puts this directory under
  the same governance the validator applies to a real company repo.

The walkthrough is not usable yet. Nothing above describes a capability that works
today; the ontologies and memory are content you can read, not a demo you can run.
```

- [ ] **Step 2: Update `AGENTS.md`.** Replace the `demo/` bullet in "Built and working" with:

```markdown
- `demo/` — the pre-installed example company (**Umbercress**, ~20 people). Its canon
  declares the fictional world and doubles as the validator's identifier allowlist; its
  ontologies and org memory are complete. Skills, constitution, and the 15-minute
  walkthrough are still being filled in — `demo/README.md` says what is there today.
```

- [ ] **Step 3: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`, 610 tests — this slice adds no tests because it adds no code.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Twenty-four new files, zero new findings.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. Every demo file is an addition, and `demo/` still has no `groundwork.pin`, so the #18 tripwire stays dormant until 2.3e.

Run the instance probe — proof that `demo/` is actually being governed rather than merely present:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
ig = validate.load_gitignore('.')
print("instances:", [r for r in validate._instance_roots('.', ig)])
for name in ("check_ontology", "check_owner_cards", "check_constitution",
             "check_proposals", "check_changelog", "check_memory",
             "check_synthetic_identifiers"):
    fn = getattr(validate, name)
    f = fn('.', ig) if name != "check_memory" else fn('.')
    print("%-28s %d finding(s)" % (name, len(f)))
PY
```

Expected: `instances:` lists both `.` and `./demo`. All checks report 0 findings. If `./demo` is missing from the instance list, the demo content is not being validated at all — stop and investigate before committing.

- [ ] **Step 4: Commit**

```bash
git add demo/README.md AGENTS.md
git commit -m "docs: demo status — ontologies and memory landed, walkthrough still to come

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No skills, Owner's Cards, or constitution.** Slice **2.3d**: the four work packages (with performance-review prep's card forbidding any drafted assessment), the demo constitution including the **rung-5 human-decision rule** that fires in demo query 3, and the meeting-challenger runnable exemplar (#8 item 3).
- **No walkthrough script and no `groundwork.pin`.** Slice **2.3e**, the capstone: the 15-minute 3-query script, the pin that makes `demo/` a governed root, and one live pending proposal — the tripwire's happy path and #4's rung-5 governance block in one artifact.
- **No validator changes.** This slice is content against live checks. If a check misfires, report it rather than editing it here.
- **Still open for the maintainer:** three Slice 1.5d-ii deferrals (dot-directory classification, case-variant authorization, the path-style nit), the `SKIP_RELPATHS` gate-scoping sign-off, and the standing re-review rule.

## Self-Review

- **Ticket coverage:** #4's demo shape — People/HR as the third deep function with onboarding orchestration and performance-review prep, customer success and product as the other two, Finance shallow-but-opinionated with spend approval / payroll / vendor payments as recorded `wait` verdicts, and query 1's org-memory decision lookup with provenance, owner, and supersession → Task 4's async-standups chain. #5's two tiers and Motion pivot → eight executive views plus seven deep records, three of which are common-core-only. #7's record schema, supersession rules, and live-only index → Task 4. #16's canon allowlist → every identifier traces to `umbercress.example`.
- **The vocabulary conflict is surfaced, not silently resolved.** Design call 1 states that #4 says `assist`, that #5's locked vocabulary has no such motion, which reading the plan implements and why, and what the alternative would cost (a schema change, a version bump under the 2.2a rule, and new pivot semantics). The record itself explains the choice in its own body, so a reader of the demo meets the reasoning too.
- **Placeholder scan:** no TBD/TODO. Every one of the 24 files is given in full, with verification commands and expected output — including the *deliberate* intermediate failure in Task 1 Step 3 (broken deep-record links until Task 3), so a red gate mid-slice is not mistaken for a mistake.
- **Type consistency:** no code changes, so no signatures move. Frontmatter fields match the schemas exactly: deep records use `SCORE_FIELDS`/`GATE_FIELDS` names, memory records use the six-field-group names from `memory/README.md`, and `superseded_by` is instance-relative.
- **Pre-empts the recurring findings.** (a) *Corpus void* — Task 5's probe asserts `./demo` appears in `_instance_roots`, because "0 findings" from a check that never scanned the directory is indistinguishable from "0 findings" from a clean one; that is the single most likely way this slice ships hollow. (b) *The synthetic-identifier extractors* — the authoring constraint against bare 7- and 10-digit runs is stated up front, since money written as `52000` would read as a phone number; every figure in the content uses `$52,000` or spelled-out counts. (c) *Freshness WARNs* — every `review_by` is in the future, checked against the invariant that the WARN count must not move. (d) *Instance-relative resolution* — Task 4's probe prints the computed instance base for the superseded record, so a pointer resolving against the repo root instead of `demo/` is caught explicitly rather than assumed.
