---
name: feature-request-triage
description: File, deduplicate, and route each week's incoming feature requests to the owning product manager with the accounts that asked
action_class: reversible-write
provisioned: yes
baseline: memory/triage-baseline.md
ontology: ontologies/product/feature-request-triage.md
---
# Feature-request triage

Once a week, collect every feature request raised in support tickets, in CRM
opportunity and check-in notes, and by the customer-success team. For each one: check
whether the tracker already knows it and link the duplicate if so, tag it by theme,
attach the accounts that asked and the annual contract value they represent, and assign
it to the product manager who owns that theme.

Leave what you cannot place. A request matching no existing theme and no owning product
manager stays unassigned and goes to Dana Whitfield. Forcing it into the nearest tag is
how a signal disappears — an unassigned request is visible, a mis-tagged one is not.

This skill decides where a request goes, never whether it gets built. It does not set or
change roadmap priority, close a request, or reply to whoever raised it
([ontology record](../../ontologies/product/feature-request-triage.md);
[the rule that holds the customer boundary](../../governance/constitution/no-agent-contacts-a-customer.md)).

## Harness requirements
- The governed pre-provisioning baseline for triage latency and attribution
  completeness: [memory/triage-baseline.md](../../memory/triage-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the support-ticket system, CRM opportunities and their notes, and the
  customer-success team's check-in notes.
- Write access to the product tracker limited to creating items, editing tags and
  assignees, and adding duplicate links and triage notes.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. It is `reversible-write` because
  every write lands on an internal tracker item and is undone by retagging or
  unlinking, and nothing it writes reaches the person who raised the request. Giving it
  the ability to reply to a requester, close a request, or change priority would make it
  track 2, and the classification and Owner's Card would have to change first.
- Read-only access to the three source systems is a hard requirement, not a preference.
  A deployment that lets it edit CRM records breaks the claim above.

## Memory row
- **Reads:** the pre-provisioning triage baseline, and the at-risk-renewal records, so a
  request from an at-risk account carries that context into the tracker item.
- **Writes:** a weekly note recording how many requests were filed, deduplicated, and
  left unassigned (observed provenance).
- **Run-only:** the per-request candidate-duplicate scores.

## Portability check

*If I had to move this skill tomorrow, what would break?* The tracker, support-system,
and CRM connectors; the governed baseline record; the theme-to-manager ownership map the
assignment step reads; and the confirmation gate named in the Owner's Card.
