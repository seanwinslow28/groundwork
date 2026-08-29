# Codex review record — branch `docs/review-record-rule`

**Branch:** `docs/review-record-rule`.

The durable per-entry review log rule 9 requires
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
| 7 | — | maintainer decisions, not a review round | — | `b33296e` |
| 8 | `b33296e` | does not approve | 9 | see below |

Fifty-six findings across seven review rounds, all accepted, none rejected. The nine rows
that had been escalated rather than fixed are dispositioned in `round-08.md`, all as fixed
in `b33296e`.

## Rejected findings

None. Every finding in every round was accepted.

## Open maintainer items

**None blocking.** The eleven items rounds 4–6 raised were decided by the maintainer on
2026-08-29; `round-07.md` records each decision and `round-08.md` records where round 8
found the landing incomplete and what was fixed.

One thing is flagged for the maintainer rather than open: **what counts as adequate grounds
for rejecting a finding** was part of item 8 and was not covered by the decision. Round 8's
finding 6 defines it — factually wrong, out of scope, or superseded, each naming its
source, scope-plus-follow-up, or superseding item. That is the builder's construction, not
a maintainer choice, and is easy to override if it is too narrow.
