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
- `proposals/` — the consent-gate convention for agent-proposed changes.
- `demo/` — the pre-installed example company (**Umbercress**, ~20 people). Its canon
  declares the fictional world and doubles as the validator's identifier allowlist. Its
  ontologies, org memory, four work packages, and constitution are complete, including
  one runnable rung-3 reminder (#8 item 3). The 15-minute walkthrough and the version
  pin are still to come — `demo/README.md` says what is there today.

**Not built yet — do not describe these as working:**

- `interview/` — the generator that would interview a company and write its OS.
  Phase 3. It does not exist.
- `demo/` walkthrough — the 15-minute 3-query script. The company's content is in place;
  the script that walks you through it is not written, so there is nothing to follow yet.
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

This adds the stateful modes: org-memory immutability, and the blast-radius tripwire
that requires an escalating change to carry a matching proposal.

To understand the shape before writing anything, read one worked example end to end:
`ontologies/people-hr/onboarding-orchestration.md` →
`skills/onboarding-orchestration/SKILL.md` → its `owner-card.md` →
`memory/onboarding-baseline.md` → `governance/constitution/`.

## The interview (not built — Phase 3)

The intended entry point is an interview: you point your agent at this repo, it asks
your company what work each function actually does — what deserves more human time,
what should be automated, and under what rules — and generates your operating system
from that map into a separate private repository.

**That generator does not exist yet.** Today this repo is the proven schema, the
validator, and three worked functions. Anything describing the interview as usable is
wrong.

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
