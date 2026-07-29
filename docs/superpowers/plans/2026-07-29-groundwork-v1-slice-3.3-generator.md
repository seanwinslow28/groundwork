# groundwork V1 — Slice 3.3: the generator (#10) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Phase 3. The interview can be asked (3.2) and its answers captured (3.1); this slice turns those confirmed layers into a company OS. `interview/generate.md` is the generation protocol and the company-repo manifest; `check_company_root` catches a pinned repo with no way in; and the slice's spine is an **end-to-end test that builds a company repo and validates it as its own root** — the first time `validate(root)` has ever run against company-shaped content with `root` not being this engine.

**Architecture:** One new document, one small check, one end-to-end test, and honesty updates. The generator is a **protocol an agent follows**, not a script — layer files are prose, and 3.2's question → destination-field map is what makes transcription reliable. The end-to-end test materializes `demo/` plus the root-file set into a temp directory and runs the whole validator against it.

**Tech Stack:** Markdown, one stdlib check, stdlib `unittest`.

## Global Constraints

- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, and `--diff main` must exit 0. The engine root carries no `groundwork.pin`, so the new check cannot fire on it — if the WARN count moves, the check's trigger is wrong.
- **Test count moves up only,** from **665**.
- **`demo/` is a governed root with frozen interview layers.** Do not edit `demo/skills/**`, `demo/governance/constitution/**`, or `demo/interview/NN-*.md`. This slice edits **no** demo content at all; where the demo is imperfect, the fixture transforms a copy.
- **Check conventions.** `check_company_root(root)` takes the root, honors nothing else (it is root-only by definition), reads through `_load_frontmatter`/`_read_utf8`, reuses `Finding`, and is wired at the **end** of `validate()`.
- **Zero dependencies.** Stdlib only in shipped scripts; `TestZeroDep` scans them all. Tests may use `shutil`/`tempfile` — `tests/` is outside that scan.
- **Keep path components short** (`check_entropy` WARNs on 40+ char runs at ≥ 4.0 bits) and keep `AGENTS.md` under 200 lines — it is at **153**.
- **Pronouns:** they/them or the person's name.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 3.2 merged and pushed (`84264f9`). 665 tests with 1 designed skip, gate + `--diff main` exit 0, 7 WARNs, `AGENTS.md` at 153 lines. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-3.3-generator
```

---

## Design calls flagged for the maintainer

**1. The generator is a protocol an agent follows, not a script — and this is forced, not preferred.**
A `scripts/generate.py` would have to read the confirmed layers and extract `gate_output`, `forbidden_actions`, and forty other fields from **prose written by a human and an agent in conversation**. That is the wrong-kind-of-parser trap this repo diagnosed in 2.2a: a restricted grammar is right for input groundwork's own generator writes, and a parser is wrong for input it does not control. Layer files are deliberately narrative — that is what makes them readable at a checkpoint — so the thing that turns them into records has to be the same kind of reader that wrote them. 3.2's question → destination-field map is what makes that reliable rather than creative: every answer already names the field it fills, so generation is transcription plus formatting. It is also what the project has claimed all along — "point your agent at this repo" describes an agent doing the work, not a program.

**2. The generator does NOT copy the hook set into the company repo.**
This one has a real cost either way. #8 says the fixed action-class gate is "an artifact you install into a company repo," and `check_hooks` is root-only precisely so it checks *that* repo's copy. But #10's load-bearing promise is that **upstream improvements arrive by `git pull` on the engine and nothing is ever re-copied** — and a copied `action_class_gate.py` is a copy that goes stale silently, which is the named-but-unwired-guard failure one level up: a company running last quarter's gate while believing it runs the engine's.

*What ships instead:* the generator writes `governance/review-gate.md` — the #19 prose form of the same rule, which is already the documented degradation for Codex, Cursor, and Gemini. Installing the runnable Claude Code gate is a **maintainer act**, documented in `delivery/` (Slice 4.1), with the re-copy obligation stated where the copy is made. *The honest cost:* a freshly generated company OS has review-gate enforcement, not runtime enforcement, until someone installs the gate — so "machinery, not documents" is weaker on day one than the phrase suggests. I still recommend it, because the alternative buries a staleness bomb inside the two-repo model's central promise. **Your call.**

**3. `demo/` is not self-contained — four of its links escape into the engine — and the fixture turns that into a tripwire rather than editing them away.**
The spec calls the demo "the demo-proven shape the generator writes `your-company/` in." Checked, on `main` today:

| File | Link | Resolves to |
|---|---|---|
| `demo/README.md` | `../AGENTS.md` | the engine's AGENTS.md |
| `demo/canon.md` | `../docs/known-limitations.md` | the engine's docs |
| `demo/governance/README.md` | `../../governance/README.md` | the engine's compiler doc |
| `demo/skills/README.md` | `../../skills/work-package-spec.md` | the engine's work-package spec |

Lift `demo/` into a standalone repo and all four break. Each one is *pedagogically* right where it is — the demo teaches by pointing at the convention it instantiates — and *wrong* in a generated company repo, where those paths do not exist. So: **the demo keeps its teaching links** (they are correct for what the demo is), the generation protocol states that **a company repo links only inside itself**, and the end-to-end test asserts the escaping set is **exactly these four**. A fifth escape fails the build and forces a decision instead of quietly making the reference target less liftable. *The alternative* — rewriting the four links now — buys a literally-copyable demo at the cost of the four places a reader learns where a convention comes from. I recommend the tripwire.

**4. `check_company_root` is a WARN, and the real enforcement is the end-to-end test.**
Every root-only check in this repo is **silent when the thing it checks is absent**: `check_root_files` documents "Silent when there is no AGENTS.md," `check_hooks` returns nothing for an absent hook set. That is deliberate — they check a claim you make, not a claim you failed to make. The consequence, verified today: **`python3 scripts/validate.py demo` prints `0 error(s), 0 warning(s)`** even though that tree has no root instruction file, no `CLAUDE.md`, and no Cursor pointer. A generated company repo missing everything an agent needs to find its way in validates perfectly clean.

The narrow fix: when the validated root **carries a `groundwork.pin`** — which is exactly the statement "this is a company repo" — a missing root `AGENTS.md` is a **WARN**. One rule, ~15 lines, and it closes the entry point, because everything else in §6's root set is already chained off AGENTS.md's presence. WARN and not ERROR because a validator cannot tell "generated and incomplete" from "hand-built and deliberately minimal," and because inverting a documented silent-on-absence posture to an ERROR would break `validate.py demo` for everyone who tries it. It will make that command print one WARN, which is honest: the demo is an example inside the engine, not a standalone company repo. **The engine root has no pin, so the 7-WARN invariant is untouched — if it moves, the trigger is wrong.**

**5. The end-to-end test is the first time `validate(root)` runs with `root` ≠ this engine, and that is the slice's real deliverable.**
The success criterion is "the adopter's required path runs end-to-end: the interview generates a `your-company/` in the demo-proven shape; `scripts/validate.py` passes on it." Today nothing proves the second half. `demo/` is validated as a *nested instance* from the engine root, which means the four root-only checks — `check_root_files`, `check_hooks`, `check_agents_chain`, `check_always_loaded_budget` — have **never run against company-shaped content**. The test copies `demo/` to a temp directory, adds exactly the root files `generate.md` says the generator writes, neutralizes the four known escaping links, and asserts `validate.validate(<tmp>)` returns zero ERRORs. If the manifest specifies something the validator rejects, this is where it surfaces — and it surfaces in *this* repo's CI rather than in an adopter's afternoon.

**Named cut line.** If the slice runs long, the cut is **Task 3's `check_company_root`**, which becomes Slice 3.3b. The protocol (Task 1) and the end-to-end test (Task 2) do not split: a manifest nothing materializes is a promise, and that is the failure mode this whole slice exists to close.

---

## File Structure

**Create (1 file):** `interview/generate.md`

**Modify (5 files):** `scripts/validate.py`, `tests/test_validate.py`, `interview/README.md`, `AGENTS.md`, `docs/known-limitations.md`

---

## Task 1: The generation protocol and the company-repo manifest

**Files:** Create `interview/generate.md`; modify `interview/README.md`.

- [ ] **Step 1: Create `interview/generate.md`:**

````markdown
# Generating the company OS

The last act of the interview. [protocol.md](protocol.md) says how to ask,
[questions.md](questions.md) says what each answer fills, [README.md](README.md) is the
state the answers live in. This is how that state becomes an operating system.

**You are the generator.** There is no script. The confirmed layers are prose written by
a person and an agent in conversation, and the honest reader for prose is a reader — the
question skeleton already names the destination field for every answer, so this is
transcription and formatting, not interpretation. Where an answer is missing, you stop;
you do not fill it in.

## Before you write anything

Four preconditions. All four, every time.

1. **The interview is complete.** `00-manifest.md` says `status: complete` and
   `open_question: none`, and there is no `_working.md`. **If the status is
   `in-progress`, stop.** Generating from provisional facts produces records that look
   confirmed and are not, and every artifact downstream inherits that.
2. **You are in the company's private repo**, not the groundwork clone. The engine is
   pull-only and nothing organizational is ever written into it (#10).
3. **The layers are committed.** Uncommitted state means the checkpoints are not what
   the manifest says they are.
4. **You have read every confirmed layer.** All of them, before writing the first file.
   A record generated from one layer while a later layer contradicts it is the kind of
   error nobody finds until it matters.

## What you write

```
<company>-os/
  AGENTS.md                       the root instruction file — routing, not content
  CLAUDE.md                       one line: @AGENTS.md
  .cursor/rules/company.mdc       alwaysApply pointer to AGENTS.md
  groundwork.pin                  schema_version + generated_by_commit
  ontologies/
    README.md                     what the two tiers mean here
    <function>/_executive-view.md  every activity, with a Direction
    <function>/<activity>.md       a deep record per acted-on activity
  skills/
    <name>/SKILL.md               one per provisioned activity
    <name>/owner-card.md          its Owner's Card
  governance/
    constitution/<rule>.md        one file per kept rule
    changelog.md                  append-only, header only at generation
    review-gate.md                the #19 prose enforcement
  memory/
    _index.md                     live records only
    <record>.md                   the captured baselines, at minimum
  proposals/                      empty at generation; pending-only forever
  interview/                      the confirmed layers, retained
```

**A company repo links only inside itself.** Never write a link that climbs out of the
repo root — an engine path resolves on the machine that generated it and nowhere else.
Where you want to explain a convention, state it, or point at the engine by name in
prose. This is the one formatting rule that a reader will not catch for you.

## The order, and why it is this order

Generate in dependency order, and run the validator between stages rather than at the
end. A gate that goes red after four hundred lines tells you less than one that goes red
after twenty.

**1. `groundwork.pin` last — but decide it first.** Record which engine commit you
generated against (`git -C <engine clone> rev-parse --short HEAD`) and
`schema_version: 1`. Write the file at the end: once it exists the repo is a governed
root, and every skill and rule you add after that is an escalating change wanting a
proposal (#18). Generate under the pin and you will write a proposal per file.

**2. `ontologies/` first.** Every function gets an `_executive-view.md` listing every
activity with a Direction — that is the whole executive tier, and most activities never
get more. Then one deep record per acted-on activity.

The **Motion is the pivot**: `automate` and `build` carry the common core *plus*
Substrate, Shape, and all eight Describability Gate fields. `buy`, `hire`, and `wait`
carry only the common core — Motion, the five scores, work type, and the accountable
owner. **Write the `wait` records.** A recorded decision not to build something is a
decision, and an ontology holding only automation verdicts reads as an automation funnel.

All eight Gate fields must be *answered*. A truthful "none" is an answer; "N/A" is not,
and there is no waiver. If a Gate answer is missing from the layers, that activity does
not get a deep record — it gets a note in the manifest and a question for the next pass.

**3. `memory/` next, because skills depend on it.** Every baseline the interview captured
becomes a record: `provenance`, `owner`, `valid_at`, `source`. Then `_index.md`, listing
live records only. A skill cannot provision without a baseline, so these exist before the
skills that cite them.

**4. `skills/` — one work package per provisioned activity.** `SKILL.md` carries `name`,
`description`, `action_class`, `provisioned`, `baseline`, and `ontology`; `owner-card.md`
carries the spine, plus the track-2 trio when the action class is external-side-effect or
high-risk.

Two exact-match obligations that a reader will not notice and the validator will: the
card's `owner` must equal the ontology record's `accountable_owner` **character for
character**, and the card's `source_of_truth` must equal `gate_source_of_truth` the same
way. Copy them; do not retype them.

**What you must not invent.** Five fields come only from a human's answer (#6):

- `owner` and `backup_owner`
- `forbidden_actions`
- `pause_condition` and `retirement_condition`

They are marked `(human-only)` in [questions.md](questions.md). If a layer does not carry
one, **the skill does not ship** — write it `provisioned: no` and record the missing
answer. An invented owner is an accountability structure the named person will discover
when something goes wrong, and an invented forbidden action is a boundary nobody agreed
to.

**5. `governance/constitution/` — one file per kept rule.** Four owned objects (value,
rule, runtime check, human appeal, each with its owner), a rung, and a sunset date. Two
things the compiler does not negotiate: a `high-risk` rule must carry a human appeal path
with an owner — **there is no rung six** — and a repealed ritual's surviving job must be
reassigned to a named person before the repeal ships.

Then `changelog.md` with its header and no entries, and `review-gate.md` — the prose form
of the action-class rule, which is what enforces it on every harness that ignores hooks.
The runnable Claude Code gate is **not** copied here; see "What stays in the engine".

**6. The root files.** `AGENTS.md` is **routing, not content**: what this repo is, the
function map, the skill roster with owners and action classes, where memory and rules
live, and how to propose a change. Every session pays for it before anyone types
anything, so it points and does not explain — the ontology records hold the detail.
`CLAUDE.md` is exactly `@AGENTS.md` on its own first content line, because Claude Code
reads `CLAUDE.md` and not `AGENTS.md`. `.cursor/rules/company.mdc` carries
`alwaysApply: true` and references `AGENTS.md`.

**7. `interview/` stays.** The confirmed layers are the record of why this OS says what
it says, and the substrate a re-interview would merge against. Keep them.

## Then prove it

From the engine clone:

```
python3 scripts/validate.py ../<company>-os
```

Exit 0 with no ERRORs. Not "looks right" — run it. Then, once the repo has one commit:

```
python3 scripts/validate.py ../<company>-os --diff <base>
```

which adds the stateful modes: org-memory immutability, frozen interview layers, and the
#18 consent gate on every governed change.

**Say what you generated and what you could not.** A list of the activities that got deep
records, the skills that shipped `provisioned: no` and why, and every question the
interview left open. A generation report that claims completeness it does not have is the
one output worse than an incomplete repo.

## What stays in the engine

The company repo is **content plus a pin**. The validator, the schemas, and the fixed
action-class gate stay in the groundwork clone, and upstream improvements arrive by
`git pull` there — nothing is ever re-copied (#10). That promise is why the runnable hook
set is not written into the company repo: a copied enforcement script goes stale silently,
and a company running last quarter's gate while believing it runs the engine's is worse
off than one that knows it has a review gate.

Installing the runnable gate is a deliberate maintainer act with a re-copy obligation
attached — the provisioning guide covers it (`delivery/`, not built yet).
````

- [ ] **Step 2: Add the pointer to `interview/README.md`.** In the opening section that lists the three documents, add `generate.md` alongside `protocol.md` and `questions.md`, and update the "what is here today / what is not built" framing so it names generation as *documented and hand-runnable*, not as automated. Keep the wording consistent with `AGENTS.md` — one story across all three files, which was a Codex finding in 3.2.

- [ ] **Step 3: Gate**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

- [ ] **Step 4: Commit**

```bash
git add interview/generate.md interview/README.md
git commit -m "feat(interview): the generation protocol and the company-repo manifest (#10)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The end-to-end proof

**Files:** Modify `tests/test_validate.py`.

> This is the slice. Everything else supports it.

- [ ] **Step 1: Write the escape tripwire first.**

```python
class TestDemoIsLiftable(unittest.TestCase):
    """demo/ is the shape the generator writes a company repo in, so a link that
    climbs out of demo/ is a link that would not resolve in a real one.

    Four such links exist today and are correct where they are — the demo teaches
    by pointing at the convention it instantiates. This test pins the set. A
    fifth makes the reference target less liftable, and that should be a decision
    somebody makes, not a thing that happens."""

    KNOWN_ESCAPES = {
        ("demo/README.md", "../AGENTS.md"),
        ("demo/canon.md", "../docs/known-limitations.md"),
        ("demo/governance/README.md", "../../governance/README.md"),
        ("demo/skills/README.md", "../../skills/work-package-spec.md"),
    }

    _LINK = re.compile(r"\]\(([^)\s#]+)")

    @classmethod
    def escapes(cls):
        found = set()
        demo = REPO / "demo"
        for dirpath, dirnames, filenames in os.walk(demo):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                p = os.path.join(dirpath, fn)
                text = open(p, encoding="utf-8").read()
                for target in cls._LINK.findall(text):
                    if target.startswith(("http:", "https:", "mailto:")):
                        continue
                    resolved = os.path.normpath(os.path.join(dirpath, target))
                    if os.path.commonpath([resolved, str(demo)]) != str(demo):
                        found.add((os.path.relpath(p, REPO).replace(os.sep, "/"),
                                   target))
        return found

    def test_escaping_links_are_exactly_the_known_four(self):
        found = self.escapes()
        # Anti-hollow: a walker that finds nothing "passes" a subset check.
        self.assertGreater(len(found), 0, "the link scan found nothing at all")
        self.assertEqual(found, self.KNOWN_ESCAPES,
                         "demo/'s engine-pointing links changed. New ones make the "
                         "reference target less liftable; removed ones should be "
                         "dropped from KNOWN_ESCAPES.")
```

- [ ] **Step 2: Write the end-to-end test.**

```python
class TestGeneratedCompanyRepo(unittest.TestCase):
    """The adopter's required path, proven: a company repo in the shape
    interview/generate.md specifies passes the gate as its OWN root.

    Nothing else exercises validate(root) with root != this engine, so the four
    root-only checks — check_root_files, check_hooks, check_agents_chain,
    check_always_loaded_budget — have never run against company-shaped content.
    This is where a manifest that specifies something the validator rejects
    surfaces, in this repo's CI rather than in an adopter's afternoon."""

    AGENTS = """# Acme Logistics — company OS

This repository is the operating system for this company: what each function does,
which work is agent-run, who owns each agent, and the rules that bind them.

## Where things are

| What | Where |
|---|---|
| What each function does | `ontologies/` |
| The agents, and who owns each | `skills/` |
| The rules, and their appeals | `governance/constitution/` |
| What the company remembers | `memory/` |
| Proposed changes awaiting a human | `proposals/` |
| How this OS was decided | `interview/` |

## Proposing a change

An agent may propose a change to a skill or a rule by writing a file in `proposals/`.
Only the maintainer lands one.
"""

    CURSOR = """---
alwaysApply: true
---
Read AGENTS.md for how this company OS is organized.
"""

    def _materialize(self, dest):
        shutil.copytree(str(REPO / "demo"), dest)
        # The four teaching links point at engine paths that do not exist in a
        # company repo. Neutralize them to plain text — the same transform the
        # generation protocol tells a generator not to need in the first place.
        replaced = 0
        for rel, target in TestDemoIsLiftable.KNOWN_ESCAPES:
            p = os.path.join(dest, rel.split("/", 1)[1])
            text = open(p, encoding="utf-8").read()
            new = re.sub(r"\[([^\]]+)\]\(" + re.escape(target) + r"\)", r"\1", text)
            self.assertNotEqual(new, text, "no link to neutralize in %s" % rel)
            replaced += 1
            open(p, "w", encoding="utf-8").write(new)
        self.assertEqual(replaced, 4)
        with open(os.path.join(dest, "AGENTS.md"), "w", encoding="utf-8") as fh:
            fh.write(self.AGENTS)
        with open(os.path.join(dest, "CLAUDE.md"), "w", encoding="utf-8") as fh:
            fh.write("@AGENTS.md\n")
        os.makedirs(os.path.join(dest, ".cursor", "rules"))
        with open(os.path.join(dest, ".cursor", "rules", "company.mdc"),
                  "w", encoding="utf-8") as fh:
            fh.write(self.CURSOR)

    def test_company_repo_validates_as_its_own_root(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            findings = validate.validate(repo)
            errors = [f for f in findings if f.level == "ERROR"]
            self.assertEqual(
                [(f.path, f.message) for f in errors], [],
                "a company repo built to the generate.md manifest does not pass "
                "the gate as its own root")

    def test_the_root_only_checks_actually_ran(self):
        """Zero ERRORs from a check that never looked is indistinguishable from
        zero ERRORs from a clean repo. Break each root file in turn and prove
        the corresponding root-only check is live on this root."""
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            # CLAUDE.md no longer imports AGENTS.md -> check_root_files ERROR
            with open(os.path.join(repo, "CLAUDE.md"), "w", encoding="utf-8") as fh:
                fh.write("# not an import\n")
            msgs = [f.message for f in validate.validate(repo) if f.level == "ERROR"]
            self.assertTrue(any("does not import AGENTS.md" in m for m in msgs),
                            "check_root_files did not run against this root")

    def test_pin_travels_with_the_repo(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            self.assertTrue(os.path.isfile(os.path.join(repo, "groundwork.pin")))
            self.assertEqual(validate.check_version_pin(repo), [],
                             "skew 0 must be silent on a company root")
```

> Add `shutil` to the test module's imports if it is not already there.

- [ ] **Step 3: Prove the end-to-end test is load-bearing** (deliberate reds, then revert)

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
# A broken card owner inside demo/ must surface through the COMPANY-ROOT path,
# not only through the engine gate.
p = pathlib.Path("demo/skills/renewal-prep/owner-card.md")
orig = p.read_text()
p.write_text(orig.replace("owner: Marcus Bell", "owner: Nobody Atall", 1))
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestGeneratedCompanyRepo"],
                   capture_output=True, text=True)
p.write_text(orig)
assert r.returncode != 0, "the company-root test passed with broken content — it is not validating the copy"
print("OK: the end-to-end test validates real content")
PY
```

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
d = pathlib.Path("demo/README.md")
orig = d.read_text()
d.write_text(orig + "\nSee [the spec](../MIGRATIONS.md).\n")
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestDemoIsLiftable"],
                   capture_output=True, text=True)
d.write_text(orig)
assert r.returncode != 0, "a new escaping link passed — the tripwire is not scanning"
print("OK: a fifth escaping link fails the build")
PY
```

Both must print their `OK:` line. Then confirm the tree is clean again:
`python3 scripts/validate.py . ; python3 scripts/validate.py . --diff main`

- [ ] **Step 4: Gate + commit**

```bash
git add tests/test_validate.py
git commit -m "test: a company repo validates as its own root — the required path, end to end

First exercise of validate(root) with root != this engine, so the four
root-only checks finally run against company-shaped content. Pins demo/'s
four engine-pointing links so a fifth is a decision, not a drift.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: `check_company_root`

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`.

> The cut line: if the session is running long, this task becomes Slice **3.3b**. It is the least load-bearing third of the slice.

- [ ] **Step 1: Tests first.**

```
pinned root, no AGENTS.md      -> exactly one WARN, zero ERRORs
pinned root, with AGENTS.md    -> silent (check_root_files takes over)
unpinned root                  -> silent even with no AGENTS.md (the engine case)
pin is a directory / unreadable-> no crash
validate('.') unchanged        -> the engine has no root pin, so no new finding
```

- [ ] **Step 2: Implement.** Add after `check_version_pin`:

```python
def check_company_root(root):
    """A root carrying a #21 groundwork.pin IS a company repo (#10), and a
    company repo with no root instruction file gives an agent no route in.

    Everything else in §6's root set is already chained off AGENTS.md's
    presence by check_root_files, which is deliberately 'silent when there is
    no AGENTS.md' — it checks a claim you make, not one you failed to make.
    That leaves exactly one gap: absence at the entry point. WARN, not ERROR,
    because a stateless validator cannot tell a half-generated repo from a
    deliberately minimal one, and because turning a documented
    silent-on-absence posture into a gate failure would break validating the
    engine's own demo/ as a root."""
    if not os.path.isfile(os.path.join(root, "groundwork.pin")):
        return []
    if os.path.isfile(os.path.join(root, "AGENTS.md")):
        return []
    return [Finding("WARN", "AGENTS.md", None,
                    "this repo carries a groundwork.pin but has no root AGENTS.md — "
                    "a company OS with no root instruction file gives an agent no "
                    "route into it (§6)")]
```

- [ ] **Step 3: Wire it** at the end of `validate()`, after `check_interview_state`.

- [ ] **Step 4: Gate.** `python3 scripts/validate.py . ; echo "exit: $?"` must still be exactly `0 error(s), 7 warning(s)` — **the engine root has no pin.** If the WARN count moved, the trigger is wrong: the check is finding `demo/groundwork.pin` instead of a *root* pin.

Then confirm the intended new behaviour:

```bash
python3 scripts/validate.py demo 2>&1 | tail -3
```
Expected: `0 error(s), 1 warning(s)` — the demo is an example inside the engine, not a standalone company repo, and now it says so.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): a pinned root with no AGENTS.md has no way in (WARN)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Honesty and the full gate

**Files:** Modify `AGENTS.md`, `docs/known-limitations.md`.

- [ ] **Step 1: Update `AGENTS.md`.** Replace the `interview/` bullet under "Built and working":

```markdown
- `interview/` — the interview end to end, as documents: the **state format** (#9), the
  **consultant protocol** (§4), the **question skeleton** mapped onto the fields each
  answer fills, and the **generation protocol** with the company-repo manifest (#10). A
  person can run all four with an agent today and get a company repo the validator
  passes; a test builds one and proves it.
```

**Remove** the `interview/` bullet from "Not built yet" entirely, and rewrite the "The interview" section's closing paragraph:

```markdown
**It is documents, not a program.** There is no `generate.py` — the confirmed layers are
prose, and the thing that turns them into records is an agent following
`interview/generate.md`, with the question skeleton naming the destination field for
every answer. What makes that trustworthy is the gate at the end:
`python3 scripts/validate.py ../<company>-os` runs the whole schema against what was
generated, and this repo's own test suite builds a company repo and proves it passes.
```

Expand the "Two repos" section to name the pull-only promise and what stays where:

```markdown
The public groundwork clone is the **engine** — pull-only, never edited by an adopter.
A company's OS lives in a **separate private repo** carrying content plus a
`groundwork.pin`; the validator, the schemas, and the runnable action-class gate stay in
the engine clone and run *against* that repo. Upstream improvements arrive by `git pull`
on the engine — **content is never re-copied**, which is why a generated company repo
carries `governance/review-gate.md` (prose, and its own) rather than a copy of the hook
set that would go stale silently.
```

> **`wc -l AGENTS.md` must stay under 200.** It is at 153.

- [ ] **Step 2: Add to `docs/known-limitations.md`:**

```markdown
- **Nothing checks that a generation was faithful.** `validate.py <company-repo>` proves
  the generated records are *well formed* — every required field present, every reference
  resolving, every owner matching its ontology. It cannot prove they say what the
  interview confirmed. A generator that transcribes the wrong owner into a card produces
  a repo that passes cleanly. The defences are the exact-match drift checks (a card's
  owner must equal its ontology's `accountable_owner`), the five `(human-only)` fields a
  generator may not invent, and the confirmed layers staying in the repo so a person can
  read the source next to the output.
- **`demo/` is the reference shape but is not literally liftable.** Four links in
  `demo/` point at engine paths (`../AGENTS.md`, `../docs/known-limitations.md`,
  `../../governance/README.md`, `../../skills/work-package-spec.md`) and would not
  resolve in a standalone company repo. They are correct where they are — the demo
  teaches by pointing at the convention it instantiates — and a test pins the set so a
  fifth is a decision rather than drift. A generated company repo links only inside
  itself.
- **A company repo is not standalone-validatable.** By design (#10) the schemas and the
  validator live in the engine clone, so checking a company OS requires both checkouts.
  The maintainer already holds both; an adopter who has only the company repo cannot
  check it.
```

- [ ] **Step 3: The full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"` — green; record the count.
Run: `python3 scripts/validate.py . ; echo "exit: $?"` — exactly `0 error(s), 7 warning(s)`, exit 0.
Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"` — exit 0. This slice edits no `demo/` content, so the frozen-layer guard and the #18 tripwire both stay quiet; if either fires, something under `demo/` was touched.
Run: `wc -l AGENTS.md` — under 200.

Then print the end-to-end proof so it is visible rather than asserted:

```bash
python3 - <<'PY'
import sys, os, shutil, tempfile, re
sys.path.insert(0, 'scripts'); import validate
sys.path.insert(0, 'tests')
import test_validate as T
with tempfile.TemporaryDirectory() as d:
    repo = os.path.join(d, "acme-os")
    t = T.TestGeneratedCompanyRepo("test_company_repo_validates_as_its_own_root")
    t._materialize(repo)
    print("company repo root:", sorted(os.listdir(repo)))
    f = validate.validate(repo)
    print("ERRORs:", len([x for x in f if x.level == "ERROR"]),
          " WARNs:", len([x for x in f if x.level == "WARN"]))
    for x in f:
        print("   ", x.level, x.path, x.message)
PY
```

Expected: the root listing shows `AGENTS.md`, `CLAUDE.md`, `groundwork.pin`, and the six content directories; **0 ERRORs**. Any WARNs must be explainable — print them so they are.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md docs/known-limitations.md
git commit -m "docs: the interview generates a company OS a person can run today

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No `delivery/`.** Slice **4.1**: the org-skills zip provisioning guide, the manual
  install of the runnable action-class gate with its re-copy obligation, and the V2 Cowork
  path documented-not-built.
- **No README changes.** Capability claims turn on in Phase **4.2** (README Tier 2). The
  README makes no interview claim today, so nothing there is false — and a claim shipped
  one phase early is how a tiering discipline dies.
- **No `your-company/` directory.** Per #10 it is not a committed directory here at all.
- **No `generate.py`.** Design call 1; the generator is a protocol, and the reason is in
  the plan rather than left as an omission.
- **No demo edits.** The four escaping links stay; the fixture transforms a copy.
- **Still open for the maintainer:** the hook-set decision (design call 2), Codex's 3.1
  finding 1 (whether an absent `layers:` key should ERROR), the health-metrics v2
  candidate, three Slice 1.5d-ii deferrals, the `SKIP_RELPATHS` sign-off, the standing
  re-review rule, the `Motion: assist` reading, and the two 2.3d carry-overs.

## Self-Review

- **Ticket coverage.** #10 in full: two repos with the engine pull-only, the private
  company repo carrying content plus a pin, the validator running from the engine against
  it, the thin-repo rule, and the never-re-copy promise — which is what decides the hook
  set. Brief §4 step 4's manifest (folder-per-function ontology, skills as work packages
  with Owner's Cards, the compiled constitution, a root instruction file with routing
  tables, the multi-harness file set) is the generator's file list, item for item. #6's
  generator refusal is the five `(human-only)` fields with the consequence spelled out —
  the skill ships `provisioned: no` rather than the generator inventing an owner. #5's
  Motion pivot, the eight-Gate no-waiver rule, and the write-the-`wait`-records
  instruction are all in the ordering section. #8's four objects, no-rung-six, and
  orphan-prohibition are in step 5.
- **The slice was shaped by running the real thing, not by reading about it** (wwf5d
  §1.3/§5.2). `python3 scripts/validate.py demo` was executed during planning and returns
  `0 error(s), 0 warning(s)` — which surfaced that every root-only check is
  silent-on-absence, and that the cross-root path has never been exercised. A link scan
  over `demo/` surfaced the four escaping links. Neither is visible from the source
  documents; both changed the plan.
- **Design calls surfaced, not buried.** Five, each with its rejected alternative and its
  cost: the generator as protocol rather than script (with the 2.2a parser reason); the
  hook set *not* copied, with the day-one-weakness cost stated plainly; the four demo
  escapes pinned rather than edited away; `check_company_root` at WARN with the reason an
  ERROR would be wrong here; and the end-to-end test named as the slice's actual
  deliverable.
- **Anti-hollow probes.** Two planted violations, each asserting a test *fails*: broken
  demo content must break the company-root test (proving it validates the copy rather
  than an empty tree), and a fifth escaping link must break the tripwire. Plus three
  in-test guards — `assertGreater(len(found), 0)` on the link scan, `assertEqual(replaced, 4)`
  on the fixture transform, and a dedicated `test_the_root_only_checks_actually_ran` that
  breaks `CLAUDE.md` and demands the specific ERROR, because zero ERRORs from a check that
  never looked is indistinguishable from zero ERRORs from a clean repo. The final report
  prints the repo listing and every finding so the proof is visible.
- **The invariant's trigger is checked, not assumed.** The new check keys on a **root**
  pin, and the plan says explicitly that if `validate.py .` moves off 7 WARNs the check is
  finding `demo/groundwork.pin` instead — the exact scoping bug class that produced two
  rounds in 2.3a.
- **The named cut line** is Task 3, and the plan says why: a manifest nothing materializes
  is a promise, so Tasks 1 and 2 do not split.
- **Placeholder scan:** no TBD/TODO. The new document is given in full; both tests and the
  check are given in full; every modification quotes its replacement text.
- **Pre-empts the recurring findings.** (a) *Scope derivation* — `check_company_root`
  looks at `root/groundwork.pin` only, never a walk, so a nested pin cannot reshape it.
  (b) *Fail-open* — the check returns `[]` when the pin is absent, which is the correct
  silent case, and the fixture test fails closed on any ERROR from any check. (c)
  *Vacuous parse* — the link scanner and the fixture transform both assert non-zero
  counts. (d) *Honesty* — three real limits are written down: nothing checks that a
  generation was faithful, the demo is not literally liftable, and a company repo is not
  standalone-validatable. (e) *Entropy and identifiers* — the fixture lives in a temp dir
  named `acme-os`, so `check_synthetic_identifiers` correctly skips it (no `demo`
  component), which is the documented behaviour for a real company repo.
- **Type consistency:** `check_company_root(root)` matches the root-only checks'
  signature (`check_hooks`, `check_version_pin`, `check_root_files`) and is wired at the
  end of `validate()`.
