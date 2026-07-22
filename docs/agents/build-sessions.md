# Build-session rules (groundwork build phase)

> Replaces the wayfinder charting rules now that the map is complete. These are workbench rules for build sessions; they are NOT product content and never ship to adopters.

## Session shape
1. **One increment per session.** Build it, `validate` green, Codex-review, record what it revealed, stop. The pull to keep going is the signal to stop.
2. **One increment ends green:** `python3 scripts/validate.py` passes (zero ERRORs) before a session is done.
3. **Review gate:** Fable 5 builds; the Codex plugin reviews at session end (`/codex` review or `codex:codex-rescue`); the maintainer (Sean) lands the merge — the commit bit is the governance teeth (#18).
4. **Claim before work:** branch before touching the tree (never build on `main`).

## Standing rules (carried from charting)
5. **Explain before Sean decides.** Before each decision he owns, explain in plain terms: what it is, the options, the recommendation, and the honest counter-argument. Never accept "go with your recommendation" as a substitute for understanding.
6. **Honesty rules:** claims match what is verified/built; no capability claim precedes the capability; overclaiming is trust debt.
7. **Source of truth:** the approved design brief and CONTEXT.md (the resolved-decision glossary). Locked decisions are not reopened without new evidence.

## Where the plan lives
- Design: `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md`
- Plans: `docs/superpowers/plans/` (this file's siblings), one per phase-slice.
