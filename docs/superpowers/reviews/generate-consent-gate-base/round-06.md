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
