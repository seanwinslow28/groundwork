# Round 05 — `5081052`

**Reviewed revision:** `50810524fbf50ea7103d5a2852aa8c9eb314b122`, clean worktree.
**Task id:** `task-mtez4xg4-7mdfyz`.

**Verdict.** No approve / does-not-approve word. Summary line, verbatim: "Standards 2 LOW
findings; Spec 0 findings."

Spec clean for the second consecutive round. The reviewer reports the product edits preserve
decision 6's exhaustive per-run obligation, reconcile `provisioned: no` correctly, and match
the validator's behaviour; and that the README rounds table and round 4's corrected targets
check out. Both findings are in `round-04.md`. No product file changes in this round's fix.

## Findings

**1. LOW** *(the reviewer's word)* — `round-04.md:36` at `5081052`. The recomputation's tally
groups two pairs without saying so: counted as distinct wrong citations rather than as
reported finding rows, the total is six, not four.

**Disposition: the tally is withdrawn, not corrected.** The count was ambiguous because it
never named its unit — reported finding rows or distinct citations — and both readings are
available from the sentence. Replacing four with six would leave a number that the next entry
has to re-audit for the same reason. **The classification is the content; the tally never
was.** It stands without a number:

- Citations that became **stale** — true when written, false after a later commit moved the
  text: `interview/generate.md:299`, cited in `round-01.md` and again in `round-02.md`.
- Citations that were **imprecise when written** — never landing on the line named, in text
  that did not subsequently move: `interview/generate.md:10-15` (the sentence ends at 16);
  `interview/generate.md:123` (the quoted sentence is at 125-126);
  `scripts/validate.py:1701` and `:1698` (both name the guard, not the line that emits, in a
  file this branch does not touch).
- Round 1 found no citation defect.

The point that survives is the one round 4 drew: a revision pin addresses staleness only, and
the imprecise class is not a notation problem.

**2. LOW** *(the reviewer's word)* — `round-04.md:25` at `5081052`. `round-04.md` breaks the
convention it restates: unpinned citations at `:25-33`, and `round-03.md:49` cited at `:73`
with no revision, none of them the permitted forward reference.

**Disposition: accepted, and the convention is narrowed here.** Two entries in a row have now
failed to follow this convention while introducing or restating it — round 3's, then round
4's. Read once, that is carelessness; read twice, it is evidence the rule was drawn too wide,
and the second reading is the one that fits. Requiring a revision on *every* line number made
it unfollowable in the passages that discuss citations most, because those passages mention
citations by the dozen.

**The convention, narrowed, from this entry on:**

- A citation offered as **evidence for a claim about where something is** carries the
  revision it holds at.
- A citation **named as the subject of discussion** — a previously defective string being
  quoted as defective — does not. It is a token, not an assertion about the file.
- A forward reference to **this round's own fix commit** cannot carry a SHA; name it as such
  and let the `README.md` rounds table resolve it.

`round-04.md`'s further requirement — that a citation into a file the branch does not modify
carry a revision too, "it costs nothing" — **is withdrawn.** Two rounds of it not being
followed is the measurement that it does cost something.

## Environment

Sandbox `TemporaryDirectory` errors from `unittest` remain environmental. The suite was run
outside the sandbox at the reviewed revision: 824 tests, OK, skipped=1. The reviewer
independently reports 0 errors, 8 warnings, and `git diff --check` clean.
