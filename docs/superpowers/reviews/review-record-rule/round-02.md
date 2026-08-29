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
