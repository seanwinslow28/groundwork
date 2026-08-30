# Round 05 — Codex review, 2026-08-30

**Reviewed:** commit `6b2bd2e` (branch HEAD after round 4's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtflswgr-5h0ntg`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Standards: 3 findings, all
**Minor**. Spec/correctness: 2 findings, both **Minor**. No Major.

Every one is an accuracy finding against the record rather than the code, and every one was
reproduced here before being fixed. The reviewer re-ran the gates (844 tests skipped=1,
`0/7`, `0/2`, `--diff main` exit 0) and confirmed the rule-map grammar, links, stdlib-only
imports and a clean `git diff --check`.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Minor | The count overclaim again. Three root-indexed emission paths is right, but there are **three** source-level suppression points, not two: the all-unsupported early return, the changelog subtraction, and the candidate-pair filter. "Two" is only the number of downstream filters. | **Fixed** — count withdrawn |
| 2 | Minor | The claim that every added or repaired behaviour was mutation-checked was false. Two mutations left all 20 `TestDiffBaseContract` tests green: reverting the changelog loop from `gov_roots - unsupported` to `gov_roots`, and removing only the `ancestor is None` WARN. | **Fixed** — two tests added, both now bite |
| 3 | Minor | "No check here can close it" and "the one route" overstate the limit. The verified limit is that a check reading only the base tree and the working tree cannot distinguish the case; inspecting the commit history between base and HEAD could reveal a marker added and later deleted. | **Fixed** — narrowed, in three places, and added to issue #40 |
| 4 | Minor | `test_deleting_the_marker_is_still_caught_when_the_base_holds_it` claimed to catch marker deletion. It catches the separately introduced rule and layer rewrites: with only the pin and manifest deleted under a base holding both, all three passes return `[]`. | **Fixed** — renamed and its prose narrowed |
| 5 | Minor | The `0 error(s), 8 warning(s)` measurement in `round-04.md` is not reproducible from the committed artifacts: the new test's fixture through `main()` returns `1 error(s), 0 warning(s)` on both revisions, because its active rule lacks a roster. | **Fixed** — the numbers are withdrawn and the equivalence restated against the committed fixture |

## Reproductions

Finding 2, measured before the tests were written: reverting the changelog filter → `OK`;
removing only the `ancestor is None` branch → `OK`. Both silent.

Finding 4, measured: `_root(d)`, then delete the pin and the manifest and nothing else —
`diff_base_findings`, `blast_radius_diff_findings` and `interview_diff_findings` each return
`[]`. That is not a gap. A pin is not a governed class, and the manifest is excluded from the
frozen set on purpose. It is why the test edits a rule and a layer as well, and the test is
now named for what it proves: `test_marker_deletion_cannot_hide_simultaneous_governed_edits`.

Finding 5, restated so the next reader can run it. The measurement that matters is the
**equivalence**, not the absolute counts, and it now uses the fixture the branch commits —
the one in `test_deleting_the_marker_under_a_pre_marker_base_says_nothing`. Every stateful
pass returns `[]` against that fixture on this branch, and every stateful pass returns `[]`
on `main` at `ea05b28`. The `0 error(s), 8 warning(s)` pair in `round-04.md` came from a
hand-made fixture in a scratch directory that was never committed, so nobody could re-run it.
That entry is immutable; this is its correction.

## The count, a fourth time

Finding 1 is the fourth instance on this branch of a repair reaching past what it replaced,
and the third time the vehicle was a count. Round 1: "accepts any escalating change".
Round 3: "the one place a finding is attributed to a root". Round 4, correcting round 3:
"two places". Round 5: three.

The count is now **withdrawn** rather than corrected again. The README names the three
sites without numbering them, which is the move R2b measured as the one that works: name a
range a reader can run, not a total they have to trust. `round-04.md` is immutable, and its
"two" stands corrected here.

## Finding 3 changes what the open Major claims, and it is worth being clear about

The open Major stays open, and the maintainer's decision stands. What narrows is the
**justification**: the gap is unreachable *by a check reading the base tree and the working
tree*, which is what the passes read today. Walking `base..HEAD` for a deleted marker is a
route nobody has explored, and it may well work. Issue #40 now carries it, so the follow-up
is not filed on a premise this round showed to be too strong.

## Verification after the fixes

The changed lines were re-read against `git diff` before this entry was written. The full
mutation table, re-run in one go, with the two rows finding 2 said were missing:

| Mutation | Result |
|---|---|
| the tripwire stops raising the skip ERROR | FAILED (4) |
| `diff_base_findings` dropped from `main()`'s pass tuple | FAILED (1) |
| the folded, fail-open pin lookup restored | FAILED (2) |
| round 1's `gov_roots` subtraction restored | FAILED (1) |
| the changelog pass reverted to the full `gov_roots` | FAILED (1) |
| the governed-root ERROR removed from the contract | FAILED (3) |
| the interview-manifest ERROR removed | FAILED (3) |
| ancestry never reports | FAILED (2) |
| only the unanswerable-ancestry WARN removed | FAILED (1) |
| none | OK |

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, **846 tests**, skipped=1
