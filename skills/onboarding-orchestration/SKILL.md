---
name: onboarding-orchestration
description: Provision a new hire's accounts, equipment, and first-week schedule before day one
action_class: external-side-effect
provisioned: yes
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Onboarding orchestration

Provision every new hire before their start date: create accounts, order standard
equipment, send the day-one schedule, and notify the manager and buddy — pausing to
a human on any exception. Generated for the People/HR onboarding-orchestration
activity ([ontology record](../../ontologies/people-hr/onboarding-orchestration.md)).

## Harness requirements
- Read/write access to the HRIS and the IT provisioning tracker.
- Permission to send calendar invites and onboarding emails.
- No spend and no deletion permissions (see the Owner's Card forbidden actions).

## Compatibility notes
- Tested in Claude Code (action-class hooks enforce the external-side-effect gate).
- On Codex / Cursor / Gemini CLI the action-class hook is absent; the same gate
  ships as a review-gate instruction (#19) — a human confirms before accounts are
  created. What breaks silently otherwise: nothing structural, but the hard-block
  becomes advisory, so the review gate is mandatory there.

## Memory row
- **Reads:** the pre-provisioning onboarding baseline (time-to-day-one-ready).
- **Writes:** an onboarding-completed note per hire (observed provenance).
- **Run-only:** the per-run checklist state (not persisted to org memory).
