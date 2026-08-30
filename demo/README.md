# demo — the pre-installed example company

A complete fictional company OS. Read it without configuring anything, see the shape a
company OS takes before generating your own, and watch the validator run against real
content.

**Start with [the 15-minute walkthrough](walkthrough.md)** — three questions, asked of
an agent pointed at this repository, ending with a governance rule refusing an
instruction. Read [canon.md](canon.md) first if you want the fictional world up front;
it is also the allowlist every identifier here is checked against.

## What is here

- [`walkthrough.md`](walkthrough.md) — the three-query script. Fifteen minutes, no
  credentials.
- `canon.md` — the fictional world and the identifier allowlist.
- [`ontologies/`](ontologies/README.md) — all eight functions' executive views, four
  automation-path deep records, and finance's three recorded decisions *not* to
  automate.
- `memory/` — why engineering moved to asynchronous standups (and the superseded
  decision it replaced), two at-risk renewals and what they are blocked on, and the four
  captured baselines.
- [`skills/`](skills/README.md) — four work packages, each a `SKILL.md` plus an Owner's
  Card naming a real person, citing the baseline captured before it was provisioned.
- [`governance/`](governance/README.md) — three rules on three rungs, the
  [roster](governance/roles.md) their owners resolve against, plus
  [one runnable rule](governance/reminders/meeting-challenger/) you can pipe
  JSON into today.
- [`interview/`](interview/00-manifest.md) — the interview this OS was generated from:
  six confirmed layers, each frozen at the checkpoint a named person approved, and one
  turn still in flight. It is the record of *why* the ontology, the work packages, and
  their boundaries say what they say — the org memory the company accreted on its own
  (standups, renewal risks) traces to its records, not to these layers.
- [`proposals/`](proposals/refusal-names-next-step.md) — two pending proposals, each
  waiting on a human: one is what an agent produces when a rule tells it no, the other is
  what a change to [the roster](governance/roles.md) has to go through, because who holds
  an owner is governance rather than bookkeeping.
- `groundwork.pin` — what makes this directory a **governed** instance rather than
  example content: the validator's `--diff` mode holds changes to its skills, rules, and
  roster to the same consent gate a real company repo gets.

## What this is not

Not a template to copy. The intended path for a real company OS is generation by the
interview into its own private repository (see [AGENTS.md](../AGENTS.md), "Two repos") —
a process you can run by hand today with an agent, following `interview/`. This directory
is a worked example to read, nothing more.
