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
  [one runnable rule](governance/reminders/meeting-challenger/) you can pipe JSON into
  today.

## What is coming

- The 15-minute walkthrough script, the version pin that puts this directory under the
  same governance the validator applies to a real company repo, and one live pending
  proposal.

The walkthrough is not usable yet: there is no script to follow, and the three queries
it will run are not written. Everything above is content you can read and check —
`python3 scripts/validate.py .` from the repository root validates this directory as
its own instance — not a demo you can run.

## What this is not

Not a template to copy. The intended path for a real company OS is generation by the
interview into its own private repository (see [AGENTS.md](../AGENTS.md), "Two
repos") — and that interview is Phase 3, not built yet. This directory is a worked
example to read, nothing more.
