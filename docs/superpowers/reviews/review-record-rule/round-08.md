## Round 8 — 2026-08-29, task-mtedvjio-d78rka, verdict: does not approve (9 findings)

Reviewed: `b33296e` (the eleven maintainer decisions implemented — rule 9 rewritten as the
operative contract, decision 7 amended to point at it, and this log converted to the
per-round layout). All 9 accepted, all CONFIRMED; six fixed in the following commit, three
answered here. Round 7's landing claims are **amended** by this entry: it recorded five of
the eleven decisions as fully landed when they had landed partially.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | The branch cannot merge under its own new rule: nine rows across rounds 1–6 remain "carried", "open", "recorded" or "escalated", which rule 9 does not recognise, and round 7 recorded where the decisions landed without ever converting those dispositions | CONFIRMED | Fixed: every one is dispositioned below, and the README's fix map now runs to `b33296e`. This is the same defect the sibling branch's round 8 found in its own log — a rule that admits two dispositions makes every prior escalation non-terminal the moment it lands |
| 2 | major | The terminal-override clause contradicts the unresolved-finding prohibition: a non-approving verdict usually carries unresolved findings, and merge-commit grounds are not one of the two allowed per-finding dispositions, so the override cannot make such a branch mergeable | CONFIRMED | Fixed by unifying rather than adding a third form: merging over a non-approving verdict **is** a rejection with grounds of the findings that remain, the grounds go in the merge commit, and those findings are listed in the README like any other rejection |
| 3 | major | Invocation recording, disposition vocabulary and numbering contradict each other: dispositions are "nothing else" and then `"aborted, no verdict"` is required as a third; an omitted invocation is claimed to show as a numbering gap, which nothing enforces; and `round-07.md` consumes a round number while saying it is not a round | CONFIRMED | Fixed in three parts: an aborted invocation's entry records the task id and that no verdict was returned, which is the entry's status and not a finding disposition; the numbering is called a record rather than a guarantee, since nothing outside the repository enforces it; and a numbered entry that is not a review round is explicitly allowed, saying so on its first line — which is what `round-07.md` does |
| 4 | major | The collision-detecting suffix only handles collisions visible before the first file is written: two concurrent branches can create the same directory, renaming at merge may conflict with immutability, and the contract does not require the branch identity in the README, define "unrelated work", or handle renames and case/Unicode folding | CONFIRMED | Fixed: the slug is lowercased ASCII with everything outside `[a-z0-9._-]` replaced, which removes the case and Unicode classes; "already exists **in the merge target**" replaces "unrelated work"; the README must record the full branch name; the mapping is stated as deliberately non-injective with the recorded name as what disambiguates; and a collision found at merge is resolved by renaming the directory, which is stated not to be an edit to any entry |
| 5 | major | "Never edited after its round has passed" has no defined boundary, and the problem is material because an entry must carry a fix-commit SHA that cannot self-reference the commit creating it — leaving a builder to guess between an editable file, a delayed file, and a superseding record | CONFIRMED | Fixed at the root rather than by defining "passed": an entry is **immutable from the moment it is committed**, its disposition is "fixed" without a SHA, and the commit that carried each round's fixes lives in the mutable `README.md`. That is what this log already did in practice; the rule now says it |
| 6 | major | Decision 8 settled who may reject and the README visibility but not what constitutes adequate grounds, so a finding can be closed with any perfunctory reason. The eleven-item closure claim omitted part of item 8 | CONFIRMED | Fixed by defining grounds, which is builder work rather than a policy choice: a rejection says the finding is factually wrong, naming the source; out of scope, naming the scope **and the follow-up work it becomes**; or superseded, naming what supersedes it. Flagged for the maintainer to override if the definition is too narrow |
| 7 | minor | The planned-slice path still needs guesses: whether `.md` is removed, what counts as a date prefix, and which plan controls when a branch carries several | CONFIRMED | Fixed: `<slice>` is the plan's filename with a leading `YYYY-MM-DD-` and the `.md` removed, and the plans path applies only when the branch carries **exactly one** plan — otherwise the branch-slug form under `reviews/` is used |
| 8 | minor | Decision 7 still states the old merge obligation, inventory, paths and append behaviour in present-tense normative language immediately before the note claiming it "records the choice … rather than restating the contract" — one operative copy, but not one textual copy | CONFIRMED | Fixed in the note rather than by deleting locked text: the amendment now says the contract as stated there is superseded by rule 9 and **retained unedited as the record of what was decided rather than as instructions to follow**, and that rule 9 governs where they differ |
| 9 | minor | Several details stay builder-selectable, some deliberately (clean-round form), some not: verdict vocabulary, what counts as approving, whether partial findings from an aborted invocation survive, invocation identity in an aborted entry, numbering start and behaviour past `round-99`, when work counts as "started", and whether the README can supersede an entry's disposition | CONFIRMED | Partly fixed: numbering starts at 01, an aborted entry records its task id, and the README "records; it never changes a disposition". The rest are left open — the clean-round form by the maintainer's decision 11, and the remainder as genuinely small. Recorded rather than silently resolved |

Verified clean by the round, and reported as such: **the conversion lost nothing.** Rounds
1–5 differ from their `74c7122` sections only by the removed blank separator line, round 6
is byte-identical including EOF, all six finding tables hash identically row for row, and
no table row was edited. The old header's content is fully accounted for. Every README row
is correct — reviewed commits match their entries, every fix commit exists with the
reviewed commit as its parent, all six verdicts are "does not approve", and the finding
total is exactly 47 (3+5+7+12+9+11). The "two of four went against the recommendation"
claim is correct against round 6's final recommendations. The worked example's 24 backfilled
fix commits all exist with the corresponding reviewed revision as parent, and its round
tables were untouched. Decision 7's normative choice and counter-argument are byte-identical
to `main` by SHA-256 (`819c15b4…` and `665a3e29…`), the r16 evidence correction is accurate,
and amending it is defensible because the maintainer decided it and rounds 3–6 supplied the
new evidence rule 7 requires. `SKIP_RELPATHS` still covers the directory exactly as it
covered the file, so nothing became newly validated or newly missed. All four gates green.

### Terminal dispositions for the nine escalated rows

Rule 9 admits two dispositions and no third. These rows were escalations, every one of them
is now decided and implemented, and each is therefore **fixed in `b33296e`** — the commit
that landed the eleven decisions. None is rejected.

| Entry | Row | What it escalated | Now |
|---|---|---|---|
| round-01 | 3 | The never-rewrite clause, unratified | Decision 1: one file per round |
| round-02 | 5 | The `/` → `-` collision | Decision 2: slug plus collision-detecting suffix |
| round-03 | 3 | Durability under-specified without the clause | Decision 1, with the merge-strategy question answered by per-entry files |
| round-03 | 4 | The collision, re-raised at major | Decision 2 |
| round-03 | 7 | Whether the contract's surface should be consolidated | Decision 4: rule 9 operative, decision 7 points at it |
| round-04 | 5 | Must the terminal verdict approve | Decision 5, refined by this round's finding 2 |
| round-04 | 6 | What counts as a round | Decision 6, refined by this round's finding 3 |
| round-05 | 9 | Five operational details left to the builder | Decisions 8–11, with this round's findings 6, 7 and 9 completing them |
| round-06 | 11 | Guesses beyond the listed items | Decisions 9–11 and this round's finding 7 |
