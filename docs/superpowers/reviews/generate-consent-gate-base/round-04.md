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
