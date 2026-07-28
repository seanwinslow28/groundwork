---
owner: Ruth Okafor
backup_owner: Priya Raman
job: Provision every new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
allowed_actions: create standard-role accounts in approved systems and record status in the IT provisioning tracker; order approved standard equipment; send the day-one schedule; notify the hiring manager and the buddy
proposed_only_actions: grant a non-standard system access after Ruth Okafor approves; convert a contractor to an employee after outside counsel reviews
forbidden_actions: approve compensation; sign offer letters; delete employee records; contact anyone outside the company
pause_condition: the HR information system or the IT tracker is unreachable; required intake data is missing; a non-standard role or access is requested; a contractor-to-employee conversion is in scope
retirement_condition: onboarding moves to a workflow inside the HR information system that the team trusts more
source_of_truth: The HR information system record for the hire; the IT provisioning tracker for access state
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package, so every harness relies on the human review gate for external side effects; an account created against a stale intake form looks identical to a correct one until day one
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every new hire is day-one-ready — accounts, equipment, and schedule — before their start date, measured against the pre-provisioning baseline of five business days' median time-to-ready and five of nine hires ready on the first morning
evidence_required: The completed onboarding checklist with per-item timestamps, and the provisioning log showing who approved each non-standard access
sources_must_not_use: A personal email account or a chat thread as a source of truth for an access grant
review_sample: The hiring manager confirms every checklist on day one; Ruth Okafor spot-checks one onboarding a week against the provisioning log
---
# Owner's Card — Onboarding orchestration

**Ruth Okafor** owns this skill; **Priya Raman** is the backup — at twenty people, one
person runs People operations and the CEO is the fallback, which is worth writing down
rather than discovering during a holiday.

It provisions against the HR information system record and pauses non-standard roles or
access to Ruth Okafor, and contractor conversions to outside counsel. It may *propose*
those exceptions and never perform them. It may never touch compensation, offers, or
record deletion, and it may not contact anyone outside the company.

This is the company's only track-2 skill, so the card carries the full evidence trio:
what the run must produce, what it may never treat as a source, and who reads a sample.
The hiring manager's day-one confirmation is the review gate. It should be retired once
the HR information system does this natively and the team trusts it more.
