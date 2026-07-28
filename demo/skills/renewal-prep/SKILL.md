---
name: renewal-prep
description: Assemble a sourced renewal brief 45 days before an Umbercress contract renewal so the CSM walks in prepared
action_class: reversible-write
provisioned: yes
baseline: memory/renewal-prep-baseline.md
ontology: ontologies/customer-success/renewal-preparation.md
---
# Renewal preparation

Forty-five days before a contract renewal, assemble a brief for the account's CSM:
contract terms and dates from the CRM, the last 90 days of Relay usage read against
the account's own history, open and recently closed support tickets, and the notes
from the most recent quarterly check-in. Name the risks you can see and give an
expansion-or-contraction read. Every number carries a link to the record it came from.

Halt rather than guess. A missing or contradictory contract record, or usage data more
than seven days stale, stops the brief and routes to Marcus Bell. A brief with an
unmarked gap is worse than no brief, because it will be trusted.

This skill stops at a brief filed in the customer-success workspace. It does not decide
the renewal, price it, edit the contract or CRM opportunity record, or contact the
customer ([ontology record](../../ontologies/customer-success/renewal-preparation.md);
[the rule that holds the customer boundary](../../governance/constitution/no-agent-contacts-a-customer.md)).

## Harness requirements
- The governed pre-provisioning baseline for brief lead time and sourcing
  completeness: [memory/renewal-prep-baseline.md](../../memory/renewal-prep-baseline.md)
  (the `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the CRM contract and opportunity records, the Relay usage warehouse,
  the support-ticket system, and the quarterly check-in notes.
- Write access to the customer-success workspace location where briefs are filed, and
  nowhere else.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. Its writes are confined to the brief
  document, which is why it is `reversible-write`: a wrong brief is corrected by
  rewriting the file, and nothing reaches the customer. Widening it to write CRM fields
  or send the brief to a customer would make it track 2, and the classification and
  Owner's Card would have to change with it.
- Read-only access to the four source systems is a hard requirement, not a preference.
  A deployment that grants write access to the CRM breaks the claim above.

## Memory row
- **Reads:** the pre-provisioning renewal-prep baseline, and the at-risk-renewal record
  for the account when one exists.
- **Writes:** a per-renewal note recording which sources were available and which were
  stale at brief time (observed provenance).
- **Run-only:** the intermediate query results behind the brief.

## Portability check

*If I had to move this skill tomorrow, what would break?* The CRM, usage-warehouse,
support-system, and check-in-notes connectors; the governed baseline record; the
customer-success workspace write location; and the CSM review gate named in the
Owner's Card.
