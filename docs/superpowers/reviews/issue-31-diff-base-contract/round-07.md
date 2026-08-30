# Round 07 — Codex review, 2026-08-30

**Reviewed:** commit `bce7347` (branch HEAD after round 6's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfmvvjy-k29q9n`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Standards: 1 **Minor**.
Spec/correctness: 2 **Minor**. In its words: no validator-behaviour defect was found. It
confirmed the renamed test and both revised test docstrings accurately describe their
assertions, and re-ran the gates, the 846 tests, the rule-map grammar, the links, the
review-record structure and `git diff --check`.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Minor | `docs/known-limitations.md` still published `0 error(s), 8 warning(s)` as the result of the marker-deletion setup. Round 5 withdrew that pair as coming from an uncommitted, unreproducible fixture — and withdrew it from the review README only. | **Fixed** |
| 2 | Minor | "Every finding the diff passes raise" is still too broad: `blast_radius_diff_findings` emits working-tree scan ERRORs that read no base at all, measured with a divergent base and an unreadable directory. The stateless half of the sentence was true. | **Fixed** |
| 3 | Minor | The file does not fold "NFC+casefold wherever it matches a PATH". Of the two path-matching sites, `scripts/validate.py:3531` calls `casefold()` alone and `4233` normalizes NFC and then casefolds. Both make their check stricter; only one performs the combined fold the sentence named. | **Fixed** |

All three were confirmed here against the source before being fixed.

## The correction round 06 is owed

Findings 2 and 3 land inside round 6's two repairs, and `round-06.md` records both as fixed:

- Its account of the ancestry docstring — "it now says every finding *the diff passes raise*"
  — describes a claim that is still too broad, for a reason round 6 did not consider: the
  tripwire's working-tree scan ERRORs are diff-pass findings that never read the base. The
  docstring now separates the findings raised **by comparing** from the ones that read no
  base, and names both kinds that read none.
- Its account of the fold docstring says the claim "now covers the folds that match a
  **path** — `scripts/validate.py:3531` and `4232`". Two things wrong in one clause: the
  second site is at `4233`, and the two do not perform the same fold. The docstring now names
  each site and what it actually does.

Round 6 narrowed two universals it had found by sweep, and both replacements were themselves
inexact. That is the branch's measured shape once more — the replacement for an overclaim has
to be checked as carefully as the overclaim was.

## The sweep, run wider this time

Rounds 5, 6 and 7 each found a repair that had been applied to some of its sites and not all,
so this round's sweep covered every mutable file the branch touches rather than the sites the
round named: `scripts/validate.py`, `tests/test_validate.py`, `docs/known-limitations.md`,
`docs/rule-map.md`, the review README, and the three corrected prose sites. It looked for
absolute counts and for universal quantifiers.

One further site was narrowed as a result, and no reviewer raised it: the README called
`_unsupported_root_finding` "the one constructor both emitters use". True, and a superlative
in a document whose superlatives have been wrong five times. It now says "the constructor
both emitters call".

Two counts were checked and **kept**, because both name the setup that produces them and a
reader can re-run either: the M2 row in the README's measurement table, which gives the base
and the edit, and the `--diff d20c04c` line, which gives the command. The count withdrawn in
finding 1 was withdrawn because its fixture was never committed, not because it was a number.

## Verification after the fixes

The changed lines were re-read against `git diff` before this entry was written. All four
fixes are prose — two docstrings in `scripts/validate.py`, one bullet in
`docs/known-limitations.md`, one line in the README — and no behaviour changed, so
`round-05.md`'s mutation table still stands. Round 6's reviewer reproduced it exactly and
round 7 found no behaviour defect.

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, 846 tests, skipped=1
