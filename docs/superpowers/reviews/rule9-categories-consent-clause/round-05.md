## Round 05 — 2026-08-29, task-mtesv6kw-qbhh65, verdict: not clean — 2 Minor Standards, 2 Minor Spec, "two unique Minor defects"

Reviewed: `933f1fc` (round 4's repair and `round-04.md`). The round says *"Not clean: two
unique Minor defects remain, both in the review record. The product amendments are
correct."* Its Spec pass found the same two defects as its Standards pass, and says so.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | Minor | `round-04.md:16` cites basename references at `build-sessions.md` lines 40, 45, 61 and 81 without naming a revision. At `933f1fc` line 81 is blank and that reference sits at line 82; the numbers were correct at `c27257e`, the revision round 4 reviewed | CONFIRMED | **Corrected here**, `round-04.md` being immutable. Verified in this worktree: lines 40, 45 and 61 are byte-identical between `c27257e` and `933f1fc`; the file grew from 105 lines to 106; round 4's own fix is what moved the fourth reference. **Read `round-04.md`'s four numbers as at `c27257e`. From `933f1fc` on they are 40, 45, 61 and 82** |
| 2 | Minor | `README.md:37` announces "Two corrections to earlier entries" above three correction bullets, one of which corrects two claims | CONFIRMED | Fixed in the README, which rule 9 makes the mutable half of the record. The heading no longer carries a count, so it cannot drift again. Two further stale numbers found while fixing it and repaired in the same edit: the open-findings line said "rounds 1–3" after round 4 had run, and it is now written without a round range |

Reported clean by the round, and recorded as its claims: `round-04.md` records all five of
round 4's rows as `Minor` with dispositions and does not guess the merged pair; before
`933f1fc` `build-sessions.md` carried no Markdown links and now carries exactly two; both
resolve under `check_links` and score 3.952797 and 3.714662 against the 4.0 threshold, while
the exact `round-12.md` form scores 4.076079 and would WARN; `round-12.md` holds decision 5a
with its grounds and counter-argument and `round-11.md` holds the options; naming
`round-12.md` in prose while linking its directory is unambiguous and not a defect; the
README's table and fix SHAs are otherwise accurate and no disposition changed; rounds 1–3 are
byte-identical to their committed states; rule 9 implements decision 5a exactly and preserves
prior text; the `CONTEXT.md` clause matches the generation exemption without importing the
v1→v2 bootstrap.

On merging, the round says these are record-only residuals a maintainer could accept under
rule 9, that the clean course is to correct both and commit this entry first, and that the
record is sufficient for a newcomer to reconstruct what was found and done.

**Gates**, reproduced by the round and verified outside the sandbox by the builder at
`933f1fc` and again after this entry's fix: engine `0 error(s), 8 warning(s)`; `demo`
`0 error(s), 3 warning(s)`; `--diff main` exit 0; `python3 -m unittest discover -s tests -q`
→ Ran 824 tests, OK (skipped=1).
