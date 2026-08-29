# Round 02 — `3d61902`

**Reviewed revision:** `3d61902bc046ad0784b00803e570bbf33f5d4574`, clean worktree.
**Task id:** `task-mtey5axq-5v6vl3`.

**Verdict.** No approve / does-not-approve word. The reviewer's own summary line, verbatim:
"Standards 2 findings, worst MEDIUM; Spec 2 findings, worst MEDIUM." Four reported rows,
three distinct defects — the reviewer says so itself, calling one of them "the same
cross-axis defect" reported on both axes.

Two of the three landed in commits round 1 produced. That is the pattern this project's
kickoff predicts and it held again.

## Findings

**1. MEDIUM** *(the reviewer's word)*, reported on both the Standards and the Spec axis —
`README.md:39` of this directory. The rounds table recorded round 02's reviewed revision as
`a9e1171` when the revision actually reviewed was `3d61902`. Cause: the row was pre-filled
with the SHA that was HEAD when round 01's entry was written, and a bookkeeping commit then
moved HEAD before the round launched. Rule 9 requires the reviewed SHA.

**Disposition: fixed.** The row now reads `3d61902`, verified against `git rev-parse` rather
than against the brief. **Process change, recorded so the cause does not recur:** a pending
round's Reviewed cell is not pre-filled again on this branch. A reviewed SHA is knowable only
once the round has launched, and writing it earlier records a prediction as a fact.

**2. LOW** *(the reviewer's word)* — `round-01.md:33` cites `interview/generate.md:10-15`,
but the sentence it cites finishes on line 16 ("required field, named or not"). Verified: at
`3d61902` the paragraph runs `:10-16`.

**Disposition: fixed here, not there.** `round-01.md` is immutable, so this entry is the
correction rule 9 requires: **the citation at `round-01.md:33` should read
`interview/generate.md:10-16`.** At this entry's own revision that paragraph still occupies
`:10-16`; the fix commit for this round does not touch it.

**3. MEDIUM** *(the reviewer's word)* — `interview/generate.md:299`. The report list is
incomplete against the global contract its own intro asserts: a memory record missing
`source` is a gap the list does not name, and `round-01.md:31` gave a rationale the reviewer
read as self-contradictory — that non-shipment is why the case needs no bullet, when the
report explicitly covers what did not ship.

**Disposition: fixed, by a different route than the one suggested.** The finding is correct
and the suggested remedy is not, so both halves are recorded.

*Correct:* the list was incomplete, and `round-01.md:31-34`'s rationale was confused. "The
body grants no permission for it" was never a reason to leave a case out of the **report**,
because the report covers non-shipment too. **That reasoning in `round-01.md` is withdrawn
here** — this entry supersedes it.

*Not adopted:* adding a `source` bullet. The memory paragraph at `interview/generate.md:123`
lists five required fields and carves out behaviour for exactly two — `owner` (the record
does not ship) and `review_by` (it ships and the validator WARNs). `provenance` and
`valid_at` have precisely the same claim to a bullet as `source` does, so a `source` bullet
alone would be arbitrary, and all five would begin enumerating a schema. That is the shape
of list that cannot be completed and goes stale the first time any schema gains a field.

*What was actually wrong,* and what is fixed instead: the **intro claimed the list was
exhaustive** — "Every artifact that shipped incomplete, or did not ship at all, is named
with its reason." No such list can be exhaustive. The intro now says the bullets are the
classes the document's ordering rules carve out by name, says in as many words that they are
not a closed list, and points at the general rule at the top of the file, which already binds
"every required field, named or not" and is where the `source` case lives. Claiming
completeness was the defect; the missed case was the symptom.

## Not re-raised, and confirmed still true

The reviewer confirmed the seven adopter-facing validator explanations still match
`scripts/validate.py`, and that the `provisioned: no` reconciliation matches the
work-package contract. It did not re-raise anything the record discloses.

The two report-list entries `round-01.md` flagged as additions rather than reconciliations —
a rule stopped by the safety-spine exception, and the roster's defaulted `review_by` — were
put to this round explicitly and drew no finding.

## Environment

Sandbox `TemporaryDirectory` errors from `unittest` are environmental, as before. The suite
was run outside the sandbox at the reviewed revision and again after the fix: 824 tests, OK,
skipped=1.
