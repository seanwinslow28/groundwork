# Synthetic interview — the shared script both shapes encode

> PROTOTYPE — throwaway. The same 3 turns are frozen into Shape A and Shape B so we
> can compare *only the state format*, not the content.

Adopter: **Meridian**, a 22-person B2B SaaS. Maintainer "Sasha" runs the interview.
Started in **Claude Code**. Harness switch to **Cursor** happens mid-turn 3.

## Layer 0 — role definition (meta, agreed before questions)
Agent defined "good vs bad organizational analyst," Sasha approved. Not a fact about
Meridian; it's the protocol frame. (Both shapes note it once.)

## Turn 1 — scope (LAYER: scope) — CHECKPOINT APPROVED
Q: "What does Meridian do, and which functions feel the most recurring pain?"
A: "B2B SaaS, 22 people. Functions: Sales, Customer Success, Product, Engineering.
   The biggest recurring grind is **renewal prep** in Customer Success."
→ Sasha approved this layer. Facts are CONFIRMED.

## Turn 2 — CS renewal activity (LAYER: cs-renewal) — CHECKPOINT APPROVED
Q: "Walk me through renewal prep, step by step."
A: "The CSM pulls product-usage data, checks the support-ticket history, drafts a
   renewal brief, and the CS manager reviews it before it goes to the customer."
→ Agent typed this as an activity with Motion = **assist** (human owns the send).
→ Sasha approved this layer. Facts are CONFIRMED.

## Turn 3 — evidence reflection (LAYER: cs-renewal, still open) — IN FLIGHT
With permission, the agent read Meridian's shared Google Calendar export and found a
recurring **"Renewal War Room"** every Tuesday that Sasha never mentioned.
Agent reflects it back:

Q (PENDING, unanswered): "Your calendar shows a weekly 'Renewal War Room' on Tuesdays
   with the CS + Sales leads. Is that part of renewal prep, or a separate escalation
   ritual? And who owns the decision that comes out of it?"

→ This produced a PROVISIONAL fact: an inferred activity ("Renewal War Room, weekly,
   CS+Sales") that the human has NOT confirmed. Provenance = inferred (from calendar).

### *** HARNESS SWITCH HAPPENS HERE ***
Sasha closes Claude Code and reopens the repo in Cursor to answer the pending question.
A fresh agent, no memory, must reconstruct: where are we, what's locked, what's just a
guess, and what's the next thing to ask.
