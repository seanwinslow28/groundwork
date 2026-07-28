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
accountable_owner: Marcus Bell
substrate: The CRM contract and opportunity records + the Relay usage warehouse + the support-ticket system
shape: single-agent
gate_inputs: The renewing account's contract terms and renewal date from the CRM, its last-90-day Relay usage, its open and recently closed support tickets, and the notes from its most recent quarterly check-in
gate_output: A renewal brief in the customer-success workspace — contract terms, usage trend against the account's own history, support history, named risks, and an expansion or contraction read — with every claim linked to the record it came from
gate_standard: Every renewal has a brief in its CSM's hands 45 days before the renewal date, and every number in it resolves to a source record
gate_source_of_truth: The CRM contract record for terms and dates; the Relay usage warehouse for product adoption
gate_exception_path: A missing or contradictory contract record, or usage data more than seven days stale, halts the brief and routes to Marcus Bell rather than shipping a brief with a gap in it
gate_error_cost: A wrong or missing brief sends a CSM into a renewal conversation underprepared — costly if unnoticed, but caught by the CSM's own review before any customer sees it
gate_owner: Marcus Bell
gate_review_gate: The account's CSM reads the brief and confirms it matches what they know before the renewal conversation
---
# Renewal preparation

**Direction: down.** With about 60 accounts on annual contracts and three people in
customer success, assembling the picture before a renewal is hours of gathering that
produces no judgment. It should stop being hand-run so CSM time goes to the renewal
conversation itself.

**Motion: automate.** Repetition is high and every source is a system of record.
Judgment scores **medium**, and the boundary is the point: the gathering is mechanical,
the decision is not. This activity ends at a brief a human reads. It never decides the
renewal, prices it, or contacts the customer.

## Accountability

Which business process runs differently: renewal prep stops being a CSM working
through three systems the week before a renewal and becomes an agent that assembles a
sourced brief 45 days out, halting to a human when a record is missing or stale rather
than filling the gap with an assumption.

Who is accountable for proving it improved: **Marcus Bell**, measured against a
baseline of brief lead time and sourcing completeness captured before provisioning
(the #5 provisioning gate — see [the captured baseline](../../memory/renewal-prep-baseline.md)).
