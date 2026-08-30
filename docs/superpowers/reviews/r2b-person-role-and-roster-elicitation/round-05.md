# Round 05 — `104709b`

**Reviewed revision:** `104709bcf02eab1bdf325e4993bae39d03bfb817`, clean worktree.
**Task id:** `task-mtf3pf5p-fgfduc`.

**Verdict.** No approve / does-not-approve word. Opening line, verbatim: "Round 5 is not
clean: 3 Standards findings and 3 Spec findings." Summary line, verbatim:
"Standards—3 findings, worst **MEDIUM**. Spec—3 findings, worst **HIGH**."

## Correction to `round-04.md`

`round-04.md`'s closing section misattributes its own evidence and is immutable.

It listed three repairs that reached for too strong a claim — "every field", "nothing in the
repository", "either cell empty is an ERROR" — and presented them as round 4's three
repair-induced defects. **"Every field" was round 2's finding 1, not round 4's.** Round 4's
third was "role somebody holds", the two extra words that excluded the unheld role. The
pattern the section names is real and this round confirms it again; its arithmetic was
borrowed from the wrong rounds.

## Findings

**1. HIGH** *(the reviewer's word)*, Spec — **round 4's fix drifted from locked decision 5.**
That fix closed a real behavioural hole by declaring an agent-only `human_appeal_owner` to be
decision 6's "unresolvable" class. Decision 5 names, verbatim, "an owner value that **does not
resolve** (no roster match, or a match on a Role row with no holder)" and "an appeal owner that
**resolves but to agent-only holders** on a non-high-risk draft — resolvable, wrongly typed" as
**two separate classes**. The fix collapsed them. The reviewer's judgement was that closing the
hole "requires a maintainer-approved spec amendment or explicit additional shipping
treatment—not reinterpretation of locked taxonomy", and that is correct.

**Disposition: fixed, and the route was the maintainer's to choose, not this session's.** The
kickoff's standing rule is that a fix touching a maintainer decision stops and asks; three
options were put with a recommendation and its counter-argument, and the maintainer chose the
one now in the tree:

`interview/generate.md` **reclassifies nothing**. It states the case as what decisions 2 and 3
already make it — an **activation** condition, since decision 3 requires the appeal owner to
resolve to at least one human holder and makes that part of activation resolution on an active
rule. The rule may not carry a rung; it ships rungless and declares the state in its body and
in the generation report anyway, on the principle that more disclosure is the safe direction.
Decision 6's three gap classes are untouched, and the text says out loud that this state is
*resolvable and wrongly typed* and **not** one of them.

*The counter-argument, recorded because the maintainer decided against it:* the in-file
declaration and the report obligation are decision 6's machinery, borrowed here for a state
decision 6 does not name — a strict reader could call that widening decision 6's obligation by
the back door. The alternatives were amending decision 6 to a fourth class (rejected: a
twenty-five-round decision reopened by a review round, for a case decision 5 already names
correctly in its own tier) and leaving the finding open with the fix backed out (rejected: that
knowingly ships a `generate.md` producing a repo that fails its own gate on the first run).

**2. HIGH** *(the reviewer's word)*, Spec — nothing stopped the interview producing a
Role/Holder namespace collision. The three questions cover holder-only, held-role, multi-holder
and unheld-role rows, but a role held by a person whose own name is another role's title —
the reviewer's example: Role `CISO` held by `Head of IT`, plus Role `Head of IT` held by Alice —
transcribes into a roster where every reference to that string is ambiguous. `_parse_roster`
ERRORs it and defines no precedence **deliberately**, so generation was free to produce a
gate-red repo.

**Disposition: fixed.** `generate.md` gains a precondition beside the others: no string may be
both a Role and a Holder; **stop and disambiguate with the company, never pick a winner, never
invent a suffix to break the tie.** The answer is the company's — which of the two the owner
values meant — and the roster is written after they say it. This is the same posture as the
malformed-`confirmed_at` precondition already there: generation halts and names the problem
rather than resolving it by inference.

**3. MEDIUM** *(the reviewer's word)*, Spec — "nobody yet … keeps the rule a draft" omitted
decision 6's exception. Where the unheld role is a **high-risk** rule's appeal owner, the rule
does not ship at all, declared or not. The outranking paragraph later in the file kept the
protocol from being wrong overall, but the new claims stated it incompletely at the point a
reader meets it.

**Disposition: fixed.** Both the question's note and `generate.md` now say the state prevents
**activation**, subject to the high-risk appeal exception, rather than saying it makes a draft.

**4. MEDIUM** *(the reviewer's word)*, Standards — the acceptance limitation's **headline**
still carried the global claim its body had already retracted: "Nothing asks a holder whether
they accepted the role" against a body naming `demo/interview/06-org-map.md`, where every
holder was asked directly and affirmed.

**Disposition: fixed** — "No question asks a holder whether they accepted the role, and no
check verifies it." Recorded plainly: **round 4 narrowed the body of that limitation and left
its headline alone.** A headline is a claim.

**5. MEDIUM** *(the reviewer's word)*, Standards — "the one way to generate a repo that fails
its own gate on the first run" is false. `docs/known-limitations.md` already documents another
unresolved composition that does exactly that — a skill shipping `provisioned: no` whose deep
record also did not ship, leaving a dangling `ontology:` reference.

**Disposition: fixed** — "a way". Worth keeping: the false word was *one*, written for emphasis
in a sentence whose actual job was causal. Superlatives are the cheapest overclaim available and
this branch has now produced several.

**6. LOW** *(the reviewer's word)*, Standards — `round-04.md`'s enumeration misattributes its
evidence. **Disposition: corrected above.**

## Checked clean this round

The reviewer confirms the round-04 corrections' substantive evidence, the coverage-test
rationale, and the validator's `active or high_risk` behaviour. It ran the targeted skeleton
tests, all three validator invocations and `git diff --check`.

## Environment

The reviewer did not rerun the full suite in the read-only sandbox. Run outside the sandbox at
the reviewed revision and again after the fixes: 824 tests, OK, skipped=1. Gates after the
fixes: `validate.py .` 0 errors 7 warnings exit 0; `validate.py demo` 0 errors 2 warnings;
`validate.py . --diff main` exit 0.
