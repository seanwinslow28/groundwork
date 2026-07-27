---
owner: VP Customer Success
backup_owner: Director of Customer Success
job: Assemble a sourced renewal brief 45 days before each contract renewal
action_class: reversible-write
allowed_actions: read CRM contract and opportunity records, product-usage data, support tickets, and business-review notes; write and revise the renewal brief in the CS workspace
proposed_only_actions: flag an account as a churn risk on the CRM record after the CSM confirms the read
forbidden_actions: edit contract or opportunity records; propose or quote pricing; contact the customer; send the brief outside the CS workspace
pause_condition: the contract record is missing or contradicts the CRM opportunity; usage data is more than seven days stale; the support system is unreachable
retirement_condition: the CRM ships a renewal-brief view the team trusts more, or renewals move to a motion that does not start from a written brief
source_of_truth: The CRM contract record for terms and dates; the usage warehouse for product adoption
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; a brief assembled from a partially stale warehouse can look complete, which is why staleness halts rather than annotates
last_reviewed: 2026-07-24
next_review: 2026-10-24
success_standard: Every renewal has a sourced brief in the CSM's hands 45 days ahead, with every number resolving to a source record, measured against the pre-provisioning baseline
evidence_required: The brief itself with its per-claim source links, and the source-availability note recorded for the run
sources_must_not_use: Slack threads, email, or a CSM's recollection as a source of truth for contract terms or usage numbers
review_sample: Every brief is read by the account's CSM before the renewal conversation; the VP reviews two briefs a month against their source records
---
# Owner's Card — Renewal preparation

The **VP Customer Success** owns this skill; the **Director of Customer Success** is
the backup. It assembles a sourced renewal brief and stops there — it may not touch
contract or opportunity records, propose pricing, or contact a customer. Flagging an
account as a churn risk is proposed-only and waits on the CSM's confirmation.

The boundary is what keeps this skill track 1: everything it writes is a document a
human reads and can rewrite. If it is ever given write access to the CRM or a path to
the customer, it becomes an external-side-effect skill and this card must be rewritten
before that ships.

It pauses rather than papering over a gap, because a brief that looks complete is
trusted. The CSM's read before every renewal conversation is the review gate; the VP's
twice-monthly sample against source records is the quality check.
