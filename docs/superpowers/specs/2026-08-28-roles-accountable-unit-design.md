# Roles as the accountable unit — design

> **Workbench artifact, not product content.** The design settling the fork the
> multi-agent decision opened: if a role is the accountable unit, must the role be held?
> Brainstormed and decision-locked with the maintainer 2026-08-28, in one session, six
> decisions — each presented with options, a recommendation, and the honest
> counter-argument (build-sessions rule 5), and each chosen by the maintainer. It feeds
> Fable implementation plans through the ordinary slice loop; nothing here is built yet.

## Why this exists

The maintainer decided this session that groundwork is becoming a multi-agent OS:
ontology roles are filled by agents — open and closed models both — adoptable by a
company or a solo builder, and **role titles are valid owners**. The code already
agrees: `governance/constitution/access-grants-need-human-signoff.md` fills every owner
field with a role title (`owner: Head of IT`, `value_owner: CISO`,
`human_appeal_owner: CISO`), and `tests/test_validate.py`'s `RULE_OK` fixture asserts
that rule is clean (verified against both files, this session). The prose says the
opposite in eight load-bearing places (grep, this session): `README.md:22` and `:102`,
`interview/generate.md:142` and `:149`, `interview/protocol.md:247` ("an owner who is a
**person**, not a role"), `interview/questions.md:97` and `:105`, and
`interview/README.md:149`.

Accepting roles as owners reopens the S3 void one level up. Run 1's record carried
`runtime_check_owner: "Delivery coordination — the function, no person named"`, and it
passed, because the check rejects only placeholders. The quad-check correction
(`~/Code-Brain/persona-company/runs/2026-07-31/quad-check-correction.md`) put the
distinction exactly: *"`Head of IT` names an accountable office, while 'the function,
no person named' disclaims one, and the check cannot tell them apart."* If any role
string is a valid owner, *enforced, but nobody owns it* comes back wearing a role
title. If only filled roles are valid, the schema again cannot express the true state
run 1 found — a live practice nobody claims — and generators are pushed back to the S3
corner: refuse to ship, or invent.

This design also settles the two confirmed enforcement holes recorded in
`quad-check-correction.md` and the durable-review-record rule, because all three take
their shape from the holding semantics.

## Decisions locked (maintainer, 2026-08-28)

1. **Roles are the accountable unit.** A role title is a valid value for every owner
   field. (Maintainer's decision preceding the brainstorm; restated here because
   everything below inherits it.)

2. **Held-to-activate.** A rule with a rung (active) must have every one of its owner
   roles resolve to a holder; a rule with no rung (draft) may carry unheld or absent
   owners. This mirrors the draft/active split the validator already implements — the
   code comment reads "Required in full once a rule is active (rung-placed)" and
   "incomplete is fine while drafting" (`scripts/validate.py:1811`, `:1852`, verified
   this session). The draft state becomes the *designed* home for incompleteness rather
   than an accident of check ordering.
   *Counter-argument, recorded:* "held" means the repo says held. A roster is
   repo-internal consistency, not reality — it can go stale the way run 1's
   finance-sign-off record did. This is an S1-class limitation and is documented, not
   solved (see "What this does not do").

3. **Holders are typed, and the human appeal must reach a human.** A holder is a
   person or an agent, and the roster marks which. The one per-object constraint: the
   `human_appeal_owner` role must resolve to at least one **human** holder — an appeal
   path that terminates in a model is not an appeal path. Value, rule, and
   runtime-check owners may be agent-held.
   *Counter-argument, recorded:* per-object holder-type rules add a distinction the
   schema could not previously see, and the smallest adopter — one human holding
   everything — carries typing machinery built for the multi-agent case.

4. **Resolution lives in one roster file per instance.** `governance/roles.md`: each
   role, its holder(s), each holder typed `human` or `agent`, with `valid_at` and
   `review_by` dating its staleness, org-memory style. The decisive argument is the
   prior session's own pattern data: its dominant failure mode was parallel-site drift
   — a fix reaching some sites but not all, seven occurrences — and holders written
   inline in every rule's frontmatter would build exactly that failure shape into every
   adopter repo. One roster is one place to go stale, and a dated one.
   *Counter-argument, recorded:* the rule's reader no longer sees the holder without a
   lookup; it is one more required file; the interview must now elicit it.

5. **Hole (a), the drafting gate: WARN, naming each gap.** A draft rule raises one
   WARN per missing or unresolvable required field — rule owner, appeal owner, sunset,
   an owner role with no roster entry — each named specifically. Today an absent rule
   owner and appeal owner on a draft raise nothing at all. Blocking would contradict
   decision 2's premise that the draft state is where incompleteness legitimately
   lives; silence is how run 1's "two drafts and zero active rules" stayed illegible.
   *Counter-argument, recorded:* WARNs are ignorable, and this one guards the
   governance layer.

6. **Hole (b), the shipping contract: permit declared drafts.** `interview/generate.md`
   is amended: an artifact missing required fields may ship only as a draft that
   declares its gaps in-file, and the generation report must name every artifact that
   shipped incomplete and why. An undeclared incomplete shipment stays prohibited.
   Under decision 2 this is not a concession — the declared draft is the designed
   encoding of *confirmed but incomplete or unheld*. Run 1's declared-draft shipment
   becomes compliant **in form**; its report obligation was not met at the time, and
   this spec says so rather than blessing it retroactively.
   *Counter-argument, recorded:* declaring may become cheaper than completing; the
   generation report obligation is the pressure against that, and a run 2 can measure
   whether it holds.

7. **Durable review verdicts: a standing rule, stored beside the plan.** A slice may
   not merge unless the verdicts of every Codex review round run against it — findings,
   severities, and dispositions (fixed in commit X / rejected with grounds), not just
   the final approve — are committed in the repository:
   `docs/superpowers/plans/<slice>-reviews.md`, appended per round on the branch, so
   the merge carries the record. Plan-less work uses
   `docs/superpowers/reviews/<branch>.md`.
   The evidence: the prior session's record was **not** captured. Its 24 rounds survive
   only as fix-commit subjects (`Codex r1`–`r15` on groundwork's log, with r3 and r9
   absent — no way now to tell whether those rounds found nothing or their record was
   lost), and the honesty plan's own header says its three rounds' "review outputs were
   not retained", leaving the merge commit as "the durable record of the approval"
   with "no inspectable artifact" dating round 3 itself. The pattern data this rule exists to keep — the
   prior session's seven parallel-site drifts and four unverified-inference errors —
   came from non-gating rounds and would be invisible in a merge-gate-only log.
   *Counter-argument, recorded:* roughly 3x the record volume (24 rounds, 2 gating,
   in that session), and appending during review adds a step to every round.

## The design

### The roster

One file per validated instance (company repo, `demo/`), `governance/roles.md`.
Sketch — the implementation plan owns the exact format:

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

One person may hold many roles (the solo builder holds all of them). A role with no
row, or a row with no holder, is **unheld**. The roster is content, so it is checked
wherever it lives, per the instance rule.

### The validator (the one code slice)

- **Activation resolution:** an active rule (rung present) whose owner role does not
  resolve to a roster holder → ERROR. Resolution is by exact role string.
- **Appeal-human:** an active rule whose `human_appeal_owner` role resolves to agent
  holders only → ERROR.
- **Draft visibility (hole a):** a draft rule missing any required field, or carrying
  an owner role that does not resolve → one WARN per gap, named.
- **No reality check:** nothing verifies a roster row against the world. `_answered()`
  keeps rejecting placeholders; the disclaiming-owner problem ("the function, no
  person named") is caught at activation by failed resolution, not by prose analysis.
- A missing roster in a repo with active constitution rules is an ERROR; a missing
  roster with only drafts is a WARN.

### The prose rewrite

The eight sites above are rewritten to the new semantics: an owner is a role; a role
must be held to activate; the interview elicits the roster (who holds what, typed) and
records where the org map came from. `interview/questions.md`'s owner rows change
meaning: "Name a person, not a queue" becomes *name a role, and say who holds it* —
the disclaimer-vs-office distinction the correction identified becomes a question the
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
- **R1** — roster schema, validator changes (activation resolution, appeal-human,
  hole-a WARNs), demo roster, tests, `docs/rule-map.md` and
  `docs/known-limitations.md` entries. The schema change is a candidate for the first
  `SCHEMA_VERSION` bump, alongside health-metrics — this is S3's resolution, and S3
  was already named the second bump candidate.
- **R2** — the `generate.md` contract amendment (hole b) and the eight-site prose
  rewrite.
- **C1–C13** grouped into slices after that; C13 stays held for the S6 decision.

## What this does not do

- **It does not make "held" true.** A roster reflects what the repo says, dated — not
  the world. A stale roster produces exactly the S1 class of confident error, one
  level up. This lands in `docs/known-limitations.md` in R1, as a limitation, never
  softened into a claim.
- **It does not verify that a holder accepted the role.** S5 stays open.
- **It does not analyze owner prose.** A disclaiming owner string fails at activation
  because it resolves to nothing, not because the validator understands disclaimers.
