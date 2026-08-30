# Round 15 — Codex review

**Reviewed:** `c82aa4c`
**Verdict:** **does not approve** — Standards 1 **Low**, Spec 1 **Low** (the reviewer's own
severity word). Both fixed. **No accepting-direction defect**, the fourth consecutive round to
reach that.

The round was framed as the merge decision and declined on two Low defects. It confirmed all
four of round 14's repairs are exact, reproducing both of that round's mutation counts.

## Findings

### Spec 1. Low — a sixth one-sided rule edge — FIXED

`_opens_a_container`'s **ordered** branch accepts a space or a tab after its delimiter, and only
the **hyphen** branch's tab was covered. Changing the ordered branch to space-only left all 871
tests green.

The reviewer built the end-to-end case that regression would open, which is what makes this more
than a coverage note: editing `12.  header` to `12.\theader` moves the item's content column, so
an eight-space-indented committed entry becomes indented code. The production guard returns
`("hidden", [])` — correctly — while the mutation accepts it and credits the appended replacement
entry. **Not a current gap; a real accepting-direction regression left unpinned.** Two cases now
pin it, for `.` and for `)`, and the mutation fails.

That is the sixth one-sided edge on this branch: rounds 13 and 14 found five between them, and
each time the search for the next one was made and came up empty a round before someone else
found it. The lesson has held every time it was tested — **a rule needs a case at each edge, and
the edge you did not think of is the one a mutation finds** — so the mutations are now run at
both edges of every branch by default rather than on suspicion.

### Standards 1. Low — the record contradicted itself, and its tallies had gone stale — FIXED

Two halves.

`round-14.md` opens by declaring four findings and then, four lines later, calls them "both
findings" — a sentence meant to say that its two *kinds* of finding were the right grounds to
decline on, which reads as a count that contradicts the header. `round-14.md` is immutable; this
entry is its correction: **it carried four findings, in two kinds.**

And the README's closing paragraph still said "ten consecutive rounds" and "seven counts have
been corrected" when round 14 had already made those eleven and eight — a tally that goes stale
every single round by construction.

**The response is to stop keeping the tally.** That paragraph now names the shapes instead: an
overclaim replaced by a differently-wrong overclaim; a sentence written to stop overclaiming
that overclaimed; a brief that reverted to wording an earlier round had been killed by; a claim
that a sweep was complete made in the entry that had not completed it; a refusal justified by a
hazard that does not exist; a mutation row naming an edit other than the one run, twice; a test
comment claiming a measurement behind a case that had none. Those are the useful record. The
number was never the useful part, and a number that must be incremented by every future round is
a defect generator — which the last four rounds demonstrated by each finding it wrong.

## What the reviewer confirmed

All four of round 14's repairs are exact: the one- and three-column comment cases exercise the
stripped-line exception, with the raw-line mutation producing exactly two failures; `</script>`
exercises rule 2's slash branch alone, with removal producing exactly one; the provenance comment
correctly scopes itself to the five measured cases and separates the proactive bare block quote;
and the README correctly names the three over-refusing round-13 regressions.

No current accepting-direction defect. The base-anchored suffix, the appended-span boundary, the
fail-closed reason mapping, `appended_targets` ordering, and both shipped headers before and
after a simulated append are all sound. It counted 846 methods at `b2cb1d0` and 871 at `c82aa4c`
independently.

## Mutations added this round

| Mutation | Result |
|---|---|
| The ordered-marker branch accepts a space but not a tab | 2 failures |
| None (restored) | OK, 871 |

Green before this round's two cases were added.

## Environment

The reviewer's sandbox had no writable temporary directory this round: 871 tests discovered with
682 `TemporaryDirectory` errors, which it correctly called environmental, running the 27 pure
changelog tests and the three validator commands instead. Verified outside the sandbox on
`c82aa4c`: `OK, 871 tests, skipped=1`.
