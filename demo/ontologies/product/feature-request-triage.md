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
accountable_owner: Dana Whitfield
substrate: The product tracker + the support-ticket system + CRM opportunity notes
shape: single-agent
gate_inputs: Every feature request raised in the last week in support tickets, in CRM opportunity and check-in notes, and by the customer-success team, plus the existing tracker items they might duplicate
gate_output: Each request filed in the tracker as a new item or linked to the one it duplicates, tagged by theme, carrying the accounts that asked and the annual contract value they represent, and assigned to its owning product manager
gate_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days, and every tracker item names the accounts it came from
gate_source_of_truth: The product tracker for what is already known; the CRM for account and contract-value attribution
gate_exception_path: A request that matches no existing theme and no owning product manager is left unassigned and raised to Dana Whitfield rather than being forced into the nearest tag
gate_error_cost: A misfiled or wrongly deduplicated request loses a customer signal until the next roadmap review — recoverable by refiling, invisible to the customer
gate_owner: Dana Whitfield
gate_review_gate: The owning product manager confirms the theme and the duplicate link when the request reaches their queue
---
# Feature-request triage

**Direction: down.** Reading every incoming request, checking whether it is already
known, attaching who asked and what they are worth, and routing it is high-volume
clerical work that produces no product judgment. With two people in product, it should
stop being hand-run.

**Motion: automate.** Repetition is high, the sources are systems of record, and the
failure mode is recoverable. Judgment scores **medium** and stays human: this activity
decides where a request *goes*, never whether it gets built.

## Accountability

Which business process runs differently: triage stops being a product manager working
through a week of tickets and call notes before they can think about the roadmap, and
becomes an agent that files, deduplicates, attributes, and routes — leaving anything it
cannot place unassigned and visible rather than guessing at a tag.

Who is accountable for proving it improved: **Dana Whitfield**, measured against a
baseline of triage latency and attribution completeness captured before provisioning
(see [the captured baseline](../../memory/triage-baseline.md)).
