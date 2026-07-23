---
owner: Head of IT
rung: human-decision
action_class: high-risk
sunset: 2027-07-01
value: Least-privilege access protects the company and its customers' data
value_owner: CISO
runtime_check: The onboarding agent may propose a non-standard access grant but must halt for a named approver; the provisioning log records who approved and when
runtime_check_owner: Head of IT
human_appeal: A denied or delayed grant can be escalated to the CISO, who decides within one business day
human_appeal_owner: CISO
ritual: IT manually provisioning every access request by ticket
scarcity: Security-review time — every access grant used to get a human's eyes
surviving_job: Deciding whether a non-standard grant is warranted (kept human)
---
# Non-standard system access requires human sign-off

**The rule.** An agent may *propose* a non-standard system-access grant; it may never
*perform* one. Every such grant halts for a named human approver, who is recorded in
the provisioning log.

**Why it sits at the human-decision rung.** Granting access is `high-risk` — it can
expose company and customer data — so it can never terminate in automation. There is
no rung six: the agent's authority stops at *proposing*, and a human decides. This is
the rule behind the onboarding skill's `proposed-only` action "grant non-standard
system access" ([Owner's Card](../../skills/onboarding-orchestration/owner-card.md)).

**Appeal.** A denied or delayed grant escalates to the CISO, who decides within one
business day — so the block never becomes a silent dead end.
