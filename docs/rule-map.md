# The rule map — what each check enforces, and at what severity

CONTEXT.md says what every resolved decision requires. `scripts/validate.py` implements
it. This table is the join, and it exists because a V1 success criterion claims "every
rule fires where CONTEXT.md says it should" — a claim that was carried for the whole build
with no artifact behind it.

**What the test proves and what it does not.** `TestRuleMap` binds this table to the code
in both directions: every check named here exists in `validate.py`, and every check
`validate.py` ships appears here. So the map cannot fall silently out of date when a check
is added, renamed, or removed. It does **not** prove a severity is *correct* — that is a
judgment against CONTEXT.md, made by hand and recorded in the Severity column. A coverage
test that claimed more than this would be the vacuous-test trap wearing another hat.

**Reading the Severity column.** Several checks are thin per-instance loops that delegate
to a private body, so the severity given is the delegate's. ERROR fails the gate; WARN
prints and does not. Where a rule is strict only once a field backs a running agent, the
column says so — that is the machinery-follows doctrine, not an inconsistency. One
severity is shared rather than per-row: every check that reads a structured file surfaces
an ERROR through the common reader when that file is unreadable or not valid UTF-8, so a
row that says WARN describes the check's own findings, not a promise that nothing under it
can ever ERROR.

| Enforces | Check | Severity |
|---|---|---|
| Secrets floor over walked, non-gitignored content, high-signal and not exhaustive (16) | check_secrets | ERROR |
| Entropy heuristic on long high-entropy runs (16) | check_entropy | WARN |
| Context-budget thresholds over a measured byte count (13) | check_context_budget | WARN near 20K est. tokens, ERROR near 50K |
| Referential integrity of relative inline markdown links (brief section 10) | check_links | ERROR |
| The Codex instruction chain against its silent 32 KiB truncation cap (13) | check_agents_chain | ERROR |
| The always-loaded aggregate: the union across harnesses, deduplicated by real path (13) | check_always_loaded_budget | WARN near 20K est. tokens, ERROR near 50K, via check_context_budget |
| The section 6 root-file set: the CLAUDE.md import, the Cursor and Gemini pointers | check_root_files | ERROR on CLAUDE.md drift, WARN on a missing Cursor or Gemini pointer |
| Machinery-follows fields on one acted-on activity's deep record (5) | check_deep_record | ERROR on the automation path and on invalid values, WARN off it and on incomplete thinking |
| The canonical executive-view grammar and deep-record listing, per instance (5) | check_ontology | ERROR on the grammar, WARN on an unlisted deep record |
| Card spine, track-2 trio, freshness, and the three drift checks, per instance (6) | check_owner_cards | ERROR on drift always and on the spine at provisioning, WARN below provisioning and on freshness |
| Org-memory record shape, provenance, and supersession chains (7) | check_memory | ERROR on the spine and broken supersession, WARN on staleness, a missing source, and an unindexed record |
| Typed rules, the no-rung-six safety invariant, orphan-prohibition, sunset (8) | check_constitution | ERROR on the safety spine, WARN on drafts and missing provenance |
| Resumable interview state: manifest pointer, frozen layers, one working file (9) | check_interview_state | ERROR on shape and on a half-committed turn, WARN on dates, ordering, and a missing source |
| The action-class gate's registration as part of its own enforcement claim (8) | check_hooks | ERROR on a guard that cannot fire, WARN on an incomplete set |
| The version-skew gate and the pull promise (21) | check_version_pin | ERROR on a malformed pin or a skew of one or more, WARN on reverse skew |
| What a pinned company root owes: a root AGENTS.md, a harness-visible skills path (10) | check_company_root | WARN |
| A symlinked content directory the stateless walker cannot enter | check_symlinked_dirs | WARN |
| Immutability between a memory record's base version and its new one (7) | check_memory_diff | ERROR |
| Proposal-file schema and three-bucket routing, per instance (17 and 18) | check_proposals | ERROR on schema and routing, WARN on incompleteness |
| The changelog entry format, per instance (17) | check_changelog | WARN |
| The synthetic-identifier allowlist, scoped to demo content only (16) | check_synthetic_identifiers | ERROR |
| The stateful memory pass under diff, driven by the base file list (7) | memory_diff_findings | ERROR |
| The frozen-layer guard under diff (9) | interview_diff_findings | ERROR |
| The blast-radius tripwire: declared against actual, plus the append-only changelog (18 and 17) | blast_radius_diff_findings | ERROR on a missing or mismatched proposal and on a changelog rewrite or deletion, WARN on a governed deletion or a missing changelog line |

## Corrections the hand audit made

This table was drafted from CONTEXT.md and then verified against every function and its
per-instance delegate. Three rows changed in that pass, and recording them is the point
of the audit:

- **check_changelog** was drafted as "ERROR on a rewrite" — wrong. The stateless check's
  own findings are entry-format WARNs (an unreadable or non-UTF-8 changelog still ERRORs
  through the shared reader, as any structured file does); the append-only rewrite ERROR
  is emitted by `blast_radius_diff_findings` under `--diff`, so it lives on that row.
- **check_interview_state** was drafted as "WARN on an open-question contradiction" —
  wrong direction. A half-committed turn (a working file naming a different question
  than the manifest, or one present without the other) is an ERROR; the WARNs are date
  formats, ordering, and a missing source.
- **check_owner_cards** was drafted as "ERROR at provisioning, WARN below it" — too
  coarse. The three drift checks ERROR regardless of the provisioned flag, and the two
  freshness checks WARN regardless; only the spine and track-2 requirements follow it.

No implemented severity was found to contradict CONTEXT.md; every disagreement found was
between this document's draft and the code, and the document was corrected.

## What is deliberately not in this table

- **The two pure cores behind the diff passes.** `classify_governed_change` and the
  private `_governed_class` decide what a change *is*; the rows above cover what the
  validator *emits*. Adding them would mix a classification with a finding.
- **Helpers and parsers.** `parse_frontmatter`, `parse_exec_table`, `iter_files`,
  `load_gitignore`, and `est_tokens` produce no findings of their own; the checks that
  call them carry the severity.
- **Anything CONTEXT.md requires that nothing enforces.** There is one, and it is
  recorded in [known-limitations.md](known-limitations.md) rather than here: the
  interview's health-metrics answer has no schema field, so it lands in prose and is the
  named first candidate for a v2 schema change.
