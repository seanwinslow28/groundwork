# Round 02 — Codex review, 2026-08-30

**Reviewed:** commit `ed47901` (branch HEAD after round 1's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfklbvl-ifkq5y`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Spec/correctness: 1 **Major**.
Standards: 1 **Minor**, with two halves.

The round was pointed at commit `ed47901` — round 1's repairs — first, and told the three
shapes previous rounds have failed in. The Major is inside round 1's fix, which is the
pattern arriving on schedule.

It also reported what it cleared: `--diff d20c04c` prints exactly two contract ERRORs, once
each; `--diff main` returns 0 errors; the stateless gates match 0/7 and 0/2; the rule-map
tests pass; and the restricted table grammar, links, stdlib-only imports and
`git diff --check` are clean.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Major | Round 1's fix removed unsupported roots from `gov_roots` **before** `governed_classes` runs, which erases exact-root authority. With an existing `a/` root and a newly added distinct `A/` root, the folded fallback lets `a` claim `A`'s files, so the tripwire is not in fact skipped for the unsupported root: the run carries the correct `A/groundwork.pin` contract ERROR **and** a misleading "no pending proposal" ERROR on `A/…/access.md` attributed to `a/proposals/` — a proposal that cannot exist, since an `a` proposal cannot target outside `a`. The reviewer noted the existing tests miss the interaction, using either a pure lookup or the non-fold-equivalent `a/` and `b/`. | **Fixed** |
| 2 | Minor | Two mutable inventories stale at HEAD: the review record said "13 tests" where `ed47901` has 17, and both the record and `docs/known-limitations.md` said "four" limitations immediately before listing five. | **Fixed** |

## Reproducing the Major

It was reproduced here before being fixed, and reproducing it took a detour worth recording.
The filesystem this repository is developed on folds `A/` and `a/` into one directory, and
folds `ß/` into `ss/` as well — `_fold` is NFC+casefold, and `casefold("ß") == "ss"`, so that
was the second thing tried and it failed the same way. Two spellings of one root cannot exist
side by side on disk here.

What works is building the **base tree with git plumbing** rather than checking it out:
`hash-object -w`, `update-index --add --cacheinfo` against a throwaway `GIT_INDEX_FILE`,
`write-tree`, `commit-tree`. The base tree then holds `a/…` while the working tree holds
`A/…`, which is exactly the shape the finding describes, and git's object store does not
care what the filesystem can represent. Measured against that base before the fix:

```
ERROR A/groundwork.pin  --diff base predates this governed root: …
ERROR A/governance/constitution/access.md  escalating change (a constitution rule …) with
      no pending proposal — … a reviewable proposal in a/proposals/ (#18)
```

After the fix, only the first line.

## The fix

`unsupported` is no longer subtracted from `gov_roots`. `governed_classes` keeps resolving
each path against every root — which is what lets an exact-case root beat a fold-equivalent
one — and the unsupported roots are filtered out of `pairs`, at the one place a finding is
attributed to a root. The changelog pass iterates `gov_roots - unsupported`, and the early
return fires when `unsupported == gov_roots`. The reason is in a comment beside the line,
because the line now looks like a missing subtraction.

## A correction to round 01

`round-01.md` justified the exact-match fix by citing `governed_classes`' own comment, that
an exact-case root stays authoritative so two distinct case-sibling roots do not
cross-demand each other's proposals. **The citation was accurate and the fix beside it
removed the condition that made the cited property hold** — subtracting the root from
`gov_roots` is precisely what stops it being seen as an exact-case root. The reviewer named
this as falsifying that line. Entries are immutable, so the correction is here: the sentence
described `governed_classes` correctly and described round 1's own code wrongly.

## Verification after the fixes

The changed lines were re-read against `git diff` before this entry was written.

| Mutation | Result |
|---|---|
| restore round 1's `gov_roots = gov_roots - unsupported` | FAILED (1) |
| none | OK |

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, **842 tests**, skipped=1

The two stale counts were **withdrawn rather than corrected**: the record now names the
command that lists the tests, and `known-limitations.md` says "What it does not do" instead
of counting. A count in a document nothing checks goes stale on the next commit, which is
how both of these arose.
