# groundwork V1 — Slice 1.5d-ii: The blast-radius `--diff` tripwire (#18) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the enforcement teeth of governed self-improvement. On `validate --diff <base>`, classify every changed skill/rule; each **escalating** change must trace to a pending proposal whose **declared** `blast_radius` matches what the diff **actually** touches (declared-vs-actual — the sharp thing #18 adds); a track-1 body-only change wants its **changelog** entry; and the changelog is enforced **append-only**. Plus the documented Known Limitation: a stateless validator cannot prove a human reviewed — the commit bit is the real teeth. **This closes Phase 1 governance.**

**Architecture:** Same split 1.4b proved — a **pure, git-free classification core** (`_governed_class`, `classify_governed_change`, `_changelog_append_only`) that is exhaustively unit-testable, behind a **thin git/IO layer** (`blast_radius_diff_findings`) that reuses 1.4b's hardened plumbing. That plumbing (toplevel/scope resolution, base-ref verification, `ls-tree -z` base listing) is **extracted once** into `_git_diff_context(root, base)` and shared with `memory_diff_findings` — two callers of one hardened contract instead of two copies.

**Scope — the tripwire is scoped to *governed roots*.** A governed root is a directory carrying a #21 `groundwork.pin` — i.e. real generated company content. The engine repo is pin-less by design, so the tripwire is **dormant here** (fixture-proven, exactly as `check_version_pin` is) and activates on `demo/` (Phase 2.3) and `your-company/`. See **Design call 1** below — this is load-bearing and flagged for the maintainer.

**Tech Stack:** Python 3.9+ standard library only (no new imports — `subprocess`, `os`, `re` are already on the allowlist); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports at all in this slice. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **Codebase conventions (match them):** stateless checks take `(root, ignore=())` and honor `_ignored`; structured reads go through `_load_frontmatter(abspath, relpath)` / `_read_utf8` (fail closed on non-UTF-8/OSError, never crash); reuse `_blank`, `_parse_date`, `Finding(level, path, line, message)`, `ACTION_CLASSES`, `TRACK2_CLASSES`, `BLAST_RADIUS`, `_frontmatter_and_body`, `_diff_in_workbench_skips`, `_committed_path_status`, `iter_files`.
- **Diff-mode conventions (1.4b, do not regress):** the scan is driven by the **base file list** (`git ls-tree -z`), never the working-tree walker; `.gitignore` never waives a committed file; unknown base ref / unreadable base blob / non-UTF-8 / symlinked path all **fail closed** with an ERROR, never a silent pass.
- **Fail-closed classification (the load-bearing invariant):** every uncertain path resolves to **`escalating`**. A misread must never license an auto-apply. Unparseable frontmatter, a missing/invalid `action_class`, a nested or non-`SKILL.md` package file — all escalate.
- **Alias laundering is closed at BOTH layers** (the 1.5d-i through-line): lexical (`os.path.normpath`) **and** filesystem (`os.path.realpath` containment). Proposal targets and changed paths are matched on **realpath**, so a symlink cannot point one place and match another.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.5d-i merged to `main` (done: `18c4ffc`). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-1.5d-ii-tripwire
```

---

## Design calls flagged for the maintainer

> These three are load-bearing. Each is **pre-made** here (with the record that decides it) so the build is unblocked; if the maintainer disagrees with any, it changes this plan, not the code that ships after it.

**1. The tripwire is scoped to pinned (company-instance) roots — it does NOT fire on the engine repo.**
Three already-locked record points determine this together: (a) 1.5d-i decided **no committed live proposal** in the engine (a proposal is transient; a committed one would be a pending change that never applies); (b) #21's pin is **company-instance metadata** and the engine root stays pin-less (1.5c, maintainer's call 2026-07-24); (c) whether groundwork **dogfoods its own governance machinery on this repo** is retained map fog, explicitly **not V1** (1.5b hook-set decision, recorded in `docs/known-limitations.md`). Firing the tripwire on the engine root would contradict all three at once: every future slice that edits `skills/onboarding-orchestration/SKILL.md` (which is `external-side-effect` — track-2, so *any* edit escalates) or the constitution rule would need a committed pending proposal that never applies. **Counter-argument, honestly:** a dormant check is the wwf5d dead-path trap — an inert scan ships looking done. Two things defuse it: the classification core is *pure* and exhaustively unit-tested (the logic is exercised, not merely present), and the CLI layer is proven end-to-end against **real temp git repos that carry a pin**, so the activation path itself is under test. And it stops being dormant on real content at **Phase 2.3**, where `demo/` gets its own pin — the demo's rung-5 governance block can then ship a real pending proposal and show the tripwire firing.

**2. A missing changelog line for a track-1 body change is a WARN, not an ERROR.**
#18 says a non-escalating change "needs only its changelog entry." But a stateless validator **cannot distinguish an agent auto-apply from the maintainer's own hand-edit** of their company's skill body — and the maintainer editing their own file is completely legitimate. ERRORing it would both false-positive on normal work and pollute the changelog with non-auto-applies, destroying the "one-glance" property #17 explicitly gives as the justification for conceding pre-approval on track-1. The harm class settles it: a missing ledger line is an **accountability** gap (loud, recoverable), not a safety invariant — and #8's ERROR tier is reserved for safety invariants (the same principle the maintainer already applied to active-rule provenance in 1.5a). **The ERROR stays exactly where #18 puts it:** an escalating change with no proposal, and the declared-vs-actual mismatch. **Counter-argument:** a WARN can be ignored, so an agent that auto-applies without logging is only nagged. True — and the answer is that the agent cannot *land* anything anyway (the commit bit), which is the honest limit this slice documents.

**3. A deleted governed file is a WARN, not an ERROR.**
Retiring a rule or a skill is legitimate (rules carry `sunset`; cards carry `retirement_condition`), and it is escalating — but it **cannot be traced to a proposal**, because `check_proposals` requires a proposal's `target` to be an existing file. Making deletion an ERROR would create an **unsatisfiable gate** (no valid proposal could ever clear it). So deletion emits a WARN naming the honest record — the maintainer's consent commit — and the limit goes in `docs/known-limitations.md`. (Memory records are different by doctrine: they are superseded, never deleted, so `memory_diff_findings` keeps its ERROR.)

---

## File Structure

- `scripts/validate.py` — **modify.**
  - Extract `_git_diff_context(root, base)` from `memory_diff_findings` (behavior-preserving; messages byte-identical).
  - Add `_git_show`, `_has_symlink_component`, `_governed_class`, `classify_governed_change`, `_changelog_append_only`, `_pin_dirs`, `_pending_proposal_radii`, `_changelog_appended_targets`, `blast_radius_diff_findings`.
  - Wire `blast_radius_diff_findings` into `main()`'s `--diff` branch.
- `tests/test_validate.py` — **modify.** `TestGovernedClassify` (pure), `TestChangelogAppendOnly` (pure), `TestBlastRadiusDiff` (real temp git repos with a pin).
- `docs/known-limitations.md` — **modify.** The #18 Known Limitation section.
- `proposals/README.md` — **modify.** One paragraph: what the tripwire enforces at PR time.
- `governance/changelog.md` — **unchanged** (its header already promises append-only enforcement; this slice makes the promise true).

> **Design notes.**
> 1. **Pure core, thin IO** (1.4b precedent). `classify_governed_change` takes texts, not paths — every #17 boundary case is a table-driven unit test with no git in sight. Only `blast_radius_diff_findings` touches the filesystem.
> 2. **One hardened git contract.** `_git_diff_context` is an extraction, not a rewrite: the existing `TestMemoryDiffCLI` / `TestDiffCLIWiring` suites are its regression proof and must pass untouched. Do **not** "improve" the error strings — tests assert on `"git repository"` and `"base ref"`.
> 3. **The scan set is base ∪ working tree.** Memory only needed base-driven (new records are fine); governance must also see **additions** — a newly added rule is escalating, and `git diff` does not list untracked files. So the candidate set is the base `ls-tree` listing unioned with a working-tree walk that deliberately ignores `.gitignore` (a gitignored new rule must not hide).
> 4. **A pin removed in the diff cannot un-govern the change that removed it** — governed roots are collected from the base tree **and** the working tree.

---

## Task 1: Extract the shared git-diff context

**Files:** Modify `scripts/validate.py`

**Interfaces:** Produces `_git_diff_context(root, base) -> (ctx|None, list[Finding])` where `ctx = {"toplevel": str, "scope": str, "base_files": list[str]}`. Consumed by `memory_diff_findings` (this task) and `blast_radius_diff_findings` (Task 3).

- [ ] **Step 1: Add `_git_diff_context` and `_git_show`** immediately **above** `def memory_diff_findings(` in `scripts/validate.py`:

```python
def _git_diff_context(root, base):
    """Resolve the git layout and the BASE file list once, with 1.4b's hardening:
    byte-safe paths, canonical-casing scope prefix, a verified base ref, and a
    NUL-separated ls-tree listing. Returns (ctx, findings); ctx is None exactly
    when the findings are fatal. Shared by every --diff mode so the plumbing is
    hardened in one place."""
    try:
        # bytes + os.fsdecode: survives locale-undecodable repo paths; and
        # --show-prefix gives root's repo-relative path in git's canonical
        # casing, so a case-variant invocation cannot blind the scope filter
        rp = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel", "--show-prefix"],
                            capture_output=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, [Finding("ERROR", root, None, "--diff requires a git repository")]
    rp_lines = os.fsdecode(rp).splitlines()
    if len(rp_lines) != 2 or not os.path.isdir(rp_lines[0]):
        # a newline/CR inside the repo path mis-splits this output; a wrong
        # scope would fail open, so refuse instead
        return None, [Finding("ERROR", root, None,
                              "--diff could not resolve the repository layout (unsupported path)")]
    toplevel = rp_lines[0]
    scope = rp_lines[1].strip("/") or "."
    try:
        subprocess.run(["git", "-C", toplevel, "rev-parse", "--verify", "--quiet",
                        "%s^{commit}" % base], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        # a typo'd base must not report a clean bill of health
        return None, [Finding("ERROR", root, None, "--diff base ref not found: %s" % base)]
    try:
        # -z: NUL-terminated, unquoted paths (immune to core.quotePath mangling
        # of non-ASCII names); os.fsdecode round-trips odd bytes losslessly
        raw = subprocess.run(["git", "-C", toplevel, "ls-tree", "-r", "--name-only", "-z", base],
                             capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None, [Finding("ERROR", root, None, "--diff could not list the base tree for %s" % base)]
    return {"toplevel": toplevel, "scope": scope,
            "base_files": [os.fsdecode(b) for b in raw.split(b"\0") if b]}, []


def _git_show(toplevel, base, repo_path):
    """The base version of one committed file as text, or None when it cannot be
    read (fetch failure or non-UTF-8). Callers treat None as fail-closed: the
    base LIST says the file exists, so an unreadable base is never 'new'."""
    show = subprocess.run(["git", "-C", toplevel, "show", "%s:%s" % (base, repo_path)],
                          capture_output=True)
    if show.returncode != 0:
        return None
    try:
        return show.stdout.decode("utf-8")
    except UnicodeError:
        return None
```

- [ ] **Step 2: Rewrite `memory_diff_findings`'s prologue to use it.** Replace everything in `memory_diff_findings` from `try:` (the `rev-parse` call) through the `raw = subprocess.run([... "ls-tree" ...])` block and its `except`, i.e. the whole span ending just before `findings = []`, with:

```python
def memory_diff_findings(root, base):
    """Compare memory records that existed at <base> (a git ref) against the
    working tree. Scoped to memory folders under root. New records are fine;
    deletions and immutable-field edits are ERRORs. Driven by the BASE file
    list, so no working-tree skip can exempt a committed record."""
    ctx, ctx_findings = _git_diff_context(root, base)
    if ctx is None:
        return ctx_findings
    toplevel, scope = ctx["toplevel"], ctx["scope"]
    findings = []
    listdir_cache = {}
    for bf in ctx["base_files"]:
```

Everything from `if scope != "." and not bf.startswith(scope + "/"):` onward is **unchanged**, except the two `git show` lines: replace

```python
        show = subprocess.run(["git", "-C", toplevel, "show", "%s:%s" % (base, bf)],
                              capture_output=True)
        if show.returncode != 0:
            # the base LIST says it exists, so a fetch failure is never "new" —
            # fail closed rather than silently passing
            findings.append(Finding("ERROR", bf, None,
                                    "--diff could not read the base version of this record"))
            continue
        try:
            old = show.stdout.decode("utf-8")
        except UnicodeError:
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify immutability: base version is not valid UTF-8"))
            continue
```

with

```python
        old = _git_show(toplevel, base, bf)
        if old is None:
            # the base LIST says it exists, so a fetch failure (or an
            # undecodable blob) is never "new" — fail closed
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify immutability: the base version of this record is "
                                    "unreadable or not valid UTF-8"))
            continue
```

- [ ] **Step 3: Update the two memory-diff tests that assert on the merged message.** In `tests/test_validate.py`, the tests asserting `"base version is not valid UTF-8"` or `"could not read the base version"` must now assert on the merged wording. Find them and change the asserted substring to `"unreadable or not valid UTF-8"`:

Run: `cd "$(git rev-parse --show-toplevel)" && grep -n "base version" tests/test_validate.py`
Then update each matched assertion's substring to `"unreadable or not valid UTF-8"`. **Change nothing else** in those tests — the ERROR level, the path, and the scenario stay as they are.

- [ ] **Step 4: Prove the extraction is behavior-preserving**

Run: `python3 -m unittest tests.test_validate.TestMemoryDiff tests.test_validate.TestMemoryDiffCLI tests.test_validate.TestDiffCLIWiring -v`
Expected: PASS — every existing memory-diff test green (this suite is the regression proof for the extraction).

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py . && python3 scripts/validate.py . --diff main`
Expected: 281 tests OK; both validator runs exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "refactor(validate): extract _git_diff_context/_git_show shared by every --diff mode

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The pure classification core

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:** Produces `_governed_class(rel) -> "rule"|"skill-md"|"skill-other"|None`, `classify_governed_change(kind, cls, old_text, new_text) -> (radius|None, detail|None)`, `_changelog_append_only(old_text, new_text) -> bool`. All pure — no filesystem, no git.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py` (append at the end of the file):

```python
SKILL_T1 = """---
name: weekly-digest
description: Summarize the week's open threads for the team channel
action_class: read-only
provisioned: no
ontology: ontologies/people-hr/onboarding-orchestration.md
---
# Weekly digest

Collect the week's open threads and summarize them.
"""


class TestGovernedClassify(unittest.TestCase):
    def test_rule_paths_are_governed(self):
        self.assertEqual(validate._governed_class("governance/constitution/access.md"), "rule")
        self.assertEqual(validate._governed_class("governance/constitution/sub/access.md"), "rule")

    def test_skill_md_and_package_files(self):
        self.assertEqual(validate._governed_class("skills/weekly-digest/SKILL.md"), "skill-md")
        self.assertEqual(validate._governed_class("skills/weekly-digest/owner-card.md"), "skill-other")
        self.assertEqual(validate._governed_class("skills/weekly-digest/sub/SKILL.md"), "skill-other")

    def test_ungoverned_paths(self):
        self.assertIsNone(validate._governed_class("skills/work-package-spec.md"))
        self.assertIsNone(validate._governed_class("governance/changelog.md"))
        self.assertIsNone(validate._governed_class("memory/onboarding-baseline.md"))
        self.assertIsNone(validate._governed_class("README.md"))

    def test_any_rule_change_escalates(self):
        r, _d = validate.classify_governed_change("modified", "rule", RULE_OK, RULE_OK + "\nmore\n")
        self.assertEqual(r, "escalating")

    def test_owner_card_change_escalates(self):
        r, _d = validate.classify_governed_change("modified", "skill-other", CARD_OK, CARD_OK + "\nx\n")
        self.assertEqual(r, "escalating")

    def test_added_skill_escalates(self):
        r, _d = validate.classify_governed_change("added", "skill-md", None, SKILL_T1)
        self.assertEqual(r, "escalating")

    def test_track1_body_only_change(self):
        new = SKILL_T1.replace("Collect the week's open threads and summarize them.",
                               "Collect the week's open threads, summarize them, and note blockers.")
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "track1-body")

    def test_track2_body_only_change_escalates(self):
        new = SKILL_OK.replace("# Onboarding orchestration", "# Onboarding orchestration\n\nextra line")
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_OK, new)
        self.assertEqual(r, "escalating")
        self.assertIn("track-2", d)

    def test_description_change_escalates(self):
        new = SKILL_T1.replace("Summarize the week's open threads for the team channel",
                               "Summarize everything anyone said this week")
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")
        self.assertIn("frontmatter", d)

    def test_action_class_change_escalates(self):
        new = SKILL_T1.replace("action_class: read-only", "action_class: high-risk")
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")

    def test_unparseable_new_frontmatter_fails_closed(self):
        new = SKILL_T1.replace("provisioned: no", "  indented: bad")
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")
        self.assertIn("unparseable", d)

    def test_missing_action_class_fails_closed(self):
        base = SKILL_T1.replace("action_class: read-only\n", "")
        new = base.replace("Collect the week's open threads and summarize them.", "Different body.")
        r, d = validate.classify_governed_change("modified", "skill-md", base, new)
        self.assertEqual(r, "escalating")
        self.assertIn("action_class", d)

    def test_invalid_action_class_fails_closed(self):
        base = SKILL_T1.replace("action_class: read-only", "action_class: mostly-harmless")
        new = base.replace("Collect the week's open threads and summarize them.", "Different body.")
        r, _d = validate.classify_governed_change("modified", "skill-md", base, new)
        self.assertEqual(r, "escalating")

    def test_unchanged_file_classifies_as_nothing(self):
        r, d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, SKILL_T1)
        self.assertIsNone(r)
        self.assertIsNone(d)

    def test_whitespace_and_crlf_only_change_is_not_a_change(self):
        new = SKILL_T1.replace("\n", "\r\n") + "\n\n"
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertIsNone(r)

    def test_frontmatter_removed_entirely_escalates(self):
        new = SKILL_T1.split("---\n", 2)[2]
        r, _d = validate.classify_governed_change("modified", "skill-md", SKILL_T1, new)
        self.assertEqual(r, "escalating")


class TestChangelogAppendOnly(unittest.TestCase):
    BASE = ("# Governance changelog\n\n## Entries\n\n"
            "- 2026-07-26 | skills/a/SKILL.md | one | scribe | a1b2c3d\n")

    def test_append_is_allowed(self):
        new = self.BASE + "- 2026-07-27 | skills/a/SKILL.md | two | scribe | b2c3d4e\n"
        self.assertTrue(validate._changelog_append_only(self.BASE, new))

    def test_identical_is_allowed(self):
        self.assertTrue(validate._changelog_append_only(self.BASE, self.BASE))

    def test_edited_entry_rejected(self):
        new = self.BASE.replace("one", "something else entirely")
        self.assertFalse(validate._changelog_append_only(self.BASE, new))

    def test_removed_entry_rejected(self):
        new = "# Governance changelog\n\n## Entries\n\n"
        self.assertFalse(validate._changelog_append_only(self.BASE, new))

    def test_reordered_entries_rejected(self):
        base = self.BASE + "- 2026-07-27 | skills/a/SKILL.md | two | scribe | b2c3d4e\n"
        new = ("# Governance changelog\n\n## Entries\n\n"
               "- 2026-07-27 | skills/a/SKILL.md | two | scribe | b2c3d4e\n"
               "- 2026-07-26 | skills/a/SKILL.md | one | scribe | a1b2c3d\n")
        self.assertFalse(validate._changelog_append_only(base, new))

    def test_prepended_entry_rejected(self):
        new = ("# Governance changelog\n\n## Entries\n\n"
               "- 2026-07-20 | skills/a/SKILL.md | zero | scribe | 0a1b2c3\n"
               "- 2026-07-26 | skills/a/SKILL.md | one | scribe | a1b2c3d\n")
        self.assertFalse(validate._changelog_append_only(self.BASE, new))

    def test_crlf_base_is_not_a_phantom_rewrite(self):
        self.assertTrue(validate._changelog_append_only(self.BASE.replace("\n", "\r\n"), self.BASE))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestGovernedClassify tests.test_validate.TestChangelogAppendOnly -v`
Expected: FAIL — `module 'validate' has no attribute '_governed_class'`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`, immediately **after** `check_changelog` and **before** `def validate(root):`:

```python
def _governed_class(rel):
    """Classify a path (relative to a governed root) into #17's routing domain:
    'rule' (any constitution file), 'skill-md' (a package's own SKILL.md),
    'skill-other' (anything else inside a skill package — the Owner's Card and
    every nested file), or None (not governed by the proposal routing at all).
    Top-level docs under skills/ (e.g. skills/work-package-spec.md) are not part
    of a package and are not governed."""
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "governance" and parts[1] == "constitution" \
            and rel.endswith(".md"):
        return "rule"
    if len(parts) >= 3 and parts[0] == "skills":
        if len(parts) == 3 and parts[2] == "SKILL.md":
            return "skill-md"
        return "skill-other"
    return None


def classify_governed_change(kind, cls, old_text, new_text):
    """PURE #17 blast-radius classification of ONE changed governed file. `kind`
    is 'added' or 'modified' (deletions are the caller's, see #18 note below);
    `cls` comes from _governed_class. Returns (radius, detail) with radius in
    BLAST_RADIUS, or (None, None) when nothing actually changed.

    Reasoning to carry: 'track1-body' is the ONLY auto-apply-eligible verdict, so
    every uncertain path must resolve to 'escalating'. A misclassification in that
    direction costs a human review; the other direction lets an unreviewed change
    land. Unparseable frontmatter, a missing or invalid action_class, a nested or
    non-SKILL.md package file, a brand-new SKILL.md (its description is a new
    selection surface) — all escalate."""
    if cls == "rule":
        return "escalating", "a constitution rule (rules never auto-apply, #17)"
    if cls == "skill-other":
        return "escalating", "a skill-package file other than SKILL.md (Owner's Card / package content)"
    if kind == "added":
        return "escalating", "a new SKILL.md (its description is a new selection surface)"

    old_fm, old_body, _old_parse = _frontmatter_and_body(old_text or "", "base")
    new_fm, new_body, new_parse = _frontmatter_and_body(new_text or "", "new")
    if any(f.level == "ERROR" for f in new_parse):
        return "escalating", "unparseable SKILL.md frontmatter (cannot prove the change is body-only)"
    if old_fm != new_fm:
        return "escalating", "SKILL.md frontmatter (description / action class / governance fields)"

    old_b = old_body.replace("\r\n", "\n").replace("\r", "\n").strip()
    new_b = new_body.replace("\r\n", "\n").replace("\r", "\n").strip()
    if old_b == new_b:
        return None, None

    # Frontmatter is identical here, so old and new action_class agree; read it
    # once and require it to be a valid class before conceding track-1.
    ac = new_fm.get("action_class")
    if not isinstance(ac, str) or ac not in ACTION_CLASSES:
        return "escalating", ("SKILL.md body of a skill with no valid action_class "
                              "(cannot prove track-1)")
    if ac in TRACK2_CLASSES:
        return "escalating", "SKILL.md body of a track-2 (%s) skill" % ac
    return "track1-body", "SKILL.md body of a track-1 (%s) skill" % ac


def _changelog_append_only(old_text, new_text):
    """PURE. #17's changelog is an append-only index: every line committed at base
    must survive, in order, as the head of the new file. Trailing blank lines on
    the base side are ignored (an append lands after them). Line endings are
    normalized first so a CRLF base blob is not a phantom rewrite."""
    def _lines(t):
        return t.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    old_lines = _lines(old_text)
    while old_lines and not old_lines[-1].strip():
        old_lines.pop()
    return _lines(new_text)[:len(old_lines)] == old_lines
```

- [ ] **Step 4: Run to verify passing**

Run: `python3 -m unittest tests.test_validate.TestGovernedClassify tests.test_validate.TestChangelogAppendOnly -v`
Expected: PASS (all 22 tests).

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #17 blast-radius classification core (pure, fail-closed to escalating)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The tripwire — `blast_radius_diff_findings`

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:** Produces `blast_radius_diff_findings(root, base) -> list[Finding]`, wired into `main()`'s `--diff` branch alongside `memory_diff_findings`.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py` (append at the end):

```python
PIN_OK = "---\nschema_version: 1\ngenerated_by_commit: abc1234\n---\n"

CHANGELOG_OK = ("# Governance changelog\n\n## Entries\n\n"
                "<!-- appended by the auto-apply track; none yet -->\n")


def _proposal(target, radius="escalating"):
    return ("---\ntarget: %s\nblast_radius: %s\n"
            "reason: The description overlaps another skill and misroutes selection\n"
            "evidence:\n  - memory/onboarding-baseline.md\nstatus: pending\n---\n"
            "# Proposal\n\n## Diff\n\n    -old\n    +new\n\n## Why\n\nBecause.\n"
            % (target, radius))


class TestBlastRadiusDiff(unittest.TestCase):
    """The #18 tripwire. Scoped to governed roots — a directory carrying a #21
    groundwork.pin — so every fixture repo plants one."""

    def _repo(self, d, pin_at=""):
        _git(d, "init", "-q")
        _git(d, "config", "user.email", "t@t.t")
        _git(d, "config", "user.name", "t")
        pre = (pin_at + "/") if pin_at else ""
        _write(d, pre + "groundwork.pin", PIN_OK)
        _write(d, pre + "skills/weekly-digest/SKILL.md", SKILL_T1)
        _write(d, pre + "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
        _write(d, pre + "governance/constitution/access.md", RULE_OK)
        _write(d, pre + "governance/changelog.md", CHANGELOG_OK)
        _write(d, pre + "memory/onboarding-baseline.md", MEM_OK)
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "base")
        return pre

    def test_unchanged_repo_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            self.assertEqual(validate.blast_radius_diff_findings(d, "HEAD"), [])

    def test_no_pin_means_dormant(self):
        # The engine repo carries no pin: the tripwire must not fire at all.
        with tempfile.TemporaryDirectory() as d:
            _git(d, "init", "-q")
            _git(d, "config", "user.email", "t@t.t")
            _git(d, "config", "user.name", "t")
            _write(d, "governance/constitution/access.md", RULE_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "base")
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            self.assertEqual(validate.blast_radius_diff_findings(d, "HEAD"), [])

    def test_rule_edit_without_proposal_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                and "access.md" in f.path for f in findings))

    def test_rule_edit_with_escalating_proposal_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            _write(d, "proposals/p1.md", _proposal("governance/constitution/access.md"))
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if f.level == "ERROR"], [])

    def test_declared_vs_actual_mismatch_errors(self):
        # The headline #18 case: a rule edit smuggled under a track1-body label.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            _write(d, "proposals/p1.md",
                   _proposal("governance/constitution/access.md", "track1-body"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "declared-vs-actual" in f.message
                                for f in findings))

    def test_track2_body_edit_needs_a_proposal(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/onboarding-orchestration/SKILL.md",
                   SKILL_OK.replace("# Onboarding orchestration",
                                    "# Onboarding orchestration\n\nAn added paragraph."))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_description_edit_under_track1_label_is_a_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Summarize the week's open threads for the team channel",
                                    "Summarize anything at all"))
            _write(d, "proposals/p1.md",
                   _proposal("skills/weekly-digest/SKILL.md", "track1-body"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "declared-vs-actual" in f.message
                                for f in findings))

    def test_owner_card_edit_escalates(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/owner-card.md", CARD_OK)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "owner-card.md" in f.path
                                for f in findings))

    def test_track1_body_edit_without_changelog_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Collect the week's open threads and summarize them.",
                                    "Collect the week's open threads and note blockers."))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            self.assertTrue(any(f.level == "WARN" and "changelog" in f.message for f in findings))

    def test_track1_body_edit_with_appended_changelog_line_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "skills/weekly-digest/SKILL.md",
                   SKILL_T1.replace("Collect the week's open threads and summarize them.",
                                    "Collect the week's open threads and note blockers."))
            _write(d, "governance/changelog.md", CHANGELOG_OK +
                   "- 2026-07-26 | skills/weekly-digest/SKILL.md | note blockers | scribe | a1b2c3d\n")
            self.assertEqual(validate.blast_radius_diff_findings(d, "HEAD"), [])

    def test_changelog_rewrite_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/changelog.md",
                   CHANGELOG_OK.replace("appended by the auto-apply track", "rewritten"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "append-only" in f.message
                                for f in findings))

    def test_changelog_deletion_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "governance", "changelog.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "changelog" in f.message
                                for f in findings))

    def test_new_rule_file_escalates(self):
        # git diff never lists an untracked file; the working-tree union must.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/new-rule.md", RULE_OK)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "new-rule.md" in f.path
                                for f in findings))

    def test_deleted_rule_warns_not_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "governance", "constitution", "access.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertEqual([f for f in findings if f.level == "ERROR"], [])
            self.assertTrue(any(f.level == "WARN" and "deleted" in f.message for f in findings))

    def test_removing_the_pin_does_not_ungovern_the_change(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            os.remove(os.path.join(d, "groundwork.pin"))
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_proposal_target_escaping_the_governed_root_does_not_match(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="company")
            _write(d, "company/governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            _write(d, "company/proposals/p1.md",
                   _proposal("../governance/constitution/access.md"))
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "no pending proposal" in f.message
                                for f in findings))

    def test_nested_governed_root_is_scoped(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin_at="company")
            _write(d, "company/governance/constitution/access.md", RULE_OK + "\nAppended.\n")
            _write(d, "company/proposals/p1.md",
                   _proposal("governance/constitution/access.md"))
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if f.level == "ERROR"], [])

    def test_symlinked_rule_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            p = os.path.join(d, "governance", "constitution", "access.md")
            os.remove(p)
            os.symlink(os.path.join(d, "memory", "onboarding-baseline.md"), p)
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" and "symlink" in f.message for f in findings))

    def test_non_utf8_working_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write_bytes(d, "governance/constitution/access.md", b"---\nowner: x\n---\n\xff\xfe bad\n")
            findings = validate.blast_radius_diff_findings(d, "HEAD")
            self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_unknown_base_ref_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            findings = validate.blast_radius_diff_findings(d, "no-such-ref")
            self.assertTrue(any(f.level == "ERROR" and "base ref" in f.message for f in findings))

    def test_workbench_trees_are_out_of_scope(self):
        # tests/ and docs/superpowers/ are the validator's own harness.
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "tests/fixtures/governance/constitution/x.md", RULE_OK)
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if "tests/" in f.path], [])

    def test_cli_wires_the_tripwire(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/constitution/access.md", RULE_OK + "\nAppended clause.\n")
            self.assertEqual(validate.main(["validate.py", d, "--diff", "HEAD"]), 1)
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestBlastRadiusDiff -v`
Expected: FAIL — `module 'validate' has no attribute 'blast_radius_diff_findings'`.

- [ ] **Step 3: Implement** — add to `scripts/validate.py`, immediately **after** `memory_diff_findings` and **before** `def main(argv):`:

```python
def _has_symlink_component(root, rel):
    """True when any component of root/rel is a symlink. A symlinked rule, skill,
    or ancestor directory cannot be classified honestly (it can point one place
    and be spelled another), so the caller fails closed."""
    p = root
    for part in rel.split("/"):
        p = os.path.join(p, part)
        if os.path.islink(p):
            return True
    return False


def _pin_dirs(root, base_files, scope):
    """Governed roots: every directory carrying a #21 groundwork.pin, collected
    from the BASE tree AND the working tree. Both sides matter — deleting the pin
    in the same diff must not un-govern the change that deleted it. Returned as
    root-relative directories, where "" is root itself. .gitignore is deliberately
    NOT honored: a pin hidden behind an ignore rule must not un-govern content."""
    dirs = set()
    for bf in base_files:
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        rel = bf if scope == "." else bf[len(scope) + 1:]
        if os.path.basename(rel) == "groundwork.pin":
            dirs.add(os.path.dirname(rel).replace("\\", "/"))
    for abspath in iter_files(root, ()):
        if os.path.basename(abspath) != "groundwork.pin":
            continue
        rel = os.path.relpath(abspath, root).replace(os.sep, "/")
        dirs.add(os.path.dirname(rel))
    return dirs


def _pending_proposal_radii(root, gov_rel):
    """{realpath(target) -> set(declared blast_radius)} for the pending proposals
    in <governed root>/proposals/. Targets resolve through the filesystem
    (realpath) and must stay contained in the governed root, so a symlink or a
    '../' alias can never point one place and match another — the same
    both-layers discipline check_proposals uses. Anything malformed is simply
    absent from the map, which makes the change it would have covered fail
    closed (no match -> the escalating ERROR fires)."""
    out = {}
    gov_abs = os.path.join(root, *gov_rel.split("/")) if gov_rel else root
    pdir = os.path.join(gov_abs, "proposals")
    if not os.path.isdir(pdir) or os.path.islink(pdir):
        return out
    try:
        names = sorted(os.listdir(pdir))
    except OSError:
        return out
    gov_real = os.path.realpath(gov_abs)
    for name in names:
        if not name.endswith(".md") or name in {"README.md", "_index.md"}:
            continue
        data, _f = _load_frontmatter(os.path.join(pdir, name), name)
        if data is None:
            continue
        status = data.get("status")
        if isinstance(status, str) and status.strip() and status.strip() != "pending":
            continue  # not pending; check_proposals already ERRORs on the lifecycle
        target, br = data.get("target"), data.get("blast_radius")
        if not isinstance(target, str) or not isinstance(br, str) or br not in BLAST_RADIUS:
            continue
        tabs = os.path.join(gov_abs, os.path.normpath(target.strip().replace("\\", "/")))
        if not os.path.isfile(tabs):
            continue
        treal = os.path.realpath(tabs)
        if not treal.startswith(gov_real + os.sep):
            continue
        out.setdefault(treal, set()).add(br)
    return out


def _changelog_appended_targets(root, gov_abs, appended_lines):
    """Realpaths of the skills named by changelog lines APPENDED since base. An
    old line for the same skill does not excuse a new edit, so only the appended
    span counts."""
    targets = set()
    for line in appended_lines:
        s = line.strip()
        if not s.startswith("- "):
            continue
        fields = [c.strip() for c in s[2:].split("|")]
        if len(fields) != 5:
            continue
        p = os.path.join(gov_abs, os.path.normpath(fields[1].replace("\\", "/")))
        if os.path.isfile(p):
            targets.add(os.path.realpath(p))
    return targets


def blast_radius_diff_findings(root, base):
    """#18's blast-radius tripwire. On --diff, classify every changed skill/rule
    under a governed root (a directory carrying a #21 groundwork.pin) and require
    each ESCALATING change to trace to a pending proposal whose DECLARED
    blast_radius matches what the diff ACTUALLY touches. A track-1 body-only
    change wants its changelog line (WARN — a stateless validator cannot tell an
    agent auto-apply from the maintainer's own edit); the changelog itself is
    append-only (ERROR).

    What this cannot do: prove a human truthfully reviewed anything. That is the
    commit bit's job (#18) — see docs/known-limitations.md."""
    ctx, ctx_findings = _git_diff_context(root, base)
    if ctx is None:
        return ctx_findings
    toplevel, scope, base_files = ctx["toplevel"], ctx["scope"], ctx["base_files"]
    findings = []

    base_rels = {}
    for bf in base_files:
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        base_rels[(bf if scope == "." else bf[len(scope) + 1:])] = bf

    gov_roots = _pin_dirs(root, base_files, scope)
    if not gov_roots:
        return findings  # no company instance in scope: the tripwire is dormant

    def governed_root_of(rel):
        best = None
        for g in gov_roots:
            if g == "" or rel == g or rel.startswith(g + "/"):
                if best is None or len(g) > len(best):
                    best = g
        return best

    # --- Pass 1: the changelog per governed root (append-only + appended span).
    appended_targets = {}
    for g in sorted(gov_roots):
        gov_abs = os.path.join(root, *g.split("/")) if g else root
        cl_rel = (g + "/" if g else "") + "governance/changelog.md"
        appended_targets[g] = set()
        bf = base_rels.get(cl_rel)
        if bf is None:
            continue  # no committed ledger at base: nothing to protect yet
        old = _git_show(toplevel, base, bf)
        if old is None:
            findings.append(Finding("ERROR", cl_rel, None,
                                    "cannot verify the governance changelog: its base version is "
                                    "unreadable or not valid UTF-8"))
            continue
        abspath = os.path.join(root, *cl_rel.split("/"))
        if _has_symlink_component(root, cl_rel):
            findings.append(Finding("ERROR", cl_rel, None,
                                    "the governance changelog is or sits behind a symlink "
                                    "(cannot verify it is append-only)"))
            continue
        if not os.path.isfile(abspath):
            findings.append(Finding("ERROR", cl_rel, None,
                                    "the governance changelog was deleted — it is an append-only "
                                    "index of auto-applied changes (#17)"))
            continue
        new, rd = _read_utf8(abspath, cl_rel)
        if new is None:
            findings += rd
            continue
        if not _changelog_append_only(old, new):
            findings.append(Finding("ERROR", cl_rel, None,
                                    "the governance changelog is append-only — an existing entry was "
                                    "edited, reordered, or removed (#17)"))
            continue
        old_lines = old.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        while old_lines and not old_lines[-1].strip():
            old_lines.pop()
        new_lines = new.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        appended_targets[g] = _changelog_appended_targets(root, gov_abs, new_lines[len(old_lines):])

    # --- Pass 2: every changed governed file.
    candidates = set(base_rels)
    for abspath in iter_files(root, ()):
        candidates.add(os.path.relpath(abspath, root).replace(os.sep, "/"))

    proposals_cache = {}
    for rel in sorted(candidates):
        if _diff_in_workbench_skips(rel):
            continue
        g = governed_root_of(rel)
        if g is None:
            continue
        inner = rel if g == "" else rel[len(g) + 1:]
        cls = _governed_class(inner)
        if cls is None:
            continue

        abspath = os.path.join(root, *rel.split("/"))
        bf = base_rels.get(rel)
        if bf is not None:
            status = _committed_path_status(toplevel, bf.split("/"), None)
            if status == "symlink":
                findings.append(Finding("ERROR", rel, None,
                                        "governed file is or sits behind a symlink (cannot classify "
                                        "its blast radius)"))
                continue
            if status == "missing":
                findings.append(Finding("WARN", rel, None,
                                        "governed file deleted — retiring a rule or skill is escalating, "
                                        "and its record is the maintainer's consent commit; a proposal "
                                        "cannot name a target that no longer exists (#18)"))
                continue
            old = _git_show(toplevel, base, bf)
            if old is None:
                findings.append(Finding("ERROR", rel, None,
                                        "cannot classify this change: the base version is unreadable "
                                        "or not valid UTF-8"))
                continue
            kind = "modified"
        else:
            if _has_symlink_component(root, rel):
                findings.append(Finding("ERROR", rel, None,
                                        "governed file is or sits behind a symlink (cannot classify "
                                        "its blast radius)"))
                continue
            if not os.path.isfile(abspath):
                continue
            old, kind = None, "added"

        new, rd = _read_utf8(abspath, rel)
        if new is None:
            findings += rd
            continue

        radius, detail = classify_governed_change(kind, cls, old, new)
        if radius is None:
            continue

        if g not in proposals_cache:
            proposals_cache[g] = _pending_proposal_radii(root, g)
        radii = proposals_cache[g].get(os.path.realpath(abspath), set())
        prefix = (g + "/") if g else ""

        if radius == "escalating":
            if not radii:
                findings.append(Finding("ERROR", rel, None,
                                        "escalating change (%s) with no pending proposal — an escalating "
                                        "change reaches the main line only through a reviewable proposal "
                                        "in %sproposals/ (#18)" % (detail, prefix)))
            elif "escalating" not in radii:
                findings.append(Finding("ERROR", rel, None,
                                        "declared-vs-actual blast-radius mismatch: the pending proposal "
                                        "declares 'track1-body' but this change actually touches %s — "
                                        "that is escalating (#18)" % detail))
        elif not radii and os.path.realpath(abspath) not in appended_targets.get(g, set()):
            findings.append(Finding("WARN", rel, None,
                                    "track-1 body-only change with no new governance changelog entry — "
                                    "an agent auto-apply must append its line (#17); a maintainer's own "
                                    "edit needs none"))
    return findings
```

- [ ] **Step 4: Wire into `main()`.** In `main(argv)`, replace:

```python
    if diff_base is not None:
        findings += memory_diff_findings(root, diff_base)
```

with:

```python
    if diff_base is not None:
        findings += memory_diff_findings(root, diff_base)
        findings += blast_radius_diff_findings(root, diff_base)
```

- [ ] **Step 5: Run to verify passing**

Run: `python3 -m unittest tests.test_validate.TestBlastRadiusDiff -v`
Expected: PASS (22 tests).

Run: `python3 -m unittest discover -s tests`
Expected: OK — 325 tests (281 + 22 pure + 22 CLI).

Run: `python3 scripts/validate.py . && python3 scripts/validate.py . --diff main; echo "exit: $?"`
Expected: `0 error(s), 9 warning(s)` on both, `exit: 0`. The engine repo carries no `groundwork.pin`, so the tripwire is dormant here — that is the designed behavior (Design call 1), not a silent pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #18 blast-radius --diff tripwire (declared-vs-actual, append-only changelog)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The documented Known Limitation + convention docs

**Files:** Modify `docs/known-limitations.md`, `proposals/README.md`

- [ ] **Step 1: Append to `docs/known-limitations.md`** (a new section at the end of the file):

```markdown
## Governance — the consent gate and its tripwire

- **A stateless validator cannot prove a human reviewed anything.** `validate --diff <base>`
  is a **tripwire**, not the teeth. It can prove that an escalating change is accompanied by
  a pending proposal whose *declared* blast radius matches what the diff *actually* touches —
  it cannot tell a maintainer-typed `approved_by` from an agent-forged one. The real
  enforcement is the **commit bit** (#18): only the git-capable maintainer can land a change
  on the main line; agents only propose. The guarantee is therefore "no unreviewed escalating
  change lands *as long as the commit bit stays with a human who runs the validator*" — a
  permissions convention, not a cryptographic proof.
- **The tripwire only governs pinned content.** It fires on files under a directory carrying a
  `groundwork.pin` (#21) — i.e. generated company content. The groundwork engine repo is
  pin-less by design, so its own `skills/` and `governance/constitution/` exemplars are not
  governed by it. Whether groundwork governs its own maintenance with its own consent gate is
  the same open question as the hook set above, not an oversight.
- **A deleted rule or skill is a WARN, not an ERROR.** Retirement is legitimate (rules carry
  `sunset`, cards carry `retirement_condition`) and it is escalating — but a proposal's
  `target` must be an existing file, so a deletion can never be traced to one. Making it an
  ERROR would build a gate nothing could clear. The honest record of a deletion is the
  maintainer's consent commit.
- **A missing changelog line is a WARN, not an ERROR.** The validator cannot distinguish an
  agent's auto-apply from the maintainer editing their own skill body. ERRORing would
  false-positive on ordinary work and fill the changelog with non-auto-applies, destroying the
  one-glance property that justifies conceding pre-approval on track-1 (#17).
- **Changelog rotation is not supported in V1.** The append-only check compares against the
  base version, so archiving or rotating `governance/changelog.md` reads as a rewrite. #17
  left rotation cadence as a build-phase detail; it lands with a documented rotation
  convention, not before.
```

- [ ] **Step 2: Append to `proposals/README.md`** (at the end of the file):

```markdown
## What the validator enforces (`validate --diff <base>`)

At PR time the validator classifies every changed skill and rule under a governed root
(a directory carrying a `groundwork.pin`) and checks the **declaration against the diff**:

- An **escalating** change with **no pending proposal** → ERROR.
- A pending proposal declaring **`track1-body`** while the diff actually touches a rule, a
  track-2 skill, frontmatter, or the Owner's Card → ERROR (**declared-vs-actual mismatch** —
  this is what stops a rule edit being smuggled under a track-1 label).
- A **track-1 body-only** change with no newly appended changelog line → WARN (an agent
  auto-apply must log its line; a maintainer's own edit needs none).
- Any edit, reorder, or removal of an existing `governance/changelog.md` entry → ERROR.

The tripwire cannot prove a human truly reviewed the change — the commit bit does that.
See [docs/known-limitations.md](../docs/known-limitations.md).
```

- [ ] **Step 3: Full gate**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py . && python3 scripts/validate.py . --diff main; echo "exit: $?"`
Expected: 325 tests OK; both validator runs report `0 error(s)`; `exit: 0`.

- [ ] **Step 4: Commit**

```bash
git add docs/known-limitations.md proposals/README.md
git commit -m "docs: #18 Known Limitation (the commit bit is the teeth) + tripwire convention

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **The `since:` retrofit + skew scatter-suppression** (#21) stay deferred to the first real v2 breaking bump, documented in `MIGRATIONS.md`.
- **Changelog rotation** (#17 left cadence as a build-phase detail) — documented as a Known Limitation, not built.
- **A live proposal or pin in the engine root** — still none, by design. The tripwire is fixture-proven and activates on `demo/` (Phase 2.3) and `your-company/`.
- **After this slice, Phase 1 governance is complete** → next is **D2 Move 2** at the Phase 1→2 boundary: the product `AGENTS.md`, the one-line `CLAUDE.md`, `.cursor/rules/*.mdc` pointers, and the deferred #13 AGENTS.md-chain context-budget check (>32 KiB hard ERROR).

## Self-Review

- **Ticket coverage (#18 §3.2, the tripwire):** "classify every change" → `_governed_class` + `classify_governed_change`; "every escalating change must trace to an approved proposal" → the no-pending-proposal ERROR; "**whose declared blast-radius matches what the diff actually touches**" → the declared-vs-actual ERROR (the sharp new thing #18 adds — headline test `test_declared_vs_actual_mismatch_errors`); "mismatch or missing-proposal → ERROR" → both are ERROR; "non-escalating change needs only its changelog entry" → the track-1 changelog check (WARN, Design call 2); "#17 changelog append-only" → `_changelog_append_only` ERROR; "**honest limit → Known Limitation**" → `docs/known-limitations.md` §Governance. #17's boundary is implemented exactly: description / governance frontmatter / Owner's Card / any track-2 skill / any rule → escalating.
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; every step carries complete code and a verification command with expected output.
- **Type consistency:** `Finding(level, path, line, message)`, `_load_frontmatter` → `(data|None, findings)`, `_read_utf8` → `(text|None, findings)`, `_frontmatter_and_body` → `(data, body, findings)`, `_committed_path_status` → `'ok'|'symlink'|'missing'`, `_git_diff_context` → `(ctx|None, findings)`, `_git_show` → `str|None`. `BLAST_RADIUS`, `ACTION_CLASSES`, `TRACK2_CLASSES` reused, not redefined. No new imports.
- **Pre-empts the recurring Codex findings.** (a) *Non-scalar frontmatter:* `isinstance(..., str)` guards on `target`, `blast_radius`, `status`, `action_class`; a bare `key:` parses to `[]` and fails every one of them, landing on escalating. (b) *Alias laundering, both layers:* proposal targets are `normpath`'d **and** `realpath`-contained in the governed root, and matched against the changed file's `realpath` — plus `_has_symlink_component` / `_committed_path_status` reject symlinked governed files outright; `test_proposal_target_escaping_the_governed_root_does_not_match` and `test_symlinked_rule_fails_closed` are the regressions. (c) *Fail-open on malformed input:* unreadable base blob, non-UTF-8 working file, unparseable frontmatter, missing/invalid `action_class`, malformed proposal — every one lands on ERROR or escalating, never a silent allow. (d) *Scope laundering:* governed roots come from base **and** working tree, so deleting the pin cannot un-govern the diff (`test_removing_the_pin_does_not_ungovern_the_change`); the candidate set is base ∪ working tree, so an **untracked** new rule is still caught (`test_new_rule_file_escalates`); `.gitignore` is deliberately not honored in either scan.
- **Convention parity:** the extraction in Task 1 keeps `memory_diff_findings`' existing messages byte-identical except the one deliberately merged base-read message, whose two assertions are updated in the same step; the existing memory-diff suites are the regression proof.
- **Load-bearing calls surfaced, not buried:** the three design calls are stated up front with the record that decides each and an honest counter-argument, per the explain-before-deciding rule.
