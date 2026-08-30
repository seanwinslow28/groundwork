# Round 07 — Codex review

**Reviewed:** `13bb323`
**Verdict:** **does not approve** — Spec 3 **Major** and 1 **Low**, Standards 1 **Moderate** and
3 **Low** (the reviewer's own severity words). All eight fixed.

Round 06 replaced a model of CommonMark's block rules with a rule that refused markup outright,
on the reasoning that four rounds had breached the model. Round 07 found the narrower rule
accepting three constructions, **two of which use no markup the rule looks at at all**. That is
the more useful finding: the problem was never which constructs were enumerated.

## Findings

### Spec 1. Major — a link reference definition with a multiline title — FIXED
### Spec 2. Major — a GFM table absorbs the pipe-delimited ledger — FIXED

Both measured accepted on `13bb323` before acting, and neither contains a `<` or a fence:

```
[x]: /url "
- 2026-07-26 | skills/a/SKILL.md | committed | scribe | a1b2c3d
"
```

A reference title may span non-blank lines and a definition renders nothing, so the committed
entry disappears. And:

```
Date | Path | Gist | Agent | SHA
--- | --- | --- | --- | ---
- 2026-07-26 | skills/a/SKILL.md | committed | scribe | a1b2c3d
```

GFM permits body rows with varying cell counts, so the committed entry renders as table data
while the appended replacement is the only live list. **Entries in this file are pipe-delimited,
which is what makes the table case specific to this format rather than a curiosity.**

### Spec 3. Major — the inline-code exception could not be trusted — FIXED by deletion

Two constructions, both measured accepted. `` \`<script>` `` — a backslash-escaped backtick, so
the first backtick is literal, the tag is live, and the closing backtick is unmatched; the
stripper read it as a span and removed the tag. And `` <!-- x ` --> <script> ` --> `` — stripping
the backticked middle left `<!-- x   -->`, which satisfied the whole-line comment exception,
while the real comment closes before a live `<script>`.

The exception is **deleted**, not repaired. `_strip_inline_code` and `_find_backtick_run` are
gone. A header that needs to show a `<` writes an HTML entity, and **both shipped changelogs
were rewritten to need none** — the engine's format example now reads `SKILL PATH | GIST | ...`
and the demo's `skills/NAME/SKILL.md`. That is a visible cost paid to remove a component whose
only job was to make an exception safe, and which two review findings showed it could not.

### The fix, and why its shape is different from the last five

The rule is now organised by **the three ways CommonMark ends a block**, which is a closed set
where a list of constructs is not:

1. **Runs to the end of the document.** Only fenced code. Refused: a fence marker at an indent a
   fence can open at.
2. **Runs to an explicit closer.** HTML blocks of types 1 to 5, every one of which begins with
   `<`. Refused: `<` followed by `!`, `?`, `/` or an ASCII letter.
3. **Runs to a blank line.** Everything else — a GFM table, a link reference definition, an HTML
   block of type 6 or 7, a paragraph, a block quote. Required: the line immediately above the
   first entry is blank, which ends any of them before the ledger begins.

Rule 3 is what rounds 02 to 07 kept missing, and it costs three lines. Both of this round's
markup-free Majors are closed by it, as are round 06's `<div hidden>` and round 05's
trailing-block case, independently of rules 1 and 2.

**This is an argument for completeness, not a proof of one**, and it is offered as the former —
which is the distinction the last four rounds' repair text kept failing to make.

### Spec 4. Low — "the all thirteen constructions claim is false" — FIXED

Correct on every count. The table labelled a case "a non-breaking space" while passing an ASCII
space; two round-05 constructions were absent; and deleting round 05's tests removed the only
coverage of `<!-->`. The claim is withdrawn rather than re-counted. `FOUND_BY_REVIEW` now lists
each construction with the round that found it and a label naming what the input actually
contains, both the NBSP and ASCII-space fence cases are present, and `<!-->` and `<!---->` are
back under the allowed-header test.

**A mutation that was assumed covered and was not.** Neutering the comment exception's
no-angle-bracket interior guard left the suite green: the live-tag-between-comments case was
refused by rule 3, because its input's last line was not blank, so the guard itself was never
exercised. The case is now blank-terminated and the mutation fails. Recorded because it is the
second time this branch has found coverage that existed only by accident, and only running the
mutation shows it.

### Standards 1. Moderate — "source falsely records the trade as the maintainer's decision" — FIXED

The docstring said "That trade was the maintainer's on 2026-08-30". It was not: `round-06.md`
and README item 2 both say the maintainer had not answered and the choice was the builder's.
The reviewer is precise that this is not the disclosed timing being re-raised but a
**contradictory replacement claim** that could let a later reader treat the choice as rule-5
approved. That is the honesty rule, and the docstring now says the shape was not approved under
rule 5, names the record, and points at the open item.

### Standards 2. Low — a missing newline merged two bullets — FIXED

`docs/known-limitations.md` read `revisited.- **A hyphen...`, burying the early-boundary
limitation inside the previous bullet. An editing defect of mine, and the kind a validator that
checks links but not list structure will not catch.

### Standards 3. Low — the mutable record repeats the undated-count defect — FIXED

The README's mutation row said the old pair-list mutation "gives 7" without naming the revision,
one entry after `round-06.md` corrected exactly that defect in `round-05.md`. Corrected in the
README, which is the mutable half of the record and so can be fixed in place.

### Standards 4. Low — "roughly 150 lines replaced by about 25" — FIXED by withdrawal

Measured `b29d3fe` to `13bb323` with `git diff --numstat`: 40 insertions, 129 deletions in
`scripts/validate.py`, and the new predicate 38 physical lines. The claim was not any of those.
**Withdrawn, not re-measured** — this branch has now had four counts corrected, and the rule that
worked in the previous slice is to name a command the reader can run instead of a figure they
must trust. The claim survives only in `round-06.md`, which is immutable, so this entry is its
correction; the README's copy of it was removed, the README being the mutable half of the
record.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`, all at this round's fix
revision. Each row names the edit literally.

| Mutation | Result |
|---|---|
| Rule 1, the fence-marker check, replaced by `if False` | 2 failures |
| Rule 2, the angle-bracket check, replaced by `if False` | 3 failures |
| Rule 3, the trailing-blank-line requirement, replaced by `return False` | 3 failures |
| Comment exception drops its no-angle-bracket interior guard | 1 failure — **and 0 before this round's test was corrected** |
| None (restored) | OK, 867 |

## Environment

The reviewer reported 868 tests discovered with 682 `TemporaryDirectory` setup errors from a
sandbox with no writable temporary directory, and correctly called it environmental. Verified
outside the sandbox on `13bb323`: `OK, 868 tests, skipped=1`. After this round the suite is
`OK, 867, skipped=1` — one fewer test method, the inline-code stripper's tests having gone with
the stripper. It also confirmed `test_both_shipped_changelog_headers_pass_the_rule` reads the
real files and would fail if either header gained a refused construct; that test now also
simulates an append, since rule 3 first engages on the append after the first.

It noted `gh issue view 32` was unavailable because its sandbox blocks network access, and that
it worked from the supplied context and the committed record instead.
