# Round 08 — Codex review

**Reviewed:** `dde4a51`
**Verdict:** **does not approve** — Spec 1 **Major**; Standards 1 **Moderate** and 1 **Low**
(the reviewer's own severity words). All three fixed.

## Findings

### Spec 1. Major — a fence behind a container marker — FIXED

```
1. ```
   ## Entries

   - 2026-07-26 | skills/a/SKILL.md | committed | scribe | a1b2c3d
   ```
- 2026-07-28 | skills/a/SKILL.md | replacement | scribe | c3d4e5f
```

Measured on `dde4a51`: `reason=None`, and the replacement entry entered the appended span,
where it could also suppress the missing-changelog WARN for a track-1 edit. Rule 1 tested
`line.lstrip(" ")` for a leading fence marker, so it never saw a fence opened inside an
ordered-list item — the `1. ` sits in front of it. The committed entry, three-space indented and
therefore still an entry by the `strip()` test, becomes fence content; the blank line above it
satisfies rule 3.

**Fixed** by testing for containment rather than position: a run of three backticks or tildes
**anywhere on a line** is refused. That covers a bullet, an ordered marker, a block quote, and
any nesting of them, without enumerating container types — the same move that fixed rule 2,
which has always tested `<` anywhere on a line rather than at a line's start. It refuses more
than CommonMark calls a fence, and since round 07 removed the inline-code exception there is
nothing a header needs to say that requires the sequence.

**Note what nearly hid this.** Probing the pure predicate with `["1. ```"]` returns True — via
**rule 3**, because that header's last line is not blank. Only a blank-terminated input
exercises rule 1. That is the second time on this branch a check passed for the wrong reason,
and round 07's own finding of the same shape is why it was caught here: the constructions added
to `FOUND_BY_REVIEW` this round are blank-terminated on purpose, with a comment saying why, and
there is an end-to-end test carrying the reviewer's construction whole.

### Standards 1. Moderate — "the closed-taxonomy claims are disproved" — FIXED

The reviewer is right that the claim as a reader would take it was false, and the distinction is
worth stating exactly rather than defending. The construction **is** mode 1 — it is a fenced
block — so the taxonomy classified it correctly. What failed was rule 1's *implementation*,
which did not recognise a fence behind a container marker. But the prose in the source, in
`docs/known-limitations.md`, in `round-07.md` and in the README said the three modes "form a
closed set" in a context where a reader would take it as a statement about what the guard
catches, and the guard did not catch this.

Corrected in the two mutable places: the docstring and `docs/known-limitations.md` now say that
classifying by termination mode is what stops the rule being a list of constructs, that this
says nothing about whether each mode is implemented completely, and that six rounds found gaps
in the implementations rather than in the taxonomy. `round-07.md` and its README paragraph are
the immutable and the already-superseded copies; this entry is the correction of record.

**This is the sixth consecutive round to find the previous round's self-description
overreaching**, and the pattern has narrowed to one thing: every time the code got better, the
sentence describing it got ahead of it. The replacement above deliberately describes only what
the guard does.

### Standards 2. Low — "rule 3 is repeatedly miscounted as costing three lines" — FIXED

Correct: it is one comment and one `return`, replacing a previous `return False`, so its net
executable cost is one changed line. **Withdrawn, not re-counted.** That is the fifth count
corrected on this branch, and every one of the five was wrong in the direction of making the
work sound larger or tidier than it was.

## What the reviewer cleared

Rule 2's character set and case handling; the overlapping-comment slice arithmetic; both
rewritten shipped format examples and the append-simulating test; and — reviewed here for the
first time since round 05, having been asked for explicitly — the base-anchored protected span,
`_changelog_first_entry`, the `CHANGELOG_REASONS` fail-closed mapping, and the `appended_targets`
boundary. No separate defect in any of them. That matters: those are the actual subject of issue
#32, and the header rule is only its consequence.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`.

| Mutation | Result |
|---|---|
| Rule 1 returned to a position test — `line.startswith` instead of containment | 6 failures |
| None (restored) | OK, 868 |

## Environment

The reviewer reported 867 tests discovered with 682 `TemporaryDirectory` setup errors from a
sandbox with no writable temporary directory, and correctly called it environmental. Verified
outside the sandbox on `dde4a51`: `OK, 867 tests, skipped=1`. After this round the suite is
`OK, 868, skipped=1`.
