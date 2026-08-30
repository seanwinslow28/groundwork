# Round 04 — Codex review, 2026-08-30

**Reviewed:** commit `a0fb017` (branch HEAD after round 3's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfl9web-4wnbyl`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Spec/correctness: 1 **Major**.
Standards: 3 findings, worst **Minor**.

It reproduced the gates independently — `0/7`, `0/2`, `--diff main` exit 0, `--diff d20c04c`
exactly two contract ERRORs — and confirmed the rule-map and zero-dependency tests, a clean
`git diff --check`, and that round 3's behavioural account matches `55823e8`.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Major | Marker deletion evades the base contract. With the base predating generation *and* the working change deleting `groundwork.pin` or `00-manifest.md`, the marker is in neither `base_files` nor `wt_files`: the contract discovers no unsupported root or state, the tripwire returns dormant, and the frozen-layer pass derives none. The reviewer measured all three passes returning `[]` and a composed `main()` returning exit 0. Existing tests kept the marker in the working tree whenever the base lacked it, so they missed the class. | **OPEN** — see below |
| 2 | Minor | `round-03.md`'s correction itself overreaches: the function does not attribute findings per root in exactly two places, because `_unsupported_root_finding(g)` is a third root-indexed emission. Two is the count of places where governed findings are *suppressed*. | **Fixed** here (`round-03.md` is immutable) |
| 3 | Minor | The README said `main()` runs the contract before "the three passes that rest on it". Only two rest on the presence contract; `memory_diff_findings` is deliberately unguarded. | **Fixed** |
| 4 | Minor | The README's mutation-check evidence claim was broader than the entries carried: the tables covered rounds 1 and 2's repairs, not every originally added behaviour — ancestry in particular. | **Fixed**, by carrying the full table below rather than by narrowing alone |

## Finding 1 stays open, and here is the whole of why

**It is real, it is not a regression, and no check in this pass can reach it.**

*Not a regression.* Measured on a fixture whose base is a pre-generation commit and whose
working change deletes both markers:

| Code | Result |
|---|---|
| this branch at `a0fb017` | `0 error(s), 8 warning(s)` |
| `main` at `ea05b28` | `0 error(s), 8 warning(s)` |

Identical. The base-contract check neither creates the gap nor widens it.

*Not reachable.* The contract is evidence-based. With the marker in neither the base tree nor
the working tree, nothing distinguishes this from an ungoverned repository — which the
engine's own deliberately pin-less root is, and which must stay green. The one route that
would reach the interview half is inferring state from layer-shaped filenames, which reverses
`check_interview_state`'s stated doctrine that discovery is by content and a directory with
no manifest has no state to check. That is a locked decision, and reopening it inside a slice
about the base contract is not something a builder does.

*What was done anyway.* Two tests pin it —
`test_deleting_the_marker_under_a_pre_marker_base_says_nothing` asserts the silence so it
cannot deepen unnoticed, and `test_deleting_the_marker_is_still_caught_when_the_base_holds_it`
is the control showing `_pin_dirs`' and `interview_diff_findings`' base-reading guarantees
intact wherever the base does carry the marker. It is recorded in `docs/known-limitations.md`
with the measurement.

*The disposition was the maintainer's.* Put under rule 5 on 2026-08-30 with three options —
open and recorded, rejected as out of scope, or fixed in this slice — a recommendation and its
counter-argument. **Open** was chosen. Rule 9's three rejection grounds are a closed list, and
the honest reading is that none fits: the finding is not factually wrong, it is not superseded,
and calling a hole in the base contract "out of scope" for the base-contract slice would be
distorting a category to fit. The counter-argument recorded at the time: an open Major on a
slice whose subject is "the base contract is now enforced" invites the reading that the
enforcement is weaker than the record claims — which is exactly why the paragraph above says
what it does and does not cover.

The follow-up is filed as **issue #40**, with the measurement, the two commits it was measured
against, and the three questions a fix would have to decide.

## The correction round 03 is owed

`round-03.md` says the function attributes findings per root in two places. **Three, if you
count every root-indexed emission** — the candidate-file pass, the changelog pass, and
`_unsupported_root_finding(g)` itself. Two is the count of places where a governed root's
findings are **suppressed**, which is what the code comment and the README now say. The
correction reached one word past what it was correcting, in the entry that was correcting an
overclaim. Third instance of the same shape on this branch, and the second inside a sentence
about a repair rather than inside a repair.

## Verification after the fixes

The changed lines were re-read against `git diff` before this entry was written. Every
behaviour this branch adds or repairs, mutation-checked against
`TestDiffBaseContract` — this is the full table finding 4 asked for:

| Mutation | Result |
|---|---|
| the tripwire stops raising the skip ERROR | FAILED (3) |
| `diff_base_findings` dropped from `main()`'s pass tuple | FAILED (1) |
| the folded, fail-open pin lookup restored | FAILED (2) |
| round 1's `gov_roots = gov_roots - unsupported` restored | FAILED (1) |
| the governed-root ERROR removed from the contract | FAILED (3) |
| the interview-manifest ERROR removed | FAILED (3) |
| ancestry never reports | FAILED (1) |
| none | OK |

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, **844 tests**, skipped=1
