---
owner: Ruth Okafor
backup_owner: Priya Raman
job: Assemble an attributed evidence pack for each review conversation one week ahead
action_class: reversible-write
allowed_actions: read the HR information system, the goal tracker, peer-feedback submissions, the manager's running notes on each employee in the cycle, and the previous cycle's records; assemble and file the evidence pack in the review workspace; group peer feedback by theme with attribution intact
proposed_only_actions: flag an employee's pack as incomplete and propose which evidence is missing, for Ruth Okafor to resolve
forbidden_actions: rate, rank, or score an employee; summarize the evidence into a verdict or a recommendation; draft or edit assessment language; paraphrase a peer submission; share a pack with anyone other than the employee's manager
pause_condition: an employee has no recorded goals; fewer than two peer submissions have been received; the employee changed manager mid-cycle; the goal tracker or the feedback system is unreachable
retirement_condition: reviews stop starting from an evidence pack, or the HR information system assembles one the team trusts more
source_of_truth: The goal tracker for goals and outcomes; peer-feedback submissions verbatim, never paraphrased
review_cadence: each review cycle, and after any change to what the pack contains
known_failure_modes: no runtime action-class hook ships with this package; a pack that silently omits a late peer submission looks identical to a complete one, which is why a pack with fewer than two submissions halts instead of shipping short
last_reviewed: 2026-07-28
next_review: 2026-10-28
success_standard: Every employee in the cycle has an attributed evidence pack in their manager's hands one week before the conversation, measured against the pre-provisioning baseline of eleven days' median lead time and six of nineteen packs delivered a week ahead
evidence_required: The pack itself with a link from every item to the submission it came from, and the halt log for any employee whose pack did not ship
sources_must_not_use: A manager's recollection, a chat thread, or a paraphrase of a peer submission as evidence of anything
review_sample: The employee's manager reads and confirms every pack before the conversation; Ruth Okafor reviews two packs a cycle for attribution integrity
---
# Owner's Card — Performance-review prep

**Ruth Okafor** owns this skill; **Priya Raman** is the backup. It gathers the record
for a review conversation and stops. It may not rate, rank, score, summarize into a
verdict, or draft assessment language — those are the same act under four names, and
all four are forbidden here.

That boundary is written twice, because once is not enough. It is a forbidden action
here, and it is the rule at
[writing a performance assessment is a human-owned decision](../../governance/constitution/assessment-is-human-owned.md)
on the human-decision rung, which also names Priya Raman as the appeal — a refusal
nobody can appeal gets routed around. Neither of those is a hook: what actually stops a
bad pack from becoming a bad conversation is the manager reading it first.

Peer feedback travels verbatim with its attribution, because the whole point of a pack
is that the manager reads what was actually written. The pack halts rather than shipping
short: a pack missing a late submission looks exactly like a complete one, and the
person it is about cannot tell the difference either.
