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
