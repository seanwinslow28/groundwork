---
owner: Director of Product
backup_owner: Principal Product Manager
job: File, deduplicate, and route each week's feature requests to the PM who owns the theme
action_class: reversible-write
allowed_actions: read support tickets, CRM opportunity notes, and community-forum posts; create tracker items; set labels, segments, and assignees; add duplicate links and triage notes
proposed_only_actions: merge two existing tracker items as duplicates after the owning PM confirms
forbidden_actions: set or change roadmap priority; close a request as won't-do; reply to the person who raised a request; edit CRM records
pause_condition: the tracker or CRM is unreachable; a request matches no existing theme and no owning PM; the theme-to-PM ownership map is stale or missing
retirement_condition: the tracker ships native deduplication and attribution the team trusts more, or requests stop arriving through three separate systems
source_of_truth: The issue tracker for what is already known; the CRM for account and ARR attribution
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; near-duplicate requests that use different vocabulary can be filed twice, which is why the weekly note reports the unassigned and duplicate counts
last_reviewed: 2026-07-27
next_review: 2026-10-27
success_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days with its asking accounts attached, measured against the pre-provisioning baseline
evidence_required: The weekly triage note with filed, deduplicated, and unassigned counts, and the per-request duplicate links
sources_must_not_use: A PM's recollection or a Slack thread as evidence that a request is already tracked
review_sample: The owning PM confirms theme and duplicate link on every request that reaches their queue; the Director reviews the unassigned pile weekly
---
# Owner's Card — Feature-request triage

The **Director of Product** owns this skill; the **Principal Product Manager** is the
backup. It routes requests and stops there — it may not set priority, close a request,
or reply to whoever raised it. Merging two existing items is proposed-only and waits
on the owning PM.

The boundary is what keeps this skill track 1: every write lands on an internal tracker
item and is undone by relabelling or unlinking, and nothing reaches the requester. If
it is ever given a path to a public thread or the ability to close requests, it becomes
an external-side-effect skill and this card must be rewritten before that ships.

It leaves what it cannot place rather than guessing, because an unassigned request is
visible and a mis-tagged one is not. The PM confirmation on each request is the review
gate; the Director's weekly pass over the unassigned pile is the quality check.
