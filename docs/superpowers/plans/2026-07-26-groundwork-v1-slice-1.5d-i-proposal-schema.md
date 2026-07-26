# groundwork V1 — Slice 1.5d-i: Proposal + changelog schema (#17/#18) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the two file-based records of governed self-improvement — the **proposal file** (the consent gate's canonical artifact, #18) carrying #17's proposal schema, and the **governance changelog** (the auto-apply track's append-only index, #17) — plus their static validator checks. The blast-radius `--diff` *tripwire* (the enforcement teeth) is the next sub-slice (1.5d-ii).

**Architecture:** A proposal is one `.md` file in `proposals/` (pending-only, #18), frontmatter carrying the #17 schema: `target` (the skill or rule it changes), `blast_radius` (`track1-body` | `escalating`), `reason`, `evidence` links, and `status: pending`. `check_proposals` validates schema completeness (incomplete → WARN, "demote to a working note") and the two invariants that don't need a diff: the routing **domain** (skills + constitution rules only) and **rules-never-auto-apply** (a rule target with `blast_radius: track1-body` is a contradiction). The **changelog** is `governance/changelog.md` — an append-only, one-line-per-auto-apply index pointing at commits; `check_changelog` validates entry format. Both records are runtime artifacts (a proposal is transient; the changelog fills as auto-applies land), so — like the #21 pin — they are proven here by fixtures and carry no committed live exemplar. The diff-based teeth (declared-vs-actual blast-radius; changelog append-only enforcement) are 1.5d-ii.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **Codebase conventions (match them):** checks take `(root, ignore=())` and honor `_ignored` for `.gitignore` parity; read structured files via `_load_frontmatter(abspath, relpath)` (returns `(data|None, findings)`; `None` = unreadable, findings already carry the ERROR — fail closed, never crash). Reuse `_blank`, `Finding`.
- **#17 routing domain:** proposals route changes to **skills and constitution rules only**. Org-memory, Owner's Cards, and ontology worksheets keep their own governance (they enter this routing only when the promotion path graduates one into a proposed skill/rule change).
- **#17 blast-radius boundary:** `track1-body` = touches only the SKILL.md body of a track-1 (read-only / reversible-write) skill → auto-apply eligible. Everything else — description, governance frontmatter, Owner's Card, any track-2 skill, **any rule** — is `escalating` → needs sign-off. (The *declared-vs-actual* enforcement is 1.5d-ii; this slice checks the declaration's internal consistency.)
- **#17 completeness:** a complete proposal carries diff + reason + evidence + blast-radius. Incomplete → **demoted to a working note** (surfaced here as WARN, not a hard fail — incompleteness is a routing state).
- **#18 lifecycle:** `proposals/` is **pending-only**; an applied proposal evaporates into the git consent commit. A non-pending `status` in `proposals/` is a lifecycle violation (ERROR).
- **#17 changelog:** central, append-only, one line per auto-apply (date, skill, gist, agent, commit sha); **index, not store** (points at commits). Auto-apply is skills-only, track-1.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.5c merged to `main` (done: `7b2dbe2`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.5d-i-proposals`.

---

## File Structure

- `scripts/validate.py` — **modify.** Add `BLAST_RADIUS`; add `check_proposals(root, ignore=())` and `check_changelog(root, ignore=())`; wire both into `validate()`.
- `tests/test_validate.py` — **modify.** Proposal-schema + changelog-format tests (tempdir fixtures).
- `proposals/README.md` — **create.** The proposal-file convention (schema, lifecycle, consent ladder).
- `governance/changelog.md` — **create.** The append-only auto-apply index (header + format; no entries yet).

> **Design notes.**
> 1. **No committed live proposal.** `proposals/` is pending-only and a proposal evaporates on apply; a committed exemplar would be a real pending change that never applies — semantically wrong. So the schema is documented (`proposals/README.md`) and proven by fixtures, exactly as #21's pin has no engine-root instance. It activates the moment a real proposal exists.
> 2. **Two tracks, two records (do not merge them):** auto-apply (track-1) → a changelog line; sign-off (escalating) → a git consent commit (the merge). `check_proposals` governs the sign-off artifact; `check_changelog` governs the auto-apply record. #18 is explicit that signed-off changes need no second ledger.
> 3. **This slice adds no diff logic.** Declared-vs-actual blast-radius matching and changelog append-only enforcement both require a base comparison → 1.5d-ii (reusing 1.4b's `--diff` infra).

---

## Task 1: Proposal schema + `check_proposals`

**Files:**
- Modify: `scripts/validate.py`, `tests/test_validate.py`
- Create: `proposals/README.md`

**Interfaces:**
- Produces: `BLAST_RADIUS = {"track1-body", "escalating"}`; `check_proposals(root, ignore=())`, wired into `validate(root)`.

- [ ] **Step 1: Create `proposals/README.md`:**

```markdown
# Proposals — the consent gate

An agent may **propose** a change to a skill or a constitution rule; only the
maintainer may **land** it (the commit bit is the real teeth, #18). A proposal is one
file here, and that file **is** the review file — diff, reason, evidence, and the
blast-radius declaration in one place.

`proposals/` is **pending-only.** When a proposal is approved and applied, the file is
**removed** — the change now lives in the edited skill/rule plus the git record of
consent (the merge commit, or an `approved_by` commit on the branchless floor). The
git event is the durable record; a PR is just the richest way to review it.

## Schema (frontmatter)

```
---
target: skills/<name>/SKILL.md        # or governance/constitution/<rule>.md
blast_radius: escalating              # track1-body | escalating
reason: <one line: why this change>
evidence:                             # org-memory records / motivating sessions
  - memory/<record>.md
status: pending
---
# Proposal: <title>

## Diff
​```diff
<the proposed change>
​```

## Why
<the reasoning, expanding the one-line reason>
```

## Routing (three buckets, #17)

- **`track1-body`** — touches **only** the SKILL.md body of a **track-1** (read-only /
  reversible-write) skill. Auto-applies with a changelog line; no human merge needed.
- **`escalating`** — touches a description, governance frontmatter, or an Owner's Card;
  or any track-2 skill; or **any constitution rule**. Needs the maintainer's sign-off.
  Rules are `escalating` by construction — they never auto-apply.
- **Incomplete** (missing reason / evidence) — demoted to an org-memory working note
  with the gaps named; it re-enters as a proposal when the gaps fill.

Proposals route **skills and rules only.** Org-memory, Owner's Cards, and ontology
worksheets keep their own governance; a memory enters this routing only when it
graduates into a proposed skill/rule change.

## Consent ladder (richest → floor)

GitHub **draft PR** → `proposal/*` **branch-merge** (Cursor / GitLab / local git) →
self-attested **`approved_by` + `approved_at`** on the committed file (the weakest rung).
The file is canonical; each rung is a way of reviewing it.
```

- [ ] **Step 2: Add failing tests** to `tests/test_validate.py`:

```python
PROPOSAL_OK = """---
target: skills/onboarding-orchestration/SKILL.md
blast_radius: escalating
reason: Tighten the description so it stops overlapping the offboarding skill
evidence:
  - memory/onboarding-baseline.md
status: pending
---
# Proposal: sharpen onboarding description

## Diff
(elided)

## Why
The two descriptions overlap and misroute selection.
"""


class TestProposals(unittest.TestCase):
    def _prop(self, d, text=PROPOSAL_OK, name="p1.md"):
        _write(d, "proposals/%s" % name, text)
        _write(d, "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
        _write(d, "memory/onboarding-baseline.md", MEM_OK)

    def test_valid_proposal_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d)
            self.assertEqual([f for f in validate.check_proposals(d) if f.level == "ERROR"], [])

    def test_missing_target_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("target: skills/onboarding-orchestration/SKILL.md\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "target" in f.message
                                for f in validate.check_proposals(d)))

    def test_target_outside_domain_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("skills/onboarding-orchestration/SKILL.md",
                                              "ontologies/people-hr/onboarding-orchestration.md"))
            self.assertTrue(any(f.level == "ERROR" and "skill" in f.message.lower()
                                for f in validate.check_proposals(d)))

    def test_invalid_blast_radius_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("blast_radius: escalating", "blast_radius: trivial"))
            self.assertTrue(any(f.level == "ERROR" and "blast_radius" in f.message
                                for f in validate.check_proposals(d)))

    def test_rule_target_cannot_be_track1_body(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "proposals/p.md",
                   PROPOSAL_OK.replace("skills/onboarding-orchestration/SKILL.md",
                                       "governance/constitution/access.md")
                   .replace("blast_radius: escalating", "blast_radius: track1-body"))
            _write(d, "governance/constitution/access.md", RULE_OK)
            self.assertTrue(any(f.level == "ERROR" and "never auto-apply" in f.message
                                for f in validate.check_proposals(d)))

    def test_non_pending_status_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("status: pending", "status: applied"))
            self.assertTrue(any(f.level == "ERROR" and "pending-only" in f.message
                                for f in validate.check_proposals(d)))

    def test_incomplete_proposal_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._prop(d, PROPOSAL_OK.replace("reason: Tighten the description so it stops overlapping the offboarding skill\n", ""))
            findings = validate.check_proposals(d)
            self.assertTrue(any(f.level == "WARN" and "working note" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "reason" in f.message for f in findings))
```

- [ ] **Step 3: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestProposals -v`
Expected: FAIL — no attribute `check_proposals`.

- [ ] **Step 4: Implement** — add to `scripts/validate.py`:

```python
BLAST_RADIUS = {"track1-body", "escalating"}


def check_proposals(root, ignore=()):
    """#17/#18 proposal-file schema. Diff-based declared-vs-actual matching is 1.5d-ii;
    this checks the static schema, the routing domain, and the pending-only lifecycle."""
    findings = []
    base = os.path.join(root, "proposals")
    if not os.path.isdir(base) or _ignored("proposals", ignore):
        return findings
    for name in sorted(os.listdir(base)):
        if not name.endswith(".md") or name in {"README.md", "_index.md"} or _ignored(name, ignore):
            continue
        abspath = os.path.join(base, name)
        rel = os.path.relpath(abspath, root)
        data, fm = _load_frontmatter(abspath, rel)
        findings += fm
        if data is None:
            continue

        target = data.get("target")
        target_is_rule = False
        if _blank(target):
            findings.append(Finding("ERROR", rel, None, "proposal missing 'target' (the skill or rule it changes)"))
        elif not isinstance(target, str):
            findings.append(Finding("ERROR", rel, None, "proposal 'target' must be a single path"))
        else:
            t = target.strip().replace("\\", "/")
            is_skill = t.startswith("skills/")
            target_is_rule = t.startswith("governance/constitution/")
            if not (is_skill or target_is_rule):
                findings.append(Finding("ERROR", rel, None,
                                        "proposal 'target' must be a skill (skills/) or a constitution rule "
                                        "(governance/constitution/); other artifacts keep their own governance (#17)"))
            elif not os.path.isfile(os.path.join(root, t)):
                findings.append(Finding("ERROR", rel, None, "proposal 'target' not found: %s" % t))

        br = data.get("blast_radius")
        if _blank(br):
            findings.append(Finding("ERROR", rel, None, "proposal missing 'blast_radius' (track1-body | escalating)"))
        elif not (isinstance(br, str) and br in BLAST_RADIUS):
            findings.append(Finding("ERROR", rel, None,
                                    "invalid 'blast_radius' %r (one of %s)" % (br, sorted(BLAST_RADIUS))))
        elif br == "track1-body" and target_is_rule:
            findings.append(Finding("ERROR", rel, None,
                                    "a constitution rule can never be 'track1-body' — rules never auto-apply; "
                                    "they are escalating by construction (#17)"))

        status = data.get("status")
        if isinstance(status, str) and status.strip() and status.strip() != "pending":
            findings.append(Finding("ERROR", rel, None,
                                    "proposals/ is pending-only; an applied proposal evaporates into the "
                                    "consent commit (#18) — status is %r" % status))

        if _blank(data.get("reason")):
            findings.append(Finding("WARN", rel, None,
                                    "incomplete proposal: missing 'reason' — belongs as an org-memory "
                                    "working note until it fills (#17)"))
        ev = data.get("evidence")
        if _blank(ev):
            findings.append(Finding("WARN", rel, None,
                                    "incomplete proposal: missing 'evidence' links — demote to a working note (#17)"))
        else:
            for e in (ev if isinstance(ev, list) else [ev]):
                if isinstance(e, str) and e.strip() and not os.path.isfile(os.path.join(root, e.strip())):
                    findings.append(Finding("WARN", rel, None, "evidence link not found: %s" % e.strip()))
    return findings
```

- [ ] **Step 5: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_symlinked_dirs(root)`, add:

```python
    findings += check_proposals(root, ignore)
```

- [ ] **Step 6: Run tests + validate**

Run: `python3 -m unittest tests.test_validate.TestProposals -v && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0 (no `proposals/` records in the engine repo → `check_proposals` silent; `proposals/README.md` is skipped).

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py proposals/README.md
git commit -m "feat(validate): #17/#18 proposal-file schema (domain, blast-radius, pending-only lifecycle)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The governance changelog + `check_changelog`

**Files:**
- Modify: `scripts/validate.py`, `tests/test_validate.py`
- Create: `governance/changelog.md`

**Interfaces:**
- Produces: `check_changelog(root, ignore=())`, wired into `validate(root)`. Each entry (a `- ` bullet) must be `YYYY-MM-DD | <skills/… path> | <gist> | <agent> | <sha>` — malformed → WARN (a record, not machinery). Append-only *enforcement* is 1.5d-ii.

- [ ] **Step 1: Create `governance/changelog.md`:**

```markdown
# Governance changelog

The append-only index of **auto-applied** (track-1) changes — body-only edits to
track-1 skills that landed without a human merge (#17). One line per change; full
diffs live in git. This file is **never edited or reordered — only appended** (the
`validate --diff` mode enforces that at PR time). The maintainer scans it in the
reconciliation pass; the one-glance property is what makes conceding pre-approval on
track-1 defensible.

Entry format:

`- YYYY-MM-DD | <skill path> | <gist> | <proposing agent> | <commit sha>`

## Entries

<!-- appended by the auto-apply track; none yet -->
```

- [ ] **Step 2: Add failing tests** to `tests/test_validate.py`:

```python
class TestChangelog(unittest.TestCase):
    def test_empty_changelog_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md", "# Governance changelog\n\n## Entries\n")
            self.assertEqual(validate.check_changelog(d), [])

    def test_valid_entry_clean(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- 2026-07-26 | skills/onboarding-orchestration/SKILL.md | trimmed wording | scribe | a1b2c3d\n")
            self.assertEqual([f for f in validate.check_changelog(d) if f.level == "ERROR"], [])
            self.assertEqual(validate.check_changelog(d), [])

    def test_malformed_entry_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n- oops not a real entry\n")
            self.assertTrue(any(f.level == "WARN" for f in validate.check_changelog(d)))

    def test_bad_date_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n"
                   "- last-tuesday | skills/x/SKILL.md | gist | agent | a1b2c3d\n")
            self.assertTrue(any(f.level == "WARN" and "date" in f.message for f in validate.check_changelog(d)))

    def test_no_changelog_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_changelog(d), [])
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestChangelog -v`
Expected: FAIL — no attribute `check_changelog`.

- [ ] **Step 4: Implement** — add to `scripts/validate.py`:

```python
def check_changelog(root, ignore=()):
    """#17 governance changelog: append-only index of auto-applied track-1 changes.
    Validates entry format; append-only enforcement is the --diff mode (1.5d-ii)."""
    findings = []
    path = os.path.join(root, "governance", "changelog.md")
    if not os.path.isfile(path) or _ignored("governance", ignore) or _ignored("changelog.md", ignore):
        return findings
    rel = os.path.relpath(path, root)
    text, rd = _read_utf8(path, rel)
    findings += rd
    if text is None:
        return findings
    for lineno, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if not s.startswith("- "):
            continue
        fields = [c.strip() for c in s[2:].split("|")]
        if len(fields) != 5:
            findings.append(Finding("WARN", rel, lineno,
                                    "malformed changelog entry (want: date | skill | gist | agent | sha)"))
            continue
        date_s, skill_s, _gist, _agent, sha_s = fields
        if _parse_date(date_s) is None:
            findings.append(Finding("WARN", rel, lineno, "changelog entry has an unparseable date: %r" % date_s))
        if not skill_s.replace("\\", "/").startswith("skills/"):
            findings.append(Finding("WARN", rel, lineno,
                                    "changelog entry skill path should be under skills/ (auto-apply is track-1 skills only)"))
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha_s):
            findings.append(Finding("WARN", rel, lineno, "changelog entry commit sha looks malformed: %r" % sha_s))
    return findings
```

- [ ] **Step 5: Wire into `validate()`** — after `findings += check_proposals(root, ignore)`, add:

```python
    findings += check_changelog(root, ignore)
```

- [ ] **Step 6: Run the full suite + real gate**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS.

Run: `python3 scripts/validate.py .`
Expected: exit 0 (the committed `governance/changelog.md` has no entries yet, so `check_changelog` finds nothing to flag).

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py governance/changelog.md
git commit -m "feat(validate): #17 governance changelog + entry-format check (append-only index)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next sub-slices)

- **Slice 1.5d-ii (the tripwire — the enforcement teeth):** on `validate --diff <base>` (reusing 1.4b's git infra), classify every changed skill/rule; each **escalating** change must trace to a pending proposal whose **declared** `blast_radius` matches what the diff **actually** touches (declared-vs-actual — the sharp thing #18 adds); a non-escalating (track-1 body-only) change needs its **changelog** entry; and the changelog is enforced **append-only**. Plus the documented Known Limitation (a stateless validator cannot prove a human reviewed — the commit bit is the real teeth).
- **Phase 2.3 / runtime:** actual proposals flowing (they are transient — none is committed here); the demo may show one end-to-end.
- **After 1.5d-ii, Phase 1 governance is complete** → next is **Move 2** (author `AGENTS.md`, collapse `CLAUDE.md`, `.cursor/rules/`, the AGENTS.md-chain budget check) at the Phase 1→2 boundary, then Phase 2 (horizontal fill + `demo/`).

## Self-Review

- **Ticket coverage:** #17 proposal schema (diff/reason/evidence/blast-radius) → `proposals/README.md` + `check_proposals`; routing domain (skills+rules only) → the target-domain ERROR; blast-radius boundary declaration + rules-never-auto-apply → the `track1-body`+rule ERROR; completeness → incomplete-WARN; #18 pending-only lifecycle → non-pending-status ERROR; consent ladder → documented in `proposals/README.md`; #17 changelog (append-only index, one line per auto-apply, index-not-store) → `governance/changelog.md` + `check_changelog`. The **declared-vs-actual tripwire and append-only enforcement are explicitly deferred to 1.5d-ii** (they need a diff).
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; complete code and content; verification commands have expected output.
- **Type consistency:** `_load_frontmatter`, `_read_utf8`, `_blank`, `_parse_date`, `_ignored`, `Finding` reused with existing signatures; checks take `(root, ignore=())` matching the codebase and their call sites in `validate()`; `BLAST_RADIUS` is a set.
- **Convention parity (pre-empts prior Codex findings):** structured reads go through `_load_frontmatter`/`_read_utf8` (fail-closed on non-UTF-8, never crash); non-scalar guards (`isinstance(..., str)`) on `target`/`blast_radius`/`status`; `.gitignore` parity via `_ignored`. No committed live proposal (transient artifact, like the #21 pin) — proven by fixtures.
```

