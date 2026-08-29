## Round 11 — 2026-08-29, task-mtefgepn-0np8vd, verdict: does not approve (5 findings)

Reviewed: `214c1b5` (round 10's fixes). All 5 accepted; two fixed in the following commit,
two corrected by supersession, one standing. Round-09 and round-10's disposition tables are
**amended** below.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The rebuilt recommendation still rests on a category error: it argues a closed taxonomy is inadequate because it could not express `5fc61c6`, but a **non-rejection** need not fit a rejection taxonomy. The stronger argument runs the other way — once accepted-risk routes through open-plus-override, this branch has produced no legitimate rejection outside the three categories, and they are more auditable than "case-specific" | CONFIRMED | Fixed by changing the recommendation, not just its reason. **(b), the closed list, is now recommended**, on a reason that is true: every rejection this session actually produced — both of them, on the sibling branch — is an out-of-scope rejection, and no case has arisen that the three categories cannot hold. Restated in full below. Third recommendation on this item, and the first whose reason survives its own precedent |
| 2 | major | The twice-corrected table is still incomplete: **round 2 row 3** was marked fixed, then round 3 row 1 removed that fix and said it "stands unfixed and escalated" — so seventeen rows needed accounting, not sixteen — and round 8 row 9 leaves the clean-round form open in addition to the four points round 9 recorded | CONFIRMED | Corrected by supersession below. Verified independently: round 2 row 3 is the terminal-record finding, round 3's header names it among the amended rows, and round 3 row 1's disposition removes its fix. Three tables in a row have now been incomplete |
| 3 | major | The README still deferred round 9's fix commit to "see round-11" although `edce94b` was already known and round 10 was committed — repeating the indirect-map defect graded major earlier on this branch | CONFIRMED | Fixed: rounds 9 and 10 now carry `edce94b` and `214c1b5`. Only round 11's own cell defers, which is the one-entry lag the rule describes |
| 4 | minor | The plan-path selector says "when the branch carries exactly one plan" without defining "carries" — adds, changes, implements, or merely contains, with 31 plan files in the tree and a branch able to implement an already-committed plan without touching it — and the ambiguity is absent from the open-findings list | PLAUSIBLE | Fixed rather than listed: "when the branch's **own commits add or change** exactly one plan", which a reader can settle from the diff |
| 5 | minor | The session still departs from rule 1 — two increments in one session, kickoff authorisation not inspectable | CONFIRMED | Standing and unchanged. Honestly disclosed, ratification reserved to the maintainer; not something this branch can close |

Verified clean by the round, and reported as such: the restored builder-rejection clause
exactly implements decision 8, and **every deletion from rule 9 between `21c6c74` and
`214c1b5` is accounted for** — the unratified taxonomy and merge-blocker removed
deliberately, the ratified clause restored, the approving-verdict model replaced by the
open-compatible one, and no other ratified decision lost. The eight-scenario walk of rule 9
is supported at every branch: a clean round, all-fixed, open-plus-override, a rejection, a
crash, a maintainer-decision entry, a rename, and a slug collision. The README accounts for
every known remaining guess except the plan selector, now fixed. Every number checks out:
71 findings across nine review rounds at the reviewed state, all reviewed revisions and
verdicts matching their entries, all nine fix commits correctly parented, and none rejected.
Decision 7's normative block and counter-argument remain byte-identical to `main`. The
worked example's 25 rounds, 102 rows and 24 backfilled fix commits all verify. The sibling
branch at `d883bb7` carries no undisclosed contradiction, and its immutable round-8 language
correctly describes the rule version then under review.

### Corrected rows, superseding rounds 9 and 10

| Entry | Row | Disposition |
|---|---|---|
| round-02 | 3 | **Fixed in `b33296e`** — the terminal-record finding, missing from every prior table. Round 2 recorded it fixed, round 3 row 1 removed that fix as unratified policy, and `b33296e` resolved it by stating plainly that the terminal record commit is unreviewed |
| round-08 | 9 | **Open**, on five points not four: verdict vocabulary and what counts as approving; partial output from an aborted invocation; numbering past `round-99`; the grandfathering boundary; **and how a clean round is represented**, which decision 11 left open and round 9's summary omitted |

The other fifteen rows stand as rounds 9 and 10 recorded them.

### Open maintainer item, restated a third time

**What counts as adequate grounds for rejecting a finding?** Decision 8 settled that the
builder may reject and that rejections are listed in the README. It did not settle what a
rejection must say.

*What the precedent shows, correctly read.* `5fc61c6` recorded slice 2.1's residuals as
"open findings … accepted as documented". That is the **open-plus-maintainer-override** path,
not a rejection — so it neither supports nor undermines any rejection taxonomy, and rounds 9
and 10 were both wrong to reason from it. Round 9 called it a fourth category; round 10
called it proof that a closed list is inadequate. Neither follows.

*Options.* (a) Leave grounds unconstrained, as decision 7 does. (b) Require a stated
category from a closed list — factually wrong (naming the source), out of scope (naming the
scope and the follow-up work it becomes), or superseded (naming what supersedes it). (c)
Require grounds to be case-specific and to say why the finding needs no change on this
branch, without a closed list.
*Recommendation:* **(b).** The evidence is this session's own: two findings were rejected,
both on the sibling branch, and both are out-of-scope rejections that state their scope and
their follow-up. Nothing has arisen that the three categories cannot hold, and the case that
looked like a fourth — accepting a correct, in-scope finding — is handled by leaving it
**open** and overriding at merge, which is what the repository's one precedent actually did.
A closed list is auditable; "case-specific" is satisfied by any sentence at all.
*Counter-argument:* a closed list cannot anticipate a legitimate reason nobody has hit in
eleven rounds of one session, and when one arrives the builder either distorts a category to
fit or is blocked. The open-plus-override path is the escape hatch that makes closing the
list survivable — but it routes through the maintainer, so (b) quietly moves work from the
builder's judgment to the maintainer's inbox, which may be the real cost.
