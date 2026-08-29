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
says so (the ordering rules below name the commonest cases; the rule holds for every
required field, named or not).

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

**The file grammars live in the engine, not here.** The validator accepts one canonical
shape for each artifact, and this document names fields rather than showing files: the
executive-view table is specified in [../ontologies/README.md](../ontologies/README.md),
the card spine in [../skills/work-package-spec.md](../skills/work-package-spec.md), the
memory-record schema in [../memory/README.md](../memory/README.md), the rule objects in
[../governance/README.md](../governance/README.md), and the pin file in
[../MIGRATIONS.md](../MIGRATIONS.md). Read the shape before writing to it.

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
`schema_version: 1`. The pin is a frontmatter-fenced file — the two keys between two
`---` lines, exactly as [../MIGRATIONS.md](../MIGRATIONS.md) shows; bare `key: value`
lines with no fences fail the gate. Write the file at the end: once it exists the repo is a governed
root, and every skill and rule you add after that is an escalating change wanting a
proposal (#18). Generate under the pin and you will write a proposal per file. Which
commit the gate measures *from*, and why the write order inside it does not change
what the gate sees, is in "Then prove it".

**2. `ontologies/` first.** Every function gets an `_executive-view.md` listing every
activity with a Direction — that is the whole executive tier, and most activities never
get more. Then one deep record per acted-on activity.

The **Motion is the pivot**: `automate` and `build` carry the common core *plus*
Substrate, Shape, and all eight Describability Gate fields. `buy`, `hire`, and `wait`
carry only the common core — Motion, the five scores, work type, and the accountable
owner — plus the grounding paragraph every deep record carries, whatever its Motion.
**Write the `wait` records.** A recorded decision not to build something is a
decision, and an ontology holding only automation verdicts reads as an automation funnel.

All eight Gate fields must be *answered*. A truthful "none" is an answer; "N/A" is not,
and there is no waiver. If a Gate answer is missing from the layers, that activity does
not get a deep record — it is named in the generation report as a question for the next
interview pass.

**Grounding and divergence carry through.** Every deep record carries a grounding
paragraph transcribed from the layer's disposition — its three dimensions and its
`practice_basis`. A claim whose basis is a general account alone carries
**unverified** wherever it appears, including the Motion rationale. A divergence
recorded in a layer lands in the record's body with its operating truth as the layer
states it — generation never resolves it, and a record that states the policy side as
practice is laundering, the same refusal class as inventing an owner. An untested
cited claim is carried as *stated in the document, untested*, never as practice.
Layers carrying no grounding dispositions are generated without grounding paragraphs,
and the report says so: "these layers carry no grounding dispositions; grounding
paragraphs not generated."

**3. `memory/` next, because skills depend on it.** Every baseline the interview captured
becomes a record: `provenance`, `owner`, `valid_at`, `source`, and `review_by` — the
interview asked when the baseline should be re-checked, and a record without that answer
is drift with a number on it (the validator WARNs). A baseline whose **owner** was never
answered does not ship as a record — `owner` is always required and a missing answer is
never filled in; name the baseline in the generation report instead. Then `_index.md`, listing
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

Exit 0 with no ERRORs. Not "looks right" — run it. Then, once the generation commit exists:

```
python3 scripts/validate.py ../<company>-os --diff <generation commit>
```

which adds the stateful modes: org-memory immutability, frozen interview layers, and the
#18 consent gate on every governed change.

**The base is the generation commit** — the one you wrote the OS in. Precondition 3
guarantees there is a history to name it against: the layers were committed, in this same
repo, before you generated. So the temptation is to reach one commit further back and diff
against the pre-generation state. Do not.

**The commit that creates the governed root is not subject to the consent gate.** #18
routes an escalating change through a reviewable proposal, and generation cannot be its
own proposal — every rule and skill in the repo arrives with the root, into a `proposals/`
this document specifies as empty at generation. Name the pre-generation commit as the base
and you ask the gate to review the act that created the thing it governs: every generated
constitution rule comes back as an escalating change with no pending proposal, and the
gate is red on a correct repo. Measured on the OS generated in the 2026-07-31
persona-company run, which carries two constitution rules: the pre-generation base returns
**2 errors, exit 1**, one per rule; the generation commit returns **0**. The write order
inside that commit is not a way out — the validator discovers `groundwork.pin` from the
working tree as well as the base tree, so putting the pin last does not keep the rules
beside it out of the changeset.

**What this run proves, and what it does not.** The comparison is the base tree against
the working filesystem, not one commit against another, and that scan does not honour
`.gitignore` — an untracked or ignored governed file is still read. Run it straight after
generation, with the working tree matching the base for every file either side holds, and
there is nothing to compare: it shows the stateful modes run clean, not that they caught
anything. Later work is what exercises them — a new rule or skill is the #18 consent
gate's case, editing or deleting a confirmed interview layer is the frozen-layer case, and
memory immutability needs a record that existed at the base to be edited or deleted, since
adding one is always fine.

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
