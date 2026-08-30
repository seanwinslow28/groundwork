# Round 08 — Codex review, 2026-08-30 (terminal)

**Reviewed:** commit `403d339` (branch HEAD after round 7's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfncglo-6km52y`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **approve.** Zero findings on both axes.

## Findings

**None.** No table, because there is nothing to put in one.

## What the round verified

It was pointed at round 7's four repairs and given each claim to check by enumeration or by
measurement rather than by reading. It reported back on all four:

- **The finding split in `diff_base_findings`' docstring is exact.** Memory findings all
  depend on base-listed records or an old/new comparison; interview findings all depend on
  base-listed layers or an old/new comparison; tripwire findings depend on base-derived
  changes **except** its working-tree unreadable-directory ERROR. The shared git-context
  errors resolve or read the base, and cannot coincide with a successfully classified
  non-ancestor base. So the findings that read no base are the stateless checks and the
  tripwire's scan ERRORs, which is what the docstring says.
- **The fold naming is accurate and complete.** Every `casefold()` in the file: the roster
  header at `2239`, `_governed_class` at `3531`, and the tripwire's fold at `4236`. The
  roster fold is not path-component folding and is correctly excluded; the two named path
  folds each make governance stricter, by keeping a classification across a case or NFC
  rename.
- **The marker-deletion measurement reproduces, both halves.** At `403d339` all four passes
  return zero findings against the committed fixture, and `ea05b28` loaded dynamically
  returns zero from all three of its stateful passes.
- **`round-07.md` describes what landed in `403d339`.**

It then re-ran the added-line sweep across the branch and found no remaining claim broader
than the implementation, confirmed the 22 contract tests including the git-plumbing
case-collision test, the full suite at 846 with one skip, the gates at `0/7`, `0/2`,
`--diff main` exit 0 and `--diff d20c04c` exactly two contract ERRORs, stdlib-only imports,
the restricted rule-map grammar, every relative link in the 13 changed markdown files, a
clean `git diff --check`, and rule-9 conformance.

## A correction to round 07, from what this round observed

`round-07.md` says round 6 "cited the second fold site as `4232` when it is `4233`". That
is sharper than the facts support. Round 6 cited `4232` against the source it was describing,
and its own docstring edit moved the site to `4233`; round 7's edit moved it again, and at
this branch's HEAD it is `4236`. The number was not wrong so much as **undated**, which is
what the citation convention settled in R2a's `round-05.md` exists to prevent: a citation
offered as evidence for where something is carries the revision it holds at. Neither
round 6's nor round 7's carried one. Round 8 raised no finding on this; it is recorded
because the observation is the reviewer's and the imprecision is this record's.

## The terminal round

Rule 9 says the last verdict is committed after the state it reviewed, so the commit
carrying this entry is not itself reviewed. That is accepted rather than exempted. What that
commit contains is this file, `round-07.md`'s fix-commit cell, and the README's status
section — no product content.

## Verification

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, 846 tests, skipped=1

The reviewer was told a clean round is a real outcome, that a finding it would not have
raised on a first read is not a finding, and which eleven items the record already discloses.
It re-raised none of them and returned an approval.
