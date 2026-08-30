# Round 06 — `9192236`

**Reviewed revision:** `9192236d909de879086f1fe7f87fc00186da2ed9`, clean worktree.
**Task id:** `task-mtf50lio-lceq76`.

**Verdict, verbatim:** "Do not approve yet. One underlying defect remains, affecting both
axes." One defect, reported as two rows — one Standards, one Spec.

## Correction to `round-05.md`

`round-05.md`'s finding 3 is immutable and over-reports its own fix.

It recorded both the question's note and `generate.md` as now saying the unheld-role state
prevents activation "subject to the high-risk appeal exception". `generate.md` did say that.
**The question's note did not** — it carried no qualification at all, and in fact said
something broader and wrong, which is this round's finding 1. The entry described the fix it
intended rather than the fix that landed.

## Findings

**1. MEDIUM** *(the reviewer's word)*, Spec — the question's note over-broadened decision 6's
exception. It said an unheld role "stops a high-risk rule shipping at all". Decision 6 forbids
shipment only where the unheld role is that high-risk rule's **appeal owner**; every other
unheld owner field on a high-risk rule ships as a declared rungless draft. `generate.md`'s
parallel sentence was already qualified correctly, so the contract's two statements of one
rule disagreed — and the wrong one was the one an interviewer reads first.

**Disposition: fixed.** The note now reads "a rule it owns cannot activate, and a high-risk
rule whose appeal owner it is does not ship at all."

**2. MEDIUM** *(the reviewer's word)*, Standards — `round-05.md` records that note as fixed
with a qualification it did not carry. **Disposition: corrected above.**

## Why these are one defect

The reviewer says so explicitly and it is worth keeping: round 5 fixed `generate.md` correctly
and wrote the *shared* claim into the note in a looser form, then recorded both as done. The
entry's error is not independent of the product error — it is the same sentence, written twice,
checked once.

## The one shape this branch produced most

Six rounds. The single most frequent defect was **the record describing a fix more complete
than the one that landed** — round 1's chronology, round 2's classification, round 3's
over-generalised acceptance claim, round 4's misattributed evidence, and now round 5's
unqualified note. In every case the product fix was real and the entry claimed slightly more
for it. The countermeasure that would have caught all five is the same one: **re-read the
changed lines before writing the entry, not the intention behind them.**

## Checked clean this round

The reviewer reports everything else clean, naming: the activation-condition route is faithful
to the maintainer's decision and to decisions 2, 3, 5 and 6; the Role/Holder precondition
matches `_parse_roster`; the Standards repairs landed; and round 5's correction of round 4 is
accurate.

## Environment

The reviewer ran the available validators, the targeted coverage tests and `git diff --check`,
and did not rerun the full suite because the sandbox cannot create its temporary directories.
Run outside the sandbox at the reviewed revision and again after the fix: 824 tests, OK,
skipped=1. Gates after the fix: `validate.py .` 0 errors 7 warnings exit 0; `validate.py demo`
0 errors 2 warnings; `validate.py . --diff main` exit 0.
