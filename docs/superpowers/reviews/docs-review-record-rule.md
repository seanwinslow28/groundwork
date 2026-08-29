# Codex review record — branch `docs/review-record-rule`

> This is the durable per-round review log rule 9 requires
> ([../../agents/build-sessions.md](../../agents/build-sessions.md)), kept on the branch
> that installs rule 9. Rule 9 is the normative text — where the log lives, what each
> round must carry, and when it must be committed. **This log's own addition, which rule 9
> does not require:** each finding is
> marked CONFIRMED (the reviewer verified it against a source) or PLAUSIBLE (reasoned,
> unverified). Whether that becomes part of rule 9 is a maintainer decision, not one taken
> here.
>
> **Naming the fix commit.** A round's dispositions are written before the commit that
> carries them exists, so they say "the following commit". The hash is recorded one round
> later: each round's opening line names the state it reviewed, which is the previous
> round's fix commit. The last round has no successor, and that gap is an open maintainer
> item below.

## Round 1 — 2026-08-29, task-mte9sxcc-x6n5gt, verdict: does not approve (3 findings)

Reviewed: commit `57babf3` (rule 9, the rule-3 pointer, and this log's opening header).
All 3 accepted; findings 1 and 2 fixed in the following commit, finding 3 recorded and
carried to the maintainer rather than changed.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | This log's header made CONFIRMED/PLAUSIBLE status a merge requirement, which neither rule 9 nor decision 7 imposes — two log headers agreeing with each other while diverging from the normative text, the drift class rule 9 exists to catch | CONFIRMED | Fixed: the header stops restating rule 9's inventory, points at rule 9 as the normative text, and names CONFIRMED/PLAUSIBLE as this log's own addition with the maintainer's call reserved. The worked example's header carries the same wording and is left as written — it predates rule 9 and is self-descriptive — but is flagged to the maintainer |
| 2 | minor | "Two of the sixteen — r3 and r9 — left no commit" undercounts: r16 also left none, and its approving verdict plus both round counts survive in `df6df21`, so "what survives is what its fix commits chose to quote" was overbroad | CONFIRMED | Fixed: three of the sixteen left no numbered commit; r16's verdict survives in the merge, r3 and r9 left nothing anywhere; the survival claim now credits the merge alongside the fix commits, and the no-complete-output claim is scoped to the sixteen. Verified independently: `3b5bb93`, which sits between r8 and r10, is an unnumbered self-check, not an r9 fix |
| 3 | minor | "A later round amends an earlier row by superseding it, never by rewriting the earlier round's table" is a fair reading of decision 7's "appended per round" and matches the worked example's history, but is not logically forced by it — a possible unapproved widening of a locked decision | PLAUSIBLE | Not changed; carried to the maintainer for express ratification. Removing it would itself be a unilateral choice, and a record that may be rewritten is not durable — so the stricter reading stands pending that ratification, flagged here and in the session report |

Verified clean by the round, and reported as such: the `df6df21` round counts and their
attribution to the rule-8 session (not the roles session, which also ran 25); no content
for r3 or r9 anywhere in the tree, all refs, reflogs, notes, or unreachable objects, and
no complete raw output for any of the sixteen; the two honesty-plan fragments verbatim;
`18fa805`'s "seventh instance"; "four factual defects" accurate against the honesty
plan's five total (defect 1 is a mechanically impossible verification command, defects
2–5 are the factual four); the worked example's 25 round sections, 102 finding rows, 102
non-empty dispositions, one approving verdict. Placement upheld: the separate "added
during build" heading is truthful, the rule-3 pointer does not duplicate, and "Where the
plan lives" should not gain the reviews path. Gate confirmed at `57babf3`: `validate.py .`
0 errors / 7 warnings, `--diff main` exit 0, `demo` 0 errors / 2 warnings, 709 tests
OK (skipped=1).

## Round 2 — 2026-08-29, task-mtea6il3-hmoxpo, verdict: does not approve (5 findings)

Reviewed: `edc3c26` (rule 9 plus the round-1 fixes). All 5 accepted; four fixed in the
following commit, one carried to the maintainer. Round-1 rows 1 and 3 are **amended** by
rows 1 and 2 below.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Leaving the never-rewrite clause in is not neutral: omitting it preserves the locked decision's silence, adding it chooses a correction policy the maintainer has not approved. Flagging is adequate escalation but does not make the branch mergeable | CONFIRMED | Fixed by removal. The asymmetry is right and round 1's reasoning ("removing is equally unilateral") was wrong — there is no symmetry between restoring silence and legislating. Rule 9 now says only "appended per round, on the branch". The question goes to the maintainer with the argument for the clause intact; if ratified it returns to rule 9 and to decision 7 together. Amends round-1 row 3 |
| 2 | major | The round-1 parallel-site fix was incomplete: the already-merged worked example's header still attributes the CONFIRMED/PLAUSIBLE merge requirement to decision 7, which does not state it — and rule 9 now names that file as its worked example, so "predates rule 9" and "self-descriptive" cure neither the false attribution nor the misleading template | CONFIRMED | Fixed: that header now separates what decision 7 requires from what the log adds, and says so in place, naming this branch and round. Its round tables are untouched. Amends round-1 row 1, whose "fixed" was true of this branch's header only |
| 3 | major | Rule 9 has no terminal-record step. Rule 3 puts review at session end, rule 9 puts the final verdict in the repository before merge — so the last verdict lands in a commit after the reviewed state, which then gets no review. The worked example shows it: round 25 reviewed `acd729c`, `a4f2970` added the approval row and closing totals and was never reviewed before merge `c7664d4`. The same gap is why dispositions say "the following commit" rather than the rule's "fixed in commit X" | CONFIRMED | Fixed: rule 9 now states the consequence — the last round's verdict lands in a commit made after the state it reviewed, that commit carries the record and no content change so it needs no round of its own, and a disposition that cannot name a not-yet-existing hash names the commit that followed. Stated as a mechanical consequence of decision 7, not a new policy |
| 4 | minor | The rewritten header restated rule 9's plan-less path, slash normalization and on-branch placement while claiming "this header does not restate it", and opened on a noun fragment | CONFIRMED | Fixed: the header restates none of rule 9 and opens on a full sentence |
| 5 | minor | The `/` → `-` flattening is collision-prone — `docs/a-b` and `docs-a/b` both normalize to `docs-a-b.md`, as does a reused branch name; sequential work can conflate records and concurrent branches can produce an add/add conflict | CONFIRMED | **Not changed; carried to the maintainer.** The normalization is decision 7's own text, so changing it is a locked-decision edit. Rule 7 allows reopening on new evidence and this is new concrete evidence, but the reopening is the maintainer's |

Verified clean by the round, and reported as such: the corrected "three of the sixteen" is
exactly right — the reviewer enumerated all thirteen numbered `fix(build): Codex r…`
commits, confirmed r3, r9 and r16 lack one, and confirmed `3b5bb93` is the unnumbered
self-check; `df6df21` carries all four claims (sixteen rounds, r16 approving, nine on the
correction, that correction approved at round 9), and the twenty-five belong to the rule-8
session, not the roles session which independently also ran twenty-five. A search of all
refs, reflogs, notes and `git fsck --unreachable` objects — 39 unreachable commits, three
unreachable blobs — found no r3 or r9 content, and no complete output for any of the
sixteen. Round-1 row 2's description of `edc3c26` is accurate. The honesty-plan
quotations, `18fa805`'s "seventh instance", the four-of-five defect count, and the worked
example's 25 sections / 102 rows / 102 dispositions / one approving verdict all hold.
`AGENTS.md` is 162 lines against its 200-line limit. Gate at `edc3c26`: `validate.py .` 0
errors / 7 warnings, `--diff main` exit 0, `demo` 0 errors / 2 warnings, 709 tests
OK (skipped=1).

### Open maintainer items from this round

1. **The never-rewrite clause** (row 1). Removed pending ratification. The case for it:
   a record that may be rewritten is not durable, and the worked example's own practice
   is append-and-supersede. The case against: decision 7 says only "appended per round",
   and a builder choosing a correction policy for a locked decision is the failure this
   session was told to expect. Ratifying it means adding it to rule 9 and to decision 7
   together.
2. **The `/` → `-` collision** (row 5). `docs/a-b` and `docs-a/b` flatten to the same
   filename, and so does a reused branch name. Decision 7's normalization as written
   cannot guarantee one file per plan-less branch.

## Round 3 — 2026-08-29, task-mteapn8r-iwjbj6, verdict: does not approve (7 findings)

Reviewed: `1c94a3c` (the round-2 fixes). All 7 accepted; three fixed in the following
commit, four carried to the maintainer or recorded. **Round 2's terminal-record fix was
itself unratified policy** — the second time on this branch that a fix legislated where it
should have asked. Round-2 rows 3, 4 and 5 are **amended** by rows 1, 2, 4 and 5 below.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The terminal-record exemption is new unratified policy with a review-bypass loophole: "carries the record and no content change" is neither defined nor checked, the record is itself repository content that can be wrong, and nothing limits the commit's diff to the log path — so a mixed commit can be characterised as terminal and escape review. It is a choice among possible terminal protocols, not a mechanical consequence of decision 7, and rule 5 owns it | CONFIRMED | Fixed by removal. Rule 9 says only "appended per round, on the branch, so the merge carries the record". Round 2's finding — that rule 9 has no terminal-record step — therefore stands **unfixed and escalated**, open item 3. Amends round-2 row 3, whose "fixed" claimed more than `1c94a3c` delivered |
| 2 | major | The terminal sentence waived the locked "fixed in commit X" format by permitting "the commit that followed", so rule 9 mandated and waived the same format; and this log practises the weaker "the following commit" without an identifier | CONFIRMED | Fixed for rule 9 by the same removal. For the log, the hash is now made traceable without changing rule 9: a header note records that each round's opening line names the state it reviewed, which is the previous round's fix commit, so "the following commit" resolves one round later. The last round has no successor — that is open item 3 |
| 3 | major | Removing the never-rewrite clause leaves durability under-specified: nothing forbids a later commit appending a round while rewriting an earlier table, the append-and-supersede rules elsewhere bind org memory and interview layers only, and git history mitigates it only if branch history survives the merge — which rule 9 does not require | PLAUSIBLE | Open item 1 extended with the git-history and squash-merge nuance. Not otherwise changed: legislating here is what rows 1 and 2 just punished |
| 4 | major | The plan-less path mapping is non-injective beyond the case already recorded: `docs/a-b`, `docs/a/b` and `docs-a/b` can all normalise alike, a reused branch name conflates records, and case-folding or Unicode-normalising filesystems add more. Severity is major, not minor, because it can merge unrelated audit histories or force add/add conflicts | CONFIRMED | Open item 2 extended with the additional collision classes and upgraded to major. It is a defect in decision 7's own text and needs an explicit reopening, which is the maintainer's. Amends round-2 row 5's severity |
| 5 | minor | Decision 7's own evidence is now less accurate than the rule implementing it: it names r3 and r9 as the rounds that left no commit, without r16 — the same parallel-site incompleteness round 2 corrected in the worked-example header | CONFIRMED | Fixed in place, the way the worked-example header was: the evidence paragraph now says two rounds are unrecoverable and notes that the approving r16 left no numbered commit either but is carried by `df6df21`, with the correction attributed to this branch and round. **The decision itself is untouched** — this corrects supporting evidence, not a locked choice |
| 6 | minor | The header still restated rule 9's obligation and on-branch placement immediately before claiming "this header does not restate any of it" | CONFIRMED | Fixed by dropping the claim rather than chasing it: the header states what rule 9 governs and stops asserting non-restatement. Amends round-2 row 4, whose fix was incomplete |
| 7 | minor | The contract is spread across decision 7, rule 9, two headers and historical session text, and that repetition is producing exactly the shotgun-edit drift the rule exists to prevent — round 1 missed the worked header, round 2 missed decision 7's evidence and left a false non-restatement claim | PLAUSIBLE | Recorded, not legislated. The mitigation applied so far is that headers point rather than restate (rows 6 and round-2 row 4). Whether the surface should be consolidated is open item 4 |

Verified clean by the round, and reported as such: the never-rewrite removal is complete
in normative text and both headers, with the clause surviving only as history in the round
tables and commit messages, which is correct. The worked-example header amendment is
accurate — decision 7 does not require CONFIRMED/PLAUSIBLE, no rule forbids correcting a
merged log's header, and its round tables are **byte-identical to `main`**. Every rule-9
historical claim re-verified from scratch: `df6df21`'s four claims; exactly thirteen
numbered `fix(build): Codex r…` commits (r1, r2, r4–r8, r10–r15) so r3, r9 and r16 lack
one, with `3b5bb93` the unnumbered self-check; a full object-database inspection — 39
unreachable commits, three unreachable blobs, no notes — finding no r3/r9 artifact and no
complete output for any of the sixteen; both honesty-plan quotations verbatim;
`18fa805`'s "seventh instance"; five defects of which #1 is the impossible verification
instruction and #2–#5 the four factual ones; the worked log's 25 sections, 102 rows, 102
non-empty dispositions, one approving verdict; and `a4f2970` containing only the round-25
log and totals, its parent the reviewed `acd729c`. `AGENTS.md` is 162 lines against its
200-line limit. Gate at `1c94a3c`: `validate.py .` 0 errors / 7 warnings, `--diff main`
exit 0, `demo` 0 errors / 2 warnings, 709 tests OK (skipped=1).

### Open maintainer items after this round

1. **The never-rewrite clause** (round 2 row 1, extended by row 3). Removed pending
   ratification. For: a record that may be rewritten is not durable, and both logs already
   practise append-and-supersede. Against: decision 7 says only "appended per round", and
   a builder choosing a correction policy for a locked decision is this session's named
   failure mode. Newly added: git history mitigates rewriting only if branch history
   survives the merge, and rule 9 mandates no history-preserving merge strategy — so
   ratification should say whether that is part of the guarantee.
2. **The `/` → `-` collision** (round 2 row 5, extended by row 4, now major). `docs/a-b`,
   `docs/a/b` and `docs-a/b` can all normalise to one filename; a reused branch name
   conflates records; case-folding and Unicode-normalising filesystems add more. Decision
   7's normalization cannot guarantee one file per plan-less branch, so it needs an
   explicit reopening.
3. **The terminal-record step** (round 2 row 3, reopened by row 1). Rule 3 puts review at
   session end and rule 9 puts the final verdict in the repository before merge, so the
   last verdict lands in a commit after the reviewed state that gets no round of its own —
   visible in the worked example, where `a4f2970` added the approval row and closing
   totals and was never reviewed before merge `c7664d4`. The same gap is why dispositions
   say "the following commit" rather than the locked "fixed in commit X". Any exemption
   needs a definition of record-only that a reader can check, or the protocol needs a
   different shape.
4. **Whether the contract's surface should be consolidated** (row 7). It currently lives
   in decision 7, rule 9, and every log header, and three rounds have each found drift
   between them.
