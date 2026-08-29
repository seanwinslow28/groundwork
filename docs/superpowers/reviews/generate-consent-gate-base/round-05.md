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
