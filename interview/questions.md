# The question skeleton

What to ask. [protocol.md](protocol.md) is how to ask it; [README.md](README.md) is where
the answers go.

The skeleton adapts the **intent-engineering 9-section spec** — objective, user goal,
desired outcomes, health metrics, strategic context, constraints, decision authority,
edge cases, stop rules and verification — from a single agent to an organization. Every
question names the field its answer fills, so nothing is asked twice and nothing required
goes unasked.

**How to read the `Fills` column.** `ontology:` is the function's deep record,
`exec:` its executive view, `card:` the skill's Owner's Card, `rule:` a constitution
record, `memory:` the captured baseline. A dash means the answer lands in a record's
prose rather than a field.

**`(human-only)`** marks the five answers an agent may never supply from context, no
matter how obvious they look (#6). The generator refuses to draft them.

Work the sections in order, one question at a time, per acted-on activity. Sections 1
and 2 also run once per function, for every activity, at the executive tier. A row that
names two fields is still asked in parts — one question at a time, per the protocol. For
`buy`, `hire`, and `wait`, stop after the common core — the Motion and its five scores,
the work type (section 1), the accountable owner (section 7), plus the grounding row
(section 1); every other row is automation-path only.

---

## 1. Objective — what is this work, and which way should it move?

| Ask | Fills | Notes |
|---|---|---|
| What does this function actually do, activity by activity? | exec:activity | Every activity, named. The executive tier is the whole list. |
| For each one: does it deserve more human time, or should it stop being hand-run? | exec:direction | up or down. Both are answers. |
| Which of these are you actually going to act on now? | — | Steer to three to five. Depth is earned by acting. |
| How should this get done — automate, build, buy, hire, or wait? | ontology:motion | The pivot. Only automate and build need the deep fields. |
| How repetitive is it, and how risky? | ontology:score_repetition, ontology:score_risk | low, medium, or high. |
| How much judgment does it take? | ontology:score_judgment | High judgment is not a veto; it is a scoping question. |
| How specific is it to this company, and how mature is the market for it? | ontology:score_company_specificity, ontology:score_market_maturity | Market maturity is the buy-versus-build tell. |
| Is this routing, sensemaking, or accountability? | ontology:work_type | Accountability work rarely leaves a person. |
| When did this last run, who did it, and what does the record show? | — | The evidence floor (mechanic 5), asked regardless of Motion — acted-on activities only, never at the executive tier. Confirmed absence, unknown, and refused are all honest answers; record which one. |
| Which business process runs differently if this works? | — | The ontology record's accountability paragraph. |

## 2. User goal — who is this for?

| Ask | Fills | Notes |
|---|---|---|
| Who does this work serve, and what are they trying to get done? | — | Their job, not the agent's. |
| Say the agent's job in one sentence, from their side. | card:job | If it takes two sentences it is two skills. |

## 3. Desired outcomes — what exists afterwards?

| Ask | Fills | Notes |
|---|---|---|
| What exactly does it produce? | ontology:gate_output | A state, not an activity. Name the artifact. |
| What does good look like, stated so someone could check it? | ontology:gate_standard | If nobody can check it, it is not a standard. |
| How will you know this actually improved? | card:success_standard | Must reference the baseline in section 4. |

## 4. Health metrics — what must not get worse?

| Ask | Fills | Notes |
|---|---|---|
| How could an agent hit that standard in a way you would hate? | card:known_failure_modes | The Goodhart question. Ask it out loud. |
| What must not degrade while this gets better? | — | Recorded in prose; groundwork has no dedicated field yet. |
| What is true today, measured, from a record rather than an estimate? | memory:source, memory:valid_at | The pre-provisioning baseline. #5 gates on it. |
| Who owns that baseline, and when should it be re-checked? | memory:owner, memory:review_by | An unowned baseline is drift with a number on it. |

## 5. Strategic context — where does this sit?

| Ask | Fills | Notes |
|---|---|---|
| Which systems hold the truth for this work? | ontology:substrate | If there is no system of record, that is the finding. |
| What does it read before it starts? | ontology:gate_inputs | Everything, including what it reads and discards. |
| When two systems disagree, which one wins? | ontology:gate_source_of_truth, card:source_of_truth | These two must match exactly. |
| Is this one agent, a team of them, or just a better chat? | ontology:shape | dont-bother is a legitimate answer. |

## 6. Constraints — what may it do, and what may it never?

| Ask | Fills | Notes |
|---|---|---|
| What may it do freely, without asking? | card:allowed_actions | Observable from the skill; still confirm it. |
| What may it never do? | card:forbidden_actions | (human-only) The refusal list comes from a person. |
| What may it propose but never perform? | card:proposed_only_actions | The most useful column on the card. |
| What must it never treat as a source of truth? | card:sources_must_not_use | Recollection and chat threads, usually. |
| What principle is that boundary protecting? | rule:value | The value half of the rule. |
| What actually stops it at that boundary? | rule:runtime_check | Trigger, evidence, action. |

## 7. Decision authority — who decides, and how far can it go?

| Ask | Fills | Notes |
|---|---|---|
| Is this read-only, reversible, external-side-effect, or high-risk? | card:action_class | Classify by mechanism, never by how it feels. |
| Who is accountable for proving this improved? One answer, not a committee. | ontology:accountable_owner, ontology:gate_owner, card:owner | (human-only) A person or the role they hold — the roster resolves either. |
| Who covers when that owner is away? | card:backup_owner | (human-only) Shared responsibility is often none. |
| Which rung does the rule sit on? | rule:rung | value, instruction, reminder, hard-block, human-decision. |
| Who owns the rule itself? | rule:owner | Whoever answers for it existing. |
| Who owns the principle, and who owns the check? | rule:value_owner, rule:runtime_check_owner | They are often different owners. |
| When this rule blocks somebody, who can they appeal to? | rule:human_appeal, rule:human_appeal_owner | A high-risk rule must have one. There is no rung six. |
| For each owner named above: is it a person, or a role somebody holds? | roster:role, roster:holder | Both resolve. The roster is where it is said which. |
| Who holds each of those roles today, and is each holder a person or an agent? | roster:holder, roster:type | An appeal path that ends at an agent is not an appeal path. |
| How often should this map of who holds what be re-confirmed? | roster:review_by | Asked once for the company, not per activity. An org map nobody re-checks is the stalest thing in the repo. |

## 8. Edge cases — what happens when it goes wrong?

| Ask | Fills | Notes |
|---|---|---|
| What should stop this rather than have it guess? | card:pause_condition | (human-only) A death condition. |
| Where does an exception go, and to whom? | ontology:gate_exception_path | Name a person, not a queue. |
| What does a mistake cost, and who notices it first? | ontology:gate_error_cost | If nobody notices, the review gate is wrong. |

## 9. Stop rules and verification — how do you know, and when do you stop?

| Ask | Fills | Notes |
|---|---|---|
| Who checks the output, and at what moment? | ontology:gate_review_gate | Before the output is used, not after. |
| What evidence must every run leave behind? | card:evidence_required | Required at external-side-effect and high-risk. |
| Which runs get read by a person, and how many? | card:review_sample | A sample nobody reads is not a sample. |
| How often is this whole thing reviewed? | card:review_cadence | Freshness warns; it never blocks. |
| What would make you turn this off? | card:retirement_condition | (human-only) Some agents should die. |
| When does this rule expire unless somebody renews it? | rule:sunset | Every rule gets one. |

---

## The constitution pass

Run once the functions are mapped, per ritual, starting with the rule everybody resents.
This is the [five-question worksheet](../governance/worksheets/five-question-worksheet.md)
with its destinations attached.

| Ask | Fills | Notes |
|---|---|---|
| Name the ritual, in plain words. What do we actually do? | rule:ritual | Not what the policy says. What happens. |
| When did this ritual last actually run, who worked it, and what does the record show? | — | Mechanic 5. The last enforcement instance, not the policy. |
| What was expensive or rare when this started? | rule:scarcity | Somebody's attention, usually. |
| Is that scarcity still real, and what job survives if it is not? | rule:surviving_job | The job almost always outlives the ritual. |
| Rewrite it as a rule a person can verify. | — | The rule record's title and body. No vibes. |
| Decide the machinery, and where it sits on the ladder. | rule:runtime_check, rule:rung | Trigger, evidence, action, owner, appeal. |
| If this repeals a ritual, which one, and who picks up the surviving job? | rule:repeals, rule:reassigned_to | Orphan-prohibition. Named before the repeal ships. |
| What action class is this rule about? | rule:action_class | Drives the no-rung-six safety invariant. |

## What the generator fills in without asking

Not everything is an interview question. These are drafted from what the interview
already captured, and confirmed at review rather than asked (#6's drafting split):

- `card:last_reviewed` and `card:next_review` — date stamps, written at generation.
- `SKILL.md`'s `name`, `description`, `provisioned`, `baseline`, `ontology` — all
  derivable from the record the skill was generated for.
- `memory:provenance` — set by *how* the fact was learned, not by asking.

Everything else in the schema is asked above. Task 3's test proves it.
