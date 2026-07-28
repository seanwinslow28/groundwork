---
activity: Feature-request triage
function: Product
motion: automate
score_repetition: high
score_risk: low
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: routing
accountable_owner: Director of Product
substrate: The issue tracker + the support-ticket system + CRM opportunity notes + the community forum
shape: single-agent
gate_inputs: Every feature request raised in the last week across support tickets, sales-call notes on CRM opportunities, and the community forum, plus the existing tracker items they might duplicate
gate_output: Each request filed in the tracker as a new item or linked to the one it duplicates, tagged by theme and customer segment, carrying the accounts that asked and the ARR they represent, and assigned to the owning PM
gate_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days, and every request in the tracker names the accounts it came from
gate_source_of_truth: The issue tracker for what is already known; the CRM for account and ARR attribution
gate_exception_path: A request that matches no existing theme and no owning PM is left unassigned and raised to the Director of Product rather than being forced into the nearest tag
gate_error_cost: A misfiled or wrongly deduplicated request loses a customer signal until someone notices it in the next review — recoverable by refiling, invisible to the customer
gate_owner: Director of Product
gate_review_gate: The owning PM confirms the theme and the duplicate link when the request reaches their queue
---
# Feature-request triage

**Direction: down.** Reading every incoming request, checking whether it is already
known, attaching who asked and what they are worth, and routing it to the right PM is
high-volume clerical work that produces no product judgment. It should stop being
hand-run so PM time goes to deciding what to build.

**Motion: automate.** Repetition is high, the sources are all systems of record, and
the failure mode is recoverable. Judgment scores **medium** and stays with a human:
this activity decides where a request *goes*, never whether it gets built.

## Accountability

Which business process runs differently: triage stops being a PM working through a
week of tickets, calls, and forum posts before they can think about the roadmap, and
becomes an agent that files, deduplicates, attributes, and routes — leaving anything
it cannot place unassigned and visible rather than guessing at a tag.

Who is accountable for proving it improved: the **Director of Product**, measured
against a baseline of triage latency and attribution completeness captured **before**
provisioning (the captured baseline is a governed org-memory record, and no skill
provisions for this activity without one — the #5 provisioning gate).
