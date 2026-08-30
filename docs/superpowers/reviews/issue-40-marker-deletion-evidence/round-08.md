# Entry 08 — Codex review round

**Reviewed revision:** `381c187`
**Verdict, in the reviewer's words:** "**Land after three documentation/record corrections. No
behavior change is required.**" Priority 3, the classifier question: "**None found.**"

**This round produced no findings in the finding-class entry 01 named, so RULE 11 FIRES** and
the slice goes to the maintainer for a merge decision rather than continuing.

## What the round was asked to do

It was briefed as the last planned round, and asked for a direct land / do-not-land
recommendation rather than only a defect list. Its first priority was round 07's fail-closed
change, which was a real behaviour change and the least-reviewed code on the branch: two git
reads that previously returned an empty set on failure now return None, and
`diff_base_findings` turns None into an ERROR and returns early.

## Priority 1 — the fail-closed change, four probes, no defect found

| Probe | Result |
|---|---|
| Does the early `return findings` drop findings already accumulated? | **No.** It returns the existing list, preserving the ancestry WARN, the unsupported-root ERRORs and the interview-manifest ERRORs. Skipping only the marker loop is correct, because its evidence is what is unavailable. |
| Is there a state where a git failure should NOT be an ERROR? | **No.** An empty repository cannot pass base-ref verification; a commit whose tree cannot be read fails earlier in `_git_diff_context`; and partial `git log` output cannot be treated as complete evidence, so ERROR is right even when stdout looks usable. |
| Is the unborn-HEAD carve-out right and reachable? | **Yes and yes, and it is not silent** — ancestry WARNs. With no HEAD commit there is no `base..HEAD` range from which a deletion could be asserted. |
| Can one run produce both new ERRORs, and is their order sensible? | **No, and yes.** The history read runs first; if it fails, `_base_markers` is never called. |

The first of those was also checked here independently before the round returned, on a fixture
where an unsupported-root ERROR and an injected `git log` failure coincide: both findings
appear. The two measurements agree.

## Priority 3 — classifier correctness: none found

The reviewer lists what it checked: marker modes, base and working-tree presence, scope
filtering, unreadable subtrees, symlink ancestors, divergent and unborn HEAD, failed and
partial git reads, no-candidate behaviour, and both failure-return paths.

## Findings

All three are about the record, and all three are corrected. None required a code change.

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Minor | "The last fail-open in this mechanism" is too broad — entry 07 records the open `GIT_DIR` fail-open in the same entry. | **Fixed** — corrected here and in the test docstring |
| 2 | Minor | Entry 07's mutation section says "Four, all caught" while naming three distinct mutations. | **Fixed** — corrected here |
| 3 | Nit | `docs/known-limitations.md` said "Of those four" over a list that has five bullets. | **Fixed** — "Of the first four" |

## Correcting entry 07, which is immutable

**Finding 1.** Entry 07 is headed "Finding 1 was the last fail-open in this mechanism", and
the same entry records finding 2 — `GIT_DIR` and `GIT_WORK_TREE` inheritance — as an open
fail-open. Both cannot be true. **The accurate statement: round 07 finding 1 closed the last
fail-open in how the git reads' RESULTS were handled. The mechanism still has an open
fail-open in which repository those reads address, disclosed as issue #43.** The test
docstring that repeated the claim is corrected in this round's fix commit; the entry stands as
written with this correction against it.

This is the seventh overclaim of its kind on this branch, and the shape is by now familiar: a
sentence written to describe a real fix reached one word further than the fix did.

**Finding 2.** Entry 07's mutation section says "Four, all caught". The accurate account:
**three distinct mutations, four executions.** The three are reverting the history walk's
failure return, reverting the base listing's failure return, and un-scrubbing
`GIT_GLOB_PATHSPECS`. The base-listing one was executed twice — it survived the first time
because its regression test monkeypatched `_base_markers`, and was rerun and caught after the
test was strengthened to assert the helper's own return. Entry 07 described that history
correctly in prose and then summed it as four mutations, which no reader could reconcile with
the three it names.

## Verification

Outside the sandbox, after these corrections: **898 tests, OK, skipped=1**; `validate.py .`
0 errors and 8 warnings (the baseline entry 01 declared); `validate.py demo` 0 errors and
2 warnings; `--diff main` exit 0.

The reviewer independently ran both validator gates and `git diff --check main...HEAD` at
`381c187` and reports the same numbers. Its sandbox could not create temporary directories, so
it did not run the unit tests — the disclosed environmental limit.

## Mutations

None. No code changed in this round's fix commit.
