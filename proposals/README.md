# Proposals — the consent gate

An agent may **propose** a change to a skill, a constitution rule, or the roles roster;
only the
maintainer may **land** it (the commit bit is the real teeth, #18). A proposal is one
file here, and that file **is** the review file — diff, reason, evidence, and the
blast-radius declaration in one place.

`proposals/` is **pending-only.** When a proposal is approved and applied, the file is
**removed** — the change now lives in the edited artifact plus the git record of
consent (the merge commit, or an `approved_by` commit on the branchless floor). The
git event is the durable record; a PR is just the richest way to review it.

## Schema (frontmatter)

````
---
target: skills/<name>/SKILL.md        # or governance/constitution/<rule>.md, or governance/roles.md
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
  or any track-2 skill; or **any constitution rule**; or **the roles roster**. Needs the
  maintainer's sign-off. Rules and the roster are `escalating` by construction — they
  never auto-apply.
- **Incomplete** (missing reason / evidence) — demoted to an org-memory working note
  with the gaps named; it re-enters as a proposal when the gaps fill.

Proposals route **skills, rules, and the roster.** Org-memory, Owner's Cards, and
ontology worksheets keep their own governance; a memory enters this routing only when it
graduates into a proposed skill/rule change.

The roster joined at schema v2: `governance/roles.md` decides who holds every active
rule's owners and where its human appeal terminates, so editing it is governance rather
than bookkeeping. The one exemption is the migration itself — a roster **added** in the
same diff that moves the root's pin from v1 to v2 is the sanctioned crossing, because
every v1→v2 migration adds one.

## Consent ladder (richest → floor)

GitHub **draft PR** → `proposal/*` **branch-merge** (Cursor / GitLab / local git) →
self-attested **`approved_by` + `approved_at`** on the committed file (the weakest rung).
The file is canonical; each rung is a way of reviewing it.

## What the validator enforces (`validate --diff <base>`)

At PR time the validator classifies every changed skill, rule, and roster under a governed root
(a directory carrying a `groundwork.pin`) and checks the **declaration against the diff**:

- An **escalating** change with **no pending proposal** → ERROR.
- A pending proposal declaring **`track1-body`** while the diff actually touches a rule, the
  roster, a
  track-2 skill, frontmatter, or the Owner's Card → ERROR (**declared-vs-actual mismatch** —
  this is what stops a rule edit being smuggled under a track-1 label).
- A **track-1 body-only** change with no newly appended changelog line → WARN (an agent
  auto-apply must log its line; a maintainer's own edit needs none).
- Any edit, reorder, or removal of an existing `governance/changelog.md` entry → ERROR.

The tripwire cannot prove a human truly reviewed the change — the commit bit does that.
See [docs/known-limitations.md](../docs/known-limitations.md).
