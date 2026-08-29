## Round 7 — 2026-08-29, maintainer decisions (not a review round)

No Codex invocation. This entry records the eleven decisions round 6 left open, all made by
the maintainer on 2026-08-29, and where each landed. Four were put with options, a
recommendation and a counter-argument and chosen individually; the other seven were
delegated to the recommendation after the maintainer saw the list. **The maintainer's first
instruction was "go with your recommendations on all of them"; rule 5 forbids taking that as
a substitute for understanding, so it was declined and the four structural ones were put
individually.** Two of those four went against the recommendation as first written.

**Fix commit for round 6: `74c7122`.** Round 1 → `edc3c26`, 2 → `1c94a3c`, 3 → `bd81918`,
4 → `bcee344`, 5 → `79d216c`, 6 → `74c7122`.

| # | Decision | Chosen | Where it landed |
|---|---|---|---|
| 1 | Never-rewrite, and what assures it | **One file per round** (the recommendation) | Rule 9's "Where"; this directory is the first instance |
| 2 | The non-injective `/` → `-` mapping | Readable slug plus a **collision-detecting suffix** — the variant of the recommendation that needs no allocator the repository does not have | Rule 9's "Where": `<branch-slug>` is the branch's last path component, `-2` or `-3` if taken |
| 3 | The unreviewed terminal commit | **State it plainly and accept it** — *against* the recommendation, which was to store the reviewer's raw output | Rule 9's "The terminal round". The raw-output option was withdrawn as an archive nobody reads; the honest sentence costs nothing and claims nothing false |
| 4 | Where the contract lives | **Rule 9 is the operative text; decision 7 points at it** — *against* the recommendation as first written, and matching the builder's stated loss of confidence in it | Rule 9's opening; decision 7 gains an amendment note and keeps the decision, evidence and counter-argument |
| 5 | Must the terminal verdict approve | **Approving unless the maintainer records grounds in the merge commit** | Rule 9's "The terminal round", citing `5fc61c6` |
| 6 | What counts as a round | **Every invocation gets a file**, aborted ones included | Rule 9's "Every invocation gets a file" |
| 7 | Recording the reviewed revision | **Required, as a commit SHA, against a clean worktree** | Rule 9's "What a round file carries" |
| 8 | Who may reject a finding, and adequate grounds | **The builder may, and every rejected finding is also listed in the directory README** | Rule 9's "What a round file carries"; this log's README carries the (empty) list |
| 9 | How `<slice>` is derived | **The plan's filename without its date prefix** | Rule 9's "Where" |
| 10 | How much finding text must survive | **Compressed summaries are enough** | Rule 9's "What a round file carries" |
| 11 | Clean-round form and severity vocabulary | **Reviewer severities kept verbatim; the clean-round form left open** | Rule 9's "What a round file carries" |

**Consequences of decision 4 for rule 9's shape.** The long evidence paragraph moved out of
rule 9 into decision 7, which is now the sole record of why the rule exists. Rule 9 keeps a
three-line evidence summary and the worked-example pointer, and gained the contract text the
eleven decisions settle. `build-sessions.md` is 70 lines; `AGENTS.md` is unchanged.

**Consequences of decisions 1 and 2 for this branch.** Rounds 1–6 were split from the single
`docs-review-record-rule.md` into `round-01.md` … `round-06.md` with no content edited, and
the mutable parts — the round map, the fix-commit map, the rejected-findings list, and the
open items — moved into `README.md`. The merged worked example
(`docs/superpowers/reviews/spec-roles-accountable-unit.md`) keeps its single-file form: rule
9 binds work started after it lands, and that log is named in rule 9 as the worked example
with that stated.

**All eleven items are closed.** No open maintainer items remain on this branch.
