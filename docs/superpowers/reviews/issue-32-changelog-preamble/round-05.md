# Round 05 — Codex review

**Reviewed:** `4452679`
**Verdict:** **does not approve** — Standards 4 findings, worst **Major**; Spec 3 findings,
worst **Major** (the reviewer's own severity words).

Every finding is fixed. Round 04 replaced round 02's comment-only rule with a general one, and
this round found that the general rule's fence half was modelled wrongly and its stated
coverage was wrong about itself. That is the third round running to find its worst finding
inside the previous round's repair.

## Findings

### Spec 1 / Standards 1. Major — "fence parity fails open", and the prose said it could not

The fence half counted fence-looking lines and refused on odd parity. Parity is not the rule.
**Measured on `4452679` before acting** — each of these leaves a fence open over the ledger and
each was accepted:

| Header | Why the fence is still open | verdict before |
|---|---|---|
| ` ``` ` then `~~~` | a tilde run closes no backtick fence | accepted |
| ` ```` ` then ` ``` ` | a closer must be at least as long as its opener | accepted |
| ` ``` ` then `` ``` trailing `` | a closing fence carries no info string | accepted |
| ` ``` ` then a four-space-indented ` ``` ` | inside a fence that line is content | accepted |
| `<!--`, ` ``` `, `-->`, ` ``` ` | parity cancels a marker inside a comment against a real one | accepted |

and in the other direction, a four-space-indented marker standing alone was refused, being
indented content rather than a fence.

**Three of these five I found myself while the round was running**, by probing the cases this
round's own brief had asked the reviewer to check; the reviewer found those three and two more.
Recorded because the brief's question list is doing work and should be read as part of the
method, not as a formality.

**The prose was the worse half of this finding.** `docs/known-limitations.md` and the docstring
said the predicate's "mistakes are all in the refusing direction". They were not, and the claim
was written in the same commit as the code that disproved it. This is the ninth-plus instance
of the shape the previous slice measured: **a replacement for an overclaim reaching past what it
can support.** The bullet now states the three rules, states that a construct outside them is
not modelled, gives the direction its *known* mistakes fall in with an example, and says
explicitly that this is not a guarantee about all of them — naming the earlier claim as the
defect it was.

**Fixed** by replacing parity with a fence scanner: `_fence_marker` reads a marker's character,
run length and info string, honours the three-space indent limit, and rejects a backtick opener
whose info string contains a backtick; the scan tracks the open marker and closes only on the
same character, at least as long, with no info string. Content inside a fence is literal and
does not reach the raw-HTML scan.

### Standards 2. Major — "the claimed CommonMark types 1 to 5 coverage omits type 4" — FIXED

Verified: `<!DOCTYPE html`, unclosed, returned `reason=None`. Type 4 is a declaration — `<!`
then a letter, closed by `>` — and it was missing while the source comment,
`docs/known-limitations.md` and `round-04.md` all claimed types 1 to 5. The claim was checkable
and wrong. `_next_header_opener` now matches it, and the pair table's comment says why type 4
is matched there rather than in the table.

**`round-04.md` is immutable under rule 9, so this entry is the correction:** where round-04.md
says the list is "CommonMark's HTML block types 1 to 5", that was false when written — type 4
was absent. It is true as of this round's fix.

### Spec 2. Major — "HTML blocks can still cross the ledger" — FIXED

`<div hidden>` on the header's last line, with the first committed entry immediately below and
`</div>` after it, was accepted. Types 6 and 7 end at a **blank line**, not at a closer, so a
pair table cannot see them. The header's last non-blank block may now not begin with a raw-HTML
line — `<` or `</` then an ASCII letter, which is what both types require. A `<!` or `<?` start
is one of the paired types and is left to the scan, which is what keeps a closed
`<!-- comment -->` on the last header line legal.

The same finding named `<presentation>` as falsely refused because `<pre` had no tag-boundary
check. The boundary check is in — `_next_header_opener` requires a space, tab, newline, `>` or
`/` after a tag opener — so `<pre` no longer matches inside the word. **The refusal remains, for
the other reason**: a trailing line beginning with a tag is refused by the types 6 and 7 rule
above, and `docs/known-limitations.md` now names that case and its one-blank-line remedy. Said
plainly rather than reported as fully repaired.

### Spec 3 / Standards 3. Major and Low — "stripping inline code can fabricate a closer" — FIXED

The sharpest finding of the round. `_strip_inline_code` deleted a matched span, so a header
holding `<script>` and then ``</scr`x`ipt>`` had a closing tag **synthesised out of text that
never contained one** — and Markdown does not process inline code inside a raw script block, so
the real state was an open block. Verified accepted. A span now becomes a **space**, which
cannot join the text on either side.

The same finding's Low half: a run of N backticks was closed by any run containing N. CommonMark
closes it with a run of exactly N. `_find_backtick_run` now matches exact length, so
``a `b `` c`` is left alone rather than over-stripped.

### Standards 4. Low — "the durable mutation count is wrong" — FIXED, and it corrects
`round-04.md`

The reviewer reproduced the mutation `round-04.md` labels "Raw-HTML pair list reduced to the
comment" and got 7 failures where the table records 1. **It is right, and the defect is the
label, not the number.** The mutation actually run commented out the CDATA pair alone; the row
described a larger mutation than the one measured. Re-run here both ways: the pair list reduced
to the comment pair alone gives **7 failures**; removing the CDATA pair alone gives 1.

**`round-04.md` is immutable, so this entry is the correction:** its mutation table's
"Raw-HTML pair list reduced to the comment | 1 failure" row is mislabelled. Read it as *"CDATA
pair removed | 1 failure"*. The README's copy of that row is corrected in place, the README
being the mutable half of the record.

The lesson is the previous slice's, in a place it had not been applied: a mutation table is a
claim about what was measured, and a row that names a bigger mutation than the one run is an
overclaim exactly like a bad count. Every row in this round's table names the edit literally.

## The reviewer's non-findings, kept because they are coverage

It checked and cleared: the comment-overlap cases (`<!-->`, `<!--->`, `<!---->`, `<!----`, and a
normal comment); same-line closers; that `pos` advances monotonically through the scan and
cannot loop or skip; that `governance/changelog.md`'s engine-pin paragraph is accurate in
context; and it found no revisionless source-line citation. It found no scope creep. It stated
its line references were all for `4452679`, which is the convention this record asks for.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`. Each row names the edit
literally.

| Mutation | Result |
|---|---|
| Fence closer no longer required to match the opener's character | 1 failure |
| Fence closer no longer required to be as long as the opener | 1 failure |
| Fence closer allowed to carry an info string | 1 failure |
| Fence indent limit raised from three spaces to 99 | 2 failures |
| Type-4 declaration match disabled | 1 failure |
| Trailing raw-HTML rule replaced by `return False` | 1 failure |
| Tag-boundary check replaced by `if True` | 1 failure |
| Code span deleted rather than replaced by a space | 1 failure |
| Backtick run matched by length >= N rather than == N | 1 failure |
| None (restored) | OK, 883 |

## Environment

The reviewer reported 876 tests discovered with 682 `TemporaryDirectory` setup errors from a
sandbox with no writable temporary directory, and correctly called it environmental. Verified
outside the sandbox on `4452679`: `OK, 876 tests, skipped=1`. After this round's tests the suite
is `OK, 883, skipped=1`.
