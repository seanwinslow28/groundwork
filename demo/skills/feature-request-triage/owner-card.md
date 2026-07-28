---
owner: Dana Whitfield
backup_owner: Jae-won Park
job: File, deduplicate, and route each week's feature requests to the product manager who owns the theme
action_class: reversible-write
allowed_actions: read support tickets, CRM opportunity and check-in notes, and customer-success submissions; create tracker items; set themes, tags, and assignees; add duplicate links and triage notes
proposed_only_actions: merge two existing tracker items as duplicates after the owning product manager confirms
forbidden_actions: set or change roadmap priority; close a request; reply to the person who raised a request; edit CRM records
pause_condition: the tracker or the CRM is unreachable; a request matches no existing theme and no owning product manager; the theme-to-manager ownership map is stale or missing
retirement_condition: the tracker ships deduplication and attribution the team trusts more, or requests stop arriving through three separate systems
source_of_truth: The product tracker for what is already known; the CRM for account and contract-value attribution
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; near-duplicate requests written in different vocabulary can be filed twice, which is why the weekly note reports the unassigned and duplicate counts
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days with its asking accounts attached, measured against the pre-provisioning baseline of nine business days' median latency and forty-four of one hundred and forty-one requests filed on time
evidence_required: The weekly triage note with filed, deduplicated, and unassigned counts, and the per-request duplicate links
sources_must_not_use: A product manager's recollection or a chat thread as evidence that a request is already tracked
review_sample: The owning product manager confirms theme and duplicate link on every request reaching their queue; Dana Whitfield reviews the unassigned pile weekly
---
# Owner's Card — Feature-request triage

**Dana Whitfield** owns this skill; **Jae-won Park** is the backup. It routes requests
and stops there — it may not set priority, close a request, or reply to whoever raised
it. Merging two existing items is proposed-only and waits on the owning product manager.

The boundary is what keeps this skill track 1: every write lands on an internal tracker
item and is undone by retagging or unlinking, and nothing reaches the requester. If it
is ever given a path to the requester or the ability to close requests, it becomes an
external-side-effect skill and this card must be rewritten before that ships.

It leaves what it cannot place rather than guessing, because an unassigned request is
visible and a mis-tagged one is not. The product manager's confirmation on each request
is the review gate; Dana Whitfield's weekly pass over the unassigned pile is the quality
check.
