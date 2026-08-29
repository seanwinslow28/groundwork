# Round 8 — Codex

**Reviewed revision:** `37e449b` (branch `feat/roster-schema-v2`, twenty-four commits
against `main` at `ddcb7a1`).
**Verdict:** **does not approve.** 6 findings — 2 BLOCKER, 2 MEDIUM, 2 LOW.

Codex reproduced the disclosed validator outputs and `--diff main` exit 0. It reports that
EOF without a trailing newline, CRLF, and ASCII whitespace-only boundaries all behaved
correctly — three of the round-7 edge cases it was asked to probe. The builder ran the full
suite on the reviewed revision: OK, 812 tests, skipped=1.

## Findings

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | BLOCKER | The block boundary treated any `str.strip()` whitespace as blank, but U+00A0 is not a blank line to CommonMark. A holder-only `CISO` row, an NBSP line, then a bare `CISO` gave zero findings and resolved `CISO` as human, while the reader sees the later line continuing the table and creating a Role/Holder collision | CONFIRMED | **Fixed.** Blankness is now spaces and tabs only — CommonMark's own definition — with a carriage return tolerated so a CRLF file's blank lines stay blank. Test covers the NBSP shape |
| 2 | BLOCKER | The round-7 invisible/bidi class omitted U+061C ARABIC LETTER MARK, which as the sole Holder produced no finding and resolved as human. The round-7 failure remained reachable | CONFIRMED | **Fixed, by changing the method rather than the list.** Enumerating ranges is the whack-a-mole that cost six rounds on the table grammar, so the check is now by Unicode **category** — `Cc`, `Cf`, `Cs`, `Co`, `Cn`, `Zl`, `Zp`, and any `Zs` that is not a plain space — which is complete by construction. Tab and CR pass for stated reasons. Test covers U+061C plus eight others, and a companion test asserts a legitimate non-ASCII name is not rejected |
| 3 | MEDIUM | The mandatory blank-line-above check was skipped when the table was the body's first line, so a table immediately after the frontmatter closer parsed cleanly — contradicting the documented grammar and the stated round-7 fix | CONFIRMED | **Fixed by making the code match the documentation**, not the reverse: the rule is unconditional, which is what `governance/README.md` and `MIGRATIONS.md` already said without qualification. A table at the body start now ERRORs and says to add the blank line |
| 4 | MEDIUM | Collision detection and resolution compared raw code-point sequences with no normalization, so NFC `José` did not resolve against NFD `José` — a false activation failure for a legitimate name — and canonically equivalent Role and Holder values evaded the collision ERROR while rendering identically | CONFIRMED | **Fixed.** Role keys, holder keys, and the owner value being resolved all go through NFC in one helper, `_roster_key`. This repository already normalizes committed paths the same way and for the same reason: two spellings that render identically are one name. Test covers both directions — the cross-normalization resolve, and the cross-normalization collision |
| 5 | LOW | `docs/roadmap.md:68` still said the generation contract permits only omitting an incomplete rule. `interview/generate.md` now permits a declared rungless draft subject to the locked exceptions, so the sentence contradicted shipped behaviour | CONFIRMED | **Fixed.** The sentence is now past-tense about what the contract permitted at the time, and states what v2 changed: a declared draft naming its own gaps, subject to the safety-spine exceptions, with the report obligation |
| 6 | LOW | `round-07.md` overstates two fixes: it says the parser requires a blank line above every table while the body-start exception remained, and that the pattern covers the bidi ranges while U+061C was accepted | CONFIRMED | **Corrected here**, since `round-07.md` is immutable. Both claims were true of the intent and false of the code at `df99dc5`. Findings 2 and 3 have now made both true, but the record needed the correction on its own terms: `round-07.md` described a state that did not exist |

## Two notes on method

**Finding 2 changed the method, not the list.** Adding U+061C would have closed the reported
case and left the class open — the seventh time in this review that enumerating what to
refuse was the wrong shape. A category check has no next omission to find. The same move is
what ended the table-grammar rounds at round 6.

**Finding 3 was resolved toward the documentation.** The code had an exception the prose did
not; either could have moved. The prose was the stricter and simpler rule, and a rule a
reader can state without a caveat is worth more than the one line of laxity it costs.

## What this entry claims

Every count and attribution above was recomputed from the entries or the source, not carried
forward from an earlier entry. Round 7's two record errors were both corrections of
overreach; this entry makes no claim about patterns across rounds beyond the two method
notes above, which describe changes visible in this branch's diff.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1–7, went unchallenged
  again.
- Findings by round: 11, 7, 6, 4, 5, 4, 6, 6.
