---
name: onboarding-orchestration
description: Provision a new Umbercress hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
baseline: memory/onboarding-baseline.md
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Onboarding orchestration

Provision every new hire before their start date: create standard-role accounts, order
approved standard equipment, send the day-one schedule, and notify the hiring manager
and the buddy. Work from the signed offer and the IT intake form, and record every
access in the IT provisioning tracker as it lands.

Pause rather than improvise. A non-standard role, a non-standard access request, or
missing intake data stops and routes to Ruth Okafor; a contractor-to-employee conversion
routes to outside counsel first. On day one the hiring manager confirms the completed
checklist against the hire's actual readiness
([ontology record](../../ontologies/people-hr/onboarding-orchestration.md)).

## Harness requirements
- The governed pre-provisioning baseline for time-to-day-one-ready and day-one
  readiness: [memory/onboarding-baseline.md](../../memory/onboarding-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read/write access to the HR information system, the IT provisioning tracker, and the
  standard-role account-provisioning systems.
- Permission to order approved standard equipment and to send calendar invites and
  onboarding messages to people inside the company.
- No permissions for non-standard access grants, discretionary spend, compensation,
  offers, or record deletion (see the Owner's Card).

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This is the one Umbercress package on **track 2**: it creates accounts, spends money
  on equipment, and sends messages, and none of that is undone by editing a document.
- This package ships no runtime action-class hook of its own. Its external-side-effect
  gate is a review instruction on every harness — a person confirms before accounts are
  created, equipment is ordered, or messages go out. The engine's fixed action-class
  gate is where runtime enforcement lives when a company installs it.

## Memory row
- **Reads:** the pre-provisioning onboarding baseline (time-to-day-one-ready).
- **Writes:** an onboarding-completed note per hire (observed provenance).
- **Run-only:** the per-run checklist state, which is not persisted to org memory.

## Portability check

*If I had to move this skill tomorrow, what would break?* The HR information system, IT
tracker, account-provisioning, equipment-ordering, calendar, and messaging connectors;
the governed baseline record; and the day-one confirmation gate named in the Owner's
Card.
