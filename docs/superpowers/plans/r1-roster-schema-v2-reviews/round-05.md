# Round 5 — Codex

**Reviewed revision:** `e3efe16` (branch `feat/roster-schema-v2`, eighteen commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 5 findings — 2 on the spec axis (worst BLOCKER), 3 on
standards and factual accuracy (worst LOW).

Codex stated it raised only novel findings and re-raised no prior disclosure; that is
correct. It verified the three validator outputs and `git diff --check`, and reported no
environmental TemporaryDirectory noise. The builder ran the full suite on the reviewed
revision: OK, 798 tests, skipped=1.

## Spec axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | BLOCKER | The round-4 forbid-list still let non-rendered content supply the live table: a **link reference definition** produces no document element and its title may span lines, so `[x]: /url "` followed by a whole canonical table and a closing quote parsed with zero findings, recorded `CISO → Ghost (human)`, and resolved. Hidden content satisfying held-to-activate and making a high-risk appeal appear to reach a human, against decisions 2 and 3 | CONFIRMED | **Fixed.** The body now carries no `]:` at all. That is `_LINK_REF_SIG`, the signature `parse_exec_table` already refuses for a neighbouring reason — applied here **without** the exec view's `"|" not in ln` carve-out, because the hiding case is precisely a definition whose title contains pipes. New test reproduces Codex's exact shape and asserts both the ERROR and that the ghost resolves to nothing |
| 2 | MEDIUM | `_pin_version_text` and `_pin_versions` ignore frontmatter parse findings and trust any extracted integer: a duplicate `schema_version`, unsupported syntax, or an unclosed block all produce parser ERRORs while the value still reads as `1`. So fixing a malformed base pin to a valid v2 while adding the roster qualified for the proposal-free bootstrap, which decision 8 limits to a genuine migration boundary. `_pin_versions` contradicted its own docstring | CONFIRMED | **Fixed.** Both fail closed when any parse finding is an ERROR. The docstring's promise is now true rather than aspirational. New test uses a duplicate-key pin and asserts the roster addition is still gated |

## Standards and factual accuracy

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 3 | LOW | Round 4's documented "whole-file" restrictions disagreed with the implementation **in both directions**: the docs said no code fence "anywhere", but a fully blockquoted fence passed because `_fence_match` sees only top-level syntax; and a raw `-->` was rejected, so ordinary prose such as `support --> security` ERRORed although a bare ASCII arrow is neither a comment nor a documented construct. An adopter still could not predict which valid-looking bodies are accepted | CONFIRMED | **Fixed in both directions, one by code and one by deletion.** The fence check now strips a blockquote marker chain before matching, making the documented "anywhere" true rather than softening the claim. The standalone `-->` check is **removed**: a comment must *open* with `<!--`, which `_ANGLE_CONSTRUCT` catches on an earlier line, and the early return guarantees the opener is reached first — so the closer check could only ever fire on prose. Two new tests, one per direction. The link-reference rule from finding 1 was added to both documents at the same time |
| 4 | LOW | `docs/roadmap.md:79` still said a **check** declares its introduction version and its ERROR demotes. Round 4 established the tag is per finding: mixed-age checks tag only their new findings while older ones bind every pin. An undisclosed parallel site *in round 4's own fix*, and a false model that could lead a later implementer to demote pre-v2 safety requirements | CONFIRMED | **Fixed.** The roadmap bullet now says the tag belongs on a finding, and carries the same worked example as `MIGRATIONS.md`: the high-risk appeal spine keeps ERRORing on its original condition under any pin while its new conditions demote. Round 4's fix corrected `MIGRATIONS.md` and never swept for siblings — the recurring drift class, inside a fix for a drift finding |
| 5 | LOW | Two false summaries in `round-04.md`: it says all four rounds' worst findings were defects in the previous round's fix, but round 1 had no previous fix — its parser defect was in the original implementation; and it says two of round 4's findings concerned documentation or the record, when three did (2 and 4 documentation, 3 the record). The README's 28/27/1 arithmetic is otherwise correct | CONFIRMED | **Corrected here**, since `round-04.md` is immutable. Both claims were wrong, and the first contradicted the bullet list printed directly beneath it, which correctly attributes round 1's defect to the original implementation. The true statement is: **rounds 2, 3, 4 and 5 each found their worst defect in the previous round's fix; round 1 found its own in the original work.** This is the third consecutive round to find a false claim in the review record itself |

## The record's own error rate

Rounds 2, 3, 4 and 5 have each found at least one factual defect inside these entries — an
axis split, a severity tally, a "strictly stronger" claim, and now two narrative summaries.
Every one was a claim the builder wrote about its own work rather than a claim about the
code, and every one was checkable against a file in the repository. The pattern is not that
the record is hard to keep; it is that summarising is where the unverified sentence gets
written. Later entries correct earlier ones, as rule 9 requires, and the count is left
visible here rather than smoothed.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1–4, went unchallenged
  again. It stands as recorded.
- Drift-site count by round: nine, three, four, zero, one. Round 5's one was inside round
  4's own fix.
