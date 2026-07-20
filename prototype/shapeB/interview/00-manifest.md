---
# SHAPE B — per-phase checkpoint artifacts. This manifest is the ONLY moving pointer.
schema: interview-manifest/v0
started_in: claude-code
last_touched_in: claude-code
phase: cs-renewal
status: awaiting-answer
---

## Resume header  (an agent reads THIS file first, then follows the pointers)

Confirmed layers are frozen files below — each was committed at its checkpoint, so
`git log` is the approval trail. The in-flight turn lives in `_working.md`. To resume:
read the confirmed layers for context, then open `_working.md` for the provisional
fact and the open question.

## Layers
| order | file                | provenance | committed | last-in |
|-------|---------------------|------------|-----------|---------|
| 0     | (role frame — in this manifest) | frame | — | — |
| 1     | 01-scope.md         | confirmed  | ✅ commit  | claude-code |
| 2     | 02-cs-renewal.md    | confirmed  | ✅ commit  | claude-code |
| 3     | _working.md         | in-flight  | ❌ dirty   | claude-code |

## Role frame (layer 0)
Analyst role defined and approved. Consultant protocol: one question at a time,
checkpoint per layer, never generate before understanding.

## Next action
Answer open question `q3` in `_working.md`. On approval: promote `_working.md`
→ frozen `03-*.md`, commit, clear `_working.md`.
