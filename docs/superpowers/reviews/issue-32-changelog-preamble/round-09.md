# Round 09 — Codex review

**Reviewed:** `e37197e`
**Verdict:** **does not approve** — Spec 1 **Major** and 1 **Moderate**; Standards 1
**Moderate** and 1 **Low** (the reviewer's own severity words). All four fixed.

## Findings

### Spec 1. Major — a U+00A0 line satisfies rule 3 without being a blank line — FIXED

Rule 3 tested `header_lines[-1].strip() != ""`. **Python's `str.strip()` removes U+00A0;
CommonMark's blank line is empty or ASCII spaces and tabs only.** So a header ending in a
no-break space satisfied the guard while ending nothing, and a link reference definition's title
ran straight through the committed ledger:

```
[x]: /url "
<U+00A0>
- 2026-07-26 | skills/a/SKILL.md | committed | scribe | a1b2c3d
"
```

Measured `reason=None` on `e37197e`, with the replacement entry entering the appended span where
it could also suppress the missing-changelog WARN. Rule 3 now strips only `" \t"`.

**A note on measuring this one.** The first probe of it returned `hidden` and looked like a
false alarm — because the probe had been written with an ordinary space rather than a real
U+00A0. Re-run with the actual character it reproduced exactly as reported. The reviewer's
finding was right and the builder's first measurement was wrong; recorded because "measure, do
not reason" only helps if the measurement is of the thing claimed.

### Spec 2. Moderate — the entry grammar accepts lines a renderer treats as code — FIXED,
by closing the route rather than by changing the grammar

`_changelog_first_entry` and the stateless check both use an unrestricted `str.strip()`, so a
four-space-indented `- ` line counts as an entry while CommonMark renders it as code. With a
header ending in an indented-code chunk, that protected line continues the code block and an
appended unindented replacement is the only live list. Measured accepted.

**The important half of this finding is what it says about the taxonomy: indented code is the
one block a blank line does not end**, so mode 3 could never reach it, and modes 1 to 3 were
therefore not exhaustive. The fix is a fourth rule — no header line indented four spaces or a
tab with content after it — rather than a change to the entry grammar, because tightening
`_changelog_first_entry` would make an indented entry *not an entry*, leaving an entry-less base
and the whole file editable. That is the wrong direction, and the three sites that share the
`"- "` test stay identical, as they were designed to.

Neither shipped changelog carries an indented line, so the new rule costs them nothing —
measured before it was added, not after.

### Standards 1. Moderate — "the replacement prose still overclaims" — FIXED

The seventh consecutive round to find the previous round's self-description ahead of its code,
and this time the overclaim was in text written *specifically to stop overclaiming*: round 08
added "classifying by termination mode is not a claim that each mode is implemented completely",
and the same paragraph still said the three modes covered "everything else". Indented code was
neither covered nor implemented.

The docstring, `docs/known-limitations.md`, the rule-map cell and the caller docstring now name
four cases, say what "blank" means, and say that indented code is the block a blank line does
not end. `round-08.md` and its README paragraph are immutable or superseded; this entry is the
correction of record for both.

### Standards 2. Low — "round 08 miscounts the wrong-reason coverage event" — FIXED

`round-07.md` called its accidental-coverage discovery the "second time", and `round-08.md`
called the later one the "second time" as well. Both cannot be right, and round 08's was at
least the third. **Withdrawn rather than renumbered** — this is the sixth count corrected on
this branch and the second ordinal, and the rule that has worked is to describe the event
instead of numbering it. The two entries are immutable; read them as "a recurrence" rather than
as a tally, and this entry as the correction.

The reviewer separately confirmed the "five counts corrected" claim in `round-08.md` checks out.

## What the reviewer cleared

Round 08's blank-terminated fence cases do exercise rule 1 before rule 3 — the specific thing
round 08 said it had fixed, verified independently. And no separate defect in the base-anchored
protected span, the appended-span boundary, the `CHANGELOG_REASONS` fallback, or
`appended_targets`, which is the second consecutive round to clear the parts of the slice that
are actually issue #32 rather than its consequence.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`.

| Mutation | Result |
|---|---|
| Rule 3's blankness test returned to `str.strip()` | 2 failures |
| Rule 4, the indented-code check, disabled | 2 failures |
| Rule 4 drops its whitespace-only guard, so a blank line reads as indented code | 1 failure |
| Rule 4 tests four spaces but not a tab | 1 failure |
| None (restored) | OK, 869 |

## Environment

The reviewer reported all four gate commands matching, including `OK, 868 tests, skipped=1`,
having found a writable temporary directory this round where earlier rounds did not. Verified
independently on `e37197e`. After this round the suite is `OK, 869, skipped=1`.
