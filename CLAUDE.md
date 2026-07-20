# groundwork — charting phase

> **TEMPORARY FILE.** This CLAUDE.md supports wayfinder map-working sessions only. When the map is complete and build sessions scaffold the product, it is replaced by the product's own root files (a one-line `@AGENTS.md` import, per the design brief §6).

## What this repo is

An open-source, harness-agnostic Company OS — ontology-first generation + compiled governance + governed self-improvement. **Nothing is built yet, deliberately.** The design is being resolved in public as a wayfinder map of decision tickets.

- **The map:** https://github.com/seanwinslow28/groundwork/issues/1
- **Source of truth:** the approved design brief — [code-brain: docs/plans/2026-07-15-company-os-design-brief.md](https://github.com/seanwinslow28/code-brain/blob/376dd5af85cd25fe06bcbe3fc9c366c022a94332/docs/plans/2026-07-15-company-os-design-brief.md). Decisions locked there are not re-opened without new evidence.
- **Tracker conventions:** [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md) (GitHub via `gh`; native sub-issues + dependencies)
- **Resolved research:** [research/](research/) — SKILL.md portability + context-budget findings (evidence for tickets #12/#13)

## Session rules (wayfinder)

1. **One ticket per session.** Resolve it, record it, chart what it revealed, stop. The pull to keep going is the signal to stop.
2. **Claim before work:** assign the ticket to the driving dev (`gh issue edit <n> --add-assignee @me`) as the session's first write.
3. **Self-brief before the first question:** read the ticket's linked brief sections, any linked research reports, and the map's Decisions-so-far. The tickets are sharp questions with evidence links — not specs; the session's output is a *decision*, not an implementation.
4. **Grilling tickets are HITL:** one question at a time, answered by Sean. Never answer on his behalf.
5. **Factual gap mid-grilling?** Do a bounded first-party check (official docs only) or spawn a `wayfinder:research` ticket and wire it as a blocker — don't improvise facts.
6. **Resolve = comment + close + map index line** (gist + link in Decisions-so-far). New tickets and graduated fog get charted before the session ends.
7. **No product scaffolding** while tickets remain. Charting artifacts (docs/, research/) are fine; `interview/`, `ontologies/`, `skills/`, `governance/` etc. are build-phase.
8. **Honesty rules:** claims match what research verified, including prior-art concessions (brief §2). Overclaiming is trust debt.
9. **Explain before asking Sean to decide.** Sean is new to building this kind of system. Before each decision question, explain in plain terms: what the decision is about, what the options are, why you recommend what you recommend, and the honest counter-argument to your own recommendation. Never accept "I'll go with your recommendation" as a substitute for understanding — the goal is that Sean could re-explain the decision to someone else. Applies to grilling tickets now and carries into build sessions (also saved in agent memory so it survives this file's replacement).

## Process notes

- Build sessions (post-map) use Fable 5 with the Codex plugin as review gate (`/codex` review or `codex:codex-rescue`).
- License is undecided (ticket #3) — README carries the placeholder until it lands.
