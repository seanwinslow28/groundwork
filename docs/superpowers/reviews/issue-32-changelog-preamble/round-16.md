# Round 16 — Codex review

**Reviewed:** `8202ab6`
**Verdict:** **does not approve** — 2 findings, both **Low** (the reviewer's own severity word).
**No accepting-direction defect**, the fifth consecutive round to reach that.

This is the last review round of the slice. The maintainer stopped the loop after it and chose
Option A — see `round-17.md`, which is not a review round.

## Findings

### 1. Low — "round 15's record rewrite still contains false and stale claims" — FIXED

Round 15 replaced a running tally with a named list of defect shapes, on the reasoning that a
tally goes stale every round by construction. **The list was right and the prose around it was
not**, in three places:

- "The last seven" mutations were covered by round 13 — but rounds 14 and 15 had since added
  rows, so "the last seven" no longer names the seven meant.
- "Every round from 02 onward found the previous round's self-description ahead of its code" —
  **rounds 03 and 10 crashed with no findings at all**, and round 02 reviewed no previous
  round's repair.
- "Every count a reviewer checked was wrong" — **reviewers reproduced correct counts in rounds
  13, 14 and 15.**

The reviewer called this merge-blocking for its own review while noting rule 9 permits a
maintainer override with the finding recorded.

The finding is worth more than the fix. Round 15 removed a stale tally *because* tallies go
stale, and the replacement was itself three overclaims — including one that overstated how badly
the branch had been overclaiming. Positional references like "the last seven" go stale exactly
as counts do. The corrected text names the rounds and drops every superlative.

### 2. Low — a seventh one-sided rule edge — NOT FIXED; the code it describes no longer exists

Rule 2 refused `<` only when followed by a recognised character, so `<` at end of line was
allowed — correctly — but nothing asserted it. Mutating rule 2 to also refuse `after == ""` left
all 27 pure changelog tests green, which would have made header prose like `Comparison: a <`
start failing without a test noticing. Current behaviour correct; coverage only.

**Disposition: superseded.** Option A deletes rule 2 along with the rest of the header guard, so
there is no longer a branch to pin. It is recorded rather than closed silently, because it is
also the seventh consecutive one-sided edge found in that guard and so is evidence for the
decision that removed it.

## What the reviewer confirmed

Round 15's two ordered-tab cases are exact, with the space-only mutation producing exactly two
failures and the end-to-end construction behaving as `round-15.md` describes. Round 15's
correction of round 14 is accurate. The base-anchored protected suffix and appended span are
sound; unknown reasons fail closed; appended targets are credited only after validation. Both
shipped headers pass before and after a simulated append. The rounds table and the 846 → 871
baseline check out. **No current accepting-direction defect.**

## Environment

871 tests discovered with 682 `TemporaryDirectory` errors from a sandbox with no writable
temporary directory, correctly called environmental; the 27 pure changelog tests and all three
validator commands were run. Verified outside the sandbox on `8202ab6`: `OK, 871, skipped=1`.
