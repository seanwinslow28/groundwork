# Codex review record — branch `docs/generate-consent-gate-base`

> This is the durable per-round review log rule 9 requires. Rule 9 lands on the sibling
> branch `docs/review-record-rule`, and the approved landing order puts it first — so this
> log is kept prospectively, and merging this branch ahead of that one would make the
> citation premature. **Both branches were built in one session**, which departs from
> build-sessions rule 1 ("one increment per session") and the design's "one slice per
> session". The maintainer authorised the two doc slices as a bundle in the session
> kickoff, which is not a repository artifact a reader can check — so this records the
> departure, it does not show the rule was satisfied or waived. Ratifying it is the
> maintainer's, at merge. Rule 9 is the normative text — where
> the log lives, what each round must carry, and when it must be committed. **This log's
> own addition, which rule 9 does not require:** each finding is marked CONFIRMED (the reviewer verified it against a source)
> or PLAUSIBLE (reasoned, unverified). Whether that becomes part of rule 9 is a maintainer
> decision, not one taken here.

## Round 1 — 2026-08-29, task-mte9z00a-zzx25t, verdict: does not approve (6 findings)

Reviewed: commit `5dcf285` (the `generate.md` fix and this log's opening header). All 6
accepted; four fixed in the following commit, two recorded as maintainer items and not
changed. Every finding was re-verified against source before acting on it, per rule 8.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | "The generation commit" is not operationally defined, and the document never requires generation to be one commit — so the fix rests on an unstated assumption and does not tell an agent which SHA to name; a later terminal commit would silently exempt post-root commits | CONFIRMED | Fixed: the base is named as **the commit that creates the governed root** — the one adding `groundwork.pin` alongside the content. A single generation commit is recommended for unambiguity; if generation spans several, the root-creating commit is still the base and anything committed after it is an ordinary governed change, which is what the pin bullet already says. Verified independently: `generate.md` carries no commit step anywhere |
| 2 | major | "They bind on the first change after generation — the first new rule, the first skill, the first memory record — and that is the run that exercises them" is false twice: an unrelated change exercises nothing, and a **new** memory record does not exercise immutability | CONFIRMED | Fixed: the sentence now says which later work exercises what — a new rule or skill is #18's case; memory immutability needs a record present at the base to be edited or deleted; a change touching neither exercises neither. Verified independently: `memory_diff_findings`'s docstring reads "New records are fine", and it is driven by the base file list |
| 3 | major | The "Later runs" paragraph asserted every later base is the generation commit or a descendant — an ancestry guarantee the validator never checks (`_git_diff_context` verifies the ref resolves, lists its tree, compares against the filesystem; no merge-base test), broken by squash, rebase, a branch cut before generation, or generation on an unmerged branch; and it is unapproved widening, not needed to implement the approved fix | CONFIRMED | Fixed by removal. The paragraph is gone and the remaining text is scoped to this run, so it makes no claim about later bases. The real contract the reviewer names — a base must already contain the complete generated root — is **not** legislated here; it is a maintainer item below |
| 4 | major | Parallel adopter-facing sites unreconciled: `README.md:123` sends an adopter checking a freshly generated OS to `--diff main` with no guarantee `main` holds the generated root, and `CONTEXT.md:104`, a source of truth under rule 7, states the consent invariant with no bootstrap exception | CONFIRMED | **Not changed; both carried to the maintainer.** `CONTEXT.md` is the resolved-decision glossary and adding an exception to the #18 invariant is a locked-decision edit, not a builder's call — and there is a live question whether the root-creating commit is an *exception* to the invariant or simply the baseline the gate measures from, which is how decision 8 of the roles design frames it. `README.md`'s example is correct under the topology the docs assume and wrong under one they never pin down; fixing it means deciding that topology. Both are recorded here as open items |
| 5 | minor | "The working tree *is* the generation commit, so the diff examines an empty changeset" is too strong, and false for the measured repo (`?? .DS_Store`): the scan is base tree vs working filesystem, `_walk_working_tree` deliberately does not honour `.gitignore`, and the candidate set is base files ∪ working-tree files — so an untracked or ignored governed file is classified and can ERROR | CONFIRMED | Fixed: the paragraph now states the comparison model, says the scan does not honour `.gitignore`, and conditions emptiness on nothing in the tree the base does not already hold. Verified independently at `scripts/validate.py:3341` and `:3573` |
| 6 | minor | "The validator reads `groundwork.pin` from the working tree" — `_pin_dirs` discovers the pin by pathname from the base list and the working-tree scan; it never reads either pin's contents | CONFIRMED | Fixed: "discovers", not "reads" |

Verified clean by the round, and reported as such: the live reproduction matches the
document exactly — `--diff 8af5680` gives 2 errors / exit 1, one per rule, with the error
text quoted verbatim, and `--diff ab9e9bd` gives 0 / exit 0; that repo's committed
`governance/constitution/` holds exactly two files. `proposals/` is specified empty at
generation (`generate.md:55`). Preconditions 2–3 plus `protocol.md:11` do establish that
the layers are committed in the same repo, closing the different-repo hole. Both new
relative links resolve, and the prose matches the file's voice. On scope: the reviewer
judged the `groundwork.pin` bullet edit a faithful consequence of S2, and the
proves/does-not-prove paragraph **required** rather than optional — the run record itself
says the generating session's own workaround "proves nothing" — while the "Later runs"
paragraph was unapproved widening, disposed of at row 3.

**Gate note.** The reviewer's `python3 -m unittest discover -s tests -q` reported
`FAILED (errors=558)`, every error a `FileNotFoundError: No usable temporary directory
found` from `tempfile.TemporaryDirectory()` — its sandbox has no writable temp location.
No assertion failure was observed. Run outside that sandbox in this worktree the suite is
`OK (skipped=1)` over 709 tests. The three validator gates matched the expected values in
both environments.

### Open maintainer items from this round

1. **`CONTEXT.md`'s consent-gate entry and the root-creating commit** (finding 4). Is the
   commit that creates a governed root an *exception* to "an escalating change reaches the
   main line only via a reviewable proposal", or is it outside the invariant because it is
   the baseline the gate measures from rather than a change within a changeset? Decision 8
   of the roles design takes the second reading for the generated-repo case. Whichever it
   is, the glossary is silent on it today.
2. **`README.md:123`'s `--diff main` for a freshly generated OS** (finding 4). Correct
   when the root-creating commit is on `main`; it reproduces the S2 bug when generation
   happened on a branch that has not merged. Fixing it means deciding the repo topology
   generation assumes, which no document states.
3. **The base contract for later runs** (finding 3). The validator requires only that the
   ref resolves; nothing enforces that a base contains the generated root. Stating that
   contract would close the hole the removed paragraph tried to cover, and is a change to
   what the gate promises rather than to how this document describes it.

## Round 2 — 2026-08-29, task-mteadhof-nhr8en, verdict: does not approve (6 findings)

Reviewed: `5a71138` (the round-1 fixes). All 6 accepted; five fixed in the following
commit, one extended. **Three of round 1's five "fixed" dispositions were wrong or
incomplete**, and one of them changed a maintainer decision without asking — the failure
this session's kickoff named explicitly. Round-1 rows 1, 2, 4 and 5 are **amended** by
rows 1, 2, 4 and 6 below, and round 1's own prose summary is corrected by row 5.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Renaming the base from the approved "the generation commit" to "the commit that creates the governed root — the one adding `groundwork.pin`" is a substantive narrowing, not an operational definition, and the multi-commit fallback it carried is an unapproved governance policy: with the pin first, every later generated rule and skill escalates, which contradicts this section's own rationale and requires a pending-proposal state the roles design records as impossible | CONFIRMED | Fixed by reverting to the approved words. The base is "the generation commit — the one you wrote the OS in", and the multi-commit policy is gone. Round 1's finding — that the term is undefined and `generate.md` has no commit step — therefore stands **unfixed and escalated**, not resolved. It is open item 4 below. Amends round-1 row 1, whose "fixed" was an unapproved change |
| 2 | major | "A change touching neither exercises neither" is still false: the same invocation runs `interview_diff_findings`, so editing or deleting a confirmed layer exercises the frozen-layer guard while touching neither a new rule/skill nor a memory record; modifications to existing rules and skills and changelog rewrites are further counterexamples | CONFIRMED | Fixed: the false universal is gone. The sentence now names three cases without closing the set — new rule or skill (#18), editing or deleting a confirmed layer (frozen layers), and memory immutability needing a record present at the base. Amends round-1 row 2, whose "verified independently" did not cover the third pass |
| 3 | major | The pin bullet's pointer, "what the root-creating commit is itself measured against", inverts the model — that commit is passed **as the base**, so its tree is excluded from the comparison rather than measured; the two descriptions conflict on the core S2 requirement | CONFIRMED | Fixed: the pointer now reads "which commit the gate measures *from*, and why the write order inside it does not change what the gate sees" |
| 4 | minor | "With nothing in the tree the base does not already hold" rules out additions by pathname only; a base file deleted from the tree, or retained with changed contents, still gives the passes something to find | CONFIRMED | Fixed: the condition is now the working tree matching the base for every file either side holds. Amends round-1 row 5 |
| 5 | major | This log overclaims: rows 1, 2 and 5 were called fixed when their replacements were wrong; the prose said "four fixed … two not changed" while the table marks five rows fixed and one not; and "the error text quoted verbatim" is false — neither the log nor `generate.md` quotes the validator's wording, and the S2 source's shortened form is not the current text | CONFIRMED | Corrected here by supersession, round 1's table left as written. The count: round 1 was **five rows fixed, one row not changed** — row 4 alone, and it carries two maintainer items, which is what the prose miscounted. The verbatim claim is withdrawn: the reviewer checked the error text against the validator's output; `generate.md` paraphrases it and quotes nothing |
| 6 | minor | Open item 2 named only `README.md:123`, omitting `delivery/README.md:238`, which gives the same company-repo `--diff main` command and promises exit 0 — and the removed "Later runs" paragraph had cited both, so it was not a discovery failure | CONFIRMED | Fixed: open item 2 now names both sites. Amends round-1 row 4's inventory |

Verified clean by the round, and reported as such: the measurement reproduces exactly —
`--diff 8af5680` gives 2 errors / 5 warnings / exit 1, one error per rule, and
`--diff ab9e9bd` gives 0 / exit 0, with exactly two committed files under
`governance/constitution/`. `_pin_dirs` does exactly *discover* pin pathnames from both
sides, so row 6 of round 1 was right. Preconditions 2–3 plus `protocol.md:11` establish
the same-repo committed history. Removing the "Later runs" paragraph was correct — it
asserted an ancestry guarantee the validator does not enforce — and the resulting silence
about later bases is fairly recorded as open item 3. The header's landing-order claim is
accurate. All four gates matched: `validate.py .` 0 errors / 7 warnings, `--diff main`
exit 0, `demo` 0 errors / 2 warnings, 709 tests OK (skipped=1).

One observation the round recorded without raising it as a finding: `proposals/` in the
generated OS contains a `README.md`, so it holds no pending proposal but is not literally
empty — the pre-existing C8 distinction. `generate.md`'s "empty at generation" is its own
existing wording, unchanged by this branch.

### Open maintainer items after this round

Items 1–3 stand as recorded in round 1, with item 2 extended:

1. **`CONTEXT.md`'s consent-gate entry and the root-creating commit.** Unchanged. The
   glossary says every escalating change reaches the main line through a proposal; this
   branch exempts the root-creating commit. Decision 8 supports reading generation as the
   baseline rather than an exception, but the glossary does not express that reading.
2. **`README.md:127` *and* `delivery/README.md:244`.** Both give a company repo
   `--diff main`, and `delivery/` promises exit 0. Both are correct once the generation
   commit is on `main` and both reproduce S2 while generation sits on an unmerged branch.
3. **The base contract for later runs.** The validator requires only that the ref
   resolves; nothing enforces that a base contains the generated root.
4. **What "the generation commit" means when generation is not one commit** (new, row 1).
   `generate.md` contains no commit step at all, so the approved words name a commit the
   document never tells anyone to make. The options are: say generation lands as a single
   commit; define the base as the commit that creates the governed root and accept the
   multi-commit governance consequences; or leave it, since the ordinary case is
   unambiguous. This was decided unilaterally in `5a71138` and is now reverted to the
   approved wording pending the maintainer's call.

## Round 3 — 2026-08-29, task-mteatahf-ox2v1s, verdict: does not approve (7 findings)

Reviewed: `f562d69` (the round-2 fixes). All 7 accepted; six fixed in the following
commit, one extended. Round-2 rows 2, 4 and 6 are **amended** by rows 1, 4 and 6 below,
and open item 4 is extended by row 3.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The frozen-layer clause omits its base-presence condition. `interview_diff_findings` derives its state directories and layers from `ctx["base_files"]`, exactly as the memory pass does, and a test at `tests/test_validate.py:6027` proves a new layer is invisible to it — so a layer committed after a stale base and then edited against that base is not frozen | CONFIRMED | Fixed: the sentence now says both guards read from the base and need a layer or record that was already there, with adding a new one always fine and invisible to them. Amends round-2 row 2, whose "fixed" claimed more than `f562d69` delivered |
| 2 | major | The section says `--diff` adds "the #18 consent gate on **every governed change**" — false: #18 binds escalating changes, track-1 body-only edits are classified separately and only WARN for a missing changelog line, and governed deletions only WARN. `CONTEXT.md:104` limits the invariant to escalating changes. Pre-existing text, in the sentence S2 rewrites, that no prior round surfaced | CONFIRMED | Fixed: "on escalating changes". A factual correction inside the paragraph under repair, not a policy change. The related adopter-facing drift the round names at `README.md:134` — rules and high-risk skills only, no external-side-effect skills, no escalating frontmatter or card edits, no deletion exception — is **not** edited here; it joins open item 2 |
| 3 | major | Open item 4's option list is incomplete: it omits defining the generation commit as the **final** generation commit, which preserves the approved policy without requiring atomic generation or governing intermediate work. The surviving prose ("the write order inside that commit", "every rule and skill arrives with the root") reads correctly only under an atomic or terminal reading the document never states | CONFIRMED | Open item 4 extended with the fourth option and with the note that the prose is sound under options 1 and 4 and unsound under a mid-sequence reading. Not otherwise changed: choosing among the four is the maintainer's, and choosing unilaterally is what round 2 punished |
| 4 | minor | The emptiness condition — the working tree matching the base "for every file either side holds" — is sufficient but not necessary. The stateful passes look only at base memory records, base interview layers, and governed rule/skill candidates plus the governance changelog; a changed root `README.md` gives them nothing | CONFIRMED | Fixed: the condition is now "nothing yet touched that the base already holds", which no longer implies that any working-tree difference makes the run non-empty. Amends round-2 row 4 |
| 5 | minor | The log header calls itself "the durable per-round review log rule 9 requires" and four lines later claims to restate none of rule 9 — the first statement restates rule 9's core requirement | CONFIRMED | Fixed by dropping the claim rather than chasing it, the same disposition R0's round 3 reached on the same defect in its own header |
| 6 | minor | Open item 2's line references are wrong: the commands are at `README.md:127` and `delivery/README.md:244`, not `:123` and `:238` | CONFIRMED | Fixed. The wrong numbers came from transcribing round 1's citations instead of the ones this session had already verified — rule 8's failure in miniature. Amends round-2 row 6 |
| 7 | minor | "`proposals/` empty at generation" is literally false — the generated repo's `proposals/` holds a committed `README.md` and zero pending proposals — and this section leaned on that literal wording | CONFIRMED | Fixed for this section: it no longer cites the word, and says generation leaves nothing pending for the gate to match against, which is the load-bearing fact. The tree diagram at `generate.md:55` keeps its own pre-existing wording, which is the known C8 distinction and not this branch's to redefine |

Verified clean by the round, and reported as such: the round-2 revert is **complete and
policy-faithful** — the introduction, the placeholder, the base sentence and the pin
pointer all carry the approved words, no root-creating base or multi-commit rule survives,
and the approved bootstrap statement remains; it matches S2's "generation commit, not
pre-generation commit" and decision 8's baseline description. Round 2's count correction
is right (round 1 had five "Fixed" rows and one "Not changed"), and the withdrawn
"quoted verbatim" claim is correctly characterised. Round 1's table is unchanged from its
first appearance in `5a71138`, and every amendment pointer resolves to the intended row.
The measurement reproduces again: `--diff 8af5680` 2 errors / 5 warnings / exit 1, one per
rule; `--diff ab9e9bd` 0 / exit 0; exactly two constitution files. `_pin_dirs` discovers
pin pathnames from both sides. Preconditions 2–3 plus `protocol.md:11` establish the
same-repo committed history. Open items 1 and 3 are accurate as recorded. Gates:
`validate.py .` 0 errors / 7 warnings, `--diff main` exit 0, `demo` 0 errors / 2 warnings,
709 tests OK (skipped=1).

### Open maintainer items after this round

Items 1 and 3 stand as recorded. Items 2 and 4 are extended:

1. **`CONTEXT.md`'s consent-gate entry and the root-creating commit.** Unchanged. The
   branch still actively contradicts the glossary's unqualified invariant.
2. **`README.md:127`, `delivery/README.md:244`, and `README.md:134`** (extended, row 2).
   The first two give a company repo `--diff main` — correct once the generation commit is
   on `main`, reproducing S2 while generation sits on an unmerged branch. The third
   describes what the stateful run enforces as rules and high-risk skills only, omitting
   external-side-effect skills and escalating frontmatter and card edits, and not
   mentioning that deletions only WARN.
3. **The base contract for later runs.** Unchanged. The validator checks only that the ref
   resolves — neither ancestry nor that the base contains the generated root.
4. **What "the generation commit" means when generation is not one commit** (extended,
   row 3). `generate.md` contains no commit step at all. Four options, not three:
   (a) say generation lands as a single commit; (b) define the base as the commit that
   creates the governed root and accept that later generation commits are governed;
   (c) define it as the **final** generation commit, which keeps the approved policy
   without requiring atomicity or governing intermediate work; (d) leave it, since the
   ordinary case is unambiguous. The section's surviving prose reads correctly under
   (a) and (c) and unsoundly under a mid-sequence reading. Option (b) was taken
   unilaterally in `5a71138` and reverted in `f562d69`.

## Round 4 — 2026-08-29, task-mteba9ee-7n0jnx, verdict: does not approve (7 findings)

Reviewed: `7421d58` (the round-3 fixes). All 7 accepted; five fixed in the following
commit, two extended. Round-3 rows 1, 2, 3, 4 and 6 are **amended** by rows 1, 2, 3, 5 and
6 below. Prior rounds' tables stay as written.

**Fix commits, recorded now that they exist** (rule 9 asks for "fixed in commit X"; a
round's dispositions are written before their commit): round 1 → `5a71138`, round 2 →
`f562d69`, round 3 → `7421d58`, round 4 → the commit following this table.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The emptiness condition — "nothing yet touched that the base already holds" — is **neither** sufficient nor necessary. Not sufficient: the blast-radius candidate set is base files ∪ working-tree files, so a newly added rule or skill touches no base-held file and still escalates (`test_new_rule_file_escalates`), which the very next sentence of the document says. Not necessary: editing a base-held but statefully irrelevant file leaves every pass clean (`test_manifest_edit_is_fine`) | CONFIRMED | Fixed by giving up on a stated condition, which three rounds have now got wrong in three different directions. The text says what to do — run it straight after generation, before you have changed anything — and what that shows, and claims no iff. Amends round-3 row 4 |
| 2 | major | The `groundwork.pin` bullet's ordering rationale is false and the round-1 pointer now connects it to a sentence saying the opposite: against a pre-generation base the pin is discovered from either tree and the blast pass scans the whole working tree, so rules and skills classify regardless of write order, and the between-stage command is stateless | CONFIRMED | Fixed by removing the pointer, restoring the bullet to its pre-existing text. Rewriting the rationale correctly depends on whether generation is one commit or many, which is open item 4 and the maintainer's — and round 1's pointer was the widening that made the latent contradiction load-bearing. The falsity is recorded as open item 5. Amends round-1 row 3 and round-2 row 3, whose fixes repaired the pointer's wording while its premise stayed false |
| 3 | major | "The stateful modes: org-memory immutability, frozen interview layers, and the #18 consent gate on escalating changes" is still an incomplete account of what `--diff` adds — `blast_radius_diff_findings` also carries #17's append-only changelog ERROR and the WARNs for a governed deletion and a missing changelog line, as `docs/rule-map.md` inventories | CONFIRMED | Fixed: the sentence now names the blast-radius pass and its three behaviours. Round 3's disposition acknowledged the omission and then called the sentence fixed, which was the overclaim. Amends round-3 row 2 |
| 4 | major | The log gives no fix-commit SHAs, so it does not deliver rule 9's "fixed in commit X" — the chronology makes them inferable, and inference is weaker than the contract | CONFIRMED | Fixed: the mapping is recorded above this table and will be extended each round. The same defect and the same remedy apply to the sibling branch's log |
| 5 | minor | Round 3 cited `CONTEXT.md:104` in the same table where it condemned unverified transcription; the invariant is at `CONTEXT.md:105` | CONFIRMED | Corrected here by supersession, prior tables untouched: the consent invariant is at **`CONTEXT.md:105`**, verified in this worktree. Open item 1 below carries the corrected reference. (A first attempt edited the earlier tables in place and was reverted — those tables are byte-identical to their first appearance.) Amends round-3 row 5's citation |
| 6 | minor | "Adding a new one is always fine" holds inside the two guard functions only: `main()` runs the whole stateless `validate(root)` before the diff passes, so a malformed new record or a layer inconsistent with its manifest still ERRORs | CONFIRMED | Fixed: "invisible to those two guards, though the stateless checks still read it". Amends round-3 row 1 |
| 7 | minor | Open item 4's option (c) is stated more confidently than the sources support — S2 exempts "the commit which creates the governed root" and decides nothing about later generation commits, so a final-commit base is an interpretation, not a consequence; and a distinct fifth option is missing: permit multi-commit generation but require the pin to land only in the final commit, making that commit the root-creating one | PLAUSIBLE | Open item 4 restated neutrally and extended with option (e). Not decided here |

Verified clean by the round, and reported as such: both round-3 guard claims are exact —
memory iterates only base-held records and excludes `_index.md`, interview state
directories and layer candidates both come from `base_files`, and no manifest, index or
working-tree scan makes a new record or layer visible to those two passes, with tests
pinning both. "Escalating" is the repository's own term and the right category. The
proposals sentence is accurate against the generated OS: its generation commit carries
`proposals/README.md`, zero pending proposals, and both rules, and `_pending_proposal_radii`
skips `README.md`. The round-1 and round-2 tables are byte-for-byte unchanged from their
first appearances in `5a71138` and `f562d69`, and every amendment pointer resolves. The
approved direction is preserved — the base is the generation commit, the root-creating
commit is excluded from subsequent comparisons, and no validator change is introduced —
and the round judged the "escalating changes" correction, the "nothing pending" rewording,
the measured explanation, and the base-tree-versus-filesystem explanation all faithful
factual consequences rather than widening. Gates: `validate.py .` 0 errors / 7 warnings,
`--diff main` exit 0, `demo` 0 errors / 2 warnings, 709 tests OK (skipped=1).

### Open maintainer items after this round

1. **`CONTEXT.md:105`'s consent-gate entry and the root-creating commit.** Unchanged in
   substance, corrected in citation. The branch still actively contradicts the
   unqualified invariant unless generation is read as the baseline rather than an
   exception.
2. **`README.md:127`, `delivery/README.md:244`, and `README.md:134–137`.** Unchanged, with
   one addition: the README passage's account of what the stateful run enforces should
   also carry #17's changelog behaviour, not only #18.
3. **The base contract for later runs.** Unchanged. `_git_diff_context` verifies only that
   the ref resolves and lists its tree — neither ancestry nor that the base contains the
   governed root.
4. **What "the generation commit" means when generation is not one commit** (restated,
   row 7). `generate.md` contains no commit step. Five options: (a) say generation lands
   as a single commit; (b) define the base as the commit that creates the governed root
   and accept that later generation commits are governed — taken unilaterally in
   `5a71138` and reverted; (c) define it as the final generation commit, which excludes
   intermediate generation commits from the gate — an interpretation S2 and decision 8
   do not settle, since S2 exempts only "the commit which creates the governed root";
   (d) leave it, since the ordinary case is unambiguous; (e) permit multi-commit
   generation but require `groundwork.pin` to land only in the final generation commit,
   so that commit is also the root-creating one and the approved singular exemption holds
   without atomic generation.
5. **The `groundwork.pin` bullet's ordering rationale is false** (new, row 2).
   "Write the file at the end … Generate under the pin and you will write a proposal per
   file" implies write order protects the generation commit. Against a pre-generation
   base it does not: the pin is discovered from either tree, the blast pass scans the
   whole working tree, and the between-stage command is stateless. The rationale is true
   only for a pin committed in an earlier commit — so repairing it depends on item 4.

## Round 5 — 2026-08-29, task-mtebvc31-4ua8c9, verdict: does not approve (8 findings)

Reviewed: `10e1ec1` (the round-4 fixes). All 8 accepted; five fixed in the following
commit, three extended or escalated. Round-4 rows 1, 2, 6 and 7 are **amended** by rows 3,
4, 6 and 8 below, and round 4's own summary is corrected by row 2. Prior rounds' tables
stay as written.

**Fix commits** (rule 9's "fixed in commit X"): round 1 → `5a71138`, round 2 → `f562d69`,
round 3 → `7421d58`, round 4 → `10e1ec1`, round 5 → the commit following this table, named
by SHA in the next round.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The log's header called the sibling branch "this session's other increment", contradicting build-sessions rule 1 ("one increment per session") and the design's "one slice per session" | CONFIRMED | Fixed by recording the departure instead of implying none: the header now says both branches were built in one session, that this departs from rule 1, and that the maintainer authorised the two doc slices as a bundle in the session kickoff |
| 2 | major | Round 4's record is not compliant: the mapping still says "round 4 → the commit following this table" although `10e1ec1` now exists, and its "five fixed" count is false — rows 1, 2, 4 and 6 were not fully fixed | CONFIRMED | Corrected by supersession, round 4's table untouched: round 4's fix commit is **`10e1ec1`**, recorded above, and the mapping now says each round's SHA is filled in by the next round rather than left as a forward reference. Round 4 delivered **one row fully fixed (row 3), four partially, and two extended** — this row supersedes its summary |
| 3 | major | The emptiness sentence is wrong a fourth time: "before you have changed anything" is not a filesystem condition — the measured repo carries untracked `.DS_Store`, `_walk_working_tree` ignores `.gitignore`, so an untracked governed file produces a finding while the operator believes nothing changed — and "it has nothing to work on" is still unconditional. Abandoning the condition removed information the reader needs | CONFIRMED | Fixed by describing the mechanism instead of any condition, true or false: the scan reads whatever sits in the directory, tracked or not; the base is the tree just committed; a clean result says the modes ran and found nothing, not that they were exercised. Four rounds have now failed to state a condition, so this states none and hides none. Amends round-4 row 1 |
| 4 | major | The restored `groundwork.pin` bullet is still false and still contradicts the new section, and **the factual repair does not require deciding the multi-commit policy** — so open item 5 was the wrong disposition | CONFIRMED | Fixed, and the review is right that I could have done this two rounds ago: the bullet's rationale is now scoped to commits — once the pin is **committed** the root is governed, and a rule added in a **later commit** escalates; "generate under a pin an earlier commit already carries" is the true reading of the original clause. No policy is decided. Open item 5 is closed. Amends round-4 row 2 |
| 5 | major | "Every rule and skill in the repo arrives with the root" and "the write order inside that commit" presuppose atomic or terminal generation, which S2 does not establish and `generate.md` does not describe — the approved words exempt the commit that creates the root and settle nothing about how many commits generation takes | CONFIRMED | Fixed by removing the presupposition, not by choosing a policy: the bootstrap sentence now rests only on "generation leaves nothing pending for the gate to match a generated rule or skill against", and the write-order sentence is conditional — a rule *committed alongside* the pin is classified exactly as one committed after it. Open item 4 still owns the underlying decision |
| 6 | major | "Though the stateless checks still read it" is false: the stateless memory and interview walkers honour `.gitignore` and skip dot directories, so an ignored new record or layer may not be read at all. And an existing layer is protected only when its interview manifest was also at the base — layer presence alone is insufficient | CONFIRMED | Fixed: the false clause is deleted rather than replaced with a fifth qualifier, and the manifest condition is now stated. The manifest requirement joins the open items as item 5 (renumbered). Amends round-4 row 6 |
| 7 | major | The parallel-site inventory is incomplete: `delivery/README.md:247–248` and `proposals/README.md:55` also give partial accounts of what the stateful run enforces, and `interview/README.md:85`, `interview/protocol.md` and `docs/security-and-privacy.md:149` imply any committed layer is protected without stating that the base must hold the layer **and** its manifest | CONFIRMED | Open item 2 extended with all five sites. Not edited here: they are the same class as the two already deferred, and repairing them means stating the base contract, which is open item 3 |
| 8 | major | Open item 4's option set is still incomplete — a sixth option is an explicit post-generation baseline commit, possibly empty or a merge, whose tree holds the completed OS — and option (d) is slanted: "the ordinary case is unambiguous" assumes a commit workflow the document does not contain | PLAUSIBLE | Fixed: option (f) added, and (d) restated neutrally as leaving the term undefined and relying on adopter inference. Amends round-4 row 7 |

Verified clean by the round, and reported as such: the mode list is correct at the policy
level — `main()` adds exactly the memory, blast-radius and interview passes, and the
sentence names all three plus the blast pass's four policy outputs. A newly added layer or
memory record is confirmed invisible to its base-driven guard. The `groundwork.pin` bullet
was byte-identical to `main` before this round's repair. Rounds 1, 2 and 3 tables are
byte-for-byte identical to `5a71138`, `f562d69` and `7421d58`, and every round's recorded
fix-commit SHA is correct. The measurement reproduced again: `--diff 8af5680` 2 errors / 5
warnings / exit 1, `--diff ab9e9bd` 0 / exit 0. Open items 1 and 3 are accurate and fairly
deferred. On the approved direction: the two literal changes are present and no validator
code changed; the round judged the measured comparison, the `_pin_dirs` discovery claim,
the base-tree-versus-filesystem explanation, the "escalating" scope, the complete mode
inventory and the nothing-pending explanation all faithful factual consequences.

**Gate note.** The reviewer's unit-test run was sandbox-blocked again — 709 tests
discovered, then 558 `FileNotFoundError: No usable temporary directory found`, with a
`TMPDIR` retry also refused; it correctly declined to report a pass. Run in this worktree
the suite is `OK (skipped=1)` over 709 tests. The three validator gates passed in both
environments: `validate.py .` 0 errors / 7 warnings, `--diff main` exit 0, `demo` 0
errors / 2 warnings.

### Open maintainer items after this round

Item 5 (the pin bullet's false rationale) is **closed** — repaired in this round's fix
commit, since the factual correction needed no policy decision. The remaining items are
renumbered.

1. **`CONTEXT.md:105`'s consent-gate entry and the root-creating commit.** Unchanged. Is
   generation outside governed self-improvement, or an exception to it? The glossary says
   every escalating change reaches the main line through a proposal, without qualification.

2. **Adopter-facing sites that state the base or the enforcement, incompletely** (extended,
   row 7). `README.md:127` and `delivery/README.md:244` give a company repo `--diff main`,
   which reproduces S2 before generation reaches `main`, and `delivery/` promises exit 0.
   `README.md:134` and `delivery/README.md:247–248` describe what the stateful run enforces
   without external-side-effect skills, frontmatter and Owner's Card escalation, or #17's
   changelog behaviour, and `README.md:134`'s blanket "or the gate ERRORs" is false for
   deletions, which WARN. `proposals/README.md:55` omits the governed-deletion WARN.
   `interview/README.md:85`, `interview/protocol.md` and `docs/security-and-privacy.md:149`
   imply any committed layer is protected, without the base condition item 4 records.

3. **The base contract for later runs.** Unchanged. `_git_diff_context` verifies only that
   the ref resolves and lists its tree — neither ancestry nor that the base holds the
   generated root. Several sites in item 2 lean on a guarantee nothing provides.

4. **What "the generation commit" means when generation is not one commit** (extended,
   row 8). `generate.md` contains no commit step. This is the item blocking the section
   from reading correctly without an unstated assumption. Six options:
   (a) say generation lands as a single commit; (b) define the base as the commit that
   creates the governed root and accept that later generation commits are governed — taken
   unilaterally in `5a71138`, reverted in `f562d69`; (c) define it as the final generation
   commit, excluding intermediate generation commits from the gate — an interpretation S2
   and decision 8 do not settle, since S2 exempts only "the commit which creates the
   governed root"; (d) leave the term undefined and rely on adopter inference; (e) permit
   multi-commit generation but require `groundwork.pin` to land only in the final
   generation commit, so that commit is also the root-creating one; (f) make an explicit
   post-generation baseline commit — possibly empty, possibly a merge — whose tree holds
   the completed OS, and define that as the baseline.

5. **The frozen-layer guarantee needs the manifest, not just the layer** (new, row 6).
   `interview_diff_findings` derives its state directories from the base file list, so a
   layer is protected only when the base also holds its interview manifest. The document
   now says this; the sites in item 2 do not.

## Round 6 — 2026-08-29, task-mtecgu1a-uhc159, verdict: does not approve (9 findings)

Reviewed: `d2ce4fc` (the round-5 fixes). All 9 accepted; six fixed in the following commit,
three corrected by supersession or escalated. Round-5 rows 1, 2, 3, 4 and 6 are **amended**
below; round 5's open-items section is **superseded in full** by this round's and left as
written. Prior tables untouched.

**Fix commit for round 5: `d2ce4fc`.** Round 1 → `5a71138`, round 2 → `f562d69`, round 3 →
`7421d58`, round 4 → `10e1ec1`, round 5 → `d2ce4fc`. Round 6's is named by round 7.

**The blocking answer.** Asked directly whether this branch can reach approve without the
maintainer deciding open item 4, the round answered no: *"This branch cannot receive
approval until item 4 is decided and the prose is made consistent with that choice."*
That is recorded here as the branch's state, not worked around.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The round-5 pin repair is base-dependent and closing item 5 was premature: "every rule or skill added in a later commit wants a proposal" is true against a pre-pin or root-creating base and false against a final-generation base, so the repair silently picked item 4's option (b) while claiming to pick none | CONFIRMED | Fixed in base-relative terms, which is topology-independent: whether a rule or skill escalates "turns on the base you diff against — it escalates when that base does not already hold it — not on the order you wrote the files in". True under all six of item 4's options. Item 5 stays closed on that basis, and this row records why. Amends round-5 row 4 |
| 2 | major | Atomic or terminal generation is still presupposed — "the one you wrote the OS in", "one commit further back", "the tree you just committed" — and **the branch cannot be approved until item 4 is decided** | CONFIRMED | Partly fixed, and the rest recorded as the branch's blocking state. The three glosses are gone: the base is named as "the generation commit" with no gloss, "one commit further back" becomes "back past generation", and the causal clause about the tree is deleted. What remains is that the approved term itself names a commit the document never tells anyone to make — which is item 4 and not repairable here. Amends round-5 row 5 |
| 3 | major | "Whatever sits in the directory is read, tracked or not" is false for a fifth formulation: `_walk_working_tree` prunes `SKIP_DIRS`, every dot-directory, and `SKIP_RELPATHS` including `tests/` and `docs/superpowers/`, and it lists candidates whose contents are read only when governed | CONFIRMED | Fixed by deleting the description. Five formulations of this sentence have now been wrong; the paragraph keeps only what has survived every round — the comparison is base tree against working filesystem, and a clean result says the modes ran and found nothing, not that they were exercised. Amends round-5 row 3 |
| 4 | major | Round 5's correction of round 4 is itself miscounted — its own text marks rows 1, 2, 4 and 6 incomplete, which leaves rows 3 **and 5** fully fixed, so round 4 was two full, four partial, one extended — and round 5's own "five fixed, three extended" is false: rows 3 and 4 remained defective, row 2's correction was wrong, row 1 records rather than cures a departure | CONFIRMED | Corrected by supersession, round 5's table untouched: **round 4 delivered two rows fully fixed (3 and 5), four partial, one extended.** For round 5 itself, this round's audit stands as the record — rows 2–5 overclaimed, row 6 was correct, row 7 delivered with one wrong citation, row 8 added the option without establishing neutrality. Amends round-5 row 2 |
| 5 | major | Recording the rule-1 departure is proper auditing but does not satisfy rule 1, and a repository reader cannot verify the maintainer authorisation from any durable artifact — the kickoff is not one | CONFIRMED | Fixed: the header now says the authorisation is not a repository artifact a reader can check, that recording the departure does not show the rule was satisfied or waived, and that ratifying it is the maintainer's at merge. Amends round-5 row 1 |
| 6 | minor | The memory guard does not catch every edit to a base-held record: `owner` and `review_by` are mutable, `source` may grow append-only, and provenance may move through allowed transitions. It catches deletion and forbidden edits | CONFIRMED | Fixed: "a base-held memory record deleted or edited in a way the schema forbids". Amends round-5 row 6's coverage sentence |
| 7 | minor | "Any OS carrying one is red" is wider than the source, which says every **generated** OS carrying a constitution rule reproduces the failure **against a pre-generation base** — an unchanged rule already at the base, or a changed one with a matching proposal, is not red | CONFIRMED | Fixed: "every generated OS carrying a constitution rule goes red against that base". The round-5 narrowing had dropped both qualifiers the source carries |
| 8 | minor | Not every cited line number is right: `docs/security-and-privacy.md`'s frozen-layer claim is at 151–152 not 149, README's "or the gate ERRORs" is at 136–137 not 134, and `protocol.md`'s same-repository text is at 13–15, with :11 naming the section | CONFIRMED | Corrected in this round's open items, verified in this worktree rather than transcribed. The historical wrong citations in rounds 1–3 stay as written and superseded |
| 9 | minor | Item 4 is a materially complete topology inventory but is not decision-ready: it has no recommendation and no counter-argument, which rule 5 requires, and its options are presented asymmetrically — (b) carries negative history, (e) is framed as preserving the approved exemption, (f) does not say it can exempt post-pin generation commits beyond S2's literal statement | PLAUSIBLE | Fixed: item 4 now carries a recommendation and a counter-argument, and the three asymmetries are levelled |

Verified clean by the round, and reported as such: `_pin_dirs` discovers pins from both the
base tree and the pruned working-tree scan; `_governed_class` classifies every new
constitution file and every new skill-package file, so a new `SKILL.md` always escalates;
`interview_diff_findings` requires both the layer and a `00-manifest.md` in the same base
state directory, so round 5's manifest sentence is exact. The measurement reproduces
unchanged. All five recorded fix-commit SHAs are correct and rounds 1–4 tables are
byte-identical to their introducing commits. All four validator and test gates passed in
the reviewer's environment this time — `validate.py .` 0 errors / 7 warnings, `--diff main`
exit 0, `demo` 0 errors / 2 warnings, and 709 tests `OK (skipped=1)` with no sandbox block.

### Open maintainer items after round 6 — superseding round 5's set in full

Item 5 stays closed: the pin rationale is now stated base-relatively, which is true under
every option below. Line references are re-verified in this worktree.

**1. `CONTEXT.md:105`'s consent-gate entry and the root-creating commit.** Unchanged. Is
generation outside governed self-improvement, or an exception to it? The glossary states
the invariant without qualification.

**2. Adopter-facing sites that state the base or the enforcement, incompletely.**
`README.md:127` and `delivery/README.md:244` give a company repo `--diff main`, which
reproduces S2 before generation reaches `main`, and `delivery/` promises exit 0.
`README.md:134–137` and `delivery/README.md:247–248` describe what the stateful run
enforces without external-side-effect skills, frontmatter and Owner's Card escalation, or
#17's changelog behaviour, and README's blanket "or the gate ERRORs" at 136–137 is false
for deletions, which WARN. `proposals/README.md:55` omits the governed-deletion WARN.
`interview/README.md:85`, `interview/protocol.md:13–15` and
`docs/security-and-privacy.md:151–152` imply any committed layer is protected, without the
base condition item 5 records.

**3. The base contract for later runs.** `_git_diff_context` verifies only that the ref
resolves and lists its tree — neither ancestry nor that the base holds the generated root.
Several sites in item 2 lean on a guarantee nothing provides.

**4. What "the generation commit" means when generation is not one commit.** This is the
item blocking the branch. `generate.md` contains no commit step, so the approved term names
a commit nothing tells anyone to create.
*Options.* (a) State that generation lands as a single commit. (b) Define the base as the
commit that creates the governed root, so generation work committed after it is governed.
(c) Define it as the final generation commit, so intermediate generation commits are
outside the gate. (d) Leave the term undefined and rely on adopter inference. (e) Permit
multi-commit generation but require `groundwork.pin` to land only in the final generation
commit, so that commit is both the final and the root-creating one. (f) Make an explicit
post-generation baseline commit — possibly empty, possibly a merge — whose tree holds the
completed OS, and define that as the baseline; like (c) and (e), this places every
generation commit inside the base rather than under the gate, which reaches further than
S2's literal exemption of "the commit which creates the governed root".
*Recommendation:* (e). It is the only option under which S2's approved sentence is
literally true without adding an atomicity requirement — the root-creating commit and the
final commit become the same commit — and the document already tells the generator to write
the pin last, so (e) turns existing advice into the definition rather than adding a rule.
*Counter-argument:* it makes a formatting-order instruction load-bearing for governance,
so a generator that writes the pin early produces a repo whose base this rule cannot name;
and (a) is simpler, matches what generation actually does today, and needs no ordering
guarantee at all. Against both: (b) is the only option that keeps every post-root commit
under the gate, which is what #18 exists for, at the cost of making a multi-commit
generation write proposals for its own output.

**5. The frozen-layer guarantee needs the manifest, not just the layer.**
`interview_diff_findings` derives its state directories from the base file list, so a layer
is protected only when the base also holds its `00-manifest.md`. `generate.md` now says
this; the sites in item 2 do not.

**6. The rule-1 departure.** (new, row 5) Both branches of this session were built as one
session's work, departing from build-sessions rule 1 and the design's one-slice-per-session
landing order. The maintainer authorised it in the session kickoff, which is not a
repository artifact. The log records the departure; whether to ratify it, and whether rule
1 should say how a bundle is authorised, is the maintainer's.
