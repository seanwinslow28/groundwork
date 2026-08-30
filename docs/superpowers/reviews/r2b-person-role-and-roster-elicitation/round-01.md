# Round 01 — `038ddd2`

**Reviewed revision:** `038ddd2634b6263591abaab1d79828736f743c76`, clean worktree.
**Task id:** `task-mtf22uf6-xyowy7`.

**Verdict.** No approve / does-not-approve word. Summary line, verbatim: "6 Standards
findings, worst **HIGH**; 1 Spec finding, **CRITICAL**."

## Commits that landed after this round was launched

The reviewer notes that "the live worktree became modified" during the review and that it
based every finding on committed `038ddd2`. That is accurate and it was this session's doing.
Eight commits landed between the launch and this entry; **none came from a finding**, and
recording them is what keeps the reviewed revision from being read as HEAD:

| Commit | What |
|---|---|
| `c4c6ec8` | Self-audit: the unchecked cadence conversion named in `docs/known-limitations.md`; two record citations narrowed |
| `9bb0f46` | Self-audit: a count withdrawn in `generate.md`'s roster rule |
| `a131fe2` | The pin-less-engine limitation named two governed families; there are three |
| `94b9323` | The record's entry for that scope call |
| `f6b493a` | The same entry corrected: fixed on this branch, not closed by it |
| `985d294` | This round's fixes |

Finding 4's second half was already repaired by `c4c6ec8` before the verdict arrived. It is
recorded below as fixed, not as fixed-by-this-round, because the sequence matters more than
the credit.

## Findings

**1. CRITICAL** *(the reviewer's word)*, Spec axis — the elicited holder type violated the
roster's enum. `interview/questions.md` asked whether each holder is "a person or an agent";
`interview/generate.md` said those answers are transcribed with the type written "as
answered". The roster's enum is `HOLDER_TYPES = {"human", "agent"}`
(`scripts/validate.py:2027` at `038ddd2`, a file this branch does not touch). The demo
exposed the gap the reviewer named: `06-org-map.md` answered `person` and the roster silently
wrote `human`, an undocumented normalization the contract never licensed.

**Disposition: fixed**, and the finding understated its own severity, which is worth
recording. The reviewer wrote that literal `person` "produces an ERROR". Measured rather than
reasoned — `person` written into `demo/governance/roles.md`, gate run, file restored — it
produces **eight**: the mistyped row drops the holder out of resolution entirely, so every
owner value naming that person fails to resolve and every rule they own goes red. A company
repo following the shipped contract literally would have been red on every active rule, not
carrying one bad cell.

The fix asks in the roster's own two words rather than documenting a normalization, because a
normalization is a step a generator can skip: the question is now "is each holder a human or
an agent", `generate.md` states that the Type cell takes those two values and nothing else
and that any other word is written as whichever of the two it means — never transcribed
literally, with the eight-ERROR consequence stated — and the demo layer answers in the enum.

**2. HIGH** *(the reviewer's word)* — "quarterly" did not deterministically produce the
stated dates. Both rosters showed a 90-day span while calling it quarterly; three calendar
months from 2026-08-20 is 2026-11-20, not 2026-11-18, and from 2026-08-29 is 2026-11-29, not
2026-11-27. `generate.md` defined no conversion convention, so "the date that produces" rested
on nothing.

**Disposition: fixed**, taking the reviewer's first option. `generate.md` now fixes the
conversion as a **day count** — a quarter 90 days, a half-year 182, a year 365 — requires the
span in the recorded derivation alongside the cadence and the base date, and says why the span
is written down at all: the word is looser than the number, and a date a reader cannot redo is
a date they have to trust. Both rosters carry the span, so both additions are now reproducible
from the file. Day count rather than calendar arithmetic because the unanswered-question
fallback is already 90 days, and one arithmetic for the elicited answer and the fallback is
the property that lets a reader compare them.

**3. HIGH** *(the reviewer's word)* — the proposal's motivating age was false.
`demo/proposals/org-map-re-confirmed.md` said "The map was five months old" against its own
dates of 2026-05-11 and 2026-08-20, which is 101 days.

**Disposition: fixed.** It now says 101 days, three months and change, past the ninety-day
mark the file itself had set. Recorded with the reviewer's own emphasis kept: this was
evidence inside a **consent artifact**, which is the worst place in the repository for a
number nobody checked.

**4. MEDIUM** *(the reviewer's word)* — two defects, reported as one row.

*Layer 6 misdescribed the interview it joins.* `demo/interview/06-org-map.md` said the five
layers before it each mapped a function; `01-role-and-scope.md` sets the analyst's role and
the company's scope, so only 02–05 are function layers. **Fixed**, naming the split.

*The review record's evidence prose.* Two parts. The citation of `questions.md:93` for the
deleted text carried no revision, which this directory's inherited convention requires of a
citation offered as evidence for a claim about where something is — **fixed**, pinned at
`555f8d2`. The round-11 grounds were stated as one when round 11 records two — **already
fixed at `c4c6ec8`**, from this session's own audit, before the verdict arrived.

**5. LOW** *(the reviewer's word)* — the record claimed artifacts that did not exist. Its
baselines section said they were stated "in the merge commit, and in the entries"; at
`038ddd2` the branch was unmerged and the directory held only `README.md`.

**Disposition: fixed**, now future tense. This is the third defect of one shape on this branch
— the other two being the "#39 is closed by this branch" claim and this entry's own
predecessor — and the shape is worth naming rather than counting: **prose that describes a
state the commit it ships in has not reached.** All three were written while the thing they
asserted was still one decision away.

**6. LOW** *(the reviewer's word)* — the public five-field claim was under-scoped.
`README.md` (twice) and `docs/EXPLANATION.md` present five fields as the generator's refusal
surface, while R2b's roster contract also forbids inventing roles, holders, types and dates.

**Disposition: fixed**, and deliberately by widening rather than by narrowing. The previous
slice's round 3 measured what goes wrong here: removing a false completeness claim
overcorrected into weakening a real obligation, because a document's illustrative list and a
binding rule are different objects and it collapsed them. So all three sites now say **both**:
the generator transcribes rather than supplies, in every field it writes, **and** five carry
that refusal as an explicit mark. The five are not reduced and the general rule is not
implied — each is stated.

## One repair that drew its own ERROR

Recorded because it is the gate doing its job on this session rather than a mishap worth
hiding. Fixing finding 1 involved writing `human` in backticks into the demo roster's body. A
roster body may carry **no backtick at all** — a code span can run across lines and render the
whole table as code — so the validator refused the file and, with it, every owner it resolves:
13 ERRORs. Removed; the roster body has no backticks, and the check that caught it is the one
this slice's own contract depends on.

## Also reported, and checked clean

The reviewer independently confirms the `valid_at` aggregation is correct — every entry's
latest confirming layer is layer 06, all dated 2026-08-20, so the earliest across entries is
2026-08-20 — that the proposal's `## Diff` block matched the actual roster edit, that the two
pending proposals and six confirmed layers both check out, and that `git diff --check` is
clean. The `## Diff` block was re-synced after this round's fixes changed the roster again.

## Environment

The reviewer did not rerun the suite, naming it sandbox-hostile, which is the expected
condition. Run outside the sandbox at the reviewed revision and again after the fixes: 824
tests, OK, skipped=1. Gates after the fixes: `validate.py .` 0 errors 7 warnings exit 0;
`validate.py demo` 0 errors 2 warnings; `validate.py . --diff main` exit 0.

## For the maintainer, out of scope here

`scripts/validate.py`'s no-backtick ERROR message reads "a roster body carries no a backtick".
A word is wrong. This branch does not touch `scripts/validate.py` and will not start; noted so
it is not lost.
