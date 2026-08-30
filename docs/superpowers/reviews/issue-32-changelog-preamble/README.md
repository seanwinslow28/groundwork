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
| `scripts/validate.py` | `_changelog_append_only` narrowed; `_changelog_lines`, `_changelog_first_entry`, `_changelog_appended_span`, `_changelog_header_leaves_a_block_open`, `_strip_inline_code`, `_find_backtick_run`, `_fence_marker`, `_next_header_opener` added; `CHANGELOG_REASONS` keys the ERROR text so an unknown reason cannot fall through the caller; the ERROR messages corrected and split |
| `tests/test_validate.py` | new tests for the narrowing, the appended span, and the header rule; `_repo` gains a `changelog=` knob; `test_changelog_rewrite_errors` re-based on an entry-bearing fixture |
| `governance/changelog.md` | "This file is never edited or reordered" was falsified by this change — corrected |
| `demo/governance/changelog.md` | the defect itself: the roster added to the enumeration, and the "Append-only." claim narrowed |
| `docs/known-limitations.md` | the rotation bullet re-worded; new entries for what the narrowed guard does not do — the unprotected header, the entry-less file, the early boundary, and the header block rule |
| `docs/rule-map.md` | the `blast_radius_diff_findings` severity cell |
| `docs/roadmap.md` | "compares against the full base file" was falsified — corrected |

No new top-level `check_*` or `*_findings` function was added, so no new `docs/rule-map.md`
row is owed; every function this branch adds or rewrites is underscore-private, which
`git diff main -- scripts/validate.py | grep '^+def '` shows, and the existing row's severity
cell carries the change.

**The engine's own correction lands inside the region this change makes editable.** Worth
saying rather than leaving for a reviewer to find. It costs nothing in practice — the engine
root carries no `groundwork.pin`, so the tripwire is dormant there and that file has never had
this guard on it.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 01 | — | maintainer decisions, not a review round | — | — |
| 02 | `c3af4d2` | **does not approve** — Standards 0, Spec 4, worst **Major** | 4 | `a5e07da` |
| 03 | `a5e07da` | **crashed — no verdict returned** (task `task-mtfxtd9w-ypa8lx`) | — | `206a78a` |
| 04 | `206a78a` | **does not approve** — Standards 4 worst **Moderate**, Spec 5 worst **Major** | 9 (8 distinct) | `4452679` |
| 05 | `4452679` | **does not approve** — Standards 4 worst **Major**, Spec 3 worst **Major** | 7 (5 distinct) | `PENDING-05` |

## Open findings

**None.** Of round 2's four findings, three are fixed and one is rejected with grounds.

## Rejected findings

**Round 2, finding 3 — Low, "demo roster claim includes unsupported deletions".** Rejected as
**factually wrong**: the finding reads a governance-routing sentence in
`demo/governance/changelog.md` as a claim about validator severity. Deletion of a governed file
*is* escalating; the source is [`proposals/README.md`](../../../../proposals/README.md)'s
"A governed file **deleted**" bullet, which states that directly and names the WARN as the
gate's own documented limitation. [`round-02.md`](round-02.md) carries the full grounds and the
reading under which the finding is fair.

## Baselines

The test count **moves**: 846 → 883. The three validator commands are unchanged.

| Command | Before | On this branch |
|---|---|---|
| `python3 scripts/validate.py .` | 0 errors, 7 warnings, exit 0 | unchanged |
| `python3 scripts/validate.py demo` | 0 errors, 2 warnings | unchanged |
| `python3 scripts/validate.py . --diff main` | exit 0 | exit 0 |
| `python3 -m unittest discover -s tests -q` | OK, 846 tests, skipped=1 | OK, **883** tests, skipped=1 |

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
| Neuter the open-comment check (round 2) | 5 failures |
| `rfind` to `find` in the open-comment check (round 2) | 1 failure |
| Caller branches on the two known reasons only (round 3) | 1 failure |
| Fence parity check removed (round 4) | 1 failure |
| CDATA pair removed (round 4 — its own entry mislabels this row as the whole list reduced to the comment pair, which gives 7; `round-05.md` carries the correction) | 1 failure |
| Comment closer searched from four characters in, not two (round 4) | 1 failure |
| Inline-code stripping removed (round 4) | 2 failures |
| Unmatched backtick run dropped rather than kept (round 4) | 2 failures |
| Fence closer no longer required to match the opener's character (round 5) | 1 failure |
| Fence closer no longer required to be as long as the opener (round 5) | 1 failure |
| Fence closer allowed to carry an info string (round 5) | 1 failure |
| Fence indent limit raised from three spaces to 99 (round 5) | 2 failures |
| Type-4 declaration match disabled (round 5) | 1 failure |
| Trailing raw-HTML rule replaced by `return False` (round 5) | 1 failure |
| Tag-boundary check replaced by `if True` (round 5) | 1 failure |
| Code span deleted rather than replaced by a space (round 5) | 1 failure |
| Backtick run matched by length >= N rather than == N (round 5) | 1 failure |
| None (restored) | OK, 883 |

## Status

**Not ready.** No round has approved yet. Round 2 did not approve; round 3 crashed without a
verdict, on a provider-side refusal caused by the brief's adversarial wording rather than by
anything in the branch; round 4 did not approve and its fixes are committed. Review threads are
not resumable, so each round is a new review.

**The arc so far, since it is the useful part.** Round 2 found a laundering route this branch
created — the pre-#32 whole-file guard had closed it by accident — and the repair for it
special-cased HTML comments. Round 4 found its worst two findings *inside that repair*: an
unclosed code fence and an unclosed raw-HTML block do the same job, so the repair had named a
construct where the rule needed to name a category. Round 5 then found its worst findings
inside **that** repair: the general rule's fence half was line parity, which is not the rule, and
five constructions left a fence open over the ledger; its claimed coverage omitted an HTML
block type; and deleting an inline code span could synthesise a closing tag out of text that
never held one.

Three rounds, three times the worst finding sat in the last round's fix — the previous slice's
measured pattern holding exactly. The recurring half is not the code: each round's repair also
wrote a claim about itself that the next round disproved. "The one way", "types 1 to 5", "its
mistakes are all in the refusing direction" — each written in the same commit as the code that
made it false.

**What round 2 changed about the slice, since it is the useful part.** Its Major was a
laundering route this branch itself created and the pre-#32 guard had closed by accident: an
HTML comment opened in the newly-editable header, closed after the ledger, hides every
committed entry from a reader while leaving all of them intact in the bytes. The narrowing now
carries an explicit check for it. Its other real catch was the same sweep failure the previous
slice measured — a claim corrected across `*.md` and not across the source's own docstrings.

## Maintainer items

**1. Decided at kickoff, 2026-08-30, before any code.** All three of issue #32's open design
questions, under rule 5, recorded in [`round-01.md`](round-01.md): narrow the guard (over
declining, and over a third option that moves the prose out of the guarded file); anchor the
boundary in the base rather than the new file; and let an entry-less base protect nothing.
Nothing is pending.
