---
activity: Renewal preparation
function: Customer success
motion: automate
score_repetition: high
score_risk: low
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: sensemaking
accountable_owner: VP Customer Success
substrate: The CRM opportunity and contract records + the product-usage warehouse + the support-ticket system
shape: single-agent
gate_inputs: The renewing account's contract terms and renewal date from the CRM, its last-90-day product usage, its open and recently closed support tickets, and the notes from the most recent business review
gate_output: A renewal brief in the CS workspace — contract terms, usage trend against the account's own history, support history, named risks, and an expansion or contraction read — with every claim linked to the record it came from
gate_standard: Every renewal has a brief in the CSM's hands 45 days before the renewal date, and every number in it resolves to a source record
gate_source_of_truth: The CRM contract record for terms and dates; the usage warehouse for product adoption
gate_exception_path: A missing or contradictory contract record, or usage data more than seven days stale, halts the brief and routes to the VP Customer Success rather than shipping a brief with a gap in it
gate_error_cost: A wrong or missing brief sends a CSM into a renewal conversation underprepared — costly if it goes unnoticed, but caught by the CSM's own review before any customer sees it
gate_owner: VP Customer Success
gate_review_gate: The account's CSM reads the brief and confirms it matches what they know before the renewal conversation
---
# Renewal preparation

**Direction: down.** Assembling the picture before a renewal — pulling contract terms,
reading the usage trend, re-reading the support history — is hours of gathering that
produces no judgment. It should stop being hand-run so the CSM's time goes to the
renewal conversation itself.

**Motion: automate.** Repetition is high and the sources are all systems of record.
Judgment scores **medium**, and that is the point of the boundary: the *gathering* is
mechanical, the *decision* is not. This activity ends at a brief a human reads; it
never decides the renewal, prices it, or contacts the customer.

## Accountability

Which business process runs differently: renewal prep stops being a CSM working
through four systems the week before a renewal and becomes an agent that assembles a
sourced brief 45 days out, halting to a human when a record is missing or stale rather
than filling the gap with an assumption.

Who is accountable for proving it improved: the **VP Customer Success**, measured
against a baseline of brief lead time and sourcing completeness captured **before**
provisioning (the captured baseline is a governed org-memory record, and no skill
provisions for this activity without one — the #5 provisioning gate).
