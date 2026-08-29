## Round 10 — 2026-08-29, task-mtef01zc-ww47s3, verdict: does not approve (6 findings)

Reviewed: `edce94b` (round 9's removal of the invented merge-blocker and the introduction of
**open**). All 6 accepted; three fixed in the following commit, two corrected by
supersession, one standing. **The round confirmed round 9's root-cause diagnosis and that
`open` resolves the central contradiction** — it walked the model at every point in time
(before merge, at merge, after merge, and a finding fixed two rounds later) and found no
clause requiring a committed disposition to change.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Removing the unapproved grounds taxonomy also removed **"The builder may reject a finding"** — half of ratified maintainer decision 8. Rule 9 then specified rejection without saying who may do it, contradicting a locked decision and rule 7, while the README still claimed decision 8 had settled it | CONFIRMED | Fixed: the clause is restored to rule 9. A ratified decision was collateral damage in removing an unratified one, which is its own lesson about surgical removals |
| 2 | major | The rejection-grounds escalation fails rule 5 on its reason, not its shape: `5fc61c6` calls its residuals **"open findings"** accepted as documented, so the precedent is the open-plus-override path this branch just built, **not** an "accepted risk" rejection category. The recommendation rested on that misreading, and the option set omitted requiring case-specific grounds without a closed taxonomy | CONFIRMED | Fixed: the false reason is withdrawn, "accepted risk" is dropped as a category, the omitted option is added, and the recommendation is rebuilt on what the precedent actually shows. Restated in full below |
| 3 | major | The corrected sixteen-row table is still inaccurate in three rows: round-04 row 2 was fixed in `b33296e`, not `edce94b`; round-06 row 9's rationale ("the README now names `21c6c74`") is unrelated to the original finding, whose missing SHA was `79d216c`; and round-06 row 11 included adequate grounds, which is still open, so the row cannot be wholly fixed | CONFIRMED | Corrected by supersession below. Round 9 claimed its table was the accurate superseding account and it was not — the second table in a row to overstate |
| 4 | minor | This README's opening still said an entry is fixed once its round "has passed", the boundary rule 9 rejected, while its own layout paragraph said "once committed" | CONFIRMED | Fixed. Round 9's finding 9 had reached the sibling branch and the layout paragraph but not this sentence — parallel-site drift inside a single file |
| 5 | minor | The open-findings list is incomplete: it omits how a clean round is represented, left open by decision 11, and whether treating a directory rename as outside entry immutability is coherent given git records a path deletion and addition | CONFIRMED | Fixed: both added. "Who may reject" is moot once finding 1's restoration lands |
| 6 | minor | The session still departs from rule 1 — two increments in one session, with kickoff authorisation asserted but not inspectable | CONFIRMED | Standing, unchanged: recorded in the README, ratification reserved to the maintainer at merge. Not something this branch can close on its own |

Verified clean by the round, and reported as such: the root-cause diagnosis is **confirmed
correct** — decision 7 never said a finding must close, and the merge-blocking clause was
builder-authored. The `open` model is coherent at every point in time, and no rule among 1,
2, 3, 5, 7 or 8 imposes a separate closure condition. Thirteen of the sixteen table rows are
right. Every README number checks out: rounds 1–6, 8 and 9 reviewed the revisions shown,
every fix commit has the reviewed revision as its parent, the total is exactly 65
(3+5+7+12+9+11+9+9) across eight review rounds, and no finding was rejected. Decision 7's
normative block and counter-argument remain byte-identical to `main` (`819c15b4…`,
`665a3e29…`). Rule 9's evidence is supported in full, the grandfathered worked example's 24
fix commits are correctly parented, and its corrected header note is accurate. The sibling
branch at `d883bb7` matches. `AGENTS.md` is 162 lines. All four gates green.

### Corrected rows, superseding round 9's table

| Entry | Row | Was recorded | Actually |
|---|---|---|---|
| round-04 | 2 | Fixed in this round's commit | **Fixed in `b33296e`** — the terminal-record decision was implemented there, stating the unreviewed record commit plainly |
| round-06 | 9 | Fixed in this round's commit, "README now names `21c6c74`" | **Fixed in `74c7122`** for the half the finding actually raised — the missing SHA was `79d216c`, recorded in the round-6 entry. The non-terminal half became admissible under `edce94b`; the rationale given was unrelated to the finding |
| round-06 | 11 | Fixed in `21c6c74` | **Partly fixed in `21c6c74`** — the filename rule, the multi-plan rule and finding fidelity landed there. The row also raised what counts as adequate grounds, which is **open** as the maintainer item below |

The other thirteen rows stand as round 9 recorded them.

### Open maintainer item, restated

**What counts as adequate grounds for rejecting a finding?** Decision 8 settled that the
builder may reject and that rejections are listed in the README. It did not settle what a
rejection must say.

*What the precedent actually shows.* `5fc61c6` recorded slice 2.1's round-32 residuals as
**"open findings … accepted as documented"** — so the repository's one worked case of
merging over unfixed work is the **open-plus-maintainer-override** path this branch now
provides, not a rejection at all. Round 9's recommendation misread it and proposed
"accepted risk" as a fourth rejection category; that is withdrawn.

*Options.* (a) Leave grounds unconstrained, as decision 7 does. (b) Require a stated
category from a closed list — factually wrong, out of scope, superseded — each naming its
source, its scope and follow-up, or the superseding item. (c) Require grounds to be
case-specific and to say why the finding needs no change **on this branch**, without a
closed list.
*Recommendation:* (c). A closed list cannot anticipate every legitimate rejection, and this
branch has already demonstrated that — the taxonomy round 8 wrote could not express its own
cited precedent. (c) constrains what a rejection must establish without pretending the
reasons are enumerable.
*Counter-argument:* "case-specific" is not checkable by anything, so a single perfunctory
sentence satisfies (c) exactly as it satisfies (a) — which makes (c) arguably (a) with more
words, while (b) at least forces the rejector to commit to a shape a reader can test.
