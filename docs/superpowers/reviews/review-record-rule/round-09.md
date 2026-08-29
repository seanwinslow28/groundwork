## Round 9 — 2026-08-29, task-mteefvcc-8d17e1, verdict: does not approve (9 findings)

Reviewed: `21c6c74` (round 8's six contradiction fixes). All 9 accepted; six fixed in the
following commit, two corrected by supersession, one escalated. Round-08's terminal table
and round-07's landing claims are **amended** below.

**The root cause, named.** Rounds 8 and 9 both found the rule unable to admit its own
branch, and the reason is a clause I wrote and the maintainer never approved. Decision 7's
merge condition is that the verdicts *are committed* — "A slice may not merge unless the
verdicts of every Codex review round run against it … are committed in the repository."
It says nothing about every finding being closed. Rule 9's "a branch carrying an unresolved
finding does not merge" was a builder addition, and it is what made the terminal override
unrecordable, the nine escalations retroactively illegal, and each patch generate the next
contradiction. **It is removed**, which restores decision 7's actual scope. This is the
third time on this branch that legislating past a locked decision produced the defect the
next round found.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Round 8's own finding 9 is dispositioned "partly fixed … the rest are left open", which rule 9 did not recognise — so the branch still violated its own merge condition, and the README's "None blocking" was false | CONFIRMED | Fixed at the root: **open** is now a recorded disposition, listed in the README, and it does not block a merge. The four points round 8 left open — verdict vocabulary and what counts as approving, partial output from an aborted invocation, numbering past 99, and the grandfathering boundary — are listed as open findings rather than described as small |
| 2 | major | The terminal override still could not produce a compliant entry: before the merge the remaining findings had no permitted disposition, after it their entries are immutable, and the README is forbidden to change a disposition — so there was no legal moment to record the rejection | CONFIRMED | Fixed by the same removal. Findings that remain at merge are **open**, recorded as such, and the maintainer merges over them with grounds in the merge commit. Nothing has to change a disposition, so no illegal moment exists. The unresolved sub-questions — per-finding or wholesale grounds, who writes the README listing, when — dissolve with it |
| 3 | major | The nine terminal dispositions are not accurately attributed: only rounds 1 row 3 and 3 row 3 are cleanly "fixed in `b33296e`"; four landed only in `21c6c74`, one was nominal but incoherent until then, and round 5 row 9 is not fixed at all | CONFIRMED | Corrected by supersession below, with per-row attribution to the commit that actually fixed it, and round 5 row 9 restated as **open** |
| 4 | major | Round 8's sweep was incomplete — round 4 rows 2, 4, 7 and 8, round 5 row 8 and round 6 row 9 ("Half fixed") were also non-terminal and were not in its table | CONFIRMED | Fixed: all six are dispositioned below. Round 8's own finding 1 was right that recording where a decision landed does not convert a disposition, and its table then failed to apply that to these rows |
| 5 | major | The README omits round 8's actual fix commit: the cell says "see below" and the text never names `21c6c74`, which is the commit carrying round 8's fixes | CONFIRMED | Fixed: the README's map names `21c6c74` for round 8 and `see round-10` for round 9, which is the normal one-entry lag the rule describes |
| 6 | major | The rejection-grounds taxonomy is an unapproved policy choice under rule 5, and is both too narrow and too permissive — it excludes the maintainer consciously accepting a correct, in-scope finding, which is exactly what `5fc61c6` did ("accepted as documented"), while its own categories can be satisfied perfunctorily | CONFIRMED | **Removed and escalated.** The taxonomy is out of rule 9; grounds are unconstrained again, as decision 7 left them. This is the third unapproved policy on this branch and the review is right to call it that. Open maintainer item below |
| 7 | major | Planned-slice directories have no collision protocol: the suffix rule applied only to `<slug>` under `reviews/`, so two branches carrying the same plan filename map to one `plans/<slice>-reviews/` directory with nothing said | CONFIRMED | Fixed: the suffix rule now reads "for **either** path", and the full-branch-name disambiguation and merge-time rename apply to both |
| 8 | minor | The slug and rename repair still needs guesses: ASCII versus Unicode lowercasing, which merge target before a PR exists, who performs a merge-time rename, whether the README records the original or current branch name, and whether a rename is truly outside immutability given git records a path change | PLAUSIBLE | Partly fixed: "ASCII-lowercased" is now explicit, and the README records the branch name "as it stood when the directory was made". The rest are recorded as open findings rather than resolved |
| 9 | minor | Parallel sites still describe superseded conventions: the grandfathered worked example's header says rule 9 asks for "fixed in commit X", which it no longer does, and both branch READMEs say entries are fixed once their round "has passed" while rule 9 now says "once committed" | CONFIRMED | Fixed: this README's wording matches rule 9, and the worked example's header note is corrected. The sibling branch's README carries the same wording and is corrected on its own branch |

Verified clean by the round, and reported as such: decision 7's amended note is accurate and
sufficiently prominent, and its normative choice and counter-argument remain byte-identical
to `main` (`819c15b4…`, `665a3e29…`). Rule 9 nowhere still says "fixed in commit X". The
numbering is unambiguous — the next entry is `round-09.md`. Aborted invocations are
internally consistent when they produced no findings. The README's rounds 1–6 rows are
correct with every fix commit having the reviewed commit as its parent, round 7 is correctly
identified as a non-review entry, and the finding total is exactly 56 (3+5+7+12+9+11+9)
across seven review rounds. `build-sessions.md` is 87 lines, `AGENTS.md` 162. All four gates
green.

### Corrected terminal dispositions, superseding round 8's table

Round 8 attributed nine rows to `b33296e`. The accurate attribution:

| Entry | Row | Disposition |
|---|---|---|
| round-01 | 3 | Fixed in `b33296e` — per-entry files and immutability |
| round-02 | 5 | Fixed in `21c6c74` — `b33296e` handled only an already-visible collision |
| round-03 | 3 | Fixed in `b33296e` — per-entry immutability closed the snapshot question |
| round-03 | 4 | Fixed in `21c6c74` — same merge-time gap as round-02 row 5 |
| round-03 | 7 | Fixed in `21c6c74` — `b33296e` made rule 9 operative but left decision 7 reading normative |
| round-04 | 2 | Fixed in this round's commit — the terminal-record fixed point resolves with the merge-blocking clause removed |
| round-04 | 4 | Fixed in `21c6c74` |
| round-04 | 5 | Fixed in this round's commit — nominal at `b33296e`, incoherent until the override became recordable |
| round-04 | 6 | Fixed in `21c6c74` — `b33296e` had made "aborted, no verdict" a third disposition |
| round-04 | 7 | Fixed in `b33296e` — durability, by per-entry immutability |
| round-04 | 8 | Fixed in `21c6c74` — contract-surface drift, by decision 7's corrected note |
| round-05 | 8 | Fixed in `b33296e` — the reviewed revision became required |
| round-05 | 9 | **Open.** Branch renames and verdict vocabulary are still unresolved; calling it fixed was wrong |
| round-06 | 9 | Fixed in this round's commit — the README now names `21c6c74` |
| round-06 | 11 | Fixed in `21c6c74` — the filename rule, the multi-plan rule and slice derivation |
| round-08 | 9 | **Open** — the four points named in row 1 above |

### Open findings

Carried in the README, blocking nothing: verdict vocabulary and what counts as approving;
whether partial output from an aborted invocation must survive; numbering past `round-99`;
the grandfathering boundary for "work started"; branch identity after a rename; which merge
target applies before a PR exists; who performs a merge-time rename; and which commit is
mapped when a round's fixes span several.

### Open maintainer item (new)

**What counts as adequate grounds for rejecting a finding.** Decision 8 settled who may
reject and the README visibility; it did not settle this, and round 8's attempt to define it
was an unapproved policy choice, now removed.
*Options.* (a) Leave grounds unconstrained, as decision 7 does. (b) Require a stated
category — factually wrong, out of scope, superseded — each naming its source, scope and
follow-up, or superseding item. (c) (b) plus a fourth category, **accepted risk**: the
finding is correct and in scope and is being accepted anyway, which is what `5fc61c6` did.
*Recommendation:* (c). The precedent this rule cites is an accepted-risk rejection, and a
taxonomy that cannot express its own worked example is the wrong taxonomy.
*Counter-argument:* any category list can be satisfied perfunctorily — an artificially
narrow scope, a superseding item that supersedes nothing — so (b) and (c) add a form to fill
in rather than a constraint, and (a) at least does not pretend otherwise.
