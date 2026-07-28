---
activity: Performance-review prep
function: People/HR
motion: automate
score_repetition: high
score_risk: medium
score_judgment: high
score_company_specificity: medium
score_market_maturity: low
work_type: sensemaking
accountable_owner: Ruth Okafor
substrate: The HR information system + the goal tracker + peer-feedback submissions + the previous review cycle's records
shape: single-agent
gate_inputs: For each employee in the cycle: their goals and recorded outcomes, submitted peer feedback, their previous review, and their manager's running notes
gate_output: An evidence pack for the manager — goals against outcomes, peer feedback grouped by theme with attribution intact, and the previous cycle's commitments with their status. No rating, no summary judgment, no draft assessment
gate_standard: Every employee in the cycle has an evidence pack in their manager's hands one week before the review conversation, and every item in it links to the submission it came from
gate_source_of_truth: The goal tracker for goals and outcomes; peer-feedback submissions verbatim, never paraphrased
gate_exception_path: Missing goals, fewer than two peer submissions, or an employee who changed manager mid-cycle halts the pack and routes to Ruth Okafor
gate_error_cost: A pack that misattributes or omits feedback distorts a conversation about someone's job — the highest-stakes error in this ontology, which is why the manager reviews every pack and no assessment is ever drafted
gate_owner: Ruth Okafor
gate_review_gate: The employee's manager reads the pack and confirms it before the review conversation
---
# Performance-review prep

**Direction: down.** Assembling the evidence for a review — goals, outcomes, peer
feedback, last cycle's commitments — is hours of gathering per employee, repeated
twice a year by one person. The gathering should stop being hand-run.

**Motion: automate — and the scope is where the care lives.** Judgment scores **high**,
which would normally point away from automation. It does not here, because the activity
is deliberately drawn to *exclude* the judgment: the agent assembles evidence and stops.
It does not rate, rank, summarize, or draft an assessment. Evaluating a person is a
human-owned decision, and the constitution rule that governs this skill blocks the
agent from crossing that line rather than trusting it not to.

Ticket #4 described this activity's motion as "assist". That is the same idea expressed
as a verdict rather than a boundary: the Motion ladder records *how the work gets done*,
and the limit on *how far the agent may go* belongs on the Owner's Card and in the
constitution, where it can actually be enforced.

## Accountability

Which business process runs differently: review prep stops being one person assembling
twenty evidence packs by hand and becomes an agent that gathers and organizes, with the
assessment itself untouched and explicitly out of bounds.

Who is accountable for proving it improved: **Ruth Okafor**, measured against a
baseline of pack lead time and evidence completeness captured before provisioning
(see [the captured baseline](../../memory/review-prep-baseline.md)).
