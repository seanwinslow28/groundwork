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

## Round 2 — 2026-08-28, task-mtdqqmhp-0wvkcp, verdict: does not approve (7 findings)

Reviewed: commit `1626d6c` (spec after round-1 fixes, plus this log). All 7 findings
accepted; fixed in the following commit. Two highs show round-1 fixes that were
incomplete — the partial-fix failure mode this branch's kickoff predicted. Round-1
rows 1, 2, 7, 9, and 13 are **amended** by rows 1–5 below (append-and-supersede;
round 1's table stays as written).

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | The S3-supersession fix kept "live practice" — the correction leaves company practice unestablished; S3's basis is the confirmed record | CONFIRMED | Fixed at all three sites: "a practice its confirmed record carries at hard-block with an owner nobody claims", liveness explicitly unestablished. Amends round-1 row 1 |
| 2 | high | Appeal-human checked only at activation lets a high-risk draft with an agent-resolving appeal owner stay green — the spine forbids that verbatim | CONFIRMED | Fixed: agent-only resolution ERRORs on high-risk drafts too (affirmatively wrong, not incomplete); unresolved-on-draft stays decision 5's WARN. Decision 3 and the validator bullet both updated. Amends round-1 row 2 |
| 3 | med | Two-way resolution is ambiguous when a string is both a Role and a Holder; no precedence or collision rule existed | CONFIRMED | Fixed: roster integrity — Role/Holder namespace collision ERRORs, conflicting holder types ERROR; no precedence rule by design. Amends round-1 row 7 |
| 4 | med | `interview/README.md:149` ("a person, not a role?") is a third explicit contradiction, not person language | CONFIRMED | Fixed: three explicit contradictions, five person-language sites. Amends round-1 row 9 |
| 5 | med | "No round's severity grades survive anywhere" is false — `f5ab4b6` carries "Two HIGH findings, both correct" | CONFIRMED | Fixed: narrowed to "no complete round output exists; what survives is what each commit chose to quote", with the counterexample cited. Amends round-1 row 13 |
| 6 | low | Decision 5 listed `sunset` among owner fields — it is not one, and its WARN already exists today outside the rung branch | CONFIRMED | Fixed: sunset removed from the new-WARN list, existing check noted unchanged |
| 7 | low | `reviews/<branch>.md` with a slashed branch name names a different path than this file's | CONFIRMED | Fixed: convention now states `/` → `-` normalization, which this file already follows |

## Round 3 — 2026-08-28, task-mtdr6fzx-wp48xv, verdict: does not approve (8 findings)

Reviewed: commit `7e24c6a` (spec after round-2 fixes, plus this log). All 8 findings
accepted; fixed in the following commit. Rows 1 and 5 are again incomplete prior
fixes; rows amended: round-2 rows 1 and 4, round-1 rows 5 and 7.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | "Record-confirmed practice" still overclaims — the record is confirmed, the practice is not; the third site's round-2 fix was partial | CONFIRMED | Fixed: the bullet now says "a practice the confirmed record carries as enforced", with the liveness caveat inline. Amends round-2 row 1 |
| 2 | high | Intent-blind resolution: a forgotten role row whose title equals a Holder string silently resolves as that holder; the integrity check cannot see an absent row | CONFIRMED | Fixed as a stated design choice: blind spot documented (roster section + What-this-does-not-do), typed owner references recorded as the known alternative, flagged for maintainer at R1 plan review |
| 3 | med | Decision 3 and this log said the high-risk-draft appeal check "ERRORs" without the v1-pin WARN demotion the validator section carries | CONFIRMED | Fixed: decision 3 names the `since: 2` demotion and its consequence — the spine's verbatim guarantee holds in full from v2. Amends round-2 row 2's wording |
| 4 | med | The validator routed resolvable-but-agent-only appeal owners on non-high-risk drafts to "decision 5's WARN tier", which decision 5 did not define | CONFIRMED | Fixed: decision 5 now defines three named gap classes, wrongly-typed included |
| 5 | med | The rewrite section still said "the two explicit contradictions" after the inventory became three | CONFIRMED | Fixed: three sites named in the rewrite contract. Amends round-2 row 4 (partial fix) |
| 6 | med | Decision 6 claimed run 1 declared every gap — the disclaiming runtime_check_owner was never declared as one, in the rule or the report | CONFIRMED | Fixed: narrowed to "the gaps it recognized as gaps", with the new unresolvable class named as new. Amends round-1 row 5 |
| 7 | med | "Refuse to ship, or invent" contradicts the three outcomes the run record weighs and the design's own declared-draft contract | CONFIRMED | Fixed: the sentence now carries the three weighed outcomes, omission-only compliance, and invention as the temptation |
| 8 | low | Header said "six decisions"; the list has seven | CONFIRMED | Fixed: seven — one carried in from the kickoff, six brainstormed |

## Round 4 — 2026-08-28, task-mtdrllt5-wbp4xs, verdict: does not approve (4 findings)

Reviewed: commit `3c585d7` (spec after round-3 fixes, plus this log). All 4 findings
accepted; fixed in the following commit. The high is again an overbroad prior fix.
Rows amended: round-3 rows 3 and 6.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | "All of these ERRORs are `since: 2`" overreaches — the existing unanswered-appeal ERROR is a v1 check and keeps its tier under any pin; only the new agent-only checks demote | CONFIRMED | Fixed: decision 3 splits the tiers by age — v1 check stays ERROR, new checks `since: 2`. Amends round-3 row 3 |
| 2 | med | Decision 5 named two owner fields where the validator section says "any" — four exist (owner, value_owner, runtime_check_owner, human_appeal_owner) | CONFIRMED | Fixed: decision 5 names all four |
| 3 | med | "Both shipped rules declare their missing rule owner, appeal path, and sunset" misstates both files' actual gaps (quad-check has human_appeal; the intake gate has a rule owner) | CONFIRMED | Fixed: per-rule enumeration matching the files. Amends round-3 row 6 |
| 4 | med | "Caught at activation by failed resolution" stated unconditionally — an erroneous roster row carrying the disclaimer string would resolve it | CONFIRMED | Fixed at both sites: conditional stated; the roster is trusted text |

## Round 5 — 2026-08-28, task-mtdrwfmc-5s5wci, verdict: does not approve (3 findings)

Reviewed: commit `7c4aaeb` (spec after round-4 fixes, plus this log). All 3 findings
accepted; fixed in the following commit. Rows amended: round-1 row 16, round-3 row 6
(second amendment), round-4 row 4.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | med | "Inspects owner fields only on active rules" is overbroad — the high-risk spine inspects appeal fields on drafts; this rule simply is not high-risk | CONFIRMED | Fixed: owner-completeness scoped, the exception named, and why it did not apply (action class `external-side-effect`). Amends round-1 row 16 |
| 2 | med | The intake gate's gap enumeration omits its disputed, unresolved action class, which the file and the report both record | CONFIRMED | Fixed: the dispute joins the enumeration. Amends round-3 row 6 again |
| 3 | med | Decision 6 still said "becomes unresolvable" unconditionally — a third occurrence the round-4 fix missed | CONFIRMED | Fixed: conditional added at the third site. Amends round-4 row 4 |

## Round 6 — 2026-08-28, task-mtds8h5f-2uj0f1, verdict: does not approve (5 findings)

Reviewed: commit `9b98819` (spec after round-5 fixes, plus this log). All 5 findings
accepted; fixed in the following commit. The two highs are design-consistency gaps,
not wording. Rows amended: round-2 row 2 (extended), round-4 row 3, round-5 rows 2
and 3.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | Decision 6's antecedent ("missing required fields") did not cover its own central case — fields populated but unresolvable, or populated but disputed | CONFIRMED | Fixed: the contract names three gap classes (missing / unresolvable / disputed), mirroring decision 5 |
| 2 | high | A high-risk draft with an answered appeal owner resolving to nothing stayed in the WARN tier — green gate, no human reachable, the spine's invariant broken | CONFIRMED | Fixed: on high-risk drafts, resolves-to-nothing ERRORs too (an appeal reaching no human is no appeal path); non-high-risk drafts keep the WARN tier. Decision 3 and the validator bullet both updated. Extends round-2 row 2 |
| 3 | med | "A row with no holder is unheld" contradicted "listing it as a Role resolves it" — a holderless Role row does not resolve | CONFIRMED | Fixed at all three sites: resolution = Holder cell, or Role row with a holder. Amends round-5 row 3 |
| 4 | low | "`_answered()` rejects only placeholders" is overbroad — it also rejects empty values and non-strings | CONFIRMED | Fixed: the full rejection set stated |
| 5 | low | Round-5 row 2's amendment pointer named round-3 row 6 but not round-4 row 3, whose "matching the files" disposition the same omission falsified | CONFIRMED | Recorded here (append-and-supersede; prior rows stay as written): round-5 row 2 also amends round-4 row 3 |

## Round 7 — 2026-08-28, task-mtdsjg9i-ucu826, verdict: does not approve (4 findings)

Reviewed: commit `dfe0b2c` (spec after round-6 fixes, plus this log). All 4 findings
accepted; fixed in the following commit. All four are consistency debts of round 6's
own design changes. Rows amended: round-6 rows 1 and 2; round-4 row 1 (superseded by
round-6 row 2, recorded here per row 4 below).

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | Decision 6's classes claimed to "mirror" decision 5's — they differ (disputed vs wrongly-typed; required vs owner fields), and no validator check reads disputes | CONFIRMED | Fixed: the mirror claim dropped; the contract's classes stated as deliberately wider, with the disputed class binding contract and declaration only. Amends round-6 row 1 |
| 2 | high | The new resolves-to-nothing ERROR's pin tier was unstated in decision 3 and conflicts with decision 2's unqualified invariant under a v1 pin | CONFIRMED | Fixed: both resolution-based ERRORs are `since: 2` — necessarily, since a v1 repo has no roster to resolve against; the verbatim invariant is the v1 check's, said at both decision 2 and decision 3. Amends round-6 row 2 |
| 3 | med | Decision 5's "no roster match" omitted the holderless-Role-row case, which matches but does not resolve | CONFIRMED | Fixed: "does not resolve (no match, or a match on a Role row with no holder)" |
| 4 | low | Round 6's amendment list omitted round-4 row 1, whose age-tier disposition the resolves-to-nothing check superseded | CONFIRMED | Recorded here: round-6 row 2 also amends round-4 row 1 |
