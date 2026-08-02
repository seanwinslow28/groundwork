# AGENTS.md — groundwork

**groundwork is an open-source, harness-agnostic Company OS.** It is files, not an
engine: markdown conventions plus one zero-dependency validator. Any coding agent that
reads a repository can read this one.

This file is the canonical instruction surface for agents working in or with this
repository. `CLAUDE.md`, `GEMINI.md`, and `.cursor/rules/groundwork.mdc` are pointers at
it — Claude Code reads `CLAUDE.md` and Gemini CLI reads `GEMINI.md`, neither of them
reads this file, and Codex and Cursor read it natively. Edit **this** file; the validator
checks that the pointers still resolve here.

## Status — what is real today

The design is fully charted (19 resolved decisions; see `CONTEXT.md`). **V1 is complete:**
the schema exists as files, three functions are worked end to end across both governance
tracks, one function records a deliberate non-automation verdict, the interview and its
generator exist as documents, `demo/` is a complete governed company, `delivery/` covers
provisioning, and the validator gates every layer of it. The protocols have been run end
to end against a simulated persona company, scored blind and with the interview
transcript audited; nobody has run them on a real company — see `docs/known-limitations.md`.

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
- `interview/` — the interview end to end, as documents: the **state format** (#9), the
  **consultant protocol** (§4), the **question skeleton** mapped onto the fields each
  answer fills, and the **generation protocol** with the company-repo manifest (#10). A
  person can run all four with an agent today and get a company repo the validator
  passes; a test builds one and proves it.
- `proposals/` — the consent-gate convention for agent-proposed changes.
- `demo/` — the pre-installed example company (**Umbercress**, ~20 people), complete:
  canon, eight executive views, seven deep records, org memory, four work packages,
  three constitution rules, one runnable rung-3 reminder, one pending proposal, and the
  15-minute three-query walkthrough. It carries a `groundwork.pin`, so it is a
  **governed root** — changes to its skills and rules run the #18 consent gate exactly
  as a company repo's would.
- `delivery/` — the provisioning guide: the repo-local symlink layer that gives generated
  skills a harness-visible path in all four harnesses, the organization plugin upload and
  GitHub-synced marketplace paths, and how to install the runnable action-class gate with
  the re-copy obligation that comes with it. Every external fact carries the date it was
  verified, and the guide says which symlink shape was tested head-to-head and which was
  not.

## The map

| Path | What it holds |
|---|---|
| `CONTEXT.md` | The glossary. Every resolved decision's vocabulary. Read this first. |
| `ontologies/` | One directory per function. All 8 executive views; `people-hr/`, `customer-success/`, `product/`, and `engineering/` also carry a worked deep record. |
| `skills/` | Work packages: `skills/<name>/SKILL.md` + `owner-card.md`. |
| `governance/` | `constitution/` (typed rules), `hooks/` (the action-class gate), `changelog.md`. |
| `memory/` | Org-memory records, one per file, with an index. |
| `interview/` | The state format (#9), the consultant protocol (§4), the question skeleton, and the generation protocol (#10). |
| `delivery/` | The provisioning guide: making a generated OS loadable, and distributing it. |
| `proposals/` | Pending improvement proposals. Empty by design — proposals are transient. |
| `scripts/validate.py` | The validator. Run it before you claim anything is done. |
| `MIGRATIONS.md` | The version-pin contract and the pull promise. |
| `docs/known-limitations.md` | What this does **not** do. Read before relying on a check. |
| `docs/rule-map.md` | Every check, what it enforces, and the severity it fires at. |
| `docs/roadmap.md` | V1, V1.5, V2, V3, and the four things groundwork will never do. |
| `docs/security-and-privacy.md` | What a company OS in a git repo exposes, and who can reach it. |

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

## The interview

The entry point is an interview: you point your agent at this repo, it asks your
company what work each function actually does — what deserves more human time,
what should be automated, and under what rules — and generates your operating system
from that map into a separate private repository.

**It is documents, not a program.** There is no `generate.py` — the confirmed layers are
prose, and the thing that turns them into records is an agent following
`interview/generate.md`, with the question skeleton naming the destination field for
every answer. What makes that trustworthy is the gate at the end:
`python3 scripts/validate.py ../<company>-os` runs the whole schema against what was
generated, and this repo's own test suite builds a company repo and proves it passes.

## Two repos

The public groundwork clone is the **engine** — pull-only, never edited by an adopter.
A company's OS lives in a **separate private repo** carrying content plus a
`groundwork.pin`; the validator, the schemas, and the runnable action-class gate stay in
the engine clone and run *against* that repo. Upstream improvements arrive by `git pull`
on the engine — **content is never re-copied**, which is why a generated company repo
carries `governance/review-gate.md` (prose, and its own) rather than a copy of the hook
set that would go stale silently.

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
