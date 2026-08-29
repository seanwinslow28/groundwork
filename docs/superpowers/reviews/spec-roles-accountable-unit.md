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

## Round 8 — 2026-08-28, task-mtdsun1l-1be6dd, verdict: does not approve (1 finding)

Reviewed: commit `86206b3` (spec after round-7 fixes, plus this log). The spec itself
drew no findings; the one finding is this log's own bookkeeping.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | low | Round-6 row 3's "Fixed at all three sites" was falsified by round-7 finding 3, but round 7's amendment inventory never named round-6 row 3 | CONFIRMED | Recorded here: round-7 row 3 amends round-6 row 3 — the round-6 fix reached the validator section and the two prose sites but not decision 5 |

## Round 9 — 2026-08-28, task-mtdt4fx6-852oq0, verdict: does not approve (2 findings, both minor)

Reviewed: commit `de27a5e` (spec after round-8 fix, plus this log). Both findings
accepted; fixed in the following commit. (Launch note: this round's job registered
under the worktree's cwd-keyed state root; a status poll from the main repo returned
"No job found", causing one duplicate launch, cancelled unrun. The lesson is
recorded in session memory, not here — it is apparatus, not spec.)

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | low | Round 3's amendment inventory omits round-2 row 2, which round-3 row 3 explicitly amends | CONFIRMED | Recorded here (append-and-supersede): round 3's inventory also includes round-2 row 2 |
| 2 | low | "All three take their shape from the holding semantics" — the review-record rule does not; it shares only the session | CONFIRMED | Fixed: the sentence now separates the two holes (shaped by the semantics) from the review rule (settled alongside, on its own evidence) |

## Round 10 — 2026-08-28, task-mtdtdsz6-ynnx9t, verdict: does not approve (4 findings, 1 major)

Reviewed: commit `8d68396` (spec after round-9 fixes, plus this log). All 4 findings
accepted; fixed in the following commit. The major is a real sequencing defect in the
landing order. Rows amended: round-4 row 1 (again — the v1-pin story), round-1 rows
11 and 16, round-7 row 2.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Between R1 (v2 engine) and R2 (generate.md rewrite), the documented generation workflow produces a failing repo either way — `schema_version: 1` hits the migration boundary; `2` without a roster fails the roster check | CONFIRMED | Fixed: R1 carries the minimal generate.md edits (pin v2 + roster generated from confirmed owner answers); R2 keeps the contract amendment, prose rewrite, and full roster elicitation |
| 2 | minor | "No draft state to ship into" is false for skills — `provisioned: no` is the work-package convention's own drafting state, and generate.md ships such skills | CONFIRMED | Fixed: deep records and memory records keep the no-draft claim; skills named as already having one. Amends round-1 row 11 |
| 3 | minor | "Its disputed action class" bound the dispute to the quad-check; it belongs to the intake gate | CONFIRMED | Fixed: "the intake gate's disputed action class" |
| 4 | bookkeeping | Round-6 row 4's `_answered()` correction amended round-1 row 16, but no amendment pointer said so | CONFIRMED | Recorded here: round-6 row 4 amends round-1 row 16 |

Also corrected in the same commit, prompted by finding 1's evidence: the v1-pin story
at decision 3 and the schema-bump bullet. The earlier "WARN under a v1 pin" phrasing
implied a green gate; in fact skew ≥ 1 fires the single migration-boundary ERROR, and
the `since: 2` demotions are the finger-pointing behind that red gate (the pull
promise's one-clean-error form). This supersedes the tier wording in round-4 row 1
and round-7 row 2 a second time.

## Round 11 — 2026-08-29, task-mtdul84p-fvdaa7, verdict: does not approve (5 findings, 3 high)

Reviewed: commit `539dea5` (spec after round-10 fixes, plus this log). All 5 findings
accepted; fixed in the following commit. The highs show round 10's sequencing fix was
infeasible as written, incomplete, and in contradiction with the spine. Rows amended:
round-10 rows 1 and 2.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | R1's roster typing "from the human-only markers" is infeasible — the marker denotes answer source, not holder humanity, and covers one owner row of five | CONFIRMED | Fixed: R1 types every holder `human`, which is transcription under the still-binding person-owner protocol; agent holders arrive with R2's elicitation. Amends round-10 row 1 |
| 2 | high | R1 omitted migrating `demo/groundwork.pin` — the R1 engine's own gate would go red on demo at the migration boundary | CONFIRMED | Fixed: the demo pin migration joins R1's enumeration |
| 3 | high | Decision 6 permitted shipping a declared draft with an unresolvable field while decisions 2–3 ERROR a high-risk draft with an unresolvable appeal owner — ship-and-fail | CONFIRMED | Fixed: decision 6 gains the safety-spine exception — high-risk appeal gaps do not ship, declared or not |
| 4 | med | `generate.md` itself both denies and affirms that `provisioned: no` skills ship — the spec repeated the affirmation as if uncontested | CONFIRMED | Fixed: the spec states the self-contradiction and assigns its reconciliation to R2. Amends round-10 row 2 |
| 5 | low | The three per-check bullets still said "(WARN under a v1 pin)" after round 10's recast — accurate in context, but the log overstated removal | CONFIRMED | Fixed: all three bullets now name the demotion as finger-pointing behind the boundary ERROR |

## Round 12 — 2026-08-29, task-mtduyhoh-2d710c, verdict: does not approve (3 findings, all high)

Reviewed: commit `d39c8d6` (spec after round-11 fixes, plus this log). All 3 findings
accepted; fixed in the following commit. All three strike round 11's fixes — the
third consecutive round in which the freshest fixes carry the defects. Rows amended:
round-11 rows 1 and 3.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | "Every holder human is transcription" is false — the protocol guarantees personhood only for acted-on activity and skill owners; constitution owners may be roles or disclaimers | CONFIRMED | Fixed: `human` typing only for the protocol's human-only owner rows; every other owner value enters as an unheld Role row, and an unresolved rule ships rungless as a declared draft. Amends round-11 row 1 |
| 2 | high | The engine-root roster needs holders for `Head of IT`/`CISO` that no file names — the implementing agent would have to invent them | CONFIRMED | Fixed: the engine-root roster is maintainer-authored content, an explicit maintainer input to the R1 plan |
| 3 | high | The spine exception covered "missing or unresolvable" appeal gaps but not resolves-to-agent-only — a shippable artifact the gate rejects | CONFIRMED | Fixed: the exception names all three spine-ERROR forms — missing, unresolvable, resolving to no human holder. Amends round-11 row 3 |

## Round 13 — 2026-08-29, task-mtdvajvt-ux28zi, verdict: does not approve (1 high, 2 plausible)

Reviewed: commit `eb71da1` (spec after round-12 fixes, plus this log). All 3 accepted
(the two PLAUSIBLE-only were accepted as real encoding gaps); fixed in the following
commit. Rows amended: round-12 rows 1 and 3.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | R1's "ships rungless as a declared draft" was unconditional — reintroducing ship-and-fail for the high-risk appeal gaps decision 6 excludes | CONFIRMED | Fixed: the R1 rule is now subject to decision 6's safety-spine exception, restated inline. Amends round-12 rows 1 and 3 |
| 2 | med | The same string arriving from a human-only row (Holder) and a constitution owner row (Role) would trip the roster-integrity ERROR — no dedup rule existed | PLAUSIBLE-only | Accepted: one entry per distinct string; the Holder classification wins (more information) |
| 3 | med | The human-only rows yield a person's name, not a role — nothing said what fills the Role cell without invention | PLAUSIBLE-only | Accepted: person-confirmed owners enter as holder-only rows (Role cell empty), the Role column filled by R2's elicitation |

## Round 14 — 2026-08-29, task-mtdvnkol-w61gcx, verdict: does not approve (4 findings)

Reviewed: commit `0df8977` (spec after round-13 fixes, plus this log). All 4 accepted
(three PLAUSIBLE-only, accepted as real); fixed in the following commit. Rows
amended: round-12 row 1, round-13 rows 2 and 3.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | med | Generating an "unheld Role row" for a disclaimer invents a role the record never confirmed | CONFIRMED | Fixed: unconfirmed owner values are not entered at all — absence fails resolution identically, with no false roster content. Amends round-12 row 1 |
| 2 | med | Holder-wins dedup suppressed the very collision the integrity rule ERRORs, invisibly | PLAUSIBLE-only | Resolved by row 1's fix: generation writes no Role rows, so there is nothing to suppress; the residual person-name coincidence is the documented intent-blind blind spot. Amends round-13 row 2 (the dedup rule is withdrawn) |
| 3 | high | A dispute whose accounts include high-risk could carry the lower class in the scalar and ship past the spine exception — S4 entering the contract | PLAUSIBLE-only | Fixed: the exception binds by the stricter reading of a recorded dispute; S4's full tie-break stays its own queued slice |
| 4 | med | "The Role column fills with R2's elicitation" implied R2 reaches existing rosters — engine pulls never re-copy content | PLAUSIBLE-only | Fixed: R2 fills rosters for repos generated after it; R1-window repos keep valid holder-only rosters, enriched only by their own edits. Amends round-13 row 3 |

## Round 15 — 2026-08-29, task-mtdw0l7k-4rwydx, verdict: does not approve (5 findings, 2 high)

Reviewed: commit `faf8059` (spec after round-14 fixes, plus this log). All 5 accepted;
fixed in the following commit. Rows amended: round-12 row 1 (again), round-14 row 1.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | Typing the backup owner human invents its type — its human-only marker denotes answer source, and a role-shaped backup is legal | CONFIRMED | Fixed: human typing restricted to the acted-on activity owner and skill owner (the "A role is not an owner" answers); the backup owner is not entered. Amends round-12 row 1 |
| 2 | high | Decision 6's exception missed the rung-independent orphan prohibition — a repeal without its surviving job reassigned ERRORs and cannot ship | CONFIRMED | Fixed: the exception generalizes to every rung-independent gate ERROR, orphan prohibition named |
| 3 | med | "Fails resolution by absence" is unconditional — a string coinciding with an entered holder resolves as that person | CONFIRMED | Fixed: the coincidence carve-out stated inline, tied to the documented blind spot. Amends round-14 row 1 |
| 4 | med | R1's draft path invoked decision 6's permission while the landing order put that amendment in R2 | PLAUSIBLE-only | Fixed: the narrow declared-draft permission lands in R1's minimal edits; R2 carries the rest of the amendment |
| 5 | med | The rewrite contract's target sentence ("an owner is a role, and the roster says who holds it") excluded person owners and holder-only rows | CONFIRMED | Fixed: "a role or a named holder, and the roster resolves it" — the additive form decision 1 requires |

## Round 16 — 2026-08-29, task-mtdwdo7s-gc0i8d, verdict: does not approve (6 findings, 2 high)

Reviewed: commit `cfa80b2` (spec after round-15 fixes, plus this log). All 6 accepted;
fixed in the following commit. Rows amended: round-15 rows 2, 3, 4, and 5; round-10
row 1 (per row 6 below).

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | R1's inline exception narrowed back to appeal gaps, dropping the orphan prohibition decision 6 had just gained | CONFIRMED | Fixed: R1's paragraph states the full rung-independent exception. Amends round-15 row 2's completeness |
| 2 | high | The R1/R2 split landed the declared-draft permission without its paired report obligation — removing decision 6's stated pressure | CONFIRMED | Fixed: permission, exceptions, and the constitution-rule report obligation land together in R1; R2 keeps the provisioned-no reconciliation and wider wording. Amends round-15 row 4 and round-10 row 1 |
| 3 | med | "Ships rungless with its unresolved owners named" was unconditional — coincidence can resolve every owner, leaving no gap | CONFIRMED | Fixed: the draft path is conditioned on at least one unresolved owner; all-resolved proceeds ordinarily. Amends round-15 row 3 |
| 4 | med | The rewrite preamble still said "the person holding one," excluding legal holder-only rows | CONFIRMED | Fixed: "a role or a named holder", with the holder-only case stated. Amends round-15 row 5 |
| 5 | med | The generated roster's `review_by` had no source — no question elicits it, and R1 must not invent | CONFIRMED | Fixed: C10's derivation pattern — a stated 90-day interim default, recorded as derived-not-answered, elicited from R2 on |
| 6 | low | Round-15 row 4's amendment inventory omitted round-10 row 1, whose "R2 keeps the contract amendment" it changed | CONFIRMED | Recorded here: round-15 row 4 also amends round-10 row 1 |

## Round 17 — 2026-08-29, task-mtdwsf0g-yk7ejh, verdict: does not approve (5 findings, 1 high)

Reviewed: commit `7ccfa2c` (spec after round-16 fixes, plus this log). All 5 accepted
(one PLAUSIBLE-only accepted as an unstated divergence); fixed in the following
commit. Rows amended: round-16 rows 3 and 5.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | high | The roster decides activation and appeal resolution but its mutation was ungoverned — an edit could redirect an active rule's appeal without a proposal | CONFIRMED | Fixed: a roles.md change in a governed root is an escalating change under the #18 gate, `--diff` mode, `since: 2` — a design addition flagged for the maintainer |
| 2 | med | R1's draft condition tested only unresolved owners — an all-resolved rule with a recorded dispute bypassed decision 6 | CONFIRMED | Fixed: the condition tests all three decision-6 gap classes. Amends round-16 row 3 |
| 3 | med | The 90-day default was miscited as "the C10 pattern" — C10 derived from an elicited cadence; this has none | CONFIRMED | Fixed: named a policy default, default-not-answered, C10's weaker cousin. Amends round-16 row 5 |
| 4 | med | The roster's `valid_at` (generation date) silently diverged from org-memory's became-true semantics | PLAUSIBLE-only | Fixed: snapshot semantics (when the mapping was last confirmed) stated deliberately, in the spec and the file |
| 5 | low | The sketch example's review_by was 92 days from valid_at, not the mandated 90 | CONFIRMED | Fixed: 2026-11-26 |
