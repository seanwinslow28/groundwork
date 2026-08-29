# Roles as the accountable unit — design

> **Workbench artifact, not product content.** The design settling the fork the
> multi-agent decision opened: if a role is the accountable unit, must the role be held?
> Brainstormed and decision-locked with the maintainer 2026-08-28, in one session,
> seven decisions — the first carried in from the maintainer's own kickoff decision,
> the other six each presented with options, a recommendation, and the honest
> counter-argument (build-sessions rule 5), and each chosen by the maintainer. The
> decision list below is this session's own account; the durable record of the
> maintainer's approval is the merge that lands this branch, the same way the honesty
> plan's approval is dated by its merge. It feeds Fable implementation plans through
> the ordinary slice loop; nothing here is built yet.

## Why this exists

The maintainer decided this session that groundwork is becoming a multi-agent OS:
ontology roles are filled by agents — open and closed models both — adoptable by a
company or a solo builder, and **role titles are valid owners**. The code already
agrees: `governance/constitution/access-grants-need-human-signoff.md` fills every owner
field with a role title (`owner: Head of IT`, `value_owner: CISO`,
`human_appeal_owner: CISO`), and `tests/test_validate.py`'s `RULE_OK` fixture pins
those same role-shaped values as producing zero ERRORs (the fixture is a synthetic
twin of that rule, not a read of the file — verified against both, this session).

The prose disagrees. Three sites contradict roles-as-owners explicitly:
`interview/questions.md:93` — "A role is not an owner" —
`interview/protocol.md:247` — "an owner who is a **person**, not a role" — and
`interview/README.md:149` — "a person, not a role?". Five more carry person language
that must be reviewed against the new semantics, though none of them states that a
role is invalid (a "named person" can be the person holding a role): `README.md:22`
and `:102`, `interview/generate.md:142` and `:149`, and `interview/questions.md:96`
("The person who answers for it existing"). The rewrite slice re-greps; this list is
the floor.

Accepting roles as owners reopens the S3 void one level up. Run 1's record carried
`runtime_check_owner: "Delivery coordination — the function, no person named"`, and it
passed — because the rule shipped as a draft, and the validator inspects owner fields
only on active rules (`scripts/validate.py`, the rung branch; verified this session).
Had the rule been active, `_answered()` would have accepted the sentence anyway, since
it rejects only placeholders. The quad-check correction
(`~/Code-Brain/persona-company/runs/2026-07-31/quad-check-correction.md:114`) put the
distinction this way: *"`Head of IT` names an accountable office, while "the function,
no person named" disclaims one, and the check cannot tell them apart."* If any role
string is a valid owner, *enforced, but nobody owns it* comes back wearing a role
title. If only filled roles are valid, the schema again cannot express the state
run 1 found — a practice its confirmed record carries at `Rung: hard-block` with an
owner nobody claims, while company-wide practice stays unestablished (the
correction's bounded reading) — and a generator is left with the outcomes run 1's
report actually weighed — do not ship, ship with the gate red, or ship a declared
draft — of which the then-pinned contract permitted only omission, with inventing an
owner as the standing temptation.

This design also settles the two confirmed enforcement holes recorded in
`quad-check-correction.md` and the durable-review-record rule, because all three take
their shape from the holding semantics.

## Decisions locked (maintainer, 2026-08-28)

1. **Roles are the accountable unit.** A role title is a valid value for every owner
   field. This is additive: a person's name stays valid too — the demo's active rules
   name people, and nothing here invalidates them. (Maintainer's decision preceding
   the brainstorm; restated because everything below inherits it.)

2. **Held-to-activate.** A rule with a rung (active) must have every one of its owner
   fields resolve against the roster; a rule with no rung (draft) may carry unheld or
   absent owners. This extends the draft/active split the validator already implements
   — the code comment reads "Required in full once a rule is active (rung-placed)" and
   "incomplete is fine while drafting" (`scripts/validate.py:1811`, `:1852`, verified
   this session). **It adds activation requirements and removes nothing:** the
   safety-spine checks that already run on drafts — a missing `action_class` and,
   above all, the ERROR on a high-risk rule with no answered appeal path and owner —
   keep firing on drafts exactly as the code and
   `test_draft_high_risk_without_appeal_still_errors` pin today. "A high-risk draft
   with no appeal path must not leave the gate green" stays true verbatim.
   **On S3:** this decision supersedes S3's requested outcome rather than delivering
   it. S3 asked for a representable third state so the machine layer stops reading
   *draft* for a practice the confirmed record carries as enforced with no owner
   (whether the practice is live is what the correction leaves unestablished); the
   maintainer instead chose the
   declared draft as the designed encoding of that state, with decision 5's named
   WARNs making the gaps legible. A structural consumer will still read "draft" there
   — by design now, not by accident — and the cost S3 measured (two drafts, zero
   active rules) is accepted as the price of never letting an active rule be owned by
   nobody.
   *Counter-argument, recorded:* "held" means the repo says held. A roster is
   repo-internal consistency, not reality — it can go stale the way run 1's
   finance-sign-off record did. This is an S1-class limitation and is documented, not
   solved (see "What this does not do").

3. **Holders are typed, and the human appeal must reach a human.** A holder is a
   person or an agent, and the roster marks which. The one per-object constraint: the
   `human_appeal_owner` must resolve to at least one **human** holder — an appeal
   path that terminates in a model is not an appeal path. This constraint rides the
   tiers that already exist: on an active rule it is part of activation resolution;
   on a **high-risk draft** it joins the safety spine that already runs draft-time
   (the existing ERROR checks that the appeal fields are answered; an answered
   appeal owner that resolves to agent-only holders is affirmatively wrong, not
   merely incomplete, so it ERRORs on a high-risk draft too — otherwise a high-risk
   draft with a model for an appeal path would leave the gate green, which the spine
   forbids verbatim). An appeal owner that resolves to *nothing* on a draft stays in
   decision 5's WARN tier — unheld is the drafting state. The tiers under a v1 pin
   differ by age: the existing check — a high-risk rule whose appeal fields are not
   answered — is a v1 ERROR and keeps firing as one under any pin; only the **new**
   agent-only-resolution ERRORs are `since: 2` checks, demoted to WARN on v1-pinned
   content, so that part of the spine's guarantee holds in full from v2. Value,
   rule, and runtime-check owners may be agent-held.
   *Counter-argument, recorded:* per-object holder-type rules add a distinction the
   schema could not previously see, and the smallest adopter — one human holding
   everything — carries typing machinery built for the multi-agent case.

4. **Resolution lives in one roster file per instance.** `governance/roles.md`: each
   role, its holder(s), each holder typed `human` or `agent`, with `valid_at` and
   `review_by` dating its staleness, org-memory style. The decisive argument is the
   prior session's own pattern data: a parallel-site drift class recurred throughout
   it — commit `18fa805` names its "seventh instance" — and holders written inline in
   every rule's frontmatter would build exactly that failure shape into every adopter
   repo. One roster is one place to go stale, and a dated one.
   *Counter-argument, recorded:* the rule's reader no longer sees the holder without a
   lookup; it is one more required file; the interview must now elicit it.

5. **Hole (a), the drafting gate: WARN, naming each gap.** A draft rule raises one
   WARN per gap in three named classes: a missing owner field (any of the four —
   rule owner, value owner, runtime-check owner, appeal owner), an owner value with
   no roster match, and an appeal owner that resolves but to agent-only holders on a
   non-high-risk draft — resolvable, wrongly typed. Each WARN names its gap
   specifically. (A missing sunset already
   WARNs today, draft or active, outside the rung branch; that check is unchanged.)
   Today an absent rule owner and appeal owner on a draft raise nothing at all (the
   safety-spine ERRORs above are the exception, and they stay ERRORs). Blocking more
   would contradict
   decision 2's premise that the draft state is where incompleteness legitimately
   lives; silence is how run 1's "two drafts and zero active rules" stayed illegible.
   *Counter-argument, recorded:* WARNs are ignorable, and this one guards the
   governance layer.

6. **Hole (b), the shipping contract: permit declared drafts, for constitution
   rules.** `interview/generate.md` is amended where it governs constitution rules: a
   rule missing required fields may ship only as a draft that declares its gaps
   in-file, and the generation report must name every artifact that shipped incomplete
   and why. An undeclared incomplete shipment stays prohibited. The other artifact
   kinds' no-ship rules — a deep record missing its Gate answer, a memory record
   missing its owner, a skill missing human-only answers — stand unchanged: they have
   no draft state to ship into, and this design does not invent one.
   Under decision 2 this is not a concession — the declared draft is the designed
   encoding of *confirmed but incomplete or unheld*. Run 1 already practiced this
   contract for the gaps it recognized as gaps: each shipped rule declares its own
   missing fields in-file — the quad-check its rule owner, appeal owner, and sunset;
   the intake gate its value statement, value owner, appeal path and owner, and
   sunset ("Each file names its own missing owners in its body rather than
   pretending to be complete") — and the generation report names both incomplete
   rules and those reasons under "What did not ship, and why"
   (`generation-report.md:45–72`, verified this session). One gap
   it did not declare, because it was not yet one: the disclaiming
   `runtime_check_owner` becomes unresolvable — and therefore a declared-draft
   obligation — only under this design. The amendment makes the contract match the
   observed declaration behavior instead of prohibiting it.
   *Counter-argument, recorded:* declaring may become cheaper than completing; the
   generation report obligation is the pressure against that, and a run 2 can measure
   whether it holds.

7. **Durable review verdicts: a standing rule, stored beside the plan.** A slice may
   not merge unless the verdicts of every Codex review round run against it — findings,
   severities, and dispositions (fixed in commit X / rejected with grounds), not just
   the final approve — are committed in the repository:
   `docs/superpowers/plans/<slice>-reviews.md`, appended per round on the branch, so
   the merge carries the record. Plan-less work uses
   `docs/superpowers/reviews/<branch>.md`, with any `/` in the branch name written
   as `-` so the log stays a single file directly under `reviews/`.
   The evidence: the prior session ran twenty-five review rounds — sixteen on the
   groundwork branch, nine on the persona-company correction, per the merge commit
   `df6df21` — and what survives is what its commits chose to carry. Fix commits
   preserve the accepted findings and their dispositions in their bodies — sometimes
   with severities, as `f5ab4b6`'s "Two HIGH findings, both correct" — but what
   survives is only what each commit chose to quote: no complete round output
   exists, rejected findings and full verdict text appear nowhere, and rounds whose
   numbers left no commit (r3 and r9 in the `fix(build): Codex r…` sequence) are
   unrecoverable. The honesty plan paid for the same loss earlier: its
   header says its three rounds' "review outputs were not retained", leaving the
   merge commit as "the durable record of the approval" with "no inspectable
   artifact" dating round 3 itself. The pattern data this rule exists to keep — the
   recurring drift class and the four factual defects build-sessions rule 8 now
   counts — came from non-gating rounds and would be invisible in a merge-gate-only
   log.
   *Counter-argument, recorded:* roughly 12x the record volume (twenty-five rounds,
   two of them approving, in that session), and appending during review adds a step
   to every round.

## The design

### The roster

One file per validated instance — the engine root, `demo/`, and every company repo —
at `governance/roles.md`. Sketch; the implementation plan owns the exact format:

```markdown
---
valid_at: 2026-08-28
review_by: 2026-11-28
source: <where this org map came from — interview layer, HR system, founder's word>
---
| Role | Holder | Type |
|---|---|---|
| Head of IT | Priya Vale | human |
| CISO | Priya Vale | human |
| Renewal-prep runner | renewal-prep agent (closed model) | agent |
```

One person may hold many roles (the solo builder holds all of them). **Resolution is
by exact string, two ways:** an owner value matching a Role cell resolves to that
row's holders; an owner value matching a Holder cell resolves to that holder
directly. The second form is what keeps person-named owners valid (decision 1) — the
demo's `owner: Ruth Okafor` resolves because Ruth Okafor appears as a holder. A role
with no row, or a row with no holder, is unheld.

Two-way resolution requires **roster integrity**, checked as part of R1: a string
appearing both as a Role and as a Holder is a namespace collision and ERRORs — every
owner reference to it would be ambiguous, and no precedence rule is defined because
none should be needed; a holder appearing in multiple rows with conflicting types
also ERRORs. The roster is content, so it is checked wherever it lives, per the
instance rule.

**Resolution is intent-blind, and that has a stated blind spot.** An owner value is
whatever it matches: nothing marks a string as meant-as-role versus meant-as-person.
So a role title whose roster row was *forgotten* — and which happens to equal an
existing Holder string — silently resolves as that holder instead of surfacing as
unheld; the integrity check cannot see a row that is absent. The structural fix would
be typed owner references in the rule itself (`role: Head of IT` / `person: Ruth
Okafor`), which discriminates at the source but changes the rule frontmatter schema
for every adopter. The recommendation is to accept intent-blind resolution and
document the blind spot in `docs/known-limitations.md` — the collision requires an
author to name a role identically to a person while also forgetting its row, and
both halves are the repo author's own text — with typed references recorded here as
the known alternative if R1's implementation or a later run shows the blind spot
biting. This is flagged for the maintainer at R1 plan review.

### The validator (the one code slice)

- **Schema bump, not a candidate.** The activation-resolution ERROR is a tightening —
  content a permissive reader accepts that a stricter one would reject — and
  `MIGRATIONS.md` is explicit that any such change "is from here on a v2 change with
  a migration note"; the no-adopters exception "was used exactly once, on the record,
  and is now spent." So R1 **is** the first `SCHEMA_VERSION` bump: the new checks
  carry `since: 2`, repos pinned to v1 receive the new-requirement demotion (WARN,
  "new since your pin") instead of ERRORs, and `MIGRATIONS.md` gains the v1→v2 note
  (add a roster; ensure active-rule owners resolve). S3 was already the second-named
  bump candidate; this is that bump happening.
- **Activation resolution** (`since: 2`): an active rule with an owner field that
  resolves to nothing in the roster → ERROR (WARN under a v1 pin).
- **Appeal-human** (`since: 2`): a rule whose `human_appeal_owner` resolves to
  agent-only holders → ERROR on any active rule, and on a **high-risk draft** too
  (the safety-spine tier decision 3 defines) — WARN under a v1 pin. On a non-high-risk
  draft, or where the appeal owner resolves to nothing, decision 5's WARN tier
  applies instead.
- **Draft visibility (hole a)** (`since: 2`): a draft rule missing any owner field,
  or carrying one that does not resolve → one WARN per gap, named. The existing
  draft-time safety-spine ERRORs are untouched.
- **Missing roster** (`since: 2`): an instance with any active constitution rule and
  no `governance/roles.md` → ERROR (WARN under a v1 pin); an instance with only
  drafts → WARN.
- **Scope: constitution rules only, deliberately.** Owner-shaped fields also live in
  deep records (`accountable_owner`, `gate_owner`), owner cards, and memory records.
  R1 does not resolve them — resolving every owner field everywhere is a larger
  change with its own trade-offs (an ontology owner is descriptive; a rule owner is
  enforcement). The unresolved remainder is a **named remaining hole**, recorded in
  `docs/known-limitations.md` in R1, until a later slice decides it.
- **No reality check:** nothing verifies a roster row against the world. The
  disclaiming-owner problem ("the function, no person named") is caught at
  activation by failed resolution, not by prose analysis — provided no roster row
  carries that exact string; a roster that lists the disclaimer as a Role or Holder
  resolves it, because the roster is trusted text. On a draft it surfaces as hole
  (a)'s named WARN.

### The prose rewrite

The sites above are rewritten to the new semantics: an owner is a role or the person
holding one; a role must be held to activate; the interview elicits the roster (who
holds what, typed) and records where the org map came from. The three explicit
contradictions carry the change: `questions.md:93`'s "A role is not an owner",
`protocol.md:247`'s "a **person**, not a role", and `interview/README.md:149`'s
"a person, not a role?" all become *an owner is a role, and the roster says who
holds it* — and the owner rows in the section at `questions.md:93–98` gain the
office-versus-disclaimer distinction the correction identified, as a question the
interviewer actually asks. The rewrite is scoped from a fresh grep at execution time,
not from this spec's list — the list above is the floor, not the ceiling.

S5's finding (a named owner who cannot confirm) is narrowed but not closed by this
design: holding is recorded in the roster, but *confirmation* of holding by the holder
remains an interview-protocol question, out of scope here and still open under S5.

### Landing order

One slice per session, each through the review-record convention from its own first
review:

- **R0** — the standing rule: build-sessions rule 9 plus the review-log convention.
  Lands first so every later slice keeps its record.
- **S2** — the consent-gate base fix in `generate.md` (already approved: a doc fix
  naming the base — the generation commit — and stating that the commit creating the
  governed root is not subject to the gate; no validator change).
- **R1** — the v1→v2 schema bump: roster schema, the validator changes above,
  rosters for the engine root **and** `demo/` (the engine root is itself a validated
  instance carrying an active rule, so without its own roster R1 would turn
  groundwork's own gate red), the demo roster rows naming its existing person-owners
  as holders, tests, and the `docs/rule-map.md`, `docs/known-limitations.md`, and
  `MIGRATIONS.md` entries.
- **R2** — the `generate.md` contract amendment (hole b) and the prose rewrite.
- **C1–C13** grouped into slices after that; C13 stays held for the S6 decision.

## What this does not do

- **It does not make "held" true.** A roster reflects what the repo says, dated — not
  the world. A stale roster produces exactly the S1 class of confident error, one
  level up. This lands in `docs/known-limitations.md` in R1, as a limitation, never
  softened into a claim.
- **It does not deliver S3's requested encoding.** A practice the confirmed record
  carries as enforced, with an owner nobody claims, still reads as a draft in the
  machine layer; the maintainer chose that as the designed encoding, with named
  WARNs, over a third state. (The record is what is confirmed — whether the practice
  is live is exactly what run 1 left unestablished.)
- **It does not resolve owner fields outside the constitution.** Deep records, owner
  cards, and memory records keep unresolved owner strings in R1 — a named remaining
  hole.
- **It does not verify that a holder accepted the role.** S5 stays open.
- **It does not know what an owner string was meant to be.** Resolution is
  intent-blind: a forgotten role row whose title equals an existing holder name
  resolves as that holder instead of surfacing as unheld (the stated blind spot in
  "The roster", flagged for the maintainer at R1 plan review).
- **It does not analyze owner prose.** A disclaiming owner string fails at
  activation only because it resolves to nothing, never because the validator
  understands disclaimers — put the same string in the roster and it resolves.
