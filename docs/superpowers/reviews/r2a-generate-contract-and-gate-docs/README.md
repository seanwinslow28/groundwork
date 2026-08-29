# Codex review record — branch `docs/r2a-generate-contract-and-gate-docs`

The durable per-round record [rule 9](../../../agents/build-sessions.md) requires. Rule 9
is the operative text; this file carries the parts that keep changing, and each
`round-NN.md` beside it is fixed once committed.

**Why `reviews/` and not `plans/`.** Rule 9 routes a branch to
`docs/superpowers/plans/<slice>-reviews/` only when its own commits add or change exactly
one plan. This branch adds and changes none, so it takes `reviews/<slug>/`, where `<slug>`
is the branch name's last path component. The path was free in `main` at branch time, so
no collision suffix applies.

**Branch:** `docs/r2a-generate-contract-and-gate-docs`, cut from `main` at `2880e43`.

## What this slice is, and what it is not

The design's landing order names **R2** as four parts. The maintainer was told at kickoff
that R2 is too big for one session and was given the split with a recommendation and its
counter-argument; they chose the split and this half first. So R2 becomes:

- **R2a — this branch.** The rest of the `generate.md` contract amendment (hole b): the
  `provisioned: no` reconciliation and the wider generation-report wording. Plus S2's open
  items 2 and 5 — the adopter-facing sites that gave a company repo the wrong `--diff`
  base, described the gate's enforcement incompletely or wrongly, and stated the
  frozen-layer guarantee without its manifest condition.
- **R2b — next session.** The person-versus-role prose rewrite and full roster
  elicitation. They are one unit: `interview/generate.md`'s holder-typing rule is built on
  the sentence at `questions.md:93` that the rewrite deletes, so separating them would
  leave the contract citing a note that no longer exists.

**Baselines are unchanged by this slice** — engine 8 warnings, demo 3. Retiring the demo
roster's staleness WARN belongs to R2b, which is what gives the demo an elicited cadence.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 01 | `4fbb9dd` | 1 finding, no approve/does-not-approve word | 1 | `a9e1171` |
| 02 | `a9e1171` | pending | — | — |

## Open findings

None recorded yet.

## Rejected findings

None recorded yet.

## Maintainer items

**1. The R2 split.** Chosen by the maintainer at this session's kickoff, from three
options with a recommendation and a counter-argument. Recorded here because the kickoff is
not a repository artifact a reader can check; ratifying it is the maintainer's at merge.
This is not a rule-1 departure — R2a is one increment — it is a narrowing of the increment
the landing order named.
