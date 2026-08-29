# Round 03 — `a9bc5de`

**Reviewed revision:** `a9bc5deeb19ca51d781eec217022ae2508122f00`, clean worktree.
**Task id:** `task-mteyl1fu-0458pi`.

**Verdict, verbatim:** "does not approve as written." Summary line, verbatim: "Standards 4
findings, worst **MEDIUM**; Spec 1 finding, **MEDIUM**." Five reported rows, four distinct
defects — the reviewer names the MEDIUM as one cross-axis defect appearing on both axes.

Every defect this round is in round 2's fix or in the record's prose about its own work. No
product edit outside round 2's own repair drew a finding.

## A convention this round forces, adopted from here on

Three rounds running have found a citation that was true when written and false later. From
this entry on, **a line-number citation in this directory is written with the revision it
holds at** — `file:line at <sha>` — because an entry is immutable and the file it cites is
not. Citations already written without one are corrected below and read as holding at their
own entry's reviewed revision.

## Findings

**1. MEDIUM** *(the reviewer's word)*, reported on both axes — `interview/generate.md:291`
at `a9bc5de`. Two faults in one sentence, and the second is the serious one.

*The overclaim.* "The report names what shipped, what shipped incomplete, and what did not
ship at all, each with its reason." A normally shipped artifact needs no reason; the
pre-branch text asked only for a list of them.

*The drift.* Round 2's repair removed a false completeness claim in a way that read as
licensing an incomplete **run report**. Those are two different objects: this document's
bullet list enumerates *kinds* and cannot usefully be closed, while a given run's report
must name *that run's* gaps without exception. Locked decision 6 of the roles design —
"the generation report must name every artifact that shipped incomplete and why" — binds
the second. Round 2 collapsed them and, in doing so, weakened a locked obligation.

**Disposition: fixed.** The intro now separates them: what was generated is listed; every
incomplete or absent artifact is named with its reason, and that obligation is stated as
exhaustive for the run; the bullets are said to be not its boundary, with the general rule
at the top of the file carrying every field no bullet mentions. Locked decision 6 is cited
in this entry rather than in `generate.md`, which is adopter-facing product content and does
not reference the workbench design.

**2. LOW** *(the reviewer's word)* — `round-02.md:36` and `round-01.md:15` both cite
`interview/generate.md:299` for the report list. Round 2's own fix shifted the section:
at `a9bc5de` line 299 was the activities bullet, not the list intro.

**Disposition: corrected here.** Both entries are immutable. **The report-list intro these
two citations mean is `interview/generate.md:291-297` at `a9bc5de`, and `:291-299` at this
round's fix commit; the memory bullets are `:303-307` at `a9bc5de`.** At the entries' own
reviewed revisions the citations were correct.

**3. LOW** *(the reviewer's word)* — `round-01.md:17` and its neighbours carry three
citations that do not land on the quoted or emitting line at HEAD.

**Disposition: corrected here**, with the cause distinguished, because it is not the same as
finding 2. `scripts/validate.py` is **untouched by this branch** (`git diff main...HEAD --
scripts/validate.py` is empty), so these were imprecise when written rather than shifted:

- The quoted `generate.md` sentence — "a record without that answer is drift with a number
  on it (the validator WARNs)" — is at `interview/generate.md:125-126`, unchanged from
  `4fbb9dd` through this round. `:123` is the paragraph's first line.
- The missing-`review_by` WARN is emitted at `scripts/validate.py:1702`; `:1701` is the
  `if` that guards it.
- The missing-`source` WARN is emitted at `scripts/validate.py:1699`; `:1698` is the `elif`
  that guards it.

The checks cited are the right ones; only the lines were the guard rather than the
emission.

**4. LOW** *(the reviewer's word)* — `round-02.md:57`. "No such list can be exhaustive" is
literally false: a finite schema can be enumerated exhaustively at a revision.

**Disposition: the claim is withdrawn here**, `round-02.md` being immutable. The defensible
argument, and the one that actually carried round 2's decision, is **brittleness**: an
enumeration one bullet per required field would have to be maintained against every schema
in the repository and would go stale the first time any of them gained a field. That is a
maintenance argument, not an impossibility argument, and round 2 should have made it as one.
The rejection of a `source`-only bullet stands on its own separate ground, which this round
did not disturb: `provenance` and `valid_at` have identical claim to a bullet, so a
`source`-only bullet would be arbitrary.

## Checked clean this round

The reviewer reports the corrected reviewed SHA, the `provisioned: no` reconciliation, all
seven adopter-facing validator explanations, and `git diff --check` as clean.

## Environment

Sandbox `TemporaryDirectory` errors from `unittest` remain environmental. The suite was run
outside the sandbox at the reviewed revision and again after the fix: 824 tests, OK,
skipped=1.
