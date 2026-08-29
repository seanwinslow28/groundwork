# Round 4 — Codex

**Reviewed revision:** `1d45659` (branch `feat/roster-schema-v2`, sixteen commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 4 findings — 1 BLOCKER, 1 MEDIUM, 2 LOW.

Codex honoured the do-not-re-raise list, verified the three validator outputs and
`git diff --check`, and reported no environmental TemporaryDirectory noise. It stated
explicitly that it found **no** additional defect in the forbidden-construct early-return
flow or in `path_since` mixed classification — the two round-3 fixes it was pointed at
hardest. The builder ran the full suite on the reviewed revision: OK, 795 tests, skipped=1.

The BLOCKER is again a defect in the previous round's fix — the fourth round in a row.

## Findings

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | BLOCKER | `_HTML_TAGGISH` matched only `<` followed by a letter or `/`, so it missed the CommonMark HTML-block forms opening `<?`, `<!DOCTYPE…` and `<![CDATA[`. Codex wrapped a canonical roster table in each: zero findings, and the ghost holder resolved as human — hidden content satisfying held-to-activate and human-appeal resolution, against decisions 2 and 3 | CONFIRMED | **Fixed.** `_ANGLE_CONSTRUCT` (`<` followed by a letter, `/`, `!` or `?`) matches every HTML-block opener. New test covers all four shapes Codex named plus `<div hidden>`, asserting both the ERROR and that the ghost resolves to nothing |
| 2 | MEDIUM | The documented roster grammar was never updated for round 3's replacement parser. The implementation rejects fences, HTML markers, autolinks and every pipe outside the table, but neither `governance/README.md` nor `MIGRATIONS.md` disclosed those whole-body restrictions; Codex reproduced failures with documented-shape rosters containing a fenced explanation, `<https://example.com>`, or explanatory pipe text. It also notes an autolink is Markdown, not HTML, so the coarse regex rejects legitimate Markdown | CONFIRMED | **Fixed, and the over-catch is kept deliberately.** Both documents now state all three restrictions where the grammar is specified, name the autolink case, and say what to write instead. Refusing autolinks is a choice, not an accident: one rule a reader can check beats a grammar that must decide what renders, and that grammar has been wrong in three consecutive rounds. A test pins both the refusal and its documentation, and a second pins the newly documented pipe rule |
| 3 | LOW | `round-03.md` calls both changed assertions "strictly stronger". Against `fae6858` one kept its resolution checks while weakening a specific-message assertion to bare `any(ERROR)`; the other exchanged specificity for new resolution checks, making it incomparable. An unrelated ERROR could satisfy the loosened half | CONFIRMED | **Both corrected here and repaired in the tests.** `round-03.md` is immutable, so this entry is the correction: the claim was wrong. The ERROR half of every hidden-construct test now names its construct — "fence" or "angle-bracket" — so it is specific without pinning one wording, which is what broke on each of the three mechanism changes. That is genuinely stronger than either the original or the round-3 form |
| 4 | LOW | `MIGRATIONS.md`'s "Each check declares the `SCHEMA_VERSION` it was introduced at" is false: `Finding.since` defaults to `None` for pre-versioning findings, and a mixed-age check tags only its new findings. This obscures why untagged checks keep binding every pin | CONFIRMED | **Fixed.** The section now says the tag is per **finding**, that an untagged finding binds every pin and is the default, and gives the worked example: the high-risk appeal spine keeps ERRORing on its original answered-fields condition under any pin while its new resolution-based conditions demote |

## The pattern this round confirms

Four rounds, four sets of BLOCKER-or-worst findings, and every one of them a defect in the
previous round's fix rather than in the original work:

- r1 → the roster parser read every canonical-looking line.
- r2 → r1's bounded table still parsed a table living entirely inside a fence.
- r3 → r2's masker mis-measured fence length **and** could manufacture a row by splicing.
- r4 → r3's forbid-list missed three HTML-block openers, and its documentation missed all
  of the restrictions.

Rounds 3 and 4 both responded by making the rule cruder and more checkable rather than more
clever — first replacing masking with a forbid-list, then widening that list to every
angle-bracket construct and accepting a known over-catch. That direction is deliberate and
is what "the class is unreachable rather than handled" means in practice; the cost is that
a roster may not carry an autolink, which is now documented rather than surprising.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1–3, went unchallenged
  again in round 4. It stands as recorded.
- Drift-site count by round: nine, three, four, zero. Round 4 found no new parallel-site
  drift — the first round in which that inventory came back empty.
- Two of this round's four findings were errors inside the review record itself (r3's
  "strictly stronger" claim) or in documentation of the implementation, not in the
  implementation. That is a shift in where the remaining defects live.
