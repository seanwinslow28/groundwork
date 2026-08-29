# Codex review record — branch `spec/roles-accountable-unit`

> The durable per-round review log this branch's own spec makes a standing rule
> (decision 7), applied prospectively to the branch that proposes it. Plan-less work
> uses this location (`docs/superpowers/reviews/<branch>.md`); slices with a plan use
> `docs/superpowers/plans/<slice>-reviews.md`. Every round is appended here before the
> branch may merge: verdict, each finding with severity and CONFIRMED/PLAUSIBLE
> status, and its disposition.

## Round 1 — 2026-08-28, task-mtdq901q-mnnojt, verdict: does not approve (17 findings)

Reviewed: commit `579cea6` (the spec, first version). All 17 findings accepted; fixed
in the following commit. Dispositions below; "fixed" means the spec text was corrected
and the correction verified against the cited source.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | Held-to-activate preserves the draft encoding S3 asked to remove, yet the spec claimed to be "S3's resolution" | CONFIRMED | Fixed: decision 2 now states it **supersedes** S3's requested outcome — the declared draft is the chosen encoding, its cost accepted; "What this does not do" carries it |
| 2 | high | "Drafts may carry absent owners" would silently downgrade the locked draft-time safety-spine ERRORs (high-risk draft without appeal) | CONFIRMED | Fixed: decision 2 and the validator section carve the safety spine out explicitly — activation adds requirements, removes nothing |
| 3 | high | Engine root is itself a validated instance with an active rule; R1 without an engine-root roster turns groundwork's own gate red | CONFIRMED | Fixed: R1 ships rosters for the engine root and demo, with the reason stated |
| 4 | high | The activation ERROR is a tightening; MIGRATIONS.md makes that mandatorily a v2 change, not a "bump candidate" | CONFIRMED | Fixed: R1 is the v1→v2 bump; new checks carry `since: 2`, v1 pins get the new-requirement demotion (WARN), migration note owed |
| 5 | high | "Run 1's report obligation was not met" is false — generation-report.md names both incomplete rules and every reason | CONFIRMED | Fixed: decision 6 now says run 1 already practiced the contract in substance, with the citation |
| 6 | high | Roles valid "for every owner field" but resolution specified only for constitution rules leaves the unheld-role hole elsewhere | CONFIRMED | Fixed: scope stated as deliberate (constitution only in R1), the remainder a named remaining hole for known-limitations.md |
| 7 | high | Demo active rules use personal names as owners; exact role-string resolution breaks them with no migration planned | CONFIRMED | Fixed: resolution matches Role cells or Holder cells; person-named owners resolve as holders; demo roster rows planned in R1 |
| 8 | med | "RULE_OK asserts that rule is clean" — the fixture is synthetic, never reads the production rule | CONFIRMED | Fixed: reworded to "pins those same role-shaped values"; synthetic-twin status stated |
| 9 | med | "Eight load-bearing places" overstates — several sites are compatible with roles; the one explicit contradiction (questions.md:93) was missing | PLAUSIBLE-only | Accepted anyway: list restructured into two explicit contradictions (questions.md:93, protocol.md:247) plus six person-language sites to review |
| 10 | med | "Name a person, not a queue" maps to gate_exception_path, not an owner row | CONFIRMED | Fixed: the rewrite section now anchors on the actual owner rows (93–98) and drops the misattributed example |
| 11 | med | Hole (b)'s "artifact" over-generalizes — other artifact kinds have their own no-ship rules and no draft state | CONFIRMED | Fixed: decision 6 scoped to constitution rules; other kinds' no-ship rules stand unchanged, stated with their cites |
| 12 | med | "24 rounds" — the merge commit records 16 + 9 = 25, two approving | CONFIRMED | Fixed: 25, sixteen + nine, two approving, cited to df6df21 |
| 13 | med | "Survive only as fix-commit subjects" — commit bodies preserve findings and dispositions; the loss is rounds without commits and all verdict/severity/rejected-finding text | CONFIRMED | Fixed: reworded to exactly that |
| 14 | med | "Dominant failure mode, seven occurrences" and "four unverified-inference errors" are retrospective classifications, not source-backed counts | PLAUSIBLE-only | Accepted anyway: replaced with what sources carry — 18fa805's "seventh instance" of the drift class, rule 8's four factual defects |
| 15 | med | Decision provenance is self-attested by the artifact asserting it | PLAUSIBLE-only | Accepted anyway: header now names the maintainer's merge as the durable approval record, matching the honesty plan's own pattern |
| 16 | med | The disclaiming owner "passed because the check rejects only placeholders" — it passed because a draft's owners are never inspected | CONFIRMED | Fixed: causal chain corrected (draft branch first, `_answered()` counterfactual second) |
| 17 | low | The correction's quotation reproduced with altered quote marks while claimed "exactly" | CONFIRMED | Fixed: quoted verbatim with the source's double quotation marks, "exactly" dropped |

Also verified clean by the round: the validator comments at `scripts/validate.py:1811`
and `:1852` match exactly; the three honesty-plan phrases match verbatim; r3 and r9
are indeed absent from the `fix(build): Codex r…` sequence.
