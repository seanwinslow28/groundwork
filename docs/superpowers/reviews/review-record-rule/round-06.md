## Round 6 — 2026-08-29, task-mtecmww0-bznzu5, verdict: does not approve (11 findings)

Reviewed: `79d216c` (the round-5 fixes). All 11 accepted. Two fixed in the following
commit, one settled as a builder error rather than a maintainer question, the rest by
rewriting the items again. Round-5's open-items section is **superseded in full** by this
round's and left as written. Prior tables untouched.

**Fix commit for round 5: `79d216c`.** Round 1 → `edc3c26`, 2 → `1c94a3c`, 3 → `bd81918`,
4 → `bcee344`, 5 → `79d216c`. Round 6's is named by round 7.

**On the non-terminal rows.** Round 6 is right that "fixed in commit X / rejected with
grounds" is the locked inventory and that "carried" or "escalated" is not a third terminal
form — so this was mine to get right, not a maintainer question, and it leaves round 5's
item 8 with one fewer sub-question. The consequence is stated rather than papered over:
**every row in this log whose disposition is an escalation is non-terminal, and rule 9's
merge condition is therefore not met.** That is not a defect in the log; it is the accurate
reading of a branch that cannot merge until the maintainer decides. Each such row becomes
"fixed in commit X" once a decision lands.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Item 1's mechanical option cannot work as written: review logs live under `docs/superpowers/`, which `SKIP_RELPATHS` excludes from the validator entirely, and a new log has no version at the base, so a base-to-HEAD diff cannot reconstruct which text belonged to an earlier round — after a squash that history is gone | CONFIRMED | Fixed: verified in this worktree at `scripts/validate.py:28`. Item 1 rewritten with options that survive a squash — per-round content hashes in the log, or one file per round — and the validator option restated with the two obstacles named |
| 2 | major | Item 2's "unique identifier" does not solve reuse: a branch creation commit is neither unique nor an immutable branch property, and a hash of the branch name repeats when the name does. The counter-argument defeats the recommendation and then falsely says (e) solves reuse. The option a maintainer would want — a readable slug plus a real per-incarnation identifier — is missing | CONFIRMED | Fixed: the false claim is withdrawn, and the slug-plus-identifier option is added and recommended |
| 3 | major | Item 3's recommendation does not establish integrity: (d) verifies path scope, (e) records a SHA, and neither verifies the builder copied the right SHA, verdict, findings or dispositions — a fabricated round at the correct path with a fabricated SHA passes both. "Auditable without asking anyone to trust the builder" is false | CONFIRMED | Fixed: the claim is withdrawn, and the missing option — binding the reviewer's own output to the appended record — is added and recommended |
| 4 | major | Item 4's stated reason is false: (c) is not the only option leaving one normative copy — (d) does too — and the natural inverse is omitted: keep decision 7 as the detailed source and make rule 9 and both headers pointers, which is what rule 7 already implies | CONFIRMED | Fixed: the false reason withdrawn, the inverse added as option (e) and recommended over (c) |
| 5 | major | Item 5's precedent claim is false. The slice-2.1 override does not survive "only in a design file": merge commit `5fc61c6` says "Merged by maintainer decision with residuals accepted as documented". What is absent is a contemporaneous review log. The actual precedent — grounds in the merge commit — was missing from the options | CONFIRMED | Fixed: verified against `5fc61c6` in this worktree. The claim is corrected to what the merge commit says, and the merge-commit-grounds option is added and recommended |
| 6 | major | Item 6 oversells (d): (b) also records every invocation, so (d) is not "the only option" preventing quiet retirement; "one line per crash" is false when the same option requires retaining partial output; and the build record establishes four crashes and manual stale-job cancellation but not preserved identities or partial findings | CONFIRMED | Fixed: (b) recommended instead, the cost claim removed, and the counter replaced with the real one — no definition prevents omission unless an attempt ledger outside the builder's control is authoritative, and the runtime's job state is not a repository artifact |
| 7 | minor | Item 7 omits whether "reviewed revision" means a commit or a tree SHA, whether a dirty working tree may be reviewed, and its dependence on item 4's outcome; and its counter leans on voluntary practice rather than the real gap | PLAUSIBLE | Fixed: all three added, and the counter replaced with the operational restriction and the authenticity gap |
| 8 | major | Item 8 bundles five questions into three arbitrary packages, and one of them is already settled: "fixed in commit X / rejected with grounds" is the locked inventory, so a non-terminal disposition is not legal at merge — a builder error, not a policy choice. It also omits what counts as adequate grounds and how faithfully finding text must be preserved | CONFIRMED | Fixed: the settled question is removed from the item and its consequence stated above; the rest are split into items 8, 9 and 10, each with its own options, and the two omissions added |
| 9 | major | The log still does not satisfy the disposition contract — several rows are "carried", "escalated" or "recorded", and round 5's fix commit `79d216c` was absent | CONFIRMED | Half fixed: `79d216c` is recorded above. The non-terminal rows are addressed by the statement above rather than by relabelling them, which would hide the branch's actual state |
| 10 | major | Rule 9 names this branch's worked example as its example, but that log has 88 `Fixed:` dispositions and none naming a SHA — 21 say "the following commit", the convention round 4 rejected as weaker. Calling it the worked example creates another parallel-site mismatch | CONFIRMED | Fixed: a fix-commit map for all 24 fix rounds is backfilled into `spec-roles-accountable-unit.md` as a new section, derived from git and verified in this worktree, with no round's table touched. Round 25 approved and left no fix commit; `a4f2970` records its verdict |
| 11 | major | Rule 9 still requires guesses beyond the listed items: how `<slice>` is derived from a plan filename when a branch has several plans; how much finding text must survive, verbatim versus compressed; and what constitutes adequate grounds for rejection | CONFIRMED | New items 9, 10 and 11. The first has no worked example at all — no planned-slice review log exists |

Verified clean by the round, and reported as such: rule 9 is **byte-identical from
`bd81918` through HEAD** (blob `9504fea1…`), and adds, drops, renames and reinterprets
nothing operative relative to decision 7. All four recorded fix SHAs are accurate by diff.
Prior round tables hash identically to their introducing commits, and round 4's entire
pre-round-5 prefix — including its open-items section — is byte-identical to `bcee344`.
Decision 7's operative block and counter-argument hash identically on `main` and HEAD.
Round 5's predecessor-SHA structure is append-only and better than round 4's
rewrite-dependent map. Item 2's collision claims were independently reproduced on this
APFS worktree: `Case.md` resolves as `case.md`, NFC and NFD `é.md` resolve to one inode,
and git accepts `x`, `x.md/y`, `docs/review` and a literal `docs%2Freview` as branch names.
Item 3's history is confirmed — `a4f2970` has parent `acd729c`, adds only the 12-line
approval and totals, is the second parent of `c7664d4`, and its body records the off-by-one
corrected before commit. `AGENTS.md` is 162 lines. All four gates passed in the reviewer's
environment: `validate.py .` 0 errors / 7 warnings, `--diff main` exit 0, `demo` 0 errors /
2 warnings, 709 tests `OK (skipped=1)`.

### Open maintainer items after round 6 — superseding round 5's set in full

Eleven items. Round 5's item 8 loses its first sub-question, which was settled, not open.

**1. Never-rewrite, and what assures it.** Decision 7 says only "appended per round".
*Options.* (a) No rule. (b) Rule, assured by review — a reader diffs prior rounds against
their introducing commits, which works only while branch history survives. (c) Rule, plus
each round records a content hash of every prior round in the log itself, so a rewrite is
detectable from the merged snapshot alone. (d) Rule, plus one file per round, so a rewrite
is a change to a file that should never change. (e) Rule, plus a history-preserving merge.
(f) Rule, plus a validator check — which today cannot be built as imagined: review logs sit
under `docs/superpowers/`, excluded by `SKIP_RELPATHS` at `scripts/validate.py:28`, and a
new log has no base version from which earlier rounds could be reconstructed, so (f) needs
(c) or (d) underneath it anyway.
*Recommendation:* (d). One file per round is the only option that makes a rewrite a change
to a file with no legitimate reason to change, needs no validator work, and survives a
squash.
*Counter-argument:* it multiplies files per branch and gives up the single readable log
that both existing records are; and a determined rewriter can still edit a per-round file —
only (b) plus (e) leaves evidence the rewriter does not control.

**2. The `/` → `-` flattening is not injective, and neither is any pure derivation.**
Reproduced collisions: reused branch names; case folding and Unicode normalization on this
filesystem; `x` versus `x.md/y`; and `docs/review` versus a branch literally named
`docs%2Freview`.
*Options.* (a) Keep the flat mapping. (b) Percent-encode `%` and every character outside
`[a-z0-9._-]`, uppercase included — total and unreadable. (c) Mirror the branch path under
`reviews/` — fails on prefix conflicts and reuse. (d) Name the log for the slice — reuse
and concurrent naming still collide. (e) Name it by a derived identifier — a creation
commit is not unique and not an immutable branch property, and a hash of the name repeats
when the name does, so this does not solve reuse. (f) A readable slug plus a real
per-incarnation identifier — an issue or PR number, a monotonic counter, or a
collision-detecting suffix — with the branch name recorded inside the log.
*Recommendation:* (f). Reuse is the collision no derivation can remove, so the name must
carry something no two incarnations share, and a readable slug keeps the directory
browsable.
*Counter-argument:* it needs somewhere to allocate the identifier, which this repository
has no mechanism for; a builder can pick a colliding counter by accident; and the issue-
number variant borrows GitHub's uniqueness at the cost of coupling the durable record to a
tracker the repository does not otherwise depend on.

**3. There is no terminal-record step, so the last verdict lands unreviewed.**
`a4f2970` added round 25 and the closing totals unreviewed, and its body records an
off-by-one in that arithmetic corrected before commit.
*Options.* (a) Exempt a final record-only commit, defined as a diff touching nothing
outside the review-log path. (b) Have the final round review the branch including its
pending record, with the verdict committed in the merge — which moves the unreviewed
content into the merge rather than removing it. (c) State in rule 9 that the terminal
record commit is unreviewed, and accept it. (d) A mechanical check on path scope and
earlier-section immutability. (e) Record the reviewed revision. (f) Store the reviewer's
own output alongside the summary, so the summary can be reconciled against something the
builder did not author.
*Recommendation:* (f) with (d). Nothing else binds the record to the review. (d) and (e)
together verify only that one path changed and that a SHA is present — a fabricated round
at the correct path with a fabricated SHA passes both, which is why round 5's claim that
they make the record auditable "without asking anyone to trust the builder" is withdrawn.
*Counter-argument:* reviewer output is large, and the runtime's job state is not a
repository artifact, so (f) changes what a review log is — from a summary a person can read
to an archive nobody will; and (c) remains the only option that costs nothing and claims
nothing false.

**4. Should the contract live in one place?**
Drift has appeared in all four sites: the worked header's attribution, this header's
non-restatement claim, decision 7's evidence, and rule 9's own historical count.
*Options.* (a) Leave it distributed. (b) Cut both headers to pointers — two normative
copies remain. (c) Make rule 9 the sole normative text and reduce decision 7 to the
decision and its counter-argument. (d) Move the contract to its own document that rule 9
and decision 7 both point at. (e) Keep decision 7 as the detailed source and make rule 9
and both headers pointers.
*Recommendation:* (e). Standing rule 7 already names the approved design as a source of
truth, so this puts the contract where the repository's own hierarchy says it lives, and it
is the only option that leaves one copy without demoting an approved decision.
*Counter-argument:* `build-sessions.md` is the file a build session actually loads, so
under (e) the operative contract is never in front of the builder — which is how rule 9's
evidence came to drift from decision 7's in the first place.

**5. Must the terminal verdict be approving?**
Silence lets a fully logged branch with unresolved major findings satisfy rule 9's literal
merge condition. The precedent: slice 2.1 was merged after a `FIX-BEFORE-SHIP` round-32
verdict, and `5fc61c6` records it — "Merged by maintainer decision with residuals accepted
as documented". What that slice lacks is a contemporaneous review log, not an override
record.
*Options.* (a) Leave rule 9 silent. (b) Require an approving terminal verdict. (c) Require
one unless the maintainer records an override with grounds **in the review log**. (d) Same,
with the grounds in the **merge commit** — which is what actually happened.
*Recommendation:* (d). It writes down the practice the repository already has rather than
inventing one, and the merge commit is the maintainer's own artifact, which is where an
override belongs.
*Counter-argument:* the merge commit is not in the log, so a reader of the record alone
sees an unresolved branch merged with no explanation — which is exactly the loss rule 9
exists to prevent, and (c) is the only option that keeps the whole story in one file.

**6. What counts as a round?**
The build record documents four Codex crashes mid-review and manual stale-job
cancellation; it does not establish that those attempts left identities or partial
findings.
*Options.* (a) A round is an invocation that returned a verdict; aborted ones are noted but
carry no row. (b) Every invocation gets a row, with "aborted, no verdict" as its
disposition. (c) Leave it undefined. (d) Distinguish attempt from round, with a numbered
round only for completed attempts and partial output retained.
*Recommendation:* (b). It is the minimum that makes an omission visible as a gap in the
numbering, and unlike (d) it does not promise to retain partial output the runtime may not
have produced.
*Counter-argument:* neither (b) nor (d) prevents omission unless an attempt ledger outside
the builder's control is authoritative, and the runtime's job state is not committed to the
repository — so both record honesty rather than enforce it.

**7. Should the reviewed revision be part of the required record?**
Both logs record it voluntarily; neither rule 9 nor decision 7 asks for it.
*Options.* (a) Leave it voluntary. (b) Require it in rule 9. (c) Require it in rule 9 and
decision 7. Orthogonal to all three: whether it is a **commit** SHA or a **tree** SHA, and
whether a review of a dirty working tree is permitted at all.
*Recommendation:* require it, as a commit SHA, with a clean worktree at review time — the
placement following whatever item 4 decides, since (b) versus (c) only matters while two
normative copies exist.
*Counter-argument:* it forbids reviewing uncommitted work, which is how a mid-slice round
naturally runs; and the revision is still self-asserted, so it improves auditability
without establishing authenticity — item 3's (f) is what would.

**8. Who may reject a finding with grounds, and what counts as adequate grounds?**
"Rejected with grounds" is the one disposition that closes a finding by disagreeing with
it, so it is where the record can be quietly weakened.
*Options.* (a) The builder may, with grounds recorded. (b) Only the maintainer may.
(c) The builder may, but a rejected finding must also be listed at the top of the log so it
is visible without reading every round.
*Recommendation:* (c). It keeps the builder's judgment, which is what makes a review loop
work, and makes the one weakening move impossible to bury.
*Counter-argument:* a summary list is another parallel site, and this branch has spent six
rounds proving that parallel sites drift.

**9. How is `<slice>` derived from a plan filename, and what if a branch has several
plans?** No planned-slice review log exists, so there is no worked example.
*Options.* (a) The plan's filename minus its date prefix. (b) The branch's slice name as
the plan's title gives it. (c) One log per plan.
*Recommendation:* (a) — mechanical, and it makes the log sort beside its plan.
*Counter-argument:* it says nothing about the several-plans case, which (c) answers and (a)
leaves to the builder.

**10. How much of a finding must survive?** Both logs compress the reviewer's findings into
one table cell.
*Options.* (a) Compressed summaries, as practised. (b) Verbatim reviewer text. (c)
Compressed in the table, verbatim output retained alongside — item 3's (f) doing double
duty.
*Recommendation:* (c), if item 3 goes that way; otherwise (a).
*Counter-argument:* a compression is an interpretation, and the builder doing the
compressing is the party the record exists to check.

**11. How is a clean round represented, and are reviewer severities kept verbatim?**
*Options.* (a) Leave both to the builder. (b) Fix a form for a clean round and require
severities verbatim. (c) Require severities verbatim and leave the clean-round form open.
*Recommendation:* (c). A normalised severity can soften a reviewer's grade, which is the
half with teeth.
*Counter-argument:* reviewers do not use one vocabulary — this branch's rounds have used
`major`/`minor` and the worked example also uses `high`, `med`, `low` and `bookkeeping` —
so "verbatim" preserves a mess rather than a signal.
