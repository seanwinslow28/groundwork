# Codex review record — branch `feat/issue-32-changelog-preamble`

The durable per-round record [rule 9](../../../agents/build-sessions.md) requires. Rule 9 is
the operative text; this file carries the parts that keep changing, and each `round-NN.md`
beside it is fixed once committed.

**Why `reviews/` and not `plans/`.** Rule 9 routes a branch to
`docs/superpowers/plans/<slice>-reviews/` only when its own commits add or change exactly one
plan. This branch adds and changes none, so it takes `reviews/<slug>/`, where `<slug>` is the
branch name's last path component. The path was free in `main` at branch time, so no collision
suffix applies.

**Branch:** `feat/issue-32-changelog-preamble`, cut from `main` at `b2cb1d0`.

## What this slice is

Issue #32: the #17 append-only changelog guard protected the **whole file**, so a changelog's
explanatory header was frozen at creation for the life of the repository. The demonstration is
`demo/governance/changelog.md`, whose preamble enumerated what escalates instead of being
logged and omitted the roster — which became the third governed artifact family at schema v2.
The correcting edit was made during the R1 slice, the gate went red, and it was reverted.

This branch narrows the guard to the ledger: **from the base file's first entry line on, the
file is append-only exactly as before; the header above it is editable.** The three design
questions the issue leaves open were decided by the maintainer before any code was written,
and [`round-01.md`](round-01.md) records them with their counter-arguments.

## What changed

| Site | Change |
|---|---|
| `scripts/validate.py` | `_changelog_append_only` narrowed; `_changelog_lines`, `_changelog_first_entry`, `_changelog_appended_span` added; caller reworked; the ERROR message corrected |
| `tests/test_validate.py` | 14 new tests; `_repo` gains a `changelog=` knob; `test_changelog_rewrite_errors` re-based on an entry-bearing fixture |
| `governance/changelog.md` | "This file is never edited or reordered" was falsified by this change — corrected |
| `demo/governance/changelog.md` | the defect itself: the roster added to the enumeration, and the "Append-only." claim narrowed |
| `docs/known-limitations.md` | the rotation bullet re-worded; three new entries for what the narrowed guard does not do |
| `docs/rule-map.md` | the `blast_radius_diff_findings` severity cell |
| `docs/roadmap.md` | "compares against the full base file" was falsified — corrected |

No new top-level `check_*` or `*_findings` function was added, so no new `docs/rule-map.md`
row is owed; the three new helpers are underscore-private and the existing row's severity cell
carries the change.

**The engine's own correction lands inside the region this change makes editable.** Worth
saying rather than leaving for a reviewer to find. It costs nothing in practice — the engine
root carries no `groundwork.pin`, so the tripwire is dormant there and that file has never had
this guard on it.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 01 | — | maintainer decisions, not a review round | — | — |

## Open findings

**None yet** — no review round has run.

## Rejected findings

**None.**

## Baselines

The test count **moves**: 846 → 860. The three validator commands are unchanged.

| Command | Before | On this branch |
|---|---|---|
| `python3 scripts/validate.py .` | 0 errors, 7 warnings, exit 0 | unchanged |
| `python3 scripts/validate.py demo` | 0 errors, 2 warnings | unchanged |
| `python3 scripts/validate.py . --diff main` | exit 0 | exit 0 |
| `python3 -m unittest discover -s tests -q` | OK, 846 tests, skipped=1 | OK, **860** tests, skipped=1 |

There is no pytest; the suite is unittest.

## Mutation table

Rule: prove a new assertion bites by breaking the thing it guards. Each mutation was applied
alone, the suite run, and the file restored. Run with `PYTHONDONTWRITEBYTECODE=1`.

| Mutation | Result |
|---|---|
| Restore the whole-file rule (`k = 0`) | 18 failures |
| Measure the appended span from the base line count instead of the protected block's end | 2 failures |
| Drop the "new file has no entry line" branch | 2 errors |
| Relax contiguity to set membership | 3 failures |
| None (restored) | OK, 860 |

## Status

**Not ready.** No Codex round has run.

## Maintainer items

**1. Decided at kickoff, 2026-08-30, before any code.** All three of issue #32's open design
questions, under rule 5, recorded in [`round-01.md`](round-01.md): narrow the guard (over
declining, and over a third option that moves the prose out of the guarded file); anchor the
boundary in the base rather than the new file; and let an entry-less base protect nothing.
Nothing is pending.
