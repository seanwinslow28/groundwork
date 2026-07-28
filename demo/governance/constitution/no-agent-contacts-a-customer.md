---
owner: Marcus Bell
rung: hard-block
action_class: external-side-effect
sunset: 2027-06-30
value: A customer hears from a person at Umbercress, not from a process
value_owner: Priya Raman
runtime_check: No skill may send a message, ticket reply, or post that reaches a customer. The check is structural rather than runtime — neither renewal-prep nor triage is granted an outbound channel at all, the brief is filed in the customer-success workspace and the triage queue lives in the product tracker, and 'contact the customer' is a forbidden action on both Owner's Cards. No hook ships for this rule: the engine's action-class gate reads Bash commands and does not see a message send, so the enforcement is the permission grant plus the CSM review gate, and giving a skill an outbound channel is the change this rule exists to catch at review
runtime_check_owner: Marcus Bell
human_appeal: A CSM who needs something to reach a customer faster than a person can send it raises it with Marcus Bell, who either sends it themselves or approves a written exception naming the message and the recipient
human_appeal_owner: Marcus Bell
ritual: Every customer-facing message being drafted and sent by the account's own CSM
scarcity: CSM time — sixty accounts across three people
surviving_job: Deciding what a customer is told, and saying it in a named person's voice
---
# No agent contacts a customer

**The rule.** An agent may assemble anything that helps a person talk to a customer. It
may not talk to the customer. Messages, ticket replies, and posts that leave the company
are sent by a named person, every time.

**Why it sits at the hard-block rung.** A message to a customer cannot be recalled, and
the harm is not that it is wrong — it is that it is nobody's. Umbercress sells to
operators who know their CSM by name; a message that turns out to have come from a
process costs more than the time it saved. Blocking is proportionate because the
workaround is trivial: a person presses send.

**What it makes possible.** This rule is why
[renewal preparation](../../skills/renewal-prep/SKILL.md) and
[feature-request triage](../../skills/feature-request-triage/SKILL.md) are track-1
skills at all. Their writes stay inside internal documents, so a mistake is corrected by
rewriting a file. Remove this boundary and both become external-side-effect skills whose
Owner's Cards would have to be rewritten before they shipped.

**Appeal.** Marcus Bell can send it, or approve a written exception naming the message
and the recipient. The exception is written down so that a pattern of exceptions is
visible rather than gradual.
