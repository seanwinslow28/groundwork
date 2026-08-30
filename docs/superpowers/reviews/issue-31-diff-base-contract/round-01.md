# Round 01 — Codex review, 2026-08-30

**Reviewed:** commit `bf33166` (the branch's single implementation commit, against `main`
at `ea05b28`).
**Task:** `task-mtfk1rxr-yn5fsn`, launched with `--background` from the worktree.
**Verdict, in the reviewer's words:** **does not approve.** Spec/correctness: 3 findings,
two **Major** and one **Minor**. Standards: **zero findings**.

The reviewer was told to attack evasion and fail-open paths specifically, and to measure
rather than reason. It did both: the first Major carries a monkeypatched measurement, and
the second carries a pure-function one.

It also reported what it cleared: the v1→v2 bootstrap remains mutually exclusive with the
new suppression, `since=None` prevents demotion, the MIGRATIONS.md rationale holds, the
persona-company measurement kept in `interview/generate.md` is properly framed as history,
and the rule-map grammar, links, naming, comment density and rule-9 record placement
conform. It ran the 13 contract tests, the 5 rule-map tests and all three validator
commands.

## Findings

| # | Severity (verbatim) | Finding | Disposition |
|---|---|---|---|
| 1 | Major | The suppression can be separated from its contract ERROR. `blast_radius_diff_findings` removed unsupported roots from `gov_roots` and returned nothing about it, so the pass called alone returned zero ERRORs — and one of the new tests asserted exactly that silence. Safety depended on `main()` scheduling `diff_base_findings` first: the reviewer monkeypatched that pass out and measured the pre-generation case going from **exit 1 to exit 0**, with all 13 new tests still passing, because none exercised the composed CLI. | **Fixed** |
| 2 | Major | The pin lookup folded NFC+casefold unconditionally, which conflates distinct governed roots. `_roots_missing_from_base({"A"}, {"a/groundwork.pin": ...})` returned the empty set: a base holding `a/` satisfied a separate `A/` root on a case-sensitive filesystem, the contract ERROR did not fire, and with valid proposals the new root could pass while the tripwire ran against a base that does not hold it. NFC-equivalent distinct siblings had the same hole. | **Fixed** |
| 3 | Minor | The review record said a `--diff d20c04c` run "is now one contract ERROR". Measured output is **two** — that base holds neither `demo/groundwork.pin` nor `demo/interview/00-manifest.md`. The reviewer noted this challenges only the recorded count, not the intended rejection. | **Fixed** |

All three were reproduced here before being fixed, not taken on report:
`_roots_missing_from_base({"A"}, {"a/groundwork.pin": ...})` returns `set()` under the folded
lookup, and `python3 scripts/validate.py . --diff d20c04c` prints two ERRORs.

## What the fixes are

**Finding 1.** The message moves into one constructor, `_unsupported_root_finding`, and
`blast_radius_diff_findings` raises it for every root it skips. `Finding` is a namedtuple
whose `since` defaults to `None`, so the two emitters produce **equal** findings and
`main()`'s existing dedupe — which is there because "a fatal context ERROR arrives
identically from each" — prints one line. The pass no longer narrows its own scope in
silence, which is the failure shape this whole slice exists to fix, and its safety no longer
rests on the schedule. Two tests now exercise `main()` directly: one asserts exit 1 and
exactly one printed line for the governed-root half, the other does the same for the
manifest half, which only `diff_base_findings` raises and which is therefore what guards
that pass's entry in the tuple.

**Finding 2.** The lookup is exact. The grounds are in the docstring: this file folds in
several places, but always where folding makes a check **stricter** — `governed_classes`
folds so a case-rename cannot walk a path out of its governed root, and its own comment
already records that an exact-case root stays authoritative precisely so two distinct
case-sibling roots do not cross-demand each other's proposals. Here folding ran the other
way. `_bootstrap_roots` looks up the same pin exactly (`base_rels.get(pin_rel)`), so exact
matching is also the file's existing rule for this file. The cost — a false ERROR where base
and working tree spell one root differently — fails closed and is now in
`docs/known-limitations.md`.

**Finding 3.** The line now names the command and states what running it produces.

## A self-caught item, and the direction it was wrong in

Before this round's verdict arrived, two items were written down as self-caught. The first
was finding 1, found independently and with a better measurement than the note had.

The second was an asymmetry inside `diff_base_findings`: the pin lookup folded and the
manifest lookup did not, with no stated reason. The asymmetry was real. **The intended fix
was to fold the manifest lookup too, and that would have widened finding 2 rather than
closing it** — it would have put the fail-open match on both conditions. The round arrived
first. Recorded because the note was written before the verdict and reversing it is the
honest outcome, not a detail to drop.

## Verification after the fixes

The changed lines were re-read against `git diff` before this entry was written. Each of
this round's three code fixes was mutation-checked — the assertion has to bite:

| Mutation | Result |
|---|---|
| tripwire stops raising the skip ERROR | FAILED (2) |
| `diff_base_findings` dropped from `main()`'s pass tuple | FAILED (1) |
| the folded, fail-open pin lookup restored | FAILED (1) |
| none | OK |

- `python3 scripts/validate.py .` — 0 errors, 7 warnings, exit 0
- `python3 scripts/validate.py demo` — 0 errors, 2 warnings
- `python3 scripts/validate.py . --diff main` — exit 0
- `python3 -m unittest discover -s tests -q` — OK, **841 tests**, skipped=1

The reviewer was told a clean round is a real outcome, which six items the record already
discloses, and that `TemporaryDirectory` errors in its sandbox are environmental. It
re-raised none of the six and reported no sandbox noise.
