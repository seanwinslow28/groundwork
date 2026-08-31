You are the BUILD half of a two-model loop on groundwork (~/Code-Brain/groundwork).
Read AGENTS.md and docs/agents/build-sessions.md first — the session rules bind, including
rule 9 (durable review verdicts) and the new rules 10 and 11. Rule 9's rejection grounds are
a CLOSED LIST of three categories; a finding no category fits is NOT rejected — it stays open
and the maintainer overrides at merge. Read the paragraphs; do not work from a summary.

Also read the new **"Craft notes — measured failure modes"** section at the end of
`docs/agents/build-sessions.md`. It is the #32 and #40 sessions' measured results. You will
hit at least three of them.

=============================================================================
THE POINT OF THIS SESSION, AND WHY IT IS NOT LIKE THE LAST FEW
=============================================================================

**The goal is run 2, not this slice.** Read `gh issue view 38` in full before anything else.

`docs/EXPLANATION.md` publishes one measured number: run 1 planted nine concealed facts and
the interview surfaced **one in full and a second in part**. `1 of 9` stands until a second
run measures the redesign. Issue #38 gates run 2 on five items, and **this session clears all
five in ONE slice** so the run can happen.

**Comparability is a wasting asset.** Every further interview-surface change landed before
the run turns "S1 measured cleanly" into "S1 plus N clarifications measured as one lump".
That is the whole reason to move now.

**MATCH THE REVIEW DEPTH TO THE ARTIFACT.** Issue #40 took seven Codex rounds because it was
a classifier over adversarial inputs: every fix opened a new state, and three Majors were
introduced by the previous round's repair. **This slice is prose in three markdown files.**
There is no adversarial input space. Two review rounds is the expectation, not eight, and the
brief below tells you what to ask for instead of an edge-case hunt.

**The real validator for interview prose is the run.** You cannot find "the interviewer will
guess wrong at turn one" by reviewing a document; you find it by running it against personas.
Over-reviewing here spends the thing that is scarce (comparable runs) to buy the thing that is
cheap (another prose round). If you find yourself on round four, stop and go to the maintainer
under rule 11.

=============================================================================
STATE
=============================================================================

main is `780d3ec`, pushed and in sync with origin. Working tree clean. Two branches:
main, and `prototype/interview-state-9` (one unmerged commit from 2026-07-20 behind decision
9 — leave it alone).

Landed since the last kickoff: issue #40 (the `--diff` marker-deletion evidence walk, merged
at `efe78a9`), build-session **rules 10 and 11**, the retirement of all four stale kickoffs,
and the craft notes.

**R2b HAS LANDED.** Issue #38's body says it was "in flight as of 2026-08-29" — that is
stale. Roster elicitation is in `interview/questions.md` at lines 99–102 on main, including
`roster:review_by`. This matters for C10 below: the second cadence question the issue warned
about **already shipped**, so C10 is now a live two-mechanism problem rather than a
prospective one.

GATE BASELINES on `780d3ec` — verify before you start:
- `python3 scripts/validate.py .` -> **0 error(s), 8 warning(s)**, exit 0
- `python3 scripts/validate.py demo` -> 0 error(s), 2 warning(s)
- `python3 scripts/validate.py . --diff main` -> exit 0
- `python3 -m unittest discover -s tests` -> **OK, 898 tests, skipped=1**
There is no pytest; use unittest.

**The 8 warnings are correct, not a regression.** The eighth is `check_entropy`'s documented
false positive on a long hyphenated path in `docs/agents/build-sessions.md`. Declared in
`docs/superpowers/reviews/issue-40-marker-deletion-evidence/round-01.md`. Do not "fix" it.

=============================================================================
THE SLICE: clear issue #38's gate in one unit
=============================================================================

Five items, all edits to `interview/protocol.md`, `interview/questions.md` and
`interview/generate.md`. Read each issue in full — each one quotes run 1's finding verbatim
with a *Before*, an *After* and a *Measured*, so the target text is largely specified already.

**TWO STRUCTURAL DECISIONS ARE ALREADY TAKEN.** The maintainer decided both on 2026-08-30, so
this session does NOT stop to ask. Record them in your round-01 entry as decisions carried in
from the kickoff, with the counter-argument each was chosen against.

- **#34 (S5) — an owner who cannot confirm.** DECIDED: **record with a caveat, and the caveat
  blocks automation.** The layer freezes; the record carries an unconfirmed-owner caveat and
  an open question — which is what run 1's generator already produced — and an activity whose
  named owner never confirmed **cannot be routed to automation until they do**. The caveat has
  a consequence rather than being a note.
  *Counter-argument, recorded:* this adds a routing rule to a protocol slice, which is scope
  the issue did not ask for. It was accepted because the alternative labels the exact failure
  #6 exists to prevent instead of preventing it.
  *Watch the boundary:* say where the block bites (routing an activity to automation) and do
  NOT build a validator check for it in this slice. If you think one is needed, that is a rule
  10 escalation — file it, do not build it.

- **#35 (S6) — the checkpoint's second approval.** DECIDED: **two approvals. The person
  confirms the CONTENT; the sponsor approves the FREEZE.** They cover different defect
  classes and neither substitutes for the other — the content confirmer cannot see the
  frontmatter, which is exactly where run 1's defect was (`_working.md`'s `source:` still read
  "interview turns pending" after the turns had happened).
  *Counter-argument, recorded:* it puts a human in a loop a mechanical check might cover
  better. Considered and not taken: a validator check on the state file's frontmatter. That is
  a new check, so rule 10 routes it to an issue — **file that issue in this session** and say
  in it that S6's second approval is the interim cover.
  C13 rides with this. Read #35's body for what C13 is.

The other three are clarifications with their target text largely written in the issues:

- **#37 (C12) — which human mechanic 1 addresses.** The smallest and highest-leverage of the
  five: it is the first act of the interview and the role it establishes governs every
  question after it. Run 1's interviewer guessed and recorded the guess; a re-measurement in
  which it guesses the other way has a confound at turn one that propagates through
  everything. `interview/protocol.md:27`.
- **#36 (C5) — one-question-at-a-time versus bulk ratings.** Settle the BOUNDARY once, in both
  directions. The issue notes the seam has now been hit from both sides — slice 3.2 reconciled
  a batched-question finding with the ask-in-parts rule, and this is the reverse case. Do not
  patch only the direction that most recently complained.
- **#33 (C10) — a cadence answer against an ISO-date field.** Say that a cadence answer is
  converted to a date at generation and the derivation is recorded on the record. **Apply it
  to BOTH `memory:review_by` and `roster:review_by`** — R2b shipped the roster cadence
  question, so the two-mechanism drift this issue warns about is live now. `governance/roles.md`
  on main already carries a hand-written derivation sentence ("quarterly, taken as 90 days,
  added to valid_at 2026-08-29") — that is the shape to generalize, and it is evidence the
  mechanism is needed rather than speculative.

**Expect:** edits to the three interview docs; possibly `interview/README.md` if the freeze
protocol's conversational half moves; new or amended tests only where a doc contract is
machine-checkable (do not invent checks to look thorough — rule 10); and `docs/rule-map.md`
ONLY if you add a top-level `check_*` or `*_findings` function, which this slice probably
should not.

**NOT THIS SESSION**, and named so they are not quietly pulled forward: S4, the nine
clarifications C1–C4/C6–C9/C11, #41, #42, #43 (the three open findings from #40), #30, #28,
#24–#27, #29. Issue #38 lists the deferred set; do not widen it.

=============================================================================
THE REVIEW BRIEF — ask for this, not an edge-case hunt
=============================================================================

Codex review via the `codex:codex-rescue` agent with `--background`. The subagent returns as
soon as it launches; poll the job JSON at
`~/.claude/plugins/data/codex-inline/state/<dir-hash>/jobs/<task-id>.json`, where the
dir-hash is keyed by the LAUNCH cwd. `result` is a DICT; read `result.rawOutput`. Rounds take
4–8 minutes. Review threads are NOT resumable — after committing fixes, launch a fresh review.

**Do not ask for classifier correctness. There is no classifier here.** Ask for a
FOLLOWABILITY AND CONTRADICTION AUDIT, which is the framing both prior sessions measured as
most valuable:

> Read `interview/protocol.md`, `interview/questions.md` and `interview/generate.md` as the
> interviewing agent would — in order, with no design context beyond what they say. For every
> instruction: can it be followed without guessing? Name every place two sentences in these
> documents disagree, every rule an agent must break to run the interview at a sane length,
> and every question whose answer has no stated destination field. Then say which of run 1's
> five gated findings (#33, #34, #35, #36, #37) the current text now answers and which it
> still leaves to the interviewer's judgment.

That last sentence is the acceptance test. **A round that says all five are answered and
names where is a clean round**, and rule 11 then sends the slice to the maintainer.

Tell Codex every round: point it at the previous round's repairs first and ask whether each
over-corrected; a clean round is a real outcome and it must not manufacture findings; it must
not re-raise anything the record already discloses (list those, and the list grows each
round); and its sandbox often cannot create temp directories, so `TemporaryDirectory` errors
from `unittest` are environmental — verify the suite yourself and say so in the round entry.

**Never word a brief adversarially.** Two of #32's rounds were killed by a provider content
filter. See the craft notes.

=============================================================================
AFTER THE SLICE MERGES: RUN 2
=============================================================================

This is the actual goal. Do not start it in the same session as the slice.

The apparatus is `~/Code-Brain/persona-company`. Read its `README.md` and
`runs/2026-07-31/timing.md` — the latter records run 1's provenance table, which is the shape
run 2 must reproduce so the two are comparable.

**Run 1 was four separate sessions**, and run 2 must be too:
1. **Interview** — a fresh blind session against the seven personas via `ask.py`.
2. **Generation** — a separate session running `interview/generate.md` into a company repo.
3. **Grading** — a **fresh grading session** given exactly `plants.md`, the generated OS, the
   interview state and the transcripts, with **no design context**. Run 1's design says
   staying out of the grading loop is what makes run 2 comparable.
4. **Audit** — the transcript audit against a FROZEN copy of the interviewing session's log.
   The harness rewrites that log live; run 1 pinned a copy at mode `444`. Without it the
   verdict degrades to *unaudited*, never *clean*.

**Do not read `personas/*/private.md` or `plants.md` in the interviewing session.** They are
the answer key and reading either voids the run. The boundary is soft on purpose and audited
afterward.

**Done means** run 2 executed under the versioned apparatus, graded blind, and
`docs/EXPLANATION.md`'s `1 of 9` replaced by a measured number **whichever direction it
moves**. A worse number that is honestly measured is a real result; issue #38 says so.

=============================================================================
HOW TO WORK
=============================================================================
- Branch before editing; never commit to main; use a git worktree
  (`~/Code-Brain/groundwork-wt-run2-gate`), and remove it after the merge.
- Rule 9 from round 1. Record goes in `docs/superpowers/reviews/<branch-slug>/`. One file per
  entry, `round-NN.md` from 01, immutable once committed. Round 01 is a maintainer-decision
  entry recording the two decisions above **and naming this slice's finding-class**, which
  rule 11 requires: *whether the interview documents can be followed by an agent without
  guessing, and whether they contradict each other.* The README carries the fix-commit map,
  the open findings and the rejected findings. Do NOT pre-fill a pending round's reviewed SHA.
- End green on all four commands above, and state any changed baseline explicitly in both the
  merge commit and the review record.
- The maintainer lands the merge unless they instruct otherwise; if they do, record that in
  the merge commit.
- **This kickoff is retired when the slice merges.** All four previous kickoffs were left on
  main describing finished work, and two of them carried factual errors into later sessions.
  Delete this file in the merge, or in a chore commit right after it.
