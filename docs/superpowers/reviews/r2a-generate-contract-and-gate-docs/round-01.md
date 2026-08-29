# Round 01 — `4fbb9dd`

**Reviewed revision:** `4fbb9dd725660305b8ce9e1ef62ce00ae7df8e03`, clean worktree.
**Task id:** `task-mtextles-jwz2sf`.

**Verdict.** The reviewer used no approve / does-not-approve word. Its own summary line,
verbatim: "Standards 0 findings; Spec 1 finding, worst severity MEDIUM."

It also stated that all seven adopter-facing validator explanations matched the cited
implementation — governed-file classification, deletion severity, generation-base
behaviour, and the base-plus-manifest condition — and that no added link was broken.

## Findings

**1. MEDIUM** *(the reviewer's word)* — `interview/generate.md:299`. The generation-report
list misses a class the document's own body creates: a memory record that ships **without**
`review_by`. The body permits it at `interview/generate.md:123` ("a record without that
answer is drift with a number on it (the validator WARNs)"), and `scripts/validate.py:1701`
WARNs rather than ERRORs, so the record ships. The list named only the baselines that did
*not* ship for an unanswered `owner`.

**Disposition: fixed.** Verified against both cited sources before accepting — the
validator line and the generate.md paragraph both say what the finding says they say. A
second bullet now names the shipping-but-incomplete case beside the not-shipping one.

*What the fix deliberately does not say.* The reviewer's suggested wording was to
"generalize the baseline bullet". The tempting generalisation — that `review_by` is the one
required memory field a record may ship without — is **false**: a record whose `provenance`
is not `confirmed` and whose `source` is blank also ships on a WARN
(`scripts/validate.py:1698`). So the fix names the one case the body actually carves out
and claims nothing about the set. The missing-`source` case is not added as a bullet
because the body grants no permission for it; it falls under the general rule at
`interview/generate.md:10-15`, which this branch widened to cover every required field,
named or not.

## Carried into the same fix commit, found by the builder rather than the round

`README.md`'s "Deleting a governed file **WARNs**" took its referent from the preceding
sentence's enumeration. "Deleting one of those governed files" says it without the
back-reference. No factual change.

## Two additions in this slice that are additions, not reconciliations

Named here so a later round judges them rather than inheriting them. Two entries in the
widened report list are **new obligations**, not restatements of wording already in the
document: a rule that did not ship at all under the safety-spine exception, and the
roster's `review_by` where it carries the interim policy default. Both follow from locked
decision 6's "the generation report must name every artifact that shipped incomplete and
why", and from this branch's own widening of the general rule; neither was previously
written as a report obligation anywhere.

## Environment

The reviewer was told, and the record repeats: its sandbox cannot create temp directories,
so `unittest` there produces environmental `TemporaryDirectory` errors. The suite was run
outside the sandbox by the builder at this revision — 824 tests, OK, skipped=1 — and again
after the fix, with the same result.
