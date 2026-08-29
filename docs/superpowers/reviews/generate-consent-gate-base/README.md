# Codex review record — branch `docs/generate-consent-gate-base`

The durable per-round review log rule 9 requires. Rule 9 lands on the sibling branch
`docs/review-record-rule`, this session's other slice, and the approved landing order puts
it first — so this log is kept prospectively, and merging this branch ahead of that one
would make the citation premature. Rule 9 is the operative text; this file carries the
parts that keep changing, and each `round-NN.md` beside it is fixed once its round has
passed.

**This log's own addition, which rule 9 does not require:** each finding is marked
CONFIRMED (the reviewer verified it against a source) or PLAUSIBLE (reasoned, unverified).

**Layout.** Rounds 1–6 ran before rule 9 named the per-round layout; they were split into
`round-NN.md` unchanged when the maintainer's decisions landed (round 7). No round's
content was edited in the move.

**Session note.** Both branches of this session were built as one session's work, departing
from build-sessions rule 1 ("one increment per session") and the design's "one slice per
session". The maintainer authorised the two doc slices as a bundle in the session kickoff,
which is not a repository artifact a reader can check — so this records the departure, it
does not show the rule was satisfied or waived. Ratifying it is the maintainer's at merge.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 1 | `5dcf285` | does not approve | 6 | `5a71138` |
| 2 | `5a71138` | does not approve | 6 | `f562d69` |
| 3 | `f562d69` | does not approve | 7 | `7421d58` |
| 4 | `7421d58` | does not approve | 7 | `10e1ec1` |
| 5 | `10e1ec1` | does not approve | 8 | `d2ce4fc` |
| 6 | `d2ce4fc` | does not approve | 9 | `13d8bef` |
| 7 | — | maintainer decision, not a review round | — | `41e0a36` |
| 8 | `41e0a36` | **approve** | 0 | terminal |

Forty-three findings across six review rounds, all accepted. Two were never fixed and are
rejected with grounds at round 8; the rest were fixed.

## Rejected findings

Two, both rejected for scope at round 8, both real and both recorded as work rather than
dismissed. Rule 9 requires them listed here so the one move that closes a finding by
disagreeing with it is visible without reading every round file.

- **Round 1, row 4** — adopter-facing sites unreconciled: `README.md:127` sends someone
  checking a freshly generated OS to `--diff main`, and `CONTEXT.md:105` states the consent
  invariant without the bootstrap qualification. *Grounds:* the approved slice is confined
  to `generate.md`, and `CONTEXT.md` is the locked-decision glossary. Open items 1 and 2.
- **Round 5, row 7** — the parallel-site inventory is incomplete:
  `delivery/README.md:247–248`, `proposals/README.md:55`, `interview/README.md:85`,
  `interview/protocol.md:13–15`, `docs/security-and-privacy.md:151–152`. *Grounds:* same
  scope, and several need the later-run base contract settled first. Open items 2 and 3.

## Status

**Ready to merge.** Round 8 approved with no findings; every finding on the branch is
fixed or rejected with grounds; the gate is green. The open items below are recorded
follow-up work, not unresolved findings.

## Open maintainer items

Item 4 — what "the generation commit" means when generation is not one commit — **is
decided** and is recorded in `round-07.md`. Item 5 was closed at round 6. The rest stand:

**1. `CONTEXT.md:105`'s consent-gate entry and the root-creating commit.** Is generation
outside governed self-improvement, or an exception to it? The glossary states the invariant
without qualification, and this branch exempts the root-creating commit.

**2. Adopter-facing sites that state the base or the enforcement, incompletely.**
`README.md:127` and `delivery/README.md:244` give a company repo `--diff main`, which
reproduces S2 before generation reaches `main`, and `delivery/` promises exit 0.
`README.md:134–137` and `delivery/README.md:247–248` describe what the stateful run
enforces without external-side-effect skills, frontmatter and Owner's Card escalation, or
#17's changelog behaviour, and README's blanket "or the gate ERRORs" at 136–137 is false
for deletions, which WARN. `proposals/README.md:55` omits the governed-deletion WARN.
`interview/README.md:85`, `interview/protocol.md:13–15` and
`docs/security-and-privacy.md:151–152` imply any committed layer is protected, without the
base condition item 5 records.

**3. The base contract for later runs.** `_git_diff_context` verifies only that the ref
resolves and lists its tree — neither ancestry nor that the base holds the generated root.
Several sites in item 2 lean on a guarantee nothing provides.

**5. The frozen-layer guarantee needs the manifest, not just the layer.**
`interview_diff_findings` derives its state directories from the base file list, so a layer
is protected only when the base also holds its `00-manifest.md`. `generate.md` says this;
the sites in item 2 do not.

**6. The rule-1 departure.** Recorded above; ratifying it is the maintainer's.

Items 2 and 3 are follow-up work rather than this slice's, and item 3 is a change to what
the gate promises rather than to how a document describes it.
