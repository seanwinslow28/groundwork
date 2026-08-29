# Codex review record — branch `feat/roster-schema-v2`

Rule 9's durable record. This branch adds exactly one plan
(`docs/superpowers/plans/2026-08-29-r1-roster-schema-v2.md`), so the directory takes the
plan-adjacent form: the plan's filename with the leading `2026-08-29-` and the `.md`
removed. The path was verified free in `main` before the directory was made. Each
`round-NN.md` beside this file is fixed once committed; this file carries the parts that
keep changing.

**Branch:** `feat/roster-schema-v2`.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 1 | `199b5bc` | does not approve | 11 (2 BLOCKER, 4 HIGH, 3 MEDIUM, 2 LOW) | `7eb0885` |
| 2 | `4bee0a7` | does not approve | 7 (1 BLOCKER, 1 HIGH, 3 MEDIUM, 2 LOW) | `87817ae` |
| 3 | `fae6858` | does not approve | 6 (2 BLOCKER, 3 LOW, 1 MEDIUM) | `65fed7d` |

Twenty-four findings across three rounds. Twenty-three fixed; one rejected with grounds.
Round 2's axis split is corrected in `round-03.md`, not in `round-02.md`, which is immutable.

## Open findings

None.

## Rejected findings

One, at round 2. Rule 9 requires it listed here so the one move that closes a finding by
disagreeing with it is visible without reading every entry.

- **Round 2, S5 (the `demo/governance/changelog.md` half)** — that file's preamble lists
  what escalates and omits the roster. *Grounds:* the changelog is append-only under #17,
  and `_changelog_append_only` treats every committed line, preamble included, as an
  immutable prefix. The edit was made, `--diff main` went red on
  *"the governance changelog is append-only"*, and the edit was reverted. Observed, not
  predicted. See maintainer item 5.

## Maintainer items

1. **Two decisions taken at plan review, 2026-08-29**, both reserved by the design and both
   answered before any code was written. The engine-root roster's holders: `Head of IT` and
   `CISO` are both held by **Sean Winslow**, typed `human`, with the roster's `source` line
   stating that groundwork is solo-maintained. Intent-blind resolution: **accepted as a
   documented blind spot** rather than moving to typed owner references, which are recorded
   in `docs/known-limitations.md` as the known alternative.

2. **`CONTEXT.md` is edited by this branch.** Locked decision 8 makes `CONTEXT.md:57`'s "the
   only two artifact kinds the three buckets route" **false**, so the glossary entry is
   amended to three, naming the roster; `:61`'s escalating enumeration gains it too. Flagged
   here because the previous slice rejected a `CONTEXT.md` edit for scope, and this one is a
   different kind: transcribing a locked decision into the glossary that exists to record
   locked decisions. Leaving `main` carrying a false sentence would violate build-sessions
   rule 6.

3. **`docs/roadmap.md` is edited by this branch, beyond the design's named list.** Two of
   its V2 bullets became false the moment the bump landed: "the first `SCHEMA_VERSION` bump,
   and its two candidate passengers" (the bump has happened, and neither candidate rode it)
   and "per-check `since:` tags … dormant at v1 by construction" (now wired). Both are
   corrected as records of what happened; the S3 account beneath the first bullet is kept
   intact, reframed as *superseded rather than delivered*, which is decision 2's own
   wording. No roadmap commitment was added or removed.

4. **Carried, none blocking this slice** — the four items the previous session left open:
   what counts as adequate grounds for rejecting a finding
   (`docs/superpowers/reviews/review-record-rule/round-11.md`); whether `CONTEXT.md:105`'s
   consent invariant should carry the bootstrap qualification; whether a later `--diff` base
   must be proven to contain the generated root; and ratification of the rule-1 departure
   recorded in both merged logs.

## Maintainer item raised by round 2 — prose inside an append-only file

A governed append-only file carries explanatory prose that can go stale, and #17's
append-only rule makes it uncorrectable. `demo/governance/changelog.md`'s preamble enumerates
what escalates and now omits the roster; every available fix changes what the append-only
guarantee means — exempting the preamble from the prefix check, supporting rotation (already
a documented V1 gap), or routing the edit through a proposal, which the changelog is
deliberately not a target for. Recorded rather than resolved.

## Maintainer question raised by round 1 — the demo's staleness WARN

Round-1 finding N1 was correct twice over: the demo roster's `review_by` carried a cadence
no demo source records, and the plan's stated reason for it was false. Removing the invented
cadence leaves the 90-day policy default, `2026-08-09`, which **has passed** — so the demo's
roster now raises a staleness WARN. Two documented outputs moved with it:

- `python3 scripts/validate.py demo` → `0 error(s), **3** warning(s)` (was 2)
- `python3 scripts/validate.py .` → `0 error(s), **8** warning(s)` (was 7), the same WARN
  seen from the outer root

The tree currently carries the honest state. The maintainer's call is whether to keep it:

- **(a) Keep `2026-08-09`, the policy default** — the roster genuinely has not been
  re-confirmed since May, and the WARN demonstrates the staleness mechanism on real content.
  Cost: groundwork's own gate output carries a WARN that only gets older, and a WARN that
  never clears is a WARN people stop reading.
- **(b) A future `review_by`, justified by the demo's own convention** — every dated record
  under `demo/memory/` carries a `review_by` that has not yet passed (2026-09-30, 2026-10-31,
  2026-12-01), so the demo reads as a live company rather than an overdue one. Under (b) the
  roster would say plainly that its date follows that convention, not an elicited cadence.
  Cost: it is a convention of the fiction, not an answer anybody gave, and dating around a
  WARN is the move finding N1 exists to catch.

The builder's original date was (b) with a false reason attached. Presented rather than
decided, because it changes the gate output the maintainer reads every session.

## Also open, not taken

Whether `demo/governance/roles.md` should carry **Role rows** for the five offices
`demo/canon.md` assigns (CEO, VP Customer Success, Director of Product, VP Engineering, Head
of People). None of the demo's three rules names an office, so nothing requires them, and
Role rows are R2's elicitation work — so they were not added. Adding them would be true to
canon and would make a future role-named owner resolve.

## Verification the builder ran, before round 1

- `python3 -m unittest discover -s tests -q` → OK, **776 tests**, skipped=1.
- `python3 scripts/validate.py .` → `0 error(s), 7 warning(s)`, exit 0.
- `python3 scripts/validate.py demo` → `0 error(s), 2 warning(s)`, exit 0.
- `python3 scripts/validate.py . --diff main` → exit 0.
- **The bootstrap exemption was proven load-bearing, not vacuous.** With
  `demo/groundwork.pin` temporarily reverted to `schema_version: 1` in the working tree,
  `--diff main` produced exactly one roster finding on `demo/governance/roles.md` and exited
  1; restoring `schema_version: 2` returned it to exit 0. That single experiment
  demonstrates three mechanisms at once: the roster is genuinely classified as a governed
  file, the migration-scoped bootstrap is what silences it, and behind a v1 pin the roster
  ERROR demotes to the `since: 2` finger-pointing WARN while the gate stays red at the
  migration-boundary ERROR alone — which is exactly what MIGRATIONS.md promises.
