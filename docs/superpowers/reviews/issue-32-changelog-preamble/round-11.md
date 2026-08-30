# Round 11 — Codex review

**Reviewed:** `daf26a5`
**Verdict:** **does not approve** — Spec 1 **Major** and 1 **Moderate**; Standards 1
**Moderate** (the reviewer's own severity words). All three fixed.

This is the round the branch was waiting for. Asked for a **completeness audit** rather than
for an attack — enumerate the CommonMark block types and the GFM table extension, and say for
each which rule governs it and whether that classification is correct — it produced the matrix
and used it to disprove the exhaustiveness claim. The claim was the builder's, made after
re-deriving the taxonomy independently, and it was wrong.

## Findings

### Spec 1. Major — list-container continuation — FIXED

```
base:  1.  header                                    new:  1. header
                                                           
       - 2026-07-26 | ... committed ...                     - 2026-07-26 | ... committed ...
                                                           - 2026-07-28 | ... replacement ...
```

`1.` followed by **two** spaces gives a content column of four, and the seven-space entry sits
three columns past it: a nested list item. `1.` followed by **one** space gives a content column
of three, and the same seven-space line sits four columns past it: indented code. The entry is
byte-identical in both, so the base-anchored boundary passes; what changed is the marker's
trailing space. Measured `reason=None` on `daf26a5`.

**This is the first construction on the branch that changes what an entry renders as without
touching the entry or adding any markup near it**, and it disproves the supporting claim that a
line whose `.strip()` begins `"- "` therefore renders as a list item. The reviewer added two
more counter-examples to that claim: a four-space-indented entry is code, and `- - -` is a
thematic break, both of which `_changelog_first_entry` calls entries.

**Fixed** by a fifth rule: a header line opening a list item or a block quote is refused, so the
header opens no container the ledger can fall inside. `_opens_a_container` recognises `>`, a
`-`/`*`/`+` followed by a space or tab or nothing, and up to nine digits followed by `.` or `)`
and then a space or tab or nothing. Neither shipped changelog header opens a container —
measured before the rule was added.

**Not fixed, and said rather than left implicit:** the two counter-examples about the entry
grammar itself. Tightening `_changelog_first_entry` to reject an indented or thematic-break
"entry" would make such a line *not an entry*, which for a base holding only that line means an
entry-less base and a wholly editable file — the wrong direction, and a tightening in a slice
that only loosens. The three sites sharing the `"- "` test stay identical. The disagreement
between the validator's entry grammar and a renderer's is now a named limitation rather than an
assumption.

### Spec 2. Moderate — rule 4 did not implement CommonMark indentation — FIXED

Two headers returned False that contain indented code. `" \tindented code"` — CommonMark
advances a tab to the next multiple of four, so one space then a tab reaches column four, while
rule 4 tested for four literal spaces or a leading tab. And `"    <!-- closed -->"` — the
comment exception ran **before** rule 4 and skipped the line, but at column four that line is
code, not a comment.

Fixed with `_md_indent`, which counts a tab the way CommonMark does, and by moving rule 4 ahead
of the comment exception. Both are mutation-checked, including the ordering.

### Standards 1. Moderate — the prose still contradicted itself — FIXED

The docstring opened on "three ways", called the taxonomy closed, then added a fourth case and
called indented code "the one block" that survives a blank line. Lists disprove both, and the
same conflict reached `docs/known-limitations.md` twice, a test section heading, and the README,
which contradicted itself eight lines apart. The reviewer also caught `round-09.md` claiming the
rule-map cell and the caller docstring "now name all four cases" when neither did.

Every mutable site is rewritten. The organising idea is now stated as *how a block relates to a
blank line*, with the explicit note that it has never been a proof of coverage and has twice
been found incomplete. The rule-map cell names the five ways a header can reach the ledger.
`round-09.md` is immutable; this entry is its correction.

**Eight consecutive rounds have found the previous round's self-description ahead of its code.**
One was in a sentence written specifically to stop overclaiming; one was in a review brief that
reverted to the framing an earlier round had already been killed by. The pattern is not
carelessness about any one sentence — it is that a description written in the same breath as a
fix inherits the fix's optimism.

## The completeness matrix, which is the round's real product

The reviewer classified every CommonMark block type and the GFM table against the rules and
found exactly two wrong: **indented code** (mixed tabs, container relativity, exception
ordering) and **list / list item** (the Major above). Thematic break, ATX heading, setext
heading, fenced code, HTML types 1 to 7, link reference definition, paragraph, block quote and
GFM table were classified correctly, with types 6 and 7 refused by rule 2 where rule 3 would
have sufficed — a conservative refusal, not a defect. It also settled lazy continuation as **not**
a separate gap: it applies only to paragraph-continuation text and cannot cross a true blank
line, and an entry's `- ` is a block start rather than lazy text.

That matrix is worth more than the findings. It is the first coverage statement on this branch
that is enumerated rather than asserted.

## What the reviewer cleared

The base-anchored protected suffix; `_changelog_first_entry` sharing its grammar with the
stateless check and `appended_targets`; entries remaining contiguous and byte-identical; the
appended span beginning after the protected suffix rather than after the old line count;
`CHANGELOG_REASONS` failing closed; header validation running before appended targets are
credited. Third consecutive round clearing the part of the slice that is actually issue #32.

It also checked all 30 `FOUND_BY_REVIEW` rows and confirmed each takes the rule its label
implies — 12 rule 1, 12 rule 2, four rule 3, two rule 4 — with no wrong-reason pass of the
round-08 shape.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`.

| Mutation | Result |
|---|---|
| Rule 5, the container check, removed | 7 failures |
| Rule 4 back to a literal four-space test | 1 failure |
| A tab advances one column instead of to a multiple of four | 3 failures |
| Rule 4 moved back after the comment exception | 4 failures |
| The container check misses block quotes | 1 failure |
| The container check misses ordered markers | 3 failures |
| A bullet marker needs no space after it | 3 failures — **and 0 at first** |
| None (restored) | OK, 871 |

The last row is the third time on this branch a mutation has exposed coverage that did not
exist. Making the bullet test stricter left the suite green, because nothing asserted that a
line beginning `*emphasis*` or `-dash-prefixed` is ordinary prose. Three prose cases were added
and the mutation then failed. A stricter mutation surviving is as much a gap as a looser one,
and only the looser direction is intuitive to check.

## Environment

The reviewer reported all four gate commands matching at `daf26a5`, including `OK, 869 tests,
skipped=1`, and a clean worktree. After this round the suite is `OK, 871, skipped=1`.
