# Roles as the accountable unit — design

> **Workbench artifact, not product content.** The design settling the fork the
> multi-agent decision opened: if a role is the accountable unit, must the role be held?
> Brainstormed and decision-locked with the maintainer 2026-08-28, in one session,
> seven decisions — the first carried in from the maintainer's own kickoff decision,
> the other six each presented with options, a recommendation, and the honest
> counter-argument (build-sessions rule 5), and each chosen by the maintainer. An
> eighth decision was put to the maintainer the same way and locked 2026-08-29,
> after adversarial review round 17 surfaced it (decision 8 below). The
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
passed — because the rule shipped as a draft, and the validator inspects
owner-completeness fields only on active rules (`scripts/validate.py`, the rung
branch; verified this session — the one exception, the high-risk safety spine that
checks appeal fields on drafts too, did not apply: this rule's action class is
`external-side-effect`, not `high-risk`). Had the rule been active, `_answered()`
would have accepted the sentence anyway — it rejects placeholders, empty values,
and non-strings, and any substantive sentence passes. The quad-check correction
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
`quad-check-correction.md`, which take their shape from the holding semantics — and,
alongside them, the durable-review-record rule, which does not: it is settled in the
same session because its evidence (the prior session's lost review record) was
established here.

## Decisions locked (maintainer, 2026-08-28 and 2026-08-29)

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
   with no appeal path must not leave the gate green" stays true verbatim in the
   sense that check gives it — answered appeal fields; decision 3 states how its
   resolution-strengthened form tiers under version pins.
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
   forbids verbatim). On a **high-risk draft** the same logic closes the remaining
   gap: an answered appeal owner that resolves to *nothing* also ERRORs there — an
   appeal reaching no human is no appeal path by this decision's own definition, and
   a WARN would leave exit 0, exactly the green gate the spine forbids. On
   non-high-risk drafts, an appeal owner resolving to nothing stays in decision 5's
   WARN tier — unheld is the drafting state. The tiers under a v1 pin differ by
   age: the existing check — a high-risk rule whose appeal fields are not answered —
   is a v1 ERROR and keeps firing as one under any pin, and decision 2's verbatim
   spine guarantee is that check's. Both **new** resolution-based ERRORs —
   agent-only holders, and resolves-to-nothing on a high-risk draft — are `since: 2`
   and demote to WARN on v1-pinned content, necessarily so: a v1 repo has no roster
   to resolve against, so a resolution check cannot bind content pinned before
   rosters existed. Those demoted WARNs never mean a green gate: a v1 pin on the v2
   engine is already red at the single migration-boundary ERROR (skew ≥ 1,
   `scripts/validate.py`'s pin check), and the WARNs are the finger-pointing behind
   it that the migration contract promises — one clean boundary error, never a
   scatter. The resolution-strengthened form of the spine therefore binds at full
   ERROR strength from a v2 pin, and no pinned state runs it as WARN-only with a
   green gate. Value, rule, and runtime-check owners may be agent-held.
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
   rule owner, value owner, runtime-check owner, appeal owner), an owner value that
   does not resolve (no roster match, or a match on a Role row with no holder), and
   an appeal owner that resolves but to agent-only holders on a non-high-risk
   draft — resolvable, wrongly typed. Each WARN names its gap specifically. (A missing sunset already
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
   rule carrying a gap in any of three classes — a required field that is missing, a
   field populated but unresolvable against the roster, or a field populated but
   recorded as disputed — may ship only as a draft that declares those gaps in-file,
   and the generation report must name every artifact that shipped incomplete and
   why. (These are the contract's own classes, deliberately wider than decision 5's
   WARN classes: they cover every required field, not only owner fields, and the
   disputed class is visible only in prose — a recorded dispute binds the generation
   contract and its in-file declaration, never a validator check, which does not
   read dispute prose. Run 1's central case, the populated-but-unresolvable
   `runtime_check_owner`, is the second class; the intake gate's disputed action
   class the third.) An undeclared incomplete shipment stays prohibited. **One
   safety-spine exception:** a high-risk rule whose appeal fields are missing or
   unresolvable does not ship at all, declared or not — decisions 2 and 3 ERROR it
   even as a draft, so the declared-draft path cannot apply; the spine outranks the
   contract — and the same logic covers every **rung-independent** gate ERROR, not
   only the appeal gaps: a repealing rule without its orphan prohibition satisfied
   (an answered surviving job, reassigned) ERRORs draft or not, so it cannot ship
   as a declared draft either. The appeal-gap forms the exception names: missing,
   unresolvable, or resolving to no human holder. And it binds by the
   **stricter reading of a disputed class**: where a recorded action-class dispute
   includes `high-risk` among the accounts, the exception applies as if the rule
   were high-risk, even when the scalar field carries the lower class — otherwise
   a dispute the validator cannot read would ship a rule the spine would reject.
   (This takes S4's stricter-reading direction for exactly this contract clause;
   S4's full tie-break rule remains its own queued slice.) The other artifact
   kinds stand unchanged: a deep record missing its Gate answer and a memory record
   missing its owner do not ship — those kinds have no draft state to ship into, and
   this design does not invent one — while a skill missing human-only answers is
   already written into the repo as `provisioned: no`, the work-package
   convention's own drafting state. (`generate.md`'s wording both denies and
   affirms this today — "the skill does not ship — write it `provisioned: no`",
   then "the skills that shipped `provisioned: no`" — a self-contradiction R2's
   contract amendment reconciles; the file behavior is unchanged either way.)
   Under decision 2 this is not a concession — the declared draft is the designed
   encoding of *confirmed but incomplete or unheld*. Run 1 already practiced this
   contract for the gaps it recognized as gaps: each shipped rule declares its own
   missing fields in-file — the quad-check its rule owner, appeal owner, and sunset;
   the intake gate its value statement, value owner, appeal path and owner, and
   sunset, plus the action-class dispute its body records as unresolved ("Each file
   names its own missing owners in its body rather than pretending to be complete")
   — and the generation report names both incomplete rules and those reasons under
   "What did not ship, and why" (`generation-report.md:45–72`, verified this
   session). One gap
   it did not declare, because it was not yet one: the disclaiming
   `runtime_check_owner` becomes unresolvable (absent a roster entry that resolves
   its exact string — a Holder cell, or a Role row with a holder) — and therefore a
   declared-draft obligation — only under this design. The amendment makes the contract match the
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
   **Amended 2026-08-29 (maintainer):** `docs/agents/build-sessions.md` rule 9 is now the
   operative text — one normative copy, which four review rounds of drift between these two
   sites argued for. **The contract as stated in this decision is superseded by rule 9 and
   retained unedited, as the record of what was decided rather than as instructions to
   follow**; where the two differ, rule 9 governs. The storage convention above is the
   clearest case: rule 9 replaces the single flattened file with one directory per branch
   and one file per entry.
   The evidence: the prior session ran twenty-five review rounds — sixteen on the
   groundwork branch, nine on the persona-company correction, per the merge commit
   `df6df21` — and what survives is what its commits chose to carry. Fix commits
   preserve the accepted findings and their dispositions in their bodies — sometimes
   with severities, as `f5ab4b6`'s "Two HIGH findings, both correct" — but what
   survives is only what each commit chose to quote: no complete round output
   exists, rejected findings and full verdict text appear nowhere, and two rounds whose
   numbers left no commit (r3 and r9 in the `fix(build): Codex r…` sequence) are
   unrecoverable. (Evidence corrected on branch `docs/review-record-rule`, Codex round 3:
   the approving r16 left no numbered commit either, but `df6df21` carries its verdict, so
   it is not among the unrecoverable. The normative choice is unchanged; only this evidence
   paragraph is.) The honesty plan paid for the same loss earlier: its
   header says its three rounds' "review outputs were not retained", leaving the
   merge commit as "the durable record of the approval" with "no inspectable
   artifact" dating round 3 itself. The pattern data this rule exists to keep — the
   recurring drift class and the four factual defects build-sessions rule 8 now
   counts — came from non-gating rounds and would be invisible in a merge-gate-only
   log.
   *Counter-argument, recorded:* roughly 12x the record volume (twenty-five rounds,
   two of them approving, in that session), and appending during review adds a step
   to every round.

8. **The roster joins the consent gate: a third governed artifact family —
   additions and modifications, with a migration-scoped bootstrap.** (Maintainer, 2026-08-29 — the one decision made
   after the original brainstorm, when review round 17 found that an ungoverned
   roster edit could redirect an active rule's appeal endpoint silently.) A change
   to `governance/roles.md` in a governed root is an escalating change requiring a
   matching proposal, extending locked #17's routing contract from two artifact
   families to three — addition and modification both. The one exemption is the
   **migration-scoped bootstrap** (re-decided by the maintainer 2026-08-29, after
   review round 23 showed an earlier modifications-only narrowing was an
   unapproved change resting on a false S2 analogy): a roster addition is not
   escalating when the same diff moves the root's pin from v1 to v2, because
   every v1→v2 migration necessarily adds its roster — the exemption is exactly
   the migration boundary, the sanctioned crossing mechanism. A freshly generated
   repo is covered by S2's baseline convention, not by base-absence: the
   interview layers are committed before generation, so a base exists, and S2's
   approved fix names the **generation commit itself as the base** for subsequent
   `--diff` runs — the commit that creates the roster is therefore never inside a
   changeset the gate examines. A roster added to a root already at v2 — a re-add after
   deletion included — is gated like any other escalating change, which closes
   the delete-then-re-add route: deletion still only WARNs, but with active rules
   the deleted state is red at the missing-roster ERROR, and the re-add needs a
   proposal regardless of what the root holds. **Deletions keep the existing
   WARN-only limitation** that `docs/known-limitations.md` already documents for
   rules and skills.
   *Counter-argument, recorded:* deletion is an attacker's cheapest move against a
   roster, and it stays loud-after-the-fact rather than gated; and every #17
   extension grows the surface the two-family promise was meant to keep small.
   Gating deletions for all three families was weighed and declined as a larger
   redesign than R1 should carry.

## The design

### The roster

One file per validated instance — the engine root, `demo/`, and every company repo —
at `governance/roles.md`. Sketch; the implementation plan owns the exact format:

```markdown
---
valid_at: 2026-08-28
review_by: 2026-11-26
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
demo's `owner: Ruth Okafor` resolves because Ruth Okafor appears as a holder. A
holder-only row (Role cell empty) is legal: it makes its holder resolvable without
asserting a role, which is what R1's generation writes for person-confirmed owners.
A role with no row, or a row with no holder, is unheld.

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
  and is now spent." So R1 **is** the first `SCHEMA_VERSION` bump: v1-pinned repos
  hit the single migration-boundary ERROR the pin check already emits at skew ≥ 1,
  `MIGRATIONS.md` gains the v1→v2 note (add a roster; ensure active-rule owners
  resolve), and the per-check `since:` mechanism — documented intent today, scheduled
  by `MIGRATIONS.md` to be wired "when the first breaking bump to v2 is authored" —
  is wired in this slice: the new checks carry `since: 2` and demote to WARN behind
  the boundary ERROR, so migration guidance is precise finger-pointing rather than a
  scatter of field ERRORs. S3 was already the second-named bump candidate; this is
  that bump happening.
- **Activation resolution** (`since: 2`): an active rule with an owner field that
  resolves to nothing in the roster → ERROR (behind a v1 pin's migration-boundary ERROR, demoted to a finger-pointing WARN).
- **Appeal-human** (`since: 2`): a rule whose `human_appeal_owner` resolves to
  agent-only holders — or, on a **high-risk draft**, to nothing at all — → ERROR on
  any active rule and on high-risk drafts (the safety-spine tier decision 3
  defines) — behind a v1 pin's migration-boundary ERROR, demoted to a finger-pointing WARN. On a non-high-risk draft, an appeal owner
  resolving to agent-only holders or to nothing takes decision 5's WARN tier
  instead.
- **Draft visibility (hole a)** (`since: 2`): a draft rule missing any owner field,
  or carrying one that does not resolve → one WARN per gap, named. The existing
  draft-time safety-spine ERRORs are untouched.
- **Missing roster** (`since: 2`): an instance with any active constitution rule and
  no `governance/roles.md` → ERROR (behind a v1 pin's migration-boundary ERROR, demoted to a finger-pointing WARN); an instance with only
  drafts → WARN.
- **Scope: constitution rules only, deliberately.** Owner-shaped fields also live in
  deep records (`accountable_owner`, `gate_owner`), owner cards, and memory records.
  R1 does not resolve them — resolving every owner field everywhere is a larger
  change with its own trade-offs (an ontology owner is descriptive; a rule owner is
  enforcement). The unresolved remainder is a **named remaining hole**, recorded in
  `docs/known-limitations.md` in R1, until a later slice decides it.
- **Roster mutations are governed** (decision 8; `--diff` mode, `since: 2`): an
  addition or modification of `governance/roles.md` in a governed root is an
  **escalating change requiring a matching proposal**, exactly as a constitution
  rule's is — except an addition in the same diff that moves the root's pin from
  v1 to v2, decision 8's migration-scoped bootstrap, which makes the tripwire
  pin-motion-aware — the roster decides who holds every active rule's owners and where
  its human appeal terminates, so editing it is governance, not bookkeeping.
  Deletions keep the documented WARN-only limitation all governed families share.
  **This makes the roster a third governed artifact family**, and R1 changes
  every surface built for two: the proposal target schema (which currently ERRORs
  on non-constitution, non-skill targets), `_governed_class()` (today three
  classifier values across two families; the roster adds a fourth value, third
  family), the #17 routing contract's enumeration, the blast-radius tripwire,
  `docs/rule-map.md`, and the tests.
- **No reality check:** nothing verifies a roster row against the world. The
  disclaiming-owner problem ("the function, no person named") is caught at
  activation by failed resolution, not by prose analysis — provided no roster entry
  resolves that exact string; a roster listing the disclaimer as a Holder, or as a
  Role row with a holder, resolves it, because the roster is trusted text (a Role
  row with no holder still fails — it is unheld). On a draft it surfaces as hole
  (a)'s named WARN.

### The prose rewrite

The sites above are rewritten to the new semantics: an owner is a role or a named
holder (a person may be a holder without any role asserted — the holder-only row);
a role must be held to activate; the interview elicits the roster (who holds what,
typed) and records where the org map came from. The three explicit
contradictions carry the change: `questions.md:93`'s "A role is not an owner",
`protocol.md:247`'s "a **person**, not a role", and `interview/README.md:149`'s
"a person, not a role?" all become *an owner is a role or a named holder, and the
roster resolves it* — the additive form decision 1 requires, under which person
owners and holder-only rows stay valid — and the owner rows in the section at
`questions.md:93–98` gain the
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
  `MIGRATIONS.md` entries, **and the demo pin migrated to `schema_version: 2`** —
  without that, the R1 engine's own gate goes red on `demo/groundwork.pin` at the
  migration boundary. **The demo roster lands under decision 8's
  migration-scoped bootstrap:** its addition sits in the same diff that moves
  `demo/groundwork.pin` from v1 to v2, so the tripwire does not classify it
  escalating. (A carried pending proposal was considered and is impossible:
  applied changes must not sit beside their pending proposals — the build's own
  decision record rejects that state — and removing the proposal would fail the
  very tripwire that demanded it.) From the first post-migration change on,
  decision 8 binds in full. **The engine-root roster is maintainer-authored content, and
  R1's plan carries it as an explicit maintainer input:** the engine's own active
  rule names `Head of IT` and `CISO`, no file identifies who holds those roles for
  the groundwork instance, and the implementing agent must not invent the answer —
  the maintainer names the holders (realistically themself, for a solo-maintained
  engine) as part of landing R1. **R1 also carries the minimal `generate.md`
  workflow edits** — the pin writes `schema_version: 2`, and a `governance/roles.md`
  is generated from the confirmed owner answers, inventing neither holders nor
  types: a holder enters typed `human` only where the binding protocol guarantees a
  person — the acted-on activity owner and the skill owner, the answers under the
  row whose note reads "A role is not an owner" (`questions.md:93`) and
  `protocol.md:247`'s person guarantee. The backup owner is **not** among them:
  its `(human-only)` marker denotes the answer's source, not the holder's
  humanity, and nothing forbids a role-shaped backup — so it is not entered.
  Person-confirmed owners are entered as **holder-only rows** (the Role cell
  empty; those questions yield a person's name, not a role). The roster's
  `valid_at` records when the mapping was last confirmed — for an R1-window
  roster, the **earliest `confirmed_at` among the interview layers its entries
  transcribe**: a conservative aggregate, since layers freeze independently and a
  newer layer reconfirms nothing about older entries; the earliest date means no
  entry's staleness is masked and the derived `review_by` comes sooner, never
  later. Never the generation date, which may fall later and confirms nothing.
  (R1's implementation plan may instead carry a per-row confirmed date, which
  dominates the aggregate; the file states whichever it uses.) Snapshot
  semantics, deliberately narrower than org-memory's when-the-fact-became-true
  `valid_at`, and stated as such in the file. **Generation precondition:** the
  source layers' `confirmed_at` dates must parse as real, non-future ISO dates —
  today the validator only WARNs on a malformed one, so a frozen interview can
  carry `confirmed_at: someday`, leaving the aggregate undefined. A malformed or
  future date stops roster generation with the offending layer named — and the
  legal recovery is **a new confirming turn**, never an edit: frozen layers are
  immutable, so the operator runs a correction layer re-confirming the affected
  entries with a parseable date, and the aggregate reads each entry's most recent
  confirming layer. The generator never invents a date. (Append-and-supersede,
  the posture the whole record already keeps.) Its `review_by`, which no current question elicits, is a stated interim
  **policy default** (90 days from `valid_at`, matching the sketch), recorded in the file as
  default-not-answered — a weaker cousin of C10's derivation, which had an
  elicited cadence to derive from where this has none — replaced by an elicited
  answer from R2 on. Every other owner
  value (a constitution rule's owners may be roles or disclaimers; run 1's
  `runtime_check_owner` proves it) is **not entered at all** — writing it as a
  Role row would assert a role the record never confirmed, a disclaimer least of
  all; the roster asserts nothing about it, it fails resolution by absence —
  unless the same string coincides with an entered holder, the documented
  intent-blind blind spot, in which case it resolves as that person. Where at
  least one decision-6 gap remains — an owner unresolved, a required field
  missing, or a recorded dispute — the rule ships rungless as a declared draft
  under decision 6 — subject to its full safety-spine exception: a rule carrying
  any rung-independent gate ERROR (a high-risk appeal gap in any of its three
  forms, or the orphan prohibition unsatisfied) does not ship at all — with its
  declared gaps named; a rule with no decision-6 gap at all, coincidental
  resolution included, proceeds by the ordinary path. The minimal edits carry
  the declared-draft permission **together with its paired accountability
  condition** — the generation report must name every constitution rule that
  shipped incomplete and why — because landing the permission without the
  obligation would remove exactly the pressure decision 6 counts on. Role rows, agent-typed holders, and typing for the rest arrive with
  R2's elicitation — for repos generated **after** R2: a repo generated in the
  R1–R2 window keeps its holder-only roster, which stays valid v2 content, and
  enriching it is that company's own edit (content is never re-copied by an
  engine pull). These edits exist because without them the documented
  generation workflow is broken for exactly the window between R1 and R2: today's
  `generate.md` instructs `schema_version: 1`, which the R1 engine ERRORs at the
  migration boundary, and writing `2` without a roster fails the missing-roster
  check on any active rule. A generation run on the R1 engine must produce a
  passing repo.
- **R2** — the rest of the `generate.md` contract amendment (hole b) — the
  `provisioned: no` reconciliation and the wider report wording — and the prose
  rewrite, including the full roster elicitation (typed holders asked for
  directly, rather than derived from the human-only markers). The narrow
  declared-draft permission, its exceptions, and its constitution-rule report
  obligation land together in R1's minimal edits: the R1-window generation path
  depends on the permission, and the obligation is its paired condition.
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
  understands disclaimers — put the same string in the roster as a Holder, or as a
  Role row with a holder, and it resolves.
