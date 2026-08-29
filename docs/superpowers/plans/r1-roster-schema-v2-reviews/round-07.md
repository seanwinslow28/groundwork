# Round 7 — Codex

**Reviewed revision:** `b8f94b4` (branch `feat/roster-schema-v2`, twenty-two commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 6 findings — 4 on the spec axis (worst BLOCKER), 2 on
standards and factual accuracy (both LOW).

Codex verified the three validator outputs and `git diff --check`, and reported no
environmental TemporaryDirectory noise. It confirms the README's 37-finding arithmetic and
per-round severity tallies are correct. The builder ran the full suite on the reviewed
revision: OK, 807 tests, skipped=1.

## Spec axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | BLOCKER | The parser ended the table at the last pipe-bearing line, but GFM continues a table across a **pipe-less** line. A holder-only `CISO` row followed by a bare `CISO` line produced zero findings and resolved `CISO` as human, while a reader sees `CISO` in both the Holder and Role columns — bypassing the namespace-collision ERROR and satisfying held-to-activate through an ambiguous endpoint | CONFIRMED | **Fixed**, and reproduced first: the shape gave `findings: []` and `resolve CISO: [('CISO', 'human')]` before the change. The block now runs from the table to the next **blank** line and requires a blank line above it — how Markdown itself delimits a table. A non-canonical line inside the block now fails the whole table **closed** rather than being skipped: a block the parser reads differently from the reader is one neither can trust. A bad *cell* stays localized. Two new tests, one per half of the block rule |
| 2 | BLOCKER | `_is_plain_text` accepts invisible and bidi Unicode controls. U+200B, U+2060, U+FEFF, U+200E and U+202E each produced zero findings as the sole Holder and resolved `CISO` to a human — the same unseen-holder failure round 6 was meant to end | CONFIRMED | **Fixed.** A forbidden-pattern entry covers the C0/C1 controls, soft hyphen, the zero-width and bidi ranges, and the interlinear annotation characters. Test covers all five characters Codex named |
| 3 | HIGH | The bootstrap followed a working-tree `groundwork.pin` **symlink** through `os.path.isfile` and `_read_utf8`. Neither `check_version_pin` nor `_governed_class` covers the pin file, so replacing a v1 pin with a symlink to v2 text while adding a roster granted the proposal-free exemption without an auditable committed v2 pin — beyond decision 8's migration-scoped exemption | CONFIRMED | **Fixed.** `_bootstrap_roots` refuses a root whose pin is or sits behind a symlink, using the existing `_has_symlink_component`. New test |
| 4 | MEDIUM | `~~Ghost~~` passed as a plain-text Holder and resolved through its role, though GFM renders it struck through — the stored identity differs from what readers see, against the plain-text-cell contract | CONFIRMED | **Fixed.** The tilde rule tightens from three-or-more to **two**-or-more, which covers strikethrough as well as the fence it was written for |

## Standards and factual accuracy

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 5 | LOW | `round-06.md` says "every round from 2 on found its worst defect in the previous round's fix", which is false for round 6: round 5's fix added link-reference handling, blockquote-fence normalisation and fail-closed pin parsing, and introduced neither round-6 BLOCKER — character references live in the shared cell helper and multiline code spans were never handled by any round | CONFIRMED | **Corrected here**, since `round-06.md` is immutable. Verified against the entries: round 6's two BLOCKERs were **pre-existing gaps in the original approach**, not regressions from round 5. The accurate statement is narrower — rounds 2, 3, 4 and 5 each found a defect in the immediately preceding fix; round 6 did not |
| 6 | LOW | `round-06.md`'s "every one was a sentence summarising the work rather than a claim about the code" contradicts round 4's finding 3, which corrected a claim about test assertions by inspecting the code, and is overbroad for round 2, whose error was a README table tally rather than a narrative sentence | CONFIRMED | **Corrected here.** Both objections hold. The checked statement is: five entries have carried a factual error — a README tally (r2), an axis split (r3), a claim about two test assertions (r4), two narrative summaries (r5), and one internal contradiction (r6). They are not all of one kind |

## What these two corrections have in common

Findings 5 and 6 are both sentences this record wrote *about itself*, and both were
generalisations one step wider than the evidence under them. Round 5 flagged that pattern,
round 6 restated it, and round 6 then committed it twice in the same paragraph — including
in the sentence naming the pattern.

No claim about the code was wrong this round. The four spec findings are defects Codex found
by probing the implementation, and every one was reproduced before it was fixed.

This entry states only what was checked against a file. Where a count or an attribution
appears above, it was recomputed from the entries rather than carried forward.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1–6, went unchallenged
  again.
- Findings by round: 11, 7, 6, 4, 5, 4, 6.
- Six entries have now carried at least one factual error found by a later round.
