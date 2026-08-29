# Round 3 — Codex

**Reviewed revision:** `fae6858` (branch `feat/roster-schema-v2`, fourteen commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 6 findings — 5 on the spec axis (worst BLOCKER), 1 on
the standards axis (LOW).

Codex honoured the do-not-re-raise list. It verified the engine, demo, and `--diff main`
outputs and ran `git diff --check`; no environmental TemporaryDirectory noise. The builder
ran the full suite on the reviewed revision: OK, 791 tests, skipped=1.

**Both BLOCKERs are defects in round 2's fix, not in the original work.** That is now the
pattern across three rounds: round 2's BLOCKER was a hole in round 1's fix, and round 3's
two are holes in round 2's. The response this round is to stop repairing the mechanism and
replace it — see S1/S2's disposition.

## Spec axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| S1 | BLOCKER | The masker reduced every fence opener to three characters, so ` ``` ` closed a ` ```` ` fence and exposed a canonical table that CommonMark still treats as code. Reproduced for backticks and tildes: `_parse_roster` returned a human ghost holder with zero findings, which can falsely satisfy held-to-activate and human-appeal resolution | CONFIRMED | **Fixed by replacement.** See below |
| S2 | BLOCKER | HTML masking could **manufacture** canonical rows from non-canonical source: prefixing each row with `<!-- template -->` gives lines that neither begin with `|` nor form a table, but splicing the comment out produced a ghost holder with zero findings. A table inside `<div hidden>` was accepted the same way | CONFIRMED | **Fixed by replacement.** See below |
| S3 | MEDIUM | Working-tree `_read_utf8` failures in the diff pass were appended without `path_since`, so an unreadable `governance/roles.md` kept `since=None` and stayed an undemoted ERROR under a v1 pin beside the boundary ERROR. Round 2's regression test exercised only the symlink branch | CONFIRMED | **Fixed.** That branch now re-tags with `path_since`. New test `test_an_unreadable_roster_finding_demotes_behind_a_v1_pin`, verified non-vacuous against the round-2 code. The round-2 entry's claim that the fix covered the pre-classification findings was too broad; this entry is the correction |
| S4 | LOW | `CONTEXT.md:57` and `proposals/README.md:49` introduce the roster as the third routed family but still say a memory graduates only into a proposed "skill/rule change", contradicting the adjacent lifecycle | CONFIRMED | **Fixed.** Both now say "a proposed change to one of the three" |
| S5 | LOW | `docs/known-limitations.md:275` and `docs/rule-map.md:88` still call health metrics the **first candidate for a v2 schema change**, while this branch spends v2 on the roster and the updated roadmap moves health metrics to a later bump | CONFIRMED | **Fixed.** Both now say the first bump was spent on the roster and health metrics is a candidate for a later one. Verified against the roadmap edit made in this branch, so the three sites now agree |

## Standards axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| S6 | LOW | `round-02.md`'s header says five spec and two standards findings; its tables carry six spec and one standards. The total and the severity tally are correct — only the axis split is wrong | CONFIRMED | **Corrected here, not there.** `round-02.md` is immutable under rule 9, so this entry is the correction: round 2's findings are **6 spec (S1–S5, S7) and 1 standards (S6)**, total 7, severities 1 BLOCKER / 1 HIGH / 3 MEDIUM / 2 LOW as recorded. The error came from renumbering Codex's own axis assignment when transcribing its table and not re-checking the header against the result. Second bookkeeping error in three rounds |

## How S1 and S2 were fixed

Not by repairing the masker. Round 1 scanned every canonical-looking line; round 2 bounded
the table and then masked non-rendered lines; each fix moved the hole rather than closing
it, and round 3's two BLOCKERs are both in the masking itself — one in how it recognised a
fence, one in the fact that rewriting a line's content can invent a row that was never in
the file.

`_parse_roster` now **forbids** code fences, HTML comments, and HTML tags anywhere in the
roster body, and reads every remaining line exactly as written. That is `parse_exec_table`'s
stated doctrine applied here: define one exact shape and ERROR on everything else, so the
class — hidden tables, decoy tables, synthesized rows, fence-length arithmetic, HTML block
semantics — is **unreachable rather than handled**. A roster has no legitimate use for any
of the three constructs; the engine's and the demo's rosters use none.

Three new tests reproduce Codex's exact shapes (the longer fence for both backticks and
tildes, the comment-prefixed rows, the `<div hidden>` block), each asserting both that an
ERROR fires and that the ghost row resolves to nothing.

## An assertion that was deliberately changed

Two round-1 tests asserted the ERROR **message** contained "exactly one table". That message
no longer exists. They now assert that an ERROR fires **and** that the ghost row resolves to
nothing — strictly stronger than before, and message-agnostic, because the mechanism behind
this property has now changed three times and a wording assertion broke on each change while
the property never did. Recorded explicitly so it is not mistaken for a weakened assertion.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1 and 2, was not
  challenged again. It stands as recorded.
- Drift-site count by round: nine, three, four. The inventory has still not come back empty.
