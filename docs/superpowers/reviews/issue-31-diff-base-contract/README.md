# Codex review record — branch `feat/issue-31-diff-base-contract`

The durable per-round record [rule 9](../../../agents/build-sessions.md) requires. Rule 9
is the operative text; this file carries the parts that keep changing, and each
`round-NN.md` beside it is fixed once committed.

**Why `reviews/` and not `plans/`.** Rule 9 routes a branch to
`docs/superpowers/plans/<slice>-reviews/` only when its own commits add or change exactly
one plan. This branch adds and changes none, so it takes `reviews/<slug>/`, where `<slug>`
is the branch name's last path component. The path was free in `main` at branch time, so no
collision suffix applies.

**Branch:** `feat/issue-31-diff-base-contract`, cut from `main` at `ea05b28`.

## What this slice is

Issue #31: the `--diff` base contract is unenforced. `_git_diff_context` proved two things
about the base and no more — that the ref resolves (`git rev-parse --verify`) and that its
tree lists (`git ls-tree`). Two guarantees rested on a base nothing verified, and they
**failed in opposite directions.** That asymmetry is the slice.

### The three failures, measured before anything was written

Measured on this repository at `ea05b28`, not reasoned about:

| | Setup | Before |
|---|---|---|
| **M1 — the consent gate over-gates, loudly** | clean worktree, base `9699ae4`, which predates `demo/governance/constitution/` | **5 ERRORs**: two rules, one SKILL.md, two Owner's Cards, each "escalating change with no pending proposal". None was a change; all five were files the base did not hold. |
| **M2 — the frozen-layer guard fails silently** | one line appended to `demo/interview/01-role-and-scope.md`, base `1ffa50b^`, which predates `demo/interview/` | **0 errors, 7 warnings, exit 0.** A green run on a tree with an edited confirmed layer. |
| **M3 — a non-ancestor base invents findings** | clean, unmodified worktree at `ea05b28`, base a divergent commit off `1ffa50b` that edited one rule and one confirmed layer | **2 ERRORs**, naming changes this line of history never made. |

After the change, on the same three setups: M1 is **2 ERRORs** — one per contract condition,
both accurate — with the tripwire skipped for that root; M2 is **1 ERROR** naming the
manifest; M3 keeps its two findings and gains the **WARN** that says what the run is
comparing.

### The three decisions, all the maintainer's, all taken 2026-08-30

Put under rule 5 with the measurements above, a recommendation and its counter-argument.
All three recommendations were chosen.

1. **What to verify:** both — that the base holds each governed root's `groundwork.pin` and
   each interview state's `00-manifest.md`, and that it is an ancestor of HEAD.
2. **At what severity:** presence **ERROR**, ancestry **WARN**. Presence is where the promise
   breaks, and M2's failure is a false green that only an ERROR stops. Ancestry warns rather
   than refuses because `--diff <remote>/main` on a branch behind its remote is a real
   workflow in which the base legitimately is not an ancestor.
3. **Whether the invalidated pass still runs:** it does not. The contract ERROR **replaces**
   the pass it invalidates, which is what turns M1's five misleading ERRORs into one accurate
   one — the recorded counter-argument for enforcement was that the over-gating wall is an
   adopter's first experience of the gate at the documented "prove it" step. For M2 the
   suppression is a no-op: that pass was already contributing nothing.

The counter-argument on the record for enforcement at all — that the present behaviour fails
loud in the safe direction — is answered by M2 rather than dismissed: **one half does not
fail loud.** It fails silent, and exits 0.

## What is on the branch

- `scripts/validate.py` — `diff_base_findings`, plus `_base_is_ancestor` and
  `_roots_missing_from_base`. `blast_radius_diff_findings` subtracts the unsupported roots
  from `gov_roots`. `main()` runs the contract before the three passes that rest on it.
- `tests/test_validate.py` — `TestDiffBaseContract`. Each half has a paired control that
  breaks the thing it guards, and every behaviour added or repaired here was
  mutation-checked: the round entries carry those tables, and
  `python3 -m unittest tests.test_validate.TestDiffBaseContract -v` lists what is there now.
- `docs/rule-map.md` — one row for `diff_base_findings`, which
  `test_every_shipped_check_is_mapped` requires of any new `*_findings` function.
- `docs/known-limitations.md` — what the check does not do, including the two worth knowing:
  it checks a **manifest's** presence, not a layer's, and `memory_diff_findings` has the same
  base-derived shape with no check at all.
- `README.md`, `delivery/README.md`, `interview/generate.md` — three sites that described the
  old over-gating behaviour as what happens. This change falsified them, so this branch fixes
  them. That is not the documentation half of #31, which R2a landed at `d42e9ae`; it is prose
  this slice's own code made wrong.

## Not in this slice

- **`memory_diff_findings` has the same silent shape.** It derives its records from the base
  file list too, so a base predating `memory/` protects nothing and reports nothing. Issue #31
  names two guarantees; this is a third, and doing half of a finding filed elsewhere is the
  failure R2b's maintainer item 5 recorded. It is written down in `docs/known-limitations.md`
  and is the maintainer's to file.
- **Issues #32, #33 and C1–C13.** The kickoff holds each of these out.

## MIGRATIONS.md — why no bump and no `since:` tag

Read before assuming. The `since:` demotion is for requirements on **content shape**, so that
a repo pinned below the version that introduced one is not failed for content a permissive
reader accepted; and MIGRATIONS.md records that a tightening of that kind is from here on a
v2 change with a migration note. These three findings reject no content: the same tree under
the same pin passes against a base that meets the contract. What they constrain is the
invocation. The reasoning is in `diff_base_findings`' docstring so it travels with the code.
**Flagged for the maintainer at merge** rather than assumed settled.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 01 | `bf33166` | **does not approve** — Spec 3 (two Major, one Minor), Standards 0 | 3 | `ed47901` |
| 02 | `ed47901` | **does not approve** — Spec 1 (Major), Standards 1 (Minor) | 2 | |

A round's fix commit is filled in with the next entry: an entry cannot name the commit that
carries its own fixes.

## Open findings

**None.** Every finding raised on this branch is fixed.

## Rejected findings

None.

## Baselines

**CHANGED by this slice**, and stated here, in the merge commit and in the round entries,
because the next session inherits it:

| Command | Before (`ea05b28`) | After |
|---|---|---|
| `python3 scripts/validate.py .` | 0 errors, 7 warnings, exit 0 | unchanged |
| `python3 scripts/validate.py demo` | 0 errors, 2 warnings | unchanged |
| `python3 scripts/validate.py . --diff main` | exit 0 | unchanged |
| `python3 -m unittest discover -s tests -q` | OK, 824 tests, skipped=1 | OK, **842 tests**, skipped=1 |

The engine's own numbers do not move because `main` satisfies the contract it now states:
it is an ancestor of any branch cut from it, and it holds both `demo/groundwork.pin` and
`demo/interview/00-manifest.md`. What does move is old bases: `python3 scripts/validate.py . --diff d20c04c` was green at
0 errors and now returns two contract ERRORs — that base holds neither `demo/groundwork.pin`
nor `demo/interview/00-manifest.md` — because the check fires on the contract being broken,
not on whether over-gating happened to surface. The count is stated from running that
command, after round 1 found this line claiming one. There is no pytest; the suite is
unittest.

## Status

Under review.
