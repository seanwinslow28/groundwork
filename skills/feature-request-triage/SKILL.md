---
name: feature-request-triage
description: File, deduplicate, and route each week's incoming feature requests to the owning PM with the accounts that asked
action_class: reversible-write
provisioned: yes
baseline: memory/feature-request-triage-baseline.md
ontology: ontologies/product/feature-request-triage.md
---
# Feature-request triage

Once a week, collect every feature request raised in support tickets, sales-call notes
on CRM opportunities, and the community forum. For each one: check whether the tracker
already knows it and link the duplicate if so, tag it by theme and customer segment,
attach the accounts that asked and the ARR they represent, and assign it to the PM who
owns that theme.

Leave what you cannot place. A request that matches no existing theme and no owning PM
stays unassigned and goes to the Director of Product. Forcing it into the nearest tag
is how a signal disappears — an unassigned request is visible, a mis-tagged one is not.

This skill decides where a request goes, never whether it gets built. It does not set
or change roadmap priority, close a request as won't-do, or reply to the person who
raised it ([ontology record](../../ontologies/product/feature-request-triage.md)).

## Harness requirements
- A governed pre-provisioning baseline for triage latency and attribution
  completeness: [memory/feature-request-triage-baseline.md](../../memory/feature-request-triage-baseline.md)
  (the `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the support-ticket system, CRM opportunities and their notes, and the
  community forum.
- Write access to the issue tracker limited to creating items, editing labels and
  assignees, and adding duplicate links and triage notes.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. It is classified
  `reversible-write` because every write lands on an internal tracker item and is
  undone by relabelling or unlinking. Nothing it writes reaches the person who raised
  the request. Granting it the ability to comment on a public forum thread, close
  requests, or change priority would make it `external-side-effect` or higher, and the
  classification and Owner's Card would have to change before that shipped.
- Read-only access to the three source systems is a hard requirement, not a
  preference. A deployment that lets it edit CRM records breaks the claim above.

## Memory row
- **Reads:** the pre-provisioning triage baseline (latency, attribution completeness).
- **Writes:** a weekly note recording how many requests were filed, deduplicated, and
  left unassigned (observed provenance).
- **Run-only:** the per-request candidate-duplicate scores.

## Portability check

*If I had to move this skill tomorrow, what would break?* The tracker, support-system,
CRM, and forum connectors; the governed baseline record; the theme-to-PM ownership map
the assignment step reads; and the PM confirmation gate named in the Owner's Card.
