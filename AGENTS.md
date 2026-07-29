# AGENTS.md — groundwork

**groundwork is an open-source, harness-agnostic Company OS.** It is files, not an
engine: markdown conventions plus one zero-dependency validator. Any coding agent that
reads a repository can read this one.

This file is the canonical instruction surface for agents working in or with this
repository. `CLAUDE.md` is a one-line import of it; `.cursor/rules/groundwork.mdc`
points here too. Edit **this** file — the others are pointers.

## Status — what is real today

The design is fully charted (19 resolved decisions; see `CONTEXT.md`). Phase 1 is
complete and Phase 2.2 extends it: the schema exists as files, three functions are
worked end to end across both governance tracks, one function records a deliberate
non-automation verdict, and the validator gates every layer of it.

**Built and working:**

- `scripts/validate.py` — the gate. Python 3 standard library only, no dependencies.
- `ontologies/` — the two-tier ontology schema, all 8 function executive views, and
  four worked deep records: three on the automation path (People/HR onboarding,
  customer-success renewal prep, product feature-request triage) and one recording a
  deliberate decision *not* to automate (engineering hiring loops, `Motion: hire`).
- `skills/` — the work-package convention and three worked packages: one
  external-side-effect (`onboarding-orchestration`) and two reversible-write
  (`renewal-prep`, `feature-request-triage`), each with its `SKILL.md` and
  `owner-card.md`.
- `governance/` — the constitution rule schema with one compiled rule, the
  action-class hook set, and the append-only changelog.
- `memory/` — the org-memory record schema with three captured baselines and an index.
- `interview/` — the interview's **state format** (#9: a fixed `00-manifest.md`, one
  frozen file per confirmed layer, one dirty `_working.md`), the **consultant protocol**
  (§4: define-the-role-first, one question at a time, evidence-based reading, checkpoint
  approvals), and the **question skeleton** — the intent-engineering 9 sections mapped
  onto the fields each answer fills. A test holds the skeleton to the schema in both
  directions, so a required field nobody asks about fails the build.
- `proposals/` — the consent-gate convention for agent-proposed changes.
- `demo/` — the pre-installed example company (**Umbercress**, ~20 people), complete:
  canon, eight executive views, seven deep records, org memory, four work packages,
  three constitution rules, one runnable rung-3 reminder, one pending proposal, and the
  15-minute three-query walkthrough. It carries a `groundwork.pin`, so it is a
  **governed root** — changes to its skills and rules run the #18 consent gate exactly
  as a company repo's would.

**Not built yet — do not describe these as working:**

- `interview/` — the **generator**. The protocol and the questions exist and a person can
  run the interview by hand with an agent; turning the confirmed layers into
  `ontologies/`, `skills/`, and `governance/` is Slice 3.3. **Nothing generates a company
  OS today.**
- `delivery/` — the provisioning guide. Phase 4.
- `your-company/` — generated content lives in a **separate private repo**, not here.

## The map

| Path | What it holds |
|---|---|
| `CONTEXT.md` | The glossary. Every resolved decision's vocabulary. Read this first. |
| `ontologies/` | One directory per function. All 8 executive views; `people-hr/`, `customer-success/`, `product/`, and `engineering/` also carry a worked deep record. |
| `skills/` | Work packages: `skills/<name>/SKILL.md` + `owner-card.md`. |
| `governance/` | `constitution/` (typed rules), `hooks/` (the action-class gate), `changelog.md`. |
| `memory/` | Org-memory records, one per file, with an index. |
| `interview/` | The state format (#9), the consultant protocol (§4), and the question skeleton. The generator is not built. |
| `proposals/` | Pending improvement proposals. Empty by design — proposals are transient. |
| `scripts/validate.py` | The validator. Run it before you claim anything is done. |
| `MIGRATIONS.md` | The version-pin contract and the pull promise. |
| `docs/known-limitations.md` | What this does **not** do. Read before relying on a check. |

## How to use this repository today

Run the gate:

```
python3 scripts/validate.py .
```

Exit 0 means no ERRORs. WARNs print but do not fail. To check a company repo from
this engine clone, pass its path instead of `.`.

Check governed changes against a base revision:

```
python3 scripts/validate.py . --diff main
```

This adds the stateful modes: org-memory immutability, frozen interview layers, and the
blast-radius tripwire that requires an escalating change to carry a matching proposal.

To see what this is for rather than how it is built, run the demo's three-query
walkthrough — fifteen minutes, no credentials, ending on a governance rule refusing an
instruction: `demo/walkthrough.md`.

To understand the shape before writing anything, read one worked example end to end:
`ontologies/people-hr/onboarding-orchestration.md` →
`skills/onboarding-orchestration/SKILL.md` → its `owner-card.md` →
`memory/onboarding-baseline.md` → `governance/constitution/`.

## The interview (not built — Phase 3)

The intended entry point is an interview: you point your agent at this repo, it asks
your company what work each function actually does — what deserves more human time,
what should be automated, and under what rules — and generates your operating system
from that map into a separate private repository.

**The generator does not exist yet.** What exists is everything up to it: the state
format (`interview/README.md`), the protocol (`interview/protocol.md`), and the question
skeleton (`interview/questions.md`), with `demo/interview/` as a worked example. A person
can run this interview by hand today and get a checked, resumable record. Turning that
record into a company OS is Slice 3.3 — anything describing that step as working is wrong.

## Two repos

The public groundwork clone is the **engine** — pull-only, never edited by an adopter.
A company's OS lives in a **separate private repo** carrying content plus a
`groundwork.pin`. The validator runs from the engine clone against that repo.
Upstream improvements arrive by `git pull` on the engine; content is never re-copied.

## Conventions that bind

- **Files, not engines.** No runtime, no server, no database. Conventions plus checks.
- **Content is checked wherever it lives.** Any directory carrying `ontologies/`,
  `skills/`, `governance/`, `proposals/`, or `memory/` is validated as its own
  instance, with references resolving inside it. That is what lets `demo/` be a
  faithful model of a company repo rather than a folder borrowing this one's examples.
- **Zero dependencies.** `scripts/validate.py` and every shipped script import the
  Python standard library only. There is no `requirements.txt` and there will not be.
- **Claims match what is built.** No capability is described before it exists. If you
  are unsure whether something works, run the validator or read
  `docs/known-limitations.md` — do not assume.
- **Agents propose; humans land.** An agent may write a proposal; only the maintainer
  can merge one. That commit permission is the real enforcement, not the validator.

## Authoring standard

Work is tracked as GitHub issues on this repository and driven with the `gh` CLI —
see `docs/agents/issue-tracker.md` for the conventions (native sub-issues and
dependencies, not checklists).

When you change files here:

- Branch before editing; never commit to `main` directly.
- Run `python3 scripts/validate.py .` and the test suite before saying you are done.
- Markdown links must resolve — the validator ERRORs on broken relative links.
- Keep this file under 200 lines. It loads into every session, and it is part of a
  chain that Codex silently truncates past 32 KiB.

## Working on groundwork itself

Contributor and build-session rules — the session shape, the review gate, and the
standing explain-before-deciding rule — live in
`docs/agents/build-sessions.md`. Those are workbench rules for developing groundwork;
they are not product content and do not ship to adopters.
