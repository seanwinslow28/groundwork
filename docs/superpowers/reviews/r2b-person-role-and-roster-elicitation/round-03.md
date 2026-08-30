# Round 03 — `b8976c0`

**Reviewed revision:** `b8976c0be4d7dddd54b11da8db6ec8642d4eb7f8`, clean worktree.
**Task id:** `task-mtf30yzr-8h857u`.

**Verdict.** No approve / does-not-approve word. Opening line, verbatim: "Round 3 is not
clean: 2 Standards findings and 2 Spec findings." Summary line, verbatim:
"Standards—2 findings, worst **MEDIUM**. Spec—2 findings, worst **HIGH**."

## Correction to `round-02.md`

`round-02.md`'s replacement classification is incomplete and immutable, so it is corrected
here.

Round 2 withdrew `round-01.md`'s false count and put a **classification** in its place —
"a self-audit that named the unchecked cadence conversion and narrowed two citations, a
peer-surfaced correction to a stale enumeration, and the record entries for both". That
accounts for `c4c6ec8`, `a131fe2`, `94b9323` and `f6b493a`. It omits **`9bb0f46`**, a
separate self-audit that withdrew an answer count in `generate.md` and made its derivation
wording plainer.

**The lesson is not "count more carefully."** Round 1 wrote a wrong number. Round 2 replaced
the number with a prose classification, on the reasoning that the classification was the
content and the number never was — and the classification was wrong in the same way, because
a classification that enumerates is a count wearing different clothes. What is checkable, and
all that this record needed:

> The range is `git log 038ddd2..985d294`. Every commit in it except `985d294` predates round
> 1's verdict and came from this session's own audits or from a peer-surfaced correction;
> `985d294` is the findings-fix commit.

That is verifiable by running the command, needs no enumeration, and cannot go stale. Round 2's
two accurate parts stand: the seven-commit observation, and withdrawing rather than replacing
`round-01.md`'s count.

## Findings

**1. HIGH** *(the reviewer's word)*, Spec — role-backed owners had no question that elicits
their holders. Round 2 repaired "holder typing does not reach holder-only rows" by rewriting
the typing row to "for every holder just named" — and in doing so **deleted the only question
that named a role's holders**, which round 1's wording ("who holds each of those roles today")
had carried. After that repair, an owner could be classified as a role and the roster could
never populate its Holder cell, which is the cell an active rule resolves through.
`interview/generate.md` carried the same gap forward, instructing that Role rows be written
from answers no question produced.

**Disposition: fixed.** Section 7 now asks three things in order rather than two: whether each
owner is a role or a named holder; who holds each role that produced; and the type of every
holder either question produced. `generate.md` states the same three in the same order.

**The coverage test cannot catch this class, and this record does not claim it can.** The test
checks that some question names the field `roster:holder`; it cannot check that the question's
words actually elicit a holder. Round 2's entry credited that test with more than it does, and
the reviewer was right to say so.

**2. MEDIUM** *(the reviewer's word)*, Standards — round 2's holder-acceptance repair claimed
an elicitation that does not exist. `interview/protocol.md` said "the interview asks for that
last part" and `docs/known-limitations.md` repeated it. No question in `interview/questions.md`
asks whether a holder knows or accepted — the authority section asks for owners, the
role-versus-holder classification, holder type and cadence, and nothing else. The limitation
also called itself "narrower than" the stale-roster limitation while its own counterexample
showed the two are independent.

**Disposition: fixed**, both halves. Both files now say plainly that **no question asks it**,
and that the holders in a roster are named by whoever sat the interview. The limitation says
**orthogonal**, which is what its counterexample demonstrates. Adding the question is S5's
work, which the design puts out of scope here; what this slice owed was an accurate
description of what it did not build.

Recording the sequence, because it is the more useful fact: round 2 fixed an unbacked claim by
writing a limitation, and the limitation contained a fresh unbacked claim of its own. A
correction is not a safe place.

**3. MEDIUM** *(the reviewer's word)*, Spec — the demo's own new layer retained the narrowing
the three root sites had dropped. `demo/interview/00-manifest.md` said "a person or a role",
and `demo/interview/06-org-map.md` used "Person or role" as its section heading, its table
header and its cell values.

**Disposition: fixed**, to the locked form. The demo's data is unchanged and was always valid —
all three owners are named holders who are human — but the design's prose-rewrite section says
the sweep is scoped from a fresh grep and is a floor rather than a ceiling, and **this slice
authored a fourth site while repairing the first three**. A grep run before the new file existed
could not have found it; re-running it after each round would have.

**4. MEDIUM** *(the reviewer's word)*, Standards — `round-02.md`'s chronology correction is
incomplete. **Disposition: corrected above**, in the section this entry opens with.

## Checked clean this round

The reviewer confirms the twice-revised global sentence — "never supplies an interview answer
the company did not give" — checks out, on the grounds that the derived and defaulted fields
are classified as non-answers and the unanswered-cadence fallback is disclosed as such. It also
confirms round 2's seven-commit observation and that withdrawing rather than replacing the
count was correct.

## Environment

The reviewer ran all three validator invocations, `git diff --check` and the targeted
question-skeleton tests successfully, and did not rerun the full suite in the read-only
sandbox. Run outside the sandbox at the reviewed revision and again after the fixes: 824 tests,
OK, skipped=1. Gates after the fixes: `validate.py .` 0 errors 7 warnings exit 0;
`validate.py demo` 0 errors 2 warnings; `validate.py . --diff main` exit 0.
