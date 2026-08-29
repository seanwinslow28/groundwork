# Round 04 — `99514c3`

**Reviewed revision:** `99514c39d2d987837b22878fc8335fe673678b2d`, clean worktree.
**Task id:** `task-mteyx4ff-aj3yig`.

**Verdict.** No approve / does-not-approve word. Summary line, verbatim: "Standards 2 LOW
findings; Spec 0 findings."

**Spec is clean.** The reviewer reports that round 3's `generate.md` repair preserves locked
decision 6's exhaustive per-run obligation without claiming the bullet list is closed, stays
consistent with the general rule at the top of the file, and retains the pre-branch
generated-activities list; and that the `provisioned: no` reconciliation and the
adopter-facing validator descriptions match their sources. No product file is changed by this
round's fix commit — both findings are in `round-03.md`.

## Findings

**1. LOW** *(the reviewer's word)* — `round-03.md:15` at `99514c3`. "Three rounds running
have found a citation that was true when written and false later" is false.

**Disposition: the claim is withdrawn here**, `round-03.md` being immutable. It was a
generalisation about this directory's own history, asserted without recomputing it — which
is the failure this record has now committed twice. **Recomputed, from the entries:**

- **Round 2** found one citation defect: `round-01.md`'s `interview/generate.md:10-15`,
  where the sentence ends at line 16. The paragraph did not move between the writing and
  the finding, so it was **imprecise when written**.
- **Round 3** found three. `round-01.md:15` and `round-02.md:36` citing
  `interview/generate.md:299` had **become stale** — round 2's own fix moved the section.
  `round-01.md`'s `interview/generate.md:123` for a sentence at `:125-126` was **imprecise
  when written**, the paragraph being unchanged. `round-01.md`'s `scripts/validate.py:1701`
  and `:1698` were **imprecise when written** too: that file is untouched by this branch, so
  nothing moved; the citations named the guard rather than the line that emits.
- **Round 1** found no citation defect at all. It found a missing report class.

So: two rounds, four citation defects, of which **one** became stale later and **three** were
wrong from the moment they were written. The entry that introduced the convention described
the minority cause as the whole pattern, and it contradicted itself doing so — its own
finding 3 says in as many words that the validator citations were "imprecise when written
rather than shifted".

*What follows for the remedy,* stated because the convention was sold on the wrong premise:
pinning a revision fixes the **staleness** class only. The imprecision class — a citation
that never landed on the line it names — is not a notation problem and no notation fixes it.
It is fixed by opening the file and reading the line before writing the citation, which is a
discipline, and the three defects above are what skipping it costs.

**2. LOW** *(the reviewer's word)* — `round-03.md:16` at `99514c3`. The entry does not follow
the convention it introduces: `scripts/validate.py:1702` and `:1699` at `round-03.md:63-66`
carry no revision, and `round-03.md:49` says "at this round's fix commit" rather than a SHA.

**Disposition: accepted, and the convention is restated here in a form that can be followed.**
`round-03.md` stated a rule with no carve-out for the one citation it could not satisfy — a
reference into the fix commit being written, whose SHA does not exist yet. A rule whose own
introducing entry breaks it is not a rule.

**The convention, as it binds from this entry on:**

- A line-number citation carries the revision it holds at: `` `file:line` at `<sha>` ``.
- The one exception is a forward reference to **this round's own fix commit**, which cannot
  carry a SHA because it does not exist when the entry is written. Name it as
  "this round's fix commit"; the `README.md` rounds table resolves it to a SHA, which is
  already that table's job.
- A citation into a file the branch does not modify still carries a revision. It costs
  nothing and it removes the reader's need to know what the branch touched.

**The two citations finding 2 names, restated in that form.** Both hold at `99514c3` and,
`scripts/validate.py` being untouched by this branch, at every revision on it:

- The missing-`review_by` WARN is emitted at `` `scripts/validate.py:1702` `` at `99514c3`.
- The missing-`source` WARN is emitted at `` `scripts/validate.py:1699` `` at `99514c3`.

And `round-03.md:49`'s forward reference resolves, under the rule above, through the rounds
table: `interview/generate.md:291-299` at `99514c3`.

## Environment

Sandbox `TemporaryDirectory` errors from `unittest` remain environmental. The suite was run
outside the sandbox at the reviewed revision: 824 tests, OK, skipped=1. The reviewer
independently reports the validator at 0 errors, 8 warnings, and `git diff --check` clean.
