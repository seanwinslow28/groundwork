# groundwork V1 — D2 Move 2: product root files + the #13 context-budget gate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cross the Phase 1→2 boundary. Author the product **`AGENTS.md`** (navigation + honest status + authoring standard), collapse **`CLAUDE.md`** to the one-line `@AGENTS.md` import, add the **`.cursor/rules/*.mdc`** pointer, and land the deferred **#13** context-budget work: the **AGENTS.md-chain >32 KiB hard ERROR** plus a correctly-scoped always-loaded aggregate — and a **root-file drift check** so the three root files can never become three sources of truth.

**Architecture:** Three root files, one canonical. `AGENTS.md` holds the content; `CLAUDE.md` is a one-line `@AGENTS.md` import (Claude Code reads `CLAUDE.md`, *not* `AGENTS.md`); `.cursor/rules/groundwork.mdc` is an always-apply pointer. Four validator additions govern that shape: `check_agents_chain` (Codex's 32 KiB truncation cap), `check_always_loaded_budget` (#13's aggregate, replacing today's mis-scoped per-file application), and `check_root_files` (the drift check). `docs/agents/build-sessions.md` keeps the workbench rules and does **not** ship into the always-loaded surface.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

---

## Live-contract findings (fetched 2026-07-27 — these decide the code; do not code from memory)

Every external behavior below was fetched from the vendor's own docs today. Where the plan's code encodes a number or a rule, this is its source.

| Contract | Verified wording | What it forces in the code |
|---|---|---|
| **Claude Code reads `CLAUDE.md`, not `AGENTS.md`** | "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md`… create a `CLAUDE.md` that imports it" — and it shows exactly `@AGENTS.md` as the file's content, plus `ln -s AGENTS.md CLAUDE.md` as an alternative | The drift check accepts **either** the `@AGENTS.md` import **or** a symlink resolving to `AGENTS.md`; anything else is ERROR |
| **Import syntax** | "`@path/to/import` syntax… Both relative and absolute paths are allowed. Relative paths resolve relative to the file containing the import… a maximum depth of four hops" and "Import parsing skips Markdown code spans and fenced code blocks" | `_strip_code()` before matching imports; `CLAUDE_IMPORT_MAX_DEPTH = 4`; relative resolution against the *importing file* |
| **Imports do not save context** | "Splitting into `@path` imports helps organization but doesn't reduce context, since imported files load at launch" | The aggregate must **follow** imports and count them, not stop at `CLAUDE.md` |
| **Codex chain order + cap** | "Codex concatenates files from the root down, joining them with blank lines" and "Codex skips empty files and **stops adding files once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)**" | Chain total = `sum(sizes) + 2*(n-1)`; empty files skipped; `AGENTS_CHAIN_MAX_BYTES = 32*1024`; over-cap is **ERROR** (silent truncation = data loss, openai/codex#7138 closed not-planned) |
| **Codex per-level precedence** | Global `~/.codex/AGENTS.override.md` else `~/.codex/AGENTS.md`; then, walking root→cwd, `AGENTS.override.md`, then `AGENTS.md`, then fallback names | `_agents_file()` prefers `AGENTS.override.md` over `AGENTS.md` at each level. **New since the #13 research** — the research only modelled `AGENTS.md` |
| **AGENTS.md spec** | "Agents automatically read the nearest file in the directory tree, so the closest one takes precedence"; free-form Markdown, **no required frontmatter** | `AGENTS.md` ships with no frontmatter; nested files are legal (the chain check walks them) |
| **Cursor rules** | `.cursor/rules` + **`.mdc`** extension; frontmatter `description` / `globs` / `alwaysApply`; "Always Apply" = `alwaysApply: true`; "Keep rules under 500 lines"; Cursor also supports `AGENTS.md` | The pointer rule is `.mdc` with `alwaysApply: true`; only always-apply rules count toward the always-loaded aggregate |
| **Claude Code per-file size guidance** | "target under 200 lines per CLAUDE.md file" | `AGENTS.md` is authored under 200 lines (a guideline this slice honors in content, not a new check — see Deferrals) |

---

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports in this slice. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **Codebase conventions (match them):** checks take `(root, ignore=())` where they walk content and honor `_ignored`; structured reads go through `_load_frontmatter` / `_read_utf8` (fail closed, never crash); reuse `_blank`, `Finding`, `est_tokens`, `SKIP_DIRS`, `SKIP_RELPATHS`, `_ignored`.
- **The dot-directory trap — read this before writing any rules-directory code.** `iter_files` skips every directory whose name starts with `.`, so `.claude/rules/` and `.cursor/rules/` are **invisible to the walker**. Any check built on `iter_files` would scan zero rule files and pass vacuously — the corpus-void failure. Both directories must be opened **explicitly by path**, and the tests must prove a real `.mdc` is actually measured.
- **Honesty bar (this slice is mostly prose, so it is the main risk):** `AGENTS.md` is product-facing. **No capability claim may precede the capability.** `interview/`, `demo/`, `your-company/`, and `delivery/` do not exist yet — every mention of them must be marked as not-yet-built. Overclaiming here is exactly the trust debt README Tier-0/1 was written to stop.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 1.5d-ii merged to `main` (done: `acb40af`; 341 tests, 1 designed skip). Branch:

```bash
git checkout main && git pull && git checkout -b build/move-2-root-files
```

---

## Design calls flagged for the maintainer

> Pre-made here so the build is unblocked. Each names the record that decides it and the honest counter-argument.

**1. `CLAUDE.md` becomes literally one line — the build rules stop auto-loading.**
*What it is:* `CLAUDE.md` collapses to `@AGENTS.md` and nothing else. Today it also carries the build-phase pointer to `docs/agents/build-sessions.md`, which is what makes the session rules (one increment, branch-first, review gate, **explain-before-deciding**) load into every session automatically.
*Why one line:* D2 says "collapse `CLAUDE.md` to the one-line `@AGENTS.md` import" and the spec's success criteria say "one-line `CLAUDE.md` import"; Claude Code's own docs show exactly this file content; and the engine should model the shape adopters copy. Sean's agent memory already carries `explain-before-deciding` with the note that it **survives CLAUDE.md replacement** — the mitigation is in place and was built for this moment.
*Counter-argument, honestly:* a drive-by session that does **not** start from a kickoff prompt loses the workbench rules from context. Every build session so far has started from a kickoff prompt naming `build-sessions.md`, so the transport exists — but it is now the orchestrator's job, not the file's.
*Mitigation in this plan:* `AGENTS.md` carries a short **"Working on groundwork itself"** section that links `docs/agents/build-sessions.md`. One hop from always-loaded context, and zero workbench prose in the adopter-facing surface.
*If you disagree:* the alternative is Claude Code's other documented shape — `@AGENTS.md` followed by a `## Claude Code` section holding the workbench pointer. That keeps the rules loading but breaks the literal "one-line" criterion.

**2. The per-file context-budget check is retired; its thresholds move to the aggregate.**
*What it is:* today `check_context_budget` runs on **every file in the repo** with #13's 20K/50K thresholds. That is why `scripts/validate.py` now WARNs about its own size — the validator warning about a Python script that never enters an agent's context. #13's thresholds are specified for "the always-loaded surface (root instructions + AGENTS.md/CLAUDE.md + always-on rules + Σ skill descriptions)" — an **aggregate**, not a per-file rule. The per-file application is drift, and the false positive is its symptom.
*Why fix it here:* Move 2 is the #13 slice; leaving it means shipping a permanent false positive on the honesty surface, and it will only grow.
*Counter-argument, honestly:* this is a real reduction in what the gate catches — after the change, a 60K-token `SKILL.md` **body** no longer ERRORs. That is correct per #13 (skill bodies load only when invoked, not always), but it is a genuine loss of a crude "this file is enormous" signal, and it is your call to accept.
*Not in scope either way:* #13's other per-file rules (200-line instruction files, 500-line Cursor rules, 1,536-char skill descriptions as standalone WARNs) — see Deferrals.

**3. `AGENTS.md` is honest that the interview does not exist.**
D2 calls `AGENTS.md` the "navigation + interview entry" — but `interview/` is Phase 3 and `demo/` is Phase 2.3. So the interview section says what the interview **will** do and states plainly that it is not built, and the "what's here today" section lists only what exists. This is D3's tiering applied to `AGENTS.md`. The counter-argument is that it makes the front door read as a construction site — accepted, because the alternative is a capability claim that precedes the capability.

---

## File Structure

- `AGENTS.md` — **create.** The canonical product instructions (navigation, honest status, authoring standard). No frontmatter (the AGENTS.md spec requires none). Under 200 lines.
- `CLAUDE.md` — **replace.** One line: `@AGENTS.md`.
- `.cursor/rules/groundwork.mdc` — **create.** Always-apply pointer to `AGENTS.md`.
- `scripts/validate.py` — **modify.** Add `AGENTS_CHAIN_MAX_BYTES`, `CLAUDE_IMPORT_MAX_DEPTH`, `SKILL_DESCRIPTION_CAP`, `_strip_code`, `_IMPORT`, `_agents_file`, `_file_size`, `check_agents_chain`, `_always_loaded_bytes`, `check_always_loaded_budget`, `check_root_files`. Change `check_context_budget` to take a byte **count**; remove its per-file call from `validate()`; wire the three new checks in.
- `tests/test_validate.py` — **modify.** `TestBudget` updated; `TestAgentsChain`, `TestAlwaysLoadedBudget`, `TestRootFiles` added.
- `docs/known-limitations.md` — **modify.** The context-budget limits section.
- `docs/agents/build-sessions.md` — **modify.** One line noting it is no longer auto-loaded via `CLAUDE.md`.

---

## Task 1: The product `AGENTS.md`

**Files:** Create `AGENTS.md`

- [ ] **Step 1: Create `AGENTS.md`.** Write this file exactly. It is product-facing prose — if you change wording, the honesty bar above governs: nothing that does not exist may be described in the present tense.

```markdown
# AGENTS.md — groundwork

**groundwork is an open-source, harness-agnostic Company OS.** It is files, not an
engine: markdown conventions plus one zero-dependency validator. Any coding agent that
reads a repository can read this one.

This file is the canonical instruction surface for agents working in or with this
repository. `CLAUDE.md` is a one-line import of it; `.cursor/rules/groundwork.mdc`
points here too. Edit **this** file — the others are pointers.

## Status — what is real today

The design is fully charted (19 resolved decisions; see `CONTEXT.md`). Phase 1 is
complete: the schema exists as files, one function is worked end to end, and the
validator gates every layer of it.

**Built and working:**

- `scripts/validate.py` — the gate. Python 3 standard library only, no dependencies.
- `ontologies/` — the two-tier ontology schema and one worked function
  (People/HR, with `onboarding-orchestration` as a full deep record).
- `skills/` — the work-package convention and one worked package
  (`SKILL.md` + `owner-card.md`).
- `governance/` — the constitution rule schema with one compiled rule, the
  action-class hook set, and the append-only changelog.
- `memory/` — the org-memory record schema with one captured baseline.
- `proposals/` — the consent-gate convention for agent-proposed changes.

**Not built yet — do not describe these as working:**

- `interview/` — the generator that would interview a company and write its OS.
  Phase 3. It does not exist.
- `demo/` — the synthetic company and the 15-minute walkthrough. Phase 2.3.
- `delivery/` — the provisioning guide. Phase 4.
- `your-company/` — generated content lives in a **separate private repo**, not here.

## The map

| Path | What it holds |
|---|---|
| `CONTEXT.md` | The glossary. Every resolved decision's vocabulary. Read this first. |
| `ontologies/` | One directory per function. Executive view + deep records. |
| `skills/` | Work packages: `skills/<name>/SKILL.md` + `owner-card.md`. |
| `governance/` | `constitution/` (typed rules), `hooks/` (the action-class gate), `changelog.md`. |
| `memory/` | Org-memory records, one per file, with an index. |
| `proposals/` | Pending improvement proposals. Empty by design — proposals are transient. |
| `scripts/validate.py` | The validator. Run it before you claim anything is done. |
| `MIGRATIONS.md` | The version-pin contract and the pull promise. |
| `docs/known-limitations.md` | What this does **not** do. Read before relying on a check. |

## How to use this repository today

Run the gate:

```
python3 scripts/validate.py .
```

Exit 0 means no ERRORs. WARNs print but do not fail. To check a company repo from
this engine clone, pass its path instead of `.`.

Check governed changes against a base revision:

```
python3 scripts/validate.py . --diff main
```

This adds the stateful modes: org-memory immutability, and the blast-radius tripwire
that requires an escalating change to carry a matching proposal.

To understand the shape before writing anything, read one worked example end to end:
`ontologies/people-hr/onboarding-orchestration.md` →
`skills/onboarding-orchestration/SKILL.md` → its `owner-card.md` →
`memory/onboarding-baseline.md` → `governance/constitution/`.

## The interview (not built — Phase 3)

The intended entry point is an interview: you point your agent at this repo, it asks
your company what work each function actually does — what deserves more human time,
what should be automated, and under what rules — and generates your operating system
from that map into a separate private repository.

**That generator does not exist yet.** Today this repo is the proven schema, the
validator, and one worked function. Anything describing the interview as usable is
wrong.

## Two repos

The public groundwork clone is the **engine** — pull-only, never edited by an adopter.
A company's OS lives in a **separate private repo** carrying content plus a
`groundwork.pin`. The validator runs from the engine clone against that repo.
Upstream improvements arrive by `git pull` on the engine; content is never re-copied.

## Conventions that bind

- **Files, not engines.** No runtime, no server, no database. Conventions plus checks.
- **Zero dependencies.** `scripts/validate.py` and every shipped script import the
  Python standard library only. There is no `requirements.txt` and there will not be.
- **Claims match what is built.** No capability is described before it exists. If you
  are unsure whether something works, run the validator or read
  `docs/known-limitations.md` — do not assume.
- **Agents propose; humans land.** An agent may write a proposal; only the maintainer
  can merge one. That commit permission is the real enforcement, not the validator.

## Authoring standard

Work is tracked as GitHub issues on this repository and driven with the `gh` CLI —
see `docs/agents/issue-tracker.md` for the conventions (native sub-issues and
dependencies, not checklists).

When you change files here:

- Branch before editing; never commit to `main` directly.
- Run `python3 scripts/validate.py .` and the test suite before saying you are done.
- Markdown links must resolve — the validator ERRORs on broken relative links.
- Keep this file under 200 lines. It loads into every session, and it is part of a
  chain that Codex silently truncates past 32 KiB.

## Working on groundwork itself

Contributor and build-session rules — the session shape, the review gate, and the
standing explain-before-deciding rule — live in
`docs/agents/build-sessions.md`. Those are workbench rules for developing groundwork;
they are not product content and do not ship to adopters.
```

- [ ] **Step 2: Verify the honesty bar and the link integrity**

Run: `python3 scripts/validate.py . 2>&1 | grep -E "AGENTS.md|ERROR"; echo "exit: $?"`
Expected: no ERROR lines mentioning `AGENTS.md` (every relative path referenced above exists). If a broken-link ERROR appears, fix the path — do not delete the check.

Run: `wc -l AGENTS.md`
Expected: fewer than 200 lines.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: author the product AGENTS.md (canonical instruction surface, D2 Move 2)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Collapse `CLAUDE.md` + add the Cursor pointer

**Files:** Replace `CLAUDE.md`; create `.cursor/rules/groundwork.mdc`; modify `docs/agents/build-sessions.md`

- [ ] **Step 1: Replace `CLAUDE.md` entirely** with exactly this one line (plus a trailing newline, no heading, no other content):

```
@AGENTS.md
```

- [ ] **Step 2: Create `.cursor/rules/groundwork.mdc`.** The `.mdc` extension is required — Cursor ignores plain `.md` in this directory (verified live 2026-07-27):

```
---
description: How to work in the groundwork repository
alwaysApply: true
---

Read AGENTS.md at the repository root before making changes. It is the canonical
instruction surface for this repo: what is built, what is not, the repo map, and the
authoring standard. CLAUDE.md and this rule are pointers to it — edit AGENTS.md.
```

- [ ] **Step 3: Note the loading change in `docs/agents/build-sessions.md`.** Add this line at the end of the "Where the plan lives" section:

```markdown
- **Loading:** these rules are no longer auto-loaded — `CLAUDE.md` is now the one-line `@AGENTS.md` import (D2 Move 2). Build sessions load this file by being pointed at it in the session kickoff; `AGENTS.md` links it under "Working on groundwork itself".
```

- [ ] **Step 4: Verify**

Run: `cat CLAUDE.md && python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `CLAUDE.md` prints exactly `@AGENTS.md`; validator exits 0. The two `CLAUDE.md:11` high-entropy WARNs from the old content are now gone.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md .cursor/rules/groundwork.mdc docs/agents/build-sessions.md
git commit -m "docs: collapse CLAUDE.md to @AGENTS.md + add .cursor/rules pointer (D2 Move 2)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: #13 — the AGENTS.md-chain ERROR + the always-loaded aggregate

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:** Produces `check_agents_chain(root, ignore=())` and `check_always_loaded_budget(root)`, both wired into `validate()`. `check_context_budget(path, num_bytes)` changes to take a byte **count**; its per-file call is removed from the walk.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py` (append at the end):

```python
class TestAgentsChain(unittest.TestCase):
    def test_no_agents_file_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# x\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_small_chain_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# Root\n")
            _write(d, "pkg/AGENTS.md", "# Pkg\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_oversized_root_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (32 * 1024 + 1))
            findings = validate.check_agents_chain(d)
            self.assertTrue(any(f.level == "ERROR" and "project_doc_max_bytes" in f.message
                                for f in findings))

    def test_chain_accumulates_across_levels(self):
        # Neither file is over the cap alone; concatenated they are.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (20 * 1024))
            _write(d, "pkg/AGENTS.md", "y" * (20 * 1024))
            findings = validate.check_agents_chain(d)
            self.assertTrue(any(f.level == "ERROR" and "pkg/AGENTS.md" in f.path
                                for f in findings))
            self.assertFalse(any(f.path == "AGENTS.md" for f in findings))

    def test_override_file_takes_precedence(self):
        # Codex reads AGENTS.override.md instead of AGENTS.md at each level.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (32 * 1024 + 1))
            _write(d, "AGENTS.override.md", "small\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_empty_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "")
            _write(d, "pkg/AGENTS.md", "# Pkg\n")
            self.assertEqual(validate.check_agents_chain(d), [])

    def test_workbench_trees_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "tests/AGENTS.md", "x" * (32 * 1024 + 1))
            self.assertEqual(validate.check_agents_chain(d), [])


CURSOR_ALWAYS = "---\ndescription: d\nalwaysApply: true\n---\n\nSee AGENTS.md.\n"


class TestAlwaysLoadedBudget(unittest.TestCase):
    def test_small_repo_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# x\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_oversized_agents_file_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (21_000 * 4))
            findings = validate.check_always_loaded_budget(d)
            self.assertTrue(any(f.level == "WARN" for f in findings))

    def test_imports_are_followed_and_counted(self):
        # Imports do not reduce context: the imported file must be measured.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@big.md\n")
            _write(d, "big.md", "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_import_inside_backticks_is_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "Mention `@big.md` literally.\n")
            _write(d, "big.md", "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_import_cycle_terminates(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "@a.md\n")
            _write(d, "a.md", "@CLAUDE.md\n")
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_always_apply_cursor_rule_counts(self):
        # .cursor/ is a dot-directory: iter_files never sees it, so this proves
        # the check reads it explicitly rather than scanning nothing.
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".cursor/rules/big.mdc",
                   "---\ndescription: d\nalwaysApply: true\n---\n" + "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_non_always_apply_cursor_rule_is_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".cursor/rules/big.mdc",
                   "---\ndescription: d\nalwaysApply: false\n---\n" + "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_path_scoped_claude_rule_is_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".claude/rules/scoped.md",
                   "---\npaths:\n  - \"src/**\"\n---\n" + "x" * (21_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_unscoped_claude_rule_counts(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, ".claude/rules/always.md", "x" * (21_000 * 4))
            self.assertTrue(any(f.level == "WARN"
                                for f in validate.check_always_loaded_budget(d)))

    def test_skill_description_is_capped_not_summed_whole(self):
        # A huge SKILL.md body is NOT always-loaded; only its description is,
        # and only up to Claude Code's 1,536-char listing truncation.
        with tempfile.TemporaryDirectory() as d:
            _write_package(d, skill=SKILL_OK + "\n" + "x" * (60_000 * 4))
            self.assertEqual(validate.check_always_loaded_budget(d), [])

    def test_error_threshold(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * (50_000 * 4))
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_always_loaded_budget(d)))
```

- [ ] **Step 2: Update `TestBudget`** — `check_context_budget` now takes a byte count, not bytes. In `tests/test_validate.py`, replace the three payload arguments:

```python
class TestBudget(unittest.TestCase):
    def test_small_file_no_findings(self):
        self.assertEqual(validate.check_context_budget("f.md", 5), [])

    def test_warn_threshold(self):
        findings = validate.check_context_budget("f.md", 20_000 * 4)
        self.assertTrue(any(f.level == "WARN" for f in findings))
        self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_error_threshold(self):
        findings = validate.check_context_budget("f.md", 50_000 * 4)
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_est_tokens(self):
        self.assertEqual(validate.est_tokens(4000), 1000)
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestAgentsChain tests.test_validate.TestAlwaysLoadedBudget -v`
Expected: FAIL — `module 'validate' has no attribute 'check_agents_chain'`.

- [ ] **Step 4: Change `check_context_budget` to take a byte count.** Replace the existing function body's first line:

```python
def check_context_budget(path, num_bytes):
    """#13 thresholds over a measured byte count. Bytes are what a stdlib
    validator can compute deterministically; tokens are reported (len/4). This
    is applied to the ALWAYS-LOADED aggregate, not to arbitrary files — a Python
    script or a research note never enters an agent's context."""
    toks = est_tokens(num_bytes)
```

Everything below that line is unchanged.

- [ ] **Step 5: Implement the new checks** — add to `scripts/validate.py`, immediately **after** `check_links` and **before** `DIRECTIONS = {"up", "down"}`:

```python
# Codex: "stops adding files once the combined size reaches the limit defined by
# project_doc_max_bytes (32 KiB by default)" — and truncates SILENTLY (no warning;
# openai/codex#7138 closed not-planned). Verified live 2026-07-27.
AGENTS_CHAIN_MAX_BYTES = 32 * 1024
# Claude Code: imports resolve "with a maximum depth of four hops".
CLAUDE_IMPORT_MAX_DEPTH = 4
# Claude Code truncates a skill's listed description at this many characters.
SKILL_DESCRIPTION_CAP = 1536
# Codex checks AGENTS.override.md before AGENTS.md at every level.
_AGENTS_NAMES = ("AGENTS.override.md", "AGENTS.md")

_IMPORT = re.compile(r"(?:(?<=\s)|^)@([^\s`]+)", re.M)


def _strip_code(text):
    """Drop fenced blocks and inline code spans. Claude Code's import parser
    "skips Markdown code spans and fenced code blocks", so `@README` inside
    backticks is literal text and must NOT be followed."""
    text = re.sub(r"```.*?(?:```|\Z)", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def _agents_file(dirpath):
    """The instruction file Codex would read at this level, honoring the
    override precedence. None when the level contributes nothing."""
    for name in _AGENTS_NAMES:
        p = os.path.join(dirpath, name)
        if os.path.isfile(p):
            return p
    return None


def _file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def check_agents_chain(root, ignore=()):
    """#13 hard ERROR. Codex "concatenates files from the root down, joining them
    with blank lines" and stops once the total reaches project_doc_max_bytes
    (32 KiB). Past the cap the tail is silently dropped — that is DATA LOSS, not
    bloat, and no harness warns about it, so the validator is the missing warning.

    Only the repo-side chain is measurable; a user's own ~/.codex/AGENTS.md counts
    against the same 32 KiB and is invisible here (docs/known-limitations.md)."""
    findings = []
    for dirpath, dirnames, _filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")
                       and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS
                       and not _ignored(d, ignore)]
        leaf = _agents_file(dirpath)
        if leaf is None:
            continue
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        sizes = []
        unreadable = None
        for i in range(len(parts) + 1):
            f = _agents_file(os.path.join(root, *parts[:i]))
            if f is None:
                continue
            n = _file_size(f)
            if n is None:
                unreadable = f
                break
            if n:  # "Codex skips empty files"
                sizes.append(n)
        if unreadable is not None:
            findings.append(Finding("ERROR", os.path.relpath(unreadable, root), None,
                                    "cannot size this instruction file — the AGENTS.md chain "
                                    "budget cannot be verified (#13)"))
            continue
        total = sum(sizes) + 2 * max(len(sizes) - 1, 0)  # joined with blank lines
        if total > AGENTS_CHAIN_MAX_BYTES:
            findings.append(Finding(
                "ERROR", os.path.relpath(leaf, root), None,
                "AGENTS.md chain reaching this directory is %d bytes, over Codex's "
                "%d-byte project_doc_max_bytes — everything past the cap is silently "
                "truncated (#13)" % (total, AGENTS_CHAIN_MAX_BYTES)))
    return findings


def _always_loaded_bytes(root):
    """#13's always-loaded surface as (label, bytes) pairs: the root AGENTS.md,
    the root CLAUDE.md and everything it imports, unscoped .claude/rules/*.md,
    always-apply .cursor/rules/*.mdc, and each skill's description capped at
    Claude Code's listing truncation.

    Both rules directories are opened BY PATH on purpose: iter_files skips every
    dot-directory, so a walker-based version would measure nothing and pass."""
    items = []

    f = _agents_file(root)
    if f is not None:
        n = _file_size(f)
        if n:
            items.append((os.path.relpath(f, root), n))

    root_real = os.path.realpath(root)
    seen = set()

    def add_import(abspath, depth):
        if depth > CLAUDE_IMPORT_MAX_DEPTH or not os.path.isfile(abspath):
            return
        real = os.path.realpath(abspath)
        if real in seen:
            return
        seen.add(real)
        rel = os.path.relpath(abspath, root)
        text, _rd = _read_utf8(abspath, rel)
        if text is None:
            return
        items.append((rel, len(text.encode("utf-8"))))
        base = os.path.dirname(abspath)
        for target in _IMPORT.findall(_strip_code(text)):
            if target.startswith("~") or os.path.isabs(target):
                continue  # outside the repo: real context, but not measurable here
            nxt = os.path.normpath(os.path.join(base, target))
            if os.path.realpath(nxt).startswith(root_real + os.sep):
                add_import(nxt, depth + 1)

    add_import(os.path.join(root, "CLAUDE.md"), 1)

    for rel_dir, ext, mode in ((os.path.join(".claude", "rules"), ".md", "claude"),
                               (os.path.join(".cursor", "rules"), ".mdc", "cursor")):
        d = os.path.join(root, rel_dir)
        if not os.path.isdir(d):
            continue
        for dirpath, _dn, filenames in os.walk(d):
            for fn in sorted(filenames):
                if not fn.endswith(ext):
                    continue
                abspath = os.path.join(dirpath, fn)
                rel = os.path.relpath(abspath, root)
                data, _fm = _load_frontmatter(abspath, rel)
                if data is None:
                    continue
                if mode == "claude":
                    # path-scoped rules load on file match, not at launch
                    if not _blank(data.get("paths")):
                        continue
                else:
                    aa = data.get("alwaysApply")
                    if not (isinstance(aa, str) and aa.strip().lower() == "true"):
                        continue
                n = _file_size(abspath)
                if n:
                    items.append((rel, n))

    sdir = os.path.join(root, "skills")
    if os.path.isdir(sdir) and not os.path.islink(sdir):
        try:
            names = sorted(os.listdir(sdir))
        except OSError:
            names = []
        for name in names:
            sp = os.path.join(sdir, name, "SKILL.md")
            if not os.path.isfile(sp):
                continue
            rel = os.path.relpath(sp, root)
            data, _fm = _load_frontmatter(sp, rel)
            if data is None:
                continue
            desc = data.get("description")
            if isinstance(desc, str) and desc.strip():
                items.append((rel + " (description)",
                              min(len(desc.encode("utf-8")), SKILL_DESCRIPTION_CAP)))
    return items


def check_always_loaded_budget(root):
    """#13's aggregate: what every session pays for before anyone types anything.
    WARN ~20K est. tokens, ERROR ~50K. Skill BODIES are excluded on purpose —
    they load only when a skill is invoked."""
    items = _always_loaded_bytes(root)
    findings = check_context_budget("(always-loaded surface)",
                                    sum(n for _lbl, n in items))
    if findings and items:
        top = ", ".join("%s %dB" % (lbl, n)
                        for lbl, n in sorted(items, key=lambda it: -it[1])[:3])
        f = findings[0]
        findings[0] = Finding(f.level, f.path, f.line, f.message + " — largest: " + top)
    return findings
```

- [ ] **Step 6: Rewire `validate()`.** Remove the per-file budget call and add the new checks. In `validate(root)`, delete this line from the per-file loop:

```python
        findings += check_context_budget(rel, data_bytes)
```

and add these at the end, after `findings += check_changelog(root, ignore)`:

```python
    findings += check_agents_chain(root, ignore)
    findings += check_always_loaded_budget(root)
```

- [ ] **Step 7: Run tests + the gate**

Run: `python3 -m unittest tests.test_validate.TestAgentsChain tests.test_validate.TestAlwaysLoadedBudget tests.test_validate.TestBudget -v`
Expected: PASS.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exit 0, and **no** `scripts/validate.py … context budget` WARN — the per-file application is retired. The always-loaded surface here is a few KB, far under the WARN threshold.

- [ ] **Step 8: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #13 AGENTS.md-chain 32KiB ERROR + correctly-scoped always-loaded budget

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The root-file drift check + Known Limitations

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`, `docs/known-limitations.md`

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestRootFiles(unittest.TestCase):
    def test_no_agents_md_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "CLAUDE.md", "# anything\n")
            self.assertEqual(validate.check_root_files(d), [])

    def test_import_satisfies_the_check(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])

    def test_missing_claude_md_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            self.assertTrue(any(f.level == "ERROR" and "CLAUDE.md" in f.path
                                for f in validate.check_root_files(d)))

    def test_claude_md_without_import_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "# separate instructions\n")
            self.assertTrue(any(f.level == "ERROR" and "drift" in f.message
                                for f in validate.check_root_files(d)))

    def test_import_in_backticks_does_not_satisfy(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "Write `@AGENTS.md` to import it.\n")
            self.assertTrue(any(f.level == "ERROR" and "drift" in f.message
                                for f in validate.check_root_files(d)))

    def test_symlinked_claude_md_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            os.symlink(os.path.join(d, "AGENTS.md"), os.path.join(d, "CLAUDE.md"))
            self.assertEqual([f for f in validate.check_root_files(d)
                              if f.level == "ERROR"], [])

    def test_symlink_to_the_wrong_target_errors(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "other.md", "# o\n")
            os.symlink(os.path.join(d, "other.md"), os.path.join(d, "CLAUDE.md"))
            self.assertTrue(any(f.level == "ERROR"
                                for f in validate.check_root_files(d)))

    def test_missing_cursor_rules_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            findings = validate.check_root_files(d)
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            self.assertTrue(any(f.level == "WARN" and "cursor" in f.path for f in findings))

    def test_cursor_rule_without_always_apply_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc",
                   "---\ndescription: d\nalwaysApply: false\n---\n\nSee AGENTS.md.\n")
            self.assertTrue(any(f.level == "WARN" for f in validate.check_root_files(d)))

    def test_cursor_rule_not_referencing_agents_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc",
                   "---\ndescription: d\nalwaysApply: true\n---\n\nUnrelated guidance.\n")
            self.assertTrue(any(f.level == "WARN" for f in validate.check_root_files(d)))

    def test_wired_into_validate(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "# drifted\n")
            self.assertTrue(any(f.level == "ERROR" and "drift" in f.message
                                for f in validate.validate(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestRootFiles -v`
Expected: FAIL — no attribute `check_root_files`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py` immediately after `check_always_loaded_budget`:

```python
def check_root_files(root):
    """§6 root-file set. AGENTS.md is canonical. Claude Code reads CLAUDE.md and
    NOT AGENTS.md (verified live 2026-07-27), so CLAUDE.md must point at it —
    either the documented '@AGENTS.md' import or a symlink resolving to it.
    Two root files that each look canonical are two sources of truth, and that
    drift is exactly what this catches. Silent when there is no AGENTS.md."""
    findings = []
    agents = os.path.join(root, "AGENTS.md")
    if not os.path.isfile(agents):
        return findings

    claude = os.path.join(root, "CLAUDE.md")
    if not os.path.lexists(claude):
        findings.append(Finding(
            "ERROR", "CLAUDE.md", None,
            "AGENTS.md is present but CLAUDE.md is missing — Claude Code reads CLAUDE.md, "
            "not AGENTS.md; add a CLAUDE.md whose content is '@AGENTS.md' (§6)"))
    elif os.path.islink(claude):
        if os.path.realpath(claude) != os.path.realpath(agents):
            findings.append(Finding(
                "ERROR", "CLAUDE.md", None,
                "CLAUDE.md is a symlink that does not resolve to AGENTS.md — the root files "
                "have drifted into separate sources of truth (§6)"))
    else:
        text, rd = _read_utf8(claude, "CLAUDE.md")
        findings += rd
        if text is not None:
            targets = _IMPORT.findall(_strip_code(text))
            if not any(os.path.normpath(t.replace("\\", "/")) == "AGENTS.md"
                       for t in targets):
                findings.append(Finding(
                    "ERROR", "CLAUDE.md", None,
                    "CLAUDE.md does not import AGENTS.md — the root files have drifted into "
                    "separate sources of truth; its content should be '@AGENTS.md' (§6)"))

    cdir = os.path.join(root, ".cursor", "rules")
    if not os.path.isdir(cdir):
        findings.append(Finding(
            "WARN", os.path.join(".cursor", "rules"), None,
            "no .cursor/rules/*.mdc pointer — Cursor loads .mdc rules from this directory; "
            "add an always-apply rule pointing at AGENTS.md (§6)"))
        return findings

    pointer = False
    for dirpath, _dn, filenames in os.walk(cdir):
        for fn in sorted(filenames):
            if not fn.endswith(".mdc"):
                continue
            abspath = os.path.join(dirpath, fn)
            rel = os.path.relpath(abspath, root)
            data, fm = _load_frontmatter(abspath, rel)
            findings += fm
            if data is None:
                continue
            aa = data.get("alwaysApply")
            if not (isinstance(aa, str) and aa.strip().lower() == "true"):
                continue
            text, _rd = _read_utf8(abspath, rel)
            if text is not None and "AGENTS.md" in text:
                pointer = True
    if not pointer:
        findings.append(Finding(
            "WARN", os.path.join(".cursor", "rules"), None,
            "no always-apply .cursor/rules/*.mdc rule references AGENTS.md — Cursor users "
            "get no route to the canonical instructions (§6)"))
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — after `findings += check_always_loaded_budget(root)`, add:

```python
    findings += check_root_files(root)
```

- [ ] **Step 5: Append to `docs/known-limitations.md`** (new section at the end):

```markdown
## Context budget (#13)

- **Only the repo-side instruction chain is measurable.** Codex's 32 KiB
  `project_doc_max_bytes` cap covers the *combined* chain, which begins with the user's
  own `~/.codex/AGENTS.md` (or `AGENTS.override.md`). That file is outside the repository
  and invisible to the validator, so a chain that passes here can still be truncated on a
  machine with a large global instruction file. The repo's own budget is what this gate
  governs.
- **Imports outside the repository are not counted.** `CLAUDE.md` may import
  `@~/.claude/…` or an absolute path; those load into context but cannot be measured from
  the repo, so they are skipped rather than guessed at.
- **Token counts are an estimate, not a tokenizer.** Bytes are measured; tokens are
  reported as `bytes / 4`. Real tokenization differs per model and per content; the
  thresholds are budget guidance, not an exact accounting.
- **The always-loaded set is a model of four harnesses, not a measurement of one.** It
  covers the root `AGENTS.md`, `CLAUDE.md` and its imports, unscoped `.claude/rules/`,
  always-apply `.cursor/rules/`, and skill descriptions capped at Claude Code's 1,536-char
  listing truncation. Harnesses differ in what else they preload (MCP tool names, system
  prompts); those are outside the repo and outside this check.
- **Skill bodies are deliberately excluded.** A `SKILL.md` body loads only when the skill
  is invoked, so its size is not part of the always-loaded budget. Before this slice these
  thresholds were applied per-file to every file in the repository, which produced false
  positives on files that never enter an agent's context (`scripts/validate.py` among
  them); the per-file application was retired, and with it any size ceiling on
  non-instruction files.
- **Dot-directories are not otherwise scanned.** `.claude/rules/` and `.cursor/rules/` are
  read by name for these checks, but the generic walker still skips dot-directories, so
  secret-scanning and link-checking do not cover them.
```

- [ ] **Step 6: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`, roughly 370 tests.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s)` and `exit: 0`. The WARN count drops from 10 to about 7: the two `CLAUDE.md` high-entropy WARNs and the `scripts/validate.py` budget WARN are gone, and no new `.cursor/rules` WARN appears because the pointer exists. Do not chase an exact number — what must hold is **0 errors**, no `CLAUDE.md` entropy WARN, and no per-file budget WARN.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py docs/known-limitations.md
git commit -m "feat(validate): §6 root-file drift check + #13 known limitations

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **#13's remaining per-file rules** — WARN over 200 lines per instruction file, WARN over 500 lines per Cursor rule, WARN over 1,536 chars per skill description as a standalone finding. They are refinements of a surface that currently holds one skill and one rule; they land with Phase 2.3 (`demo/`) and Phase 3, where there is a real population to measure. The 1,536-char cap **is** already honored inside the aggregate.
- **Config-overridable thresholds** (#13 mentions them) — not built; the constants are module-level and editable.
- **Secret/link scanning inside dot-directories** — the walker still skips them; documented as a limitation.
- **`interview/`, `demo/`, `delivery/`, `your-company/`** — later phases. `AGENTS.md` names them as not-built and must not imply otherwise.
- **After this slice, Phase 2 begins:** (2.1) the remaining 7 executive-view ontologies, (2.2) CS renewal-prep + PM feature-request-triage as worked slices, (2.3) the full `demo/` — which is also where the #18 tripwire and the #21 pin stop being dormant.

## Self-Review

- **Coverage of D2 Move 2:** product `AGENTS.md` (navigation + interview entry + GitHub authoring standard, honestly marking `interview/` and `demo/` in progress) → Task 1; one-line `CLAUDE.md` import → Task 2; `.cursor/rules/*.mdc` pointers → Task 2; the deferred #13 AGENTS.md-chain check (>32 KiB hard ERROR) → Task 3; "drift between the root files is a validator check" (spec success criterion) → Task 4. `docs/agents/build-sessions.md` continues to carry workbench rules independently, and says so.
- **Live contracts, not memory.** Every external number and rule in the code traces to a doc fetched 2026-07-27 and quoted in the table above. Two facts were **new relative to the #13 research**: Codex's `AGENTS.override.md` per-level precedence, and `project_doc_fallback_filenames` (noted, not implemented — a repo cannot know an adopter's config).
- **Placeholder scan:** no TBD/TODO; every step carries complete content or code and a verification command with expected output.
- **Type consistency:** `Finding(level, path, line, message)`; `_load_frontmatter` → `(data|None, findings)`; `_read_utf8` → `(text|None, findings)`; `_file_size` → `int|None`; `_always_loaded_bytes` → `list[(str, int)]`; `check_context_budget(path, num_bytes)` now takes an **int** (its three tests are updated in the same task). No new imports.
- **Pre-empts the recurring Codex findings.** (a) *Corpus void / dead path* — `.claude/rules/` and `.cursor/rules/` are dot-directories that `iter_files` skips, so both are opened by path and two tests prove a real `.mdc`/`.md` is actually measured; a walker-based version would have passed vacuously. (b) *Non-scalar frontmatter* — `isinstance(..., str)` guards on `alwaysApply` and `description`; `paths` is tested with `_blank` so a bare `paths:` (which parses to `[]`) does not read as path-scoped. (c) *Fail-open on malformed input* — unreadable instruction files ERROR in the chain check rather than being skipped; unreadable rules and skills are skipped from the aggregate only after `_load_frontmatter` has already emitted its own finding. (d) *Alias/laundering* — import following is confined to `realpath` inside the root, cycles terminate via a `seen` set of realpaths, and depth is capped at Claude Code's documented 4 hops; a backticked `@path` does not count as an import in either the budget or the drift check (two dedicated tests). (e) *Symlinks* — the drift check accepts a `CLAUDE.md` symlink only when it resolves to `AGENTS.md`, and rejects one that resolves elsewhere.
- **Behavior change surfaced, not buried:** retiring the per-file budget check removes an existing signal. It is Design call 2, is stated in `docs/known-limitations.md`, and the exact false positive it fixes is named.
