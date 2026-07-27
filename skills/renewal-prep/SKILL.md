---
name: renewal-prep
description: Assemble a sourced renewal brief before a contract renewal so the CSM walks in prepared
action_class: reversible-write
provisioned: yes
baseline: memory/renewal-prep-baseline.md
ontology: ontologies/customer-success/renewal-prep.md
---
# Renewal preparation

Forty-five days before a contract renewal, assemble a brief for the account's CSM:
contract terms and dates, the last 90 days of product usage read against the account's
own history, open and recently closed support tickets, and the notes from the most
recent business review. Name the risks you can see and give an expansion-or-contraction
read. Every number and claim carries a link to the record it came from.

Halt rather than guess. A missing or contradictory contract record, or usage data more
than seven days stale, stops the brief and routes to the VP Customer Success. A brief
with an unmarked gap is worse than no brief, because it will be trusted.

This skill stops at the brief. It does not decide the renewal, propose pricing, edit
the contract or CRM opportunity record, or contact the customer
([ontology record](../../ontologies/customer-success/renewal-prep.md)).

## Harness requirements
- A governed pre-provisioning baseline for brief lead time and sourcing completeness:
  [memory/renewal-prep-baseline.md](../../memory/renewal-prep-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the CRM contract and opportunity records, the product-usage
  warehouse, the support-ticket system, and the business-review notes.
- Write access to the CS workspace location where briefs are filed — and nowhere else.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. Its writes are confined to the
  brief document, which is why it is classified `reversible-write` rather than
  `external-side-effect`: a wrong brief is corrected by rewriting the file, and no
  message reaches the customer. Widening it to write CRM fields or send the brief to
  a customer would make it track 2, and the classification and Owner's Card would have
  to change with it.
- Read-only access to the four source systems is a hard requirement, not a
  preference. A deployment that grants write access to the CRM breaks the action-class
  claim above.

## Memory row
- **Reads:** the pre-provisioning renewal-prep baseline (brief lead time, sourcing
  completeness).
- **Writes:** a per-renewal note recording which sources were available and which were
  stale at brief time (observed provenance).
- **Run-only:** the assembled brief's intermediate query results.

## Portability check

*If I had to move this skill tomorrow, what would break?* The CRM, usage-warehouse,
support-system, and business-review connectors; the governed baseline record; the CS
workspace write location; and the CSM review gate named in the Owner's Card.
