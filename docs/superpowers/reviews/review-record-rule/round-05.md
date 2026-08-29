## Round 5 — 2026-08-29, task-mtebuqtg-jcrq9j, verdict: does not approve (9 findings)

Reviewed: `bcee344` (the round-4 fixes). All 9 accepted. One fixed structurally, six by
rewriting the open items the round showed to be unsound, two added as new items. Round-4
rows 1, 3, 4, 7 and 8 are **amended** below; round 4's open-items section is **superseded
in full** by this round's, and left as written. Prior tables untouched.

**Fix commit for round 4: `bcee344`.** From here each round records the previous round's
SHA in its own entry rather than a mapping that would have to be rewritten to extend —
which round 4's structure required, and which is the very durability question item 1
leaves open. Round 1 → `edc3c26`, round 2 → `1c94a3c`, round 3 → `bd81918`, round 4 →
`bcee344`.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Round 4's mapping still says "round 4 → the commit following this table" though `bcee344` exists, and says it will be "extended each round", which would mean rewriting an earlier entry — the durability question item 1 leaves unresolved | CONFIRMED | Fixed structurally: `bcee344` is named above, and each round now records its predecessor's SHA in its own entry, so the record only ever grows. Amends round-4 row 1 |
| 2 | major | Item 2's recommendation is not collision-safe. Mirroring the branch path under `reviews/` still fails on reused branch names, case and Unicode folding on this filesystem, and file/directory prefix conflicts — valid branches `x` and `x.md/y` need `reviews/x.md` to be both. Option (b) was falsely called injective: encoding only `/` collides `docs/review` with the valid literal branch `docs%2Freview`. Whole families were omitted. The "only option injective" reason is false and the counter-argument is a straw man | CONFIRMED | Fixed: item 2 rewritten with a correct option set and a recommendation whose reason survives. Supplying technically valid options was mine to get right; choosing among them is not. Amends round-4 row 4 |
| 3 | major | Item 3's path-scoped exemption is only partially checkable: it does not say which diff and parent are authoritative, what the review-log path is while item 2 is open, whether renames or symlink replacement qualify, whether earlier rounds may be rewritten inside that path, or who checks. It proves one path changed, not that the append is accurate. Option (b) was also misstated — a merge commit still adds the verdict after the review, so the self-reference moves rather than disappears | CONFIRMED | Fixed: item 3 rewritten. The claim that (a) closes the loophole is withdrawn; two mechanical options the round named are added. Amends round-4 row 2's disposition |
| 4 | major | Item 1 conflates durability with preserved history — a no-rewrite rule governs the merged snapshot regardless of squash, and preserved branch history aids detection, not prevention. Option (a) leaves a nested decision unresolved, mechanical enforcement is omitted, and the counter-argument ("both logs practised it without a rule") does not show the risk is absent | PLAUSIBLE | Fixed: item 1 rewritten, the two properties separated, mechanical enforcement added as an option, and the stronger counter substituted. Amends round-4 row 7 |
| 5 | major | Item 4's recommendation contradicts its own evidence: "every drift this branch found was a header restating rule 9" is false — round 1 corrected rule 9's own historical count. And cutting the headers does not make rule 9 the sole normative text while decision 7 remains a source of truth under rule 7 | CONFIRMED | Fixed: the false claim is withdrawn, and the option that actually reduces the contract to one normative copy is stated with the cost it carries. Amends round-4 row 8 |
| 6 | major | Item 5 omits the strongest model — require an approving terminal verdict unless the maintainer records an explicit override with grounds — and understates the consequence: silence lets a fully logged branch with unresolved major findings satisfy rule 9's literal merge condition. Rule 3 does not say Codex approval is unnecessary; it calls this a review gate | PLAUSIBLE | Fixed: the override model is added and recommended, and the consequence is stated as the review found it. The repository has a precedent — the 32-round slice was merged over a FIX-BEFORE-SHIP verdict, recorded only in a design file — which is now cited in the item. Amends round-4 row 5's framing |
| 7 | major | Item 6 recommends the least tamper-resistant definition. A crashed invocation is not empty — it has an identity, a terminal status, and possibly partial findings — and the options omit an attempt/round distinction under which a crash cannot be quietly retired | PLAUSIBLE | Fixed: the attempt/round option is added and recommended in place of the previous one, which the round correctly read as giving the builder discretion its own counter-argument admitted was a risk. Amends round-4 row 6 |
| 8 | major | Rule 9 does not require the reviewed revision to be recorded. Both logs do it voluntarily; neither rule 9 nor decision 7 asks for it, so a compliant log can carry a verdict and a fix SHA without establishing which tree was reviewed, making amendment chains unauditable | PLAUSIBLE | New open item 7. Not fixed in rule 9: adding to the inventory decision 7 fixed is a decision-7 change, not a clarification |
| 9 | minor | Several operational details stay builder-selectable outside the open items: who may reject a finding with grounds; whether "carried" or "escalated" is a valid merge-time disposition or every row must end fixed or rejected; which branch name controls after a rename; how a clean round is represented; whether reviewer severity and verdict vocabularies are kept verbatim or normalised | PLAUSIBLE | New open item 8, with the two that have teeth separated from the ones that are formatting |

Verified clean by the round, and reported as such: all four of round 4's supersession
corrections are right — round 3's four-fixed/three-carried split, the corrected amendment
map, what `1c94a3c` did versus `bd81918`, and that both headers still restate. The
decision-7 normative prefix and counter-argument hash identically on `main` and HEAD, with
only the evidence paragraph differing. Prior round tables are unmodified, verified by
SHA-256 against their introducing commits. After the recorded supersessions, rounds 1–3's
dispositions match their diffs. Rule 9's historical claims all re-verified from git and
repository content, across every ref, 875 reflog entries, notes, 39 unreachable commits
and three unreachable blobs — including that one of the worked example's 102 rows carries
severity `bookkeeping` and is still a finding row, and that `a4f2970`'s body records an
off-by-one in its closing arithmetic corrected before commit. Decision 7 and rule 9 agree
on every operative requirement; rule 9's additions remain evidentiary. Rule 9, decision
7's corrected evidence, and both headers now agree. `AGENTS.md` is 162 lines.

**Gate note.** The reviewer's unit-test run was sandbox-blocked again: 709 tests
discovered, 558 `TemporaryDirectory()` errors, with `/private/tmp`, `/var/tmp`, `/tmp` and
the worktree all denied as `TMPDIR`. It correctly declined to report a pass and noted that
`scripts/` and `tests/` are byte-identical to `main`. Run in this worktree the suite is
`OK (skipped=1)` over 709 tests. The three validator gates passed in both environments.

### Open maintainer items after round 5 — superseding round 4's set in full

Round 4's items had the right shape and, in four cases, unsound content: a recommendation
whose stated reason was false, an option set missing whole families, and a counter-argument
that was a straw man. These replace them. Two are new. Nothing here is decided.

**1. Should a later round be forbidden from rewriting an earlier round's table — and if
so, what assures it?** Two separable questions; round 4 ran them together.
*Options.* (a) No rule, as decision 7 has it. (b) State the rule in rule 9 and decision 7,
with assurance by review — a reader diffs prior rounds against their introducing commits,
which every round of this branch has done. (c) (b) plus a mechanical check: `validate
--diff` ERRORs when an earlier round section of a review log changes. (d) (b) plus a
history-preserving merge, so the branch's own commits stay inspectable.
*Recommendation:* (c). A rule whose only assurance is that someone remembers to diff has
the same shape as the drafting silence rule 9 exists to end. And (c) governs the merged
snapshot whatever the merge strategy, which (d) does not — preserved history helps you
detect a rewrite afterwards, it does not prevent one before the merge.
*Counter-argument:* (c) would be the first time the engine's gate polices workbench
documents rather than product content, which is a real scope change to what
`scripts/validate.py` is for; and until it is built, (b) is what actually operates, so
ratifying (b) alone may be the honest step.

**2. The `/` → `-` flattening is not injective, and neither is the obvious repair.**
Demonstrated collisions: reused branch names; case and Unicode folding on this filesystem;
file/directory prefix conflicts, where valid branches `x` and `x.md/y` would need
`reviews/x.md` to be both a file and a directory; and percent-encoding only `/` collides
`docs/review` with a branch literally named `docs%2Freview`.
*Options.* (a) Keep the flat mapping and accept the collisions. (b) Percent-encode `%`
first and then every character outside `[a-z0-9._-]`, uppercase included, giving a total,
reversible, case-safe name — mechanical and unreadable. (c) Mirror the branch path under
`reviews/` — fails on prefix conflicts and reuse. (d) Name the log for the slice rather
than the branch, which is what `plans/<slice>-reviews.md` already does. (e) Name it by a
stable identifier — the branch's creation commit, or a hash of the full branch name — with
the human branch name recorded inside the log.
*Recommendation:* (d). It makes the two halves of decision 7 consistent instead of adding
an encoding scheme to one of them, and its failure mode — a human reusing a slice name —
is visible at the moment of choosing, where a normalization collision is silent.
*Counter-argument:* (d) reintroduces exactly the judgment decision 7 removed by deriving
the name mechanically, two people can name the same work differently, and it does not
solve reuse either — only (e) does, by including something no two branches share. If the
mapping must stay mechanical, (b) is the only total one, and its cost is that nobody can
read a directory listing.

**3. There is no terminal-record step, so the last verdict lands unreviewed.**
The worked example shows the risk is not theoretical: `a4f2970` added round 25 and the
closing totals unreviewed, and its own body records an off-by-one in that arithmetic
corrected before commit.
*Options.* (a) Exempt a final record-only commit, defined as a diff touching nothing
outside the review-log path. (b) Have the final round review the branch including its
pending record, with the verdict committed in the merge. (c) State in rule 9 that the
terminal record commit is unreviewed, and accept it. (d) A mechanical check that the
terminal commit touches only the log path and leaves earlier round sections unchanged —
item 1's option (c) doing double duty. (e) Record each verdict against the exact tree SHA
the reviewer examined, so a reader can verify what was reviewed even though the record
commit was not.
*Recommendation:* (e) with (d). Together they make the record auditable without asking
anyone to trust the builder's characterisation of their own commit.
*Counter-argument:* both are engineering rather than a rule, and until they exist (c) is
the only honest description of what happens today — it costs one sentence and claims
nothing false. Round 4's claim that (a) closes the loophole is withdrawn: a path scope
proves one path changed, not that what was appended is accurate, and it leaves open which
diff is authoritative, whether renames or a symlink replacement qualify, and whether
earlier rounds may be rewritten inside that path. Option (b) does not remove the
self-reference either — the merge commit still adds the verdict after the review; it moves
the unreviewed content into the merge.

**4. Should the contract live in one place?**
Round 4 said every drift this branch found was a header restating rule 9. That is false:
round 1 corrected rule 9's own historical count, and round 3 corrected decision 7's
evidence. Drift has appeared in all four sites.
*Options.* (a) Leave it distributed. (b) Cut both headers to pointers — which still leaves
rule 9 and decision 7 as two normative copies. (c) Make rule 9 the single normative text
and reduce decision 7 to the decision and its counter-argument, pointing at rule 9 for the
contract. (d) Move the contract to its own document that rule 9 and decision 7 both point
at.
*Recommendation:* (c). It is the only option that leaves one normative copy; (b) halves
the problem and calls it solved.
*Counter-argument:* (c) demotes an approved design decision to a pointer, which is a
source-of-truth change under rule 7 and precisely the kind of tidying a builder should not
reach for; and decision 7's evidence has value as the record of why the rule exists, which
a pointer would not carry.

**5. Must the terminal verdict be approving?**
Rule 9 requires every verdict committed and does not require the last to approve, while its
own "not just the final approve" presupposes that it does. The consequence is not just
reader ambiguity: a fully logged branch with unresolved major findings satisfies rule 9's
literal merge condition. Rule 3 does not say otherwise — it calls this a review gate and
says the maintainer lands the merge.
*Options.* (a) Leave rule 9 silent. (b) Require an approving terminal verdict. (c) Require
an approving terminal verdict unless the maintainer records an explicit override with
grounds in the log.
*Recommendation:* (c). It keeps the maintainer's authority, which is what (a) was
protecting, and closes the hole (a) leaves. The repository already has the case: the
32-round slice 2.1 was merged over a FIX-BEFORE-SHIP verdict, and that override survives
only in a design file, not in any review record.
*Counter-argument:* (c) adds a gate to a rule scoped to recordkeeping, and rule 3 plus the
commit bit may already mean it — in which case (c) writes down what is true and adds a
sentence someone must maintain.

**6. What counts as a round?**
The build record documents four Codex crashes mid-review. A crashed invocation is not
empty: it has an identity, a terminal status, and sometimes partial findings.
*Options.* (a) A round is an invocation that returned a verdict; aborted invocations are
noted but carry no row. (b) Every invocation gets a row, with "aborted, no verdict" as its
disposition. (c) Leave it undefined. (d) Distinguish attempt from round: log every launched
attempt with its task id and terminal status; a completed attempt becomes a numbered round,
a crashed one keeps whatever partial output it produced, and the retry is a new attempt.
*Recommendation:* (d). It is the only option under which a crash cannot be used to retire
an inconvenient partial review, and it costs one line per crash. Round 4 recommended (a),
whose own counter-argument admitted that risk.
*Counter-argument:* (d) records noise in the common case where a crash produced nothing,
and makes the log's numbering two-level where decision 7 imagined one.

**7. Should the reviewed revision be part of the required record?** (new)
Both logs record `Reviewed: <commit>` voluntarily. Neither rule 9 nor decision 7 asks for
it, so a compliant log could carry a verdict and a fix SHA without establishing which tree
was reviewed — which makes the amendment chain, and every terminal-record argument above,
unauditable.
*Options.* (a) Leave it voluntary. (b) Require it in rule 9. (c) Require it in rule 9 and
decision 7 together.
*Recommendation:* (c). A verdict with no revision cannot be checked against anything, and
adding it to rule 9 alone would put the two normative copies out of step — the drift item
4 is about.
*Counter-argument:* it adds to the inventory decision 7 deliberately fixed, so it is a
change to a locked decision rather than a clarification of it; and both logs already do it,
so the gap may never have been at risk.

**8. Five operational details rule 9 leaves to the builder.** (new)
Who may reject a finding with grounds; whether "carried" or "escalated" is a valid
merge-time disposition or every row must end fixed or rejected; which branch name controls
after a rename; how a clean round is represented; whether reviewer severity and verdict
vocabularies are kept verbatim or normalised.
*Options.* (a) Leave all five to the builder. (b) Settle all five in rule 9. (c) Settle the
two with teeth — who may reject, and whether a non-terminal disposition is legal at merge —
and leave the other three as formatting.
*Recommendation:* (c). "Rejected with grounds" is the one disposition that lets a builder
close a finding by disagreeing with it, so who may do that is where the record can be
quietly weakened; and this log currently has rows ending "carried to the maintainer",
which is neither fixed nor rejected, so whether that is a legal state at merge is
load-bearing for this very branch.
*Counter-argument:* settling two of a list of five looks arbitrary, and the other three
have teeth too — a normalised severity vocabulary can soften a reviewer's grade, and an
undefined clean-round representation lets an approving round be recorded in whatever form
flatters it.
