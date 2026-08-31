# Entry 07 — Codex review round

**Reviewed revision:** `f5861f6`
**Verdict:** not clean — 2 Major and 1 Minor. The reviewer gave no summary sentence; the
severity words below are its own.

Still in the finding-class entry 01 named, so **rule 11 does not fire**.

## Findings

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Major | Every nonzero `git log` exit was read as "no candidates", so a FAILED git command was indistinguishable from a repository that never carried a marker and the run went green. Reachable without touching the repository: an injected `diff.orderFile` pointing at a missing path makes git exit 128. | **Fixed** — both reads fail closed |
| 2 | Major | The validator inherits `GIT_DIR` and `GIT_WORK_TREE`, so a caller can supply one repository's working tree and another's history. | **Open** — documented, issue #43 |
| 3 | Minor | Round 06's record and code comment called `GIT_GLOB_PATHSPECS` harmless. It is not: with it set, `*` stops crossing `/`, so a nested marker is missed. | **Fixed** — the reasoning, not the code |

## Finding 1 was the last fail-open in this mechanism

Two git reads could fail, and both returned an empty set on failure. An empty set is a real
answer — "no marker" — so each failure was laundered into evidence:

- `_markers_added_since_base` returning empty meant "nothing was ever added", and the run went
  **silent**. That is issue #40's own escape, reachable from the environment.
- `_base_markers` returning empty meant "the base holds no marker", and the caller then
  reported **every candidate as deleted** — fabricated evidence rather than an error. Round 05
  named this shape without fixing it; this is where it is fixed.

Both now return `None` for "could not read" and a set otherwise, and the caller emits one
ERROR naming what failed. An unborn or unresolvable HEAD still returns an empty set, because
that is not a failure: there is no `base..HEAD` range to ask about, the ancestry check already
WARNs, and an ERROR there would invent evidence.

## Finding 3 corrects entry 06's reasoning, not its code

Entry 06 scrubbed four pathspec environment variables and recorded two of them as harmless
tidiness. **`GIT_GLOB_PATHSPECS` is not harmless.** Measured here on the reviewer's shape:

| | `git log` raw output |
|---|---|
| unset | `:000000 100644 … A` `nested/groundwork.pin` |
| `GIT_GLOB_PATHSPECS=1` | *empty* |

With it set, `*` stops crossing `/`, so `*groundwork.pin` no longer matches a marker in a
subdirectory. The scrub was right for a reason the record got wrong. `GIT_ICASE_PATHSPECS`
remains tidiness — it only widens git's preliminary matching and the exact basename check
settles the verdict — and the code comment now says which is which. Entry 06 is immutable, so
this entry carries the correction.

## Finding 2, and what was measured versus what was inferred

**Measured**, against `f5861f6`, with a decoy repository sharing the base commit:

| Environment | `diff_base_findings` |
|---|---|
| unset | `['groundwork.pin']` |
| `GIT_DIR=<decoy>/.git` | `[]` |

**Inferred, and stated as inference:** no git call in the validator controls its inherited
environment beyond the pathspec variables, so `_git_diff_context`, `_git_show` and
`_base_is_ancestor` are exposed to the same redirection on `main`. **A pre-#40 pass changing
its verdict this way was NOT demonstrated.** Two attempts failed to produce one — with a decoy
lacking the base ref the run fails closed, and with a decoy sharing the base the blast-radius
pass still reported correctly. The claim is therefore structural, and issue #43 says so rather
than asserting a flipped verdict nobody has shown.

**Decided by the maintainer 2026-08-30: documented, not fixed.** Scrubbing the variables in
this slice's two calls alone was refused because the marker walk would then read the real
repository while the base listing and ancestry check still read whatever `GIT_DIR` names — two
repositories behind one verdict, which is the argument that decided issue #42 the other way.
The coherent fix is one environment policy across every git invocation, which rule 10 routes
to an issue.

**The counter-argument, recorded:** unlike a replace ref, `GIT_DIR` is set routinely by CI
harnesses, git hooks and wrapper scripts, so this is reachable **by accident** in a way the
other disclosed limits are not. That is the strongest case for fixing rather than documenting,
and it is why #43 exists rather than a single line in the limitations file.

## What this session probed independently

Before the round returned, the `GIT_CONFIG_COUNT` injection class was tested here — it is the
same shape as round 06's Major and round 06 had not looked at it. Injected `log.diffMerges`,
`log.showRoot`, `core.quotePath`, `diff.renames` and `log.follow` all left the verdict
unchanged, because the explicit flags win over configuration. The reviewer then found the one
injection that is NOT about a flag being overridden: config that makes `git log` **fail**,
which no flag can defend against. Probing the class and missing the case inside it is worth
recording.

## Verification

Outside the sandbox: **898 tests, OK, skipped=1**; `validate.py .` 0 errors and 8 warnings
(the baseline entry 01 declared); `validate.py demo` 0 errors and 2 warnings; `--diff main`
exit 0.

The reviewer ran the 56 focused `TestDiffBaseContract` tests and both validator gates, and did
not rerun the full suite, relying on the supplied external result for this revision.

## Mutations

Four, all caught. Three at first: restoring the empty-set-on-failure return in each of the
two reads, and un-scrubbing `GIT_GLOB_PATHSPECS`. **The base-listing one survived**, because
the test for it monkeypatched `_base_markers` to return None and so pinned the CALLER's
handling while leaving the helper's own failure return untested — the exact conflation the
finding was about, reproduced in its own regression test. The test now asserts
`_base_markers(d, "no-such-ref-at-all") is None` directly, and the mutation is caught.
