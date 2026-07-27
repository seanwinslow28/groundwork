# groundwork V1 — Slice 2.1: the remaining 7 executive-view ontologies (+ two deferral folds) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open Phase 2 (horizontal fill) by authoring the **7 remaining executive-view ontologies** — sales, customer success, marketing, product, engineering, finance, legal — completing #5's exec tier across all 8 functions. Fold in the two deferral sets that this content directly amplifies: the **Move 2 Codex deferrals** (`_strip_code` fence handling, aggregate double-counting, absolute-import message) and the **Slice 1.2 exec-table deferrals** (a misspelled `Direction` header currently disables every check in the file — a fail-open that scales 8× with this slice).

**Architecture:** No new schema. #5's exec tier is "every activity, carrying only its name and Direction" — one `_executive-view.md` per function directory, a markdown table with `Activity | Direction | Deep record`. Deep records are *not* authored here (depth is earned by acting; 2.2 deepens CS renewal-prep and PM feature-request-triage). The validator work is hardening only: `parse_exec_table` and `check_ontology` become fail-closed on malformed tables, and the Move 2 budget/drift helpers get their edge cases closed.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports in this slice. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **#5 severity contract — do not exceed it.** ERROR exactly when a field backs (or is about to back) running machinery; WARN on incomplete thinking about an acted-on activity; **silent** on untouched worksheets. A function with an executive view and no deep records is *silent* — the 7 new functions must add **zero** findings.
- **Engine repo ≠ generated company.** These ontologies are **engine exemplars** — a starting map an adopter edits, not claims about anyone's company. Each file must say so (Design call 3).
- **Codebase conventions:** reuse `Finding`, `_read_utf8`, `_load_frontmatter`, `_ignored`, `DIRECTIONS`, `_LINK`. Checks take `(root, ignore=())` and honor `.gitignore` parity.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

D2 Move 2 merged to `main` (done: `8a0956d`; 378 tests, 1 designed skip, gate exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.1-executive-views
```

---

## Design calls flagged for the maintainer

**1. Both Move 2 deferrals are folded in, not left to rot — and the `_strip_code` one is a genuine fail-open, not a nit.**
Fable recommended deferring the `_strip_code` regex fix. I disagree on one specific ground, and it is worth stating precisely. The current `_strip_code` handles **only** ` ``` ` fences. A CommonMark **tilde** fence is a fenced code block, so Claude Code's import parser skips it — but our regex does not. A `CLAUDE.md` that merely *documents* the import inside a `~~~` block therefore **satisfies the drift check while Claude Code imports nothing**. That is silent root-file drift passing an ERROR-level guarantee — the exact failure `check_root_files` exists to prevent. Fable's own counter-argument ("a guarantee a contrived file can bypass is weaker than it looks") is the right read. The fix is ~35 lines of line-based scanning and it lands here.
*The unavoidable tension, decided:* the two consumers of `_strip_code` want **opposite** safe directions. For the **drift check**, over-stripping is safe (we miss an import → false ERROR, loud) and under-stripping is fail-open (we see a fake import → silent drift). For the **budget**, it inverts (over-stripping undercounts). **Tiebreak: over-strip**, because the drift guarantee is ERROR-level and the budget is a WARN threshold. A consequence to accept knowingly: a backslash-escaped backtick (`` \` ``) is treated as opening a code span, so an import next to one reads as absent → false drift ERROR. Loud, rare, and on the safe side. Documented in `docs/known-limitations.md`.

**2. Fable's own observation — the aggregate counts `AGENTS.md` twice — is a real defect, and it is folded in.**
In this repo the always-loaded aggregate counts `AGENTS.md` once as the root instruction file and again as `CLAUDE.md`'s import. Fable framed it as a conservative overcount. It is conservative in *direction* but wrong in *model*: no single harness loads the file twice — Codex loads `AGENTS.md`, Claude Code loads `CLAUDE.md` → `AGENTS.md`. The honest model is **max across harnesses**, not union-with-duplicates. It matters because the aggregate's upper threshold is an **ERROR** that fails the gate: a company repo whose `AGENTS.md` is most of its always-loaded surface could be pushed past 50K est. tokens by pure double-counting and be blocked for a budget it does not actually spend. Fix: dedupe by realpath across all four contributors.

**3. Absolute in-repo imports: keep the ERROR, fix the message.**
Fable recommended leaving `@/abs/path/AGENTS.md` as-is. I agree with the *outcome* and disagree with the *wording*. An absolute path committed in a repo resolves only on the machine that wrote it, so failing is correct — but calling it "drift" misdiagnoses it and sends the reader looking for the wrong problem. This slice keeps the ERROR and gives it its own message. No behavior change, no new code path.

**4. The 7 exec views are labelled as starting templates, not claims about anyone's company.**
Each of these files ships an opinionated Direction for every activity ("Recruiting & candidate screening: down"). That is useful as a default map and false as an assertion about a specific company. The locked convention already says root `ontologies/` are engine exemplars — but nothing in the files says so, and an adopter's agent reading them has no way to know. Each file gets a one-paragraph frame, and **`people-hr/_executive-view.md` is retrofitted with the same frame** so the eight are consistent. *Counter-argument:* it is prose the generator will overwrite anyway. Accepted — it costs four lines and it is the difference between a template and an unmarked claim.

---

## File Structure

- `scripts/validate.py` — **modify.** Replace `_strip_code` with a fence-aware scanner (+ `_strip_spans`, `_FENCE`); dedupe `_always_loaded_bytes` by realpath; add the absolute-import message to `check_root_files`; harden `parse_exec_table` (escaped pipes) and `check_ontology` (unparsable table ERROR, empty Activity cell ERROR, non-regular-file guard, path-based orphan matching).
- `tests/test_validate.py` — **modify.** `TestStripCode`, `TestAggregateDedupe`, `TestExecTableHardening`, `TestOntologyFileSafety` added; existing `TestExecTable` / `TestOntology` unchanged.
- `ontologies/sales/_executive-view.md` — **create.**
- `ontologies/customer-success/_executive-view.md` — **create.**
- `ontologies/marketing/_executive-view.md` — **create.**
- `ontologies/product/_executive-view.md` — **create.**
- `ontologies/engineering/_executive-view.md` — **create.**
- `ontologies/finance/_executive-view.md` — **create.**
- `ontologies/legal/_executive-view.md` — **create.**
- `ontologies/people-hr/_executive-view.md` — **modify.** Add the same template frame.
- `ontologies/README.md` — **create.** The exec-tier convention in one page.
- `AGENTS.md` — **modify.** The repo map's `ontologies/` row now covers 8 functions.
- `docs/known-limitations.md` — **modify.** The `_strip_code` over-strip bias.

---

## Task 1: Fold in the Move 2 deferrals

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestStripCode(unittest.TestCase):
    def _imports(self, text):
        return validate._IMPORT.findall(validate._strip_code(text))

    def test_plain_import_is_seen(self):
        self.assertEqual(self._imports("@AGENTS.md\n"), ["AGENTS.md"])

    def test_backtick_fence_is_stripped(self):
        self.assertEqual(self._imports("```\n@AGENTS.md\n```\n"), [])

    def test_tilde_fence_is_stripped(self):
        # The fail-open this fold closes: a ~~~ block is a CommonMark fenced
        # code block, so Claude Code imports nothing from it.
        self.assertEqual(self._imports("~~~\n@AGENTS.md\n~~~\n"), [])

    def test_four_backtick_fence_is_stripped(self):
        self.assertEqual(self._imports("````\n@AGENTS.md\n````\n"), [])

    def test_fence_with_info_string_is_stripped(self):
        self.assertEqual(self._imports("```markdown\n@AGENTS.md\n```\n"), [])

    def test_inner_shorter_fence_does_not_close_outer(self):
        self.assertEqual(self._imports("````\n```\n@AGENTS.md\n```\n````\n"), [])

    def test_single_backtick_span_is_stripped(self):
        self.assertEqual(self._imports("Write `@AGENTS.md` here.\n"), [])

    def test_double_backtick_span_is_stripped(self):
        self.assertEqual(self._imports("Write ``@AGENTS.md`` here.\n"), [])

    def test_unclosed_span_leaves_text(self):
        # An unterminated backtick run is literal text, so the import is real.
        self.assertEqual(self._imports("A ` stray tick then @AGENTS.md\n"), ["AGENTS.md"])

    def test_import_after_a_closed_fence_is_seen(self):
        self.assertEqual(self._imports("```\ncode\n```\n@AGENTS.md\n"), ["AGENTS.md"])

    def test_unclosed_fence_swallows_to_end(self):
        # Matches CommonMark: an unclosed fence runs to end of document.
        self.assertEqual(self._imports("```\n@AGENTS.md\n"), [])


class TestAggregateDedupe(unittest.TestCase):
    def test_agents_md_counted_once(self):
        # AGENTS.md is both the root instruction file and CLAUDE.md's import.
        # No harness loads it twice; double-counting can only push a legitimate
        # repo past an ERROR threshold.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * 4000)
            _write(d, "CLAUDE.md", "@AGENTS.md\n")
            items = validate._always_loaded_bytes(d)
            paths = [lbl for lbl, _n in items]
            self.assertEqual(len(paths), len(set(paths)))
            self.assertEqual(sum(n for _l, n in items), 4000 + len("@AGENTS.md\n"))

    def test_symlinked_duplicate_counted_once(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "x" * 4000)
            _write(d, "CLAUDE.md", "@alias.md\n")
            os.symlink(os.path.join(d, "AGENTS.md"), os.path.join(d, "alias.md"))
            total = sum(n for _l, n in validate._always_loaded_bytes(d))
            self.assertEqual(total, 4000 + len("@alias.md\n"))


class TestAbsoluteImportMessage(unittest.TestCase):
    def test_absolute_import_gets_its_own_message(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "AGENTS.md", "# a\n")
            _write(d, "CLAUDE.md", "@%s\n" % os.path.join(d, "AGENTS.md"))
            findings = validate.check_root_files(d)
            self.assertTrue(any(f.level == "ERROR" and "absolute" in f.message
                                for f in findings))
            self.assertFalse(any("drifted" in f.message for f in findings))
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestStripCode -v`
Expected: FAIL — the tilde-fence, four-backtick, and double-backtick-span tests fail against the current regex.

- [ ] **Step 3: Replace `_strip_code`** in `scripts/validate.py`. Delete the existing three-line function and put this in its place:

```python
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def _strip_spans(line):
    """Remove inline code spans: a run of N backticks closed by a run of exactly
    N. An unterminated run is literal text and is kept."""
    out = []
    i = 0
    while i < len(line):
        if line[i] != "`":
            out.append(line[i])
            i += 1
            continue
        n = 0
        while i + n < len(line) and line[i + n] == "`":
            n += 1
        close = line.find("`" * n, i + n)
        # the closing run must be EXACTLY n backticks, not part of a longer run
        while close != -1 and close + n < len(line) and line[close + n] == "`":
            close = line.find("`" * n, close + n + 1)
        if close == -1:
            out.append(line[i:i + n])
            i += n
        else:
            i = close + n
    return "".join(out)


def _strip_code(text):
    """Blank out fenced code blocks and inline code spans, the way a CommonMark
    reader does — Claude Code's import parser "skips Markdown code spans and
    fenced code blocks".

    Why a scanner and not a regex: a regex that knows only ``` fences fails
    OPEN. An `@AGENTS.md` inside a ~~~ block would be read as a real import, so
    a CLAUDE.md that merely *documents* the import would satisfy the root-file
    drift check while Claude Code loaded nothing.

    Deliberate bias: when the two consumers disagree, OVER-strip. Missing a real
    import makes the drift check ERROR (loud, safe); seeing a fake one makes it
    pass (silent drift). The cost is that a backslash-escaped backtick reads as
    opening a span — documented in docs/known-limitations.md."""
    out = []
    fence = None  # (char, length) of the currently open fence
    for line in text.split("\n"):
        m = _FENCE.match(line)
        if fence is None:
            if m:
                fence = (m.group(1)[0], len(m.group(1)))
                out.append("")
                continue
            out.append(_strip_spans(line))
        else:
            # a closing fence: same character, at least as long, no info string
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and not m.group(2).strip():
                fence = None
            out.append("")
    return "\n".join(out)
```

- [ ] **Step 4: Dedupe the aggregate.** In `_always_loaded_bytes`, replace the import-tracking `seen` set with a single `counted` set of realpaths shared by every contributor.

Immediately after `root_real = os.path.realpath(root)`, the accumulator becomes:

```python
    counted = set()

    def _take(abspath, rel_label, num_bytes):
        """Count a file once. AGENTS.md is reachable both as the root
        instruction file and as CLAUDE.md's import; no harness loads it twice,
        and double-counting can only push a legitimate repo past the ERROR
        threshold."""
        real = os.path.realpath(abspath)
        if real in counted or not num_bytes:
            return False
        counted.add(real)
        items.append((rel_label, num_bytes))
        return True
```

Move the root-`AGENTS.md` block to use it, so ordering puts the root file in `counted` before imports are followed:

```python
    f = _agents_file(root)
    if f is not None:
        n = _file_size(f)
        if n is None:
            items.append((os.path.relpath(f, root), AGENTS_CHAIN_MAX_BYTES))
        else:
            _take(f, os.path.relpath(f, root), n)
```

> Keep the existing fail-closed branch for an unreadable root instruction file exactly as Codex round 2 left it — do not regress it into a silent skip.

In `add_import`, replace the `seen` guard and the `items.append(...)` with `_take`, keeping the breadth-first expansion Codex round 2 introduced:

```python
        rel = os.path.relpath(abspath, root)
        text, rd = _read_utf8(abspath, rel)
        if text is None:
            findings_out.extend(rd)
            return
        if not _take(abspath, rel, len(text.encode("utf-8"))):
            return
```

and in the rules and skills loops replace each `items.append((rel, n))` / description append with the corresponding `_take(abspath, rel, n)` call. For the skill description, key on the `SKILL.md` path with a distinct label so a skill whose body is already counted elsewhere still contributes its description:

```python
            if isinstance(desc, str) and desc.strip():
                items.append((rel + " (description)",
                              min(len(desc), SKILL_DESCRIPTION_CAP)))
```

> The description stays a plain `items.append` — it is measured in **characters** (Codex round 1 fixed this) and is not a file, so it has no realpath to dedupe on.

- [ ] **Step 5: Give the absolute import its own message.** In `check_root_files`, replace the final `else:` branch's drift finding with:

```python
        text, rd = _read_utf8(claude, "CLAUDE.md")
        findings += rd
        if text is not None:
            targets = _IMPORT.findall(_strip_code(text))
            if not any(os.path.normpath(t.replace("\\", "/")) == "AGENTS.md"
                       for t in targets):
                abs_agents = [t for t in targets
                              if (os.path.isabs(t) or t.startswith("~"))
                              and os.path.basename(t) == "AGENTS.md"]
                if abs_agents:
                    findings.append(Finding(
                        "ERROR", "CLAUDE.md", None,
                        "CLAUDE.md imports AGENTS.md by absolute path (%s) — that resolves "
                        "only on the machine that wrote it; use the repo-relative "
                        "'@AGENTS.md' (§6)" % abs_agents[0]))
                else:
                    findings.append(Finding(
                        "ERROR", "CLAUDE.md", None,
                        "CLAUDE.md does not import AGENTS.md — the root files have drifted "
                        "into separate sources of truth; its content should be "
                        "'@AGENTS.md' (§6)"))
```

- [ ] **Step 6: Run tests + gate**

Run: `python3 -m unittest tests.test_validate.TestStripCode tests.test_validate.TestAggregateDedupe tests.test_validate.TestAbsoluteImportMessage tests.test_validate.TestAlwaysLoadedBudget tests.test_validate.TestRootFiles -v`
Expected: PASS — including every pre-existing Move 2 test (they are the regression proof that the scanner and the dedupe did not change legitimate behavior).

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s)`, exit 0.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "fix(validate): fence-aware _strip_code, realpath-dedupe the always-loaded aggregate

Closes the Move 2 deferrals: a ~~~ or 4-backtick fenced @AGENTS.md no longer
satisfies the drift check (fail-open), AGENTS.md is counted once not twice, and
an absolute import gets its own diagnosis instead of reading as drift.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Fold in the Slice 1.2 exec-table deferrals

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

> **Why now:** these were deferred when one function existed. This slice takes it to eight. A misspelled `Direction` header makes `parse_exec_table` return `[]`, which today means **every Direction in that file goes unchecked and the gate stays green** — a fail-open whose blast radius scales with the number of functions. That is the moment to close it.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestExecTableHardening(unittest.TestCase):
    def _exec(self, d, body, fn="sales"):
        _write(d, "ontologies/%s/_executive-view.md" % fn, body)

    def test_misspelled_header_errors_instead_of_passing_silently(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Diretcion |\n|---|---|\n| Forecast | up |\n")
            self.assertTrue(any(f.level == "ERROR" and "activity table" in f.message
                                for f in validate.check_ontology(d)))

    def test_missing_table_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\nProse only, no table.\n")
            self.assertTrue(any(f.level == "ERROR" and "activity table" in f.message
                                for f in validate.check_ontology(d)))

    def test_header_present_but_no_rows_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n")
            self.assertTrue(any(f.level == "ERROR" and "activity table" in f.message
                                for f in validate.check_ontology(d)))

    def test_empty_file_is_silent(self):
        # An untouched worksheet stays silent (#5): only a file with content
        # that fails to parse is a problem.
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "")
            self.assertEqual(validate.check_ontology(d), [])

    def test_empty_activity_cell_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, "# Sales\n\n| Activity | Direction |\n|---|---|\n|  | up |\n")
            self.assertTrue(any(f.level == "ERROR" and "Activity" in f.message
                                for f in validate.check_ontology(d)))

    def test_escaped_pipe_does_not_split_a_cell(self):
        rows = validate.parse_exec_table(
            "| Activity | Direction |\n|---|---|\n| Quote \\| order handoff | down |\n")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "Quote | order handoff")
        self.assertEqual(rows[0][1], "down")

    def test_good_table_still_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._exec(d, EXEC_OK)
            self.assertEqual([f for f in validate.check_ontology(d)
                              if f.level == "ERROR"], [])


class TestOntologyFileSafety(unittest.TestCase):
    def test_directory_named_md_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md", EXEC_OK)
            os.makedirs(os.path.join(d, "ontologies", "sales", "notes.md"))
            findings = validate.check_ontology(d)  # must not raise
            self.assertTrue(any(f.level == "ERROR" and "regular file" in f.message
                                for f in findings))

    def test_non_utf8_deep_record_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md", EXEC_OK)
            _write_bytes(d, "ontologies/sales/bad.md", b"---\nmotion: automate\n---\n\xff\xfe\n")
            self.assertTrue(any(f.level == "ERROR" for f in validate.check_ontology(d)))

    def test_deep_record_linked_by_path_not_basename(self):
        # A link to another function's file must not satisfy the listing check.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Deep record |\n|---|---|---|\n"
                   "| Renewal | down | [d](../people-hr/renewal.md) |\n")
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/renewal.md", AUTOMATE_OK)
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            self.assertTrue(any(f.level == "WARN" and "not listed" in f.message
                                and "sales/renewal.md" in f.path
                                for f in validate.check_ontology(d)))

    def test_fragment_link_still_counts_as_listed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/sales/_executive-view.md",
                   "| Activity | Direction | Deep record |\n|---|---|---|\n"
                   "| Renewal | down | [d](renewal.md#scores) |\n")
            _write(d, "ontologies/sales/renewal.md", AUTOMATE_OK)
            self.assertFalse(any("not listed" in f.message
                                 for f in validate.check_ontology(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestExecTableHardening tests.test_validate.TestOntologyFileSafety -v`
Expected: FAIL — several errors and at least one uncaught exception from the directory-named-`.md` case.

- [ ] **Step 3: Harden `parse_exec_table`.** Only the cell split changes — the signature and return shape stay exactly as they are, so the existing `TestExecTable` tests remain valid:

```python
_CELL_SPLIT = re.compile(r"(?<!\\)\|")
```

(place it next to `_LINK`), and inside the row loop replace

```python
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
```

with

```python
        cells = [c.strip().replace("\\|", "|")
                 for c in _CELL_SPLIT.split(line.strip().strip("|"))]
```

- [ ] **Step 4: Harden `check_ontology`.** Replace the `else:` branch that parses the executive view, and the `for df in deep_files:` loop, with:

```python
        else:
            rel_exec = os.path.relpath(exec_path, root)
            exec_text, exec_findings = _read_utf8(exec_path, rel_exec)
            findings += exec_findings
            rows = parse_exec_table(exec_text) if exec_text is not None else []
            if exec_text is not None and exec_text.strip() and not rows:
                # A misspelled or missing 'Direction' header parses to zero rows,
                # which would leave every Direction in this file UNCHECKED while
                # the gate stayed green. Fail closed instead (#5).
                findings.append(Finding("ERROR", rel_exec, None,
                                        "executive view has no parsable activity table — a header "
                                        "row containing 'Direction' and at least one activity row "
                                        "are required (#5 exec tier)"))
            for activity, direction, link, ln in rows:
                if not activity:
                    findings.append(Finding("ERROR", rel_exec, ln,
                                            "executive-view row has an empty Activity cell"))
                if direction not in DIRECTIONS:
                    findings.append(Finding("ERROR", rel_exec, ln,
                                            "Direction must be 'up' or 'down', got %r" % direction))
                if link:
                    target = os.path.normpath(
                        os.path.join(fdir, link.split("#", 1)[0]))
                    linked.add(os.path.realpath(target))
        for df in deep_files:
            dpath = os.path.join(fdir, df)
            if not os.path.isfile(dpath):
                # a directory (or FIFO) named x.md would crash or block the read
                findings.append(Finding("ERROR", os.path.join(rel_fdir, df), None,
                                        "ontology entry ending in .md is not a regular file"))
                continue
            findings += check_deep_record(dpath, root)
            if os.path.realpath(dpath) not in linked:
                findings.append(Finding("WARN", os.path.join(rel_fdir, df), None,
                                        "deep record not listed in the executive view"))
```

> `linked` now holds **realpaths**, not basenames. That closes both 1.2 deferrals at once: a link to another function's file no longer satisfies the listing check, and a `#fragment` link no longer falsely warns.

- [ ] **Step 5: Run tests + gate**

Run: `python3 -m unittest tests.test_validate.TestExecTable tests.test_validate.TestExecTableHardening tests.test_validate.TestOntology tests.test_validate.TestOntologyFileSafety -v`
Expected: PASS, including the three pre-existing `TestExecTable` tests unchanged.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s)`, exit 0 — the existing People/HR executive view parses and its deep record is still matched by path.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "fix(validate): fail closed on an unparsable executive view (Slice 1.2 deferrals)

A misspelled Direction header returned zero rows, leaving every Direction
unchecked with a green gate. Also: empty Activity cells, escaped pipes,
non-regular .md entries, and path-based (not basename) deep-record matching.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The 7 executive views

**Files:** Create seven `_executive-view.md` files; modify `ontologies/people-hr/_executive-view.md`; create `ontologies/README.md`

> **Authoring rules for every file below.** Exec tier is **name + Direction only** — no Motion, no scores, no deep fields (#5: "required-ness is a property of the tier"). **Direction** means: **up** = deserves *more* human time; **down** = should stop being hand-run. Every row's Deep record cell is `—` (no deep records are authored in this slice). Keep the frame paragraph identical across files so the eight read as one system.

- [ ] **Step 1: Create `ontologies/README.md`:**

```markdown
# Ontologies — the map of what each function does

One directory per function. Each carries an `_executive-view.md` (the top tier) and,
for activities the company has chosen to act on, one deep record per activity.

## The two tiers (#5)

**Executive view** — *every* activity the function does, carrying only its **name** and
its **Direction**. That is the whole requirement. It is meant to be legible to
leadership and finishable in one sitting; it never demands deep fields.

- **up** — deserves *more* human time. Judgment, relationships, or consequences that
  should not be handed to a machine.
- **down** — should stop being hand-run. Repetitive, describable, or mechanical.

Direction is a claim about *where the work should go*, not about how it is done today.

**Deep record** — one file per **acted-on** activity: the Motion verdict with its five
scores, Work type, and the accountability owner, plus — when Motion is `automate` or
`build` — Substrate, Shape, and all eight parts of the Describability Gate.

Depth is earned by acting, not by planning to act. An activity with no deep record is
not a gap; it is an activity nobody has chosen to work on yet, and the validator stays
silent about it.

## These files are templates

The ontologies in this repository are **engine exemplars** — a plausible starting map
for a B2B SaaS company, not claims about yours. The activity lists and Directions are
meant to be edited, cut, and argued with. A generated company's real ontology lives in
its own private repository (see `AGENTS.md`, "Two repos").

`people-hr/` is worked one level deeper than the rest: it carries the
`onboarding-orchestration` deep record that the skill, Owner's Card, memory baseline,
and constitution rule are all built on. Read it as the reference shape.
```

- [ ] **Step 2: Add the template frame to `ontologies/people-hr/_executive-view.md`.** Replace its existing intro paragraph (everything between the `# People/HR — executive view` heading and the table) with:

```markdown
Every activity this function does, with its Direction — **up** (deserves more human
time) or **down** (should stop being hand-run). Deep records exist only for the
activities the company has chosen to act on first; the rest are listed but not yet
worked (depth is earned by acting, not by planning to act).

*A starting template, not a claim about your company — edit it (see
[ontologies/README.md](../README.md)).*
```

- [ ] **Step 3: Create the seven files.** Each uses this exact frame under its own heading:

```markdown
Every activity this function does, with its Direction — **up** (deserves more human
time) or **down** (should stop being hand-run). No deep records yet: depth is earned
by acting, not by planning to act.

*A starting template, not a claim about your company — edit it (see
[ontologies/README.md](../README.md)).*
```

**`ontologies/sales/_executive-view.md`** — heading `# Sales — executive view`, then the frame, then:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Discovery calls | up | — |
| Account planning for strategic accounts | up | — |
| Competitive deal strategy | up | — |
| Deal-desk approvals and pricing exceptions | up | — |
| Lead routing and qualification | down | — |
| Pipeline hygiene and CRM updates | down | — |
| Proposal and quote generation | down | — |
| Forecast roll-up | down | — |
| Contract redlining coordination | down | — |
| Sales-enablement content upkeep | down | — |
```

**`ontologies/customer-success/_executive-view.md`** — heading `# Customer success — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Escalation management | up | — |
| Churn-risk intervention | up | — |
| Expansion-opportunity identification | up | — |
| Voice-of-customer synthesis | up | — |
| Renewal preparation | down | — |
| Health-score monitoring | down | — |
| Quarterly business-review preparation | down | — |
| Customer onboarding | down | — |
| Support-ticket triage | down | — |
| Reference and advocacy coordination | down | — |
```

**`ontologies/marketing/_executive-view.md`** — heading `# Marketing — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Positioning and messaging | up | — |
| Brand and creative direction | up | — |
| Analyst and press relations | up | — |
| Competitive intelligence | up | — |
| Lead-generation experiment design | up | — |
| Content production and repurposing | down | — |
| Campaign performance reporting | down | — |
| Email nurture operations | down | — |
| SEO and site hygiene | down | — |
| Event planning and logistics | down | — |
```

**`ontologies/product/_executive-view.md`** — heading `# Product — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Discovery and problem framing | up | — |
| Roadmap prioritization | up | — |
| Pricing and packaging decisions | up | — |
| Sunset and deprecation decisions | up | — |
| Feature-request triage | down | — |
| Customer-interview synthesis | down | — |
| Specification and PRD drafting | down | — |
| Release-notes authoring | down | — |
| Usage-analytics reporting | down | — |
| Cross-functional launch coordination | down | — |
```

**`ontologies/engineering/_executive-view.md`** — heading `# Engineering — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Architecture decisions | up | — |
| Incident response | up | — |
| Design review | up | — |
| Technical hiring loops | up | — |
| Dependency and security patching | down | — |
| Post-incident review authoring | down | — |
| CI/CD pipeline maintenance | down | — |
| Test-suite maintenance | down | — |
| On-call rotation scheduling | down | — |
| Capacity and cost review | down | — |
```

**`ontologies/finance/_executive-view.md`** — heading `# Finance — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Financial planning and scenario modeling | up | — |
| Revenue-recognition judgments | up | — |
| Vendor contract review | up | — |
| Month-end close | down | — |
| Invoice processing and accounts payable | down | — |
| Expense-report review | down | — |
| Budget-versus-actuals reporting | down | — |
| Payroll runs | down | — |
| Board-reporting package | down | — |
| Audit preparation | down | — |
```

**`ontologies/legal/_executive-view.md`** — heading `# Legal — executive view`:

```markdown
| Activity | Direction | Deep record |
|---|---|---|
| Contract negotiation for non-standard terms | up | — |
| Litigation and dispute strategy | up | — |
| Policy drafting | up | — |
| Employment-law advisory | up | — |
| Standard contract review (NDAs, MSAs) | down | — |
| Compliance monitoring and filings | down | — |
| Regulatory change tracking | down | — |
| Data-privacy request handling | down | — |
| IP and trademark administration | down | — |
| Vendor and procurement review | down | — |
```

- [ ] **Step 4: Update the `AGENTS.md` repo map.** In the map table, replace the `ontologies/` row's description with:

```markdown
| `ontologies/` | One directory per function. All 8 executive views; `people-hr/` also carries a worked deep record. |
```

And in the "Built and working" list, replace the `ontologies/` bullet with:

```markdown
- `ontologies/` — the two-tier ontology schema, all 8 function executive views, and
  one worked deep record (People/HR `onboarding-orchestration`).
```

- [ ] **Step 5: Verify the content adds zero findings**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)` and `exit: 0` — **the same 7 warnings as before this slice.** Seven new functions with executive views and no deep records must be completely silent (#5: silence on untouched worksheets). If any new WARN or ERROR appears, that is a real finding — read it before changing the content.

Run: `python3 -c "
import sys; sys.path.insert(0, 'scripts'); import validate
rows = 0
import os
for fn in sorted(os.listdir('ontologies')):
    p = os.path.join('ontologies', fn, '_executive-view.md')
    if os.path.isfile(p):
        r = validate.parse_exec_table(open(p, encoding='utf-8').read())
        rows += len(r)
        print('%-20s %2d activities' % (fn, len(r)))
print('total', rows)
"`
Expected: 8 functions listed, each with 10 activities, `total 80`. A function reporting `0` means its table did not parse — Task 2's new ERROR should have caught it, so investigate rather than moving on.

- [ ] **Step 6: Commit**

```bash
git add ontologies AGENTS.md
git commit -m "feat(ontologies): the remaining 7 executive views (#5 exec tier complete)

Sales, customer success, marketing, product, engineering, finance, legal —
name + Direction only, no deep records (depth is earned by acting). Adds the
ontologies/ convention README and marks every view as an editable template.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Known limitations + full gate

**Files:** Modify `docs/known-limitations.md`

- [ ] **Step 1: Append to the "Context budget (#13)" section:**

```markdown
- **Code-span detection is deliberately biased toward over-stripping.** `_strip_code`
  scans fences (backtick and tilde, any length ≥ 3) and inline spans, but it does not
  implement backslash escapes: `` \` `` reads as opening a code span. The bias is
  chosen, not accidental — the root-file drift check is an ERROR-level guarantee where
  *under*-stripping fails open (a fenced `@AGENTS.md` would satisfy the check while
  Claude Code imported nothing), so ambiguity resolves toward stripping. The cost is a
  possible false drift ERROR next to an escaped backtick, and a slight undercount in the
  budget aggregate.
- **The always-loaded aggregate models the union of harnesses, deduplicated by real
  path.** `AGENTS.md` reached both directly and through `CLAUDE.md`'s import counts once:
  no single harness loads it twice, and double-counting could push a legitimate repo past
  the ERROR threshold for budget it does not spend.
```

- [ ] **Step 2: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`, roughly 400 tests.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. The seven new ontologies are not in the #18 routing domain (proposals route skills and rules only), and the engine repo carries no `groundwork.pin`, so the tripwire stays dormant.

- [ ] **Step 3: Commit**

```bash
git add docs/known-limitations.md
git commit -m "docs: record the _strip_code over-strip bias and the aggregate dedupe

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No deep records.** Depth is earned by acting (#5 §5). Slice 2.2 deepens **CS renewal-prep** and **PM feature-request-triage** into full worked slices — Motion + five scores, Work type, accountability owner, Substrate, Shape, and all eight Describability Gate parts, plus their skills and Owner's Cards.
- **No `demo/`.** Phase 2.3: the synthetic ~20-person B2B SaaS, the 15-minute 3-query script, demo canon + the #16 synthetic-identifier check, the meeting-challenger exemplar, and the demo's real `groundwork.pin` — which is where the #18 tripwire and the #21 skew gate stop being dormant.
- **No new #5 checks.** The severity contract is unchanged; this slice only stops the existing checks from failing open.
- **Still open for the maintainer:** the four Slice 1.5d-ii deferrals (nested-root schema coverage, dot-directory classification, case-variant authorization, the path-style nit) and the `SKIP_RELPATHS` gate-scoping sign-off. None blocks this slice.

## Self-Review

- **Ticket coverage:** #5 exec tier ("every activity, name + Direction only") → 7 new `_executive-view.md` files completing all 8 functions; the tier rule and the depth doctrine → `ontologies/README.md`; #5's silence clause → verified by the expected-output check that the WARN count does not move.
- **Deferral folds are justified, not opportunistic.** Task 1 closes the Move 2 deferrals the maintainer asked about, one of which is a fail-open on an ERROR-level guarantee. Task 2 closes the Slice 1.2 exec-table deferrals **because this slice multiplies their blast radius by eight** — a silently-unparsed table is exactly the failure that content growth converts from theoretical to likely.
- **Placeholder scan:** no TBD/TODO; every file's content and every code change is given in full, with verification commands and expected output.
- **Type consistency:** `parse_exec_table` keeps its `(activity, direction, link, line_no)` tuple shape and its bare-list return, so the three existing `TestExecTable` tests are untouched. `linked` changes from a set of basenames to a set of realpaths — a local variable, single call site. `_take` returns `bool`. No new imports.
- **Pre-empts the recurring Codex findings.** (a) *Fail-open on malformed input* — the whole point of Task 2: an unparsable table now ERRORs instead of passing green; non-regular `.md` entries ERROR instead of crashing; non-UTF-8 deep records already fail closed through `_load_frontmatter` and are now proven by test. (b) *Alias laundering* — deep-record listing matches on `realpath`, so a link to another function's identically-named file no longer satisfies it. (c) *Non-scalar frontmatter* — untouched in this slice; no new frontmatter is read. (d) *Corpus void* — the Task 3 verification command counts parsed activities per function, so a table that silently fails to parse is visible as a `0` rather than an absent finding.
- **Honest cost stated:** the `_strip_code` over-strip bias can produce a false drift ERROR next to an escaped backtick. It is a deliberate tiebreak between two consumers with opposite safe directions, and it is written down in `docs/known-limitations.md` rather than left as a surprise.
