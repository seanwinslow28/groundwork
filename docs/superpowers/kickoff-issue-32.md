You are the BUILD half of a two-model loop on groundwork (~/Code-Brain/groundwork).
Read AGENTS.md and docs/agents/build-sessions.md first — the session rules bind, including
rule 9 (durable review verdicts), which this session must follow from its first Codex round.
Rule 9's rejection grounds are a CLOSED LIST of three categories; a finding no category fits
is NOT rejected — it stays open and the maintainer overrides at merge. Read the paragraph;
do not work from a summary.

STATE. main is 108c600, pushed and in sync with origin. Working tree clean. Only two
branches exist anywhere: main, and prototype/interview-state-9 (one unmerged commit from
2026-07-20 holding the Shape A vs Shape B prototype behind decision 9 — leave it alone).

Landed on 2026-08-30, in this order:
- `a7a80ea` — retired demo/proposals/org-map-re-confirmed.md, an APPLIED proposal still
  marked pending, plus the four sites that counted or linked it. Three Codex rounds,
  five findings, terminal round approving with zero. The demo now carries ONE pending
  proposal, against a rule; there is no live roster-targeted example in it.
- `f0a7358` — issue #31, the --diff base contract. Eight Codex rounds, twenty findings,
  nineteen fixed, ONE OPEN, none rejected. Merged over the open one with the grounds in the
  merge commit.
- `108c600` — .gitignore gains .DS_Store. One line, no Codex round, and the branch commit
  records why none ran.

Issues #39 and #31 are CLOSED. Issue #40 is OPEN and was filed by that session — the open
Major #31 shipped with. It is NOT this session's work.

GATE BASELINES on 108c600 — verify before you start. #31 changed the test count; do NOT
expect 824 from any older kickoff:
- `python3 scripts/validate.py .` -> 0 error(s), 7 warning(s), exit 0
- `python3 scripts/validate.py demo` -> 0 error(s), 2 warning(s)
- `python3 scripts/validate.py . --diff main` -> exit 0 (an empty diff from main; to test the
  gate for real, diff against a pre-merge base such as ea05b28, which is also 0 errors)
- `python3 -m unittest discover -s tests -q` -> OK, 846 tests, skipped=1
There is no pytest; use unittest.

NEW SINCE THE LAST KICKOFF, and it changes how you test: `--diff` now enforces a base
contract. `diff_base_findings` ERRORs when the base tree holds no `groundwork.pin` for a
governed root or no `00-manifest.md` for an interview state, and WARNs when the base is not
an ancestor of HEAD. If you name an old base out of habit you will now get contract ERRORs
that are correct rather than a wall of escalating-change ERRORs that were not.

=============================================================================
NO RATIFICATIONS ARE OWED. START HERE.
=============================================================================

The previous session's three maintainer items were all put under rule 5 and decided, and
its own findings are all recorded. Nothing is pending your review before you begin. If you
find something that looks like an unratified decision, check
`docs/superpowers/reviews/issue-31-diff-base-contract/README.md` and
`docs/superpowers/reviews/retire-applied-demo-proposal/README.md` before raising it.

=============================================================================
THIS SESSION'S SCOPE: ISSUE #32
=============================================================================

**Issue #32 — the append-only changelog guard protects the preamble too, making a stale
header uncorrectable.** Read the issue in full AND its one comment (`gh issue view 32
--comments`). It is filed with its evidence and its counter-argument; do not work from this
summary alone.

**What is true today, verified on 108c600.** Re-confirm rather than trusting these:

- `_changelog_append_only` (scripts/validate.py:3598) is PURE and whole-file: "every line
  committed at base must survive, in order, as the head of the new file." Preamble included.
- Its only caller is `blast_radius_diff_findings` (scripts/validate.py:4360), which raises
  the ERROR under `--diff`. #17 requires that ERROR; the SCOPE is what is in question.
- The stateless check's notion of an entry line is `s.startswith("- ")`
  (scripts/validate.py:3315). `_changelog_appended_targets` uses the same test at 4157.
- `demo/governance/changelog.md`'s preamble enumerates "rules, Owner's Cards, descriptions,
  governance frontmatter, any track-2 skill" and omits the roster, which became the third
  governed family at v2. That sentence is the demonstration, and it cannot be corrected.

**A FACT THE ISSUE DOES NOT CARRY, measured on 108c600.** Run it yourself:

    python3 -c "
    import pathlib
    for p in ['governance/changelog.md','demo/governance/changelog.md']:
        lines = pathlib.Path(p).read_text().split('\n')
        print(p, len(lines), 'lines,',
              len([l for l in lines if l.strip().startswith('- ')]), 'entry lines')"

**Both changelogs have ZERO entry lines.** Under the issue's proposed narrow fix — "the
contiguous block before the first entry line is editable, from the first entry on the file
is append-only exactly as today" — an entry-less changelog is editable in its ENTIRETY.
That is the state every shipped changelog is in right now, and every freshly generated
company repo will be in. The proposal as written therefore grants, on day one, exactly the
freedom the security counter-argument is about. It may still be the right answer — there
are no entries to launder — but it has to be DECIDED, not discovered in round 4.

**A second site the fix would falsify.** `governance/changelog.md` (the engine's own) says
in its preamble: "This file is **never edited or reordered — only appended**". Narrowing the
guard makes that sentence false about its own file. `demo/governance/changelog.md` says
"Append-only." Both are prose your change would have to correct — and the engine's is
itself inside the region the narrowed guard would make editable, which is a pleasing
demonstration and also a thing to say out loud rather than let a reviewer find.

**The two test surfaces are not equivalent, and the issue comment says why.** The engine
root carries NO `groundwork.pin` (`ls groundwork.pin` -> no such file); only
`demo/groundwork.pin` exists. So the tripwire — and therefore `_changelog_append_only` —
runs against `demo/` and not against the engine's own `governance/`. Demonstrating the fix
against `demo/` is the faithful test and costs a pending proposal in `demo/proposals/` for
any governed demo file you touch alongside, plus the obligation to remove that proposal
after merge. Demonstrating it against the engine costs nothing and proves less.

**The questions, and they are the maintainer's, not yours:**
1. Narrow the guard at all, or decline and document the limitation in
   `docs/known-limitations.md`? The issue's own scope note says declining is a real option.
2. If narrowing: is the editable region the contiguous block before the first entry line, or
   something else? State what an entry is BYTE FOR BYTE, and whether an existing entry can be
   converted into non-entry text by editing its leading characters — that is the laundering
   route the counter-argument names.
3. What happens when a changelog has NO entry lines, which is the state of both today? Is the
   whole file editable, is there a floor, or does the narrowing only engage once a first
   entry exists?

Put all three under rule 5 with a recommendation and the honest counter-argument. The
counter-argument is already on file and it is the serious one: **loosening an append-only
guard is exactly how a laundering route gets created.**

**MIGRATIONS.md, so you do not burn a round on it.** #31 established that the `since:`
demotion is for requirements on CONTENT SHAPE, and that a tightening — content a permissive
reader once accepted that a stricter one now ERRORs — is a v2 change with a migration note.
This slice runs the OTHER way: it would make the gate accept content it currently rejects.
Loosening does not break the pull promise and does not want a bump. Verify that reading
against MIGRATIONS.md yourself before relying on it, and say so in the record either way.

**Expect:** new tests, a `docs/rule-map.md` row or an amended severity cell (the guard's
ERROR lives on the `blast_radius_diff_findings` row, not `check_changelog`'s — read the
"Corrections the hand audit made" section, which says so explicitly), a
`docs/known-limitations.md` entry for whatever the narrowed guard cannot do, and the two
preamble corrections above.

NOT THIS SESSION:
- **Issue #40** — marker deletion under a pre-marker base. Filed 2026-08-30, open by
  decision, with its measurement and two tests already pinning it. Its own slice.
- **Issue #33 (C10)** for `memory:review_by`. R2b implemented C10's shape for the ROSTER only
  and deliberately left C10 open.
- **C1-C13** generally, with C13 held for the S6 decision (#35).
- The `memory_diff_findings` base-derived gap named in `docs/known-limitations.md`.

=============================================================================
FAILURE MODES — the #31 session's MEASURED results, not general advice
=============================================================================

Eight rounds. Round 1 found the only two behaviour defects, both in the code shipped before
any review saw it, and BOTH FAILED OPEN. Rounds 2 through 7 then each found their worst
defect inside the PREVIOUS round's fix — every single round. Point every round at the last
round's repairs, explicitly, in the review prompt.

1. **A repair reaches past what it can support.** NINE instances. The vehicle was almost
   always a count or a superlative: "accepts any escalating change", "the one place", "two
   places", "three", "always where folding makes the check stricter", "every finding in the
   run", "no check here can close it". Each replaced a real overclaim and each was itself
   wrong. **The replacement for an overclaim must be checked as carefully as the overclaim
   was** — rounds 6 and 7 each found the previous round's REPLACEMENT text inexact.
2. **Withdraw a count rather than correct it.** Corrected three times, wrong three times.
   What worked was naming the sites without numbering them, or naming a command the reader
   can run. A count survives only if the text names the setup that produces it — two were
   kept on exactly that basis and round 8 cleared them.
3. **A grep-scoped sweep must be re-run after each round, across every mutable file the
   branch touches — not the sites the round named.** Rounds 5, 6 and 7 each found a repair
   applied to some of its sites and not all: a claim narrowed in the README and not in
   known-limitations, then narrowed in three places and not in a test docstring. Round 7 ran
   the sweep wide and round 8 approved.
4. **A citation carries the revision it holds at.** Round 7 said round 6 "cited 4232 when it
   is 4233"; round 8 observed both were right at their own revision and each round's edit had
   moved the line. The number was undated, not wrong. R2a's round-05 convention exists for
   this.
5. **Measure, do not reason, when validator behaviour is in question.** Two examples worth
   knowing. A finding claimed to be a regression was measured identical on main — that
   changed its disposition. And a fold-collision bug could not be reproduced on this
   filesystem at all: macOS folds `A/` into `a/` AND `ß/` into `ss/`, so two roots that
   `_fold` collides cannot both exist on disk. The base tree was built with git plumbing
   instead (`hash-object -w`, `update-index --add --cacheinfo` against a throwaway
   `GIT_INDEX_FILE`, `write-tree`, `commit-tree`), which holds `a/` at base while the working
   tree holds `A/`. That technique is in
   `tests/test_validate.py::TestDiffBaseContract._base_tree_holding` and it is reusable.
6. **Prove a new assertion bites by breaking the thing it guards.** Every behaviour added or
   repaired was mutation-checked, and the table is in the round entries. Two mutations that
   were ASSUMED covered turned out to leave the suite green — a filter reverted, and one
   branch of a three-way helper deleted. Run the mutations; do not assert coverage.
7. **A test needing two governed roots may need two for a reason.** One attempt at a
   regression test did not bite because a single unsupported root hit an early return before
   the code under test. Check that your fixture reaches the line you are testing.
8. **`docs/rule-map.md` rows use a restricted grammar.** `_canonical_row` rejects backticks,
   angle brackets, pipes and backslashes, and a rejected row silently drops out and fails
   `test_every_shipped_check_is_mapped`. Any new top-level function named `check_*` or
   `*_findings` REQUIRES a row — that is how the test is scoped.
9. **When changing a test's assertion, assert behaviour AND the class of error**, never one
   exact message and never a bare `any(ERROR)`.
10. **A disposition that fits none of rule 9's three grounds is OPEN.** One Major went to the
    maintainer with three options and a recommendation, and open was chosen — because calling
    a hole in a contract "out of scope" for that contract's own slice would have been
    distorting a category to fit. That escape hatch is the maintainer's, not yours.

=============================================================================
HOW TO WORK
=============================================================================
- Branch before editing; never commit to main; use a git worktree
  (`~/Code-Brain/groundwork-wt-issue-32`), and remove it after the merge.
- Rule 9 from round 1. If this branch's own commits add or change exactly one plan, the
  record goes in `docs/superpowers/plans/<slice>-reviews/`; otherwise
  `docs/superpowers/reviews/<branch-slug>/`. One file per entry, `round-NN.md` from 01,
  immutable once committed. Record the reviewed revision as a commit SHA, the verdict, and
  every finding with the reviewer's own severity word verbatim plus its disposition. A
  correction to an earlier entry goes in a later one. The README carries the fix-commit map,
  the open findings and the rejected findings. Do NOT pre-fill a pending round's reviewed SHA.
- Codex review via the `codex:codex-rescue` agent with `--background`. **The subagent returns
  as soon as it launches the job — that is not the review finishing.** Poll the job JSON at
  `~/.claude/plugins/data/codex-inline/state/<dir-hash>/jobs/<task-id>.json`, where the
  dir-hash is keyed by the LAUNCH cwd (the worktree, not the main repo). The `result` field is
  a DICT; read `result.rawOutput`, not `result` as a string. Status passes through `queued`
  before `running`, and the job file may not exist for a few seconds after launch — poll for
  the file, then for the status. #31's rounds took 3-8 minutes each.
- Review threads are NOT resumable. After committing fixes, launch a fresh review.
- Tell Codex every round: point it at the PREVIOUS round's repairs first and name the failure
  shapes above; a clean round is a real outcome and it must not manufacture findings, and a
  finding it would not have raised on a first read is not a finding; it must not re-raise
  anything the record already discloses (list those explicitly, and the list grows each
  round); and its sandbox usually cannot create temp directories, so hundreds of
  `TemporaryDirectory` errors from `unittest` are environmental — verify the suite yourself
  and say so in the round entry.
- End green on all four commands above, and state any changed baseline explicitly in both the
  merge commit and the review record. The maintainer lands the merge unless they instruct
  otherwise; if they do, record that in the merge commit.

AFTER #32: issue #40 (marker deletion under a pre-marker base) is the natural next slice — it
is filed with its measurement, its two pinning tests, and the one unexplored route (walking
`base..HEAD` for a deleted marker).
