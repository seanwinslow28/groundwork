# Entry 06 — Codex review round

**Reviewed revision:** `0d9fc74`
**Verdict, in the reviewer's words:** "Round 06 is not clean: 1 Major classifier defect and 2
Minor defects."

Still in the finding-class entry 01 named, so **rule 11 does not fire**.

## Findings

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Major | `GIT_LITERAL_PATHSPECS` and `GIT_NOGLOB_PATHSPECS` turn the walk's wildcard pathspecs literal, so it matched nothing and the run returned to silence. Settable from the shell, without touching the repository. | **Fixed** — the pathspec environment is scrubbed |
| 2 | Minor | `_base_markers` listed the whole base tree even with no candidates — an unconditional second full-tree traversal on every diff run. | **Fixed** — short-circuited |
| 3 | Minor | Prose and record: the caller comment still said `isfile` "ALONE" and called `lexists` "the whole answer"; it said "Three ways" over four bullets; the rule map said the ERROR requires "no regular file"; a doubled word in `docs/known-limitations.md`; and the README's corrections section carried neither the unreadable-tree narrowing nor the presence-proof supersession. | **Fixed** |

## Finding 1 is a miss, not a new edge

Round 05 removed the pathspec surface from `_base_markers` because a colon-prefixed path made
git exit 128 and the helper's empty return meant "the base holds no marker". **The sibling
`git log` call still used wildcard pathspecs, and was not looked at.** Finding 1 is that
oversight coming back in a different form: not a malformed path, but an environment variable
that reinterprets every pathspec.

Reproduced here before fixing, and again after:

| Environment | Before | After |
|---|---|---|
| normal | `['groundwork.pin']` | `['groundwork.pin']` |
| `GIT_LITERAL_PATHSPECS=1` | `[]` | `['groundwork.pin']` |
| `GIT_NOGLOB_PATHSPECS=1` | `[]` | `['groundwork.pin']` |
| `GIT_ICASE_PATHSPECS=1` | (not harmful) | `['groundwork.pin']` |

`--glob-pathspecs` was considered and is not an option: git rejects it when the literal
setting is active. Scrubbing the four pathspec variables makes the answer depend on the
repository rather than on the shell the gate runs from. `GIT_GLOB_PATHSPECS` and
`GIT_ICASE_PATHSPECS` are scrubbed too — neither is harmful here, and leaving them would make
the result environment-dependent for no reason.

## A sub-finding of 3 that this session got wrong first

Finding 3 reported a doubled word, "presence presence", in `docs/known-limitations.md`. The
first check for it here used a line-scoped regular expression, found nothing, and nearly
recorded the sub-finding as not reproducing. **The typo was real** — it spans a line break, so
a per-line pattern cannot see it. Recorded because the failure was the check's, not the
report's, and because this branch has already rejected one finding on a reproduction that did
not reproduce: the standard has to cut both ways, and a probe that fails to reproduce is
evidence about the probe until the probe is verified.

## The round-05 repair audit came back clean

The first time on this branch that the presence question drew no over-correction. The reviewer
confirmed, and two probes run here independently agree: an ancestor symlink is refused even
when it points inside the repository, which is what `os.walk(followlinks=False)` does; a
final-component symlink to a regular file stays present; root-level candidates work with no
ancestor loop; annotated tags resolve; and `ls-tree -r` does not recurse through gitlinks, so
the base listing invents no markers inside submodules.

## Verification

Outside the sandbox: **895 tests, OK, skipped=1**; `validate.py .` 0 errors and 8 warnings
(the baseline entry 01 declared); `validate.py demo` 0 errors and 2 warnings; `--diff main`
exit 0.

## Mutations

Two, both caught: restoring the inherited environment on the `git log` call, and removing the
no-candidates short-circuit.
