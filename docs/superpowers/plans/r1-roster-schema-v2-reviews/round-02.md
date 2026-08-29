# Round 2 — Codex

**Reviewed revision:** `4bee0a7` (branch `feat/roster-schema-v2`, twelve commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 7 findings — 5 on the spec axis (worst BLOCKER), 2 on
the standards axis (worst LOW).

Codex was told not to re-raise anything round 1 or the README already discloses, and it
did not. It reported running 66 relevant tests, `git diff --check`, and the three validator
invocations, all matching the disclosed outputs; no environmental TemporaryDirectory noise
this round. The builder ran the full suite on the reviewed revision: OK, 785 tests,
skipped=1.

Every finding was verified against the source before being acted on.

## Spec axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| S1 | BLOCKER | Round 1's bounded parser still accepts a complete canonical table when it is the **only** pipe-bearing block inside a fence or a multiline HTML comment. Round 1's tests only appended a hidden row *after* a real table, so they miss this shape. Codex reproduced both forms: no findings, and `CISO` resolved to a human. Non-rendered example content can therefore satisfy held-to-activate and the human-appeal gate, contradicting decisions 2 and 3 | CONFIRMED | **Fixed.** `_parse_roster` now blanks every line inside a fence or an HTML comment before locating the table — blanking, not removing, so reported line numbers stay the file's own. The out-of-block check still reads the **raw** lines, so a fenced example after a real table is still reported rather than quietly ignored. Two new tests reproduce Codex's exact shapes and assert both that an ERROR fires and that the ghost row resolves to nothing |
| S2 | HIGH | `_bootstrap_roots` only detects roster paths present in the base **file list**. A v1 base whose tracked `governance` is a directory symlink already exposes a roster the file list never names, so replacing that symlink with a real directory during v1→v2 makes a changed roster look like an exempt addition. Codex reproduced it: changed the `CISO` holder, supplied a proposal only for the rule, and got zero diff findings | CONFIRMED | **Fixed.** The bootstrap now refuses any root where the base file list contains the roster path **or any ancestor of it** under NFC+casefold — an ancestor present as a file entry means a symlink. New test `test_an_ancestor_symlink_at_base_is_not_a_bootstrap`, verified non-vacuous against the round-1 code |
| S3 | MEDIUM | Diff-time symlink, unreadable-file and read-failure findings are emitted before the roster class receives `since=2`, so a v1-pinned fixture produced an undemoted ERROR beside the migration-boundary ERROR — violating the demotion tier and the one-clean-boundary-error promise | CONFIRMED | **Fixed.** A `path_since` is computed from the classification before those findings are raised and passed to each. Mixed classification (also a rule or skill under another governed root) stays untagged, since those bind v1. New test `test_a_symlinked_roster_finding_demotes_behind_a_v1_pin`, verified non-vacuous |
| S4 | MEDIUM | Round 1's rewrite newly required at least one data row. A draft-only instance with no confirmed mapping has a legitimate header-and-delimiter-only roster — drafts may carry absent or unheld owners, and generation must invent no entries — so the parser forced either roster omission or fabricated content. The pre-round-1 parser imposed no minimum | CONFIRMED | **Fixed.** Only the delimiter row is required. Two new tests: an empty roster is clean, and an empty roster does **not** rescue an active rule — it resolves nothing, so all four owner fields ERROR by name |
| S5 | MEDIUM | Two closed summaries still describe the consent gate as covering rules and track-2 skills while omitting the roster: `README.md:136` and `demo/governance/changelog.md:4` | CONFIRMED | **Split.** `README.md` **fixed**. A twelfth site the review did not name was found by a fresh sweep and fixed too: `docs/known-limitations.md:62`'s "a deleted rule or skill is a WARN". The changelog half is **rejected with grounds**, below |
| S7 | LOW | `_parse_roster`'s docstring still says rows are read from the full text because frontmatter cannot contain pipes, while the rewrite finds the frontmatter close and scans after it — and a test depends on that. A stale explanation of a security-sensitive boundary | CONFIRMED | **Fixed.** The docstring now describes the frontmatter skip, the fence/comment blanking, and why the out-of-block check reads raw lines |

## Standards axis

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| S6 | LOW | The durable review README records round 1 as `2 BLOCKER, 3 HIGH, 3 MEDIUM, 3 LOW`; `round-01.md` actually carries `2 BLOCKER, 4 HIGH, 3 MEDIUM, 2 LOW`. The rule-9 audit record is factually wrong | CONFIRMED | **Fixed.** Recounted mechanically from `round-01.md`'s own rows rather than from the review's claim: 2 BLOCKER, 4 HIGH, 3 MEDIUM, 2 LOW, total 11. The README row now says that. This is the disposition-table bookkeeping error the session was warned about, and it happened anyway |

## Rejected with grounds

**S5, the `demo/governance/changelog.md` half.** The finding is correct — that file's preamble
lists what escalates and omits the roster. It is **not fixed**, on these grounds: the
governance changelog is an **append-only** artifact under #17, and
`_changelog_append_only` treats every committed line, preamble included, as immutable
prefix. Editing the sentence made `validate.py . --diff main` fail with *"the governance
changelog is append-only — an existing entry was edited, reordered, or removed"*. That was
observed, not predicted: the edit was made, the gate went red, and the edit was reverted.
Correcting this prose would require the gate to permit rewriting a committed changelog line,
which is exactly what #17 forbids.

This exposes a tension neither the design nor #17 anticipated: a governed append-only file
carries explanatory prose that can go stale, and nothing can correct it. That is recorded
in the README as a maintainer item rather than resolved here, because every available fix —
exempting the preamble, rotating the file, or gating the edit through a proposal — changes
what an append-only guarantee means.

## Notes for the next round

- The round-1 note offering the active-rule ERROR suppression for challenge was left
  unchallenged. It stands as recorded: with an active rule and no roster at all, one
  missing-roster ERROR is emitted and the four per-field resolution ERRORs are suppressed;
  drafts are not suppressed. Still the builder's choice, still offered.
- The fresh drift sweep this round found one site the review missed
  (`docs/known-limitations.md:62`) and one the review named that cannot be fixed. Round 1
  found nine, round 2 found three. The inventory has not yet come back empty.
