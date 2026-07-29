# The interview state format

An interview is a conversation that has to survive being interrupted — by a meeting, by
a week, by switching from one agent harness to another. This directory documents the
shape that state takes so it survives all three.

**What is here today: this format and its checks, the consultant protocol
([protocol.md](protocol.md)), and the question skeleton ([questions.md](questions.md)).**
The generator that turns confirmed answers into a company OS is **not built** — Slice
3.3. A person can run the interview by hand with an agent and get a checked, resumable
record; nothing generates a company OS from it yet.

## Where the state lives

In the **company's private repo**, never in the public groundwork clone (#10). The
interview's first act is creating that repo; every confirmed answer is committed there
from the start, so confidential organizational facts never sit in a public working tree.
The validator runs from the engine clone *against* that repo.

## The three kinds of file

```
interview/
  00-manifest.md      the pointer. Small, fixed shape, rewritten every turn.
  01-role-and-scope.md    a confirmed layer. Frozen at its checkpoint commit.
  02-customer-success.md  a confirmed layer.
  _working.md         the turn in flight. Provisional. Dirty until approved.
```

**The manifest points; it never labels.** There is no "status: confirmed" column,
because a label an agent writes is a label an agent can get wrong. What makes a layer
confirmed is *structure*: it is a numbered file, it is listed in the manifest, it carries
`provenance: confirmed`, and it is committed. `git log` is the approval trail.

### `00-manifest.md`

```markdown 00-manifest.md
---
company: Nettleford Supply
role: asks what the work is before proposing anything, and says not worth automating out loud
phase: customer success, activity by activity
status: in-progress
open_question: q-renewal-brief-owner
last_checkpoint: 2026-07-28
layers:
  - 02-customer-success.md
---
# Interview manifest — Nettleford Supply

Customer success is mapped and frozen. One question is open: who owns the renewal
brief when the account manager is away. Product is next.
```

A resuming agent reads this file **first**, and only then the layers it needs. That is
what keeps the boot cost bounded: the manifest grows one line per layer, not one line per
turn.

`layers:` must be a **list**, even with one entry, and every entry must be a real file in
this directory named `NN-slug.md` with `NN` from `01`. `00` is reserved for the manifest.
The list and the directory must agree in **both** directions — a layer file nobody listed
is a layer a resuming agent will not read, and a listed file that does not exist sends it
looking for an answer that was never captured. That drift is the one cost #9 accepted
when it chose this shape, and this is the check that pays it.

### A confirmed layer — `NN-slug.md`

```markdown 02-customer-success.md
---
provenance: confirmed
confirmed_by: Mara Voss
confirmed_at: 2026-07-28
source: interview turns 9 through 14, plus the Q2 renewal log read with permission
---
# Layer 2 — customer success

Renewal prep is the one acted-on activity: Motion automate, run from the CRM as the
source of truth. Health-check calls stay human — Direction up, and Mara said why.
```

**Frozen at its checkpoint.** Once committed, a layer file never changes — not the
frontmatter, not the body. Run `python3 scripts/validate.py <repo> --diff <base>` and any
edit to a committed layer is an ERROR, exactly as it is for an org-memory record (#7).
If a confirmed fact turns out to be wrong, the next layer records the correction and says
so; you do not go back and rewrite what a person approved.

`provenance`, `source`, and the ERROR-vs-WARN split on them are #7's vocabulary, not a
parallel one: `confirmed` means a human approved it at a checkpoint, and a confirmed fact
without a source is an ERROR.

### The turn in flight — `_working.md`

```markdown _working.md
---
provenance: observed
source: the Q2 renewal log, read with permission
open_question: q-renewal-brief-owner
---
# In flight — renewal prep, ownership

Fifteen of twenty-six Q2 renewals had a written brief, median eight days out. The log
names no owner for the brief when the account manager is away.

## Open question

Who owns the renewal brief when the account manager is out — a person, not a role?
```

`provenance` here can never be `confirmed`. A working file that calls itself confirmed is
the exact laundering this shape exists to stop, and it is an ERROR — the way to confirm a
fact is to **promote** the file, not to relabel it.

`observed` means the agent read it somewhere; `inferred` means the agent concluded it.
Both are the agent's, not the company's, until a person says otherwise. This is where
§4's evidence-based move lands: an agent that reads the handbook and reflects back the
rules the company is *actually* running produces `observed` facts with a `source:`,
because people report the rules they wish they had.

## The promote-and-commit protocol

One layer, one checkpoint, one commit:

1. **Ask.** The open question goes in `_working.md` along with whatever the agent has
   provisionally gathered. The manifest's `open_question` names it. Nothing is committed
   — with one exception: when nobody can answer, the halt rule
   ([protocol.md](protocol.md)) commits `_working.md` and the manifest together, so the
   open question survives the interruption it just caused.
2. **Answer.** The human answers. The agent updates `_working.md`. Still nothing is
   committed — a fact is not confirmed because an agent heard it.
3. **Checkpoint.** The agent states back what it believes is now settled and asks for
   approval. This is the approval; there is no other one.
4. **Promote.** On approval, `_working.md` is renamed to the next `NN-slug.md`, its
   `provenance` becomes `confirmed`, and `confirmed_by` / `confirmed_at` record who
   approved it and when.
5. **Commit.** The promoted layer and the updated manifest are committed together, in one
   commit. That commit *is* the record of consent — the same substrate the constitution's
   proposals use (#18).

A turn that half-commits — a promoted layer without a manifest update, or the reverse —
is what `check_interview_state` catches on the next run.

## When the interview is finished

Set `status: complete` and `open_question: none`, and delete `_working.md`. A completed
interview with a turn still in flight is a contradiction, and it ERRORs.

## What is checked, and how hard

| Rule | Level |
|---|---|
| Manifest missing `company` / `role` / `phase` / `status` / `open_question` / `last_checkpoint` | ERROR |
| `status` not `in-progress` or `complete`; `layers` not a list | ERROR |
| A listed layer that does not exist, or an existing layer nobody listed | ERROR |
| A layer file whose `provenance` is not `confirmed` | ERROR |
| A layer file with no `confirmed_by`, no `confirmed_at`, no `source`, or no rule content | ERROR |
| `_working.md` claiming `provenance: confirmed` | ERROR |
| `_working.md` present while `status: complete` | ERROR |
| `_working.md` missing while a question is open, or naming a different question than the manifest | ERROR |
| An edit to, or deletion of, a committed layer (`--diff`) | ERROR |
| `confirmed_at` unparseable or in the future; a gap or a wrong order in the numbering; `_working.md` with no `source` | WARN |

Strict exactly where the state backs a resuming agent, because a manifest that points at
the wrong thing does not fail loudly — it silently re-asks a settled question or skips one
that was never settled. Everything that is only thinking-quality warns.

**Silence is decided by content.** A directory is interview state when it carries a
`00-manifest.md`. This directory has none — it is documentation — so nothing here is
checked as state, and a company repo that has not started an interview is silent rather
than nagged.
