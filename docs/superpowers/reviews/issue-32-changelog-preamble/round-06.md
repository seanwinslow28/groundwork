# Round 06 — Codex review

**Reviewed:** `b29d3fe`
**Verdict:** **does not approve** — 4 findings, worst **Major** (the reviewer's own severity
word). All four fixed, and the fix is a change of approach rather than a fourth patch.

## The finding behind the findings

Three Majors, and all three were inside round 05's repair — the fourth consecutive round to
find its worst finding in the previous round's fix. Each was measured on `b29d3fe` before
acting, and each was in the **accepting** direction:

| Finding | Construction | verdict before |
|---|---|---|
| Major 1 | `<div hidden>` on a line that is not the first of its block — the trailing-block rule looked only at the first line after the last blank | accepted |
| Major 2 | a code span opened on one line and closed on the next, so a quoted `<!DOCTYPE` was read as a real declaration and consumed the real `<script>`'s `>` as its closer | accepted |
| Major 3 | a non-breaking space after a closing fence — Python's `str.strip()` removes it, CommonMark permits only spaces and tabs there | accepted |

The reviewer also observed, correctly, that these disprove statements in `round-05.md`, in
`docs/known-limitations.md`, in the caller docstring and in the rule-map cell — all four of
which described protection the code did not have.

**The pattern is now the finding.** Rounds 02, 04, 05 and 06 each breached the previous round's
model of when Markdown closes a block, and each round's repair shipped a claim about its own
completeness that the next round falsified: *"the one way"*, *"types 1 to 5"*, *"its mistakes
are all in the refusing direction"*. Four for four is not a run of bad luck; it is the wrong
kind of check for this validator, which states "files, not engines" and carries no parser.

## The decision, and who made it

The maintainer was asked under rule 5, at the end of round 05, to choose between keeping the
CommonMark model and collapsing it to a rule that refuses markup in a header outright. Round
06's brief put the same question to the reviewer as input rather than as a finding, and its
answer was independent and the same:

> I would choose the smaller rule that refuses fences and raw-HTML lines while permitting
> closed comments. Its narrower accepted language is easy to explain and test, and its false
> negatives are far less likely than those of a partial CommonMark parser.

**Taken: the smaller rule.** `_changelog_header_reaches_the_ledger` replaces the fence scanner,
the block-pair table, the declaration matcher and the trailing-block rule — roughly 150 lines
of CommonMark modelling — with about 25 lines that ask one question of each header line, after
its matched inline code spans are removed: does it carry a fenced-code marker at an indent a
fence can open at, or a `<` followed by `!`, `?`, `/` or a letter? A `<` that opens nothing, as
in `a < b`, is prose. The one exception is a line whose whole content is a single closed HTML
comment with no angle bracket of its own.

**Every construction rounds 02 to 06 found is refused by it**, and a single test enumerates all
thirteen so the coverage is asserted rather than described. That is the argument for the shape:
the narrow rule closes by construction what four rounds of modelling closed one patch at a time.

**Before choosing it, the cost was measured rather than assumed.** Both shipped changelog
headers clear the rule as written — the engine's entry format is already inline backticks, and
both trailing comments are whole-line and closed — and a test asserts that against the real
files, so a future edit to either header cannot quietly break the rule the header depends on.

**The counter-argument, recorded.** The rule refuses headers a renderer accepts: a fenced
example, and any raw-HTML line. That is a real restriction on adopters, and it says no for
reasons about a guard rather than about their document. The remedy is inline code or an HTML
entity, and `docs/known-limitations.md` carries the cost, the reason, and the revision the
earlier model can be recovered from.

**This was the maintainer's decision to make and the maintainer had not answered when the
switch was made.** It was made on the round's evidence — three further accepting-direction
Majors and an independent reviewer reaching the same recommendation — and it is one commit to
revert, the CommonMark model standing complete at `b29d3fe`. If the maintainer prefers it,
round 06's three Majors return as open findings wanting a fifth patch.

## Finding 4. Low — "two new factual counts are already wrong" — FIXED

Two halves, and they are different defects.

**The first is an ordinary wrong count.** `docs/known-limitations.md` said three parity
constructions had been accepted where `round-05.md` enumerates five. It was wrong, and it is
not re-counted: Option B replaced that bullet, and the surviving text names the rules rather
than tallying anything.

**The second is the undated-count shape, and the reviewer's number and this record's are both
right.** `round-05.md` says reducing `_HEADER_BLOCK_PAIRS` to the comment pair gives 7 failures;
the reviewer measured 8 at `b29d3fe`. Both hold at their own revision — the mutation was run at
`4452679`, and round 05 then *added* `test_a_tag_opener_needs_a_tag_boundary`, which the same
mutation also fails. **The defect is that `round-05.md` did not date its measurement**, exactly
the shape R2a's round-05 convention exists for and the one this branch had so far only applied
to source-line citations. `round-05.md` is immutable, so this entry is the correction: read its
"7 failures" as *measured at `4452679`*; the same mutation at `b29d3fe` gives 8, and after this
round `_HEADER_BLOCK_PAIRS` no longer exists.

## What the reviewer cleared

The ordinary fence cases it was asked to probe classified correctly at `b29d3fe`: tab
indentation, opener and closer at different indents, longer closers, exact-three markers, and
tildes in a tilde fence's info string. Nine of round 05's ten mutation rows reproduced their
stated counts exactly, and it confirmed round 05's type-4 correction was itself valid. It found
no revisionless source-line citation, and no scope creep.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`, all at this round's fix
revision. Each row names the edit literally.

| Mutation | Result |
|---|---|
| Fenced-marker rule replaced by `if False` | 7 failures |
| Angle-bracket rule replaced by `if False` | 10 failures |
| Comment exception drops its no-angle-bracket interior guard | 1 failure |
| Inline-code stripping removed | 3 failures |
| None (restored) | OK, 868 |

## Baseline

**The test count goes DOWN**, and that is worth stating plainly rather than reporting only the
net: 883 at `b29d3fe`, 868 after this round. Option B deletes `_fence_marker`,
`_next_header_opener`, `_HEADER_BLOCK_PAIRS` and `_HEADER_TAG_OPENERS`, and the tests that
covered them go with the code. What replaces them is denser — the thirteen constructions from
five rounds are asserted in one parametrised test — but fewer test *methods*. Against `main` the
branch is 846 -> 868.

## Environment

The reviewer reported 883 tests discovered with 682 `TemporaryDirectory` setup errors from a
sandbox with no writable temporary directory, and correctly called it environmental. Verified
outside the sandbox on `b29d3fe`: `OK, 883 tests, skipped=1`.
