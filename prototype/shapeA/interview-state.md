---
# SHAPE A — one resumable state file. Everything lives here; rewritten every turn.
schema: interview-state/v0
started_in: claude-code
last_touched_in: claude-code
phase: cs-renewal          # resume pointer: which layer is in flight
status: awaiting-answer    # awaiting-answer | awaiting-approval | between-layers
open_question_id: q3
---

## Resume header  (an agent reads THIS block first)

You are mid-interview with Meridian. Layer `scope` is confirmed and approved. Layer
`cs-renewal` is in flight: two facts are confirmed, one is provisional (inferred from
the calendar), and there is ONE open question awaiting Sasha's answer. Do not
re-ask confirmed material. Ask `q3` (below), then fold the answer in.

## Role frame (layer 0)
Analyst role defined and approved. Consultant protocol: one question at a time,
checkpoint per layer, never generate before understanding.

## Confirmed facts
<!-- provenance: confirmed — approved by Sasha at a layer checkpoint. Frozen. -->
- [scope] Meridian = 22-person B2B SaaS. Functions: Sales, CS, Product, Engineering.
- [scope] Highest recurring pain: renewal prep (Customer Success).
- [cs-renewal] Activity "Renewal prep": CSM pulls usage → checks support history →
  drafts renewal brief → CS manager reviews. Motion = assist (human owns the send).

## Provisional facts
<!-- provenance: inferred/observed — agent's, NOT yet confirmed by the human. -->
- [cs-renewal] (inferred, source: calendar-export) Weekly "Renewal War Room" Tue,
  CS + Sales leads. Relationship to renewal prep UNKNOWN. Decision-owner UNKNOWN.

## Open questions
- id: q3  (status: pending)
  "Your calendar shows a weekly 'Renewal War Room' on Tuesdays with the CS + Sales
  leads. Is that part of renewal prep, or a separate escalation ritual? And who owns
  the decision that comes out of it?"

## Transcript digest
<!-- compressed running log; grows every turn -->
- t1 scope: functions + top pain → confirmed.
- t2 cs-renewal: renewal-prep steps + Motion=assist → confirmed.
- t3 cs-renewal: agent read calendar, surfaced War Room → provisional, asked q3.
