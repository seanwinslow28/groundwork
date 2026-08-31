# Build-session rules (groundwork build phase)

> Replaces the wayfinder charting rules now that the map is complete. These are workbench rules for build sessions; they are NOT product content and never ship to adopters.

## Session shape
1. **One increment per session.** Build it, `validate` green, Codex-review, record what it revealed, stop. The pull to keep going is the signal to stop.
2. **One increment ends green:** `python3 scripts/validate.py` passes (zero ERRORs) before a session is done.
3. **Review gate:** Fable 5 builds; the Codex plugin reviews at session end (`/codex` review or `codex:codex-rescue`); the maintainer (Sean) lands the merge — the commit bit is the governance teeth (#18). Rule 9 governs the record those rounds must leave.
4. **Claim before work:** branch before touching the tree (never build on `main`).

## Standing rules (carried from charting)
5. **Explain before Sean decides.** Before each decision he owns, explain in plain terms: what it is, the options, the recommendation, and the honest counter-argument. Never accept "go with your recommendation" as a substitute for understanding.
6. **Honesty rules:** claims match what is verified/built; no capability claim precedes the capability; overclaiming is trust debt.
7. **Source of truth:** the approved design brief and CONTEXT.md (the resolved-decision glossary). Locked decisions are not reopened without new evidence.
8. **Pre-made text is not pre-verified.** A plan's pre-made replacement text carries a
   source citation for every factual claim, and the executor verifies those claims against
   that source *before* transcribing. Transcription fidelity protects the wording a review
   approved; it does not make the claims true, and "the plan said so" is not a basis. Where
   the source is another record, check that record against *its* sources too — one of the
   2026-08-01 slice's four factual defects was inherited from a run record that was itself
   wrong. Codex review caught three on the branch, before `main`'s product files carried
   them; the fourth surfaced only after the slice had merged, and it did reach `main`'s
   roadmap. Assume the ones you have not found yet are already shipped.

## Standing rules (added during build)
9. **Durable review verdicts.** A slice may not merge unless the verdicts of every Codex
   review round run against it are committed in the repository. That is the whole merge
   condition: the record must exist, not that every finding be closed. **This is the
   operative text.** Decision 7 of the 2026-08-28 roles-as-the-accountable-unit design,
   under `docs/superpowers/specs/`, records the decision, its evidence and its
   counter-argument.

   **Where.** One directory per branch, one file per entry:
   `docs/superpowers/reviews/<slug>/`, or `docs/superpowers/plans/<slice>-reviews/` when the
   branch's own commits add or change exactly one plan, where `<slice>` is that plan's
   filename with the leading `YYYY-MM-DD-` and the `.md` removed. `<slug>` is the branch
   name's last path component, ASCII-lowercased, with every character outside `[a-z0-9._-]`
   replaced by `-`. For **either** path: if that path is occupied in the branch's merge
   target — by a directory or by an ordinary file — append `-2`, then `-3`, and so on until
   the name is free. The mapping is deliberately not injective; the directory's `README.md`
   records the full branch name as it stood when the directory was made, which is what
   disambiguates. A collision found only at merge time is resolved by renaming the directory;
   that is not an edit to any entry.

   **Entries.** `round-NN.md`, numbered consecutively from 01, every entry taking the next
   number. Every Codex invocation gets one, a crashed or abandoned one included — that entry
   records the task id and that no verdict was returned. A directory may also carry a
   numbered entry that is not a review round, such as a record of maintainer decisions; it
   says so on its first line. Nothing outside the repository enforces that no invocation was
   omitted, so the numbering is a record, not a guarantee.

   **An entry is immutable once committed.** A correction to an earlier entry is made by a
   later one, never by editing it.

   **What a round entry carries.** The reviewed revision as a commit SHA — a review runs
   against a clean worktree — the verdict, and every finding with the reviewer's own
   severity word kept verbatim, plus its disposition. A finding may be summarised rather
   than quoted in full. **Fixed** and **rejected with grounds** are the dispositions that
   close a finding. A finding that is neither is **open**: it stays recorded as open rather
   than being dressed as something else. **The builder may reject a finding**, and the
   directory's `README.md` lists every open and every rejected finding, so neither the work
   still owed nor the one move that closes a finding by disagreeing with it can be buried
   inside an entry.

   **Grounds for a rejection: a closed list.** A rejection states one of exactly three
   categories, and carries what that category requires: **factually wrong**, naming the
   source that shows it wrong; **out of scope**, naming the scope it falls outside and the
   follow-up work it becomes; or **superseded**, naming what supersedes it. A finding no
   category fits is **not** rejected — it stays **open**, and the maintainer overrides at
   merge if the slice should land anyway (see "The terminal round" below, and what
   `5fc61c6` did for slice 2.1). That escape hatch is the maintainer's to use, not the
   builder's. *Grounds:* a closed list is auditable, where "case-specific grounds" is
   satisfied by any sentence at all. *Counter-argument, recorded:* a closed list cannot
   anticipate a legitimate reason nobody has hit yet, and when one arrives the builder
   either distorts a category to fit or routes the finding to the maintainer. Decided by
   the maintainer 2026-08-29. Entry 12 — `round-12.md` in
   [R1's review record](../superpowers/plans/r1-roster-schema-v2-reviews/) — records the
   decision, its grounds and its counter-argument, and
   [round 11](../superpowers/reviews/review-record-rule/round-11.md) of the
   review-record-rule log records the options it was chosen from.

   **`README.md` carries what keeps changing** — the full branch name, a row per entry, the
   commit that carried each round's fixes, the open findings, the rejected findings, and any
   maintainer items. An entry cannot name the commit that fixes it, since that commit does
   not exist when the entry is written; the README's map is where that SHA lives, normally
   filled in with the next entry. The README records; it never changes a disposition.

   **The terminal round.** The last verdict is committed after the state it reviewed, so
   that commit is not itself reviewed. That is accepted, and said here rather than exempted.
   The final verdict should be approving. The maintainer may merge over a non-approving
   verdict, or over open findings, recording the grounds in the merge commit — as `5fc61c6`
   did for slice 2.1, whose residuals were "accepted as documented". The commit bit is the
   gate (rule 3); this rule governs the record.

   *Evidence:* the session that landed rule 8 ran twenty-five review rounds and kept no round
   output; three of its sixteen groundwork rounds left no numbered fix commit, and two of
   those left nothing anywhere. Decision 7 carries the full account.
   *Worked example:* `docs/superpowers/reviews/spec-roles-accountable-unit.md` — 25 rounds,
   102 findings, every disposition, one approving verdict, with its fix-commit map
   backfilled. It predates the per-entry layout above, which binds work started after this
   rule lands.

10. **A check the issue did not ask for is a rule 5 escalation before it is written.** A
    slice implements the issue's scope; a new check outside it — however well motivated —
    goes to the maintainer first, with what it defends against and what it would cost.

    *Evidence:* issue #32. Measured on `8202ab6`, the fix the issue asked for — the
    base-anchored changelog boundary — was 66 lines, landed in round 1, and drew no
    accepting-direction finding in the fifteen rounds that followed. A second guard the
    issue never raised, started silently in round 2, was 122 lines across 12 commits and
    drew every accepting-direction finding on the branch. The maintainer deleted it.
    `docs/superpowers/reviews/issue-32-changelog-preamble/round-17.md` carries the account.

    *Counter-argument, recorded:* it adds a round-trip to work that is often genuinely
    necessary, and a builder who spots a real hole mid-slice now has to stop. The answer is
    that the escalation is a paragraph where the unescalated guard was twelve commits, and
    that a builder who spots a real hole has an existing mechanism for it — file an issue.
    Decided by the maintainer 2026-08-30.

11. **When a review round produces no findings in the class the slice is about, the slice
    goes to the maintainer for a merge decision** rather than continuing until a reviewer
    says "approve". Rule 9 already says the record must exist, not that every finding must
    close. **The slice's finding-class is named in its round 01 entry**, so the trigger is
    checkable against something written before it fires rather than chosen at the moment
    stopping is convenient.

    *Evidence:* #32's rounds 13 to 16 ran after the safety question had been settled twice
    and closed only accuracy defects in the builder's own prose.

    *Counter-argument, recorded:* a reviewer may find a real defect on round N+1 that round
    N missed, and stopping early trades that away — #32's rounds 08, 09 and 11 each found a
    Major after an earlier round had looked clean in some respect. What blunts it, and the
    reason this rule is adopted together with rule 10 rather than alone: all three of those
    Majors were inside the out-of-scope guard, which under rule 10 would not have existed.
    Rule 11 is safe because rule 10 keeps the slice small; adopting it alone is the weak
    combination. Decided by the maintainer 2026-08-30.

## Craft notes — measured failure modes

**These are not numbered rules.** Rules 1–11 are decisions the maintainer took; these are
practices the build sessions have paid for, each with the evidence that bought it. They are
kept here because they were carried in a session kickoff, proved load-bearing across two
slices, and would otherwise survive only in git history — which no session loads.

Where a claim is attributed to a session, that session's review record is the source; where
this document states a count, name the cases rather than trusting the number to stay true.

### Scope

- **Scope expansion is the expensive failure, not code quality.** #32 measured every
  accepting-direction finding on its branch — rounds 02, 04, 05, 06, 07, 08, 09 and 11 — as
  landing in 122 lines the issue never asked for, while the 66 lines it did ask for were never
  breached. Rule 10 exists because of this. If you find yourself building a second mechanism,
  stop and escalate.
- **Take the thing out rather than describing it better.** #40 wrote four statements about one
  `git log` flag and the first three were wrong, each correction written to fix the last one.
  The sequence ended by deleting the flag. Two other constructs went the same way: an NFC fold
  and a `--full-history` flag were both removed once no mutation of them could be made to
  fail. **A guard nobody can show is needed should come out**, and saying so is cheaper than a
  paragraph explaining why it stays.

### Claims about your own work

- **Write what the code does; never write what it guarantees.** Both slices found the previous
  round's prose ahead of its code in nearly every round, *including sentences written
  specifically to stop overclaiming*. Assume your correction is the next overclaim.
- **Withdraw a count, do not correct it.** #32 corrected eight counts and every one was wrong
  again or wrong in the direction of making the work sound larger. #40 repeated it three times
  after being warned by this very list: a README said "the two tests" when a third surfaced, a
  round entry said "four mutations, all caught" while naming three, and a limitations file said
  "of those four" over five bullets. **Name the cases and let the reader count.** Positional
  references — "the last seven" — go stale exactly as counts do.
- **A correction removes the wrong statement; it does not merely add the right one.** #32 left
  a wrong mutation row standing beside its correction for two rounds.
- **A test's provenance is a factual claim.** #32 had a comment saying six cases survived a
  recorded regression when five had. #40 left three docstrings crediting a call that had
  already been replaced, and one test describing itself as a regression when it pinned nothing
  that had ever been broken. When a fix changes *why* a test passes, its docstring is now
  wrong.

### Verification

- **Measure the thing you are claiming.** #32 wrote a U+00A0 probe with an ordinary space and
  read the result as a false alarm. #40 checked for a doubled word with a line-scoped pattern
  against a duplication that spanned a line break, and nearly recorded a real defect as not
  reproducing. **A probe that finds nothing is evidence about the probe** until the probe
  itself is verified — which matters most when a finding is about to be rejected for failing
  to reproduce.
- **A check can pass for the wrong reason.** #32 had a case refused by a different rule than
  the one its test named. #40 had two: a test whose base was also HEAD, so the walk it meant to
  exercise saw no commits at all; and a test that patched out the helper it was meant to pin,
  so it verified only the caller. Construct each case so **only** the thing under test can
  produce the result — and where a precondition carries the test, assert the precondition.
- **Run mutations at BOTH edges of every rule.** A stricter mutation surviving is as much a gap
  as a looser one, and only the looser direction is intuitive to check. #32 found three gaps in
  the OVER-refusing direction — a rule silently narrowing what an adopter may write. #40's
  reviews found over-refusing defects repeatedly without mutation: a lookalike filename
  promoted to a marker, a directory named like a marker drawing a false deletion, an unreadable
  directory elsewhere in the tree blinding an absence that was independently provable. Its own
  over-refusing mutations were all caught, which is the outcome that shows a rule is not
  quietly stricter than it claims — so run them even when you expect them to be caught.

  *An earlier draft of this bullet said #40 "found three more" over-refusing gaps. It did not:
  its over-refusing mutations were caught, not survivors. The count was written from memory of
  the shape rather than the record, in the paragraph telling you not to do that.*
- **A mutation row must name the LITERAL edit run.** #32 mislabelled twice, both times
  describing a bigger mutation than the one performed, and a later round measured the
  difference.
- **A killed mutation run leaves the tree mutated.** #40 had a harness die at a harness timeout
  mid-mutation; three later results were measured against a file that still carried the
  previous edit and had to be rerun. Check the tree between runs, not only at the end.

### Review rounds

- **Audit each round's repairs for over-correction, not only the original question.** This is
  #40's most productive finding and it is not in #32's list. Three of #40's Majors were
  *introduced by the previous round's repair*, and one of them reopened the escape the issue
  existed to close. Asking "does this repair open a new state?" found a defect in three
  consecutive rounds.
- **Review briefs must not be worded adversarially.** #32 lost two rounds to a provider content
  filter — "produce an input that hides the ledger" reads as an attack request. Every round
  that completed asked the same question as **classifier correctness** ("which inputs does this
  classify wrongly, in either direction") or as a **completeness audit** ("enumerate the cases;
  for each say which rule governs it and whether that is correct"). Across both slices, the
  completeness-audit and repair-audit framings produced the most valuable rounds, and no round
  briefed that way was refused.
- **Tell the reviewer a clean round is a real outcome**, and list what the record already
  discloses so it is not re-raised. The disclosure list grows every round.
- **The builder can be wrong about a finding, and the reviewer can be wrong about a defect.**
  #40 rejected a Major whose reproduction did not reproduce against the revision it was filed
  against, and a later round independently confirmed the rejection. The same round found a
  defect the builder's own probe had missed. Neither side's report is evidence until it is run.

### Mechanics

- **Editing a large test file by slicing between anchors ate the module fixtures twice** in
  #32. `tests/test_validate.py` has two `PIN_OK` definitions, so a naive "cut to the next
  `class`" removes `CHANGELOG_OK` and its neighbours. Run `python3 -c "import
  tests.test_validate"` after any block edit. #40 used anchored insertion with that check after
  every edit and lost nothing.
- **An anchor that fails to match is a silent no-op if the write is unconditional.** #40 had a
  README edit assert-fail on text an earlier round had already replaced; the commit went out
  without it. Assert the match count, and check the result rather than the exit status.

## Where the plan lives
- Design: `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md`
- Plans: `docs/superpowers/plans/` (this file's siblings), one per phase-slice.
- **Loading:** these rules are no longer auto-loaded — `CLAUDE.md` is now the one-line `@AGENTS.md` import (D2 Move 2). Build sessions load this file by being pointed at it in the session kickoff; `AGENTS.md` links it under "Working on groundwork itself".
