# Round 1 — Codex

**Reviewed revision:** `199b5bc` (branch `feat/roster-schema-v2`, nine commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 11 findings — 4 on the standards axis (worst HIGH),
7 on the spec axis (worst BLOCKER).

Codex marked each finding CONFIRMED (verified against the source) or PLAUSIBLE (reasoned,
unverified); its own severity words are kept verbatim below. Every finding was verified by
the builder against the source before being acted on.

**Builder's verification of the suite.** Codex's sandbox could not run the tests; it ran the
validator only. The builder ran `python3 -m unittest discover -s tests -q` on the reviewed
revision: OK, 776 tests, skipped=1. No environmental TemporaryDirectory noise was reported
by Codex this round.

## Spec axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| S1 | BLOCKER | `scripts/validate.py` — appeal resolution ran only when `roster is not None`, so a high-risk **draft** with answered appeal fields and no roster exited green on two WARNs. Locked decision 3 requires an answered appeal owner resolving to nothing to ERROR there. The test missed it because it excluded only ERRORs whose path contains `roles.md`; the required ERROR points at the rule | CONFIRMED | **Fixed.** The guard is gone: `_resolve_owner` already accepts `roster=None`, so no roster resolves to nobody, which is exactly decision 3's case. New test `test_high_risk_draft_with_no_roster_at_all_still_errors` |
| S3 | BLOCKER | `_parse_roster` scanned every canonical-looking three-cell line in the raw file, so a row inside a fenced block or an HTML comment became a live holder — enough to satisfy held-to-activate and to make a high-risk appeal appear to reach a human — while a visible row missing its trailing `|` was silently ignored | CONFIRMED | **Fixed.** The parser now reads **one bounded table**, mirroring `parse_exec_table`'s doctrine: scan starts after the frontmatter, the block is the contiguous pipe-bearing run, a `\|` outside it ERRORs, the header and delimiter rows are required, and a non-canonical row inside the block ERRORs. Five new tests, including both halves of this finding |
| S2 | HIGH | The same `roster is not None` guard suppressed decision 5's field-specific WARNs when an ordinary draft had populated owners and no roster; only the aggregate missing-roster WARN fired. Decision 5 requires one named WARN per gap, so four unresolved fields cannot collapse into one | CONFIRMED | **Fixed.** The draft-visibility loop no longer guards on a roster existing. New test `test_plain_draft_with_no_roster_names_each_gap` asserts a named WARN for each of the four owner fields |
| S4 | HIGH | Frontmatter-parser findings were appended unchanged, retaining `since=None`, so a duplicate `valid_at` ERRORed undemoted under a v1 pin — contradicting the function's own "every finding here carries since=2" | CONFIRMED | **Fixed.** Both `_parse_roster`'s reader findings and `_load_roster`'s `_read_utf8` findings are re-tagged `since=2`. New test `test_a_malformed_frontmatter_finding_also_carries_since_two` |
| S5 | HIGH | On a case-insensitive filesystem, a v1 root that already holds `governance/roles.md` could bump its pin while respelling the file `Governance/Roles.md`: the base spelling reads as a deletion WARN and the new one as a bootstrap-exempt addition, laundering a modification through decision 8's addition-only exemption | PLAUSIBLE (traced, not executed) | **Fixed.** `_bootstrap_roots` now refuses any root whose **base** already held a roster under any NFC+casefold spelling. `_fold` was moved above its new first use. New test `test_a_case_rename_at_the_boundary_is_not_a_bootstrap`, verified non-vacuous: it fails with the guard removed and passes with it |
| S6 | MEDIUM | `MIGRATIONS.md` said draft owner gaps become WARNs and advised dropping `rung`, without the high-risk exception — high-risk drafts still ERROR on absent, unresolved, or agent-only appeal owners. `governance/README.md` omitted decision 5's third WARN class (a plain draft's resolvable-but-agent-only appeal owner) | CONFIRMED | **Fixed.** Both sites now state the exception and the third class. This was migration advice that would not have cleared the gate |
| S7 | MEDIUM | Old two-family routing survived at `CONTEXT.md:121`, `interview/generate.md:87,265,278`, `scripts/validate.py:2947,3788,3963`, `proposals/README.md:69`, and the generated-company fixture at `tests/test_validate.py:6957` | CONFIRMED | **Fixed** at all nine. Each line was re-read before editing rather than trusted from the citation; all nine were where the review said. Three of them are user-visible validator strings, including the deletion WARN a deleted roster now hits |

## Standards axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| N1 | HIGH | `demo/governance/roles.md:3` — `review_by: 2026-11-30` was justified in the plan as matching a recorded demo cadence, but no demo source records an org-map cadence; 90 days after `valid_at: 2026-05-11` is 2026-08-09. The adjacent `source` claim, "The founder's own account, confirmed across layers 01–05", is also unsupported: those layers were confirmed by Priya Raman, Marcus Bell, Ruth Okafor and Dana Whitfield | CONFIRMED | **Fixed.** Verified independently: layers 01–05 carry four distinct `confirmed_by` values. `source` now names layers 01–03 and the three people who confirmed them — the layers these three entries actually transcribe. `review_by` is now the 90-day policy default, `2026-08-09`, recorded in the file as a default rather than an answer. **It has passed, so the demo now carries a third WARN and the engine root an eighth.** That consequence is a maintainer question, recorded in the README |
| N2 | MEDIUM | `demo/governance/roles.md:8` and `demo/governance/README.md:20` say Umbercress "holds no formal offices", but `demo/canon.md` assigns CEO, VP Customer Success, Director of Product, VP Engineering and Head of People. Holder-only rows remain appropriate; the stated justification contradicts the demo's own source of truth | CONFIRMED | **Fixed.** Verified: canon.md assigns five offices. Both sites now give the true reason — the three rules name people rather than offices, so the roster records holders and asserts no roles — and point at the canon file for the offices. Whether the demo should also carry Role rows for those five offices is noted in the README as an open option, not taken: no rule references one, and Role rows are R2's elicitation work |
| N3 | LOW | The plan said the test change adds four classes (the diff adds six), listed `demo/canon.md` as modified though it is absent from the diff, and said that file enumerates demo contents | CONFIRMED | **Fixed.** Verified by diffing the class list against `main`: six classes, named individually in the plan now. `demo/canon.md` was checked during execution and carries no inventory, so it was never touched; the plan now says so and tells a later executor to confirm rather than assume |
| N4 | LOW | `docs/roadmap.md:48` still headed the section "V2 — documented, not built" and said every item is deliberately absent from V1, immediately above two bullets saying the roster and the `since:` mechanism have landed | CONFIRMED | **Fixed.** The heading and preamble now say the first two have landed and everything below them is still documented-not-built |

## What Codex explicitly cleared

- Both `PIN_OK` definitions are v2 and their `.replace()` call sites target the v2 text — no
  silent no-op was introduced by the fixture migration.
- The three validator runs it was permitted matched the reported green results.

## Notes for the next round

- One implementation choice the review did not raise, recorded so it is not silent: when an
  instance has an **active** rule and no roster, the builder emits the single missing-roster
  ERROR and suppresses the four per-field resolution ERRORs. That suppression is the
  builder's, not the design's. It changes no verdict — the gate is red either way — and it
  is deliberately **not** applied to drafts, where decision 5 asks for named gaps and
  nothing is red. Raise it if it reads as invented policy.
- `tests/test_validate.py` defines `PIN_OK` **twice** at module level, the second shadowing
  the first for every test at run time; the first has been dead since it was written. Both
  were set to v2 rather than consolidated, which is out of this slice's scope.
