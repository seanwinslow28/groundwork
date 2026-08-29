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
   review round run against it are committed in the repository. **This is the operative
   text.** Decision 7 of the 2026-08-28 roles-as-the-accountable-unit design, under
   `docs/superpowers/specs/`, records the decision, its evidence and its counter-argument,
   and points here for the contract.

   **Where.** One directory per branch or slice, one file per round, never edited after its
   round has passed: `docs/superpowers/reviews/<branch-slug>/round-NN.md` for plan-less
   work, or `docs/superpowers/plans/<slice>-reviews/round-NN.md` beside a plan, where
   `<slice>` is the plan's filename without its date prefix. `<branch-slug>` is the branch
   name's last path component; if that directory is already taken by unrelated work, add
   `-2`, `-3`. A `README.md` in the same directory carries the parts that keep changing:
   what each round reviewed, the fix-commit map, the rejected findings, and any open
   maintainer items.

   **What a round file carries.** The reviewed revision as a commit SHA — a review runs
   against a clean worktree — the verdict, and every finding with the reviewer's own
   severity word kept verbatim, plus its disposition. A finding may be summarised rather
   than quoted in full. A disposition is **fixed in commit X** or **rejected with grounds**,
   and nothing else. A finding that is neither is unresolved, and a branch carrying an
   unresolved finding does not merge under this rule. The builder may reject a finding; every
   rejected one is also listed in the directory's `README.md`, so the single move that closes
   a finding by disagreeing with it cannot be buried inside a round file.

   **Every invocation gets a file**, including one that crashed or was abandoned — disposition
   "aborted, no verdict" — so a missing round shows as a gap in the numbering rather than as
   nothing at all.

   **The terminal round.** The last verdict is committed after the state it reviewed, so that
   commit is not itself reviewed. That is accepted, and said here rather than exempted. The
   final verdict must be approving unless the maintainer records the grounds for merging over
   it in the merge commit, as `5fc61c6` did for slice 2.1.

   *Evidence:* the session that landed rule 8 ran twenty-five review rounds and kept no round
   output; three of its sixteen groundwork rounds left no numbered fix commit, and two of
   those left nothing anywhere. Decision 7 carries the full account.
   *Worked example:* `docs/superpowers/reviews/spec-roles-accountable-unit.md` — 25 rounds,
   102 findings, every disposition, one approving verdict, with its fix-commit map
   backfilled. It predates the per-round layout above, which binds work started after this
   rule lands.

## Where the plan lives
- Design: `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md`
- Plans: `docs/superpowers/plans/` (this file's siblings), one per phase-slice.
- **Loading:** these rules are no longer auto-loaded — `CLAUDE.md` is now the one-line `@AGENTS.md` import (D2 Move 2). Build sessions load this file by being pointed at it in the session kickoff; `AGENTS.md` links it under "Working on groundwork itself".
