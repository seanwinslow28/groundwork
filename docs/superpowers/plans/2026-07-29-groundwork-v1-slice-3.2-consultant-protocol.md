# groundwork V1 — Slice 3.2: the consultant protocol + the question skeleton — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the interview askable. Slice 3.1 built the state format an interview writes into; this slice builds *how* it asks (§4's consultant protocol — define-the-role-first, one question at a time, evidence-based read-what-exists, checkpoint approvals) and *what* it asks (the intent-engineering 9-section skeleton adapted to an organization, plus the constitution compiler's five-question worksheet). The question skeleton ships as a **question → destination-field map**, and two tests hold it to the schema in both directions, so an interview that cannot fill a required field is a test failure rather than a discovery made during generation.

**Architecture:** Content plus two tests. No `scripts/validate.py` changes. `interview/` gains `protocol.md` and `questions.md` alongside 3.1's `README.md`; `governance/worksheets/five-question-worksheet.md` gains its caller. The tests import the field constants `validate.py` already exports (`SCORE_FIELDS`, `GATE_FIELDS`, `CARD_REQUIRED`, `CARD_TRACK2`, `_RULE_OBJECT_FIELDS`) and the canonical row splitter `_canonical_row`, so the question bank is checked against the same definitions the gate enforces.

**Tech Stack:** Markdown + two stdlib `unittest` tests.

## Global Constraints

- **No `scripts/validate.py` changes.** This slice adds engine documentation and the tests that keep it honest. If a check misfires, stop and report rather than editing it here.
- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, and `--diff main` must exit 0. The test count moves **up only**, from **662**.
- **`demo/` is a governed root, and its five interview layers are now frozen.** Do not edit anything under `demo/interview/NN-*.md`, `demo/skills/`, or `demo/governance/constitution/` — `--diff main` will ERROR. This slice touches no demo content at all.
- **Reuse the canonical row grammar; do not invent a second one.** `validate._canonical_row` splits exactly three cells with the escapes/HTML/code-span ban already pinned in 2.2a. The question table is three columns on purpose so it can reuse it. Any row that is not canonical is a **test failure**, not a tolerated variant.
- **Zero dependencies.** Stdlib only, in tests as well as in shipped scripts.
- **Keep path components short** (`check_entropy` WARNs on 40+ character runs at ≥ 4.0 bits) and keep `AGENTS.md` under 200 lines — it is at **149**.
- **Pronouns:** they/them or the person's name.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 3.1 merged and pushed (`73f2c5e`). 662 tests with 1 designed skip, gate + `--diff main` exit 0, 7 WARNs, `AGENTS.md` at 149 lines. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-3.2-consultant-protocol
```

---

## Design calls flagged for the maintainer

**1. The 9-section spec was read from the live tool, and the brief's paraphrase is missing two sections.**
Brief §4 says the question skeleton "adapts the intent-engineering 9-section spec (objective, outcomes, health metrics, constraints, autonomy, edge cases, stop rules)" — that is **seven**. The actual scaffold, generated from the `intent-engineering` MCP server on 2026-07-29, is:

| # | Section | In the brief's list? |
|---|---|---|
| 1 | Objective | yes |
| 2 | **User goal** | **no** |
| 3 | Desired outcomes | yes |
| 4 | Health metrics | yes |
| 5 | **Strategic context** | **no** |
| 6 | Constraints (steering + hard) | yes |
| 7 | Decision authority | yes ("autonomy") |
| 8 | Edge cases | yes |
| 9 | Stop rules & verification | yes |

Both missing sections map cleanly onto things groundwork already collects — *user goal* onto the Owner's Card's job-in-one-sentence and the ontology's "which business process runs differently", *strategic context* onto Substrate, `gate_inputs`, and `gate_source_of_truth`. So this is a **correction to a paraphrase, not a change of scope**, and the skeleton ships all nine. Recorded because the brief is a locked source document and I am departing from its enumeration on the strength of the live tool.

**2. The nine sections map onto groundwork's existing fields almost one-for-one — so the skeleton ships as a question → field map, not as prose.**
This is the slice's central design decision and it is worth seeing:

| Section | Where the answer lands |
|---|---|
| Objective | `exec:direction`, `ontology:motion`, the five `score_*`, `ontology:work_type` |
| User goal | `card:job`, the ontology's accountability paragraph |
| Desired outcomes | `ontology:gate_output`, `ontology:gate_standard`, `card:success_standard` |
| Health metrics | the captured baseline (`memory:*`) — **and one genuine gap, see call 3** |
| Strategic context | `ontology:substrate`, `ontology:gate_inputs`, `ontology:gate_source_of_truth`, `ontology:shape` |
| Constraints | `card:allowed_actions` / `proposed_only_actions` / `forbidden_actions` / `sources_must_not_use`, `rule:value`, `rule:runtime_check` |
| Decision authority | `action_class`, `ontology:accountable_owner`, `card:owner` / `backup_owner`, `rule:rung`, the four rule owners |
| Edge cases | `ontology:gate_exception_path`, `ontology:gate_error_cost`, `card:pause_condition` |
| Stop rules & verification | `ontology:gate_review_gate`, `card:evidence_required` / `review_sample` / `review_cadence` / `retirement_condition`, `rule:sunset` |

Two things follow. First, **the generator in 3.3 becomes mechanical** — every question already names the field it fills, so generation is transcription plus formatting rather than interpretation. Second, **the skeleton's completeness is testable**: Task 3 asserts that every field in the schema's required sets is named by at least one question, which is #5's "all eight Gate fields must be *answered*; there is no waiver mechanism" made mechanical at the interview end rather than only at the validator end. An interview that cannot fill a required field is now a failing test instead of a surprise during generation.

**3. Health metrics is the one section groundwork has no field for — and I am not bumping the schema for it.**
The 9-section spec defines health metrics as *"what must NOT degrade while pursuing outcomes"* — the Goodhart guard, elicited by asking "how could the agent achieve this in a way I'd hate?". groundwork collects `success_standard` (what good looks like, measured against a captured baseline) and `known_failure_modes` (what has gone wrong), but it has **no home for the thing that must not get worse**. That is a real gap, found by running the real scaffold rather than by reading the brief's summary of it.

*Options.* (a) Ask the question and land the answer in prose — the card's `known_failure_modes` and the ontology record's body. No schema change. (b) Add a `health_metric` field to the Owner's Card. That is a schema change, and **since 2026-07-29 the pull promise binds**: `demo/` carries a pin, so a new required field is a `SCHEMA_VERSION` bump to v2 with a migration note, spending the first migration on one field.

*Recommendation: (a), with the gap recorded* in `docs/known-limitations.md` and named as the **first candidate for a v2 bump** whenever one is needed for other reasons. The question gets asked either way — the difference is whether the answer is a checked field or checked prose. Counter-argument, honestly: a field the validator does not know about is a field the generator can quietly skip, and "we asked but did not store it structurally" is exactly the kind of soft spot this project usually closes. I still recommend (a), because spending the first-ever migration gate on one card field is a worse trade than carrying a documented gap until a bump is warranted on its own merits. **Your call.**

**4. The interview ships as documents, not as a skill — and this is not a stylistic choice.**
A builder will reach for `skills/company-interview/`. It cannot work: `_check_owner_cards_instance` requires every directory under `skills/` to carry a `SKILL.md` with an `ontology:` reference resolving under `ontologies/`, and the interview has no ontology deep record because it is not a company work package — it is the engine's own procedure. It also would not be right if it did work: skills are the things groundwork *generates for a company*, and the interview is what generates them. `AGENTS.md` points at `interview/` and that is the entry point.

**5. The no-human rule: if nobody is there to answer, the interview stops.**
§4 says "no generation until understanding is complete," which is a rule about *sequence*. It leaves the headless case undefined — and an unconditional "ask the human" step in a chain that ends in a subagent either hangs or gets silently skipped, at which point the agent proceeds on inference and calls it confirmed. So the protocol states the strict form explicitly: **an unanswerable question halts the interview and is recorded in `_working.md`; it is never resolved by inference.** This is the same doctrine as #6's generator refusal (the owner, the forbidden actions, and the death conditions come only from a human's answer) and it is why those four fields are marked **human-only** in the question map — a mark the generator in 3.3 will read.

**Named cut line.** If the question bank runs longer than expected, it splits at **Task 2** as named Slice **3.2b** and the spec's Build log says so — never a silent trim. The protocol without its questions is the inert artifact the Phase 3 re-ordering existed to avoid, so if anything gets deferred it is not Task 2's completeness; it is Task 3's second test, which becomes 3.2b along with the remaining rows.

---

## File Structure

**Create (2 files):**

- `interview/protocol.md`
- `interview/questions.md`

**Modify (5 files):** `interview/README.md`, `governance/worksheets/five-question-worksheet.md`, `tests/test_validate.py`, `AGENTS.md`, `docs/known-limitations.md`.

---

## Task 1: The consultant protocol

**Files:** Create `interview/protocol.md`.

- [ ] **Step 1: Create `interview/protocol.md`:**

````markdown
# The interview — how to run it

This is the procedure. [questions.md](questions.md) is what to ask;
[README.md](README.md) is the state format the answers are written into. Read all
three before starting, and read this one again at every checkpoint.

An interview produces a company's operating system. It is not a form, and filling it in
faster does not make it better — a wrong answer captured confidently is worse than a
question still open, because everything downstream is generated from it.

## Before anything: the private repo

The first act is creating the company's own **private** repository. Every answer, every
checkpoint, and every generated file lives there. Nothing organizational is ever written
into the public groundwork clone, which stays a pull-only engine (#10).

```
gh repo create <company>-os --private
```

Then `interview/` is created inside it, and the manifest is the first commit.

## The four mechanics

### 1. Define the role first, then act as it

Before the first question, ask the human this, and wait:

> "What does a *good* organizational analyst do here, and what does a bad one do?"

Their answer is the role, and it goes in the manifest's `role:` field verbatim enough
that a resuming agent inherits it. Write it down before asking anything else.

The reason is not ceremony. An analyst who has not agreed what good looks like defaults
to the shape of its training — arriving with a solution and interviewing for permission.
The role, stated by the person who has to live with the result, is the thing you check
your own behaviour against when the conversation gets interesting.

A reasonable default, if they ask for one: *a good analyst asks what the work actually
is before asking what to do about it, says "that is not worth automating" out loud, and
never proposes machinery for a problem nobody has named.* Offer it as a starting point,
not as the answer.

### 2. One question at a time — and no generation until understanding is complete

One question. Wait for the answer. Then the next.

Batched questions get batched answers, and batched answers are where detail goes to die:
the person answers the easy one, gestures at the rest, and the gaps are invisible because
the shape of a reply looks complete.

**No file outside `interview/` is written until the interview is complete.** Not a draft
ontology, not a sample skill, not "here is what I would generate." The reason is that a
generated artifact stops being a question — the person starts editing your draft instead
of telling you how the work actually happens, and you have replaced their model of their
company with yours. Slice 3.3's generator enforces this at the mechanical level: it
refuses to run while the manifest says `status: in-progress`.

If the person asks to see something concrete, show them `demo/` — a company that is
already finished, and not theirs.

### 3. Read what exists, with permission, and reflect it back

Ask:

> "May I read what you already have — the handbook, a calendar export, the tracker, the
> repo, a quarter of meeting notes? I will tell you what I think the rules actually are,
> and you tell me where I am wrong."

This is the highest-yield move in the interview, and the reason is uncomfortable: people
report the rules they wish they had. Asked "what is your renewal process," you get the
process as designed. Read the renewal log and you get the process as run — and the gap
between them is usually the thing worth acting on.

What comes back from a read is **`observed`**, and what you conclude from it is
**`inferred`**. Neither is `confirmed`. Both go in `_working.md` with a `source:` naming
what you read, and both stay provisional until a person says otherwise. Reflect the
finding back as a claim they can correct, with the evidence attached:

> "The log says fifteen of twenty-six renewals had a written brief, median eight days
> out. Is that the process, or is that the process failing?"

If permission is refused, say what that costs — the interview will record what people
report rather than what the records show — and continue. Refused permission is a fact
about the company, not an obstacle.

### 4. Checkpoint approvals, one layer at a time

A **layer** is one coherent chunk of understanding — a function, or the opening scope.
When a layer feels settled:

1. State back what you believe is now true, in the person's own terms, short enough to
   read in one go.
2. Ask: **"Is this right, and may I freeze it?"**
3. Only their yes confirms it. Your confidence does not.
4. On yes: promote `_working.md` to the next `NN-slug.md`, set `provenance: confirmed`,
   record `confirmed_by` and `confirmed_at`, update the manifest, and commit them
   together in one commit.

That commit is the approval record. The promote-and-commit protocol is specified in
[README.md](README.md); this is the conversational half of it.

**A layer is frozen once committed.** If a confirmed fact turns out to be wrong, the next
layer records the correction and says what it corrects. You do not go back and rewrite
what somebody approved — `--diff` will catch it, and more importantly it destroys the
one thing the checkpoint was for.

## The rule when nobody can answer

**An unanswerable question halts the interview.** It does not get resolved by inference.

Write the question into `_working.md`, name it in the manifest's `open_question`, commit
the manifest, and stop. A resuming agent — possibly in a different harness, possibly
weeks later — picks it up from there.

This matters most in the places it is most tempting to skip. Four answers **may only
come from a human**, and no amount of reading produces them (#6):

- the **owner** and the **backup owner** of any skill,
- the **forbidden actions**,
- the **pause condition** and the **retirement condition**.

They are marked *human-only* in [questions.md](questions.md). An agent that fills one of
them from context has invented an accountability structure, and the person named will
find out when something goes wrong.

## The shape of the interview

**Layer 1 — role and scope.** The role (mechanic 1). Then: how many people, what the
company sells, what its shape rules out. Then the decision that governs everything after
it — **which functions go deep.**

Steer toward **three to five acted-on activities** on a first pass. This is doctrine, not
a validator rule: *depth is earned by acting, not by planning to act.* An organization
that deep-records twelve activities has written twelve worksheets and changed nothing. If
they want more, agree to come back — the state format is resumable precisely so a second
pass is cheap.

**Layers 2..N — one function each.** For each function: name every activity and give each
one a **Direction** — up (deserves more human time) or down (should stop being hand-run).
That is the whole executive tier, and most activities never get more than it.

For the activities they have chosen to act on, work the question skeleton
([questions.md](questions.md)) in section order. The Motion verdict is the pivot: only
`automate` and `build` need Substrate, Shape, and all eight Describability Gate answers.
`buy`, `hire`, and `wait` stop after the common core — about four answers.

**A `wait` is a real answer.** Record it, with its reasoning. An ontology that only ever
records automation verdicts reads as an automation funnel, and in a year somebody will
want to know whether a function was considered and dismissed or simply never asked.

**The constitution pass.** Once the functions are mapped, run the
[five-question worksheet](../governance/worksheets/five-question-worksheet.md) over the
company's rituals — **starting with the rule everybody resents**, because it is the one
where the answer to "is that scarcity still real?" is most often no, and because getting
one repeal right buys the credibility for the rest.

Each surviving rule is typed as four owned objects, placed on a rung, and given a sunset
date. Section 6 and 7 of the question skeleton carry those questions. Two hard rules the
compiler does not negotiate: a `high-risk` rule must carry a human appeal path — **there
is no rung six** — and a repealed ritual's surviving job must be reassigned to a named
person before the repeal ships.

**The last layer — the baselines.** For every activity that will get a provisioned
skill, capture what is true today, measured, before anything is generated. Not an
estimate; a number from a record, with the record named. This is #5's provisioning gate:
no skill ships for an activity without a captured baseline, because "it got better" is
not a claim you can make later if you never wrote down what it was like.

## Finishing

Set `status: complete` and `open_question: none`, delete `_working.md`, and commit.

Then generation runs — Slice 3.3, **not built yet**. Today the interview produces a
complete, checked, resumable record of what the company decided; turning that record into
`ontologies/`, `skills/`, and `governance/` is the next thing to build, and nothing here
should be described as doing it.

## What good looks like at the end

- Every acted-on activity has an owner who is a **person**, not a role, and who knows it.
- Every automation-path activity answers all eight Gate questions. A truthful "none" is
  an answer; "N/A" is not, and there is no waiver.
- At least one activity is recorded as **not** worth automating.
- At least one rule was **repealed**, with its surviving job reassigned.
- Every provisioned skill cites a baseline captured before it was provisioned.
- The person can read the confirmed layers and recognize their own company.
````

- [ ] **Step 2: Gate**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Every link resolves (`questions.md` does not exist yet — **this step is expected to ERROR on that one broken link**; it is fixed by Task 2. If you would rather not carry a red gate between tasks, write Task 2's file first and run this once.)

> **Deliberate red, named:** `interview/protocol.md` links `questions.md`, which Task 2 creates. `check_links` ERRORs until then. This is the plan's only intentional intermediate failure.

- [ ] **Step 3: Commit** (after Task 2's file exists, so the tree is green — see Task 2 Step 3)

---

## Task 2: The question skeleton

**Files:** Create `interview/questions.md`; modify `governance/worksheets/five-question-worksheet.md`.

> **Format rule:** the destination table is three canonical columns — `| Ask | Fills | Notes |` — with leading and trailing pipes, exactly three cells per row, a `|---|---|---|` delimiter, and no HTML, code spans, escapes, or inner pipes in any cell. Task 3's test parses it with `validate._canonical_row`, the same splitter the executive-view grammar uses. A non-canonical row is a test failure.

- [ ] **Step 1: Create `interview/questions.md`:**

````markdown
# The question skeleton

What to ask. [protocol.md](protocol.md) is how to ask it; [README.md](README.md) is where
the answers go.

The skeleton adapts the **intent-engineering 9-section spec** — objective, user goal,
desired outcomes, health metrics, strategic context, constraints, decision authority,
edge cases, stop rules and verification — from a single agent to an organization. Every
question names the field its answer fills, so nothing is asked twice and nothing required
goes unasked.

**How to read the `Fills` column.** `ontology:` is the function's deep record,
`exec:` its executive view, `card:` the skill's Owner's Card, `rule:` a constitution
record, `memory:` the captured baseline. A dash means the answer lands in a record's
prose rather than a field.

**`(human-only)`** marks the four answers an agent may never supply from context, no
matter how obvious they look (#6). The generator refuses to draft them.

Work the sections in order, one question at a time, per acted-on activity. Sections 1
and 2 also run once per function, for every activity, at the executive tier.

---

## 1. Objective — what is this work, and which way should it move?

| Ask | Fills | Notes |
|---|---|---|
| What does this function actually do, activity by activity? | exec:activity | Every activity, named. The executive tier is the whole list. |
| For each one: does it deserve more human time, or should it stop being hand-run? | exec:direction | up or down. Both are answers. |
| Which of these are you actually going to act on now? | — | Steer to three to five. Depth is earned by acting. |
| How should this get done — automate, build, buy, hire, or wait? | ontology:motion | The pivot. Only automate and build need the deep fields. |
| How repetitive is it, and how risky? | ontology:score_repetition, ontology:score_risk | low, medium, or high. |
| How much judgment does it take? | ontology:score_judgment | High judgment is not a veto; it is a scoping question. |
| How specific is it to this company, and how mature is the market for it? | ontology:score_company_specificity, ontology:score_market_maturity | Market maturity is the buy-versus-build tell. |
| Is this routing, sensemaking, or accountability? | ontology:work_type | Accountability work rarely leaves a person. |
| Which business process runs differently if this works? | — | The ontology record's accountability paragraph. |

## 2. User goal — who is this for?

| Ask | Fills | Notes |
|---|---|---|
| Who does this work serve, and what are they trying to get done? | — | Their job, not the agent's. |
| Say the agent's job in one sentence, from their side. | card:job | If it takes two sentences it is two skills. |

## 3. Desired outcomes — what exists afterwards?

| Ask | Fills | Notes |
|---|---|---|
| What exactly does it produce? | ontology:gate_output | A state, not an activity. Name the artifact. |
| What does good look like, stated so someone could check it? | ontology:gate_standard | If nobody can check it, it is not a standard. |
| How will you know this actually improved? | card:success_standard | Must reference the baseline in section 4. |

## 4. Health metrics — what must not get worse?

| Ask | Fills | Notes |
|---|---|---|
| How could an agent hit that standard in a way you would hate? | card:known_failure_modes | The Goodhart question. Ask it out loud. |
| What must not degrade while this gets better? | — | Recorded in prose; groundwork has no dedicated field yet. |
| What is true today, measured, from a record rather than an estimate? | memory:source, memory:valid_at | The pre-provisioning baseline. #5 gates on it. |
| Who owns that baseline, and when should it be re-checked? | memory:owner, memory:review_by | An unowned baseline is drift with a number on it. |

## 5. Strategic context — where does this sit?

| Ask | Fills | Notes |
|---|---|---|
| Which systems hold the truth for this work? | ontology:substrate | If there is no system of record, that is the finding. |
| What does it read before it starts? | ontology:gate_inputs | Everything, including what it reads and discards. |
| When two systems disagree, which one wins? | ontology:gate_source_of_truth, card:source_of_truth | These two must match exactly. |
| Is this one agent, a team of them, or just a better chat? | ontology:shape | dont-bother is a legitimate answer. |

## 6. Constraints — what may it do, and what may it never?

| Ask | Fills | Notes |
|---|---|---|
| What may it do freely, without asking? | card:allowed_actions | Observable from the skill; still confirm it. |
| What may it never do? | card:forbidden_actions | (human-only) The refusal list comes from a person. |
| What may it propose but never perform? | card:proposed_only_actions | The most useful column on the card. |
| What must it never treat as a source of truth? | card:sources_must_not_use | Recollection and chat threads, usually. |
| What principle is that boundary protecting? | rule:value | The value half of the rule. |
| What actually stops it at that boundary? | rule:runtime_check | Trigger, evidence, action. |

## 7. Decision authority — who decides, and how far can it go?

| Ask | Fills | Notes |
|---|---|---|
| Is this read-only, reversible, external-side-effect, or high-risk? | card:action_class | Classify by mechanism, never by how it feels. |
| Who is accountable for proving this improved? One name. | ontology:accountable_owner, ontology:gate_owner, card:owner | (human-only) A role is not an owner. |
| Who covers when that person is away? | card:backup_owner | (human-only) Shared responsibility is often none. |
| Which rung does the rule sit on? | rule:rung | value, instruction, reminder, hard-block, human-decision. |
| Who owns the rule itself? | rule:owner | The person who answers for it existing. |
| Who owns the principle, and who owns the check? | rule:value_owner, rule:runtime_check_owner | They are often different people. |
| When this rule blocks somebody, who can they appeal to? | rule:human_appeal, rule:human_appeal_owner | A high-risk rule must have one. There is no rung six. |

## 8. Edge cases — what happens when it goes wrong?

| Ask | Fills | Notes |
|---|---|---|
| What should stop this rather than have it guess? | card:pause_condition | (human-only) A death condition. |
| Where does an exception go, and to whom? | ontology:gate_exception_path | Name a person, not a queue. |
| What does a mistake cost, and who notices it first? | ontology:gate_error_cost | If nobody notices, the review gate is wrong. |

## 9. Stop rules and verification — how do you know, and when do you stop?

| Ask | Fills | Notes |
|---|---|---|
| Who checks the output, and at what moment? | ontology:gate_review_gate | Before the output is used, not after. |
| What evidence must every run leave behind? | card:evidence_required | Required at external-side-effect and high-risk. |
| Which runs get read by a person, and how many? | card:review_sample | A sample nobody reads is not a sample. |
| How often is this whole thing reviewed? | card:review_cadence | Freshness warns; it never blocks. |
| What would make you turn this off? | card:retirement_condition | (human-only) Some agents should die. |
| When does this rule expire unless somebody renews it? | rule:sunset | Every rule gets one. |

---

## The constitution pass

Run once the functions are mapped, per ritual, starting with the rule everybody resents.
This is the [five-question worksheet](../governance/worksheets/five-question-worksheet.md)
with its destinations attached.

| Ask | Fills | Notes |
|---|---|---|
| Name the ritual, in plain words. What do we actually do? | rule:ritual | Not what the policy says. What happens. |
| What was expensive or rare when this started? | rule:scarcity | Somebody's attention, usually. |
| Is that scarcity still real, and what job survives if it is not? | rule:surviving_job | The job almost always outlives the ritual. |
| Rewrite it as a rule a person can verify. | — | The rule record's title and body. No vibes. |
| Decide the machinery, and where it sits on the ladder. | rule:runtime_check, rule:rung | Trigger, evidence, action, owner, appeal. |
| If this repeals a ritual, who picks up the surviving job? | rule:reassigned_to | Orphan-prohibition. Named before the repeal ships. |
| What action class is this rule about? | rule:action_class | Drives the no-rung-six safety invariant. |

## What the generator fills in without asking

Not everything is an interview question. These are drafted from what the interview
already captured, and confirmed at review rather than asked (#6's drafting split):

- `card:last_reviewed` and `card:next_review` — date stamps, written at generation.
- `SKILL.md`'s `name`, `description`, `provisioned`, `baseline`, `ontology` — all
  derivable from the record the skill was generated for.
- `memory:provenance` — set by *how* the fact was learned, not by asking.

Everything else in the schema is asked above. Task 3's test proves it.
````

- [ ] **Step 2: Add the caller to `governance/worksheets/five-question-worksheet.md`.** Append after the numbered list, before the orphan-prohibition paragraph:

```markdown
**Who runs this.** The interview does, once the functions are mapped — see
[the constitution pass](../../interview/questions.md) for these five questions with the
field each answer fills, and [the protocol](../../interview/protocol.md) for when in the
interview they get asked.
```

- [ ] **Step 3: Gate + commit both tasks**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0 — the Task 1 link now resolves.

```bash
git add interview/protocol.md interview/questions.md governance/worksheets/five-question-worksheet.md
git commit -m "feat(interview): the consultant protocol and the 9-section question skeleton

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The two tests that keep the documents honest

**Files:** Modify `tests/test_validate.py`.

> Prose is the one artifact this repo has no gate for, and these two tests are the closest thing to one. The first makes the state-format docs' examples executable; the second binds the question bank to the schema in both directions.

- [ ] **Step 1: Test one — the docs' worked examples validate.**

`interview/README.md` (Slice 3.1) ships example blocks for the manifest, a layer, and the working file. Nothing checks them, so they can drift from the schema silently and the first person to hit it is an adopter copying an example that fails the gate. Add to `tests/test_validate.py`:

```python
class TestInterviewDocExamples(unittest.TestCase):
    """The state-format doc ships example files. Nothing checked them, so they
    could drift from the schema silently — and the first person to notice would
    be an adopter copying an example that fails the gate. Extract them and run
    the real check."""

    # Blocks are labelled in the doc by the filename they demonstrate, in the
    # fence info string: ```markdown 00-manifest.md
    _BLOCK = re.compile(
        r"^```[a-z]*[ \t]+(00-manifest\.md|_working\.md|[0-9]{2}-[a-z-]+\.md)[ \t]*\n"
        r"(.*?)^```[ \t]*$",
        re.S | re.M)

    def test_readme_examples_validate(self):
        doc = (REPO / "interview" / "README.md").read_text()
        blocks = dict((m.group(1), m.group(2)) for m in self._BLOCK.finditer(doc))
        # Anti-hollow: an empty extraction validates an empty directory and passes.
        self.assertIn("00-manifest.md", blocks,
                      "no labelled manifest example found in interview/README.md — "
                      "the extractor found nothing, so this test proves nothing")
        self.assertGreaterEqual(len(blocks), 3, "expected manifest + layer + working")
        with tempfile.TemporaryDirectory() as d:
            state = os.path.join(d, "interview")
            os.makedirs(state)
            for name, body in blocks.items():
                with open(os.path.join(state, name), "w", encoding="utf-8") as fh:
                    fh.write(body)
            findings = validate.check_interview_state(d)
        self.assertEqual([f for f in findings if f.level == "ERROR"], [],
                         "the documented example does not satisfy the check it documents")
```

> **The doc must be edited to match.** `interview/README.md`'s three example fences currently carry a bare `markdown` info string. Change them to `markdown 00-manifest.md`, `markdown 02-customer-success.md`, and `markdown _working.md`, and fill the placeholder angle brackets with values that actually validate (a real ISO date, a real `layers:` list naming `02-customer-success.md`, matching `open_question` values in the manifest and the working file). **A documented example that does not pass is the finding, not the test.**

- [ ] **Step 2: Test two — the question bank covers the schema, both directions.**

```python
class TestQuestionSkeletonCoverage(unittest.TestCase):
    """The interview must be able to fill every field the validator requires. A
    schema field nobody asks about is a record the generator cannot complete;
    a question naming a field that does not exist is a question whose answer
    lands nowhere. Both directions are silent failures without this test.

    #5's 'all eight Gate fields must be answered, and there is no waiver' is
    enforced at the validator end. This is the same rule at the interview end."""

    # Fields the generator draws from what it already captured rather than
    # asking — #6's drafting split, encoded. Each entry needs a reason.
    NOT_ASKED = {
        "card:last_reviewed": "date stamp written at generation",
        "card:next_review": "date stamp written at generation",
        "memory:provenance": "set by how the fact was learned, not by asking",
    }

    # Mirrors check_memory's required spine. Update together — validate.py has
    # no constant for it (candidate for extraction next time memory changes).
    MEMORY_SPINE = ("provenance", "owner", "valid_at", "source", "review_by")

    def _fills(self):
        doc = (REPO / "interview" / "questions.md").read_text()
        fills, rows = set(), 0
        for line in doc.split("\n"):
            cells = validate._canonical_row(line)
            if cells is None:
                # A '|' outside a canonical row means the table grammar slipped.
                self.assertNotIn("|", line,
                                 "non-canonical table line in questions.md: %r" % line)
                continue
            if cells[0] in ("Ask", "") or set(cells[1]) <= set("- "):
                continue  # header or delimiter
            rows += 1
            for f in cells[1].split(","):
                f = f.strip()
                if f and f != "—":
                    fills.add(f)
        self.assertGreater(rows, 30, "the question table parsed almost nothing")
        return fills

    def test_every_named_field_exists(self):
        known = set()
        for f in validate.SCORE_FIELDS + validate.GATE_FIELDS:
            known.add("ontology:" + f)
        for f in ("motion", "work_type", "accountable_owner", "substrate", "shape"):
            known.add("ontology:" + f)
        for f in validate.CARD_REQUIRED + validate.CARD_TRACK2 + ["action_class"]:
            known.add("card:" + f)
        for f in validate._RULE_OBJECT_FIELDS + ["owner", "rung", "action_class",
                                                 "sunset", "ritual", "scarcity",
                                                 "surviving_job", "reassigned_to"]:
            known.add("rule:" + f)
        for f in self.MEMORY_SPINE:
            known.add("memory:" + f)
        known |= {"exec:activity", "exec:direction"}
        unknown = self._fills() - known
        self.assertEqual(unknown, set(),
                         "questions.md names fields the schema does not have: %s" % sorted(unknown))

    def test_every_required_field_is_asked(self):
        fills = self._fills()
        required = set()
        for f in validate.SCORE_FIELDS + validate.GATE_FIELDS:
            required.add("ontology:" + f)
        for f in ("motion", "work_type", "accountable_owner", "substrate", "shape"):
            required.add("ontology:" + f)
        for f in validate.CARD_REQUIRED + validate.CARD_TRACK2:
            required.add("card:" + f)
        for f in validate._RULE_OBJECT_FIELDS + ["owner", "rung", "sunset"]:
            required.add("rule:" + f)
        for f in self.MEMORY_SPINE:
            required.add("memory:" + f)
        missing = required - fills - set(self.NOT_ASKED)
        self.assertEqual(missing, set(),
                         "the schema requires fields no question asks for: %s — either "
                         "add the question or add it to NOT_ASKED with a reason"
                         % sorted(missing))
```

> Add `import tempfile` / `import os` / `import re` to the test module only if they are not already imported. **Do not add a dependency.**

- [ ] **Step 3: Prove both tests are load-bearing** (deliberate reds, then revert)

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
q = pathlib.Path("interview/questions.md")
orig = q.read_text()
q.write_text(orig.replace("ontology:gate_error_cost", "ontology:gate_error_kost", 1))
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestQuestionSkeletonCoverage"],
                   capture_output=True, text=True)
q.write_text(orig)
assert r.returncode != 0, "a typo'd field name passed — the coverage test is not reading the table"
print("OK: a field the schema does not have fails the build")
PY
```

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
q = pathlib.Path("interview/questions.md")
orig = q.read_text()
q.write_text(orig.replace("| card:evidence_required |", "| — |", 1))
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestQuestionSkeletonCoverage"],
                   capture_output=True, text=True)
q.write_text(orig)
assert r.returncode != 0, "a required field with no question passed — the coverage direction is dead"
print("OK: a required field nobody asks about fails the build")
PY
```

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
d = pathlib.Path("interview/README.md")
orig = d.read_text()
d.write_text(orig.replace("provenance: confirmed", "provenance: inferred", 1))
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestInterviewDocExamples"],
                   capture_output=True, text=True)
d.write_text(orig)
assert r.returncode != 0, "a broken documented example passed — the extractor found nothing"
print("OK: the documented examples are executable")
PY
```

Each must print its `OK:` line. **A probe that passes without the planted break means the test is reading nothing** — stop and fix the extractor before continuing.

- [ ] **Step 4: Gate + commit**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"` — green; count is up from 662.
Run: `python3 scripts/validate.py . ; echo "exit: $?"` — exactly `0 error(s), 7 warning(s)`, exit 0.

```bash
git add tests/test_validate.py interview/README.md
git commit -m "test: the interview docs are executable — examples validate, questions cover the schema

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Honesty and the full gate

**Files:** Modify `AGENTS.md`, `docs/known-limitations.md`.

- [ ] **Step 1: Update `AGENTS.md`.** Replace the `interview/` bullet under "Built and working" with:

```markdown
- `interview/` — the interview's **state format** (#9: a fixed `00-manifest.md`, one
  frozen file per confirmed layer, one dirty `_working.md`), the **consultant protocol**
  (§4: define-the-role-first, one question at a time, evidence-based reading, checkpoint
  approvals), and the **question skeleton** — the intent-engineering 9 sections mapped
  onto the fields each answer fills. A test holds the skeleton to the schema in both
  directions, so a required field nobody asks about fails the build.
```

Replace the `interview/` bullet under "Not built yet" with:

```markdown
- `interview/` — the **generator**. The protocol and the questions exist and a person can
  run the interview by hand with an agent; turning the confirmed layers into
  `ontologies/`, `skills/`, and `governance/` is Slice 3.3. **Nothing generates a company
  OS today.**
```

Update the map table's `interview/` row to:

```markdown
| `interview/` | The state format (#9), the consultant protocol (§4), and the question skeleton. The generator is not built. |
```

And in "The interview (not built — Phase 3)", replace the closing paragraph with:

```markdown
**The generator does not exist yet.** What exists is everything up to it: the state
format (`interview/README.md`), the protocol (`interview/protocol.md`), and the question
skeleton (`interview/questions.md`), with `demo/interview/` as a worked example. A person
can run this interview by hand today and get a checked, resumable record. Turning that
record into a company OS is Slice 3.3 — anything describing that step as working is wrong.
```

> **`wc -l AGENTS.md` must stay under 200.** It is at 149; this adds roughly ten lines.

- [ ] **Step 2: Record the health-metrics gap in `docs/known-limitations.md`.** Append to the section covering the schema (or add one titled `## The interview (#9, §4)`):

```markdown
- **The schema has no field for "what must not degrade".** The question skeleton asks the
  Goodhart question — *how could an agent hit this standard in a way you would hate?* —
  because the intent-engineering 9-section spec makes health metrics a first-class
  section. groundwork has `success_standard` (what good looks like, against a captured
  baseline) and `known_failure_modes` (what has gone wrong), but no field for the thing
  that must not get worse while the standard is met. The answer is recorded in prose on
  the Owner's Card and the ontology record instead. Adding a field is a `SCHEMA_VERSION`
  bump now that `demo/` carries a pin, so it is named here as the **first candidate for a
  v2 schema change** rather than spending the first migration on one field.
- **Nothing checks interview prose.** `check_interview_state` validates the *shape* of
  what an interview captured, not whether the interview was any good — whether the role
  was defined first, whether questions came one at a time, whether a confirmed fact was
  actually confirmed by the person named. Those are properties of a conversation, and no
  file check can see them. The two engine tests cover what can be mechanized: that the
  documented examples validate, and that the question skeleton can fill every required
  field.
```

- [ ] **Step 3: The full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"` — green; record the final count.
Run: `python3 scripts/validate.py . ; echo "exit: $?"` — exactly `0 error(s), 7 warning(s)`, exit 0.
Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"` — exit 0. This slice touches no `demo/` content, so the frozen-layer guard and the #18 tripwire both stay quiet; if either fires, something under `demo/` was edited.
Run: `wc -l AGENTS.md` — under 200.

Run the coverage report, so the mapping is visible rather than asserted:

```bash
python3 - <<'PY'
import sys, re; sys.path.insert(0, 'scripts'); import validate
doc = open('interview/questions.md').read()
fills = set()
rows = 0
for line in doc.split("\n"):
    c = validate._canonical_row(line)
    if not c or c[0] in ("Ask", "") or set(c[1]) <= set("- "):
        continue
    rows += 1
    fills |= {x.strip() for x in c[1].split(",") if x.strip() and x.strip() != "—"}
print("question rows parsed:", rows)
print("distinct fields filled:", len(fills))
for ns in ("exec", "ontology", "card", "rule", "memory"):
    print("  %-9s %d" % (ns, len([f for f in fills if f.startswith(ns + ":")])))
PY
```

Expected: 30+ rows, 40+ distinct fields, every namespace non-zero. A zero anywhere means the table stopped parsing partway.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md docs/known-limitations.md
git commit -m "docs: the interview can be run by hand; the generator still cannot

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No generator.** Slice **3.3**: reading the confirmed layers and writing `ontologies/`,
  `skills/`, `governance/` in the demo-proven shape, plus #10's two-repo semantics and the
  refusal to run while `status: in-progress`. This slice writes the questions; it does not
  write the answers into records.
- **No schema change.** The health-metrics gap is documented, not filled — filling it is a
  v2 bump under the promise that started binding on 2026-07-29.
- **No `demo/` edits.** The demo's interview layers are frozen and its skills and rules are
  governed. This slice touches neither.
- **No validator changes.** Two tests, no checks.
- **Still open for the maintainer:** the Phase 3 re-ordering sign-off (treated as accepted
  by the 3.1 merge — say so if not), Codex's 3.1 finding 1 (whether an absent `layers:` key
  should ERROR rather than read as an empty just-started interview), the health-metrics
  call above, three Slice 1.5d-ii deferrals, the `SKIP_RELPATHS` sign-off, the standing
  re-review rule, the `Motion: assist` reading, and the two 2.3d carry-overs.

## Self-Review

- **Ticket coverage.** Brief §4's four mechanics, each with the reason it exists rather
  than just the instruction: role-first, one-at-a-time with the no-generation rule,
  evidence-based reading with the "people report the rules they wish they had" reason and
  the `observed`/`inferred` landing, and checkpoint approvals wired to 3.1's
  promote-and-commit protocol. §4's depth doctrine (three to five acted-on activities) and
  #10's private-repo-first act are both in the protocol. #6's generator refusal is encoded
  twice — as the protocol's no-human rule and as `(human-only)` marks in the question map.
  #8's five-question worksheet gains its caller and its destination fields. #5's Motion
  pivot and the no-waiver Gate are both stated where an interviewer will hit them.
- **The live tool was run, and it changed the artifact** (wwf5d §1.3/§5.2). The
  `intent-engineering` scaffold was generated on 2026-07-29 rather than working from the
  brief's summary of it, which turned out to list **seven** of the nine sections — *user
  goal* and *strategic context* were missing. Both map onto fields groundwork already
  collects, so the correction costs nothing but would have been invisible from the brief
  alone.
- **Design calls surfaced, not buried.** Five, each with the rejected option: the
  nine-section correction; the question-bank-as-field-map (which is what makes 3.3
  mechanical); the health-metrics gap left as prose rather than spending the first
  migration gate on one field; the interview as documents rather than a skill, with the
  mechanical reason it cannot be a skill; and the no-human rule answered in the strict
  direction.
- **Prose is the artifact with no gate — so this slice builds two.** The first makes the
  state-format doc's examples executable, closing a gap 3.1 shipped (example blocks that
  nothing checked). The second binds the question bank to `validate.py`'s own field
  constants in **both** directions: a question naming a field that does not exist fails,
  and a required field no question asks about fails. That second direction is #5's
  "no waiver mechanism" moved to the interview end, and it is the thing that would
  otherwise rot silently as the schema evolves.
- **Anti-hollow probes.** Three planted violations, each asserting the test *fails*: a
  typo'd field name, a required field with its question removed, and a broken documented
  example. Plus two in-test guards — `assertIn("00-manifest.md", blocks)` and
  `assertGreater(rows, 30)` — because an extractor that finds nothing validates an empty
  directory and passes, which is this slice's single most likely way to ship hollow. The
  final coverage report prints the parsed row and field counts so the mapping is visible
  rather than asserted.
- **The one deliberate red is named.** `interview/protocol.md` links `questions.md` before
  Task 2 creates it, so `check_links` ERRORs between the two tasks; the plan says so and
  offers the alternative ordering.
- **The named cut line.** If the question bank runs long it becomes Slice 3.2b — and what
  defers is Task 3's coverage test plus the remaining rows, never the protocol/questions
  pairing, because splitting *those* re-creates the inert-prose problem the Phase 3
  re-ordering existed to avoid.
- **No second table grammar.** The question table is three canonical columns parsed with
  `validate._canonical_row` — the splitter the executive-view grammar already uses, with
  its escape/HTML/code-span ban intact. A non-canonical row is a test failure, not a
  tolerated variant. The 2.2a lesson applied rather than re-learned.
- **Placeholder scan:** no TBD/TODO. Both new files are given in full; both tests are
  given in full; every modification quotes its replacement text.
- **Pre-empts the recurring findings.** (a) *Vacuous parse* — covered by the two in-test
  guards and the three probes. (b) *Maintenance link* — `MEMORY_SPINE` is a literal in the
  test because `validate.py` has no constant for it; the comment says so and names
  extraction as the fix next time memory's schema changes, rather than leaving a silent
  mirror. (c) *Honesty* — `AGENTS.md` moves `interview/` from "not built" to "the
  generator is not built", and says plainly that a person can run this by hand today,
  which is true and testable, while nothing claims generation works. (d) *Known
  limitations* — both real limits are written down: the missing health-metric field, and
  the fact that no check can tell whether an interview was conducted well.
