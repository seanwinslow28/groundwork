# Codex review record — branch `feat/issue-40-marker-deletion-evidence`

The durable per-round record [rule 9](../../../agents/build-sessions.md) requires. Rule 9 is
the operative text; this file carries the parts that keep changing, and each `round-NN.md`
beside it is fixed once committed.

**Why `reviews/` and not `plans/`.** Rule 9 routes a branch to
`docs/superpowers/plans/<slice>-reviews/` only when its own commits add or change exactly
one plan. This branch adds and changes none, so it takes `reviews/<slug>/`, where `<slug>`
is the branch name's last path component. The path was free in `main` at branch time, so no
collision suffix applies.

**Branch:** `feat/issue-40-marker-deletion-evidence`, cut from `main` at `9e8d7f8`.

## What this slice is

Issue #40: `diff_base_findings`, `_pin_dirs` and `interview_diff_findings` read two trees —
the base tree and the working tree. Name a base from before `groundwork.pin` or
`interview/00-manifest.md` was committed **and** delete that marker in the same working
change, and it is in neither. Nothing is discovered, nothing is checked, nothing is said.

The slice adds a third source of evidence: the commits between the base and HEAD. Where they
show a marker was introduced and the working tree no longer holds it, the run says so.
**The slice does not change what any pass gates** — that option was considered and refused
in entry 01.

## The slice's finding-class, under rule 11

**Whether the marker-existence evidence classifies a working tree correctly** — a marker that
existed between base and HEAD and is now gone must be reported; a repository that never
carried one must not be. Named in `round-01.md` before any code was written, which is what
rule 11 requires.

## Entries

| Entry | What it is | Reviewed SHA | Verdict | Fixes landed in |
|---|---|---|---|---|
| [01](round-01.md) | Maintainer decision, not a review round | n/a — decided against `9e8d7f8` | n/a | n/a |
| [02](round-02.md) | Codex review round | `ae654cf` | Not clean — 2 Major + 7 Minor on classifier correctness, plus 2 Major on prose | `d63196c` |
| [03](round-03.md) | Codex review round | `cfb0c20` | Not clean — 1 Major + 1 Minor on classifier correctness, plus 3 Minor on prose | `d1ab4fc` |
| [04](round-04.md) | Codex review round | `512126f` | Not clean — 4 Major + 1 Minor on classifier correctness, plus 2 Minor on prose and the record. One Major rejected. | `de7eaf8` |
| [05](round-05.md) | Codex review round | `095ca91` | Not clean — 1 Major + 2 Minor. Entry 04's rejection independently confirmed. | (this branch's round-05 fix commit) |

## Open findings

Both are from entry 02, both **Minor**, and both are recorded in `docs/known-limitations.md`.
Neither is rejected, because no closed-list category fits and rule 9 keeps such a finding
open rather than dressing it as something else.

- **Finding 4 — a marker inside an initialized submodule.** The superproject's history
  records a gitlink, not the nested path, so an intermediate marker state inside a vendored
  submodule leaves no evidence in the outer walk. Closing it needs a second mechanism: a
  `git log` per initialized submodule.
- **Finding 7 — `git replace` and `.git/info/grafts`.** A local replacement can make HEAD
  appear to parent the base directly and hide the addition between them. The one-flag fix
  (`--no-replace-objects`) would make this read follow a different history from
  `_git_diff_context`'s base-tree read in the same run.

**Decided 2026-08-30: both are documented rather than fixed**, and each has an issue so the
work is not lost — finding 4 is [issue #41](https://github.com/seanwinslow28/groundwork/issues/41),
finding 7 is [issue #42](https://github.com/seanwinslow28/groundwork/issues/42). They remain
**open** here rather than rejected: "the maintainer decided not to build it" is not one of rule
9's three closed-list grounds, and entry 03 records the grounds in full.

## Rejected findings

**Entry 04, finding 1 — Major — rejected as FACTUALLY WRONG.** The finding reported that
history simplification prunes a side branch whose marker was added and removed before a
net-zero merge, giving `Wrong output: []`. The source that shows it wrong is the reviewer's own
reproduction: rebuilt verbatim and run against `512126f`, the revision it was filed against, it
returns the ERROR rather than the reported silence. Independently, a `git merge -s ours` case —
the canonical shape for `--full-history` mattering — gives byte-identical `git log` output with
and without the flag, because `--diff-merges=separate` already forces every merge to be diffed
against each parent. `--full-history` had been added for this finding and was removed.
`test_a_marker_on_a_net_zero_merged_side_branch_is_seen` is kept as the evidence, with a
docstring saying it pins nothing that was broken. Full account in
[entry 04](round-04.md).

## Corrections carried forward

Entry 01 has been corrected twice, both times about a claim that was too strong, and both
times by a later entry because entry 01 is immutable:

- **Mutation M8.** Entry 01 argued the mutation survived "by construction". Entry 02's merge
  fixture disproves the argument. The sentence that replaced it in the code was then found
  false by entry 03 — the flag is a narrowing, and nothing measured shows it is needed. Entry
  04 then disproved *that*: the flag discarded the `T` record for a path that arrived as a
  symlink and later became a real marker, so it was not harmless, and it was removed. Four
  statements about one flag, of which the first three were wrong. Entry 04 records the
  sequence and why deleting the flag is what ended it; this paragraph said "three statements"
  and "the first two" until entry 05 caught it standing after entry 04 had superseded it.
- **"The walk reads committed history."** Entry 01's residual-limit paragraph says this
  without qualification. It reads what this repository's configured `git log` will show it,
  which is narrower in four separate ways. Corrected in entry 03;
  `docs/known-limitations.md` carries the accurate statement.

Entry 02's own account of finding 5 was superseded by entry 03: `lexists` was the wrong side
of that problem. Three test docstrings credited it. Two —
`test_a_directory_named_like_a_marker_is_not_a_deletion` and the unreadable-directory test,
which was also renamed — were corrected in the round-03 fix commit. The third,
`test_a_still_present_marker_is_not_called_deleted_by_spelling`, was missed there and caught
by round 04; it is corrected in the round-04 fix commit. An earlier version of this paragraph
said "the two tests", which was the count before round 04 found the third.

## Maintainer items

Two workbench rules were adopted in entry 01 and written into
`docs/agents/build-sessions.md` by this session: **rule 10** (a check the issue did not ask
for is a rule 5 escalation before it is written) and **rule 11** (a round with no findings
in the slice's class sends the slice to the maintainer; the class is named in round 01).
They are on this branch rather than their own because rule 11 binds this slice's own record
from entry 01 onward.
