---
name: performance-review-prep
description: Assemble an attributed evidence pack for each review conversation so the manager arrives with the record in front of them
action_class: reversible-write
provisioned: yes
baseline: memory/review-prep-baseline.md
ontology: ontologies/people-hr/performance-review-prep.md
---
# Performance-review prep

For each employee in the cycle, assemble an evidence pack for their manager: goals
against recorded outcomes, submitted peer feedback grouped by theme with every
attribution intact, and the previous cycle's commitments with their status. File it in
the review workspace one week before the review conversation. Every item links to the
submission it came from.

**Gather and stop.** This skill does not rate, rank, score, summarize the evidence into
a verdict, or draft any assessment language. Evaluating a person is a human-owned
decision, and it is not a matter of instruction: the rule at
[writing a performance assessment is a human-owned decision](../../governance/constitution/assessment-is-human-owned.md)
sits on the human-decision rung and refuses the request when it is made, naming its
owner and the appeal path.

Halt rather than fill a gap. Missing goals, fewer than two peer submissions, or an
employee who changed manager mid-cycle stops the pack and routes to Ruth Okafor. Peer
feedback is carried verbatim; paraphrasing it is the failure the pack format exists to
stop ([ontology record](../../ontologies/people-hr/performance-review-prep.md)).

## Harness requirements
- The governed pre-provisioning baseline for pack lead time and evidence completeness:
  [memory/review-prep-baseline.md](../../memory/review-prep-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the HR information system, the goal tracker, peer-feedback
  submissions, and the previous cycle's records.
- Write access to the review workspace location where packs are filed, and nowhere
  else.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. It is `reversible-write` on the
  mechanism: it files a document that a manager fetches, nothing is sent, nothing
  reaches the employee, and a wrong pack is corrected by regenerating it before the
  conversation. The care in this activity lives in its *scope*, not in its action class
  — which is why the boundary is written into the card's forbidden actions and into a
  constitution rule, where it can be enforced rather than merely intended.
- Giving this skill a path to the employee, or the ability to write into the review
  record itself, would make it track 2 and would need the card rewritten first.

## Memory row
- **Reads:** the pre-provisioning review-prep baseline (pack lead time, attribution
  completeness).
- **Writes:** a per-cycle note recording how many packs were assembled and how many
  halted for missing evidence (observed provenance).
- **Run-only:** the per-employee source-document extracts behind the pack.

## Portability check

*If I had to move this skill tomorrow, what would break?* The HR information system,
goal-tracker, and peer-feedback connectors; the governed baseline record; the review
workspace write location; the manager confirmation gate named in the Owner's Card; and
the constitution rule that keeps the assessment itself out of scope.
