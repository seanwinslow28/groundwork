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

## The roster: who holds what

An owner is a **role** or a **named holder**, and `governance/roles.md` is where that
resolves. One roster per instance.

````
---
valid_at: <ISO date — when this mapping was last confirmed>
review_by: <ISO date — when to re-confirm it>
source: <where this org map came from: an interview layer, an HR system, the founder's word>
---
| Role | Holder | Type |
|---|---|---|
| Head of IT | Priya Vale | human |
|  | Ruth Okafor | human |
````

- **Two-way resolution, by exact string.** A value matching a **Role** cell resolves to
  that row's holders; a value matching a **Holder** cell resolves to that holder. The
  second form is what keeps `owner: Ruth Okafor` valid.
- **A holder-only row** (Role cell empty) names a holder without asserting a role.
- **A role with no row, or a row with no holder, is unheld** — and a rule with a rung
  cannot have an unheld owner. Drop the rung and it is a draft again, gaps named as WARNs.
- **Type is `human` or `agent`.** The `human_appeal_owner` must reach at least one
  `human`: an appeal path that terminates in a model is not an appeal path.
- **No string may be both a Role and a Holder** — every reference to it would be ambiguous,
  and no precedence rule is defined because none should be needed.
- `valid_at` is a **snapshot**, deliberately narrower than org-memory's
  when-the-fact-became-true `valid_at`.

**The body is a restricted grammar, and the restrictions are whole-file.** Below the
frontmatter a roster carries **one** table and nothing that could be mistaken for another:

- **No backtick.** A code span can run across lines and render a whole table as code, and
  a backtick fence can hide one outright.
- **No run of three or more tildes** — the other code fence.
- **No angle-bracket construct** — no HTML tag, comment, doctype, CDATA section or
  processing instruction, and no autolink either. An autolink is Markdown rather than HTML,
  so refusing it is deliberately over-strict. Write a plain URL, or an ordinary
  bracket-and-parenthesis Markdown link.
- **No link reference definition** — no `]:` in the body. One renders nothing at all and
  its title may run across lines, so an entire table can live inside one. The executive
  view refuses them too.
- **No character reference** — no `&#32;`, no `&amp;`. It renders as something other than
  what is written, so a holder could be text nobody can see. A bare ampersand is fine.
- **No `|` outside the table.** A pipe in explanatory prose reads as a second table, so it
  is refused rather than guessed at.

Each is an ERROR naming its own line, and each is matched against the raw line with **no
regard for context** — a construct inside a list, a blockquote, or an indented block is
refused exactly as one at the top level is. That bluntness is the point. Deciding what
*renders* means emulating CommonMark, and five review rounds of trying produced a checker
that was wrong in one direction or the other every time. Over-catching costs a clear error
on a line you can see; under-catching lets an owner resolve against something a reader
cannot see, which is the exact failure held-to-activate exists to prevent.

Write the body plainly: a heading, a few sentences, and the table.

Changing the roster in a governed root is an escalating change (#17): it decides who holds
every active rule's owners, and where its human appeal terminates.

## What the validator enforces

- **ERROR:** a `high-risk` rule with no human-appeal path (no rung six — placeholder
  answers like `none`/`TBD` do not count); a repeal (`repeals`) whose `surviving_job`
  is not `reassigned_to` a single accountable person; an active rule (placed on a
  rung) with no `owner`, or missing any of the four owned objects or its rule
  statement (the H1 title + body); a missing `action_class` on an active rule; an
  active rule whose `owner`, `value_owner`, `runtime_check_owner`, or
  `human_appeal_owner` does not resolve in the roster; an active rule (or a `high-risk`
  draft) whose `human_appeal_owner` reaches no human holder; an instance with an active
  rule and no `governance/roles.md`.
- **WARN:** a missing, unparseable, or overdue `sunset`; a rule not yet placed on a
  rung (draft), plus one named WARN per gap it carries, in three classes — an owner field
  with no answer; one that does not resolve; and, on a rule that is **not** `high-risk`, an
  appeal owner that resolves but only to `agent` holders. The safety-spine ERRORs above
  apply to drafts too — only the `owner` requirement waits for provisioning (rung
  placement).

## Where worksheets live (and why it matters)

Blank and in-progress five-question worksheets live in `governance/worksheets/`.
Kept, compiled rules live in `governance/constitution/`. The validator checks only
`governance/constitution/` — so an unfinished worksheet for a ritual nobody has acted
on is silent, exactly as the doctrine requires, while every file that *is* a rule is
held to the full contract. Silence is decided by **location**, not by leniency.
