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

## Open findings

None recorded yet.

## Rejected findings

None recorded yet.

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
