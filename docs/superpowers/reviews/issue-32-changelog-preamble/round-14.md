# Round 14 — Codex review

**Reviewed:** `3c35799`
**Verdict:** **does not approve** — 4 findings, all **Low** (the reviewer's own severity word).
All four fixed. **No accepting-direction gap**, the third consecutive round to reach that.

Asked outright whether it would approve, it declined on record accuracy and one-sided test
coverage. Both are the right grounds to decline on, and both findings landed on round 13's
repairs — which is where nearly every round has found its worst finding.

## Findings

### Standards 1. Low — "over-refusal tally is wrong" — FIXED

`round-13.md` and the README said four of the seven regressions over-refuse. **Three do** — the
two-character fence threshold, the Unicode-letter opener, and the space-only blank. The other
four under-refuse. Worse, `round-13.md`'s very next sentence says "this round three more", so the
entry contradicted itself two lines apart.

**Eighth count corrected on this branch.** The response is the one that has worked: the number is
withdrawn from the mutable README and the three are named. `round-13.md` is immutable; this entry
is its correction — read its "four of those seven" as **three**, and its own next sentence is
right.

That every checked count on this branch has been wrong is no longer a coincidence worth
remarking on individually. It is the branch's signature defect, and the record's answer to it is
to stop counting: name the cases and let the reader count them.

### Standards 2. Low — "one new test is falsely described as mutation-derived" — FIXED

Round 13 added six cases under a comment saying each survived a recorded regression. Five did.
The bare block-quote case was added proactively and is covered by round **11**'s block-quote
mutation, not by any of round 13's seven. The provenance claim was false, and a maintainer
reading it would take that boundary for mutation-measured evidence.

The comment now scopes itself to the five it measured, and the block-quote case sits under its
own note naming what actually covers it. A test's provenance is a factual claim like any other.

### Spec 1. Low — "the fifth over-refusing edge remains unpinned" — FIXED

The comment exception keys on `stripped`, so a closed comment indented one to three columns is
allowed — deliberately, since at column four rule 4 has it first. **Nothing asserted that.**
Changing `stripped.startswith` to `line.startswith` left all 871 tests green while refusing
`   <!-- safe -->`, which an adopter could reasonably write.

Round 13 went looking for a fifth over-refusing edge and did not find it; round 14 did. Two cases
now pin it, at one column and at three, and the mutation fails with two failures.

### Spec 2. Low — "rule 2's slash branch is unpinned" — FIXED

`<` followed by `/` is refused, and `docs/known-limitations.md` says so, but removing `/` from the
tuple left all 871 tests green. A declared refusal with no test behind it. `</script>` is now a
case — it is refused by the slash branch alone, since no letter follows the `<` — and the mutation
fails.

## What the reviewer cleared

The stale mutation row is gone; `_opens_a_container`'s rewritten docstring and the ASCII-letter
correction in `docs/known-limitations.md` are accurate; the base-anchored suffix, the appended
span, the fail-closed reason mapping and the appended-target ordering are sound; both shipped
headers pass before and after a simulated append; and all seven of round 13's mutation counts
reproduce exactly as `1, 2, 1, 2, 2, 1, 2`. It ran every gate itself, including the base revision
at 846 tests.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`. Both were green before this
round's cases were added.

| Mutation | Result |
|---|---|
| The comment exception keyed on the raw line, not the stripped one | 2 failures |
| Rule 2 drops `/` from its opener set | 1 failure |
| None (restored) | OK, 871 |

## Environment

The reviewer reproduced every gate command, including `OK, 871 tests, skipped=1` on the branch
and `OK, 846 tests, skipped=1` on the base `b2cb1d0`.
