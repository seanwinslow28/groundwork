You are the BUILD half of a two-model loop on groundwork (~/Code-Brain/groundwork).
Read AGENTS.md and docs/agents/build-sessions.md first — the session rules bind, including
rule 9 (durable review verdicts), which this session must follow from its first Codex round.
Rule 9's rejection grounds are a CLOSED LIST of three categories; a finding no category fits
is NOT rejected — it stays open and the maintainer overrides at merge. Read the paragraph;
do not work from a summary.

STATE. main is d42e9ae, pushed and in sync with origin. R2a landed on 2026-08-29: nine
commits, six Codex rounds, terminal round approving with zero findings, every finding fixed,
none open and none rejected. It carried the rest of the generate.md hole-(b) contract
amendment and S2's open items 2 and 5. R2 was split by the maintainer at that session's
kickoff; this session is the other half.

GATE BASELINES on d42e9ae — verify before you start. This session is EXPECTED to change two
of them:
- `python3 scripts/validate.py .` -> 0 error(s), 8 warning(s), exit 0
- `python3 scripts/validate.py demo` -> 0 error(s), 3 warning(s)
- `python3 scripts/validate.py . --diff main` -> exit 0
- `python3 -m unittest discover -s tests -q` -> OK, 824 tests, skipped=1
There is no pytest; use unittest.

The eighth engine warning and the third demo warning are the SAME finding — the demo
roster's passed `review_by`. If the demo gets a real elicited cadence this session, the new
baselines are 7 engine warnings and 2 demo warnings, and you must say so explicitly in the
merge commit and in the review record, because the next session inherits them. Read the
complication about this below before assuming it follows automatically.

READ BEFORE WRITING ANYTHING:
- docs/superpowers/specs/2026-08-28-roles-accountable-unit-design.md — decisions 1, 3 and 4,
  the "The prose rewrite" section, and the Landing order R2 bullet. LOCKED means locked.
- docs/superpowers/reviews/r2a-generate-contract-and-gate-docs/ — the whole record.
  round-03.md is the one to read closely: a repair that removed a false completeness claim
  overcorrected into drift from a locked decision. round-05.md settles the citation
  convention this record should reuse.
- docs/superpowers/plans/r1-roster-schema-v2-reviews/round-12.md — the three maintainer
  decisions, including 5c.

THIS SESSION'S SCOPE — R2b, the second half of R2. Two parts, and they are ONE UNIT.

1. **The person-versus-role prose rewrite.** Three sites state the contradiction explicitly.
   Line numbers VERIFIED on d42e9ae — three of the four moved under R2a's edits, so do not
   reuse any older list:
   - `interview/questions.md:93` — "A role is not an owner"
   - `interview/protocol.md:248` — "an owner who is a **person**, not a role"
   - `interview/README.md:156` — "a person, not a role?"
   All three become *an owner is a role or a named holder, and the roster resolves it* — the
   additive form decision 1 requires, under which person owners and holder-only rows stay
   valid. **Scope from a fresh grep, not from this list.** A fresh grep also surfaces
   `interview/questions.md:105`, `interview/generate.md:170` and `:172`, and `README.md:22`
   and `:102` — judge each; none of those states that a role is invalid.

2. **Full roster elicitation:** typed holders asked for directly, and a review cadence for the
   org map, rather than derived from the human-only markers. R1's roster `review_by` is a
   stated interim policy default of 90 days; this replaces it with an elicited answer.

**WHY THEY ARE ONE UNIT — the coupling R2a found.** `interview/generate.md:170-172` builds
R1's holder-typing rule directly on the sentence at `questions.md:93`: it says to type a
holder `human` only for "the answers under the row [questions.md] marks 'A role is not an
owner'". Delete that sentence without landing the elicitation and the shipped contract cites
a note that no longer exists. Do not separate them.

TWO COMPLICATIONS, VERIFIED IN CODE DURING R2a — do not re-derive, but do re-confirm:

a) **Eliciting a cadence does NOT automatically retire the demo WARN.** The demo roster's
   `valid_at` is 2026-05-11. If `review_by` stays derived as `valid_at + cadence`, a
   three-month elicited cadence yields 2026-08-11 — still passed, WARN unchanged. Only a
   cadence of roughly four months or more clears it against the current date. So "give the
   demo an elicited cadence" and "retire the WARN" are two decisions and the first
   constrains the second. The alternative is deriving `review_by` from the confirming
   layer's date rather than from `valid_at`, which is a roster-schema semantics change and
   its own decision. **Put this to the maintainer with options, a recommendation and the
   counter-argument (rule 5) rather than picking a cadence that happens to clear the WARN.**

b) **The demo can take a new interview layer legally.** `interview_diff_findings` freezes
   only files matching `(0[1-9]|[1-9][0-9])-[a-z0-9]+(?:-[a-z0-9]+)*\.md`, so
   `00-manifest.md` is editable and a new `06-*.md` layer is the sanctioned
   append-and-supersede route for eliciting the cadence without editing a frozen layer.
   `check_interview_state` requires the manifest's `layers:` list and the directory to agree
   in BOTH directions, so the layer and its manifest entry land together. Note the demo
   manifest is `status: in-progress` with a `_working.md`; confirm adding a layer does not
   trip the half-committed-turn ERROR.

MAINTAINER INPUT REQUIRED (rule 5 — explain before deciding, every time):
- The cadence question's wording, and what the demo answers, per complication (a).
- Whether the ENGINE's own roster gets an elicited cadence or stays on the maintainer's
  statement. Nothing forces it: `governance/roles.md` carries `review_by: 2026-11-27`, still
  in the future.

NOT THIS SESSION:
- **Issue #31** — the `--diff` base contract (decision 5c). `_git_diff_context` checks only
  that the ref resolves. Its own slice; it changes what the gate promises.
- **Issue #32** — the append-only changelog guard protecting the preamble, making a stale
  header uncorrectable. Its own slice; it has a security-shaped counter-argument.
- **C1-C13**, with C13 held for the S6 decision.
- Rule 9 saying out loud that review entries are themselves reviewed surface. The maintainer
  was given the options and the counter-argument on 2026-08-29 and chose to leave rule 9
  silent. Do not reopen without new evidence.

FAILURE MODES — these are R2a's measured results, not general advice:
- **Every fix is where the next defect lands.** R2a rounds 2 and 3 each found their worst
  defect inside the previous round's fix. Point every round at the last round's repairs.
- **The review record is itself reviewable surface.** In R2a, round 1 found the only defect
  in the product edits; EVERY finding from round 2 onward was in the record's own prose,
  and rounds 4 and 5 changed no product file at all. Write entries with no generalisation
  you have not recomputed.
- **Removing a false completeness claim can overcorrect into drift from a locked decision.**
  R2a round 3: fixing "this list names everything" weakened generate.md into licensing an
  incomplete generation report, which locked decision 6 forbids. A document's illustrative
  list of kinds and a run's exhaustive obligation are different objects; say both.
- **Withdraw a count rather than correct it.** R2a round 5: a corrected number is a number
  the next entry must re-audit. Prefer no count.
- **A convention whose own introducing entry breaks it is drawn too wide.** R2a rounds 4 and
  5. Narrow it on that evidence rather than resolving to try harder.
- **Claiming completeness is the error, not the missed case.** If a check or claim cannot be
  complete, say so in docs/known-limitations.md in the words the secrets floor uses —
  "high-signal, not exhaustive".
- **A grammar whose own documented example fails is not a grammar.** Anything you specify
  gets a test that extracts and parses the documented example.
- **When changing a test's assertion, assert behaviour AND the class of error**, never one
  exact message and never a bare `any(ERROR)`.
- **docs/rule-map.md rows use a restricted grammar.** `_canonical_row` rejects code spans, so
  a backticked cell silently drops the row and fails `test_every_shipped_check_is_mapped`.
  This cost R2a a test failure. No backticks in that table.
- Re-verify every quoted line number against the source file, not against a review's
  citation. Diff every deletion and account for it. If a fix touches a maintainer decision,
  stop and ask.

HOW TO WORK:
- Branch before editing; never commit to main; use a git worktree
  (`~/Code-Brain/groundwork-wt-r2b`), and remove it after the merge.
- Rule 9 from round 1. If this branch's own commits add or change exactly one plan, the
  record goes in `docs/superpowers/plans/<slice>-reviews/`; otherwise
  `docs/superpowers/reviews/<branch-slug>/`. One file per entry, `round-NN.md` from 01,
  immutable once committed. Record the reviewed revision as a commit SHA, the verdict, and
  every finding with the reviewer's own severity word verbatim plus its disposition. A
  correction to an earlier entry goes in a later one. The README carries the fix-commit map,
  the open findings and the rejected findings. Do NOT pre-fill a pending round's reviewed
  SHA — R2a's round 2 found that defect.
- Reuse R2a's settled citation convention (its round-05.md): a citation offered as evidence
  for a claim about where something is carries the revision it holds at; a citation quoting
  a previously defective citation as the subject of discussion does not; a forward reference
  to the round's own fix commit resolves through the README's rounds table.
- Codex review via the `codex:codex-rescue` agent with `--background`. **The subagent returns
  as soon as it launches the job — that is not the review finishing.** Poll the job JSON at
  `~/.claude/plugins/data/codex-inline/state/<dir-hash>/jobs/<task-id>.json`, where the
  dir-hash is keyed by the LAUNCH cwd (the worktree, not the main repo). Run the watcher as a
  `run_in_background` Bash call; a foreground wrapper is killed at the harness timeout while
  the job still reports "running". R2a's rounds took 3-9 minutes.
- Review threads are NOT resumable. After committing fixes, launch a fresh review.
- Tell Codex every round: a clean round is a real outcome and it must not manufacture
  findings; it must not re-raise anything the record already discloses (list those
  explicitly); and its sandbox usually cannot create temp directories, so hundreds of
  `TemporaryDirectory` errors from `unittest` are environmental — verify the suite yourself
  and say so in the round entry.
- End green on all four commands above, and state any changed baseline explicitly in both
  the merge commit and the review record. The maintainer lands the merge unless they
  instruct otherwise; if they do, record that in the merge commit.

AFTER R2b, in order: issue #31 (the --diff base contract), then issue #32 (the append-only
preamble). Both are filed with their evidence and counter-arguments; neither should be
started in the same session as R2b.
