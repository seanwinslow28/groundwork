# Round 06 — Codex review, 2026-08-30

**Reviewed:** commit `20280ba` (branch HEAD after round 5's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfmd86j-6go6b2`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Two unique **Minor** findings,
one reported on both axes. In its words: no validator-behaviour defect found.

What it verified rather than assumed, and reported back: both of round 5's new tests bite
exactly once under their targeted mutations; the two-root early-return explanation is
correct; the orphan-HEAD test passed 25 repeated runs; the README's suppression enumeration
is complete; the fixture equivalence reproduces, all four branch passes and all three
`ea05b28` passes returning `[]`; and the ten-row mutation table reproduces exactly,
`4/1/2/1/1/3/3/2/1/OK`. Plus the gates, 846 tests, stdlib-only, rule-map grammar, links,
rule-9 structure and `git diff --check`.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Minor (reported on both axes) | Round 5 narrowed "no check here can close it" in the README and in `docs/known-limitations.md` and **missed the test docstring**, which still carried it — an incomplete repair, which also makes `round-05.md`'s "Fixed" for that finding inaccurate. | **Fixed** |
| 2 | Minor | `test_marker_deletion_cannot_hide_simultaneous_governed_edits` is still overbroad. Measured against a **pre-marker** base, deleting both markers *while* modifying the rule and the confirmed layer makes all three passes return `[]`. What the test proves is the guarantee **when the base holds the markers**, so `round-05.md`'s "named for what it proves" was false. | **Fixed** |

Both were reproduced here before being fixed. Finding 2's measurement: pre-marker base,
both markers deleted, rule and layer both edited — `diff_base_findings`,
`blast_radius_diff_findings` and `interview_diff_findings` each return `[]`.

## The correction round 05 is owed

Two claims in `round-05.md` are wrong, and it is immutable:

- Its finding 3 is marked **Fixed**. The repair was **incomplete** — three of the four sites
  were narrowed and the test docstring was not.
- Its finding 4 says the test is "named for what it proves". It was not. The name still
  claimed a general property, and the property is conditional on the base holding the
  markers. It is now `test_marker_deletion_hides_nothing_when_the_base_holds_the_markers`.

Both are the same failure: **a grep-scoped sweep that was not re-run after the round's own
edits.** R2b measured that exact shape and named the countermeasure; round 5 did not apply it.

## Two more found by re-running the sweep

Round 6's sweep was run over every line this branch adds, not only the sites the round named,
and it found two universal claims of the branch's own making. Neither was a reviewer finding;
both are recorded because the sweep is the point.

- `diff_base_findings`' docstring said a non-ancestor base makes "every finding in the run" a
  difference between two lines of history. **False for the stateless checks**, which never
  read the base. It now says every finding *the diff passes raise*, and says the stateless
  ones are unaffected.
- `_roots_missing_from_base`' docstring said this file folds NFC+casefold "always where
  folding makes the check STRICTER". **False:** `casefold()` at `scripts/validate.py:2239`
  folds the roster header, which makes that check looser. The claim now covers the folds that
  match a **path** — `scripts/validate.py:3531` and `4232`, the two the argument actually
  rests on — and both of those do make their check stricter.

That is five and six on this branch's tally of a claim reaching past what it can support, and
the second and third caught by sweep rather than by review.

## Verification after the fixes

The changed lines were re-read against `git diff` before this entry was written. All four
fixes are prose — two test docstrings, one test name, two code docstrings — and no behaviour
changed, so the mutation table in `round-05.md` still stands; it was re-run by the reviewer
this round and reproduced exactly.

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, 846 tests, skipped=1
