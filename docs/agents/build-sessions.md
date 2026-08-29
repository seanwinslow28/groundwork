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
   review round run against it — findings, severities, and dispositions (fixed in commit X /
   rejected with grounds), not just the final approve — are committed in the repository. A
   slice with a plan stores them beside it, at `docs/superpowers/plans/<slice>-reviews.md`;
   plan-less work uses `docs/superpowers/reviews/<branch>.md`, with any `/` in the branch
   name written as `-` so the log stays a single file directly under `reviews/`. The log is
   appended per round, on the branch, so the merge carries the record: a later round amends
   an earlier row by superseding it, never by rewriting the earlier round's table.
   *Evidence:* the session that landed rule 8 ran twenty-five rounds — sixteen on the
   groundwork branch, nine on the persona-company correction, per merge commit `df6df21` —
   and what survives is what the fix commits and the merge chose to quote. Three of the
   sixteen left no numbered commit in the `fix(build): Codex r…` sequence: r16 approved, and
   `df6df21` carries that verdict and both round counts; r3 and r9 left nothing, there or
   anywhere else in the repository. No complete round output survives for any of the sixteen. The honesty plan paid the same cost
   earlier: its header records that its three rounds' "review outputs were not retained",
   leaving the merge as the durable record of the approval, with "no inspectable artifact"
   dating round 3 itself. The non-gating rounds are where the pattern data lives — the
   recurring parallel-site drift class, whose "seventh instance" `18fa805` names, and the
   four factual defects rule 8 counts — so a log of approvals alone would keep none of it.
   *Worked example:* `docs/superpowers/reviews/spec-roles-accountable-unit.md`, written
   prospectively on the branch that proposed this rule — twenty-five rounds, 102 findings,
   every disposition, one approving verdict. The rule and its counter-argument are locked as
   decision 7 of the 2026-08-28 roles-as-the-accountable-unit design, under
   `docs/superpowers/specs/`.

## Where the plan lives
- Design: `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md`
- Plans: `docs/superpowers/plans/` (this file's siblings), one per phase-slice.
- **Loading:** these rules are no longer auto-loaded — `CLAUDE.md` is now the one-line `@AGENTS.md` import (D2 Move 2). Build sessions load this file by being pointed at it in the session kickoff; `AGENTS.md` links it under "Working on groundwork itself".
