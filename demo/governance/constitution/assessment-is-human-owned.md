---
owner: Ruth Okafor
rung: human-decision
action_class: high-risk
sunset: 2027-06-30
value: Judging a person's work is a judgment a person owns and answers for
value_owner: Priya Raman
runtime_check: The review-prep skill assembles the evidence pack and stops. A request to rate, rank, score, summarize the evidence into a verdict, or draft assessment language is refused at the moment it is made, and the refusal names this rule, its owner, and the appeal path rather than simply declining
runtime_check_owner: Ruth Okafor
human_appeal: A manager who believes the boundary is wrong for their case raises it with Priya Raman, who decides within one business day and records the decision. The answer can be yes about the process and is never yes about the assessment
human_appeal_owner: Priya Raman
ritual: Managers assembling the evidence and writing the first draft of the assessment in one sitting, with no record of which was which
scarcity: Manager attention during review season
surviving_job: Forming and writing the assessment itself, which stays human permanently
---
# Writing a performance assessment is a human-owned decision

**The rule.** An agent may gather, organize, and attribute the evidence for a
performance review. It may not evaluate. Rating, ranking, scoring, summarizing the
evidence into a verdict, and drafting assessment language are the same act under five
names, and all five stop here.

**Why it sits at the human-decision rung.** Evaluating a person is `high-risk`: it
changes what happens to somebody, and it cannot be undone by editing a file. So it can
never terminate in automation. **There is no rung six** — the agent's authority ends at
the evidence, and a person decides. That is also why this rule carries a named appeal
path: a block with no appeal is a dead end, and dead ends get routed around.

**What it protects, concretely.** The pack that
[performance-review prep](../../skills/performance-review-prep/SKILL.md) assembles is
deliberately shaped to be useful and not conclusive: goals against outcomes, peer
feedback verbatim and attributed, last cycle's commitments with their status. Ask it for
a rating and it will not produce one — not because it was asked nicely in a prompt, but
because this rule refuses, names Ruth Okafor as the owner, and points at Priya Raman as
the appeal.

**Appeal.** Priya Raman, within one business day, recorded. A manager can win an
argument about the *process* — what evidence belongs in the pack, how it is grouped. No
one wins the argument about who writes the assessment.
