# Generating the company OS

The last act of the interview. [protocol.md](protocol.md) says how to ask,
[questions.md](questions.md) says what each answer fills, [README.md](README.md) is the
state the answers live in. This is how that state becomes an operating system.

**You are the generator.** There is no script. The confirmed layers are prose written by
a person and an agent in conversation, and the honest reader for prose is a reader — the
question skeleton already names the destination field for every answer, so this is
transcription and formatting, not interpretation. A missing answer is never filled in:
an incomplete interview stops generation entirely (precondition 1), and a gap inside a
complete one means the artifact that needed it does not ship and the generation report
says so (the ordering rules below name each case).

## Before you write anything

Four preconditions. All four, every time.

1. **The interview is complete.** `00-manifest.md` says `status: complete` and
   `open_question: none`, and there is no `_working.md`. **If the status is
   `in-progress`, stop.** Generating from provisional facts produces records that look
   confirmed and are not, and every artifact downstream inherits that.
2. **You are in the company's private repo**, not the groundwork clone. The engine is
   pull-only and nothing organizational is ever written into it (#10).
3. **The layers are committed.** Uncommitted state means the checkpoints are not what
   the manifest says they are.
4. **You have read every confirmed layer.** All of them, before writing the first file.
   A record generated from one layer while a later layer contradicts it is the kind of
   error nobody finds until it matters.

## What you write

```
<company>-os/
  AGENTS.md                       the root instruction file — routing, not content
  CLAUDE.md                       one line: @AGENTS.md
  GEMINI.md                       one line: @./AGENTS.md
  .cursor/rules/company.mdc       alwaysApply pointer to AGENTS.md
  groundwork.pin                  schema_version + generated_by_commit
  ontologies/
    README.md                     what the two tiers mean here
    <function>/_executive-view.md  every activity, with a Direction
    <function>/<activity>.md       a deep record per acted-on activity
  skills/
    <name>/SKILL.md               one per provisioned activity
    <name>/owner-card.md          its Owner's Card
  governance/
    constitution/<rule>.md        one file per kept rule
    changelog.md                  append-only, header only at generation
    review-gate.md                the #19 review-gate instruction, as prose
  memory/
    _index.md                     live records only
    <record>.md                   the captured baselines, at minimum
  proposals/                      empty at generation; pending-only forever
  interview/                      the confirmed layers, retained
```

**A company repo links only inside itself.** Never write a link that climbs out of the
repo root — an engine path resolves on the machine that generated it and nowhere else.
Where you want to explain a convention, state it, or point at the engine by name in
prose. This is the one formatting rule that a reader will not catch for you.

## The order, and why it is this order

Generate in dependency order, and run the validator between stages rather than at the
end. A gate that goes red after four hundred lines tells you less than one that goes red
after twenty.

**1. `groundwork.pin` last — but decide it first.** Record which engine commit you
generated against (`git -C <engine clone> rev-parse --short HEAD`) and
`schema_version: 1`. Write the file at the end: once it exists the repo is a governed
root, and every skill and rule you add after that is an escalating change wanting a
proposal (#18). Generate under the pin and you will write a proposal per file.

**2. `ontologies/` first.** Every function gets an `_executive-view.md` listing every
activity with a Direction — that is the whole executive tier, and most activities never
get more. Then one deep record per acted-on activity.

The **Motion is the pivot**: `automate` and `build` carry the common core *plus*
Substrate, Shape, and all eight Describability Gate fields. `buy`, `hire`, and `wait`
carry only the common core — Motion, the five scores, work type, and the accountable
owner. **Write the `wait` records.** A recorded decision not to build something is a
decision, and an ontology holding only automation verdicts reads as an automation funnel.

All eight Gate fields must be *answered*. A truthful "none" is an answer; "N/A" is not,
and there is no waiver. If a Gate answer is missing from the layers, that activity does
not get a deep record — it is named in the generation report as a question for the next
interview pass.

**3. `memory/` next, because skills depend on it.** Every baseline the interview captured
becomes a record: `provenance`, `owner`, `valid_at`, `source`, and `review_by` — the
interview asked when the baseline should be re-checked, and a record without that answer
is drift with a number on it (the validator WARNs). Then `_index.md`, listing
live records only. A skill cannot provision without a baseline, so these exist before the
skills that cite them.

**4. `skills/` — one work package per provisioned activity.** `SKILL.md` carries `name`,
`description`, `action_class`, `provisioned`, `baseline`, and `ontology`; `owner-card.md`
carries the spine, plus the track-2 trio when the action class is external-side-effect or
high-risk.

Two exact-match obligations that a reader will not notice and the validator will: the
card's `owner` must equal the ontology record's `accountable_owner` **character for
character**, and the card's `source_of_truth` must equal `gate_source_of_truth` the same
way. Copy them; do not retype them.

**What you must not invent.** Five fields come only from a human's answer (#6):

- `owner` and `backup_owner`
- `forbidden_actions`
- `pause_condition` and `retirement_condition`

They are marked `(human-only)` in [questions.md](questions.md). If a layer does not carry
one, **the skill does not ship** — write it `provisioned: no` and record the missing
answer in the generation report. An invented owner is an accountability structure the
named person will discover when something goes wrong, and an invented forbidden action
is a boundary nobody agreed to.

**5. `governance/constitution/` — one file per kept rule.** Four owned objects (value,
rule, runtime check, human appeal, each with its owner), a rung, and a sunset date. Two
things the compiler does not negotiate: a `high-risk` rule must carry a human appeal path
with an owner — **there is no rung six** — and a repealed ritual's surviving job must be
reassigned to a named person before the repeal ships.

Then `changelog.md` with its header and no entries, and `review-gate.md` — the prose form
of the action-class rule, the instruction every harness that ignores hooks falls back to.
An instruction is not enforcement: on day one a generated repo has a review gate an agent
is told to honor, and runtime enforcement only once a maintainer installs the runnable
gate. That gate is **not** copied here; see "What stays in the engine".

**6. The root files.** `AGENTS.md` is **routing, not content**: what this repo is, the
function map, the skill roster with owners and action classes, where memory and rules
live, and how to propose a change. Every session pays for it before anyone types
anything, so it points and does not explain — the ontology records hold the detail.
`CLAUDE.md` is exactly `@AGENTS.md` on its own first content line, because Claude Code
reads `CLAUDE.md` and not `AGENTS.md`. `GEMINI.md` is `@./AGENTS.md` for the same reason —
Gemini CLI's default context filename is `GEMINI.md` and it does not read `AGENTS.md`
either (verified 2026-07-29). `.cursor/rules/company.mdc` carries `alwaysApply: true` and
references `AGENTS.md`. Codex and Cursor read `AGENTS.md` natively, so they need no
pointer.

**One more line in `AGENTS.md`, and it is a legal one.** State that the contents of this
repository are the company's own work, generated with groundwork and not covered by
groundwork's Apache-2.0 license. groundwork's own README says this; the promise is only
worth something if the repository holding the content says it too, which is why it is
written here rather than assumed.

**7. `interview/` stays.** The confirmed layers are the record of why this OS says what
it says, and the substrate a re-interview would merge against. Keep them.

## Then prove it

From the engine clone:

```
python3 scripts/validate.py ../<company>-os
```

Exit 0 with no ERRORs. Not "looks right" — run it. Then, once the repo has one commit:

```
python3 scripts/validate.py ../<company>-os --diff <base>
```

which adds the stateful modes: org-memory immutability, frozen interview layers, and the
#18 consent gate on every governed change.

**Say what you generated and what you could not.** A list of the activities that got deep
records, the skills that shipped `provisioned: no` and why, and every question still
open — including the ones generation itself surfaced, a missing Gate answer or an
unanswered human-only field. Answering them is a **new interview turn** under the state
format ([README.md](README.md)) — a fresh `_working.md` and a later layer — never an edit
to a frozen one. A generation report that claims completeness it does not have is the
one output worse than an incomplete repo.

## What stays in the engine

The company repo is **content plus a pin**. The validator, the schemas, and the fixed
action-class gate stay in the groundwork clone, and upstream improvements arrive by
`git pull` there — nothing is ever re-copied (#10). That promise is why the runnable hook
set is not written into the company repo: a copied enforcement script goes stale silently,
and a company running last quarter's gate while believing it runs the engine's is worse
off than one that knows it has a review gate.

Installing the runnable gate is a deliberate maintainer act with a re-copy obligation
attached — the provisioning guide covers it (`delivery/`).
