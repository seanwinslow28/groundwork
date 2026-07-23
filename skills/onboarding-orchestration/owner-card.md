---
owner: Head of People
backup_owner: People Ops Lead
job: Provision every new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
allowed_actions: create standard-role accounts in approved systems and record status in the IT provisioning tracker; order approved standard equipment; send the day-one schedule; notify manager and buddy
proposed_only_actions: grant non-standard system access after Head of People approval; convert a contractor to an employee after Legal review
forbidden_actions: approve compensation; sign offer letters; delete employee records
pause_condition: the HRIS or IT tracker is unreachable; required intake data is missing; a non-standard role or access is requested; contractor-to-employee conversions route to Legal first
retirement_condition: onboarding moves to a dedicated HRIS-native workflow the team trusts more
source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; every harness relies on the human review gate for external side effects
last_reviewed: 2026-07-20
next_review: 2026-10-20
success_standard: Every new hire is day-one-ready (accounts + equipment + schedule) before their start date, measured against the pre-provisioning baseline
evidence_required: The completed onboarding checklist with per-item timestamps and the provisioning log
sources_must_not_use: Personal email or chat threads as a source of truth for access grants
review_sample: One onboarding per week spot-checked by the hiring manager
---
# Owner's Card — Onboarding orchestration

The **Head of People** owns this skill; the **People Ops Lead** is the backup. It
runs the onboarding runbook as an agent that provisions against the HRIS record and
pauses non-standard roles or access to the Head of People and contractor conversions
to Legal. It may propose — never unilaterally perform — those exceptions, and it may
never touch compensation, offers, or record deletion. It also pauses when its sources
of truth are unreachable. The hiring manager confirms every checklist on day one, and
the weekly sample is an additional quality review. The skill should be retired once a
trusted HRIS-native workflow supersedes it.
