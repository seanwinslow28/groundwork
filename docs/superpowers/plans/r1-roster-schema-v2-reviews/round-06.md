# Round 6 — Codex

**Reviewed revision:** `01414ed` (branch `feat/roster-schema-v2`, twenty commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 4 findings — 2 BLOCKER, 2 LOW.

Codex verified the three validator outputs and `git diff --check`, and reported no
environmental TemporaryDirectory noise. It states explicitly that it found **no novel
pin/demotion defect** — the round-5 fix it was pointed at hardest. The builder ran the full
suite on the reviewed revision: OK, 802 tests, skipped=1.

## Findings

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | BLOCKER | Character references pass `_is_plain_text`. The row `\| CISO \| &#32; \| human \|` produced zero findings and resolved `CISO` to `[('&#32;', 'human')]`, while Markdown renders the Holder cell **blank**. An active or high-risk rule could satisfy the human-appeal requirement through a holder the reader cannot see, against decisions 2 and 3 | CONFIRMED | **Fixed.** A character reference — decimal, hex, or named — is refused anywhere in the body. A bare `&` is still fine, and a test pins that the rule is precise rather than a ban on ampersands |
| 2 | BLOCKER | The forbidden-construct scan recognised fenced code but not **multiline inline code spans**: a single-backtick span opened before a canonical table and closed after it produced zero findings and resolved `CISO → Ghost (human)`, although Markdown renders the whole block as code. The repository's own `_strip_code` removes that span, confirming the parser was consuming content a reader does not see | CONFIRMED | **Fixed.** No backtick anywhere in the body. That subsumes backtick fences as well as spans |
| 3 | LOW | Round 5's fence normalisation disagreed with the documented "no code fence anywhere" rule **in both directions**: it stripped all leading whitespace, so four-space indented code containing literal triple backticks was falsely rejected; and a genuine list-contained opener such as `- ```` passed because the list marker remained | CONFIRMED | **Fixed by removing the mechanism.** Position no longer matters because nothing looks at position — see below. Both halves close at once, and the documentation now states the flat rules exactly, in both directions |
| 4 | LOW | `round-05.md` calls round 5 "the third consecutive round" to find a false review-record claim, while lines 30–31 of the same entry correctly enumerate rounds 2, 3, 4 and 5 — four. The rule-9 record is internally contradictory | CONFIRMED | **Corrected here**, since `round-05.md` is immutable. Verified against the entries themselves: r2 found the README's severity tally wrong, r3 found round-02.md's axis split, r4 found round-03.md's "strictly stronger" claim, r5 found round-04.md's two narrative summaries. That is **four** consecutive rounds, and round 6 makes five |

## The fix is a deletion

Findings 1, 2 and 3 all closed with the same change, and it removed code rather than adding
it. `_ROSTER_FORBIDDEN` is now one flat table of line patterns — no backtick, no run of
three or more tildes, no angle-bracket construct, no `]:`, no character reference — each
matched against the **raw line with no container semantics at all**. The blockquote-marker
stripping and the fence-length arithmetic are gone.

Six rounds argued for this shape. Every attempt to decide what *renders* was wrong in at
least one direction, because deciding what renders is CommonMark emulation and CommonMark
is large: r1 scanned every canonical line; r2 bounded the table but not fenced-only tables;
r3 mis-measured fence length and could synthesise a row; r4 missed three HTML-block
openers; r5 missed link reference definitions; r6 missed code spans and character
references. The failure was never the individual rule — it was that each rule had to model
rendering.

Flat patterns cannot be subtly wrong about position, nesting, or length. They are wrong in
one direction only, and that direction is documented: a roster may not carry constructs a
prose author might reasonably want, and `governance/README.md` now says so plainly and says
what to write instead. The two shipped rosters were reworded to obey the rule they define,
and a test asserts both parse clean — a grammar the reference implementation violates is
not a grammar.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1–5, went unchallenged
  again.
- Findings by round: 11, 7, 6, 4, 5, 4. Every round from 2 on found its worst defect in the
  previous round's fix; the parser has now been rewritten three times and simplified twice.
- Five consecutive rounds have found a factual defect inside these entries. Every one was a
  sentence summarising the work rather than a claim about the code.
