You are the BUILD half of a two-model loop on groundwork (~/Code-Brain/groundwork).
Read AGENTS.md and docs/agents/build-sessions.md first — the session rules bind, including
rule 9 (durable review verdicts). Rule 9's rejection grounds are a CLOSED LIST of three
categories; a finding no category fits is NOT rejected — it stays open and the maintainer
overrides at merge. Read the paragraph; do not work from a summary.

STATE. main is `2eeffef`, pushed and in sync with origin. Working tree clean. Only two
branches exist: main, and `prototype/interview-state-9` (one unmerged commit from 2026-07-20
behind decision 9 — leave it alone).

Landed 2026-08-30: issue #32, the append-only changelog guard narrowed to the ledger.
`_changelog_append_only` now protects the region from the BASE file's first entry line on;
the header above it is editable. Sixteen Codex rounds. **Issue #32 is CLOSED.**

GATE BASELINES on `2eeffef` — verify before you start. #32 changed the test count; do NOT
expect 846 or 871 from an older kickoff:
- `python3 scripts/validate.py .` -> 0 error(s), 7 warning(s), exit 0
- `python3 scripts/validate.py demo` -> 0 error(s), 2 warning(s)
- `python3 scripts/validate.py . --diff main` -> exit 0 (empty diff; for a real one use
  `--diff ea05b28`, also 0 errors)
- `python3 -m unittest discover -s tests -q` -> OK, 861 tests, skipped=1
There is no pytest; use unittest.

=============================================================================
START HERE: TWO PROCESS DECISIONS ARE PENDING. DO NOT SKIP TO #40.
=============================================================================

The #32 session ran SIXTEEN review rounds. The measurement that ended it, taken on `8202ab6`:

| | Lines | Commits touching it | Accepting-direction findings |
|---|---|---|---|
| Issue #32's actual fix — the base-anchored boundary | 66 | 1 (round 1) | **0 in 15 rounds** |
| A header-rendering guard added on top | 122 | 12 | **8** |

**The thing the issue asked for was correct in round 1 and was never breached.** Every
accepting-direction finding was in a second guard the issue never asked for, which the builder
began in round 2 without a rule 5 escalation and never revisited. The maintainer chose to delete
it. Full account: `docs/superpowers/reviews/issue-32-changelog-preamble/round-17.md`.

That entry proposes two rules for `docs/agents/build-sessions.md` and deliberately does NOT
write them there, because a workbench rule is the maintainer's to set. **Put both to the
maintainer under rule 5 — plain terms, options, recommendation, honest counter-argument —
BEFORE touching #40.** Proposed text:

> **10. A check the issue did not ask for is a rule 5 escalation before it is written.** A slice
> implements the issue's scope; a new check outside it — however well motivated — goes to the
> maintainer first, with what it defends against and what it would cost.

> **11. When a review round produces no findings in the class the slice is about, the slice goes
> to the maintainer for a merge decision** rather than continuing until a reviewer says
> "approve". Rule 9 already says the record must exist, not that every finding must close.

The honest counter-argument to 10, which you must state: it adds a round-trip to work that is
often genuinely necessary, and a builder who spots a real hole mid-slice now has to stop. The
counter to 11: a reviewer may find a real defect on round N+1 that round N missed, and stopping
early trades that away — #32's own rounds 8, 9 and 11 each found a Major after an earlier round
had looked clean in some respect.

Whatever is decided, the deciding session writes it into `docs/agents/build-sessions.md`, not you
unilaterally.

=============================================================================
THEN: ISSUE #40
=============================================================================

**#40 — deleting `groundwork.pin` or `interview/00-manifest.md` escapes the `--diff` base
contract when the base predates the marker.** Read the issue in full (`gh issue view 40`). It is
filed with its measurement and its reasoning; do not work from this summary.

**What is true, and re-confirm rather than trusting it.** `diff_base_findings` discovers a
governed root by its `groundwork.pin` and an interview state by its `00-manifest.md`, in the base
tree OR the working tree. Name a base from before the marker was committed AND delete it in the
same working change, and it is in neither: nothing is discovered, nothing checked, nothing said.

**Measured 2026-08-30 and already pinned by two tests** in `TestDiffBaseContract`:
`test_deleting_the_marker_under_a_pre_marker_base_says_nothing` (asserts the silence so it cannot
deepen unnoticed) and `test_deleting_the_marker_is_still_caught_when_the_base_holds_it` (the
control). The gap measured **identical on `main` at `ea05b28`** — it is standing, not introduced
by #31.

**The issue names three questions and they are the maintainer's, not yours.** Put all three under
rule 5 with a recommendation and the honest counter-argument, at the same time as the two process
rules above:

1. Is there a source of evidence beyond the two trees — e.g. whether any ancestor commit
   reachable from HEAD carried the marker? That is the one unexplored route, and it means walking
   `base..HEAD`, which no check currently does.
2. If a marker deletion becomes detectable, is it an ERROR, or the same WARN a governed-file
   deletion already gets (a proposal cannot name a target that no longer exists)?
3. Does the answer differ for the pin and for the manifest, as it did in #31?

**A fourth question the issue does not ask, and you should add it:** is declining and leaving the
documented limitation the right answer? #32 spent sixteen rounds building a defence against a
threat the issue had not raised, and the lesson is not "build less" but "decide the scope with
the maintainer first". Present declining as a real option with its cost.

**Do not reopen** `check_interview_state`'s doctrine that discovery is by content and a directory
with no manifest has no state. That is a locked decision. The issue says so.

**MIGRATIONS.md.** #31 established that `since:` demotion is for requirements on CONTENT SHAPE,
and that a tightening — content a permissive reader accepted that a stricter one now ERRORs — is
a v2 change with a migration note. Unlike #32, this slice would run that way: making a
previously-silent deletion detectable is a TIGHTENING. Verify that reading yourself and say so in
the record either way.

**Expect:** new tests, a `docs/rule-map.md` severity-cell amendment (any new top-level `check_*`
or `*_findings` function REQUIRES a row — that is how `test_every_shipped_check_is_mapped` is
scoped), a `docs/known-limitations.md` edit to whatever the fix does or does not close, and the
two existing pinning tests updated rather than deleted.

NOT THIS SESSION: #33 (C10), #35 (S6/C13), #30, #28, and C1–C13 generally.

=============================================================================
FAILURE MODES — the #32 session's MEASURED results, not general advice
=============================================================================

1. **Scope expansion is the expensive failure, not code quality.** 8 of 8 accepting-direction
   findings were in 122 lines nobody asked for. The 66 lines the issue asked for were never
   breached. If you find yourself building a second mechanism, stop and escalate.
2. **Every repair's self-description overreached.** Most rounds found the previous round's prose
   ahead of its code — including a sentence written specifically to stop overclaiming, and a
   paragraph replacing a stale tally that was itself three overclaims. **Write what the code
   does; never write what it guarantees.**
3. **Withdraw a count, do not correct it.** Eight counts were corrected and every one was wrong
   again or wrong in the direction of making the work sound larger. Positional references —
   "the last seven" — go stale exactly as counts do. Name the cases and let the reader count.
4. **A mutation row must name the LITERAL edit run.** Mislabelled twice; both times the label
   described a bigger mutation than the one performed, and a later round measured the difference.
5. **Run mutations at BOTH edges of every rule.** Three coverage gaps were found in the
   OVER-refusing direction — a rule silently narrowing what an adopter may write. A stricter
   mutation surviving is as much a gap as a looser one, and only the looser direction is
   intuitive to check.
6. **A check can pass for the wrong reason.** `["1. ```"]` was refused by rule 3 (its last line
   was not blank), not by the fence rule the test named. Construct each case so only the rule
   under test can fire.
7. **Measure the thing you are claiming.** A U+00A0 probe was written with an ordinary space and
   looked like a false alarm. Re-run with the real character it reproduced exactly.
8. **A test's provenance is a factual claim.** A comment said each of six cases survived a
   recorded regression; five had.
9. **A correction removes the wrong statement, it does not merely add the right one.** A README
   kept a wrong mutation row standing beside its correction for two rounds.
10. **Codex review briefs must not be worded adversarially.** Rounds 03 and 10 were both killed
    by a provider content filter — "produce an input that hides the ledger" reads as an attack
    request. Rounds 04–16 all completed by asking the SAME question as classifier correctness
    ("which inputs does this classify wrongly, in either direction") or as a completeness audit
    ("enumerate the block types; for each say which rule governs it and whether that is
    correct"). The completeness-audit framing produced the single most valuable round.
11. **Editing a large test file by slicing between anchors ate the module fixtures twice.**
    `tests/test_validate.py` has two `PIN_OK` definitions; a naive "cut to the next `class`"
    removes `CHANGELOG_OK` and friends. Check `python3 -c "import tests.test_validate"` after any
    block edit.

=============================================================================
HOW TO WORK
=============================================================================
- Branch before editing; never commit to main; use a git worktree
  (`~/Code-Brain/groundwork-wt-issue-40`), and remove it after the merge.
- Rule 9 from round 1. Record goes in `docs/superpowers/reviews/<branch-slug>/` unless this
  branch's own commits add or change exactly one plan. One file per entry, `round-NN.md` from 01,
  immutable once committed. A numbered entry may be a maintainer-decision record rather than a
  review round; it says so on its first line. Record the reviewed revision as a commit SHA, the
  verdict, and every finding with the reviewer's own severity word verbatim plus its disposition.
  A correction to an earlier entry goes in a later one. The README carries the fix-commit map,
  the open findings and the rejected findings. Do NOT pre-fill a pending round's reviewed SHA.
- Codex review via the `codex:codex-rescue` agent with `--background`. **The subagent returns as
  soon as it launches the job — that is not the review finishing.** Poll the job JSON at
  `~/.claude/plugins/data/codex-inline/state/<dir-hash>/jobs/<task-id>.json`, where the dir-hash
  is keyed by the LAUNCH cwd (the worktree). `result` is a DICT; read `result.rawOutput`. Status
  passes through `queued` before `running`. #32's rounds took 4–8 minutes each.
- Review threads are NOT resumable. After committing fixes, launch a fresh review.
- Tell Codex every round: point it at the PREVIOUS round's repairs first; name the failure shapes
  above; a clean round is a real outcome and it must not manufacture findings; it must not
  re-raise anything the record already discloses (list those explicitly, and the list grows each
  round); and its sandbox often cannot create temp directories, so hundreds of
  `TemporaryDirectory` errors from `unittest` are environmental — verify the suite yourself and
  say so in the round entry.
- End green on all four commands above, and state any changed baseline explicitly in both the
  merge commit and the review record. The maintainer lands the merge unless they instruct
  otherwise; if they do, record that in the merge commit.

AFTER #40: the interview-surface issues (#33, #35, #34, #37, #36) are a coherent cluster and
#38 depends on them settling. #30 and #28 are validator-behaviour slices in the same family as
#31 and #40.
