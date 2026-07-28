# groundwork V1 — Slice 2.3a: instance-aware validation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the five structural checks discover groundwork content **anywhere under the validated root**, not just at the root itself — so that `demo/` (and `your-company/`) are governed the same way the engine root is. This must land **before** any demo content is authored, or Phase 2.3 would build a whole synthetic company that the validator silently ignores while the gate stayed green. It also closes a named Slice 1.5d-ii deferral.

**Architecture:** One new primitive, `_instance_roots(root, ignore=())`, returning every directory that carries a well-known content directory (`ontologies/`, `skills/`, `governance/`, `proposals/`, `memory/`). Each of `check_ontology`, `check_owner_cards`, `check_constitution`, `check_proposals`, and `check_changelog` becomes a thin loop over those roots wrapping its existing body, unchanged. Cross-references (a skill's `ontology:`, its `baseline:`, a proposal's `target:`, a changelog's skill path) resolve **within the same instance**, which is what makes `demo/` a faithful model of a company repo rather than a folder borrowing the engine's exemplars. `check_memory` already works this way and is the precedent being generalized.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

---

## Why this is a slice, and where it sits

Phase 2.3 (`demo/`) is the largest remaining item on the runway. Decomposed, it is:

| Slice | Contents |
|---|---|
| **2.3a** (this plan) | Instance-aware validation. Fixture-proven; no demo content yet. |
| 2.3b | The demo canon (#16) + `check_synthetic_identifiers` (demo-scoped ERROR) + the demo skeleton. |
| 2.3c | The demo company's ontologies + org memory, including the async-standups decision record with its supersession chain (demo query 1). |
| 2.3d | The demo's skills + Owner's Cards + constitution, including the rung-5 human-decision rule, and the meeting-challenger runnable exemplar (#8 item 3). |
| 2.3e | The 15-minute 3-query script, `demo/groundwork.pin`, and one live pending proposal — the capstone that takes the #18 tripwire and the #21 skew gate live. |

**Why the pin lands last (2.3e), not first:** once `demo/groundwork.pin` exists, `demo/` becomes a governed root and every *addition* of a demo skill or rule is an escalating change that the #18 tripwire requires a matching pending proposal for. Authoring the demo's content under that constraint would mean shipping a proposal per file. Landing the pin after the content is stable means the tripwire activates on a settled instance — and from then on, changes to demo content genuinely do need proposals, which is the demo working as designed.

---

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **This is a refactor, not a rewrite.** Each check's *body* — every rule, severity, and message — is unchanged. Only the directory it starts from and the base for reference resolution move. If a rule needs changing to make this work, stop and say so rather than editing it silently.
- **Findings report root-relative paths.** `os.path.relpath(x, root)` stays relative to the validated root, not the instance, so output is unchanged for the existing repo.
- **The engine repo must be byte-identical in output.** Root is currently the only instance, so `python3 scripts/validate.py .` must still print exactly `0 error(s), 7 warning(s)`. Any change to that number is a regression, not an improvement.
- **Codebase conventions:** reuse `Finding`, `_read_utf8`, `_load_frontmatter`, `_blank`, `_ignored`, `SKIP_DIRS`, `SKIP_RELPATHS`, `_memory_record_files`, `_live_record_realpaths`, `_record_ref_realpath`.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.2b merged and pushed (`d90f5d5`; 535 tests, 1 designed skip, gate exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.3a-instance-aware
```

---

## Design calls flagged for the maintainer

**1. The finding that reorders Phase 2.3: five checks are root-only, so `demo/` would have shipped unchecked.**
Verified directly against merged `main`:

| Check | Base | Instance-aware? |
|---|---|---|
| `check_ontology` | `root/ontologies` | **no** |
| `check_owner_cards` | `root/skills` | **no** |
| `check_constitution` | `root/governance/constitution` | **no** |
| `check_proposals` | `root/proposals` | **no** |
| `check_changelog` | `root/governance/changelog.md` | **no** |
| `check_memory` | walks for any `memory/` | yes |

So a full synthetic company under `demo/` — its ontologies, skills, Owner's Cards, constitution rules, proposals — would be scanned by **none** of the structural checks, and the gate would stay green throughout. Only its memory records would be governed. That is the corpus-void trap at phase scale: authoring the demo would look like proof that the schema works, and prove nothing. Hence this slice, before any demo content exists.

**2. Cross-references become instance-relative — a load-bearing shape decision.**
Today a skill's `ontology:`/`baseline:`, a proposal's `target:`, and a changelog's skill path all resolve against the validated root. For an instance under `demo/`, they must resolve against `demo/` instead.

*Why instance-relative is right:* under #10, an adopter's company OS **is** the root of its own repo, so its skills say `ontology: ontologies/customer-success/renewal-prep.md`. If `demo/` is to be a faithful model of that — and it must be, since the generator writes `your-company/` in the demo-proven shape — the demo's files have to carry exactly the same paths. Root-relative refs would make the demo a shape no real company repo ever has.

*What it also buys:* a demo skill can no longer reference an engine exemplar by climbing out (`../../ontologies/...`), because resolution is contained to its own instance. The demo has to be a complete company, not a folder borrowing the engine's homework.

*The cost, stated:* this is a silent semantic change for any file that ever *did* rely on root-relative resolution from a nested location. Nothing in the repo does today (root is the only instance), so nothing breaks — but it is a contract change, and it is why the plan pins the engine-repo output as an invariant rather than trusting the test suite alone.

**3. This closes a Slice 1.5d-ii deferral.**
That review recorded: *"`check_proposals`/`check_changelog` scan only `<validated root>/proposals` and `governance/changelog.md`, so a proposal or ledger inside a nested pinned root is schema-checked only if validate runs from that root… Fix direction if wanted: make the static checks per-governed-root."* Task 3 is that fix, generalized from "per-governed-root" to "per-instance" so it does not depend on a pin existing.

**4. `check_hooks` is deliberately NOT made instance-aware.**
The action-class gate is one shipped artifact with one registration, not per-instance content — the demo demonstrates it by reference rather than shipping a second copy. Making it per-instance would invite a `demo/governance/hooks/` whose registration claim nothing can satisfy. Excluded, and recorded here so the omission reads as a decision rather than an oversight.

---

## File Structure

- `scripts/validate.py` — **modify.** Add `CONTENT_DIRS` and `_instance_roots`; convert five checks to per-instance loops; move reference resolution to the instance base.
- `tests/test_validate.py` — **modify.** `TestInstanceRoots` plus per-check nested-instance tests.
- `docs/known-limitations.md` — **modify.** What "instance" means and what is still root-only.
- `AGENTS.md` — **modify.** One line in "Conventions that bind".

---

## Task 1: The `_instance_roots` primitive

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:** Produces `_instance_roots(root, ignore=()) -> list[str]` (absolute paths, root first, deterministic order).

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestInstanceRoots(unittest.TestCase):
    def _rel(self, d, roots):
        return sorted(os.path.relpath(r, d) for r in roots)

    def test_root_with_content_is_an_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d)), ["."])

    def test_nested_instance_is_discovered(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "demo/ontologies/sales/_executive-view.md", EXEC_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d)), [".", "demo"])

    def test_instance_without_root_content(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/x/SKILL.md", SKILL_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d)), ["demo"])

    def test_every_content_dir_marks_an_instance(self):
        for cd, rel in (("ontologies", "ontologies/f/_executive-view.md"),
                        ("skills", "skills/x/SKILL.md"),
                        ("governance", "governance/constitution/r.md"),
                        ("proposals", "proposals/p.md"),
                        ("memory", "memory/m.md")):
            with tempfile.TemporaryDirectory() as d:
                _write(d, "demo/" + rel, "# x\n")
                self.assertIn("demo", self._rel(d, validate._instance_roots(d)), cd)

    def test_no_content_means_no_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "# x\n")
            self.assertEqual(validate._instance_roots(d), [])

    def test_workbench_and_dot_dirs_are_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "tests/fixtures/ontologies/f/_executive-view.md", EXEC_OK)
            _write(d, "docs/superpowers/ontologies/f/_executive-view.md", EXEC_OK)
            _write(d, ".hidden/ontologies/f/_executive-view.md", EXEC_OK)
            self.assertEqual(validate._instance_roots(d), [])

    def test_gitignored_content_dir_does_not_mark_an_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "vendor/skills/x/SKILL.md", SKILL_OK)
            self.assertEqual(validate._instance_roots(d, ("vendor",)), [])

    def test_deeply_nested_instances(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "a/b/c/memory/m.md", "# x\n")
            self.assertEqual(self._rel(d, validate._instance_roots(d)), ["a/b/c"])

    def test_root_first_and_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/x/SKILL.md", SKILL_OK)
            _write(d, "zeta/skills/x/SKILL.md", SKILL_OK)
            _write(d, "alpha/skills/x/SKILL.md", SKILL_OK)
            self.assertEqual(self._rel(d, validate._instance_roots(d))[0], ".")
            self.assertEqual(validate._instance_roots(d), validate._instance_roots(d))
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestInstanceRoots -v`
Expected: FAIL — no attribute `_instance_roots`.

- [ ] **Step 3: Implement.** Add to `scripts/validate.py`, immediately after `iter_files`:

```python
# The directory names that mark a groundwork instance. A company OS repo carries
# these at ITS root; inside this repo, demo/ carries them too.
CONTENT_DIRS = ("ontologies", "skills", "governance", "proposals", "memory")


def _instance_roots(root, ignore=()):
    """Every directory holding groundwork content: the validated root itself, if
    it carries one of the well-known content directories, plus any directory
    beneath it that does. Absolute paths, root first, then depth-then-name order
    so output is deterministic.

    Why this exists: check_memory has always discovered `memory/` folders
    anywhere under root, but every other structural check started at
    `root/<content-dir>`. That meant a complete instance under demo/ — its
    ontologies, skills, cards, rules, and proposals — was scanned by NOTHING,
    with a green gate throughout. Reference resolution follows the instance, so
    a demo skill's `ontology:`/`baseline:` resolve inside demo/, exactly as a
    company repo's resolve inside that repo (#10)."""
    roots = []
    for dirpath, dirnames, _filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
            and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS
            and not _ignored(d, ignore))
        if any(d in CONTENT_DIRS for d in dirnames):
            roots.append(dirpath)
    return roots
```

> `os.walk` yields the root first and, with `dirnames` sorted in place, visits children in name order — so "root first, deterministic" falls out without a second sort. `followlinks` stays at its default `False`, matching every other walker; `check_symlinked_dirs` is what makes a symlinked content directory loud.

- [ ] **Step 4: Verify**

Run: `python3 -m unittest tests.test_validate.TestInstanceRoots -v`
Expected: PASS (9 tests).

Run: `python3 -c "
import sys; sys.path.insert(0,'scripts'); import validate
print([r for r in validate._instance_roots('.', validate.load_gitignore('.'))])"`
Expected: exactly one entry, the repo root — `demo/` does not exist yet.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): _instance_roots — discover groundwork content anywhere under root

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: `check_ontology` and `check_owner_cards` per instance

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
def _write_instance(d, prefix=""):
    """A complete miniature instance: one function, one provisioned skill with
    its card, and the baseline the skill cites."""
    _write(d, prefix + "ontologies/people-hr/_executive-view.md", EXEC_OK)
    _write(d, prefix + "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
    _write(d, prefix + "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
    _write(d, prefix + "skills/onboarding-orchestration/owner-card.md", CARD_OK)
    _write(d, prefix + "memory/onboarding-baseline.md", MEM_OK)
    _write(d, prefix + "memory/_index.md",
           "# Index\n\n- [b](onboarding-baseline.md)\n")


class TestNestedInstanceOntology(unittest.TestCase):
    def test_nested_ontology_is_checked(self):
        # The finding this whole slice exists for: before it, a broken demo
        # ontology produced NOTHING.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/ontologies/sales/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            findings = validate.check_ontology(d)
            self.assertTrue(any(f.level == "ERROR" and "Direction" in f.message
                                for f in findings))

    def test_finding_paths_stay_root_relative(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/ontologies/sales/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            self.assertTrue(any(f.path.startswith("demo/ontologies")
                                for f in validate.check_ontology(d)))

    def test_root_and_nested_instances_both_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            _write(d, "demo/ontologies/sales/_executive-view.md",
                   EXEC_OK.replace("| down |", "| sideways |"))
            paths = {f.path.split("/")[0] for f in validate.check_ontology(d)
                     if f.level == "ERROR"}
            self.assertEqual(paths, {"ontologies", "demo"})

    def test_clean_nested_instance_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_ontology(d)
                              if f.level == "ERROR"], [])


class TestNestedInstanceCards(unittest.TestCase):
    def test_nested_skill_package_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/x/SKILL.md", SKILL_OK)  # name mismatch: x vs the frontmatter
            findings = validate.check_owner_cards(d)
            self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_clean_nested_instance_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_ontology_ref_resolves_inside_its_own_instance(self):
        # demo/ has the ontology; root does not. Instance-relative resolution
        # must find it.
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_a_demo_skill_cannot_borrow_the_engine_ontology(self):
        # The ontology exists only at the ROOT; the demo skill must not reach it.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/skills/onboarding-orchestration/owner-card.md", CARD_OK)
            _write(d, "demo/memory/onboarding-baseline.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "ontology" in f.message.lower()
                                for f in validate.check_owner_cards(d)))

    def test_baseline_resolves_inside_its_own_instance(self):
        # The baseline exists only at the root; a demo skill citing it must fail.
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            os.remove(os.path.join(d, "demo", "memory", "onboarding-baseline.md"))
            _write(d, "memory/onboarding-baseline.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "baseline" in f.message.lower()
                                for f in validate.check_owner_cards(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestNestedInstanceOntology tests.test_validate.TestNestedInstanceCards -v`
Expected: FAIL — nested content produces no findings today.

- [ ] **Step 3: Implement.** Convert both checks to per-instance loops. The pattern for each is identical: rename the existing function to a private per-instance worker taking `(inst, root, ignore)`, change every base path from `root` to `inst`, leave every `os.path.relpath(..., root)` alone, and add a thin public wrapper.

For `check_ontology`:

```python
def check_ontology(root, ignore=()):
    """#5 structural checks, run for every instance under root (see
    _instance_roots): the engine root, demo/, your-company/."""
    findings = []
    for inst in _instance_roots(root, ignore):
        findings += _check_ontology_instance(inst, root, ignore)
    return findings


def _check_ontology_instance(inst, root, ignore=()):
    # ...the existing body, with:
    #   base = os.path.join(inst, "ontologies")
    # and every relpath(..., root) left exactly as it is
```

For `check_owner_cards`, the same wrapper, plus three base changes inside the worker:

```python
    base = os.path.join(inst, "skills")
    ontologies_root = os.path.realpath(os.path.join(inst, "ontologies"))
    # and, where the baseline is resolved:
    memory_record_realpaths = _live_record_realpaths(_memory_record_files(inst))
```

and the `baseline`/`ontology` reference resolution must resolve against `inst`, not `root` — wherever the body calls `_record_ref_realpath(root, ...)` or joins a ref onto `root`, pass `inst`.

> **Do not change any rule, severity, or message.** The only edits are the base directory and the reference base. If you find a spot where a rule cannot be expressed against `inst`, stop and report it rather than adjusting the rule.

- [ ] **Step 4: Verify — including the invariant**

Run: `python3 -m unittest tests.test_validate.TestNestedInstanceOntology tests.test_validate.TestNestedInstanceCards tests.test_validate.TestOntology tests.test_validate.TestOwnerCard tests.test_validate.TestCardDrift tests.test_validate.TestProvisioningGate -v`
Expected: PASS. The pre-existing classes are the regression proof that the bodies did not change.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: **exactly** `0 error(s), 7 warning(s)`, exit 0. Root is still the only instance, so any movement here is a regression.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): check_ontology and check_owner_cards run per instance

References resolve inside their own instance, so demo/ models a company repo
rather than borrowing the engine's ontologies.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: `check_constitution`, `check_proposals`, `check_changelog` per instance

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

> This closes the Slice 1.5d-ii deferral: *"`check_proposals`/`check_changelog` scan only `<validated root>/proposals` and `governance/changelog.md` … Fix direction if wanted: make the static checks per-governed-root."* Generalized to per-instance so it does not wait on a pin.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestNestedInstanceGovernance(unittest.TestCase):
    def test_nested_constitution_rule_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/governance/constitution/r.md",
                   RULE_OK.replace("rung: human-decision", "rung: rung-six"))
            self.assertTrue(any(f.level == "ERROR" and "demo/" in f.path
                                for f in validate.check_constitution(d)))

    def test_clean_nested_rule_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/governance/constitution/r.md", RULE_OK)
            self.assertEqual([f for f in validate.check_constitution(d)
                              if f.level == "ERROR"], [])

    def test_nested_proposal_is_schema_checked(self):
        # The 1.5d-ii deferral, closed.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/proposals/p1.md",
                   PROPOSAL_OK.replace("blast_radius: escalating",
                                       "blast_radius: trivial"))
            self.assertTrue(any(f.level == "ERROR" and "blast_radius" in f.message
                                for f in validate.check_proposals(d)))

    def test_nested_proposal_target_resolves_in_its_instance(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/memory/onboarding-baseline.md", MEM_OK)
            _write(d, "demo/proposals/p1.md", PROPOSAL_OK)
            self.assertEqual([f for f in validate.check_proposals(d)
                              if f.level == "ERROR"], [])

    def test_a_demo_proposal_cannot_target_an_engine_skill(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "skills/onboarding-orchestration/SKILL.md", SKILL_OK)
            _write(d, "demo/proposals/p1.md", PROPOSAL_OK)
            self.assertTrue(any(f.level == "ERROR" and "target" in f.message
                                for f in validate.check_proposals(d)))

    def test_nested_changelog_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/governance/changelog.md",
                   "# Governance changelog\n\n## Entries\n\n- oops not an entry\n")
            self.assertTrue(any(f.level == "WARN" and "demo/" in f.path
                                for f in validate.check_changelog(d)))

    def test_both_instances_checked_independently(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md",
                   "# c\n\n## Entries\n\n- bad root entry\n")
            _write(d, "demo/governance/changelog.md",
                   "# c\n\n## Entries\n\n- bad demo entry\n")
            tops = {f.path.split("/")[0] for f in validate.check_changelog(d)}
            self.assertEqual(tops, {"governance", "demo"})
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestNestedInstanceGovernance -v`
Expected: FAIL — nested governance produces no findings today.

- [ ] **Step 3: Implement.** Same wrapper pattern for all three:

```python
def check_constitution(root, ignore=()):
    findings = []
    for inst in _instance_roots(root, ignore):
        findings += _check_constitution_instance(inst, root, ignore)
    return findings
```

with `base = os.path.join(inst, "governance", "constitution")` inside the worker.

```python
def check_proposals(root, ignore=()):
    findings = []
    for inst in _instance_roots(root, ignore):
        findings += _check_proposals_instance(inst, root, ignore)
    return findings
```

with `base = os.path.join(inst, "proposals")`, and — importantly — **every target resolution against `inst`**: the `os.path.isfile(os.path.join(root, t))` existence check, the `os.path.realpath(os.path.join(root, t))` classification, the `os.path.realpath(root)` containment base, and the evidence-link existence check all take `inst`. Keep the `bucket` prefixes (`skills/`, `governance/constitution/`) exactly as they are — they are instance-relative by construction now.

```python
def check_changelog(root, ignore=()):
    findings = []
    for inst in _instance_roots(root, ignore):
        findings += _check_changelog_instance(inst, root, ignore)
    return findings
```

with `path = os.path.join(inst, "governance", "changelog.md")` and the skill-path resolution/realpath containment against `inst`.

> **The realpath containment checks are the security-relevant part of `check_proposals`.** Changing their base from `root` to `inst` *tightens* them (a demo proposal can no longer resolve to an engine skill). Make sure the containment comparison uses `os.path.realpath(inst)` on both sides — a half-converted check that resolves the target against `inst` but contains against `root` would be a fail-open.

- [ ] **Step 4: Verify**

Run: `python3 -m unittest tests.test_validate.TestNestedInstanceGovernance tests.test_validate.TestConstitution tests.test_validate.TestConstitutionProvenance tests.test_validate.TestProposals tests.test_validate.TestChangelog -v`
Expected: PASS — the pre-existing classes prove the bodies are unchanged.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): constitution, proposals, and changelog run per instance

Closes the Slice 1.5d-ii deferral: a proposal or ledger in a nested instance was
schema-checked only when validate ran from that directory.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Documentation and the full gate

**Files:** Modify `docs/known-limitations.md`, `AGENTS.md`

- [ ] **Step 1: Append to `docs/known-limitations.md`** (a new section at the end):

```markdown
## What the validator treats as an "instance"

- **An instance is any directory carrying `ontologies/`, `skills/`, `governance/`,
  `proposals/`, or `memory/`.** The validated root is one if it has them; so is
  `demo/`, and so is a `your-company/` checkout. Structural checks run once per
  instance, and findings are still reported relative to the validated root.
- **References resolve inside their own instance.** A skill's `ontology:` and
  `baseline:`, a proposal's `target:`, and a changelog's skill path are all relative to
  the instance that contains them — matching a company repo, where those paths are
  relative to the repo root (#10). A nested instance therefore cannot reference the
  engine's exemplars by climbing out of itself.
- **Discovery is by directory name, not by a marker file.** A directory that happens to
  be called `skills/` for unrelated reasons will be treated as an instance's skill
  directory. Renaming it, or adding it to `.gitignore`, is the way out; there is no
  opt-out frontmatter, because a marker would re-assert rather than verify (#16's
  reasoning applied to layout).
- **`check_hooks` stays root-only.** The action-class gate is one shipped artifact with
  one registration, not per-instance content. A nested `governance/hooks/` is not
  scanned, and a demo demonstrates the gate by reference rather than by shipping a
  second copy whose registration nothing could satisfy.
- **The always-loaded budget and the root-file drift check stay root-only** — both
  describe one repository's session surface, not per-instance content.
```

- [ ] **Step 2: Add one line to `AGENTS.md`,** in "Conventions that bind", after the "Files, not engines" bullet:

```markdown
- **Content is checked wherever it lives.** Any directory carrying `ontologies/`,
  `skills/`, `governance/`, `proposals/`, or `memory/` is validated as its own
  instance, with references resolving inside it. That is what lets `demo/` be a
  faithful model of a company repo rather than a folder borrowing this one's examples.
```

- [ ] **Step 3: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`, roughly 565 tests.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0.

Run the end-to-end proof that the slice does what it claims — a throwaway nested instance with one broken file per check, which must produce a finding from **every** converted check:

```bash
python3 - <<'PY'
import os, sys, tempfile
sys.path.insert(0, 'scripts'); import validate
sys.path.insert(0, 'tests')
import test_validate as T
with tempfile.TemporaryDirectory() as d:
    T._write(d, "demo/ontologies/f/_executive-view.md", T.EXEC_OK.replace("| down |", "| sideways |"))
    T._write(d, "demo/skills/x/SKILL.md", T.SKILL_OK)
    T._write(d, "demo/governance/constitution/r.md", T.RULE_OK.replace("rung: human-decision", "rung: rung-six"))
    T._write(d, "demo/governance/changelog.md", "# c\n\n## Entries\n\n- bad entry\n")
    T._write(d, "demo/proposals/p.md", T.PROPOSAL_OK.replace("blast_radius: escalating", "blast_radius: trivial"))
    for name in ("check_ontology", "check_owner_cards", "check_constitution",
                 "check_proposals", "check_changelog"):
        f = getattr(validate, name)(d)
        print("%-22s %d finding(s)" % (name, len(f)), "<-- SILENT" if not f else "")
PY
```

Expected: all five report at least one finding. Any `<-- SILENT` line means that check was not actually converted, which is the exact failure this slice exists to prevent.

- [ ] **Step 4: Commit**

```bash
git add docs/known-limitations.md AGENTS.md
git commit -m "docs: what the validator treats as an instance, and what stays root-only

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No demo content.** `demo/` does not exist after this slice; the work is fixture-proven, as #21's pin and #17's proposal schema were. Slice **2.3b** creates the demo canon, `check_synthetic_identifiers` (#16, demo-scoped ERROR), and the demo skeleton.
- **No `check_hooks` change** (Design call 4), and no change to `check_always_loaded_budget` or `check_root_files` — all three describe one repository, not per-instance content.
- **No rule, severity, or message changes.** This is a refactor; the pre-existing test classes are the proof.
- **No pin.** `demo/groundwork.pin` lands in 2.3e, after the demo's content is stable, so the #18 tripwire activates on a settled instance rather than demanding a proposal per authored file.
- **Still open for the maintainer:** three of the four Slice 1.5d-ii deferrals (dot-directory classification, case-variant authorization, the path-style nit — the fourth is closed by Task 3), the `SKIP_RELPATHS` gate-scoping sign-off, and the standing re-review rule.

## Self-Review

- **The finding is measured, not inferred.** The root-only scoping of all five checks was verified by reading the base-path lines in merged `main` (`check_owner_cards` 751/1244, `check_ontology` 1154, `check_constitution` 1714, `check_proposals` 2130), and `check_memory`'s walking discovery was confirmed as the existing precedent.
- **Ticket coverage:** #10 two-repo semantics (a company OS is the root of its own repo, so refs are repo-relative) → instance-relative resolution; #5/#6/#7/#8/#17/#18 checks → unchanged in behavior, extended in reach; the Slice 1.5d-ii nested-root deferral → closed by Task 3.
- **Placeholder scan:** no TBD/TODO; every code change is described precisely against the existing function bodies, with verification commands and expected output.
- **Type consistency:** `_instance_roots(root, ignore=()) -> list[str]` (absolute paths). Every converted check keeps its public signature `(root, ignore=())` and its `list[Finding]` return, so `validate()` is untouched. No new imports.
- **Pre-empts the recurring Codex findings.** (a) *Fail-open through a half-conversion* — the Task 4 probe asserts that **every** converted check fires on a nested instance, so a check left root-only shows as `SILENT` rather than as an absent finding; this is the corpus-void trap and it is the single most likely way this slice ships broken. (b) *Alias laundering* — `check_proposals`' realpath containment moves to `inst` on **both** sides, and Task 3 Step 3 calls out that resolving against `inst` while containing against `root` would be a fail-open. (c) *Silent behavior change* — the engine repo's output is pinned as an invariant (`0 error(s), 7 warning(s)`) at three separate verification points, so a rule that shifted during the refactor is caught immediately. (d) *Skip parity* — `_instance_roots` reuses the walker's exact skip set (`SKIP_DIRS`, dot-directories, `SKIP_RELPATHS`, `.gitignore`), with tests for each.
- **The load-bearing shape decision is surfaced:** instance-relative reference resolution is a contract change, stated with what it buys (the demo becomes a faithful company-repo model) and what it costs (a nested file can no longer reach out to the engine's exemplars) rather than slipped in as part of a refactor.
