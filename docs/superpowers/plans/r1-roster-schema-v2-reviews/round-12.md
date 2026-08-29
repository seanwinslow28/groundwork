# Entry 12 — the last three maintainer decisions, not a review round

**This entry is not a review round.** It records the maintainer's answers to the three items
entry 11 left open, given 2026-08-29, each having been put with its options, a
recommendation and its counter-argument.

Unlike entry 11's six, **two of these imply edits**, and neither edit is on this branch. Why
not is recorded below rather than left to be inferred from its absence.

## Decided

**5a. Adequate grounds for rejecting a finding: the closed list.** A rejection must state one
of three categories — **factually wrong** (naming the source), **out of scope** (naming the
scope and the follow-up work it becomes), or **superseded** (naming what supersedes it). The
grounds: a closed list is auditable, where "case-specific grounds" is satisfied by any
sentence at all. The escape hatch for a finding no category fits is unchanged and already has
a precedent — leave it **open** and let the maintainer override at merge, which is what
`5fc61c6` did for slice 2.1. *Counter-argument, recorded:* a closed list cannot anticipate a
legitimate reason nobody has hit yet, and the escape hatch routes that case to the
maintainer's inbox rather than the builder's judgment.

This slice's one rejection — round 2's `demo/governance/changelog.md` half — is **out of
scope** under the list, and was demonstrated rather than argued: the edit was made, the gate
went red, the edit was reverted.

**Implementation owed:** `docs/agents/build-sessions.md` rule 9 gains the three categories.
Not on this branch — see below.

**5b. `CONTEXT.md:105` gains a qualifying clause.** The consent-gate entry states that an
escalating change reaches the main line only via a reviewable proposal plus a human
affirmative act, with no exception noted. *Recorded honestly, because the case is weaker than
the one for `CONTEXT.md:57` that this branch already repaired:* decision 8's migration
bootstrap does not let an escalating change through unproposed — it classifies a roster
addition at the v1→v2 boundary as **not escalating**, which the invariant survives. The
generation exemption S2 established is the harder case, since escalating-shaped content does
reach the main line there without proposals. So the clause is warranted, but on one exception
rather than two. *Counter-argument, recorded:* the glossary is deliberately terse and states
intent; each exception added moves it toward being a spec.

**Implementation owed:** one qualifying clause at `CONTEXT.md:105`. Not on this branch.

**5c. The `--diff` base contract is not enforced now.** `_git_diff_context` will keep
checking only that the ref resolves. Accepting the recommendation here means **not** building
it into R1: it becomes its own small slice, because it changes what the gate promises and
because the present behaviour fails loud in the safe direction — a base predating the
generated root over-gates into a wall of escalating ERRORs rather than under-gating.
*Counter-argument, recorded:* that wall is an adopter's first experience of the gate, at the
documented "prove it" step.

## Why 5a's and 5b's edits are not on this branch

Two reasons, both recorded in this directory already.

**The unreviewed tail.** `round-10.md` states that the commits after `2bc94ce` — the round-9
fixes and the entries — were seen by no review round, and that this is a larger tail than
rule 9's accepted one-commit exemption. Bolting two more unreviewed governance-document edits
onto the end would widen exactly the gap that entry named as the branch's weakest point.

**Rule 1.** `round-11.md` ratified the previous session's one-increment departure and recorded
that **this** session did not depart: R1 was one slice. Amending `docs/agents/build-sessions.md`
is workbench-rules work belonging to R0's territory, and `CONTEXT.md`'s consent entry is not
roster content. Adding them here would make that statement false in the same commit range
that asserts it.

Both are small, both are decided, and both are ready to run as one short follow-up slice —
"amend two governance documents to reflect decisions already taken" — with its own review
record. Nothing about R1 depends on them.
