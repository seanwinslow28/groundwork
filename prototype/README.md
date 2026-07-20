# Prototype — interview state format (ticket #9)

> **THROWAWAY.** Captured primary source for [ticket #9](https://github.com/seanwinslow28/groundwork/issues/9).
> Not product code; nothing here graduates to `main`. Kept so the resolution is
> reproducible.

**Question:** one resumable state file vs per-phase checkpoint artifacts — what survives
a harness switch mid-interview, and how are confirmed-vs-provisional facts encoded?

**Verdict: Shape B (per-phase checkpoint artifacts).** Confirmed layers are committed,
frozen files (`git log` = the approval trail); the in-flight turn is a single dirty
`_working.md` (the provisional state). This encodes confirmed-vs-provisional as git
structure rather than agent-honored labels, inherits #10's "checkpoint = commit"
substrate for free, stays inside #13's context budget (fixed-size manifest, no
unbounded transcript reload), and matches #7's frozen-at-commit doctrine.

## Files
- `SYNTHETIC-INTERVIEW.md` — the shared 3-turn script both shapes encode.
- `shapeA/interview-state.md` — Shape A (rejected): one file, rewritten each turn.
- `shapeB/interview/` — Shape B (chosen): manifest + frozen layer files + `_working.md`.
- `shapeB/GITLOG.txt` — real checkpoint-as-commit evidence from the throwaway repo.
- `RESUME-TRACE.md` — the head-to-head Cursor-resume comparison and the crux.
