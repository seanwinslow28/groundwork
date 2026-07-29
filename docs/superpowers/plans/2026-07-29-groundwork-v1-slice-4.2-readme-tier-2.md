# groundwork V1 — Slice 4.2: README Tier 2 — the honesty slice — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn on the README's capability claims — the "**Not technical? Point your agent at this repo**" first-section move (brief §4 step 1), the demo walkthrough, and `validate` usage — with every claim anchored to a file or a test. Along the way, close the fourth harness's instruction pointer (a live fetch found Gemini CLI reads `GEMINI.md`, not `AGENTS.md`), pay the License carve-out promise the generator's arrival made due, and clear the three stale not-built-yet statements this slice's promotion creates.

**Architecture:** One new one-line root file, one added WARN in an existing check, one README rewrite, and an honesty sweep across four files. The README is the deliverable; the WARN is what makes its first paragraph true.

**Tech Stack:** Markdown, one stdlib finding, stdlib `unittest`.

## Global Constraints

- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, and `--diff main` must exit 0. **Task 1 is the one place this can move**, and only if the new `GEMINI.md` and the new WARN do not land together — if the count goes to 8, the file is missing; if a *demo* finding appears, the check is reading the wrong root (the 2.3a scoping-bug class).
- **`python3 scripts/validate.py demo` must stay exactly `0 error(s), 2 warning(s)`.** `check_root_files` returns `[]` when there is no `AGENTS.md`, and `demo/` has none — so the new WARN must be provably silent there. There is a step that checks it.
- **Test count moves up only,** from **684** (1 designed skip).
- **`AGENTS.md` must stay under 200 lines.** It is at **157**.
- **`demo/` is a governed root and this slice does not touch it.** No file under `demo/` is on the list. If a step seems to need one, stop and report.
- **The honesty bar is the whole point of this slice.** Every capability sentence in the README must be traceable to a file in this repo or a test in `tests/`. Three claims are load-bearing *understatements* and must not be smoothed: the demo's rung-5 refusal is **instruction-strength, not a runtime block**; skill auto-invocation is **not reliable**; the generator is **documents an agent follows, not a program**. Removing any of those hedges is the failure mode this slice exists to avoid.
- **Zero dependencies.** Stdlib only in shipped scripts.
- **Watch `check_entropy`:** it WARNs on a 40+ character run of `[A-Za-z0-9+/=_-]` at ≥ 4.0 bits. `README.md` is scanned. Every link path in the new README is short on purpose; do not introduce `ontologies/people-hr/onboarding-orchestration.md` (a 44-character run) or any other long hyphenated path there. There is a measurement step.
- **No test counts, star counts, or commit shas in the README.** A number that goes stale every slice is trust debt with a timer.
- **Pronouns:** they/them or the person's name.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 4.1 merged and pushed (`5554b0b`; spec log at `d0141e3`). Phase 4 open. Baseline verified at planning time: **684 tests OK (1 skip)**, `validate.py .` = `0 error(s), 7 warning(s)`, `--diff main` exit 0, `validate.py demo` = `0 error(s), 2 warning(s)`, `AGENTS.md` 157 lines, `origin/main..main` = 0. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-4.2-readme-tier-2
```

---

## Design calls flagged for the maintainer

**1. Gemini CLI does not read `AGENTS.md`, so today a Gemini user who points their agent at this repo loads nothing. The maintainer chose to ship the fourth pointer.**
Fetched live 2026-07-29, two independent first-party sources agreeing (the raw `google-gemini/gemini-cli` docs on GitHub and the published docs site): the default context filename is `GEMINI.md`; `AGENTS.md` is loaded **only** when `context.fileName` is configured in `settings.json`; and the context file supports importing other files with `@file.md`, "both relative and absolute paths," demonstrated as `@./components/instructions.md`.

That makes this the **fifth time in this build that fetching the live contract changed the artifact** (the hook output contract, `AGENTS.override.md` precedence, the `defer` rung-3 mechanism, the org-provisioning unit being a plugin — and now the fourth root pointer). It also lands squarely on 4.2, because "Not technical? Point your agent at this repo" is the README's *first* section and it is the sentence the gap falsifies.

Decided (maintainer, 2026-07-29): **ship a one-line root `GEMINI.md` and add a missing-pointer WARN to `check_root_files`.** The WARN has exact precedent — `check_root_files` already WARNs when no always-apply `.cursor/rules/*.mdc` references `AGENTS.md`. Honest cost, recorded: 4.2 gains a `validate.py` change and a test in a slice that would otherwise be content, and it edits Slice 3.3's company-repo manifest. The rejected alternatives were a content-only three-harness README with a Gemini footnote (fully honest, but leaves §6's root-file set incomplete against groundwork's own harness-agnostic headline) and shipping the file with no check (an unchecked pointer drifts, which is the exact failure `check_root_files` exists to catch for `CLAUDE.md`).

**Two details that are decisions, not typos.** The shipped content is `@./AGENTS.md`, with the `./` prefix, because that is the form the Gemini docs *demonstrate* — a bare `@AGENTS.md` is very likely fine and was not shown, and 2.3d's rule is to ship the claim at the strength the evidence supports. And the check accepts either spelling, because the invariant is "this file imports the canonical instructions," not "it is spelled the way we spelled it."

**2. `AGENTS.md:44`'s "loadable in all four harnesses" — change the verb, not the guide.**
The carried 4.1 finding: `AGENTS.md` asserts the symlink layer makes generated skills *loadable* in all four harnesses, while `delivery/README.md` says the one-hop shape its commands print has not been separately tested for Claude Code discovery.

I checked the tempting fix — switch `delivery/`'s commands to the "verified" two-hop shape — and **it does not work.** The empirically verified shape (#19, 2026-07-18) had a *real skill directory* at `.agents/skills/<name>` with a `.claude/skills/<name>` symlink pointing at it. Slice 3.3's manifest puts skills at `skills/<name>/`, and it has to: `iter_files` skips every dot-directory, so skills living under `.agents/skills/` would be invisible to the validator — the corpus-void trap. So *some* extra hop is unavoidable, no fully-verified zero-hop shape exists, and `delivery/`'s caveat plus its `/doctor` fallback is the honest artifact.

**Resolution: the wording in `AGENTS.md` moves from an outcome to a structure** — the layer *gives generated skills a harness-visible path* in all four harnesses, which is true by construction and is exactly what was verified, with the tested-versus-untested detail staying in `delivery/README.md` where it belongs. Fable's "leave it" instinct was right about the guide and wrong about one verb.

**3. The License carve-out promise is not merely due — it is unpaid where it matters, and this slice pays it.**
The README promises "an explicit README/NOTICE carve-out will ship with the generator." The generator shipped in 3.3. Reading `interview/generate.md` during planning: **it says nothing about licensing at all**, so a generated company repo carries no statement that its content is the company's own. The README's own sentence is substantively the carve-out, but the promised artifact was one that ships *with the generator*, and that one does not exist.

Decided (maintainer, 2026-07-29): **pay it in 4.2.** One sentence in `generate.md`'s root-files step instructing the generator to write the carve-out into the company repo's own `AGENTS.md`, and a README License section that describes what exists and points at it. The `LICENSE` file itself still lands in **4.3**, and the README says so plainly rather than in a promise. This is the third occurrence of the same shape the build log has now named twice — *a justification written as a present-tense condition acquires an expiry date the moment something can satisfy it* — and "will ship with the generator" expired on `8c41721`.

**4. The complete list of files that mention something this slice promotes.** Three slices in a row have shipped a sibling file contradicting a promotion (3.2's three-document split, 3.3's `protocol.md`, 4.1's `generate.md`). Grepped, not remembered:

| File | What is stale after this slice |
|---|---|
| `AGENTS.md:52` | `- The README's capability claims (Tier 2). Phase 4.2.` under "Not built yet" |
| `AGENTS.md:13-16` | The status paragraph still says "Phase 1 is complete and Phase 2.2 extends it" — three phases out of date |
| `AGENTS.md:44` | Design call 2's verb |
| `interview/generate.md:176` | "`delivery/`, not built yet" — the carried 4.1 finding |
| `interview/generate.md:33-55` | The manifest gains `GEMINI.md` (design call 1) |
| `interview/generate.md:130-136` | The root-files step gains the carve-out (design call 3) |
| `docs/known-limitations.md:78` | "a model of four harnesses" enumerates four contributors and will not include `GEMINI.md` |
| `tests/test_validate.py` (`TestGeneratedCompanyRepo._materialize`) | The fixture builds the manifest's root file set and must gain `GEMINI.md` |

Nothing under `demo/` appears — checked. `README.md` is the only place any of this becomes a *capability claim*.

**5. What the README may claim, and the anchor for each.** No sentence ships without one.

| Claim | Anchor |
|---|---|
| Four harnesses load the canonical instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/groundwork.mdc` + `check_root_files` + the four live fetches dated 2026-07-29 |
| 15 minutes, three queries, zero credentials, ending on a refusal that names rule/owner/appeal | `demo/walkthrough.md` |
| The refusal is instruction-strength, not a runtime block | `demo/walkthrough.md` "Honest limits"; 2.3e design call 5 |
| The interview is four documents an agent follows | `interview/README.md`, `protocol.md`, `questions.md`, `generate.md` |
| A generated OS passes the gate | `TestGeneratedCompanyRepo` |
| Zero dependencies | `TestZeroDep` |
| `--diff` adds memory immutability, frozen layers, the consent tripwire | `memory_diff_findings`, `check_interview_state`'s diff guard, `blast_radius_diff_findings` |
| Provisioning is manual, three surfaces | `delivery/README.md` |
| What it does not do | `docs/known-limitations.md` |

**6. What must not regress.** #14 pins the credit block at the **bottom** of the README, in **prose bullets**, with paid/free stated straight and no "worth buying" endorsement; #15 pins the two-project comparison as a compact table whose rows are pointers plus an "On the two active projects" prose subsection carrying the concessions as the single source of truth. **Both sections ship byte-identical** except where a link target moves. They are re-verified by grep, not by reading.

**Named cut line — and it has a consequence, which is why it is stated here.** If the session runs long the cut is **Task 1**, which becomes Slice **4.2b**. Cutting it *changes Task 2*: the README's step 1 must then name three harnesses plus the one-line Gemini fix, because **the README may not claim the fourth pointer before the file exists.** Tasks 2 and 3 do not split.

---

## File Structure

**Create (1 file):** `GEMINI.md`

**Modify (5 files):** `README.md`, `scripts/validate.py`, `tests/test_validate.py`, `AGENTS.md`, `interview/generate.md`, `docs/known-limitations.md`

> `interview/generate.md` is edited in **two** tasks with clearly separate edits: the manifest line in Task 1 (it is one contract with the fixture), the not-built-yet fix and the carve-out in Task 3.

---

## Task 1: The fourth pointer

**Files:** Create `GEMINI.md`. Modify `scripts/validate.py`, `tests/test_validate.py`, `interview/generate.md`.

> **This task must land as one commit.** The file without the check is an unenforced pointer; the check without the file takes the engine to 8 WARNs. Write the tests first, then the check, then the file, then commit once.

- [ ] **Step 1: Tests first.** Add to `TestRootFiles` in `tests/test_validate.py`. Put this next to `CURSOR_ALWAYS` at module scope first:

```python
GEMINI_POINTER = "@./AGENTS.md\n"
```

Then the cases:

```python
    def test_missing_gemini_md_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            findings = validate.check_root_files(d)
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            gem = [f for f in findings if f.path == "GEMINI.md"]
            self.assertEqual(len(gem), 1, "one GEMINI finding, not several")
            self.assertEqual(gem[0].level, "WARN")
            self.assertIn("Gemini CLI reads GEMINI.md", gem[0].message)

    def test_gemini_pointer_satisfies_the_check(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", GEMINI_POINTER)
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])

    def test_bare_gemini_import_also_satisfies(self):
        # The invariant is 'this file imports the canonical instructions',
        # not 'it is spelled the way the engine spells it'.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])

    def test_gemini_md_that_only_mentions_agents_warns(self):
        # A mention imports nothing: Gemini concatenates the file it reads and
        # follows '@' imports. 'See AGENTS.md' loads no instructions.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "See AGENTS.md for how this repo works.\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                and "does not import" in f.message
                                for f in findings))

    def test_gemini_absolute_import_does_not_satisfy(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", "@%s\n" % os.path.join(d, "AGENTS.md"))
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                for f in validate.check_root_files(d)))

    def test_symlinked_gemini_md_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            os.symlink(os.path.join(d, "AGENTS.md"), os.path.join(d, "GEMINI.md"))
            self.assertEqual(validate.check_root_files(d), [])

    def test_gemini_symlink_to_the_wrong_target_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "other.md", "# o\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            os.symlink(os.path.join(d, "other.md"), os.path.join(d, "GEMINI.md"))
            self.assertTrue(any(f.level == "WARN" and f.path == "GEMINI.md"
                                for f in validate.check_root_files(d)))

    def test_unreadable_gemini_md_does_not_accuse(self):
        # Slice 4.1's lesson, the paired direction: a diagnostic that cannot
        # see must say nothing rather than assert a fact it did not inspect.
        # The read failure is its own finding; no drift claim rides on it.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            with open(os.path.join(d, "GEMINI.md"), "wb") as fh:
                fh.write(b"\xff\xfe not utf-8 \xff")
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.path == "GEMINI.md" and "UTF-8" in f.message
                                for f in findings), "the read failure is silent")
            self.assertFalse(any("does not import" in f.message for f in findings),
                             "the check accused a file it could not read")

    def test_gemini_warn_fires_without_any_cursor_rules(self):
        # ORDERING PROBE, and it is the load-bearing one: the .cursor/rules
        # branch early-returns when the directory is absent. A GEMINI check
        # placed after it would be silent on exactly the repos that need it
        # most, with a green gate.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.path == "GEMINI.md" for f in findings),
                            "the GEMINI check sits after the .cursor early return")
            self.assertTrue(any("cursor" in f.path for f in findings))

    def test_engine_root_carries_its_gemini_pointer(self):
        # The 7-WARN trigger, asserted rather than assumed.
        self.assertEqual([f for f in validate.check_root_files(str(REPO))
                          if f.path == "GEMINI.md"], [])
```

- [ ] **Step 2: Fix the one pre-existing test the new WARN breaks.** `test_import_satisfies_the_check` asserts `check_root_files(d) == []` on a fixture with no `GEMINI.md`. Add one line:

```python
    def test_import_satisfies_the_check(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            _write(d, "GEMINI.md", GEMINI_POINTER)
            _write(d, ".cursor/rules/g.mdc", CURSOR_ALWAYS)
            self.assertEqual(validate.check_root_files(d), [])
```

> Planning-side survey of every `check_root_files` assertion in the suite says this is the **only** full-equality one that has an `AGENTS.md` and no `GEMINI.md`; every other assertion either filters to `ERROR` or uses `any(...)`. If the run says otherwise, list the additional tests in the commit message rather than loosening any of them.

- [ ] **Step 3: Extend `check_root_files`.** Widen the docstring and insert the block **immediately after the `CLAUDE.md` handling and immediately before `cdir = os.path.join(root, ".cursor", "rules")`**. The position is not cosmetic — see the ordering probe.

Docstring becomes:

```python
    """§6 root-file set. AGENTS.md is canonical and the other three root files
    are pointers at it. Claude Code reads CLAUDE.md and NOT AGENTS.md; Gemini
    CLI reads GEMINI.md and NOT AGENTS.md; Codex and Cursor read AGENTS.md
    natively (all four verified live 2026-07-29). So CLAUDE.md and GEMINI.md
    must each point at it, and an always-apply .cursor/rules/*.mdc must
    reference it.

    Severity split, deliberately: CLAUDE.md is an ERROR because two root files
    that each look canonical are two sources of truth, and that drift is what
    this check exists to catch. GEMINI.md and the Cursor pointer are WARNs —
    a missing pointer costs one harness's users the instructions, which is a
    completeness problem rather than a contradiction. Silent when there is no
    AGENTS.md: this checks a claim you make, not one you failed to make."""
```

Inserted block:

```python
    # Gemini CLI's default context filename is GEMINI.md, and it does not read
    # AGENTS.md — AGENTS.md loads only when context.fileName is configured in
    # settings.json (verified live 2026-07-29 against the first-party docs).
    # The context file supports '@path' imports, "both relative and absolute
    # paths", demonstrated as '@./file.md'.
    #
    # This sits BEFORE the .cursor/rules block on purpose: that block returns
    # early when the directory is absent, so a GEMINI check placed after it
    # would go silent on exactly the repos with the least harness wiring.
    gemini = os.path.join(root, "GEMINI.md")
    if not os.path.lexists(gemini):
        findings.append(Finding(
            "WARN", "GEMINI.md", None,
            "no GEMINI.md — Gemini CLI reads GEMINI.md, not AGENTS.md, so Gemini "
            "users get no route to the canonical instructions; add a GEMINI.md "
            "whose content is '@./AGENTS.md' (§6)"))
    elif os.path.islink(gemini):
        if os.path.realpath(gemini) != os.path.realpath(agents):
            findings.append(Finding(
                "WARN", "GEMINI.md", None,
                "GEMINI.md is a symlink that does not resolve to AGENTS.md — the "
                "Gemini pointer has drifted off the canonical instructions (§6)"))
    else:
        text, rd = _read_utf8(gemini, "GEMINI.md")
        findings += rd
        # A diagnostic that cannot see says nothing rather than accusing
        # (Slice 4.1): the read failure above is its own finding, and no drift
        # claim is made about content nobody read.
        if text is not None:
            targets = _IMPORT.findall(_strip_code(text))
            if not any(os.path.basename(t) == "AGENTS.md"
                       and not (os.path.isabs(t) or t.startswith("~"))
                       for t in targets):
                findings.append(Finding(
                    "WARN", "GEMINI.md", None,
                    "GEMINI.md does not import AGENTS.md — Gemini CLI loads this file "
                    "and would run on instructions that drifted from the canonical "
                    "ones; its content should be '@./AGENTS.md' (§6)"))
```

- [ ] **Step 4: Create `GEMINI.md`.** Exactly one line, mirroring `CLAUDE.md`:

```
@./AGENTS.md
```

> `CLAUDE.md` stays exactly `@AGENTS.md` — Claude Code's documented form, and `check_root_files` ERRORs on anything else as the first content line. The two files differ by three characters on purpose, and each matches its own harness's documented syntax.

- [ ] **Step 5: `interview/generate.md` — the manifest gains the file.** In the `## What you write` block, after the `CLAUDE.md` line:

```
  GEMINI.md                       one line: @./AGENTS.md
```

And in step 6 of "The order, and why it is this order", extend the sentence that already explains `CLAUDE.md`:

```markdown
`CLAUDE.md` is exactly `@AGENTS.md` on its own first content line, because Claude Code
reads `CLAUDE.md` and not `AGENTS.md`. `GEMINI.md` is `@./AGENTS.md` for the same reason —
Gemini CLI's default context filename is `GEMINI.md` and it does not read `AGENTS.md`
either (verified 2026-07-29). `.cursor/rules/company.mdc` carries `alwaysApply: true` and
references `AGENTS.md`. Codex and Cursor read `AGENTS.md` natively, so they need no
pointer.
```

- [ ] **Step 6: The end-to-end fixture builds the manifest, so it gains the file too.** In `TestGeneratedCompanyRepo._materialize`, beside the `CLAUDE.md` write:

```python
        with open(os.path.join(dest, "GEMINI.md"), "w", encoding="utf-8") as fh:
            fh.write("@./AGENTS.md\n")
```

Then the paired probe — an absence assertion next to the one that proves the same code path is loud on the same file class:

```python
    def test_manifest_repo_needs_no_gemini_warning(self):
        """Paired with the next test, which is what makes this one mean
        anything: a repo built to generate.md's manifest emits no
        harness-pointer WARN, and the same repo with GEMINI.md removed does."""
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            self.assertEqual(
                [f.message for f in validate.check_root_files(repo)
                 if f.path == "GEMINI.md"], [])

    def test_manifest_repo_without_gemini_md_warns(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            os.remove(os.path.join(repo, "GEMINI.md"))
            self.assertTrue(
                any(f.level == "WARN" and f.path == "GEMINI.md"
                    for f in validate.check_root_files(repo)),
                "the pointer check does not reach a company root")
```

- [ ] **Step 7: Gate, with the trigger checked rather than assumed**

```bash
python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -3
python3 scripts/validate.py . --diff main >/dev/null 2>&1 ; echo "diff exit: $?"
```

Expected: green with a count above 684; exactly `0 error(s), 7 warning(s)` and exit 0; `demo` at exactly `0 error(s), 2 warning(s)`; diff exit 0.

**If `validate.py .` shows 8 warnings**, `GEMINI.md` did not land or is not satisfying the check — fix the file, never the check. **If `validate.py demo` moved off 2**, the check is not honoring the silent-on-absent-`AGENTS.md` early return, which is the scoping-bug class this repo has hit twice.

Then the deliberate-red probe, proving the WARN is reachable on this repo and not just on fixtures:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import subprocess, sys, os, pathlib
p = pathlib.Path("GEMINI.md")
orig = p.read_text()
p.unlink()
try:
    out = subprocess.run([sys.executable, "scripts/validate.py", "."],
                         capture_output=True, text=True).stdout
finally:
    p.write_text(orig)
assert "GEMINI.md" in out and "8 warning(s)" in out, out[-800:]
print("OK: removing GEMINI.md takes the engine to 8 warnings and names the file")
PY
python3 scripts/validate.py . 2>&1 | tail -2
```

> The heredoc restores the file in a `finally` and the last line re-confirms 7 WARNs. `GEMINI.md` is data, not code, so no bytecode can survive the restore — `PYTHONDONTWRITEBYTECODE=1` is set anyway because 4.1's lesson is cheap to honor and expensive to skip.

- [ ] **Step 8: Commit**

```bash
git add GEMINI.md scripts/validate.py tests/test_validate.py interview/generate.md
git commit -m "feat(validate): the fourth root pointer — Gemini CLI reads GEMINI.md

Gemini CLI's default context filename is GEMINI.md and it does not read
AGENTS.md unless context.fileName is configured (verified live 2026-07-29).
Ships the one-line pointer, the missing-pointer WARN alongside the existing
Cursor one, and the manifest + fixture that keep a generated company repo
in the same shape.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: README Tier 2

**Files:** Modify `README.md`.

> The deliverable. Everything above `## How groundwork compares` is new or rewritten; that section and `## Prior art & inspiration` ship **byte-identical**, and `## License` is rewritten per design call 3.

- [ ] **Step 1: Replace `README.md` lines 1–9** (the H1 through the end of `## Status: building V1`) with the following. Leave line 10 onward — `## How groundwork compares` and everything below it — untouched for now; Step 2 handles the License section.

`````markdown
# groundwork

> The groundwork your company runs on.

An open-source, harness-agnostic **Company OS**. It is files, not an engine: markdown
conventions plus one zero-dependency validator, so any coding agent that reads a
repository can read this one. You point your agent here, it interviews your company about
the work each function actually does — what deserves **more** human time, what should be
**automated away**, and under **what rules** — and generates your operating system from
that map into a separate private repository: folder-per-function ontologies, skills with
named owners, a compiled constitution, and organizational memory that learns under
governance instead of rewriting itself.

## Not technical? Point your agent at this repo

One person who can use git. That is the whole technical requirement, and it is a real
requirement — everyone else receives skills and proposes changes in conversation.

1. **Clone this repository and open it in your coding agent** — Claude Code, Codex,
   Cursor, or Gemini CLI. Each loads [`AGENTS.md`](AGENTS.md) by its own convention:
   Claude Code through `CLAUDE.md`, Gemini CLI through `GEMINI.md`, Codex and Cursor
   natively. All four pointers are committed here, and `scripts/validate.py` checks that
   they still point at the same file.
2. **Say this:** *"Read AGENTS.md, then walk me through `demo/walkthrough.md`."* Fifteen
   minutes, three questions, no credentials.
3. **Then say this:** *"Interview me by following `interview/`, and generate our OS into a
   new private repository."* The agent asks one question at a time, and where an answer
   can only come from a person it stops instead of guessing.

Nothing to install, no server, no signup. The one command anyone runs is
`python3 scripts/validate.py`.

## See it work first — fifteen minutes, no credentials

[`demo/walkthrough.md`](demo/walkthrough.md) is a pre-installed fictional twenty-person
company. Three questions, in order:

1. **A decision lookup.** Why engineering moved to asynchronous standups, who decided it,
   and what it replaced. The answer has a name and a date on it, the reasoning includes
   what was given up, and the superseded decision is still readable rather than deleted.
2. **A cross-function synthesis.** Which renewals are at risk because of unbuilt product
   work, and how much contract value is exposed. Nobody wrote that answer down — it lives
   across two functions' records, and the ontology is what makes them addressable
   together.
3. **A skill, and a refusal.** Ask for a performance-review evidence pack and you get a
   description of one. Then ask the agent to write the assessment itself, and it refuses —
   naming the rule, the owner, the appeal path, and what it *can* do instead — then points
   at the pending proposal somebody filed the last time this happened.

**What the walkthrough is honest about, and so is this page.** That refusal is
instruction-strength, not a runtime block: no hook enforces it, and the demo says so at
the exact moment overstating it would be most tempting. The company is fictional and
nothing is connected, so no skill there can actually run. Agents do not reliably
auto-select a skill from a description, so you may have to point at the file. And these
are three questions asked of a language model — the walkthrough tells you what a good
answer contains, not a transcript to match.

## The interview, and what it writes

**It is documents, not a program.** There is no `generate.py`. [`interview/`](interview/)
holds four things an agent follows: a resumable state format where "confirmed" is git
structure rather than a label an agent can edit, the consultant protocol (define the role
first, one question at a time, no generation until understanding is complete), a
nine-section question skeleton in which every question names the field its answer fills,
and the generation protocol with the manifest of what a company repo contains.

Five fields the generator refuses to invent: the owner, the backup owner, the forbidden
actions, and the two death conditions. An invented owner is an accountability structure
the named person discovers when something goes wrong.

Your OS lands in a **separate private repository**. This clone stays a pull-only engine;
nothing organizational is ever written into it, upstream improvements arrive by
`git pull` here, and your content is never re-copied — see [`AGENTS.md`](AGENTS.md) ("Two
repos") and [`MIGRATIONS.md`](MIGRATIONS.md) for the version-pin contract that makes
pulling safe.

The generator is a protocol rather than a script because its input is prose written by a
person and an agent in conversation, and a parser for that has an unbounded supply of
ways to be wrong. What makes it trustworthy is the gate at the end — and this repository's
own test suite builds a company repo from the manifest and proves the gate passes on it.

## Check what you have

```
python3 scripts/validate.py .
```

Python 3 standard library only. No dependencies, no `requirements.txt`, and a test that
fails if a shipped script ever imports one. Exit 0 means no ERRORs; WARNs print and do not
fail. To check the OS you generated, pass its path instead:

```
python3 scripts/validate.py ../acme-os
python3 scripts/validate.py ../acme-os --diff main
```

The first run checks structure and referential integrity, the two ontology tiers, every
Owner's Card against its ontology's owner and source of truth, every constitution rule
against the safety invariant that no rule may end in automation, every memory record's
provenance and supersession chain, a high-signal secrets floor, and the always-loaded
context budget. The second adds the stateful rules: organizational memory is
append-and-supersede rather than editable, confirmed interview layers are frozen, and a
change to a rule or a high-risk skill must carry a matching pending proposal or the gate
ERRORs.

**What it does not prove.** The secrets floor is high-signal, not exhaustive. Nothing
checks prose — the validator can confirm every required field is answered and cannot tell
you the answer is true. [`docs/known-limitations.md`](docs/known-limitations.md) is the
full list, written to be read before you rely on a check rather than after.

## Getting it in front of people

[`delivery/`](delivery/) is the provisioning guide: the repo-local symlink layer that
gives your generated skills a path each harness reads, the organization plugin paths for
people who never touch git, and how to install the runnable action-class gate — with the
re-copy obligation that comes with it. Nothing in groundwork zips, uploads, or syncs
anything; these are steps a maintainer runs, and every external fact in the guide carries
the date it was verified, because all of these surfaces move.

## Status

V1 is nearly complete, and this is the ledger.

**Working today:** the schema as files with `scripts/validate.py` gating every layer of
it; eight function ontologies plus worked deep records on both governance tracks,
including one recording a deliberate decision *not* to automate; work packages with
Owner's Cards; a typed constitution on a five-rung enforcement ladder, with one runnable
exemplar and prose degradation everywhere else; organizational memory with provenance and
supersession; the consent gate and its blast-radius tripwire; the interview and generation
protocols; the complete `demo/` company and its walkthrough; and the provisioning guide.

**Not here yet:** the `LICENSE` file, a security-and-privacy section, and a versioned
roadmap. [`CONTEXT.md`](CONTEXT.md) is the glossary of all nineteen resolved design
decisions; [`AGENTS.md`](AGENTS.md) carries the current built / not-built list and is
always the more current of the two.
`````

- [ ] **Step 2: Rewrite the `## License` section** (design call 3) in place, leaving `## How groundwork compares` above it and `## Prior art & inspiration` below it untouched:

```markdown
## License

Apache-2.0 — chosen for its patent grant (enterprise-counsel comfort). The `LICENSE` file
lands with the first release artifacts.

**Your content is yours.** The operating system the interview generates is the adopter's
own work and is **not** covered by groundwork's license. That is not only a statement
here: [`interview/generate.md`](interview/generate.md) instructs the generator to write
the same carve-out into the company repository's own root instruction file, so the
repository holding your content is the one that says whose it is.
```

- [ ] **Step 3: Prove the two locked sections did not move.** They are content #14 and #15 grilled to a verdict, and a rewrite is exactly when a phrase quietly changes:

```bash
git diff main -- README.md | grep -E "^[-+]" | grep -iE "sylph|clawcompany|Jiaona|Stulberg|Aakash|Nate|dswh|Open Brain|prior art|maintenance-slowed"
```

Expected output: **nothing.** Any line here means a locked concession, credit, or paid/free statement changed — revert that line. Then confirm the sections are still there and still in order:

```bash
grep -n "^## " README.md
```

Expected order: `Not technical?` → `See it work first` → `The interview, and what it writes` → `Check what you have` → `Getting it in front of people` → `Status` → `How groundwork compares` → `License` → `Prior art & inspiration`.

- [ ] **Step 4: Gate, plus the two README-specific measurements**

```bash
python3 scripts/validate.py . ; echo "exit: $?"
```

Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Every relative link in the new README must resolve — `AGENTS.md`, `CONTEXT.md`, `MIGRATIONS.md`, `demo/walkthrough.md`, `interview/`, `interview/generate.md`, `delivery/`, `docs/known-limitations.md`.

Then measure the entropy risk directly rather than hoping:

```bash
python3 - <<'PY'
import sys
sys.path.insert(0, 'scripts')
import validate
print([ (f.level, f.path, f.message) for f in validate.check_entropy('.')
        if f.path.startswith('README') ])
PY
```

Expected: `[]`. A hit means a link path or token in the new prose crossed the 40-character / 4.0-bit line; shorten the path.

- [ ] **Step 5: Prove the README is actually in the link corpus** (deliberate red, then revert). A green gate on a file the checker never opened is indistinguishable from a green gate on a clean file:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import subprocess, sys, pathlib
p = pathlib.Path("README.md")
orig = p.read_text()
p.write_text(orig.replace("(docs/known-limitations.md)",
                          "(docs/known-limitations-typo.md)", 1))
try:
    r = subprocess.run([sys.executable, "scripts/validate.py", "."],
                       capture_output=True, text=True)
finally:
    p.write_text(orig)
assert r.returncode != 0 and "README.md" in r.stdout, r.stdout[-800:]
print("OK: a broken README link fails the gate and names README.md")
PY
python3 scripts/validate.py . 2>&1 | tail -2
```

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "docs(readme): Tier 2 — capability claims turn on, each with its anchor

The 'Not technical? Point your agent at this repo' first-section move, the
demo walkthrough, the interview, validate usage, and provisioning. Every
claim traces to a file or a test; the walkthrough's three honest limits
travel with it. Positioning (#15) and prior art (#14) unchanged. License
now describes the carve-out that exists rather than promising one.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The honesty sweep

**Files:** Modify `AGENTS.md`, `interview/generate.md`, `docs/known-limitations.md`.

> Design call 4's table, executed. Every file that mentions something Tasks 1 and 2 promoted.

- [ ] **Step 1: `AGENTS.md` — the status paragraph.** Lines 13–16 still describe Phase 2.2. Replace that paragraph with:

```markdown
The design is fully charted (19 resolved decisions; see `CONTEXT.md`). Phases 1 through 3
are complete and Phase 4 is closing it out: the schema exists as files, three functions
are worked end to end across both governance tracks, one function records a deliberate
non-automation verdict, the interview and its generator exist as documents, `demo/` is a
complete governed company, and the validator gates every layer of it.
```

- [ ] **Step 2: `AGENTS.md` — the `delivery/` verb** (design call 2). Line 44's bullet becomes:

```markdown
- `delivery/` — the provisioning guide: the repo-local symlink layer that gives generated
  skills a harness-visible path in all four harnesses, the organization plugin upload and
  GitHub-synced marketplace paths, and how to install the runnable action-class gate with
  the re-copy obligation that comes with it. Every external fact carries the date it was
  verified, and the guide says which symlink shape was tested head-to-head and which was
  not.
```

- [ ] **Step 3: `AGENTS.md` — "Not built yet" loses the README bullet.** Delete `- The README's capability claims (Tier 2). Phase 4.2.` The section then holds `your-company/` alone, so reword the surviving bullet to stand on its own and add the one thing that is genuinely still missing:

```markdown
**Not built yet — do not describe these as working:**

- `your-company/` — a generated company OS lives in a **separate private repo**, never
  here. There is no directory to look at; `demo/` is what a generated repo looks like.
- The `LICENSE` file, the security-and-privacy section, and the versioned roadmap.
  Phase 4.3.
```

- [ ] **Step 4: `AGENTS.md` — the root-file sentence gains the fourth pointer.** Lines 7–9:

```markdown
This file is the canonical instruction surface for agents working in or with this
repository. `CLAUDE.md`, `GEMINI.md`, and `.cursor/rules/groundwork.mdc` are pointers at
it — Claude Code reads `CLAUDE.md` and Gemini CLI reads `GEMINI.md`, neither of them
reads this file, and Codex and Cursor read it natively. Edit **this** file; the validator
checks that the pointers still resolve here.
```

> **`wc -l AGENTS.md` must stay under 200.** It is at 157 and these edits are roughly net-neutral.

- [ ] **Step 5: `interview/generate.md:176` — the carried 4.1 finding.** Drop the stale clause:

```markdown
Installing the runnable gate is a deliberate maintainer act with a re-copy obligation
attached — the provisioning guide covers it (`delivery/`).
```

- [ ] **Step 6: `interview/generate.md` — the License carve-out** (design call 3). Append to step 6, "The root files":

```markdown
**One more line in `AGENTS.md`, and it is a legal one.** State that the contents of this
repository are the company's own work, generated with groundwork and not covered by
groundwork's Apache-2.0 license. groundwork's own README says this; the promise is only
worth something if the repository holding the content says it too, which is why it is
written here rather than assumed.
```

- [ ] **Step 7: `docs/known-limitations.md` — three updates.**

(a) The always-loaded-surface bullet at line 78 enumerates its contributors. Add the pointer and say plainly that it is not counted:

```markdown
- **The always-loaded set is a model of four harnesses, not a measurement of one.** It
  covers the root `AGENTS.md`, `CLAUDE.md` and its imports, unscoped `.claude/rules/`,
  always-apply `.cursor/rules/`, and skill descriptions capped at Claude Code's 1,536-char
  listing truncation. The root `GEMINI.md` pointer is **not** separately counted: it is a
  one-line import of `AGENTS.md`, which is already in the total, so Gemini CLI's real
  always-loaded surface is the measured figure plus twelve bytes. Harnesses also differ in
  what else they preload (MCP tool names, system prompts); those are outside the repo and
  outside this check.
```

(b) In the `## Context budget (#13)` section or wherever the root-file discussion sits, add the harness-pointer limit:

```markdown
- **Three of the four root files are pointers, and only one of them is an ERROR.** A
  missing or drifted `CLAUDE.md` is an ERROR because two root files that each look
  canonical are two sources of truth. A missing `GEMINI.md` or `.cursor/rules/*.mdc`
  pointer is a WARN, so a repository can ship with one harness's users getting no
  instructions at all and still pass the gate. Verified 2026-07-29: Claude Code reads
  `CLAUDE.md` and Gemini CLI reads `GEMINI.md`; neither reads `AGENTS.md`, and Gemini
  loads `AGENTS.md` only if `context.fileName` is configured — a setting no repository
  can supply for its readers.
```

(c) Append to the `## Provisioning (delivery/)` section:

```markdown
- **The symlink shape the guide prints is one hop away from the shape that was tested.**
  The head-to-head A/B (2026-07-18) pointed `.claude/skills/<name>` at a real skill
  directory under `.agents/skills/`; a generated company repo keeps its work packages at
  `skills/<name>/`, because `iter_files` skips dot-directories and skills living under a
  dot-directory would be invisible to the validator. So some extra hop is unavoidable and
  the guide names the untested one, with the `/doctor` check and the tested fallback next
  to it. Nothing in this repository can test another harness's discovery.
```

- [ ] **Step 8: The full gate**

```bash
python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py . --diff main >/dev/null 2>&1 ; echo "diff exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -3
wc -l AGENTS.md
```

Expected: green above 684; exactly `0 error(s), 7 warning(s)` exit 0; diff exit 0; `demo` at `0 error(s), 2 warning(s)`; `AGENTS.md` under 200.

Then the cross-file honesty sweep — the one grep that catches the failure this repo has now shipped three times:

```bash
grep -rn "not built yet\|Tier 2\|Phase 4.2\|will ship with the generator" \
  --include="*.md" . | grep -v "^./docs/superpowers" | grep -v "^./research"
```

Expected: **no hits outside `docs/superpowers/` and `research/`.** A hit in `AGENTS.md`, `README.md`, `interview/`, `docs/`, or `demo/` is a sibling file contradicting this slice.

And the claims audit, run by hand and reported in the commit message: for each capability sentence in the new README, name the file or test it points at. The table in design call 5 is the checklist. If a sentence has no anchor, cut the sentence — do not go find an anchor for it.

- [ ] **Step 9: Commit**

```bash
git add AGENTS.md interview/generate.md docs/known-limitations.md
git commit -m "docs: the README's claims are on, and every sibling file agrees

AGENTS.md's status paragraph catches up three phases, 'all four harnesses'
becomes the structural claim that was actually verified, and 'Not built yet'
loses the README bullet. generate.md stops calling delivery/ unbuilt and
gains the license carve-out the generator's arrival made due. Three new
known limitations: the WARN-level harness pointers, the GEMINI.md byte the
budget does not count, and why the tested symlink shape is one hop away.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No `LICENSE` file.** Slice **4.3**, and both `README.md` and `AGENTS.md` now say so by name rather than by promise.
- **No security-and-privacy section and no versioned roadmap.** Slice **4.3**, which also audits `docs/known-limitations.md` against the V1 success criteria rather than rewriting it, and then walks those criteria one by one.
- **No `demo/` changes.** It is a governed root and nothing in this slice needs it.
- **No `check_always_loaded_budget` change.** `GEMINI.md` is a twelve-byte import of a file already counted, so under the locked max-across-harnesses model the aggregate is correct to within twelve bytes. The honest move is the written limitation in Task 3, not code — and saying so is cheaper than a check nobody needs.
- **No Cursor or Codex root-file change.** Both read `AGENTS.md` natively; re-verified live 2026-07-29 (Cursor: "Place it in your project root as an alternative to `.cursor/rules`"; Codex's chain and its 32 KiB `project_doc_max_bytes` cap were first-party-verified 2026-07-27 and are already encoded in `check_agents_chain`). The Codex re-check this session went through a search summary, not a first-party page, so **nothing from it is quoted in a shipped artifact** — 3.2's rule.
- **Still open for the maintainer:** Codex's 3.1 finding 1 (should an absent `layers:` key ERROR); the health-metrics v2 candidate; the 3.3 hook-set call; three Slice 1.5d-ii deferrals; the `SKIP_RELPATHS` sign-off; the standing re-review rule; the `Motion: assist` reading; #21's `since:` retrofit; whether groundwork dogfoods its own hook set. *(The carried "`gh issue close 10`" item was struck 2026-07-29 — #10 was already closed at charting time; the to-do had been carried unverified through three log entries.)*

## Self-Review

- **Ticket coverage.** Brief §4 step 1 is Task 2's first section, verbatim in intent — "Not technical? Point your agent at this repo," and it is genuinely first. #15's comparison and #14's credit block are carried untouched and **verified by grep rather than by reading**, because a rewrite is exactly when a grilled concession quietly softens. #3's carve-out promise is paid where it was owed. The demo walkthrough and `validate` usage are the spec's other two 4.2 items, each with a section.
- **Four external contracts fetched live 2026-07-29, and one of them changed the artifact.** Gemini CLI (two independent sources agreeing: default `GEMINI.md`, `AGENTS.md` only via `context.fileName`, `@./file.md` imports) produced Task 1 outright. Cursor confirmed root `AGENTS.md` support and the `.mdc` requirement. Claude Code re-confirmed `CLAUDE.md`-not-`AGENTS.md`, the `@path` import, and the four-hop depth. Codex was re-checked only through a search summary, which is why nothing from it is quoted anywhere in this slice's output. **Fifth time in this build that fetching the live contract changed the artifact.**
- **The design calls are surfaced with their costs.** Five, including the one that is a scope *expansion* into `validate.py` during what would otherwise be a content slice; the one where the tempting fix was investigated and **rejected on evidence** (the two-hop shape is not the verified shape either, because the verified shape had a real directory where the manifest puts a symlink); and the one where the honest reading is that a promise was unpaid rather than merely due.
- **Anti-hollow probes, and the absence-assertions come in pairs.** The ordering probe (`test_gemini_warn_fires_without_any_cursor_rules`) is the load-bearing one — the `.cursor/rules` branch early-returns, so a check placed after it would be silent on the least-wired repos with a green gate. `test_manifest_repo_needs_no_gemini_warning` asserts an absence and is paired with `test_manifest_repo_without_gemini_md_warns` on the same fixture, which is the only thing that makes the absence mean anything. Two live deliberate-reds: removing `GEMINI.md` must take the engine to 8 WARNs and name the file, and breaking one README link must fail the gate and name `README.md` — the second proves the README is in the link corpus at all, which is the "what does the scanner SEE" surface. Plus `test_unreadable_gemini_md_does_not_accuse`, which is 4.1's lesson pointed the other way.
- **The trigger is checked, not assumed.** `test_engine_root_carries_its_gemini_pointer` asserts the 7-WARN invariant's precondition directly, and Step 7 says what each possible movement means: 8 WARNs is a missing file, a moved `demo` count is the scoping-bug class.
- **`demo` is a named tripwire.** `check_root_files` is silent without an `AGENTS.md` and `demo/` has none, so `validate.py demo` must stay at `0 error(s), 2 warning(s)`. That is asserted in two tasks rather than assumed once.
- **Every file that mentions a promoted thing is on the list, and the list came from a grep.** Eight entries in design call 4's table, plus a closing grep in Task 3 Step 8 that fails the sweep if any survive. This is the fourth consecutive slice to face this failure mode and the first to carry both a pre-built table and a post-hoc grep.
- **The honesty risk is named as an understatement risk, not an overclaim risk.** The three hedges that must survive editing — instruction-strength refusal, unreliable auto-invocation, documents-not-a-program — are listed in the Global Constraints as the failure mode, because in a slice whose job is turning claims on, the loss is not a false sentence added but a true qualifier smoothed away.
- **No stale numbers in shipped content.** The README carries no test count, star count, or commit sha, on purpose: the plan's own baseline numbers are gate tripwires for the builder and belong in the plan, not in the product.
- **Placeholder scan:** no TBD/TODO. The README is given in full, the check is given in full, all thirteen tests are given in full, and every prose modification quotes its replacement text.
- **Type consistency:** `check_root_files(root)` keeps its signature and its wiring; `Finding(level, path, line, message)` and the `_read_utf8` / `_IMPORT` / `_strip_code` helpers are reused, not reimplemented. No new grammar, no second parser.
