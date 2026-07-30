# groundwork V1 — Slice 4.3: finish — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close V1. The `LICENSE` file lands (which is what restores the word "open source" to both identity lines), a security-and-privacy document and a versioned roadmap ship, `docs/known-limitations.md` is audited rather than rewritten, and the two V1 success criteria that are **not** currently discharged get discharged: the rule map binds CONTEXT.md's severities to the code that enforces them, and the generation protocol gets executed for the first time.

**Architecture:** Four new documents, one of them bound by a test; one canonical legal file fetched rather than typed; one discovery task that runs an artifact nobody has ever run; and an honesty pass that turns the README's Status from "nearly complete" into a ledger that names the one thing still undone. **`scripts/validate.py` is not modified.**

**Tech Stack:** Markdown, one canonical text file, stdlib `unittest`.

## Global Constraints

- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, `--diff main` must exit 0, and `python3 scripts/validate.py demo` must stay exactly `0 error(s), 2 warning(s)`. **Nothing in this slice should move any of them.** If one moves, a new document tripped a check — the document is wrong.
- **Test count moves up only,** from **702** (1 designed skip).
- **`scripts/validate.py` is not on the file list.** This is the closing slice; a validator change here is a change nobody has a slice left to review. Task 3's parsing lives in the **test**, using `validate._canonical_row`. If a task seems to need a validator edit, stop and report.
- **`AGENTS.md` stays under 200 lines.** It is at **164**.
- **`demo/` is a governed root and this slice does not touch it.** Task 2 *reads* `demo/interview/` and writes nothing there or anywhere under `demo/`.
- **The `LICENSE` text is fetched, never typed.** A canonical legal document reconstructed from memory is the one artifact in this repo where a paraphrase is a defect rather than a style choice. Task 1 pins its sha256.
- **Zero dependencies.** Stdlib only in shipped scripts; nothing shipped in this slice is a script.
- **`check_entropy` WARNs on 40+ character runs of `[A-Za-z0-9+/=_-]` at ≥ 4.0 bits, and `docs/` is scanned.** The roadmap and security documents will carry external URLs — keep them short, and there is a measurement step. (The canonical `LICENSE` text was measured during planning: **zero findings** from both `check_secrets` and `check_entropy`.)
- **This slice ends the build, so it is the last chance to overclaim.** "V1 is complete" is a claim, and it is only honest next to the thing nobody has done. Task 6 says it and names it in the same breath.
- **Pronouns:** they/them or the person's name.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 4.2 merged and pushed (`1ab4346`). Baseline verified at planning time: **702 tests OK (1 skip)**, `validate.py .` = `0 error(s), 7 warning(s)`, `--diff main` exit 0, `validate.py demo` = `0 error(s), 2 warning(s)`, `AGENTS.md` 164 lines, `README.md` 178 lines, `origin/main..main` = 0, working tree clean. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-4.3-finish
```

---

## The V1 success criteria, audited during planning

The spec lists five. Three are met and need nothing from this slice; two are not, and they are why this slice is bigger than three prose documents.

**1. "The adopter's required path runs end-to-end: `interview/` generates a `your-company/` in the demo-proven shape; `scripts/validate.py` passes on it; a provisioning guide exists."**
**PARTIALLY MET — and this is the most important finding of the audit.** The path *exists* (`interview/README.md`, `protocol.md`, `questions.md`, `generate.md`), its *output shape* is proven (`TestGeneratedCompanyRepo` materializes a company repo and validates it as its own root at zero ERRORs), and the guide exists (`delivery/README.md`). What has never happened is **an agent following `generate.md` from start to finish.** The test proves the destination validates; it does not prove the protocol gets you there. A protocol that has never been executed is the dead-path class this repo has named three times, at the top of the adopter's funnel. **Task 2 executes it, scoped, for the first time.**

**2. "`demo/` runs the 15-minute 3-query script with zero credentials, including the rung-5 governance block."**
**MET.** `demo/walkthrough.md` ships with the three queries, the expected-answer checklists, the rung-5 refusal at query 3, and its own honest-limits section (fictional company, unreliable auto-invocation, answers vary, instruction-strength not runtime). Nothing owed.

**3. "`scripts/validate.py` is Python-3-stdlib-only (zero third-party deps; self-checked), and every #5/#6/#7/#8/#16/#18/#21 ERROR/WARN rule fires where CONTEXT.md says it should."**
**FIRST HALF MET, SECOND HALF NEVER AUDITED.** `TestZeroDep` covers stdlib-only across every shipped `.py`, repo-wide. The second half has no artifact behind it: nothing in this repo maps CONTEXT.md's stated severities onto the functions that implement them, so the claim has been carried on 702 passing tests that were each written against one check rather than against the contract as a whole. **Task 3 builds the map and binds it in both directions.**

**4. "The README is honest at every stage: no capability claim precedes the capability; positioning concedes shared ground; prior art credits by name with paid/free stated straight."**
**MET, and 4.2 produced the evidence.** Codex raised "open source" as a claim outrunning its artifact, the builder initially declined, Codex re-raised with sources, and the builder conceded — the word came out of both identity lines pending the file. A bar that holds under a disagreement it lost is a bar. **Task 1 puts the word back, because the file arrives.**

**5. "Root files match §6: `AGENTS.md` canonical, one-line `CLAUDE.md` import, `.cursor/rules/` pointers; drift between them is a validator check."**
**MET AND EXCEEDED.** `check_root_files` enforces the `CLAUDE.md` import at ERROR level and the Cursor and Gemini pointers at WARN; 4.2 added `GEMINI.md`, which §6 did not ask for and the live contract required.

---

## Design calls flagged for the maintainer

**1. No `NOTICE` file ships, which departs from the wording of #3 — and the reason I first gave for it was weaker than the reason that actually decides it.**
#3 says the carve-out line goes in "the README/NOTICE." Only the README half ships. Two grounds, in order of strength:

- **Apache-2.0 §4(d) makes NOTICE contents propagate.** If the Work includes a NOTICE file, every derivative work must reproduce the attribution notices in it. A statement about the *adopter's own* `your-company/` content is meaningless to a downstream redistributor of the engine and would be forced on them anyway. NOTICE is an attribution instrument, and a scope carve-out is not an attribution.
- **A pristine `LICENSE` is diffable against `apache.org`.** A reader can confirm byte-for-byte what they are agreeing to. That is the same property this repo already spends effort on elsewhere — the version pin, the dated external facts — and modifying the canonical text spends it.

**The argument I initially reached for does not hold, and it is recorded because a plan that hides its own retracted reasoning teaches nothing.** I expected "appending text breaks GitHub's license detection." Fetched first-party (the `licensee` README via `gh api`, 2026-07-30): detection tries exact match after stripping whitespace and copyright notices, then falls back to **Sørensen–Dice similarity**, which is explicitly designed to tolerate "legally insignificant changes." Appending ~500 bytes to an 11,358-byte license is roughly a 4% change and would very likely still match. So detection is a *preference* for pristine, not proof — and the two grounds above stand without it. #14 independently ruled NOTICE out for its own candidate use, so this is the second ticket to land on the same answer from a different direction.

**2. The rule map is parsed in the test, not in `validate.py` — so the closing slice ships no validator change.**
The map needs a parser. Putting it in `validate.py` would mean a new check in the slice that has no successor to review it, and it would fire on any repo that happens to have a `docs/rule-map.md`. Putting it in the test keeps the binding exactly where it belongs: this repo's own CI, checking this repo's own claim about itself. The test imports `validate._canonical_row` — **the existing grammar**. A second table grammar in this repo is a decision nobody should make twice; the exec-view table cost 32 review rounds establishing that rule.

Honest cost: the map is checked only when this repo's suite runs, so an adopter cannot verify it. That is correct — it is a claim *about the engine*, and the engine is where it is checked.

**3. The map binds names and severities, and does NOT prove a severity is right.** The test proves every mapped check exists and every shipped check is mapped, so the map cannot silently fall out of date when a check is added or renamed. Whether ERROR is the *correct* level for a given rule is a judgment against CONTEXT.md, made once by hand in Task 3 and recorded per row. Saying so in the document is the difference between a coverage test and a correctness claim, and 3.2's lesson was exactly that a coverage test can pass while proving less than it appears to.

**4. Task 2's dry run is a test of the protocol's clarity, not of the demo's content — and its findings may legitimately edit `interview/generate.md`.**
Regenerating Umbercress from `demo/interview/` cannot validate the *content*: those layers were written from committed demo content, so any comparison is circular. What is not circular is whether an agent reading `generate.md` knows what to do. That has never been tested, and it is the only executable thing in the interview.

So `interview/generate.md` is on the file list **conditionally**, with a hard boundary: **clarifications only — wording, an added example, an ordering note. No new requirement, no new field, no new artifact.** If the dry run surfaces a *structural* gap (the protocol cannot produce something the manifest requires, or two instructions conflict), **stop and report it rather than redesigning the generator in the closing slice.** A structural finding becomes its own slice, and finding one is a success, not a failure.

**5. "V1 is complete" ships next to what nobody has done.** After this slice the README's Status has nothing left on its not-here-yet list, and the honest version of that sentence is not "V1 is complete." It is "V1 is complete, and here is the thing no one has done yet." Task 6 writes it that way. This is the last document in the build and the cheapest possible place to lose the property the whole thing was built on.

**Named cut line.** Two cuts, in order: **Task 2** (the dry run) becomes Slice **4.3b**, and after it **Task 3's test** (the map ships as prose, and known-limitations records that it is unbound). Cutting Task 2 changes Task 6: the "nobody has walked it" limitation still ships, but it may not claim a dry run was attempted. **Task 1 does not split** — the `LICENSE` file and the restoration of "open source" are one honesty unit, and shipping either alone is worse than shipping neither.

---

## File Structure

**Create (4 files):** `LICENSE`, `docs/rule-map.md`, `docs/security-and-privacy.md`, `docs/roadmap.md`

**Modify (4 files):** `README.md`, `AGENTS.md`, `docs/known-limitations.md`, `tests/test_validate.py`

**Conditionally modify (1 file):** `interview/generate.md` — clarifications only, and only from Task 2's findings. See design call 4.

---

## Task 1: The `LICENSE` file, and the word it makes true

**Files:** Create `LICENSE`. Modify `README.md`, `AGENTS.md`.

- [ ] **Step 1: Fetch the canonical text and verify it before it enters the repo.** Do not type it, do not let a model reproduce it, do not reformat it.

```bash
curl -sSL -o LICENSE https://www.apache.org/licenses/LICENSE-2.0.txt
wc -lc LICENSE
shasum -a 256 LICENSE
```

Expected, measured 2026-07-30: **202 lines, 11358 bytes**, sha256 `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.

If the sha differs, Apache has revised the served file. **Do not proceed on a mismatch** — record the new sha and the byte count in the commit message, confirm by eye that the header still reads `Apache License / Version 2.0, January 2004`, and say so explicitly rather than silently accepting a different file.

> The file ends with the `APPENDIX: How to apply the Apache License to your work` boilerplate carrying `[yyyy] [name of copyright owner]`. **Leave the brackets unfilled.** They are part of the canonical text; filling them in is a modification, and the copyright line has its own home in Step 3.

- [ ] **Step 2: Confirm it is inert to the gate.** Measured during planning against the real fetched text — both checks returned zero findings, and `iter_files` does pick up an extension-less `LICENSE`. Re-confirm, because a measurement nobody repeated is a memory:

```bash
python3 - <<'PY'
import sys
sys.path.insert(0, 'scripts')
import validate
text = open("LICENSE", encoding="utf-8").read()
print("bytes:", len(text.encode()))
print("secrets:", validate.check_secrets(text, "LICENSE"))
print("entropy:", validate.check_entropy(text, "LICENSE"))
seen = [p for p in validate.iter_files(".") if p.endswith("LICENSE")]
print("walker sees LICENSE:", bool(seen))
PY
python3 scripts/validate.py . ; echo "exit: $?"
```

Expected: `secrets: []`, `entropy: []`, `walker sees LICENSE: True`, and exactly `0 error(s), 7 warning(s)`.

- [ ] **Step 3: `README.md` — the identity line gets its word back, and the License section says who the Licensor is.** Line 5 currently opens `A harness-agnostic **Company OS**.` Restore:

```markdown
An open-source, harness-agnostic **Company OS**. It is files, not an engine: markdown
```

Then replace the whole `## License` section with:

```markdown
## License

[Apache-2.0](LICENSE) — chosen for its patent grant (enterprise-counsel comfort). The
`LICENSE` file is the canonical Apache text, unmodified, so you can diff it against
[apache.org](https://www.apache.org/licenses/LICENSE-2.0.txt) and see exactly what you are
agreeing to.

Copyright 2026 Sean Winslow.

**Your content is yours.** The operating system the interview generates is the adopter's
own work and is **not** covered by groundwork's license. That is not only a statement
here: [`interview/generate.md`](interview/generate.md) instructs the generator to write
the same carve-out into the company repository's own root instruction file, so the
repository holding your content is the one that says whose it is.

There is deliberately **no `NOTICE` file.** Under Apache-2.0 a NOTICE file's contents must
be reproduced by every derivative work, which makes it an attribution instrument — the
wrong home for a statement about the adopter's own content in a different repository. The
carve-out lives where the person it protects will read it.
```

- [ ] **Step 4: `AGENTS.md` — the same word, same reason.** Line 3 currently opens `**groundwork is a harness-agnostic Company OS.**` Restore:

```markdown
**groundwork is an open-source, harness-agnostic Company OS.** It is files, not an
```

- [ ] **Step 5: Gate + commit**

```bash
python3 scripts/validate.py . ; echo "exit: $?"
grep -n "open-source" README.md AGENTS.md
grep -rn "does not call groundwork open source\|until it does" README.md
```

Expected: exactly `0 error(s), 7 warning(s)` exit 0; both identity lines carry the word; **no hits** for the 4.2 placeholder wording — the sentence explaining that the word was waiting must be gone, not merely contradicted.

```bash
git add LICENSE README.md AGENTS.md
git commit -m "feat: the LICENSE file, and the word it makes true

The canonical Apache-2.0 text, fetched not typed, unmodified so a reader can
diff it against apache.org (202 lines, 11358 bytes, sha256 cfc7749b...).
'open source' returns to both identity lines because the file that grants it
now exists. No NOTICE file: under 4(d) its contents propagate to every
derivative work, which is the wrong instrument for a carve-out about the
adopter's own content in a different repository.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Execute the generation protocol — the first time anyone has

**Files:** Reads `interview/generate.md` and `demo/interview/`. Writes to a scratch directory outside the repo. Conditionally modifies `interview/generate.md` (clarifications only).

> This is the discovery task and it runs **second on purpose** — before the documents are written, so its findings can land in them. What is under test is the **protocol's clarity**, not the demo's content: the layers in `demo/interview/` were written from already-committed demo content, so any content comparison is circular. Whether an agent reading `generate.md` knows what to do is not circular, and it has never been checked.

- [ ] **Step 1: Read the four interview documents in order, as a first-time reader would.** `interview/README.md`, `protocol.md`, `questions.md`, `generate.md`. Take notes on anything you have to infer. **Do not read `demo/` first** — the point is to arrive at the demo's layers with only the protocol in hand.

- [ ] **Step 2: Set up a scratch target outside the repo.** Nothing this task produces is committed.

```bash
WORK=$(mktemp -d); echo "$WORK"
mkdir -p "$WORK/dryrun"
```

- [ ] **Step 3: Run the protocol's four preconditions against `demo/interview/` and record the verdict.** `generate.md` opens with four, all four every time. Check each and write down what you found — including that the demo's committed manifest is deliberately *not* complete (it models a second-pass turn in flight, which is why `TestGeneratedCompanyRepo` promotes its copy). **Precondition 1 should stop you.** That is the protocol working, and it is the first finding: a first-time reader following `generate.md` against the demo halts, correctly, and the plan for how to proceed anyway is a *fixture* decision recorded in a test rather than in the protocol.

Then proceed for the purpose of the dry run, treating the manifest as complete exactly the way the fixture does, and say so in the report.

- [ ] **Step 4: Generate ONE function, end to end, following only `generate.md`.** Pick **customer success** — it has an executive view, a deep record, a provisioned skill with an Owner's Card, a baseline memory record, and a constitution rule touching it, so it exercises the ordering rules, both exact-match obligations, and the human-only refusals in one function.

Write into `"$WORK/dryrun"` in the order `generate.md` specifies. Follow the document literally. Every time you have to make a decision the document does not make for you, **write it down** — that is the deliverable.

Then run the gate the protocol tells you to run:

```bash
python3 scripts/validate.py "$WORK/dryrun" 2>&1 | tail -20
```

> The dry-run repo is one function, so it will not be a complete company and may well emit findings. **That is not the result being measured.** Record what it says; the finding that matters is whether `generate.md` told you enough to produce a file the schema accepts.

- [ ] **Step 5: Write the report.** In the commit message and in your final summary, answer these five explicitly:

1. **Where did the protocol not tell you what to do?** Each spot, with the line you were reading.
2. **Which of the two exact-match obligations (the card's `owner` against the ontology's `accountable_owner`, and `source_of_truth` against `gate_source_of_truth`) did you get right without re-reading?** These are the ones `generate.md` says a reader will not notice and the validator will.
3. **Did the five human-only refusals actually stop you**, or did the surrounding prose make it feel reasonable to draft one?
4. **What did the gate say**, and was each finding explainable from the one-function scope rather than from a protocol defect?
5. **What would you change in `generate.md`, and is each change a clarification or a new requirement?**

- [ ] **Step 6: Apply clarifications only — and stop on anything structural.** For each item in answer 5 that is a **clarification** (wording, an added example, an ordering note that the document already implies), edit `interview/generate.md`. Quote the before and after in the commit message.

For anything that is a **new requirement, a new field, a new artifact, or two instructions in conflict**: **stop and report it.** Do not fix it. Design call 4 says why — a structural change to the generator in the closing slice has no successor slice to review it, and a clean report naming the gap is a better outcome than a rushed fix.

- [ ] **Step 7: Clean up and gate**

```bash
rm -rf "$WORK"
python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py . --diff main >/dev/null 2>&1 ; echo "diff exit: $?"
git status --short
```

Expected: green at 702; exactly `0 error(s), 7 warning(s)`; diff exit 0; **nothing under `demo/` or in the working tree except `interview/generate.md` if Step 6 edited it.**

- [ ] **Step 8: Commit** (skip if Step 6 made no edits, and say so in the final summary)

```bash
git add interview/generate.md
git commit -m "docs(interview): clarifications from the first execution of the protocol

The generation protocol had never been run. Generated the customer-success
function from demo/interview/ into a scratch repo following generate.md only,
and fixed what the document left to inference. Clarifications only; any
structural gap is reported, not patched.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: `docs/rule-map.md` and the test that binds it

**Files:** Create `docs/rule-map.md`. Modify `tests/test_validate.py`.

> Success criterion 3's second half. The map is one table with **exactly three columns**, parsed with `validate._canonical_row` — the existing grammar, reused, not reinvented.

- [ ] **Step 1: Create `docs/rule-map.md`.** The check names must be **plain text with no backticks** — `_canonical_row` rejects a cell containing `` ` ``, `<`, `>`, `|`, or `\`, which is also why no severity cell may contain `>=`.

```markdown
# The rule map — what each check enforces, and at what severity

CONTEXT.md says what every resolved decision requires. `scripts/validate.py` implements
it. This table is the join, and it exists because a V1 success criterion claims "every
rule fires where CONTEXT.md says it should" — a claim that was carried for the whole build
with no artifact behind it.

**What the test proves and what it does not.** `TestRuleMap` binds this table to the code
in both directions: every check named here exists in `validate.py`, and every check
`validate.py` ships appears here. So the map cannot fall silently out of date when a check
is added, renamed, or removed. It does **not** prove a severity is *correct* — that is a
judgment against CONTEXT.md, made by hand and recorded in the Severity column. A coverage
test that claimed more than this would be the vacuous-test trap wearing another hat.

**Reading the Severity column.** Several checks are thin per-instance loops that delegate
to a private body, so the severity given is the delegate's. ERROR fails the gate; WARN
prints and does not. Where a rule is strict only once a field backs a running agent, the
column says so — that is the machinery-follows doctrine, not an inconsistency.

| Enforces | Check | Severity |
|---|---|---|
| Secrets floor, every file, high-signal and not exhaustive (16) | check_secrets | ERROR |
| Entropy heuristic on long high-entropy runs (16) | check_entropy | WARN |
| Context-budget thresholds over a measured byte count (13) | check_context_budget | WARN near 20K est. tokens, ERROR near 50K |
| Referential integrity of relative markdown links (brief section 10) | check_links | ERROR |
| The Codex instruction chain against its silent 32 KiB truncation cap (13) | check_agents_chain | ERROR |
| The always-loaded aggregate, deduplicated as max across harnesses (13) | check_always_loaded_budget | WARN near 20K est. tokens, ERROR near 50K, via check_context_budget |
| The section 6 root-file set: the CLAUDE.md import, the Cursor and Gemini pointers | check_root_files | ERROR on CLAUDE.md drift, WARN on a missing Cursor or Gemini pointer |
| Machinery-follows fields on one acted-on activity's deep record (5) | check_deep_record | ERROR when a field backs a running agent, WARN on incomplete thinking |
| The canonical executive-view grammar and deep-record listing, per instance (5) | check_ontology | ERROR on the grammar, WARN on thinking quality |
| Card spine, track-2 trio, freshness, and the three drift checks, per instance (6) | check_owner_cards | ERROR at provisioning, WARN below it |
| Org-memory record shape, provenance, and supersession chains (7) | check_memory | ERROR on the spine and broken supersession, WARN on a missing or overdue review date |
| Typed rules, the no-rung-six safety invariant, orphan-prohibition, sunset (8) | check_constitution | ERROR on the safety spine, WARN on drafts and missing provenance |
| Resumable interview state: manifest pointer, frozen layers, one working file (9) | check_interview_state | ERROR on shape, WARN on an open-question contradiction |
| The action-class gate's registration as part of its own enforcement claim (8) | check_hooks | ERROR on a guard that cannot fire, WARN on an incomplete set |
| The version-skew gate and the pull promise (21) | check_version_pin | ERROR at a skew of one or more, WARN on reverse skew |
| What a pinned company root owes: a root AGENTS.md, a harness-visible skills path (10) | check_company_root | WARN |
| A symlinked content directory the stateless walker cannot enter | check_symlinked_dirs | WARN |
| Immutability between a memory record's base version and its new one (7) | check_memory_diff | ERROR |
| Proposal-file schema and three-bucket routing, per instance (17 and 18) | check_proposals | ERROR on schema and routing, WARN on incompleteness |
| The append-only governance changelog (17) | check_changelog | ERROR on a rewrite, WARN on a missing line |
| The synthetic-identifier allowlist, scoped to demo content only (16) | check_synthetic_identifiers | ERROR |
| The stateful memory pass under diff, driven by the base file list (7) | memory_diff_findings | ERROR |
| The frozen-layer guard under diff (9) | interview_diff_findings | ERROR |
| The blast-radius tripwire: declared against actual (18) | blast_radius_diff_findings | ERROR on a missing or mismatched proposal, WARN on a deletion |

## What is deliberately not in this table

- **The two pure cores behind the diff passes.** `classify_governed_change` and the
  private `_governed_class` decide what a change *is*; the rows above cover what the
  validator *emits*. Adding them would mix a classification with a finding.
- **Helpers and parsers.** `parse_frontmatter`, `parse_exec_table`, `iter_files`,
  `load_gitignore`, and `est_tokens` produce no findings of their own; the checks that
  call them carry the severity.
- **Anything CONTEXT.md requires that nothing enforces.** There is one, and it is
  recorded in [known-limitations.md](known-limitations.md) rather than here: the
  interview's health-metrics answer has no schema field, so it lands in prose and is the
  named first candidate for a v2 schema change.
```

- [ ] **Step 2: Add `TestRuleMap` to `tests/test_validate.py`.** The implemented set is discovered by **AST**, never listed — a hardcoded list is precisely how the next check goes unmapped.

```python
class TestRuleMap(unittest.TestCase):
    """docs/rule-map.md binds CONTEXT.md's rules to the code that enforces
    them, in BOTH directions. A prose map nothing checks is the artifact that
    rots: the next check added or renamed silently falsifies it. This is 3.2's
    question-bank coverage test pointed at the validator's own surface.

    Parsed with validate._canonical_row — the EXISTING grammar. A second table
    grammar in this repo is a decision nobody should make twice (the exec-view
    table cost 32 review rounds establishing that)."""

    MAP = REPO / "docs" / "rule-map.md"

    def _rows(self):
        rows = []
        text = self.MAP.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.split("\n"), 1):
            cells = validate._canonical_row(line)
            if cells is None:
                continue
            if cells[1] == "Check":                 # header
                continue
            if all(set(c) <= set("-: ") for c in cells):   # delimiter
                continue
            rows.append((cells, lineno))
        return rows

    def _implemented(self):
        tree = ast.parse((REPO / "scripts" / "validate.py").read_text())
        return {n.name for n in tree.body
                if isinstance(n, ast.FunctionDef)
                and (n.name.startswith("check_") or n.name.endswith("_findings"))}

    def test_the_map_actually_parsed(self):
        """An empty extractor satisfies every other assertion in this class."""
        rows = self._rows()
        self.assertGreater(len(rows), 20,
                           "docs/rule-map.md parsed %d rows — the table is not in "
                           "the canonical three-cell shape" % len(rows))

    def test_every_row_names_a_check_that_exists(self):
        implemented = self._implemented()
        for cells, lineno in self._rows():
            self.assertIn(cells[1], implemented,
                          "docs/rule-map.md:%d names %r, which validate.py does "
                          "not define" % (lineno, cells[1]))

    def test_every_shipped_check_is_mapped(self):
        named = {cells[1] for cells, _ln in self._rows()}
        missing = sorted(self._implemented() - named)
        self.assertEqual(missing, [],
                         "these checks ship with no row in docs/rule-map.md: %s "
                         "— add a row or explain the omission in the document's "
                         "'not in this table' section" % missing)

    def test_every_row_declares_a_severity(self):
        for cells, lineno in self._rows():
            self.assertTrue("ERROR" in cells[2] or "WARN" in cells[2],
                            "docs/rule-map.md:%d declares no severity" % lineno)

    def test_one_table_only(self):
        """Two tables would make the row set depend on which one a reader means."""
        text = self.MAP.read_text(encoding="utf-8")
        headers = [ln for ln in text.split("\n")
                   if (validate._canonical_row(ln) or ["", "", ""])[1] == "Check"]
        self.assertEqual(len(headers), 1,
                         "docs/rule-map.md has %d canonical tables; it must have "
                         "exactly one" % len(headers))
```

- [ ] **Step 3: Verify every severity by hand against the code.** This is the audit half, and the test cannot do it. For each of the 24 rows, open the named function (and its `_check_*_instance` delegate where it has one) and confirm the Severity cell matches what it emits and what CONTEXT.md asks for. Correct the **document** where they disagree.

If a row's implemented severity genuinely contradicts CONTEXT.md, **do not change the code.** Record it as a finding in the commit message and add it to `docs/known-limitations.md` in Task 5. A severity mismatch found in the closing slice is a v1.5 item, not a same-day fix.

```bash
python3 - <<'PY'
import ast, pathlib
tree = ast.parse(pathlib.Path("scripts/validate.py").read_text())
for n in tree.body:
    if not isinstance(n, ast.FunctionDef):
        continue
    if not (n.name.startswith("check_") or n.name.endswith("_findings")):
        continue
    levels = sorted({c.value for c in ast.walk(n)
                     if isinstance(c, ast.Constant) and c.value in ("ERROR", "WARN")})
    print("%-30s emits: %s" % (n.name, "/".join(levels) or "(delegates)"))
PY
```

> A `(delegates)` result is expected for the per-instance loops and for `check_always_loaded_budget`; go read the delegate. **Do not record "(delegates)" as a severity** — a wrapper that emits nothing itself is not a check that finds nothing.

- [ ] **Step 4: Prove the binding is load-bearing** (three deliberate reds, all reverted). The map is a `.md` file so no bytecode can survive, but `PYTHONDONTWRITEBYTECODE=1` is set anyway.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import subprocess, sys, pathlib
m = pathlib.Path("docs/rule-map.md")
orig = m.read_text()
runs = []

def run():
    return subprocess.run([sys.executable, "-m", "unittest",
                           "tests.test_validate.TestRuleMap"],
                          capture_output=True, text=True)

# (a) a row naming a check that does not exist must fail
m.write_text(orig.replace("| check_secrets |", "| check_nonexistent |", 1))
runs.append(("bogus check name", run().returncode != 0))

# (b) dropping a row for a shipped check must fail
lines = [ln for ln in orig.split("\n") if "| check_secrets |" not in ln]
m.write_text("\n".join(lines))
runs.append(("dropped row", run().returncode != 0))

# (c) indenting a row takes it out of the canonical shape; the row-count
#     floor is what catches wholesale non-parsing
m.write_text("\n".join("    " + ln if ln.startswith("| check_") else ln
                       for ln in orig.split("\n")))
runs.append(("table not parsing", run().returncode != 0))

m.write_text(orig)
assert run().returncode == 0, "the map does not pass after restore"
for name, caught in runs:
    print(("OK  " if caught else "MISS") + "  " + name)
assert all(c for _n, c in runs), runs
PY
```

Expected: three `OK` lines and a clean restore.

- [ ] **Step 5: Gate + commit**

```bash
python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"
python3 scripts/validate.py . ; echo "exit: $?"
```

Expected: green above 702; exactly `0 error(s), 7 warning(s)`.

```bash
git add docs/rule-map.md tests/test_validate.py
git commit -m "docs+test: the rule map, bound to the code in both directions

V1 success criterion 3's second half had no artifact behind it. 24 rows join
CONTEXT.md's rules to the checks that enforce them; TestRuleMap proves every
mapped check exists and every shipped check is mapped, discovering the
implemented set by AST so the next check cannot go unmapped. Severities were
verified by hand against each function and its per-instance delegate — the
test binds names, not correctness, and the document says so.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: `docs/security-and-privacy.md`

**Files:** Create `docs/security-and-privacy.md`.

> **Different audience from `known-limitations.md`, which is why it is a second document rather than a section.** Known-limitations is engineer-facing: what each check does not do. This is adopter- and counsel-facing: what a company OS in a git repo exposes, who can reach it, and what the maintainer must do. It **points at** known-limitations for mechanism rather than restating it — the same two-surfaces discipline #14 and #15 use.

- [ ] **Step 1: Create the file:**

`````markdown
# Security and privacy

Who this is for: the person deciding whether to put their company's operating rules in a
git repository, and whoever has to sign off on that. It describes what groundwork exposes,
what it cannot protect, and the three things a maintainer has to get right.

For the mechanics of what each individual check does and does not catch, read
[known-limitations.md](known-limitations.md). This page is the shape of the risk, not the
list of gaps.

## The shape of the thing

groundwork is markdown files in a private git repository, read by coding agents, maintained
by one person who has the commit bit. There is no server, no database, no hosted component,
and no account. That removes whole categories of risk — there is no service to breach, no
tenancy to escape, no session to hijack — and concentrates what is left into two places:
**your git host** and **the machines your agents run on**.

Everything groundwork ships that executes is three Python files: the validator, the
action-class hook, and the demo's rung-3 reminder. All three are Python 3 standard library
only, take input and print output, and **make no network calls** — the stdlib allowlist in
`TestZeroDep` does not contain `urllib`, `socket`, `http`, or any client library, so a
shipped script that reached the network would fail this repository's own test suite. There
is no telemetry, no update check, and nothing that phones home.

## The one failure that is silent, and it is a privacy failure

If you distribute your skills as an organization plugin, **the plugin source must be a
subdirectory, never the repository root.** A manifest entry pointing at the root packages
the whole company repo — including your interview transcript, your organizational memory,
and your constitution — and ships it to every employee who installs it.

It is silent: nothing breaks, no error appears, the plugin works. And pointing the
marketplace at the repository you already have is the obvious first move, which makes this
the single most likely serious mistake available. [`delivery/README.md`](../delivery/README.md)
states it as a hard rule with the reason attached. **No check can enforce it** — the
manifest lives in a dot-directory the validator never scans, and that limit is recorded
rather than papered over.

## What is in the repository, most sensitive first

1. **`interview/` — the interview transcript.** The most sensitive thing in a company OS,
   and the easiest to underestimate. It records how the company actually works, including
   what people said about what is broken and who owns what. Treat it the way you would
   treat leadership meeting notes, because that is roughly what it is.
2. **`memory/` — organizational memory.** Named people, dates, decisions, contract values,
   and captured baselines. Records are append-and-supersede, so nothing is ever edited
   away — see the erasure tension below.
3. **`governance/constitution/` — the rules.** Each rule names an owner and an appeal
   path, so it is a map of who decides what.
4. **`ontologies/` and `skills/` — the work map.** Process and role detail, plus each
   agent's owner, forbidden actions, and death conditions.

All four are why the two-repo model exists: the public groundwork clone is an engine and
nothing organizational is ever written into it.

## Who can reach it

**One git-capable maintainer.** That is the access model, stated plainly rather than as a
limitation: employees do not get the repository. They receive skills through organization
provisioning and propose changes in conversation; the maintainer commits.

The consequence is that **your repository's access control is your git host's** — branch
protection, org membership, SSO, and audit log are the git host's features, not
groundwork's. Organization plugin distribution adds a second surface with its own
requirements (Team or Enterprise plan, Cowork and Skills enabled, Owners only), documented
with its verification date in [`delivery/README.md`](../delivery/README.md).

## Secrets

A company OS should contain no credentials, and the validator enforces a floor rather than
a guarantee: a curated set of high-signal patterns plus an entropy heuristic, ERROR-level,
running over all content. It is **not** exhaustive.

**Use [Gitleaks](https://github.com/gitleaks/gitleaks) as the real backstop**, in CI or as
a pre-commit hook. That is not a hedge — it is the documented design, because a
zero-dependency stdlib scanner cannot compete with a maintained rule set, and pretending
otherwise would be the more dangerous claim. Two scope facts worth knowing: `.gitignore`
matching is minimal (exact names and simple globs), and this repository's own gate skips
`tests/` and `docs/superpowers/` because the validator's fixtures necessarily quote
example secret patterns.

## What the validator cannot prove

Three limits matter more than the rest, and none of them is a bug:

- **It cannot prove a human reviewed anything.** The consent gate is a tripwire: it can
  demand that an escalating change carry a matching proposal, and it cannot tell whether
  anyone read it. The real enforcement is the commit bit — only the maintainer can land a
  change. That is a permissions convention, not a cryptographic proof.
- **It cannot read prose for truth.** Every required field can be answered, correctly
  shaped, and wrong. The validator checks that the answer exists; a person checks that it
  is true.
- **It cannot prove your demo or your records are free of real names.** Structured
  identifiers — emails, domains, phones, addresses — are mechanically checked against a
  declared allowlist in demo content. A real person named in free prose looks exactly like
  a fictional one.

## Personal data, and an honest tension

Organizational memory names people. Records carry an owner, a provenance label, and a
date, and a superseded record stays readable rather than being deleted — that is the whole
point of the schema, and it is what makes "why do we do it this way" answerable.

**It is also in tension with an erasure request**, and V1 does not resolve it. Git history
means that even deleting a file leaves the content reachable; a real erasure is a
history-rewriting operation on the repository. groundwork ships no runbook for that in V1.
The compliance pack — a consent registry, CODEOWNERS on sensitive generated folders, a
Gitleaks profile, an erasure runbook, and a data-protection impact template — is
documented on the [roadmap](roadmap.md) and **not built**. If personal-data handling is a
gating requirement for you, that is the honest answer today.

Two things you can do now, neither of which groundwork implements for you: keep
performance and assessment content out of organizational memory (the demo's
performance-review rule models exactly this boundary), and decide deliberately whether
your interview transcript is retained — nothing in the validator requires an `interview/`
directory to exist, and the demo retains its own as a disposition rather than a rule.

## Reporting something

groundwork is files, so the realistic vulnerability surface is small: the three scripts,
and any instruction in a shipped document that would lead an agent to do something unsafe.
If you find either, open an issue on the repository. There is no embargo process and no
security mailing list, and saying so is more useful than implying one exists.
`````

- [ ] **Step 2: Gate.** Every relative link must resolve — `known-limitations.md`, `roadmap.md` (created in Task 5, so **this step is a deliberate red until Task 5 lands**), and `../delivery/README.md`.

> **Named deliberate red.** `python3 scripts/validate.py .` will report a broken relative link to `roadmap.md` between Task 4 and Task 5. That is expected and is the reason the two tasks are adjacent. If you need a green intermediate commit, do Task 5 first — the two have no other dependency.

```bash
python3 scripts/validate.py . 2>&1 | tail -3
```

- [ ] **Step 3: Commit** (after Task 5, or immediately if you reordered)

```bash
git add docs/security-and-privacy.md
git commit -m "docs: security and privacy, for the person who has to sign off

Adopter- and counsel-facing, pointing at known-limitations for mechanism
rather than restating it. Leads with the one silent failure (a plugin source
that is not a subdirectory ships the interview transcript), states the no
network claim with the test that backs it, and records the erasure tension
with append-and-supersede memory rather than resolving it.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: `docs/roadmap.md`

**Files:** Create `docs/roadmap.md`.

> Drawn from the spec's locked scope boundaries. **This is the most staleness-prone document in the repository**, so it carries a review date and one rule about itself.

- [ ] **Step 1: Create the file:**

`````markdown
# Roadmap

**Last reviewed 2026-07-30.** Nothing below V1 is described in the present tense, and
nothing moves onto the shipped list until it is. That rule is the same one the README has
run on since the first commit: no capability claim precedes the capability.

## V1 — shipped

The adoptable core: the two-tier ontology schema, work packages with Owner's Cards, the
compiled constitution on a five-rung enforcement ladder, organizational memory with
provenance and supersession, the consent gate and its blast-radius tripwire, the version
pin and the pull promise, the interview and generation protocols, the `demo/` company with
its fifteen-minute walkthrough, the provisioning guide, and the zero-dependency validator
that gates all of it.

One thing on this list has never been done by anyone: **the generation protocol has been
executed once, in a scoped dry run by the team that wrote it, and never by an adopter on a
real company.** [known-limitations.md](known-limitations.md) says so where it counts.

## V1.5 — hardening, no schema change

Small, and none of it is promised by a date.

- **Gate on git-tracked content** rather than on a walker plus a minimal `.gitignore`
  reader. Cleaner scope than the current model and it retires two known limitations.
- **`SPDX-License-Identifier` headers** on the three shipped scripts. Deferred from V1
  deliberately: worth adding once, on purpose, rather than as a side effect of a
  documentation slice.
- **Changelog rotation.** The append-only check compares against the full base file, so a
  long-lived changelog has no supported way to be archived.
- **Any severity mismatch** the rule map's hand audit turned up. There is no code fix in a
  closing slice; there is a recorded row and a later pass.

## V2 — documented, not built

Each of these is designed far enough to be described and deliberately absent from V1. The
first one is the only one with a schema cost.

- **The first `SCHEMA_VERSION` bump, and its named first passenger:** a health-metrics
  field. The interview already asks what must not degrade while a standard is met — the
  Goodhart guard — and there is nowhere typed to put the answer, so it lands in prose. A
  new required field is a v2 change with a migration note, and the pull promise has been
  binding since 2026-07-29.
- **Per-check `since:` tags** and scatter-suppression, which is the other half of the
  version-skew policy. Dormant at v1 by construction; wired at the first real bump.
- **The Classify, Consent, Enforce compliance pack:** a consent registry with approved and
  forbidden uses and expiry, CODEOWNERS on sensitive generated folders, a Gitleaks
  profile, an erasure runbook, and a data-protection impact template.
- **Cowork plugin packaging and the GitHub-synced marketplace as a walkthrough** rather
  than as documented steps a maintainer runs by hand.
- **Runnable learning-loop skills** — session-to-skill extraction and an
  improvement-proposal skill — plus generated rung-3 reminders rather than one hand-written
  exemplar.
- **The morning-briefing pattern** and a truth-layer schema.
- **Governed autonomous application:** today an agent proposes and a human lands. The
  question V2 asks is which changes an agent may apply under a rule that a human wrote,
  with the consent record still intact.
- **Cross-harness runtime-enforcement parity.** Hooks are Claude-Code-only; everywhere
  else the action-class rule degrades to an instruction. Closing that means building on
  each harness's own enforcement surface, where one exists.

## V3 — further out

- **Re-interview and drift.** Merging a new interview pass against retained state, which
  is what the frozen-layer format was built to make possible.
- **Per-function deepening** past the first three-to-five acted-on activities.
- **An adoption scoreboard** measured as coordination tax removed rather than as usage.
- **An evaluations and traces recipe** for skills that actually run.

## Never

Not "not yet" — these are commitments, and they are what keeps everything above cheap.

- **No hosted anything.** No server, no dashboard, no per-seat features, no account.
- **No agent runtime.** The harness is the runtime.
- **No memory or retrieval engine.** groundwork owns what an organization should remember,
  with what provenance, owned by whom — not how it is indexed or recalled.
- **No third-party dependencies** in shipped scripts. There is no `requirements.txt` and
  there will not be.

## How this document stays honest

Two mechanisms, both cheap. It carries the date it was last reviewed, so a reader can see
how stale it is rather than guessing. And an item may only move to the shipped list in the
same change that ships it — the same rule that kept the word "open source" out of the
README until the `LICENSE` file existed.
`````

- [ ] **Step 2: Gate**

```bash
python3 scripts/validate.py . ; echo "exit: $?"
python3 - <<'PY'
import sys
sys.path.insert(0, 'scripts')
import validate
hits = [(f.level, f.path, f.message[:90]) for f in validate.validate('.')
        if f.path.startswith('docs/roadmap') or f.path.startswith('docs/security')]
print(hits or "clean")
PY
```

Expected: exactly `0 error(s), 7 warning(s)` exit 0 (both new documents now present, so Task 4's deliberate red is closed), and `clean`.

- [ ] **Step 3: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs: a versioned roadmap, with a Never list and a review date

V1 shipped, V1.5 hardening, V2 documented-not-built with the health-metrics
field named as the first schema bump's passenger, V3, and four commitments
that are not 'not yet'. Carries the date it was last reviewed and one rule
about itself: an item moves to shipped only in the change that ships it.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 6: The audit, the status, and the verdict

**Files:** Modify `docs/known-limitations.md`, `README.md`, `AGENTS.md`.

- [ ] **Step 1: Audit `docs/known-limitations.md` rather than rewriting it.** It is 296 lines across nine sections and it is substantially right. Walk every section and confirm each bullet is still true after 4.2 and this slice. Specifically re-read: the `## Validator` section against the rule map you just built, `## Context budget (13)` against the four root pointers, `## Generation (10)` against Task 2's dry run, and `## Provisioning` against the security document. **Change only what is false.** Report what you checked and what you changed; "audited, no changes needed in section X" is a real and useful result.

- [ ] **Step 2: Add the new limitations this slice creates.** Append each to the section it belongs in.

To `## Generation (#10)`:

```markdown
- **The generation protocol has been executed once, by the people who wrote it.** A scoped
  dry run generated one function from `demo/interview/`'s committed layers into a scratch
  repository, following `interview/generate.md` only, to find out where the protocol left
  decisions to inference. That tests the document's clarity. It does not test the thing an
  adopter cares about: **no interview has ever been run on a real company, and no company
  OS has ever been generated from real answers.** The output *shape* is proven by a test
  that materializes a company repo and validates it as its own root; the *transcription
  from real answers* is proven by nothing. Walking that path for real is the first honest
  post-V1 act, not a V1 claim.
```

To `## Validator`:

```markdown
- **The rule map binds names, not correctness.** [rule-map.md](rule-map.md) joins
  CONTEXT.md's rules to the checks that implement them, and `TestRuleMap` proves the join
  stays complete in both directions — a check cannot be added, renamed, or removed without
  the map failing. It does **not** prove that a given severity is the *right* one. Those
  were verified by hand once, during Slice 4.3, and a future disagreement about a severity
  is a judgment call against CONTEXT.md rather than something the suite will catch.
```

To the `## Validator` section, or wherever the licensing discussion best sits:

```markdown
- **There is no `NOTICE` file, and that is deliberate.** Under Apache-2.0 a NOTICE file's
  contents must be reproduced by every derivative work, which makes it an attribution
  instrument. The `your-company/` carve-out is a statement about the adopter's own content
  in a different repository, so propagating it to downstream redistributors of the engine
  would be both meaningless and confusing. The carve-out lives in the README and in the
  root instruction file the generator writes into the company repo. Ticket #3's wording
  said "README/NOTICE"; only the README half ships, and this is the record of why.
```

Plus any severity mismatch Task 3 Step 3 surfaced, and any structural gap Task 2 Step 6
reported instead of fixing. **If either list is empty, say so explicitly in the commit
message** — an unstated absence reads as an unchecked one.

- [ ] **Step 3: `README.md` — the Status section becomes a completed ledger that names what is undone.** Replace the whole `## Status` section:

```markdown
## Status

**V1 is complete.** Everything this page describes is in the repository, and
`scripts/validate.py` gates all of it: the schema as files; eight function ontologies plus
worked deep records on both governance tracks, including one recording a deliberate
decision *not* to automate; work packages with Owner's Cards; a typed constitution on a
five-rung enforcement ladder, with one runnable exemplar and prose degradation everywhere
else; organizational memory with provenance and supersession; the consent gate and its
blast-radius tripwire; the interview and generation protocols; the `demo/` company and its
walkthrough; the provisioning guide; and the licence, security, and roadmap documents.

**And here is the thing nobody has done.** No interview has been run on a real company, so
no company OS has been generated from real answers. What is proven is the destination — a
test builds a company repo in the shape the manifest specifies and validates it as its own
root — plus one scoped dry run of the generation protocol against the demo's own layers.
The path from a real conversation to a real repository has been designed, documented, and
gated, and not yet walked. If you walk it, the thing we most want to hear about is where
the protocol left you guessing.

[`docs/roadmap.md`](docs/roadmap.md) is what comes next and what never will.
[`docs/known-limitations.md`](docs/known-limitations.md) is what this does not do.
[`docs/security-and-privacy.md`](docs/security-and-privacy.md) is what it exposes.
[`docs/rule-map.md`](docs/rule-map.md) is every check and the severity it fires at.
[`CONTEXT.md`](CONTEXT.md) is the glossary of all nineteen resolved design decisions.
```

- [ ] **Step 4: `AGENTS.md` — the status paragraph and the map table.** The status paragraph becomes:

```markdown
The design is fully charted (19 resolved decisions; see `CONTEXT.md`). **V1 is complete:**
the schema exists as files, three functions are worked end to end across both governance
tracks, one function records a deliberate non-automation verdict, the interview and its
generator exist as documents, `demo/` is a complete governed company, `delivery/` covers
provisioning, and the validator gates every layer of it. The one thing nobody has done is
run the interview on a real company — see `docs/known-limitations.md`.
```

Then delete the whole **"Not built yet"** section — after this slice there is nothing in it — and add the three new documents to the map table:

```markdown
| `docs/rule-map.md` | Every check, what it enforces, and the severity it fires at. |
| `docs/roadmap.md` | V1, V1.5, V2, V3, and the four things groundwork will never do. |
| `docs/security-and-privacy.md` | What a company OS in a git repo exposes, and who can reach it. |
```

> **`wc -l AGENTS.md` must stay under 200.** It is at 164; deleting a section and adding three rows is roughly net-neutral.

- [ ] **Step 5: The final gate, and the sweep**

```bash
python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py . --diff main >/dev/null 2>&1 ; echo "diff exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -3
wc -l AGENTS.md README.md
```

Expected: green above 702; exactly `0 error(s), 7 warning(s)` exit 0; diff exit 0; `demo` at exactly `0 error(s), 2 warning(s)`; `AGENTS.md` under 200.

Then the cross-file honesty sweep — the failure this repo has shipped four times:

```bash
grep -rn "not built yet\|nearly complete\|lands with the first release\|will ship with\|Not here yet\|Phase 4.3" \
  --include="*.md" . | grep -v "^./docs/superpowers" | grep -v "^./research"
```

Expected: **no hits.** Every one of those phrases described something this slice shipped.

And the reverse sweep — nothing may claim V1 is complete while a not-built list survives:

```bash
grep -rn "Not built yet" AGENTS.md README.md ; echo "expect no output"
```

- [ ] **Step 6: The V1 success-criteria verdict.** Walk the five criteria at the bottom of `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md` one at a time and state, in your final summary and in the commit message, whether each is met and what the evidence is. The plan's audit section above gives the four settled verdicts and their evidence; you owe fresh verdicts on the two this slice touched:

- **Criterion 1** — now supported by the dry run *plus* the recorded limitation. Say plainly which half is proven by a test, which by a dry run, and which by nothing.
- **Criterion 3** — now supported by `docs/rule-map.md` and `TestRuleMap`. Say how many rows, how many checks the AST found, and whether any severity disagreed with CONTEXT.md.

**Do not edit the spec.** The Build log is the planner's surface and gets the verdict after merge.

- [ ] **Step 7: Commit**

```bash
git add docs/known-limitations.md README.md AGENTS.md
git commit -m "docs: V1 is complete, and the README names what nobody has done

known-limitations audited section by section rather than rewritten, plus the
three limitations this slice creates: the protocol has been executed once by
its authors and never on a real company, the rule map binds names and not
correctness, and there is deliberately no NOTICE file. AGENTS.md loses its
'Not built yet' section because nothing is in it. The README's Status says
V1 is complete in the same breath as the path nobody has walked.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No `scripts/validate.py` change.** Design call 2. A validator edit in the closing slice has no successor slice to review it, and Task 3's parsing lives in the test where the claim belongs.
- **No `NOTICE` file.** Design call 1, which departs from #3's wording and records why.
- **No SPDX headers.** V1.5 on the roadmap: worth adding once, deliberately, not as a side effect of a documentation slice.
- **No structural change to `interview/generate.md`.** Clarifications only, from Task 2, with a hard stop-and-report boundary on anything more.
- **No real interview.** Task 2 is a scoped dry run against the demo's own layers, and the limitation it cannot discharge is written down rather than absorbed.
- **No `demo/` changes.** Governed root; Task 2 reads it and writes nothing.
- **Still open for the maintainer:** Codex's 3.1 finding 1 (should an absent `layers:` key ERROR); the health-metrics v2 candidate (now on the roadmap as the first bump's named passenger); the 3.3 hook-set call; three Slice 1.5d-ii deferrals; the `SKIP_RELPATHS` sign-off; the standing re-review rule; the `Motion: assist` reading; #21's `since:` retrofit; whether groundwork dogfoods its own hook set. **None blocks V1**, and the roadmap is now the durable home for the ones that are really scope rather than judgment.

## Self-Review

- **Ticket and criteria coverage.** #3 gets its `LICENSE` file, its carve-out home, and a recorded departure on NOTICE. The spec's 4.3 line asks for a security-and-privacy section, a versioned roadmap, and the `LICENSE` — all three ship. The success-criteria audit is not deferred to the builder as a chore: it is done in this plan with evidence, which is how the two undischarged criteria were found and turned into Tasks 2 and 3.
- **The audit changed the slice, which is what an audit is for.** Three prose documents plus a licence would have closed 4.3 on schedule and left two of five success criteria resting on assertion. Criterion 1's gap in particular — *the generation protocol has never been executed* — is the dead-path class this build has named three times, sitting at the top of the adopter's funnel and invisible because the *output* is well tested.
- **Two external contracts fetched live 2026-07-30, and one of them refuted my own argument.** The canonical Apache text was fetched and pinned by sha (202 lines, 11,358 bytes, `cfc7749b…`) and **measured** against `check_secrets` and `check_entropy` with zero findings, so the plan states an inert-to-the-gate fact rather than hoping for one. The `licensee` README (via `gh api`, first-party) then showed that appending text would probably *not* break GitHub's license detection, because matching falls back to Sørensen–Dice similarity — so the detection argument is recorded at its honest strength as a preference, and the decision rests on §4(d) propagation and on a canonical text staying diffable. **A plan that hides its own retracted reasoning teaches nothing**, which is why the retraction is in design call 1 rather than quietly dropped.
- **The one search-summary source is quarantined.** GitHub's own licensing docs 404'd at the URL I tried, and the fallback was a search summary. Nothing from it is quoted in any shipped artifact — 3.2's rule — and the first-party `licensee` README is what the design call actually cites.
- **Anti-hollow probes, and the absence-assertions are paired.** Task 3 ships three deliberate reds on the same file — a row naming a nonexistent check must fail, a dropped row must fail, and an indented (non-parsing) table must fail — plus `test_the_map_actually_parsed`, which exists precisely because an empty extractor satisfies every other assertion in the class. That is the 2.3b lesson: a scanner's two failure surfaces are what it allows and what it *sees*, and the row-count floor is the only assertion an empty parse cannot satisfy. Task 1 re-measures the licence against the gate rather than trusting the planning measurement.
- **The implemented set is discovered by AST, never listed.** A hardcoded check list is exactly how the next check goes unmapped, and the failure would be silent — the map would still pass while describing an older validator.
- **No second table grammar.** `_canonical_row` is reused for a third consumer (exec views, the question bank, now the rule map). The exec-view table cost 32 review rounds establishing that rule and the plan cites it at the point of temptation.
- **A deliberate red is named before it happens.** Task 4 links `roadmap.md` before Task 5 creates it, so `validate.py` will report one broken link between the two tasks. Named, with the reorder that avoids it — because a designed intermediate failure that is not flagged reads as a mistake.
- **`demo` and the 7-WARN invariant are tripwires in every task**, and the plan says what a movement would mean rather than only that it must not happen.
- **The closing honesty move is structural, not rhetorical.** "V1 is complete" appears in exactly two places and in both of them the very next sentence names the path nobody has walked, with an invitation to report where it breaks. `AGENTS.md`'s "Not built yet" section is *deleted* rather than emptied, and a reverse grep asserts no file claims completeness while a not-built list survives. The README also asks the reader for the one thing the project cannot generate for itself — a first real walk — which is the honest ending for a build whose whole discipline was refusing to claim it early.
- **Placeholder scan:** no TBD/TODO. All four documents are given in full, the test class is given in full, every prose modification quotes its replacement text, and the one fetched artifact is pinned by sha with an explicit instruction not to proceed on a mismatch.
- **Type consistency:** no function signature changes anywhere; `Finding`, `_canonical_row`, `iter_files`, `check_secrets`, and `check_entropy` are called, not modified.
