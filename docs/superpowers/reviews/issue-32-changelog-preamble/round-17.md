# Entry 17 — maintainer decision, not a review round

This entry is **not a Codex review round.** It records the maintainer's decision to stop the
review loop after round 16 and reduce the slice to what issue #32 asked for. No review round
has run against the resulting state, and the merge commit says so.

**Decided:** 2026-08-30, by the maintainer, after sixteen rounds.

## What the measurement showed

Put to the maintainer at their request, measured on `8202ab6`:

| | Lines | Commits touching it | Accepting-direction findings |
|---|---|---|---|
| Issue #32's fix — the base-anchored boundary | 66 | 1 (`c3af4d2`, round 1) | **0 in 15 rounds** |
| The header-rendering guard added on top | 122 | 12 | **8** |

**The thing the issue asked for was right in round 1 and was never breached.** Every
accepting-direction finding on this branch — rounds 02, 04, 05, 06, 07, 08, 09, 11 — was in a
second guard the issue never asked for.

## What that guard was, and why it was built

Issue #32's counter-argument was about **laundering entries**: editing one, removing one,
converting one into non-entry text. The base-anchored boundary closes all of that, and the
record shows fifteen rounds failing to get past it.

The builder then reasoned that #17's one-glance property is a property of *reading* the file, so
a header that changes how entries **render** defeats it too, and built a check for that. It is a
real observation. Acting on it meant modelling CommonMark's block structure inside a validator
whose stated conventions are "files, not engines" and "zero dependencies" — and then discovering,
one round at a time, that modelling CommonMark is hard: fences behind list markers, U+00A0 versus
an ASCII blank, a list item's content column, tab stops at multiples of four, GFM tables
absorbing pipe-delimited entries, link reference titles spanning into the ledger.

**That scope expansion was never escalated.** The three questions the issue posed went to the
maintainer under rule 5 and were answered. The fourth workstream, larger than all three, was
started silently in round 2 and never revisited.

## The decision

**Option A, taken: keep the base-anchored boundary, delete the header guard.** The gate protects
the ledger's bytes; a header edit that changes how it renders is a documentation change caught by
a human reading the diff, which is the consent gate #18 already rests on.
`docs/known-limitations.md` states that plainly, including that a check for it was built and
removed.

Considered and not taken: **merging as it stood.** Four consecutive rounds had found no
accepting-direction defect, and rule 9 permits merging over recorded open findings. It was
refused because 122 lines of Markdown modelling in a zero-dependency validator is a liability for
whoever touches it next, defending against a threat the issue did not raise.

**The counter-argument, recorded.** The removed guard worked. Two rounds derived its coverage
matrix independently and agreed it had no accepting-direction gap, and roughly forty mutations
pinned it. Option A discards verified work, and it widens what an adopter can do to a changelog
header without the gate objecting. The answer is that the gate never owed that protection, and
that saying so is more honest than a parser that will be wrong again.

## What was removed, and what was kept

Removed: `_md_indent`, `_opens_a_container`, `_changelog_header_reaches_the_ledger`, the
`"hidden"` reason and its caller branch, and the header test matrices. Also reverted are the
three edits made to shipped changelogs **only** to satisfy the guard — the engine's entry-format
example, the demo's `skills/<name>/` placeholder, and the trailing blank line each file gained.

Kept: the base-anchored boundary and its helpers; the appended span measured from the protected
block's end; `CHANGELOG_REASONS` failing closed; **the roster added to the demo changelog's
enumeration, which is the defect issue #32 was filed for**; and both preambles' corrected
append-only claims.

**The review entries all stay.** They are the evidence for why the removal is right, and deleting
them would erase the reason.

## Correcting round 16's finding 1, which the record must carry

Round 16 found three false claims in round 15's rewritten README paragraph. All three are
corrected in the README. `round-15.md` is immutable, so this entry records them: "the last seven"
mutations no longer names the seven it meant once rounds 14 and 15 added rows; **rounds 03 and 10
crashed with no findings**, so "every round from 02 onward" is wrong; and reviewers reproduced
correct counts in rounds 13, 14 and 15, so "every count a reviewer checked was wrong" is wrong —
an overclaim about how much the branch had overclaimed.

## The process finding, which is the maintainer's to decide

The rule that would have caught this in round 2, offered for `docs/agents/build-sessions.md` and
**not written there by the builder**, since a workbench rule is the maintainer's to set:

> **A check the issue did not ask for is a rule 5 escalation before it is written.** A slice
> implements the issue's scope; a new check outside it — however well motivated — goes to the
> maintainer first, with what it defends against and what it would cost.

A second, from the same evidence: **when a review round produces no findings in the class the
slice is about, the slice goes to the maintainer for a merge decision** rather than continuing
until a reviewer says "approve". Rule 9 already says the record must exist, not that every
finding must close. Rounds 13 to 16 spent four rounds closing accuracy defects in the builder's
own prose after the safety question had been settled twice.
