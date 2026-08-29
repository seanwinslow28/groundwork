# EXPLANATION.md

A 4Q comprehension artifact (Nate B. Jones) for groundwork — the explanation that travels with the work: what this is, why this approach, what would break, what I learned.

---

## What is this?

An open-source, harness-agnostic Company OS for a company's agents. You point a coding agent at this repository; it interviews your company about the work each function actually does — what deserves more human time, what should be automated away, under what rules — and generates your operating system into a separate private repo: folder-per-function ontologies, skills with named owners, a compiled constitution, and organizational memory that changes under governance instead of rewriting itself.

Its lane is governance. The generator refuses to invent accountability: five fields (owner, backup owner, forbidden actions, two death conditions) come only from a human's answers. Every rule sits on a five-rung ladder from value down to human-decision, and there is no sixth rung — a high-risk action never terminates in automation.

## Why this approach?

**Files, not an engine.** There is no generator script, no server, no runtime to install — markdown conventions plus one zero-dependency validator (`python3 scripts/validate.py .`, standard library only), and a test enforces the zero-dependency claim. Rejected: a platform. The input is a conversation, so the "engine" is whatever coding agent the company already runs; anything heavier would make groundwork a vendor instead of a convention, and a dependency tree would be the first thing to rot.

**An interview, not a template.** Rejected: shipping a fill-in-the-blanks company OS. A template invites "N/A" and invented owners — precisely the accountability theater the tool exists to refuse. The interview stops where an answer can only come from a person, and the Describability Gate makes eight preconditions (inputs, output, standard, source of truth, exception path, error cost, owner, review gate) hold before any skill exists, with no waiver mechanism.

**Strictness follows consequence, not completeness.** The validator errors exactly where a field backs a running agent, warns on incomplete thinking you've acted on, and stays silent on untouched work. Rejected: a linter that demands everything everywhere — it trains people to satisfy the gate instead of thinking, and its noise buries the errors that matter.

**Blast-radius routing over blanket review.** A change auto-applies only when a bad version's worst case is bounded; anything touching governance, an owner, or a higher-risk skill escalates to a human, and auto-applies land in an append-only changelog. Rejected: human review of every change (nobody sustains it) and full autonomy (the thing the constitution exists to prevent).

## What would break?

These are live, knowingly accepted risks — not fixed defects. The complete inventory is [`docs/known-limitations.md`](known-limitations.md); these are the ones I'd volunteer first.

**1. No real company has ever run the interview.** Everything is proven against a simulated twenty-person company staffed by adversarial agent personas — and a persona is a cooperative interviewee by construction: it will not be bored, will not protect a colleague, will not misremember, will not hold knowledge it cannot articulate. What the harness measures is whether the protocol surfaces *designed* gaps; whether it surfaces *human* ones is untested. I accept this because the alternative — claiming readiness off a simulation — is trust debt; the repo states the boundary plainly and treats a real-company run as the first honest post-V1 act.

**2. The one measured detection number is bad, published, and not yet re-measured.** The 2026-07-31 persona-company run planted nine concealed facts behind seven personas; the interview surfaced one in full and a second in part. That landed on the lowest row of the pre-committed diagnostic band, and the diagnosis was structural: the interview's stopping condition was schema completeness, not evidential grounding — it stopped asking when the form was full, not when the answers were load-bearing. The findings returned as reviewed design changes (the evidence-floor work), but until a second run measures the redesign the same way, `1 of 9` is the number, and I publish it rather than the argument that personas calibrated to yield only to near-exact probes understate the protocol.

**3. Enforcement is a permissions convention, not a mechanism.** The consent gate's validator is a tripwire: it can prove an escalating change carries a matching pending proposal; it cannot tell a maintainer-typed approval from an agent-forged one. The real teeth are the commit bit — agents propose, only the git-capable human lands changes — so the guarantee holds exactly as long as that human runs the validator. Similarly, the action-class hook is Claude-Code-only; on Codex, Cursor, and Gemini CLI the same rule ships as an instruction, and an instruction is not enforcement. Cross-harness parity is a deliberate later graduation, not a V1 claim.

**4. The gates read structure, not truth.** No check reads prose for honesty. A company can satisfy every field with confident fiction and the validator will pass it; the demo's refusal is instruction-strength, not a runtime block. groundwork constrains the *shape* of accountability; it cannot manufacture the substance.

## What did I learn?

**The refusal is the product.** Every capable model wants to be helpful, and helpful means inventing the owner, drafting the death conditions, filling the field. The hard engineering was not generation — it was making "I can't answer that; a person has to" survive contact with an agent's compliance instincts, and the persona run showed even that only goes as deep as the questions force it to.

**A bad score you pre-committed to reading is worth more than a good one you didn't.** The `1 of 9` hurt, but the diagnostic band was written before the run, so the result routed to "diagnose the protocol" instead of to excuse-making or quiet re-runs. The blind spot it found — schema completeness masquerading as done — is a better design input than a flattering score would have been.

**Governance survives handoff; cleverness doesn't.** Writing the same rules for four harnesses (one of which enforces hooks, three of which silently ignore them) forced every mechanism to degrade honestly into an instruction plus a named limitation. The discipline of writing down what each layer *cannot* do turned out to be the most reusable artifact in the repo.
