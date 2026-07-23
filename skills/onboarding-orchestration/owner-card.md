---
owner: Head of People
backup_owner: People Ops Lead
job: Provision every new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
allowed_actions: create accounts in the HRIS/IT tracker; order standard equipment; send the day-one schedule; notify manager and buddy
proposed_only_actions: grant non-standard system access; convert a contractor to an employee
forbidden_actions: approve compensation; sign offer letters; delete employee records
pause_condition: the HRIS or IT tracker is unreachable, or required intake data is missing
retirement_condition: onboarding moves to a dedicated HRIS-native workflow the team trusts more
source_of_truth: The HRIS record for the hire; the IT provisioning tracker for access state
review_cadence: monthly
known_failure_modes: none observed yet; on other harnesses the action-class hard-block degrades to an advisory review gate (#19)
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
pauses to a human on any exception. It may propose — never unilaterally perform —
non-standard access grants and contractor conversions, and it may never touch
compensation, offers, or record deletion. It pauses when its sources of truth are
unreachable, and it should be retired once a trusted HRIS-native workflow supersedes it.
