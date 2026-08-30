# Round 04 — `74c86be`

**Reviewed revision:** `74c86be8788057ce9baa85e0f096cc575da957bc`, clean worktree.
**Task id:** `task-mtf3bngw-k09po4`.

**Verdict.** No approve / does-not-approve word. Opening line, verbatim: "Round 4 is not
clean: 2 Standards findings and 2 Spec findings." Summary line, verbatim:
"Standards—2 findings, worst **MEDIUM**. Spec—2 findings, worst **HIGH**."

## Corrections to `round-02.md` and `round-03.md`

Both entries are immutable; both carry a claim this round showed false.

**`round-03.md`'s finding 2 over-generalised.** It recorded the fix as both files now saying
"no question asks it", which is true, but the prose it approved also said **nothing in the
repository** records a holder's answer. `demo/interview/06-org-map.md` records that every named
owner was present and that each affirmed the accountability was theirs; the demo roster and the
pending proposal repeat it. What is true is narrower and is what both files say now: no question
in the skeleton asks it, no schema field carries the answer, no check looks for one. The
"orthogonal to stale-roster" classification that entry also made stands — the reviewer confirms
it independently.

**`round-02.md`'s finding 3 stated a row-level invariant the schema does not have.** It recorded
the coverage requirement's reason as "a roster row with either cell empty is an ERROR". It is
not: `test_role_row_with_no_holder_is_legal_and_unheld` proves `| CISO |  |  |` is legal, and
that unheld state is one locked decision 2 keeps deliberately. The requirement itself was right
and stays; its reason is **active-owner resolution** — an active rule's owners must resolve to a
holder and its appeal owner to a human one, so an interview that never asks who holds what can
generate drafts and nothing else.

## Findings

**1. HIGH** *(the reviewer's word)*, Spec — the first roster question excluded the locked
unheld-role state. Round 3's wording, "is it a role somebody holds, or a named holder?",
narrowed the locked pair a second time — by two words this time rather than by a paraphrase.
Decisions 2 and 4 keep an unheld role as a legal, meaningful state: a Role row with empty Holder
and Type, which resolves to nothing and therefore keeps the rules naming it as drafts. An unheld
role fits neither offered answer, so it would never be "just named" for the holder question that
follows it. `generate.md` repeated the narrowing.

**Disposition: fixed.** The question is now the locked pair and nothing else — "is it a role, or
a named holder?" The holder question says **"nobody yet" is an answer**, and says it is the
answer that keeps the rule a draft. `generate.md` writes that row with Holder and Type empty and
routes the rules naming it to the gap rule.

This is the third narrowing of the same locked form on this branch: a paraphrase (round 2), a
site the slice authored itself (round 3), and now two extra words inside the corrected wording.
The pattern is worth stating: **every time this form was restated in the session's own words it
got narrower.** It is now quoted rather than restated.

**2. HIGH** *(the reviewer's word)*, Spec — an agent-only appeal owner could be generated onto
an **active, non-high-risk** rule. `generate.md`'s three gap classes are missing, unresolvable
and disputed; its no-human exception names high-risk rules only. A non-high-risk rule whose
`human_appeal_owner` matches the roster but resolves entirely to agent-typed holders therefore
had no listed gap, kept its rung, and shipped active — and `scripts/validate.py`'s check fires
on `active or high_risk`, not on high-risk alone, so the gate ERRORs it. **Generation would
produce a repo that fails its own gate on the first run**, which is the specific outcome the
R1-window edits exist to prevent.

**Disposition: fixed, without adding a fourth gap class**, because decision 6 locks the number
at three and a fourth would be an amendment this slice has no mandate for. Decision 3 makes the
human-holder constraint part of **activation resolution**, so an appeal owner resolving only to
agents has not resolved — it is the second class, read correctly. `generate.md` now says that
explicitly and says why the other reading is the dangerous one: the field looks answered, no gap
is listed, the rung stays on, and the validator refuses it.

**3. MEDIUM** *(the reviewer's word)*, Standards — round 3's acceptance repair introduced a
false global claim. **Disposition: corrected above**, and fixed in both files.

**4. MEDIUM** *(the reviewer's word)*, Standards — the coverage test's rationale contradicted
the roster schema. **Disposition: corrected above**, and the comment in `tests/test_validate.py`
now gives the real reason, naming both the round that added the requirement and the round that
caught the reason.

## Checked clean this round

The reviewer reports a repository-wide search found **no further live "person or role"
narrowing**, and that round 3's chronology correction matches `git log 038ddd2..985d294`. The
two targeted question-coverage tests passed.

## The shape this branch keeps producing

Four rounds, and in each of rounds 2, 3 and 4 the worst finding was inside the previous round's
repair. Round 3 already named one half of it — a correction is not a safe place. Round 4 adds
the sharper half: **three of the four defects this round were introduced by prose written to fix
a defect**, and in every case the repair reached for a stronger claim than the one it replaced —
"every field", "nothing in the repository", "either cell empty is an ERROR". The claim that
survives review is the narrow one that is checkable, not the broad one that sounds like a
guarantee.

## Environment

The reviewer ran the targeted question-coverage tests and did not rerun the full suite in the
read-only sandbox. Run outside the sandbox at the reviewed revision and again after the fixes:
824 tests, OK, skipped=1. Gates after the fixes: `validate.py .` 0 errors 7 warnings exit 0;
`validate.py demo` 0 errors 2 warnings; `validate.py . --diff main` exit 0.
