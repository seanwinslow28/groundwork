# Entry 01 — maintainer decision, not a review round

This entry is **not a Codex review round.** It records four decisions the maintainer took
before any code on this branch was written, and the measurements put to them.

**Decided:** 2026-08-30, by the maintainer, against `9e8d7f8` (a clean tree; the branch had
no commits of its own yet).

## The slice's finding-class, named under rule 11

Rule 11 requires this, and requires it here rather than later. **The class this slice is
about: whether the marker-existence evidence classifies a working tree correctly — a marker
that existed between the base and HEAD and is now gone must be reported, and a repository
that never carried one must not be.** Findings in that class are what keep the review loop
running. Findings outside it — prose accuracy, record accuracy, test provenance — are real
and get fixed, but under rule 11 they do not by themselves justify another round.

## Gate baselines verified before any edit, on `9e8d7f8`

- `python3 scripts/validate.py .` -> 0 error(s), 7 warning(s), exit 0
- `python3 scripts/validate.py demo` -> 0 error(s), 2 warning(s)
- `python3 scripts/validate.py . --diff main` -> exit 0
- `python3 -m unittest discover -s tests` -> OK, 861 tests, skipped=1

## What was measured, and how

The kickoff instructed re-confirmation rather than trust. The fixture was built from the
**committed** helpers in `tests/test_validate.py` (`_git`, `_write`, `_iv_state`, `PIN_OK`,
`RULE_OK`, `IV_LAYER_OK`) rather than hand-authored — issue #40's own comment records that
its original `0 error(s), 8 warning(s)` figure came from an uncommitted scratch fixture and
so cannot be re-run, and this entry does not repeat that.

Base: a pre-generation commit. Working change: delete `groundwork.pin` and
`interview/00-manifest.md`, add an unproposed clause to a constitution rule, and rewrite a
confirmed interview layer.

| Pass | On `9e8d7f8` | On `ea05b28` |
|---|---|---|
| `diff_base_findings` | 0 findings | absent at that revision |
| `blast_radius_diff_findings` | 0 findings | 0 findings |
| `interview_diff_findings` | 0 findings | 0 findings |
| `memory_diff_findings` | 0 findings | 0 findings |

The control — the same working change against a base that holds both markers — returned the
`no pending proposal` ERROR from the tripwire and the `frozen at its checkpoint` ERROR from
the frozen-layer guard. So the silence is specific to the pre-marker base, and it is
unchanged from `ea05b28`.

**Question 1 of the issue was answered by measurement, not by argument.**
`git log <base>..HEAD -- groundwork.pin interview/00-manifest.md` named the commit that
introduced the markers, in both variants tried: the deletion left uncommitted in the working
tree, and the deletion committed on top. That is a source of evidence beyond the two trees,
and it reads nothing that `check_interview_state`'s discovery-by-content doctrine governs.

## Two corrections to the kickoff document

1. It names the control test `test_deleting_the_marker_is_still_caught_when_the_base_holds_it`.
   The test in the tree is `test_marker_deletion_hides_nothing_when_the_base_holds_the_markers`.

2. It states that this slice is a **tightening** and therefore a v2 change with a migration
   note, and asked for that reading to be verified either way. **It was verified and it does
   not hold.** MIGRATIONS.md scopes a tightening to content a permissive reader once
   accepted that a stricter one now ERRORs — a requirement on content shape.
   `diff_base_findings` already settled the same question for #31 in its own docstring: its
   conditions reject no content, and the same tree under the same pin passes against a base
   that meets the contract; what they constrain is the invocation. This slice is that same
   species. Independently: `apply_since_demotion` resolves pins from the working tree via
   `_pin_versions`, so a deleted pin is absent from `pins`, `pinned` is None, and no
   demotion can fire — a `since:` tag on a marker-deletion finding would be inert by
   construction. **No version bump and no migration note.**

## The four decisions

**1. Rule 10 adopted as written** — a check the issue did not ask for is a rule 5 escalation
before it is written. Written into `docs/agents/build-sessions.md` by this session, with the
#32 evidence and the counter-argument that it adds a round-trip to work that is often
necessary.

**2. Rule 11 adopted, with the round-01 addition** — a round with no findings in the slice's
class sends the slice to the maintainer, and the class is named in round 01. The
counter-argument recorded with it corrects the kickoff's framing: #32's rounds 08, 09 and 11
each found a Major after an earlier round looked clean, and all three were inside the
out-of-scope guard that rule 10 would have prevented. Rule 11 is adopted **because** rule 10
is.

**3. Issue #40 implemented, narrowly: the walk supplies evidence and emits a finding, and
nothing changes what the stateful passes gate.** Considered and not taken: feeding the
discovered root back into `_pin_dirs` and `interview_diff_findings` so gating resumes. That
is more thorough and materially larger, and it changes the behaviour of passes this issue
did not ask about. The narrow option mirrors `_unsupported_root_finding`, which also reports
rather than re-gates.

Also considered and not taken: **declining**, and leaving the limitation documented.
`docs/known-limitations.md` already discloses the hole without overclaiming, two tests pin
it, and the consent gate rests on the commit bit rather than on the validator. It was
refused because the evidence route was measured to work and is small, and because unlike
#32's second guard this **is** the scope the issue asked for.

**4. ERROR, and the same treatment for the pin and the manifest.** A WARN exits 0, so the
run stays green and the escalating changes stay unreported. #31 chose ERROR for the
analogous base-predates-this-root case. The messages differ because the two markers protect
different things; the mechanism and the severity do not. The cost, recorded: a repository
deliberately removing groundwork goes red under `--diff` until it stops passing a
pre-marker base.

## Residual limit, stated before it is built

The walk reads committed history. A shallow clone whose graft point is newer than the
commit that added the marker will not see it, and the run will be silent. That is the same
silence the tree has today, so it is not a regression, and it belongs in
`docs/known-limitations.md` rather than in a claim that the escape is closed.

## A changed gate baseline, declared

`python3 scripts/validate.py .` goes from **7 warnings to 8** on this commit, and the extra
one is not a defect this branch introduced into any shipped file. `check_entropy` matches
`[A-Za-z0-9+/=_-]{40,}`, a class that excludes `.`; rule 10's citation of
`docs/superpowers/reviews/issue-32-changelog-preamble/round-17.md` contains a 57-character
run with no dot in it, so it reads as a possible secret. The same file already carries the
same false positive on `main` for the design-spec path in "Where the plan lives", so this is
the established behaviour rather than a new class of noise.

Shortening the citation to a directory link was tried and did not clear it — the slug alone
keeps the run over 40. The citation is the evidence for rule 10, so it is kept precise and
the baseline is declared instead of the reference being degraded to satisfy a check whose
own message says it is "high-signal, not exhaustive".
