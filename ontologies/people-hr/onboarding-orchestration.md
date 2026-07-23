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
accountable_owner: Head of People
substrate: HRIS + IT provisioning tracker + the onboarding checklist doc
shape: single-agent
gate_inputs: The new hire's start date, role, manager, equipment needs, and required system accesses, from the signed offer and the IT intake form
gate_output: A completed onboarding checklist — accounts provisioned, equipment ordered, the day-one schedule sent, manager and buddy notified
gate_standard: Every new hire has working accounts, equipment en route, and a scheduled first week before their start date
gate_source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
gate_exception_path: A non-standard role or missing intake data pauses to the Head of People; contractor-to-employee conversions route to Legal first
gate_error_cost: A missed access or late laptop delays a hire's first day — recoverable within a day, embarrassing, not dangerous
gate_owner: Head of People
gate_review_gate: The hiring manager confirms the checklist is complete on day one
---
# Onboarding orchestration

**Direction: down.** The manual coordination of accounts, equipment, and day-one
logistics should stop being hand-run — it is high-repetition, low-judgment routing
work with a clear source of truth, which is exactly what should be automated so the
People team's time goes to the human parts of joining a company.

**Motion: automate.** Repetition is high, risk and judgment are low, the workflow is
only moderately company-specific, and the market for onboarding automation is mature.

## Accountability

Which business process runs differently: the pre-start onboarding runbook stops being
a person hand-working a checklist and becomes an agent that provisions, orders, and
schedules against the HRIS record, pausing to a human on any exception.

Who is accountable for proving it improved: the **Head of People**, measured against a
baseline of time-to-day-one-ready and day-one readiness captured **before** provisioning
(the captured baseline is a governed org-memory record — Slice 1.4 — and no skill
provisions for this activity without one).
