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

## Open findings

None yet.

## Rejected findings

None yet.

## Maintainer items

Two workbench rules were adopted in entry 01 and written into
`docs/agents/build-sessions.md` by this session: **rule 10** (a check the issue did not ask
for is a rule 5 escalation before it is written) and **rule 11** (a round with no findings
in the slice's class sends the slice to the maintainer; the class is named in round 01).
They are on this branch rather than their own because rule 11 binds this slice's own record
from entry 01 onward.
