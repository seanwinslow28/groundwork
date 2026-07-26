# Proposals — the consent gate

An agent may **propose** a change to a skill or a constitution rule; only the
maintainer may **land** it (the commit bit is the real teeth, #18). A proposal is one
file here, and that file **is** the review file — diff, reason, evidence, and the
blast-radius declaration in one place.

`proposals/` is **pending-only.** When a proposal is approved and applied, the file is
**removed** — the change now lives in the edited skill/rule plus the git record of
consent (the merge commit, or an `approved_by` commit on the branchless floor). The
git event is the durable record; a PR is just the richest way to review it.

## Schema (frontmatter)

````
---
target: skills/<name>/SKILL.md        # or governance/constitution/<rule>.md
blast_radius: escalating              # track1-body | escalating
reason: <one line: why this change>
evidence:                             # org-memory records / motivating sessions
  - memory/<record>.md
status: pending
---
# Proposal: <title>

## Diff
```diff
<the proposed change>
```

## Why
<the reasoning, expanding the one-line reason>
````

## Routing (three buckets, #17)

- **`track1-body`** — touches **only** the SKILL.md body of a **track-1** (read-only /
  reversible-write) skill. Auto-applies with a changelog line; no human merge needed.
- **`escalating`** — touches a description, governance frontmatter, or an Owner's Card;
  or any track-2 skill; or **any constitution rule**. Needs the maintainer's sign-off.
  Rules are `escalating` by construction — they never auto-apply.
- **Incomplete** (missing reason / evidence) — demoted to an org-memory working note
  with the gaps named; it re-enters as a proposal when the gaps fill.

Proposals route **skills and rules only.** Org-memory, Owner's Cards, and ontology
worksheets keep their own governance; a memory enters this routing only when it
graduates into a proposed skill/rule change.

## Consent ladder (richest → floor)

GitHub **draft PR** → `proposal/*` **branch-merge** (Cursor / GitLab / local git) →
self-attested **`approved_by` + `approved_at`** on the committed file (the weakest rung).
The file is canonical; each rung is a way of reviewing it.
