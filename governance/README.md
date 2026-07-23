# Governance — the constitution compiler

groundwork's governance layer generates **machinery, not documents**. V1's constitution
compiler ships **guided content**: each surviving rule is a typed, validator-checked
record. (Runnable per-rule automation is V2; the fixed action-class hook set — the V1
runnable floor — ships separately.)

## Compiling a rule (the five-question worksheet)

For each ritual: name the ritual → name the scarcity it protected → is that scarcity
still real, and what job survives → rewrite it as a rule a person can verify → decide
the machinery (trigger, evidence, action, owner, appeal). Start with the rule everyone
resents.

## A rule is four owned objects, on a rung, with a sunset

Every kept rule is one file under `governance/constitution/`, carrying four governance
objects — each with its own owner:

- **value** — the principle it protects (`value`, `value_owner`).
- **rule** — the verifiable statement (the file's title + body; `owner` owns it).
- **runtime check** — the machinery: trigger, evidence, action (`runtime_check`,
  `runtime_check_owner`).
- **human appeal** — the escalation path (`human_appeal`, `human_appeal_owner`).

It is placed on the **five-rung enforcement ladder** — `value` → `instruction` →
`reminder` → `hard-block` → `human-decision`. **There is no rung six:** a consequential
(`high-risk`) action never terminates in automation, so it must carry a human-appeal
path. Every rule gets a **sunset** date. When a ritual is repealed, its **surviving
job** must be reassigned before the repeal ships (orphan-prohibition).

## What the validator enforces

- **ERROR:** a `high-risk` rule with no human-appeal path (no rung six — placeholder
  answers like `none`/`TBD` do not count); a repeal (`repeals`) whose `surviving_job`
  is not `reassigned_to` a single accountable person; an active rule (placed on a
  rung) with no `owner`, or missing any of the four owned objects or its rule
  statement (the H1 title + body); a missing `action_class` on an active rule.
- **WARN:** a missing, unparseable, or overdue `sunset`; a rule not yet placed on a
  rung (draft). The safety-spine ERRORs above apply to drafts too — only the `owner`
  requirement waits for provisioning (rung placement).
