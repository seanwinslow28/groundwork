# Round 02 — `c00b2b7`

**Reviewed revision:** `c00b2b71a4e0e0a0945b2a62aa8ee8d251f9dea9`, clean worktree.
**Task id:** `task-mtf2lcle-zkqlya`.

**Verdict.** No approve / does-not-approve word. Opening line, verbatim: "Round 2 is not
clean: 3 Standards findings and 3 Spec findings." Summary line, verbatim:
"Standards—3 findings, worst **HIGH** global overclaim. Spec—3 findings, worst **HIGH**
incomplete owner/holder elicitation."

**Four of the six were inside round 1's own repairs**, which is the failure mode this
session was warned to expect and did not avoid. The remaining two were in the elicitation
rows this slice exists to add.

## Correction to `round-01.md`

`round-01.md:13` is wrong and immutable, so it is corrected here rather than edited.

It said eight commits landed between round 1's launch and its entry, and that none came from
a finding. Both halves fail. The table directly beneath it lists six rows, so the sentence
contradicts its own evidence at a glance; `985d294` is in that table labelled "This round's
fixes", so "none came from a finding" is false of the row it sits above; and
`git log 038ddd2..c00b2b7` returns seven, the entry commit included.

**No number replaces it** — the previous slice's round 5 established that a corrected count is
a count the next entry has to re-audit, and the classification was always the content. What
was true, stated without arithmetic: **between round 1's launch and its fix commit, the branch
moved on for reasons unrelated to the review** — a self-audit that named the unchecked cadence
conversion and narrowed two citations, a peer-surfaced correction to a stale enumeration, and
the record entries for both. `985d294` is the findings-fix commit and belongs to no such
category. The reviewer based its findings on committed `c00b2b7`, correctly.

## Findings

**1. HIGH** *(the reviewer's word)*, Standards — round 1's five-field repair overcorrected
into a false global claim. `README.md` and `docs/EXPLANATION.md` had been made to say the
generator transcribes answers rather than supplying them, "that rule binds every field it
writes". Untrue: the generator derives `last_reviewed` and `next_review`, writes
`provisioned`, aggregates the roster's `valid_at`, composes its `source`, and falls back on a
default `review_by` — and this repository's own tests classify three of those as `NOT_ASKED`.

**Disposition: fixed**, at the rule's real width: the generator never supplies an interview
**answer** the company did not give, the roster's holders and types included. The five explicit
marks are untouched.

This is the second time in two slices that removing a false completeness claim produced a
different false claim in its place, and the shape is now specific enough to name: **the
replacement for an overclaim is a narrower true statement, not a broader one.** Round 1's fix
reached for "every field" because it read as the strongest available guarantee; the strongest
available guarantee was the thing that made it false.

**2. HIGH** *(the reviewer's word)*, Spec — the locked "role or named holder" model was
narrowed to "person or role". Locked decision 1 and the design's prose-rewrite section give
the replacement form as *an owner is a role or a named holder*; decision 3 allows value, rule
and runtime-check owners to be agent-held. The three rewritten sites offered only person-or-
role, so an owner a company names directly as an agent could be elicited only by miscasting it
as a role or by leaving it out.

**Disposition: fixed**, and by adopting the spec's own words verbatim at all three sites
rather than paraphrasing them. `questions.md:93`'s note, `protocol.md`'s "what good looks
like" bullet, and `interview/README.md`'s sample question now read "a role or a named holder".
The typing row says a named holder need not be a person, and `generate.md` states that an
owner named directly and typed `agent` is a holder-only row like any other.

Worth recording why the paraphrase happened: the additive form was read as *adding roles to
persons*, when what decision 1 adds is roles to **named holders** — and a named holder is the
wider category. Paraphrasing a locked form is how the narrowing entered.

**3. HIGH** *(the reviewer's word)*, Spec — full holder typing was not actually elicited for
holder-only owners. "Who holds each of those roles today, and is each holder a human or an
agent?" is grammatically about the holders of roles, so an owner answered as a person — which
becomes a holder-only row, and is the demo's own three rows — was never typed at all. The
reviewer also found the hole in this slice's new coverage test: `roster:holder` and
`roster:type` were in the known set but not the required set, so both elicitation rows could
be deleted without failing coverage.

**Disposition: fixed**, both halves. The question now reads "for every holder just named — of
a role, or standing alone". `roster:holder` and `roster:type` are required, with the reason
stated in the test: a roster row with either cell empty is an ERROR, so a skeleton that stops
asking for them ships a roster the gate rejects. Verified by deletion — removing the typing
row now fails with `roster:type` named. `roster:role` stays known-but-not-required
deliberately, and the comment says why: a holder-only row's Role cell is legitimately empty,
which is exactly what the demo's three rows are.

**4. MEDIUM** *(the reviewer's word)*, Standards — the rejected wording survived in the live
contract. `interview/generate.md` still described the question as asking whether a holder is
"a person or an agent" after `questions.md` had moved to the enum's words. The enum rule added
in round 1 limited the damage, but two normative instructions disagreed.

**Disposition: fixed.** Recorded as its own defect rather than folded into finding 1's entry,
because the cause is worth keeping: round 1's CRITICAL was fixed at the site the reviewer
cited and not at the site that quotes it. A contract that describes a question is a second
copy of that question.

**5. MEDIUM** *(the reviewer's word)*, Spec — the protocol claimed holder confirmation the
locked spec leaves open. `protocol.md`'s bullet ends "and whoever holds it knows", while the
design says confirmation of holding by the holder "remains an interview-protocol question, out
of scope here and still open under S5".

**Disposition: fixed**, and the finding is better than it reads. The clause is **inherited** —
it predates this branch — so the tempting disposition was *out of scope*, one of rule 9's three
rejection categories, naming S5 as the follow-up. That was not taken, on checking:
`docs/known-limitations.md` carried **no entry at all** about holder confirmation, so the
claim was not merely out of scope, it was unbacked anywhere in the repository. It now has one,
distinguished from the stale-roster limitation next to it: a roster can be freshly confirmed by
the person writing it and still name a holder who has never heard of the role. The protocol
bullet keeps the aspiration and points at the limitation.

**6. MEDIUM** *(the reviewer's word)*, Standards — `round-01.md`'s chronology is false.
**Disposition: corrected above**, in the section this entry opens with.

## Checked clean this round

The reviewer independently confirms both 90-day additions, the 101-day age, that 182 and 365
are defensible as explicitly local day-count conventions, the layer description, the pinned
citation, the future-tense baselines, the five explicit marks, and that the proposal's `## Diff`
block matches the roster as it now stands.

## Environment

The reviewer reran the three validators, `git diff --check`, and the targeted skeleton tests
successfully, and did not rerun the full suite because of the documented sandbox restriction.
Run outside the sandbox at the reviewed revision and again after the fixes: 824 tests, OK,
skipped=1. Gates after the fixes: `validate.py .` 0 errors 7 warnings exit 0; `validate.py
demo` 0 errors 2 warnings; `validate.py . --diff main` exit 0.
