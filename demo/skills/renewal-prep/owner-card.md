---
owner: Marcus Bell
backup_owner: Nina Sokolova
job: Assemble a sourced renewal brief 45 days before each contract renewal
action_class: reversible-write
allowed_actions: read CRM contract and opportunity records, Relay usage data, support tickets, and quarterly check-in notes; write and revise the renewal brief in the customer-success workspace
proposed_only_actions: flag an account as a churn risk on the CRM record after the account's CSM confirms the read
forbidden_actions: edit contract or opportunity records; propose or quote pricing; contact the customer; send the brief outside the customer-success workspace
pause_condition: the contract record is missing or contradicts the CRM opportunity; usage data is more than seven days stale; the support system is unreachable
retirement_condition: the CRM ships a renewal-brief view the team trusts more, or renewals stop starting from a written brief
source_of_truth: The CRM contract record for terms and dates; the Relay usage warehouse for product adoption
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; a brief assembled from a partially stale warehouse can look complete, which is why staleness halts rather than annotates
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every renewal has a sourced brief in its CSM's hands 45 days ahead with every number resolving to a source record, measured against the pre-provisioning baseline of eight days' median lead time and fifteen briefs in twenty-six renewals
evidence_required: The brief itself with its per-claim source links, and the source-availability note recorded for the run
sources_must_not_use: A chat thread, an email, or a CSM's recollection as a source of truth for contract terms or usage numbers
review_sample: The account's CSM reads every brief before the renewal conversation; Marcus Bell reviews two briefs a month against their source records
---
# Owner's Card — Renewal preparation

**Marcus Bell** owns this skill; **Nina Sokolova** is the backup. It assembles a sourced
renewal brief and stops there — it may not touch contract or opportunity records,
propose pricing, or contact a customer. Flagging an account as a churn risk is
proposed-only and waits on the CSM's confirmation.

The boundary is what keeps this skill track 1: everything it writes is a document a
person reads and can rewrite. If it is ever given write access to the CRM or a path to
the customer, it becomes an external-side-effect skill and this card must be rewritten
before that ships. The rule at
[no agent contacts a customer](../../governance/constitution/no-agent-contacts-a-customer.md)
holds that boundary from the other side.

It pauses rather than papering over a gap, because a brief that looks complete is
trusted. The CSM's read before every renewal conversation is the review gate; Marcus
Bell's twice-monthly sample against source records is the quality check.
