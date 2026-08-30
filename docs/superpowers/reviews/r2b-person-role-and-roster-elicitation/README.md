# Codex review record — branch `docs/r2b-person-role-and-roster-elicitation`

The durable per-round record [rule 9](../../../agents/build-sessions.md) requires. Rule 9
is the operative text; this file carries the parts that keep changing, and each
`round-NN.md` beside it is fixed once committed.

**Why `reviews/` and not `plans/`.** Rule 9 routes a branch to
`docs/superpowers/plans/<slice>-reviews/` only when its own commits add or change exactly
one plan. This branch adds and changes none, so it takes `reviews/<slug>/`, where `<slug>`
is the branch name's last path component. The path was free in `main` at branch time, so
no collision suffix applies.

**Branch:** `docs/r2b-person-role-and-roster-elicitation`, cut from `main` at `555f8d2`.

## What this slice is

R2b — the second half of the R2 the maintainer split at R2a's kickoff. Two parts that the
[roles design](../../specs/2026-08-28-roles-accountable-unit-design.md)'s landing order
names together and that R2a proved cannot be separated:

- **The person-versus-role prose rewrite.** The three sites that state the contradiction
  explicitly become the additive form locked decision 1 requires — an owner is a role or a
  named holder, and the roster resolves it — under which person owners and holder-only rows
  stay valid.
- **Full roster elicitation.** Typed holders asked for directly, and a review cadence for
  the org map, replacing R1's stated interim policy default.

**Why one unit.** `interview/generate.md`'s holder-typing rule was built on the sentence at
`interview/questions.md:93` **at `555f8d2`**, which the rewrite deletes: it typed a holder
`human` for "the answers under the row [questions.md] marks 'A role is not an owner'".
Deleting the sentence without landing the elicitation would leave the shipped contract citing
a note that no longer exists.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|
| 01 | `038ddd2` | 7 findings, worst CRITICAL, no approve/does-not-approve word | 7 | `985d294` |
| 02 | `c00b2b7` | 6 findings, worst HIGH on both axes, no approve/does-not-approve word | 6 | `8868b9e` |
| 03 | `b8976c0` | 4 findings, worst HIGH, no approve/does-not-approve word | 4 | `1c6b4b1` |
| 04 | `74c86be` | 4 findings, worst HIGH, no approve/does-not-approve word | 4 | `063fb3e` |

## Open findings

**None.** Every finding raised on this branch is fixed.

## Rejected findings

None.

## Baselines

**CHANGED by this slice.** Stated here now; the merge commit and each round entry will
carry them too, because the next session inherits them:

| Command | Before (`555f8d2`) | After |
|---|---|---|
| `python3 scripts/validate.py .` | 0 errors, 8 warnings, exit 0 | 0 errors, **7 warnings**, exit 0 |
| `python3 scripts/validate.py demo` | 0 errors, 3 warnings | 0 errors, **2 warnings** |
| `python3 scripts/validate.py . --diff main` | exit 0 | exit 0 |
| `python3 -m unittest discover -s tests -q` | OK, 824 tests, skipped=1 | OK, 824 tests, skipped=1 |

The eighth engine warning and the third demo warning were the same finding — the demo
roster's passed `review_by`. It retired because the demo took a real confirming turn, not
because a cadence was chosen to clear it: the interview layer re-confirms all three holders
on a recent date, which moves the roster's snapshot forward, and a plain quarterly answer
applied to that snapshot lands in the future. There is no pytest; the suite is unittest.

## Maintainer items

**1. Three decisions taken at kickoff**, each put with options, a recommendation and its
counter-argument (rule 5), all three recommendations chosen:

- **The cadence question's shape** — three new rows in `questions.md` §7.
- **How far the demo goes** — the full route: a re-confirming layer 06, the roster edit,
  and the pending proposal the consent gate demands.
- **The engine's own roster** — one disclosure sentence, no date change.

**2. One refinement inside decision 1, made rather than asked, and flagged here.** The
approved preview placed the two typing rows immediately after the accountable-owner row,
where "that owner" would have scoped them to one of the six owner fields §7 names. They sit
after the appeal row instead, phrased "for each owner named above". The reason is a defect
this project has already measured once: round 11 of the roles-design review found R1's
first typing rule infeasible, and one of its two grounds was that the marker that rule read
"covers one owner row of five"
([spec-roles-accountable-unit.md](../spec-roles-accountable-unit.md), round 11, row 1). Ratifying the placement is the
maintainer's at merge.

**3. Follow-up owed, deliberately not done here.** `proposals/` is pending-only and an
applied proposal's file is removed once the change lands. Removing
`demo/proposals/org-map-re-confirmed.md` is legal only *after* the merge — a branch that
carries the roster change without the proposal fails the very gate that demanded it, and
`--diff main` run from `main` is an empty diff — so it is the maintainer's to do or to
defer. Until it is removed, the demo roster's gate is pre-licensed for further edits.

**4. C10 is implemented in shape, for the roster only, and stays open.** Run 1's
clarification C10 approved a direction for cadence answers against ISO-date fields: convert
at generation and record the derivation on the record. Read this session at
`persona-company/runs/2026-07-31/findings.md:263-267` — another repository, so no revision
of this one pins it. The link is not new here: round 17 of the roles-design review already
corrected the spec for citing the 90-day default as "the C10 pattern" when it had no
elicited cadence to derive from, and the spec has called it "C10's weaker cousin" ever since
([the design](../../specs/2026-08-28-roles-accountable-unit-design.md), the R1 landing-order
bullet). This slice is what gives it a cadence, so the roster's `review_by` now follows C10
properly. **C10 itself is scoped to `memory:review_by` and is not implemented** — that half
is untouched, deliberately: doing half of a finding filed against another field would leave
two cadence mechanisms in one document.

**5. Issue #39 is fixed on this branch and stays open until the merge lands.** A peer
session surfaced a stale
enumeration in `docs/known-limitations.md`: the pin-less-engine bullet named `skills/` and
`governance/constitution/` as the engine's ungoverned exemplars, when R1 made the roster a
third governed family — `_governed_class` returns `rule`, `roster`, `skill-md` and
`skill-other`, verified here against `scripts/validate.py` rather than taken on report. It
was folded in rather than deferred because this branch already edits both files the sentence
was wrong about, and because it is `known-limitations.md`, which no gate governs. Whether
that was the right call against rule 1's one-increment rule is the maintainer's at merge; the
alternative was shipping an enumeration this slice's own edits made staler. **The fix is at
`a131fe2`, which is on this branch and not on `main`** — so #39 is not closed by anything
here, and closing it before the merge would assert something the back-out flagged in the
sentence above can still falsify. It closes when `a131fe2` reaches `main`.

**6. One limitation added, not a check.** `docs/known-limitations.md` now records that
nothing validates the cadence-to-date conversion: the roster check reads the date and cannot
read the sentence beside it. The recorded derivation is there so a reader can check it.
