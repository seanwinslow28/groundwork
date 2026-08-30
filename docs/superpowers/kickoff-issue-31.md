You are the BUILD half of a two-model loop on groundwork (~/Code-Brain/groundwork).
Read AGENTS.md and docs/agents/build-sessions.md first — the session rules bind, including
rule 9 (durable review verdicts), which this session must follow from its first Codex round.
Rule 9's rejection grounds are a CLOSED LIST of three categories; a finding no category fits
is NOT rejected — it stays open and the maintainer overrides at merge. Read the paragraph;
do not work from a summary.

STATE. main is 06dd094, pushed and in sync with origin. R2b landed on 2026-08-29: 20 commits,
seven Codex rounds, terminal round approving with zero findings, 28 findings all fixed, none
open and none rejected. Its record is docs/superpowers/reviews/r2b-person-role-and-roster-elicitation/.
The R2b worktree is removed and its branch deleted.

GATE BASELINES on 06dd094 — verify before you start. R2b changed the first two; do NOT
expect the old 8/3 numbers from any older kickoff:
- `python3 scripts/validate.py .` -> 0 error(s), 7 warning(s), exit 0
- `python3 scripts/validate.py demo` -> 0 error(s), 2 warning(s)
- `python3 scripts/validate.py . --diff main` -> exit 0 (an empty diff from main; to test the
  gate for real, diff against a pre-merge base such as 555f8d2, which is also 0 errors)
- `python3 -m unittest discover -s tests -q` -> OK, 824 tests, skipped=1
There is no pytest; use unittest.

=============================================================================
PART A — TWO RATIFICATIONS THE MAINTAINER OWES, BEFORE ANY BUILD WORK
=============================================================================

R2b merged with two items recorded as awaiting the maintainer's ratification rather than
assumed. Both are already ON MAIN. Ratifying costs nothing; backing either out is a small
follow-up commit. Put each to the maintainer under rule 5 — plain terms, the options, a
recommendation, the honest counter-argument — and do it BEFORE starting issue #31, because
one of them may generate work.

They are items 2 and 6 under "Maintainer items" in
docs/superpowers/reviews/r2b-person-role-and-roster-elicitation/README.md. Read that file;
do not work from this summary alone.

**Ratification 1 — the roster typing rows' placement in interview/questions.md §7.**
The maintainer approved a preview that put the two typing rows immediately after the
accountable-owner row. They were landed after the APPEAL row instead, phrased "for each owner
named above", because "that owner" in the approved position would have scoped typing to one of
the six owner fields §7 names — the defect round 11 of the roles-design review found in R1's
first typing rule (docs/superpowers/reviews/spec-roles-accountable-unit.md, round 11, row 1).
The change was made rather than asked and flagged in the record. Options: ratify as landed;
or move them back to the approved position and accept the narrower scope. Verify the claim
about scoping yourself against the current §7 before recommending.

**Ratification 2 — folding issue #39's fix into R2b against rule 1 (one increment per
session).** #39 is a stale enumeration in docs/known-limitations.md: the pin-less-engine
bullet named skills/ and governance/constitution/ as the engine's ungoverned exemplars when
_governed_class returns rule, roster, skill-md and skill-other — the roster has been a third
governed family since v2. It was surfaced by a peer session and folded in at a131fe2, on the
grounds that R2b already edited both files the sentence was wrong about. Options: ratify the
fold-in; or revert it and let #39 be its own slice. **#39 is still OPEN and its fix is now on
main, which was the stated condition for closing it** — so if the maintainer ratifies, close
#39 with `gh issue close 39` and a comment naming 06dd094.

**Also surface, not a ratification:** demo/proposals/org-map-re-confirmed.md is still pending
beside the change it licenses. proposals/ is pending-only by convention and removing it only
became legal with the merge. Until it is removed the demo roster's gate is pre-licensed for
further edits. Ask whether to remove it now or keep it as a second worked proposal in the
demo. This is a demo-content change, so check whether removing it needs its own consent-gate
handling before recommending — the roster proposal exists BECAUSE the roster is governed.

=============================================================================
PART B — THIS SESSION'S SCOPE: ISSUE #31
=============================================================================

**Issue #31 — the `--diff` base contract is unenforced.** Read the issue in full
(`gh issue view 31`), and decision 5c in
docs/superpowers/plans/r1-roster-schema-v2-reviews/round-12.md, which is where the maintainer
decided this becomes its own slice. Related: #28, whose "alternatively, teach the tripwire..."
suggestion is this issue.

**What is true today, verified on 06dd094.** `_git_diff_context` at scripts/validate.py:3697
does exactly two checks on the base: `git rev-parse --verify --quiet <base>^{commit}` (the ref
resolves) and `git ls-tree -r --name-only -z <base>` (the tree lists). It does NOT check that
the base is an ancestor of HEAD, and it does NOT check that the base holds the governed root.
Re-confirm this rather than trusting the sentence.

**Two guarantees rest on a base nothing verifies, and they fail in OPPOSITE directions.**
This asymmetry is the heart of the slice:
- **The #18 consent gate fails LOUD.** A base predating the generated root returns every
  generated rule, skill and roster as an escalating change with no pending proposal — measured
  on the 2026-07-31 persona-company run (#28): 2 errors on a two-rule repo from a
  pre-generation base, 0 from the generation commit. Over-gating, in the safe direction.
- **The frozen-layer guard fails SILENT.** `interview_diff_findings` derives its state
  directories from the BASE file list, so a confirmed layer is protected only where the base
  holds both the layer and its 00-manifest.md. A base predating the interview protects
  nothing and reports nothing.

**The three questions the issue poses, and they are the maintainer's, not yours:**
1. Should the gate verify the base contains the governed root, that it is an ancestor of HEAD,
   or neither?
2. At what severity — ERROR (refuse a diff whose base cannot support the promise) or WARN
   (run, but say the run is not covering what the reader thinks)?
3. Does the frozen-layer case want a DIFFERENT answer from the consent-gate case, given they
   fail in opposite directions?

Put all three under rule 5 with a recommendation and the counter-argument. The recorded
counter-argument for enforcement is already on file: the present over-gating wall is an
adopter's first experience of the gate at the documented "prove it" step, and it looks like 13
violations rather than a wrong flag.

**This changes what the gate PROMISES.** It is the first slice in a while that touches
scripts/validate.py. Expect: new tests, a docs/rule-map.md row per new check, a
docs/known-limitations.md entry for whatever the check cannot do, and a MIGRATIONS.md
consideration if any new finding needs a `since:` tag — R1 spent the v1->v2 bump on the
roster, so read MIGRATIONS.md before assuming a new ERROR can simply be added.

**Already done and NOT part of this slice:** the documentation half. interview/generate.md
names the generation commit as the base and carries the measurement (S2). README.md and
delivery/README.md were corrected in R2a (d42e9ae), along with the three sites that stated the
frozen-layer guarantee without its manifest condition. #31 is only the enforcement question.

NOT THIS SESSION:
- **Issue #32** — the append-only changelog guard protecting the preamble. Its own slice; it
  has a security-shaped counter-argument. Start it only after #31 has merged.
- **Issue #33 (C10)** for memory:review_by. R2b implemented C10's shape for the ROSTER only
  and deliberately left C10 open; do not do the other half opportunistically.
- **C1-C13** generally, with C13 held for the S6 decision (#35).

=============================================================================
FAILURE MODES — R2b's MEASURED RESULTS, not general advice
=============================================================================

R2b ran seven rounds. Round 1 found the only defect in the original product edits; EVERY round
after it found its worst defect inside the PREVIOUS round's fix. Three shapes accounted for
nearly all of it. Point every round at the last round's repairs.

1. **A repair reaches for a stronger claim than the one it replaced.** Measured five times:
   "every field", "nothing in the repository", "either cell empty is an ERROR", "the one way",
   "stops a high-risk rule shipping at all". Each was written to fix a real overclaim and each
   was itself false. **The replacement for an overclaim is a NARROWER true statement, not a
   broader one.** Superlatives ("the one way", "nothing", "every") are the cheapest overclaim
   available.
2. **The record describes the fix that was INTENDED, not the one that LANDED.** Five of seven
   rounds carried one. The countermeasure is mechanical: re-read the changed lines before
   writing the entry.
3. **A locked form restated in your own words gets narrower every time.** Decision 1's "a role
   or a named holder" was narrowed three times — by paraphrase, by a site the slice authored
   itself, and by two extra words inside a correction — before it was quoted rather than
   restated. **Quote locked wording; do not paraphrase it.**

Also measured in R2b:
- **A fix that touches a maintainer decision must stop and ask.** Round 5 found that round 4's
  fix had collapsed two gap states locked decision 5 keeps separate — drift from a locked
  decision, produced while quoting the decision that separates them. Three routes went to the
  maintainer; the chosen one amended nothing.
- **Withdraw a count rather than correct it — and a prose classification that enumerates is a
  count wearing different clothes.** Round 1 wrote a wrong number, round 2 replaced it with a
  classification, round 3 found the classification incomplete. What worked was naming a
  `git log` range a reader can run.
- **A grep-scoped sweep must be re-run after each round**, because a slice can author a new
  site while repairing the old ones. R2b did exactly that.
- **Measure, do not reason, when a validator behaviour is in question.** A reviewer said a bad
  Type cell "produces an ERROR"; running it produced eight, because the mistyped row drops the
  holder out of resolution entirely. The difference changed the severity of the finding.
- **docs/rule-map.md rows use a restricted grammar.** `_canonical_row` rejects code spans, so a
  backticked cell silently drops the row and fails `test_every_shipped_check_is_mapped`. No
  backticks in that table. The same restricted-grammar rule applies to interview/questions.md.
- **A roster body may contain NO backtick at all.** R2b tripped this and took the whole table
  down with it: 13 ERRORs from one code span.
- **When changing a test's assertion, assert behaviour AND the class of error**, never one
  exact message and never a bare `any(ERROR)`. Prove a new assertion bites by breaking the
  thing it guards and watching it fail.
- Re-verify every quoted line number against the source file, not against a review's citation.
  Diff every deletion and account for it.

=============================================================================
HOW TO WORK
=============================================================================
- Branch before editing; never commit to main; use a git worktree
  (`~/Code-Brain/groundwork-wt-issue-31`), and remove it after the merge.
- Rule 9 from round 1. If this branch's own commits add or change exactly one plan, the record
  goes in `docs/superpowers/plans/<slice>-reviews/`; otherwise
  `docs/superpowers/reviews/<branch-slug>/`. One file per entry, `round-NN.md` from 01,
  immutable once committed. Record the reviewed revision as a commit SHA, the verdict, and
  every finding with the reviewer's own severity word verbatim plus its disposition. A
  correction to an earlier entry goes in a later one. The README carries the fix-commit map,
  the open findings and the rejected findings. Do NOT pre-fill a pending round's reviewed SHA.
- Citation convention, settled in R2a round-05.md and used throughout R2b: a citation offered
  as evidence for a claim about where something is carries the revision it holds at; a citation
  quoting a previously defective citation as the subject of discussion does not; a forward
  reference to the round's own fix commit resolves through the README's rounds table.
- Codex review via the `codex:codex-rescue` agent with `--background`. **The subagent returns as
  soon as it launches the job — that is not the review finishing.** Poll the job JSON at
  `~/.claude/plugins/data/codex-inline/state/<dir-hash>/jobs/<task-id>.json`, where the
  dir-hash is keyed by the LAUNCH cwd (the worktree, not the main repo). The `result` field is
  a DICT; read `result.rawOutput`, not `result` as a string. Run the watcher as a
  `run_in_background` Bash call. R2b's rounds took 4-9 minutes.
- Review threads are NOT resumable. After committing fixes, launch a fresh review.
- Tell Codex every round: a clean round is a real outcome and it must not manufacture findings;
  it must not re-raise anything the record already discloses (list those explicitly); and its
  sandbox usually cannot create temp directories, so hundreds of `TemporaryDirectory` errors
  from `unittest` are environmental — verify the suite yourself and say so in the round entry.
- End green on all four commands above, and state any changed baseline explicitly in both the
  merge commit and the review record. The maintainer lands the merge unless they instruct
  otherwise; if they do, record that in the merge commit.

AFTER #31: issue #32 (the append-only changelog preamble). It is filed with its evidence and
its security-shaped counter-argument, and should not share a session with #31.
