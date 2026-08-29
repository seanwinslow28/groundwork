# Codex review record — branch `docs/review-record-rule`

**Branch:** `docs/review-record-rule`.

The durable per-entry review log rule 9 requires
([../../../agents/build-sessions.md](../../../agents/build-sessions.md)), kept on the
branch that installs rule 9. Rule 9 is the operative text; this file carries the parts
that keep changing, and each `round-NN.md` beside it is fixed once committed.

**This log's own addition, which rule 9 does not require:** each finding is marked
CONFIRMED (the reviewer verified it against a source) or PLAUSIBLE (reasoned, unverified).

**Layout.** Rounds 1–6 ran before rule 9 named the per-entry layout; they were split into
`round-NN.md` unchanged when the maintainer's decisions landed (round 7). No round's
content was edited in the move. An entry is fixed once committed.

**Session note.** Both branches of this session — this one and
`docs/generate-consent-gate-base` — were built as one session's work, departing from rule 1
("one increment per session"). The maintainer authorised the two doc slices as a bundle in
the session kickoff, which is not a repository artifact a reader can check; ratifying it is
the maintainer's at merge.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 1 | `57babf3` | does not approve | 3 | `edc3c26` |
| 2 | `edc3c26` | does not approve | 5 | `1c94a3c` |
| 3 | `1c94a3c` | does not approve | 7 | `bd81918` |
| 4 | `bd81918` | does not approve | 12 | `bcee344` |
| 5 | `bcee344` | does not approve | 9 | `79d216c` |
| 6 | `79d216c` | does not approve | 11 | `74c7122` |
| 7 | — | maintainer decisions, not a review round | — | `b33296e` |
| 8 | `b33296e` | does not approve | 9 | `21c6c74` |
| 9 | `21c6c74` | does not approve | 9 | see round-11 |
| 10 | `edce94b` | does not approve | 6 | see round-11 |

Seventy-one findings across nine review rounds, all accepted, none rejected. Sixteen rows
that had been escalated rather than closed are dispositioned in `round-09.md`, three of them
corrected again in `round-10.md`.

## Rejected findings

None. Every finding in every round was accepted.

## Open findings

Recorded, blocking nothing — rule 9's merge condition is that the verdicts are committed,
not that every finding is closed:

- verdict vocabulary, and which reviewer words count as approving;
- whether partial output from an aborted invocation must survive;
- entry numbering past `round-99`;
- the grandfathering boundary — when work counts as "started" for the per-entry layout;
- branch identity after a rename;
- which merge target applies before a PR exists, and what happens if it changes;
- who performs a merge-time directory rename;
- which commit is mapped when one round's fixes span several;
- how a clean round is represented — left open by maintainer decision 11;
- whether treating a directory rename as outside entry immutability is coherent, given git
  records it as a path deletion and addition.

## Open maintainer items

**None blocking.** The eleven items rounds 4–6 raised were decided by the maintainer on
2026-08-29; `round-07.md` records each decision and `round-08.md` records where round 8
found the landing incomplete and what was fixed.

**One item is open for the maintainer: what counts as adequate grounds for rejecting a
finding.** It was part of item 8 and the decision did not cover it. Round 8 defined it
unilaterally, round 9 removed that as an unapproved policy choice, and round 10 found round
9's replacement recommendation rested on a misread precedent. `round-10.md` carries the
restated options, recommendation and counter-argument — read that one, not round 9's.
