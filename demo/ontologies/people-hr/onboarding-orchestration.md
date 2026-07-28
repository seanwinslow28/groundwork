---
activity: Onboarding orchestration
function: People/HR
motion: automate
score_repetition: high
score_risk: low
score_judgment: low
score_company_specificity: medium
score_market_maturity: high
work_type: routing
accountable_owner: Ruth Okafor
substrate: The HR information system + the IT provisioning tracker + the onboarding checklist
shape: single-agent
gate_inputs: The new hire's start date, role, manager, equipment needs, and required system accesses, from the signed offer and the IT intake form
gate_output: A completed onboarding checklist — accounts provisioned, equipment ordered, the first-week schedule sent, manager and buddy notified
gate_standard: Every new hire has working accounts, equipment en route, and a scheduled first week before their start date
gate_source_of_truth: The HR information system record for the hire; the IT provisioning tracker for access state
gate_exception_path: A non-standard role or missing intake data pauses to Ruth Okafor; contractor-to-employee conversions route to outside counsel first
gate_error_cost: A missed access or a late laptop delays a hire's first day — recoverable within a day, embarrassing, not dangerous
gate_owner: Ruth Okafor
gate_review_gate: The hiring manager confirms the checklist is complete on day one
---
# Onboarding orchestration

**Direction: down.** One person runs all of People operations at Umbercress. The
coordination of accounts, equipment, and first-week logistics is high-repetition,
low-judgment routing with a clear source of truth, and it should stop being hand-run
so that time goes to the human parts of someone joining a company.

**Motion: automate.** Repetition is high, risk and judgment are low, the workflow is
only moderately company-specific, and the market for onboarding automation is mature.

## Accountability

Which business process runs differently: the pre-start runbook stops being a person
hand-working a checklist and becomes an agent that provisions, orders, and schedules
against the HR system record, pausing to a human on any exception.

Who is accountable for proving it improved: **Ruth Okafor**, measured against a
baseline of time-to-day-one-ready and day-one readiness captured before provisioning
(see [the captured baseline](../../memory/onboarding-baseline.md)).
