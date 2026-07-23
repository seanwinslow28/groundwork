---
name: onboarding-orchestration
description: Provision a new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
baseline: memory/onboarding-baseline.md
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Onboarding orchestration

Provision every new hire before their start date: create standard-role accounts,
order approved standard equipment, send the day-one schedule, and notify the manager
and buddy. Pause a non-standard role, non-standard access, or missing intake data to
the accountable owner named in the Owner's Card; route contractor-to-employee
conversions to Legal first. Generated for the People/HR onboarding-orchestration
activity. On day one, the hiring manager confirms that the completed checklist matches
the hire's actual readiness
([ontology record](../../ontologies/people-hr/onboarding-orchestration.md)).

## Harness requirements
- A governed pre-provisioning baseline for time-to-day-one-ready and day-one
  readiness: [memory/onboarding-baseline.md](../../memory/onboarding-baseline.md)
  (the `baseline:` this skill cites — the #5 provisioning gate).
- Read/write access to the HRIS, the IT provisioning tracker, and approved
  standard-role account-provisioning systems.
- Permission to order approved standard equipment and to send calendar invites and
  onboarding emails.
- No permissions for non-standard access grants, discretionary spend, compensation,
  offers, or record deletion (see the Owner's Card).

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package does not ship a runtime action-class hook. Its external-side-effect
  gate is a review instruction on every harness: a human confirms before accounts
  are created, equipment is ordered, or messages are sent. Runtime hook enforcement
  is deferred to the fixed governance hook set.

## Memory row
- **Reads:** the pre-provisioning onboarding baseline (time-to-day-one-ready).
- **Writes:** an onboarding-completed note per hire (observed provenance).
- **Run-only:** the per-run checklist state (not persisted to org memory).

## Portability check

*If I had to move this skill tomorrow, what would break?* The HRIS, IT tracker,
account-provisioning, equipment-ordering, calendar, and email connectors; the governed
baseline record; and the human review gate named in the Owner's Card must all move with
it.
