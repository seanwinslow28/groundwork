# Round 13 — Codex review

**Reviewed:** `8888fae`
**Verdict:** **does not approve** — Spec 1 **Low**; Standards 3 **Low** (the reviewer's own
severity words). All four fixed. No finding above Low, and none in the accepting direction.

## Job 1: the coverage result, independently re-derived

The round was asked not to take round 12's central result on trust but to re-derive it. It did,
against CommonMark 0.31.2 and the GFM table specification, and **agrees: there is no
accepting-direction gap in the current guard.** Its matrix covers thematic break, ATX and setext
headings, indented code (including tab stops and the comment ordering), fenced code (including
fences behind containers), HTML types 1 to 7, link reference definitions with multiline titles,
paragraphs, blank lines under the ASCII-space-or-tab definition, block quotes, lists and list
items, GFM tables, and lazy continuation — which it confirms is not a separate gap, since it
cannot cross the required blank line.

**Two independent rounds now agree on that**, derived separately, after eight rounds that each
found a way through. It is the result the branch has been working toward and it is worth stating
as its own thing rather than folded into a findings list.

The reviewer also confirmed the deliberate entry-grammar non-fix, the base-anchored suffix and
appended-span boundary, the fail-closed reason mapping, the appended-target ordering, the rounds
table, the 846 → 871 baseline, and that all of `FOUND_BY_REVIEW` reaches the rule its label
implies. It reproduced round 12's four mutation counts exactly — 2, 1, 1 and 4 — and checked the
base revision `b2cb1d0` at 846 tests itself.

## Findings

### Spec 1. Low — "several rule boundaries remain unpinned by tests" — FIXED

The suite stayed green through seven separate regressions. **Measured here, each applied alone:**

| Regression | Before | After |
|---|---|---|
| Rule 2 drops `?` from its opener set, so `<?pi` runs through the ledger | green | 1 failure |
| Rule 5 drops the hyphen bullet, so a bare `-` header holds the entry | green | 2 failures |
| Rule 5's marker requires a space, not a tab, so `-\titem` is not a container | green | 1 failure |
| Rule 5's ordered marker requires content, so a bare `1.` is not a container | green | 2 failures |
| The fence threshold tightens to two characters, wrongly refusing `~~struck~~` | green | 2 failures |
| Rule 2 treats any letter as an opener, wrongly refusing `<étude` | green | 1 failure |
| Blank means space-only, wrongly refusing a tab-only separator | green | 2 failures |

**Four of those seven are the over-refusing direction**, and that is the part worth keeping. A
rule needs pinning at both edges: the leaky edge is the one you think to test, and the strict
edge is the one that silently narrows what an adopter may write. Round 11 found the first
instance of this shape, round 12 the second, and this round three more — enough that it is now a
standing check rather than a curiosity.

The cases are added to the two parametrised matrices, which is why the test **count** does not
move: they are `subTest` rows inside existing methods.

### Standards 1. Low — the README kept the row round 12 corrected — FIXED

The mutation table carried both the wrong row from round 11 ("rule 4 moved after the comment
exception | 4 failures") and round 12's corrected pair ("moved | 1", "deleted | 4"), so it
contradicted itself and its own preamble. **A correction that adds the right row without
removing the wrong one is not a correction**, and this is the mutable half of the record where
removal was available. The stale row is gone.

### Standards 2. Low — the replacement docstring was false — FIXED

`_opens_a_container` claimed a ten-or-more-digit marker is a conservative refusal whose digits
"may still trip the bullet or quote tests". It returns `False`, as the branch's own test
requires. **Round 12 wrote that sentence while fixing a false claim about block quotes** — the
tenth consecutive round in which a repair's own prose overreached, and the second time in two
rounds that the overreach was in a *justification for a refusal* rather than a claim of
protection. The docstring now names the one genuine conservative refusal, `* * *`, and states
both digit bounds, each pinned by a test.

`docs/known-limitations.md` also said `<` plus "a letter" where the implementation correctly
means an ASCII letter; corrected, with the reason.

### Standards 3. Low — "round 12 overcounts the preceding accepting rounds" — FIXED

`round-12.md` says nine rounds found a route into the ledger. The record supports **eight**: 02,
04, 05, 06, 07, 08, 09 and 11. **Seventh count corrected on this branch, and the third ordinal.**
`round-12.md` is immutable; this entry is its correction. Every count on this branch that has
been checked has been wrong, and every one of them was wrong in the direction of making the work
sound larger. That is the whole finding, and the response is the one that has worked before: the
number is withdrawn, and the rounds are named — 02, 04, 05, 06, 07, 08, 09, 11 — so a reader can
count them without trusting me.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`. Each row names the edit
literally. All seven were green before this round's test cases were added and fail after.

| Mutation | Result |
|---|---|
| Rule 2 drops `?` from its opener set | 1 failure |
| Rule 5 drops the hyphen bullet | 2 failures |
| Rule 5's marker requires a space, not a tab | 1 failure |
| Rule 5's ordered marker requires content after it | 2 failures |
| Fence threshold tightened to two characters | 2 failures |
| Rule 2 treats any Unicode letter as an opener | 1 failure |
| Rule 3's blank means space-only, not space-or-tab | 2 failures |
| None (restored) | OK, 871 |

## Environment

The reviewer had a writable temporary directory this round and reproduced every gate command
itself, including `OK, 871 tests, skipped=1` on the branch and `OK, 846 tests, skipped=1` on the
base `b2cb1d0`. The worktree stayed clean.
