# Codex review record — branch `docs/generate-consent-gate-base`

> The durable per-round review log rule 9 requires. Rule 9 lands on the sibling branch
> `docs/review-record-rule`, this session's other increment, and the approved landing
> order puts it first — so this log is kept prospectively, and merging this branch ahead
> of that one would make the citation premature. Plan-less work uses this location
> (`docs/superpowers/reviews/<branch>.md`, `/` written as `-`). Rule 9 is the normative
> text and this header does not restate it. **This log's own addition, which rule 9 does
> not require:** each finding is marked CONFIRMED (the reviewer verified it against a
> source) or PLAUSIBLE (reasoned, unverified). Whether that becomes part of rule 9 is a
> maintainer decision, not one taken here.

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
