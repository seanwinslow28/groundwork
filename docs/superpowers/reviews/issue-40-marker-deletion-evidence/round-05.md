# Entry 05 — Codex review round

**Reviewed revision:** `095ca91`
**Verdict, in the reviewer's words:** "The round is not clean: 1 Major classifier defect and
2 Minor defects."
**Brief:** audit round 04's repairs for over-correction, then the standing questions. The
brief also asked the reviewer to scrutinise entry 04's rejection and to say so if it was
wrong — the one place re-raising a disposed finding was explicitly invited.

Still in the finding-class entry 01 named, so **rule 11 does not fire**.

## Findings

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Major | `isfile` resolves through a **symlinked parent directory**, which `_walk_working_tree` never descends. So a marker under one read as present to this check while being invisible to every other pass, and the deletion went unreported. | **Fixed** — `_reachable_regular_file` |
| 2 | Minor | `_base_markers` passed candidates as **pathspecs**: a real path beginning with a colon is read as pathspec magic and git exits 128, and a large enough list exceeds the argv limit. Either made the helper return empty for EVERY candidate, so the caller ERRORed that the base lacked files it holds. | **Fixed** — no pathspec at all |
| 3 | Minor | The README still said "three statements" about `--diff-filter=A` with "the first two" wrong, after entry 04 had made it four and three; two test docstrings still explained themselves through the removed flag. | **Fixed** |

## Finding 1 is the third time a repair reopened the escape

Worth stating plainly. `isfile` was round 03's fix for `lexists`, and round 04 made it the
sole presence proof after removing the name-membership check. Both changes were right about
the state they were for and wrong about this one: `os.walk` runs with `followlinks=False`, so
a marker beneath a symlinked directory is not discovered by `_pin_dirs`, the governed root it
would mark does not exist as far as the validator is concerned, and answering "present" for it
suppressed the very finding this slice adds.

`_reachable_regular_file` judges presence the way the scan judges it: **no ancestor component
may be a symlink**. The final component still may be — a symlink to a real pin file is listed
by `os.walk` in `filenames` and read like any other file. Both edges are pinned, and the
mutation forbidding a symlink at the final component is caught too, so the rule is not
quietly stricter than stated.

## Finding 2 was found by the builder in parallel

While the round was running, the same defect was found here by probing the pathspec question
the brief had raised — `:(exclude)/groundwork.pin` makes `ls-tree` exit 128, and the helper's
empty-on-failure return means "the base holds no marker". The round then reported it with the
argv half as well, which had not been found here. The fix covers both: **there is no pathspec
now.** One unfiltered `ls-tree -r -z` has nothing to misread and no argv to overflow, and
`_git_diff_context` already pays that cost once so the order of the work is unchanged.

`--literal-pathspecs` was measured and does fix the magic half. It was not taken, because it
leaves the argv limit standing and keeps a pathspec surface that has now produced one defect.

## The entry 04 rejection was independently confirmed

The brief invited the reviewer to overturn it. It did not, and it supplied a mechanism the
rejection had only inferred from measurement: git's `set_separate()` sets `simplify_history =
0`, which is why separate merge diffs already expose the net-zero side branch and why
`--full-history` changed nothing. The rejection stands, now on a documented cause rather than
two measurements alone.

## Verification

Outside the sandbox: **893 tests, OK, skipped=1**; `validate.py .` 0 errors and 8 warnings
(the baseline entry 01 declared); `validate.py demo` 0 errors and 2 warnings; `--diff main`
exit 0.

## Mutations

Three, all caught, and the middle one is at the over-refusing edge rather than the intuitive
one: reverting to `isfile` alone; forbidding a symlink at the final component as well as the
ancestors; and restoring a pathspec to the `ls-tree` call.
