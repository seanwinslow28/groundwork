# Entry 10 — maintainer decision, not a review round

**This entry is not a review round.** No Codex invocation produced it. It records the
maintainer's decision to stop reviewing and the state that decision leaves behind, as rule 9
permits a numbered entry to do.

**Decision (maintainer, 2026-08-29):** stop the review loop after round 9 and write the
terminal entry. The instruction was given after round 9's findings were fixed and after the
builder recommended stopping, with the counter-argument recorded: nothing guarantees a round
10 would be clean, and every round so far found something real.

## The honest position

**There is no approving verdict on this branch.** Round 9, the last round run, returned
**does not approve** against `2bc94ce`. Its six findings were all fixed in `a5ba199`. No
finding from any round is open; one is rejected with grounds, at round 2.

Rule 9's merge condition is that the verdicts of every round run against the slice are
committed in the repository, and that condition is met: rounds 1–9 each have an entry, with
every finding, its reviewer's severity word verbatim, and its disposition. The rule also
says the final verdict *should* be approving. This one is not, and that departure is
recorded here rather than smoothed over. Rule 9 anticipates it: the maintainer may merge
over a non-approving verdict, recording the grounds in the merge commit, as `5fc61c6` did
for slice 2.1.

## What was never reviewed

Rule 9 accepts that the last verdict is committed after the state it reviewed, so the entry
commit itself is unreviewed. **On this branch the unreviewed tail is larger than that**, and
saying so is the point of this paragraph. Two commits sit after `2bc94ce`, the last reviewed
revision:

- `a5ba199` — the round-9 fixes. **Substantive code**, including a rewritten
  `_invisible_char`, the zero-width-joiner exemption, the symlinked-roster ERROR, the
  proposal-target equality test, and the corrected documented example. No review round has
  seen any of it.
- `24f1bcc` — `round-09.md` and the README update.

What is known about that tail is what the builder verified, not what a reviewer confirmed:
each fix carries a test, several were checked to fail without their fix, and the gate is
green. That is weaker evidence than a review round, and it is the evidence there is.

## Verified at `24f1bcc`, the state this entry describes

- `python3 -m unittest discover -s tests -q` → OK, **824 tests**, skipped=1.
- `python3 scripts/validate.py .` → `0 error(s), 8 warning(s)`, exit 0.
- `python3 scripts/validate.py demo` → `0 error(s), 3 warning(s)`, exit 0.
- `python3 scripts/validate.py . --diff main` → exit 0.
- 28 commits against `main` at `ddcb7a1`.

The eighth engine warning and the third demo warning are the same finding — the demo
roster's passed `review_by` — which is an open maintainer question, not a defect.

## What nine rounds cost and what they bought

Fifty-five findings: 11, 7, 6, 4, 5, 4, 6, 6, 6. Fifty-four fixed, one rejected with
grounds. Eleven of them were BLOCKERs, and every BLOCKER was the same shape — text a reader
does not see supplying a holder, or a row a reader does see that the parser did not.

The roster parser was rewritten three times and simplified twice. It ended smaller than it
started: a flat table of forbidden line patterns matched with no container semantics, after
masking, fence-length arithmetic and blockquote-stripping were each tried and each found
wrong in one direction. The lesson the entries record is that every attempt to decide what
*renders* was CommonMark emulation, and that the completeness claims made along the way —
round 8's "complete by construction", disproved by round 9 — were the error, not the
particular character each round missed. What replaced them is `docs/known-limitations.md`
saying the check is high-signal and not exhaustive, in the words the secrets floor already
uses.

Six entries carried a factual error found by a later round: a severity tally, an axis split,
a claim about two test assertions, two narrative summaries, an internal contradiction, and a
completeness claim. Every one was a sentence the builder wrote **about its own work**, and
every one was checkable against a file in the repository. No claim about the code was wrong
in rounds 7 or 9. Later entries correct earlier ones, as rule 9 requires, and the count is
left visible rather than tidied.

## Still the maintainer's, and not decided here

1. **The demo roster's `review_by`.** Option (a), in the tree now: the 90-day policy default
   `2026-08-09`, which has passed, so `demo` reads `0 error(s), 3 warning(s)` and the engine
   root `0 error(s), 8 warning(s)`. Option (b): a future date justified by the demo's own
   convention that its dated records are not yet due. The full case for each is in this
   directory's README.
2. **Prose inside an append-only file.** `demo/governance/changelog.md`'s preamble omits the
   roster and #17's append-only rule makes it uncorrectable. Recorded, not resolved.
3. **Role rows for the demo's five canon offices** — considered and not taken, since no demo
   rule names an office and Role rows are R2's elicitation work.
4. **The active-rule ERROR suppression.** With an active rule and no roster at all, one
   missing-roster ERROR is emitted and the four per-field resolution ERRORs are suppressed;
   drafts are not suppressed. This is the builder's implementation choice, not the design's.
   It was offered for challenge in every round from 1 to 9 and never challenged.
5. **The four items carried in from the previous session**, none of them this slice's: what
   counts as adequate grounds for rejecting a finding; whether `CONTEXT.md:105`'s consent
   invariant should carry the bootstrap qualification; whether a later `--diff` base must be
   proven to contain the generated root; and ratification of the rule-1 departure recorded in
   both merged logs.
6. **Two edits this branch made beyond the design's named list**, both flagged when made:
   `CONTEXT.md`, because locked decision 8 made its "only two artifact kinds" false, and
   `docs/roadmap.md`, because two of its V2 bullets became false when the bump landed.

## Grounds for the merge commit

If the maintainer lands this, rule 9 asks the grounds be recorded there. The facts they
would rest on: every round's verdict is committed; no finding is open; one is rejected with
grounds; the last verdict does not approve and no approving verdict exists; the round-9 fixes
and this entry are unreviewed; and the gate is green on all four commands at `24f1bcc`.
