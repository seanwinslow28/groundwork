# Round 03 — Codex review, 2026-08-30

**Reviewed:** commit `55823e8` (branch HEAD after round 2's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfl07fw-sfqa30`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Standards: 2 findings, worst
**Minor**. Spec/correctness: **zero findings**.

The round was pointed at commit `55823e8` — round 2's repair — and given a list of ways to
break it. It broke none of them, and said what it had checked instead: `pairs` is filtered
before `path_since` and before every candidate-level symlink, unreadable, deletion,
base-read, working-read and classification finding; the changelog pass excludes unsupported
roots separately; `appended_targets` and `proposals_cache` are reached only through supported
pairs; `_bootstrap_roots` cannot authorise an unsupported root because its exact base-pin
lookup fails; nested supported roots keep their authority while exact case siblings do not
cross-claim; the empty-root case returns before `unsupported == gov_roots` is evaluated and
the all-unsupported case returns the contract findings; and the plumbing regression test
genuinely exercises `a/` at base against `A/` in the working tree, would fail under round 1's
subtraction, scopes `GIT_INDEX_FILE` to its subprocesses, and leaves nothing outside the
temporary repository.

That is the first round on this branch to find nothing on the correctness axis.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Minor | The review record's "What is on the branch" still said `blast_radius_diff_findings` subtracts the unsupported roots from `gov_roots`. `55823e8` deliberately does the opposite. The mutable summary was describing the superseded round-1 implementation. | **Fixed** |
| 2 | Minor | The comment beside the code, and `round-02.md`, said the roots' findings are dropped "at the one place a finding is attributed to a root". False: the changelog pass is a second per-root emission path, and it carries its own `gov_roots - unsupported` filter. The reviewer proposed narrowing it to the candidate-file pass, and noted that `round-02.md` is immutable so its correction belongs in the next entry. | **Fixed** in the code and the record; **corrected below** for `round-02.md` |

## The correction round 02 is owed

`round-02.md` says, of the round-2 fix: "the unsupported roots are filtered out of `pairs`,
at the one place a finding is attributed to a root." **The clause after the comma is false.**
`blast_radius_diff_findings` attributes findings to a root in two places, and round 2's own
commit changed both — the candidate-file pass filters `pairs`, and the changelog pass
iterates `gov_roots - unsupported`. The entry described the fix accurately and then
generalised one half of it into a claim about the whole function.

This is the first measured failure shape yet again — a repair reaching for a stronger claim
than the one it replaced — and this time it landed in the sentence *describing* the repair
rather than in the repair. "The one place" is a superlative, which is the cheapest overclaim
available. The code comment now names the candidate-file pass and points at the changelog
pass beside it.

## Verification after the fixes

Both fixes are prose. The changed lines were re-read against `git diff` before this entry
was written; neither touches behaviour, and no mutation check applies.

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, 842 tests, skipped=1

The reviewer independently reproduced the gates and the `--diff d20c04c` measurement, and
confirmed imports are stdlib-only. It re-raised none of the eight disclosed items and
reported no sandbox noise.
