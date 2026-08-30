# Round 02 — Codex review, 2026-08-30

**Reviewed:** commit `17950e4` (branch HEAD after round 1's fixes, against `main` at
`ea05b28`).
**Task:** `task-mtfjidtf-b3gyv0`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** One distinct finding, reported
on both axes — **Low** on Standards, **Moderate** on Spec/correctness.

The reviewer was pointed at round 1's repairs first, and told the three shapes this project
has measured previous rounds failing in. It found one, in the first shape.

The reviewer also reported what it cleared: the other round-1 repairs and their descriptions
in `round-01.md` match the lines that actually changed; the 0/7 and 0/2 baselines; `--diff
main` and `git diff --check` clean; `AGENTS.md` at 163 lines; no live markdown link at the
deleted proposal.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Moderate (Spec), reported again as Low (Standards) | Round 1's repair of `demo/README.md` replaced a sequencing error with a broader claim: "Changing the roster … is escalating too and needs a proposal in the same way". Not universally true. A roster **addition** in the diff that moves the root's pin v1→v2 is exempt under decision 8's migration-scoped bootstrap (`_bootstrap_roots`, `scripts/validate.py:4064`), and a roster **deletion** is a WARN rather than a proposal-requiring ERROR, because a proposal's target must be a file that still exists (`scripts/validate.py:4231`). The reviewer named this as the round-1 repair reaching for a stronger claim than the one it replaced. | **Fixed** |

Both citations were checked against `scripts/validate.py` at `17950e4` before the fix, not
taken on report. The sentence now reads: "The last change to the roster was escalating and
needed a proposal of its own" — the landed case, which is what the paragraph is about.

This is the same shape as round 1's Moderate, one round later and inside the repair for it.
That is the pattern the branch was warned about, arriving on schedule.

## One fix not asked for

`demo/walkthrough.md` said "The roster is governed the same way". That is the same
equivalence claim in three fewer words, on a site round 1 authored, and the bootstrap
exemption is roster-only so "the same way" is not exactly true. It now reads "The roster is
governed too", which asserts that the roster is governed without asserting that the
mechanism is identical. Recorded here because the reviewer did not raise it: R2b's measured
lesson is that a grep-scoped sweep must be re-run after each round, because a slice can
author a new site while repairing the old one.

## Verification after the fix

The changed lines were re-read against `git diff` before this entry was written, not
against the intent:

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, 824 tests, skipped=1

The reviewer reported none of the four disclosed items and no sandbox noise.
