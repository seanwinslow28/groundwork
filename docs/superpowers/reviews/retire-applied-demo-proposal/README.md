# Codex review record — branch `chore/retire-applied-demo-proposal`

The durable per-round record [rule 9](../../../agents/build-sessions.md) requires. Rule 9
is the operative text; this file carries the parts that keep changing, and each
`round-NN.md` beside it is fixed once committed.

**Why `reviews/` and not `plans/`.** Rule 9 routes a branch to
`docs/superpowers/plans/<slice>-reviews/` only when its own commits add or change exactly
one plan. This branch adds and changes none, so it takes `reviews/<slug>/`, where `<slug>`
is the branch name's last path component. The path was free in `main` at branch time, so
no collision suffix applies.

**Branch:** `chore/retire-applied-demo-proposal`, cut from `main` at `ea05b28`.

## What this slice is

R2b landed the demo roster's re-confirmation together with the proposal that licensed it,
and left the proposal in place: removing it was legal only after the merge, so R2b recorded
it as maintainer item 4 rather than doing it. This branch does it.

`demo/proposals/org-map-re-confirmed.md` was **applied** — `demo/governance/roles.md`
carries its post-state (`valid_at: 2026-08-20`, `review_by: 2026-11-18`) at `ea05b28` — while
still declaring `status: pending`. Two things followed from that:

- `proposals/` is pending-only, and [`proposals/README.md`](../../../../proposals/README.md)
  states that an applied proposal's file is **removed**. The demo is a faithful model of a
  company repo, so a demo that keeps an applied proposal models the convention wrongly.
- The gate was **pre-licensed**. `_pending_proposal_radii`
  ([`scripts/validate.py:3956`](../../../../scripts/validate.py) at `ea05b28`) keys
  `target -> declared radii`, and `blast_radius_diff_findings` clears an escalating change
  when a pending proposal names that target **and** its declared radii include `escalating`;
  a proposal declaring only `track1-body` draws a mismatch ERROR instead. The removed
  proposal declared `escalating`, so while that file stood, a further escalating edit to the
  demo roster would have cleared the consent gate with no new proposal.

**What it does not do.** It does not replace the removed example. The demo now carries one
pending proposal, against a rule; the roster stays a governed family with no live worked
proposal in the demo. That was the maintainer's choice among three routes on 2026-08-30,
against keeping the applied file and against authoring a fresh un-applied roster proposal.

## Sites changed

Four, plus the deletion. Three of them stated a count — two of them the words "two pending
proposals", the third the ordinal "the second pending proposal" — and the fourth linked the
file, which after the deletion would have been a `check_links` ERROR:

| Site | Was |
|---|---|
| `demo/proposals/org-map-re-confirmed.md` | the applied proposal — deleted |
| `demo/governance/README.md` | linked the file as a pending proposal |
| `demo/README.md` | "two pending proposals" |
| `demo/walkthrough.md` | "The second pending proposal is the same mechanism" |
| `AGENTS.md` | "two pending proposals — one against a rule, one against the roster" |

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 01 | `173978d` | **does not approve** — Standards 1 (worst Low), Spec 3 (worst Moderate) | 3 distinct | `17950e4` |
| 02 | `17950e4` | **does not approve** — one finding, worst Moderate, reported on both axes | 1 | `f3840e5` |
| 03 | `f3840e5` | **approve** | 0 | terminal |

## Open findings

**None.** All three of round 1's findings are fixed.

## Rejected findings

**None.**

## Baselines

**Unchanged by this slice.** Verified on this branch:

| Command | Result |
|---|---|
| `python3 scripts/validate.py .` | 0 errors, 7 warnings, exit 0 |
| `python3 scripts/validate.py demo` | 0 errors, 2 warnings |
| `python3 scripts/validate.py . --diff main` | exit 0 |
| `python3 -m unittest discover -s tests -q` | OK, 824 tests, skipped=1 |

There is no pytest; the suite is unittest.

## What the rounds found, since it is the useful part

Three rounds, five findings, every one fixed. Round 1 found the only defect in the original
edits — and then rounds 1 and 2 both found their worst defect in the *previous* fix, in the
same shape each time: **a repair reaching for a stronger claim than the one it replaced.**
Round 1: "accepts any escalating change to a target a pending proposal names". Round 2, in
the repair for it: "Changing the roster is escalating too and needs a proposal in the same
way". Both were replaced by the narrow landed case, and round 3 approved with zero findings.

Two fixes were made that no reviewer asked for, both recorded in the entry that made them,
and both were the same sweep problem: this branch authored a new site while repairing an
old one.

## Status

**Ready for the maintainer to merge.** Round 3 approved with zero findings on both axes;
all five findings are fixed; none is open and none rejected; the gate is green on all four
commands and no baseline moved.

## Maintainer items

**1. Ratified at kickoff, 2026-08-30.** Three R2b items were put to the maintainer under
rule 5 before this branch was cut: the §7 typing-row placement (ratified as landed), the
issue #39 fold-in (ratified; #39 closed naming `06dd094`), and this proposal's removal —
chosen as its own commit, deliberately outside the issue #31 slice so rule 1 holds.
