## Round 15 — 2026-08-29, task-mtegxi4p-0vmryz, verdict: does not approve (1 finding)

Reviewed: `a3740d0` (round 14's fixes). **No major findings.** One minor, CONFIRMED, fixed
in the following commit. The round stated plainly what stood between the branch and rule 9's
merge condition, and this was all of it.

**Fix commit for round 14: `a3740d0`.**

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | minor | The collision suffix triggers only when "a directory of that name already exists", but a valid branch named `docs/spec-roles-accountable-unit.md` maps onto the existing **ordinary file** `docs/superpowers/reviews/spec-roles-accountable-unit.md` — the grandfathered worked example. The occupant is a file, so the rule does not fire, and the builder must guess between suffixing, moving the file, and failing. The open-ended `-2`, `-3` wording closed the numeric bound, not the path-type question, and it was not in the open-findings list | CONFIRMED | Fixed in the rule: the trigger is now "if that path is occupied in the branch's merge target — by a directory or by an ordinary file". The example is real, not hypothetical: that filename exists in this repository today |

Verified clean by the round, and reported as such — this is the fullest audit the branch has
had, and everything else in it passed.

**The accounting, independently reconstructed.** Rounds 1–6, 8–12 and 14 are the twelve
review rounds; rounds 7 and 13 are correctly excluded as a maintainer-decision entry and a
record correction. Every entry header matches its finding table, and the per-round counts
are 3, 5, 7, 12, 9, 11, 9, 9, 6, 5, 3, 5 — **84 findings across twelve review rounds**. Each
round's fix commit has that round's reviewed revision as its parent. The seventeen
historical escalated rows resolve to **14 fixed** (r1.3, r2.3, r2.5, r3.3, r3.4, r3.7, r4.2,
r4.4–r4.8, r5.8, r6.9), **3 open** (r5.9, r6.11, r8.9) and none rejected, with three further
open rows correctly recorded — r10.6 and r11.5 reclassified by round 13, and r12.2. Across
all 84 rows the supersession chain leaves **78 fixed, 6 open, none rejected**, and nothing
under "standing", "carried" or any other vocabulary rule 9 does not define.

**Every disclosed guess is disclosed.** The round enumerated twelve — verdict vocabulary and
what counts as approving; partial output from an aborted invocation; numbering after
`round-99`; the grandfathering boundary; branch identity after a rename; selecting or
changing the merge target; who performs a merge-time rename; fix mapping when fixes span
commits; the clean-round form; directory rename versus entry immutability; plan selection
after a revert, rename or deletion; and adequate rejection grounds as the open maintainer
item — and found all of them present in the README. The ordinary-file collision above was
the only required-but-undisclosed guess in the rule.

**Everything else verified from source:** decision 7's normative block and counter-argument
byte-identical to `main` (`819c15b4…`, `665a3e29…`); the worked example's 25 rounds, 102
finding rows, one approving verdict and 24 backfilled fix commits each correctly parented;
`df6df21`'s sixteen-plus-nine split, the thirteen numbered fix commits, r3/r9/r16 absent
with r16 surviving in the merge, and `3b5bb93` the unnumbered self-check; no r3/r9 artifact
in any ref, reflog, note or unreachable object; exactly two rejections in the session, both
on the sibling branch, both out of scope with follow-up named; and no contradiction among
rule 3, decision 7 and its amendment, the grandfathered example, this branch's entries, or
the sibling at `d883bb7`. The separate standards pass was clean beyond the disclosed rule-1
departure. `AGENTS.md` is 162 lines, `build-sessions.md` 89.

**Gate note.** The reviewer's unit-test run was sandbox-blocked — 709 discovered, 558
`TemporaryDirectory()` errors, zero assertion failures — and it correctly declined to let
that affect the verdict, noting `scripts/` and `tests/` are byte-identical to `main`. Run in
this worktree the suite is `OK (skipped=1)` over 709 tests. The three validator gates passed
in both environments.

**On the merge question**, asked directly: *"Once that wording is fixed or the issue is
recorded as open, and this round-15 verdict is committed, the branch meets Rule 9's literal
merge condition."* The wording is fixed in the following commit and this verdict is
committed with it.
