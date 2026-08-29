## Round 4 — 2026-08-29, task-mteb9nc8-0nrn68, verdict: does not approve (12 findings)

Reviewed: `bd81918` (the round-3 fixes). All 12 accepted; two fixed in the following
commit, four corrected by supersession here, six answered by rewriting the escalation to
what rule 5 actually requires. Round-2 row 1 and round-3 rows 2, 5 and 7 are **amended**
by rows 10, 1, 11 and 12 below. Prior rounds' tables stay as written.

**Fix commits, recorded now that they exist** (rule 9 asks for "fixed in commit X"; a
round's dispositions are written before their commit): round 1 → `edc3c26`, round 2 →
`1c94a3c`, round 3 → `bd81918`, round 4 → the commit following this table.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The header's "naming the fix commit" note is another unratified policy layer: it locally relaxes the normative "fixed in commit X" into an indirect convention, its universal claim is false for round 1, `bd81918` is unnamed because no round succeeds it, and the worked example uses the same practice with no such note | CONFIRMED | Fixed by deleting the note and satisfying the contract directly: the SHAs are recorded above this table and extended each round. Amends round-3 row 2, whose fix was itself the policy |
| 2 | major | The terminal-record fixed point is still unresolved — rule 3 puts review at session end, rule 9 puts that verdict in the repository before merge, so the record commit is after the reviewed state and unreviewed, and reviewing it makes another. Removing the exemption restored the locked decision's silence but did not make the branch mergeable | CONFIRMED | Escalated properly rather than fixed: open item 3 now carries the decision, three options, a recommendation, and the counter-argument, per rule 5 |
| 3 | major | The four-item escalation does not satisfy standing rule 5, which requires the decision, the options, a recommendation, and an honest counter-argument — the items gave arguments or bare defects, never options plus a recommendation. Removing builder-made policy was right; listing questions is not a complete escalation | CONFIRMED | Fixed: every open item is rewritten to rule 5's shape. This is the round's most important finding — three rounds punished me for deciding, and I over-corrected into deciding nothing, which rule 5 does not ask for either |
| 4 | major | The `/` → `-` mapping remains collision-prone and open item 2 states the defect one-sidedly, with no remedy options, no recommendation, and no defence of the current simple mapping | CONFIRMED | Fixed as an escalation: open item 2 now carries four options, a recommendation, and the argument for keeping the flat mapping |
| 5 | major | Nothing in rule 9 requires the terminal verdict to be approving. "Not just the final approve" presupposes approval and the examples model it, but the operative text permits a fully recorded terminal "does not approve" | PLAUSIBLE | Escalated, not changed: open item 5. My reading is that rule 9 governs the record and rule 3 governs the gate, so the silence is correct — but the presupposition in rule 9's own words makes that a fair thing to state rather than leave inferred |
| 6 | major | "Every review round" is undefined for crashed or aborted invocations. The build record documents four Codex crashes mid-review, and such an invocation has no verdict to record — so the obligation is impossible under one reading and builder-selectable under the other | CONFIRMED | Escalated: open item 6, new. A previously unsurfaced hole in decision 7 itself, not only in rule 9 |
| 7 | major | Durability is under-specified without the never-rewrite clause; open item 1 states both core arguments and the squash nuance but has no recommendation or complete option set | PLAUSIBLE | Fixed as an escalation: open item 1 now carries three options, a recommendation, and the counter |
| 8 | minor | The contract surface is still drift-prone, and open item 4 records only the consolidation side, not the discoverability argument for distributed text | PLAUSIBLE | Fixed as an escalation: open item 4 now carries both sides, options, and a recommendation |
| 9 | minor | Round 3's summary miscounts — rows 1, 2, 5 and 6 claim fixes (four) and rows 3, 4 and 7 are open or recorded (three), not "three fixed, four carried" — and its amendment map is wrong: row 5 amends nothing, row 6 amends round-2 row 4, and the correct map is rows 1–2 → round-2 row 3, row 4 → round-2 row 5, row 6 → round-2 row 4 | CONFIRMED | Corrected here by supersession, round 3's table untouched: **four fixed, three carried**, and the amendment map is as stated in this row |
| 10 | minor | Round 2's row 1 says `1c94a3c` left rule 9 saying "only 'appended per round, on the branch'" — that commit removed the never-rewrite clause and added the terminal exemption in the same breath, and round 3 removed the exemption without expressly amending the row | CONFIRMED | Corrected by supersession: `1c94a3c` removed the clause **and** added the terminal-record sentence; rule 9 reached "appended per round, on the branch" alone only at `bd81918`. Amends round-2 row 1 |
| 11 | minor | "The decision itself is untouched" is literally overbroad — the operative decision text and counter-argument are byte-identical to `main` (the operative block hashes identically), but numbered decision 7 as a whole is not, because its evidence paragraph changed | CONFIRMED | Fixed in the spec: the parenthetical now says the **normative choice** is unchanged and only the evidence paragraph is. Amends round-3 row 5's wording |
| 12 | minor | Round 3's row 7 claims "headers point rather than restate" as an applied mitigation — false. The worked header restates both paths, the timing and the required inventory; this branch's header restates placement and normative scope. Neither still claims "restates none", but both restate | CONFIRMED | Corrected by supersession: no such mitigation has been applied. What the two rounds actually removed was the false *claim* of non-restatement, not the restatement. Whether to reduce the headers to pointers is open item 4. Amends round-3 row 7 |

Verified clean by the round, and reported as such: the terminal sentence is completely
gone from rule 9; `bd81918` delivered each of its four stated changes; round-3 rows 1 and 6
describe their diffs accurately, and rows 3 and 4 record open items without touching
normative text. Decision 7 and rule 9 are substantively identical on the normative
contract — every round, verdict, findings, severities, dispositions, both storage paths,
slash flattening, append on branch before merge — and rule 9's additions are evidentiary,
not normative. The evidence amendment is factually right, correctly attributed, correctly
placed, and forbidden by no rule; rule 7 permits acting on new evidence, and the operative
decision was unchanged. The historical fact-check passed again in full from git and
repository content, including the thirteen numbered fix commits, the 39 unreachable
commits and three unreachable blobs with no r3/r9 artifact, all three honesty-plan
phrases, `18fa805`'s "a seventh instance", the four-of-five defect split, the worked log's
25 sections / 102 rows / 102 dispositions / one approving verdict, and that `a4f2970` adds
only 12 lines on parent `acd729c` and was not reviewed before merge `c7664d4`.
`AGENTS.md` is 162 lines.

**Gate note.** The reviewer's `python3 -m unittest discover -s tests -q` reported 558
errors, every one raised at `tempfile.TemporaryDirectory()` because its sandbox has no
usable temporary directory; it correctly declined to report that as a pass. `scripts/` and
`tests/` are unchanged from `main`. Run in this worktree the suite is `OK (skipped=1)` over
709 tests. The three validator gates matched in both environments: `validate.py .` 0
errors / 7 warnings, `--diff main` exit 0, `demo` 0 errors / 2 warnings.

### Open maintainer items after this round — in rule 5's shape

Rule 5 wants the decision, the options, a recommendation, and the honest
counter-argument. Round 3's version had arguments without options and defects without
remedies. These are rewritten. Nothing here is decided.

**1. Should a later round be forbidden from rewriting an earlier round's table?**
Decision 7 says only "appended per round". Rule 9 said more for two commits and no longer
does.
*Options.* (a) Ratify the clause into rule 9 and decision 7 together, and say whether the
guarantee depends on a history-preserving merge. (b) Ratify the clause alone and leave
merge strategy unmentioned. (c) Leave it silent, as decision 7 has it.
*Recommendation:* (a). A record that may be rewritten is not a durable record, which is
the whole premise of decision 7; and git history only mitigates rewriting while the branch
history survives, so a squash merge would quietly remove the fallback.
*Counter-argument:* it puts a git-strategy constraint into a rules file that has never
constrained git strategy, and both logs have practised append-and-supersede without a rule
telling them to — so the clause may be codifying something that was never at risk.

**2. The `/` → `-` flattening is not injective.**
`docs/a-b`, `docs/a/b` and `docs-a/b` can produce one filename; a reused branch name
conflates records; case-folding and Unicode-normalising filesystems add more. The failure
is silent — two branches' audit histories merge into one file, or a merge hits add/add.
*Options.* (a) Keep the flat mapping and accept the collision. (b) Percent-encode `/`
(`docs%2Freview-record-rule.md`) — injective, mechanical, ugly. (c) Mirror the branch path
under `reviews/`, so `docs/review-record-rule` becomes
`reviews/docs/review-record-rule.md` — injective, mechanical, and it gives up decision 7's
stated "single file directly under `reviews/`". (d) Name the log for the slice rather than
the branch, as `plans/<slice>-reviews.md` already does.
*Recommendation:* (c). It is the only option that is both injective and free of judgment,
and the cost is one property whose purpose — `ls reviews/` as the index — is served nearly
as well by `find reviews/`.
*Counter-argument:* decision 7 chose flat deliberately, nested directories make the index
one level less obvious, and the collision needs two branches whose names differ only in
where a slash falls — which no repository has yet produced.

**3. There is no terminal-record step, so the last verdict lands unreviewed.**
Rule 3 puts review at session end; rule 9 puts that verdict in the repository before merge.
The record commit is therefore after the state that was reviewed. The worked example shows
it: `a4f2970` added round 25 and the closing totals and was never reviewed before merge
`c7664d4` — and its own body reports that its closing arithmetic was initially off by one,
so this is not a theoretical risk.
*Options.* (a) Exempt a final record-only commit, with "record-only" defined so a reader
can check it: the diff touches nothing outside the review-log path. (b) Have the final
round review the branch *including* its pending record, with the verdict committed as part
of the maintainer's merge, so no post-review commit exists. (c) Accept that the terminal
commit is unreviewed and say so in rule 9, rather than leaving it unsaid.
*Recommendation:* (a). It closes the loophole round 3's exemption had — that version left
"no content change" undefined, and a path-scoped definition is checkable from the diff
alone.
*Counter-argument:* it is still an exemption, nothing enforces the path scope, and (b) is
the only option with no exempted commit at all — at the cost of putting record content
into a merge commit, where this repository has never put content.

**4. Should the contract live in one place?**
It is currently in decision 7, rule 9, and both log headers, and four rounds have found
drift between them — the worked header's false attribution, this header's false
non-restatement claim, decision 7's stale evidence.
*Options.* (a) Leave it distributed. (b) Make rule 9 the sole normative text and cut both
headers to a one-line pointer. (c) Move the contract into its own document that rule 9 and
decision 7 both point at.
*Recommendation:* (b). Every drift this branch found was a header restating rule 9 and
getting it wrong; a pointer cannot drift.
*Counter-argument:* a header that only points is less useful to someone reading a log in
isolation — in a PR diff, or years later — and the restatements exist because that reader
is real.

**5. Must the terminal verdict be approving?**
Rule 9 requires every verdict committed; it does not require the last one to approve, while
its own "not just the final approve" presupposes that it does.
*Options.* (a) Leave rule 9 silent, on the ground that it governs the record and rule 3
governs the gate — the maintainer's commit bit is the approval. (b) State in rule 9 that
the last recorded verdict must be approving.
*Recommendation:* (a), with the wording tightened so it does not presuppose what it does
not require.
*Counter-argument:* a reader who takes rule 9 as the merge condition will read the
presupposition as the rule, and (b) removes that ambiguity for one sentence's cost.

**6. What counts as a round?** (new)
The build record documents four Codex crashes mid-review. A crashed or aborted invocation
has no verdict, so "every review round" is either impossible to satisfy or leaves the
builder to decide what counted.
*Options.* (a) A round is an invocation that returned a verdict; aborted invocations are
noted in the log but carry no row. (b) Every invocation gets a row, with "aborted, no
verdict" as its disposition. (c) Leave it undefined.
*Recommendation:* (a). The record exists to carry verdicts and dispositions, and an
invocation that produced neither has nothing to carry.
*Counter-argument:* (a) lets a builder retire an inconvenient round by calling it aborted,
and nobody outside the session can tell. (b) is the tamper-resistant version, at the cost
of rows that say nothing.
