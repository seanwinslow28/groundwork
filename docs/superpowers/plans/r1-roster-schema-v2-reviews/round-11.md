# Entry 11 — maintainer decisions, not a review round

**This entry is not a review round.** No Codex invocation produced it. It records the
maintainer's answers to six of the items entry 10 left open, given 2026-08-29 after each was
put with its options, a recommendation and its counter-argument.

Every decision below is **keep what is in the tree**, so no file changes as a result. What
changes is that these stop being open questions.

## Decided

**1. The demo roster's `review_by` stays `2026-08-09`.** The date is `generate.md`'s 90-day
policy default applied to `valid_at: 2026-05-11`, it has passed, and the staleness WARN
stands — so `demo` reads `0 error(s), 3 warning(s)` and the engine root `0 error(s),
8 warning(s)`. The grounds: the demo's frozen interview never asked how often an org map
should be re-confirmed, so the roster genuinely has no elicited cadence, and the WARN is the
mechanism correctly reporting a dated artifact past its default. The two alternatives were a
future date justified by the demo's own freshness convention — which is what the builder did
first, and what round 1 caught as a false justification — and adding a cadence to
`demo/canon.md` as authored fact, which would have disagreed with the roster's own `source`
line. **This is expected to resolve in R2**, whose roster elicitation gives the demo a real
cadence; the WARN should then disappear because the question was answered, not because the
date was moved.

**2. `demo/governance/changelog.md` stays as it is, and the underlying question is queued.**
Its preamble lists what escalates and omits the roster; `#17`'s append-only rule makes the
sentence uncorrectable, as round 2 established by making the edit and watching the gate go
red. Scope confirmed while deciding: the **engine's** changelog preamble carries different
text that enumerates nothing, so this is one file. The queued question — protect only lines
matching the entry format, leaving a file's explanatory header editable — is a change to what
an append-only guarantee means and is not this slice's.

**3. The demo roster stays holder-only.** No Role rows for the five offices
`demo/canon.md` assigns. The grounds: the demo models a *generated* company, and a repo
generated in the R1–R2 window gets exactly holder-only rows, because that is all
`generate.md` permits without inventing. Role rows arrive in R2 with the elicitation that
justifies them. The cost accepted: the demo does not exercise the Role column, and only the
engine-root roster demonstrates it.

**4. The active-rule ERROR suppression stays.** With an active rule and no roster at all,
one missing-roster ERROR is emitted and the four per-field resolution ERRORs are suppressed;
with a roster present all four fire, and drafts are never suppressed. The verdict is
identical either way, so this decides what a reader sees rather than whether the gate is red.

**This one is recorded as the weakest of the six, on the builder's own account.** Its
rationale borrows `MIGRATIONS.md`'s "one clean boundary error, never a scatter" promise,
which is written about pin skew rather than about missing rosters. It was offered for
challenge in all nine review rounds and declined every time — by a reviewer explicitly told
it was already disclosed, which makes nine declines weak evidence rather than strong. It is
a handful of lines to reverse if a later slice disagrees.

**5d. The rule-1 departure is ratified.** The previous session built two slices (R0 and S2)
against rule 1's one-increment-per-session, recorded in the READMEs of
`docs/superpowers/reviews/review-record-rule/` and
`docs/superpowers/reviews/generate-consent-gate-base/`. Ratified as authorised in that
session's kickoff. **This session did not depart from rule 1** — R1 was one slice, across
nine review rounds.

**6. Both edits beyond the design's named list are ratified.** `CONTEXT.md`, because locked
decision 8 made its "the only two artifact kinds the three buckets route" affirmatively
false; and `docs/roadmap.md`, because two of its V2 bullets — the first `SCHEMA_VERSION` bump
and the unwired `since:` mechanism — became false the moment this branch landed. Both
transcribe decisions already locked rather than adding policy. The precedent the previous
slice set, rejecting a `CONTEXT.md` edit for scope, is distinguished rather than overturned:
that edit would have *extended* the glossary, this one repairs a sentence the branch itself
falsified.

## Still open, and still the maintainer's

Three items were deliberately not answered, and stay open:

- **5a. What counts as adequate grounds for rejecting a finding.** Options and a
  recommendation (a closed list: factually wrong / out of scope / superseded) are in
  `docs/superpowers/reviews/review-record-rule/round-11.md`. This slice adds one worked
  example: round 2's rejection was demonstrated rather than argued.
- **5b. Whether `CONTEXT.md:105`'s consent invariant should carry a qualifying clause.** It
  states the invariant without exception, and there are now two — generation, and decision
  8's migration bootstrap.
- **5c. Whether a later `--diff` base must be proven to contain the generated root.**
  Recommended as its own small slice rather than folded into this one.

Two follow-ups created by the decisions above, neither blocking:

- Entry 2's queued question about protecting a changelog's entry lines rather than its whole
  text. Not yet filed as an issue.
- R2 should pick up the demo roster's cadence when it lands roster elicitation, per decision
  1 above.
