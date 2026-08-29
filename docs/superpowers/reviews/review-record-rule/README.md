# Codex review record — branch `docs/review-record-rule`

The durable per-round review log rule 9 requires
([../../../agents/build-sessions.md](../../../agents/build-sessions.md)), kept on the
branch that installs rule 9. Rule 9 is the operative text; this file carries the parts
that keep changing, and each `round-NN.md` beside it is fixed once its round has passed.

**This log's own addition, which rule 9 does not require:** each finding is marked
CONFIRMED (the reviewer verified it against a source) or PLAUSIBLE (reasoned, unverified).

**Layout.** Rounds 1–6 ran before rule 9 named the per-round layout; they were split into
`round-NN.md` unchanged when the maintainer's decisions landed (round 7). No round's
content was edited in the move.

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
| 7 | — | maintainer decisions, not a review round | — | see round-07 |

Forty-seven findings across six rounds, all accepted, none rejected.

## Rejected findings

None. Every finding in every round was accepted.

## Open maintainer items

**None.** The eleven items rounds 4–6 raised were decided by the maintainer on 2026-08-29
and are implemented in rule 9 and in this directory's layout. `round-07.md` records each
decision, what was chosen, and where it landed.
