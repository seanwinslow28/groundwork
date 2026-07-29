# groundwork V1 — Slice 4.1: `delivery/` — the provisioning guide — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open Phase 4 by closing the gap between "the generator wrote a company OS" and "an agent actually loads it." `delivery/README.md` documents the three provisioning surfaces — the repo-local symlink layer that makes generated skills visible to all four harnesses, the organization plugin upload (the spec's "org-skills zip", corrected below), and the GitHub-synced org marketplace — plus installing the runnable action-class gate that Slice 3.3 deliberately did not copy. `check_company_root` gains one WARN so a company repo whose skills no harness can see says so.

**Architecture:** One new document, one added finding in an existing check, and honesty updates. Every external fact in the guide was fetched live on 2026-07-29 and several of them correct the design brief.

**Tech Stack:** Markdown, one stdlib finding, stdlib `unittest`.

## Global Constraints

- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, and `--diff main` must exit 0. The engine root carries no `groundwork.pin`, so the new finding cannot fire on it — **if the WARN count moves, the trigger is wrong.**
- **Test count moves up only,** from **676**.
- **No `.claude-plugin/` directory and no `marketplace.json` file anywhere in this repo.** See design call 5 — every manifest in the guide is a fenced example. This is not a style preference; a real marketplace manifest here would make *this* repo a marketplace to anyone whose Claude Code found it, and `iter_files` skips dot-directories so the validator could not see it.
- **`demo/` is a governed root.** Do not touch `demo/skills/**`, `demo/governance/constitution/**`, or `demo/interview/NN-*.md`. `demo/README.md` **is** editable — `_governed_class("README.md")` returns `None`, so it is not a governed class and needs no proposal. Task 4 fixes one stale line in it.
- **Every external claim carries its verification date.** The harness surfaces in this guide move; three of them have already changed during this build. A fact without a date is a fact nobody can re-check.
- **Zero dependencies.** Stdlib only in shipped scripts.
- **Keep path components short** (`check_entropy` WARNs on 40+ char runs at ≥ 4.0 bits) and keep `AGENTS.md` under 200 lines — it is at **152**.
- **Pronouns:** they/them or the person's name.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 3.3 merged and pushed (`8c41721`), Phase 3 closed. 676 tests with 1 designed skip, gate + `--diff main` exit 0, 7 WARNs, `AGENTS.md` at 152 lines. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-4.1-delivery
```

---

## Design calls flagged for the maintainer

**1. The brief's "zip → org skills" is wrong in a way that changes the artifact: the unit of provisioning is a PLUGIN, not a skill.**
Fetched live 2026-07-29 — the Claude Code plugin-marketplace reference and the organization-plugins admin article. What is actually true:

- Skills reach an organization **inside a plugin**. A plugin's skills load from `skills/<name>/SKILL.md` under the plugin root; there is no skill-level org upload surface.
- The manual upload path is real, and it is a **plugin zip**: *"The file must be a valid .zip under 50 MB."* Maximum **100 plugins** per manual marketplace; uploading a plugin with the same name overwrites the previous version.
- The repository path is a private GitHub repo synced as a marketplace, maximum **500 plugins**, with optional automatic sync.
- Both are **Team and Enterprise plans only**, managed by Owners and Primary Owners, and the prerequisite is stated flatly: *"Cowork and Skills must both be enabled for your organization before you can use plugin marketplaces."*

That last line is worth pausing on: it means **#10's "the company repo doubles as the Cowork marketplace" is now first-party confirmed**, and Cowork is the gating feature rather than an alternative path. The spec's wording ("org-skills zip") survives as an intent but not as a mechanism, and the guide uses the surfaces' real names. Recorded because the brief and the spec are locked sources and this departs from both.

**2. #10's confidentiality guarantee is conditional, and the condition was never written down.**
#10 justified the company-repo-as-marketplace design on a verified fact: installs copy only manifest-listed plugin directories, *"so interview state / org memory / constitution source are never distributed to employees."* The copy semantics still hold — *"Claude Code copies the plugin directory to a cache location. This means plugins can't reference files outside their directory."*

But the guarantee depends on something #10 never stated: **the plugin `source` must be a subdirectory.** A `marketplace.json` entry with `"source": "."` makes the manifest-listed directory the whole repository, and then the confidential layer — `interview/` with the company's own transcript, `memory/` with its baselines, `governance/constitution/` — is packaged and shipped to every employee's machine. The failure is silent, it is a privacy breach rather than a broken build, and the natural first attempt (point the marketplace at the repo you already have) is exactly the wrong one. So the guide states it as a hard rule with the reason attached, and it is the first thing in the org-distribution section rather than a footnote.

**3. A generated company repo's skills load in NO harness until provisioning runs — which makes this the worst silent first-run failure available.**
Slice 3.3's manifest writes work packages to `skills/<name>/`. Verified against the live discovery table: Claude Code reads `.claude/skills/<name>/SKILL.md` (personal, project, plugin, or managed) and **`.agents/skills/` does not appear in it at all**, which matches #19's empirical A/B from 2026-07-18. Codex, Cursor, and Gemini CLI read `.agents/skills/`. **Nobody reads plain `skills/`.**

So an adopter can run the interview, generate a validating company OS, open their agent, and have nothing happen — and conclude that groundwork does not work. The guide's first section is the fix (a symlink layer, zero duplication, all four harnesses), and `check_company_root` gains **one** WARN — not one per skill — when a pinned root has skills under `skills/` and no harness-visible path for them. One line, because four cry-wolf lines on a demo nobody is provisioning is how a validator teaches people to ignore it.

**4. The "curated core default-on, rest available" pattern is an ADMIN setting, not something groundwork encodes.**
Brief §4 step 6 wanted "curated core default-on, rest 'available'". Confirmed live: an admin sets one of four per-plugin distribution preferences — **Installed by default**, **Available for install**, **Not available**, **Required** — with group-level overrides on Enterprise, and *"members can't edit organization-managed plugins."* There is also a `defaultEnabled` field in `marketplace.json` (v2.1.154+), but for org distribution the admin preference is what governs.

The consequence for groundwork is a scope reduction, and a welcome one: **groundwork's job is to recommend a curation, not to implement one.** The guide gives the recommendation — the track-1 skills as *Available for install*, anything track-2 as *Available* rather than default, and nothing marked *Required* until an Owner's Card has a named owner who agreed to it — and points at the admin surface for the mechanism. Nothing to build.

**5. No `marketplace.json` or `.claude-plugin/` ships in this repo. Fenced blocks only.**
Two reasons, and the second is the one that decides it. First, the 2.3d precedent: a config file that nothing validates is a named-but-unwired artifact. Second and worse: `.claude-plugin/marketplace.json` is a *live* surface — a real one committed here would make the groundwork engine itself a marketplace to anyone whose Claude Code discovered it, and because `iter_files` skips dot-directories the validator would never see it. A file that changes an external system's behaviour and is invisible to our own gate is the one kind of artifact this repo should never commit as an example.

**Named cut line.** If the slice runs long, the cut is **Task 3's added WARN**, which becomes Slice 4.1b. Tasks 1 and 4 do not split: the guide is the deliverable, and the honesty updates are what stop `AGENTS.md` describing a phase that already landed.

---

## File Structure

**Create (1 file):** `delivery/README.md`

**Modify (5 files):** `scripts/validate.py`, `tests/test_validate.py`, `AGENTS.md`, `demo/README.md`, `docs/known-limitations.md`

---

## Task 1: The provisioning guide

**Files:** Create `delivery/README.md`.

- [ ] **Step 1: Create `delivery/README.md`:**

````markdown
# Provisioning — getting the OS in front of people

The interview generates a company OS and the validator says it is well formed. Neither of
those makes an agent load it. This is the step in between.

**Read this first, because it is the failure everybody hits:** a generated company repo
keeps its work packages in `skills/<name>/`, and **no harness reads that path.** Claude
Code reads `.claude/skills/`; Codex, Cursor, and Gemini CLI read `.agents/skills/`. Until
one of the sections below has been run, an agent opened in a freshly generated company
repo will find nothing and behave exactly as if the OS were not there.

**Everything external in this document was verified on 2026-07-29**, against the Claude
Code plugin-marketplace and skills references and the organization-plugins admin article,
with the harness matrix in [`research/`](../research/) verified 2026-07-18 against Claude
Code 2.1.210, cursor-cli 2026.07.16, Codex CLI 0.144.1, and Gemini CLI 0.51.0. These
surfaces move — three of them changed during groundwork's own build — so re-check the
dates before trusting a detail, and treat a mismatch as the document being stale rather
than the harness being wrong.

---

## 1. Repo-local: make the skills loadable (no admin, all four harnesses)

This is the default, and for a single-maintainer company it may be the only section you
need. It costs one symlink pair per skill and duplicates nothing.

From the root of the company repo:

```bash
mkdir -p .agents/skills .claude/skills
for s in skills/*/; do
  name=$(basename "$s")
  ln -sfn "../../skills/$name" ".agents/skills/$name"
  ln -sfn "../../skills/$name" ".claude/skills/$name"
done
```

Commit both directories. They are part of the repo, not local scratch.

**Why both.** `.agents/skills/` is the Agent Skills standard location that Codex, Cursor,
and Gemini CLI read directly. Claude Code does **not** read it — that was tested
head-to-head, not inferred: a skill present only in `.agents/skills/` was not discovered,
and the same skill became discoverable the moment a `.claude/skills/<name>` symlink
existed. **The Claude Code symlink is load-bearing, not belt-and-braces.**

**What was verified, and what was not.** The verified form pointed
`.claude/skills/<name>` at `.agents/skills/<name>`. The commands above point both
symlinks straight at `skills/<name>`, which is the same mechanism with one less hop but
has not been separately tested. Check it rather than trusting it:

```
claude
/doctor
```

`/doctor` reports the skill listing and its context cost; your skills should be in it. If
they are not, point `.claude/skills/<name>` at `../../.agents/skills/<name>` instead —
that is the tested shape — and tell us, because this document is wrong.

**What each harness does with the parts it does not understand: nothing, silently.**
Skill-scoped `hooks`, `context: fork`, `agent:`, `allowed-tools`, `$ARGUMENTS`, and
dynamic `` !`cmd` `` injection are Claude Code extensions. Codex, Cursor, and Gemini CLI
parse a skill carrying them and list it normally, ignoring those fields with no warning,
no error, and no rejection. That is why every groundwork work package carries
**compatibility notes**: the degradation is invisible at runtime, so it has to be visible
in the file.

---

## 2. Organization plugins — manual upload

For putting skills in front of people who never touch git. **This is the V1 path.**

### The rule that comes before the steps

**A plugin is copied in isolation, so what you package is what you ship.** Package a
*subdirectory*, never the repository root. A plugin whose source is the whole company repo
distributes `interview/` — your own interview transcript — along with `memory/` and
`governance/constitution/` to every employee who installs it.

That is not a hypothetical: pointing the marketplace at the repo you already have is the
obvious first move, and it is the wrong one. The confidentiality property that makes a
private company repo safe to use as a distribution source is *"only the plugin directory
is copied"* — and it only protects you if the plugin directory is smaller than the repo.

### What to build

```
plugins/
  company-core/
    .claude-plugin/
      plugin.json
    skills/
      renewal-prep/
        SKILL.md
        owner-card.md
```

`plugin.json`:

```json
{
  "name": "acme-company-core",
  "description": "Acme's governed work packages: renewal prep and feature-request triage",
  "version": "1.0.0",
  "author": { "name": "Acme AI Ops" }
}
```

A plugin's skills load from `skills/<name>/SKILL.md` under the plugin root, so the
directory above needs the skill content inside it. Copy it in from `skills/` as a build
step — and because that is a copy, it goes stale: re-run it whenever the source skill
changes, and treat the plugin version as the thing that tells you which copy people have.

Ship the Owner's Card alongside the `SKILL.md`. It is what makes the skill accountable
rather than merely available, and it costs nothing to carry.

### Upload it

Zip the plugin directory and upload it at **Organization settings → Plugins**
(`claude.ai/admin-settings/plugins`).

- **Team or Enterprise plan only**, and only Owners and Primary Owners can manage it.
- **Cowork and Skills must both be enabled for the organization** before plugin
  marketplaces are available at all. If the Plugins page is not there, that is why.
- The file must be a valid `.zip` **under 50 MB**.
- **Maximum 100 plugins** per manually managed marketplace.
- Uploading a plugin with the same name **overwrites** the previous version — no delete
  step, and no confirmation that you meant to.

### Decide what people get

Set a distribution preference per plugin. There are four:

| Preference | What the member sees | Use it for |
|---|---|---|
| Installed by default | Already in their installed list | Nothing, on the first pass |
| Available for install | They can find and install it | Every track-1 skill |
| Not available | Hidden entirely | A skill still being reviewed |
| Required | Auto-installed, cannot be removed | A skill an owner has explicitly signed off |

**The recommended curation, and the reasoning:** start with everything **Available for
install**. Move a skill to *Installed by default* only after somebody has used it by
choice and the Owner's Card has a named owner who agreed to own it at scale. Reserve
*Required* for a skill whose absence would be a governance problem, because a member
cannot uninstall it. Nothing in groundwork should be *Required* on day one — a skill
nobody chose is a skill nobody owns.

Members cannot edit organization-managed plugins, which is the point: the version people
run is the version the maintainer landed. Enterprise plans add group-level overrides.

---

## 3. Organization plugins — GitHub sync

The same distribution surface, fed by the private company repo instead of by uploads.
**groundwork does not build this**; this section is what to do if you want it.

Add `.claude-plugin/marketplace.json` at the repo root:

```json
{
  "name": "acme-os",
  "owner": { "name": "Acme AI Ops" },
  "plugins": [
    {
      "name": "acme-company-core",
      "source": "./plugins/company-core",
      "description": "Acme's governed work packages"
    }
  ]
}
```

Then connect the repository at Organization settings → Plugins and sync it.

- The marketplace repository **must be private or internal**; org sync reads it through
  the Claude GitHub App or your organization's GitHub Enterprise App.
- **Keep the plugin folders inside the marketplace repository and reference them with a
  relative path** (`./plugins/...`). Org sync packages each plugin during distribution, so
  members never need access to a separate repo — and a private source in a *different*
  repo generally cannot be authenticated, so a relative path is the only reliable shape.
- Plugin source types `github`, `url`, and `git-subdir` are supported. `npm` is not.
- **Maximum 500 plugins**; automatic syncing can be enabled per marketplace. Otherwise
  push, then click Update.
- `source: "."` is the mistake from section 2, one layer up. Never point a plugin at the
  repository root.

**Why this is the governance gate and the delivery gate at once (#18/#10):** merging a
change into the company repo is simultaneously the maintainer's consent act and the event
that ships it. There is no second approval step to forget, and no way to distribute
something that never went through a pull request.

---

## 4. Installing the runnable action-class gate

The generator writes `governance/review-gate.md` — the action-class rule as an
instruction, which is what enforces it on every harness that ignores hooks. It does
**not** copy the runnable Claude Code gate, and that is deliberate: the two-repo model's
promise is that upstream improvements arrive by `git pull` on the engine and content is
never re-copied, and a copied enforcement script goes stale silently. A company running
last quarter's gate while believing it runs the engine's is worse off than one that knows
it has a review gate.

So installing it is a deliberate act with an obligation attached. From the engine clone:

```bash
mkdir -p ../acme-os/governance/hooks
cp governance/hooks/action_class_gate.py ../acme-os/governance/hooks/
cp governance/hooks/review-gate.md        ../acme-os/governance/hooks/
cp governance/hooks/settings.snippet.json ../acme-os/governance/hooks/
```

Merge `settings.snippet.json` into the company repo's `.claude/settings.json`, keeping any
hooks already there. Then prove it fires:

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/x"}}' \
  | python3 governance/hooks/action_class_gate.py
```

You should see `"permissionDecision": "deny"`. A benign command prints nothing.

**The obligation.** This is a copy, so it is now yours to keep current. Re-copy it after
any engine `git pull` that touches `governance/hooks/`, and if you would rather not carry
that, do not install it — the review gate in prose is an honest floor and the validator
will confirm the hook set is well formed either way (`check_hooks` runs against whichever
repo you point the validator at).

**What it is not.** A high-signal pattern floor, not a sandbox. It denies a curated set of
high-risk command shapes; a determined or unusual command can pass it. That posture is
documented rather than hedged, in [`docs/known-limitations.md`](../docs/known-limitations.md).

---

## 5. Check your work

From the engine clone, against the company repo:

```bash
python3 scripts/validate.py ../acme-os
python3 scripts/validate.py ../acme-os --diff main
```

Exit 0 on both. The second adds the stateful modes — org-memory immutability, frozen
interview layers, and the #18 consent gate.

A WARN saying the repo has skills with no harness-visible path means section 1 has not
been run yet.

---

## What this does not cover

- **Non-Claude organization distribution.** Codex, Cursor, and Gemini CLI read
  `.agents/skills/` from a repo a person has checked out. There is no admin push surface
  for them here, so for those harnesses "provisioning" means "the person has the repo".
- **Any automation of the above.** Nothing in groundwork zips, uploads, or syncs anything.
  These are steps a maintainer runs, and the honest reason to write them down rather than
  script them is that every one of these surfaces has moved at least once this year.
- **Employees editing the OS.** They do not. The git posture is one git-capable
  maintainer; everyone else receives skills and proposes changes in conversation. That is
  a deliberate constraint, not a missing feature.
````

- [ ] **Step 2: Gate**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

> Two things to watch. The guide links `../research/` and `../docs/known-limitations.md` — both must resolve. And the fenced JSON contains `claude.ai` and `example.com`-free text: `delivery/` is **not** under `demo/`, so `check_synthetic_identifiers` does not apply, but `check_entropy` and `check_secrets` do — no long tokens, no key-shaped strings.

- [ ] **Step 3: Commit**

```bash
git add delivery/README.md
git commit -m "docs(delivery): the provisioning guide — repo-local, org upload, org sync

Every external fact verified live 2026-07-29. Corrects the brief: the unit of
org provisioning is a plugin, not a skill, and #10's confidentiality guarantee
holds only when the plugin source is a subdirectory.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Prove the guide's mechanism against the live discovery table

**Files:** Modify `tests/test_validate.py`.

> The guide's section 1 claims a symlink layer makes generated skills loadable. Nothing in this repo would notice if that layer stopped resolving, and Slice 3.3's company-repo fixture is one line away from being able to check it.

- [ ] **Step 1: Extend the company-repo fixture with the provisioning layer.** In `TestGeneratedCompanyRepo`, add a method that runs the guide's symlink loop against the materialized repo and a test that asserts the result:

```python
    def _provision(self, repo):
        """Section 1 of delivery/README.md, executed. Both symlinks point straight
        at skills/<name>; the guide says so and says it is the untested hop."""
        os.makedirs(os.path.join(repo, ".agents", "skills"))
        os.makedirs(os.path.join(repo, ".claude", "skills"))
        names = sorted(n for n in os.listdir(os.path.join(repo, "skills"))
                       if os.path.isdir(os.path.join(repo, "skills", n)))
        self.assertGreater(len(names), 0, "no skills to provision — fixture is empty")
        for n in names:
            for d in (".agents", ".claude"):
                os.symlink(os.path.join("..", "..", "skills", n),
                           os.path.join(repo, d, "skills", n))
        return names

    def test_provisioned_repo_still_validates_and_links_resolve(self):
        with tempfile.TemporaryDirectory() as d:
            repo = os.path.join(d, "acme-os")
            self._materialize(repo)
            names = self._provision(repo)
            # every provisioned path must resolve to a real SKILL.md
            for n in names:
                for base in (".agents", ".claude"):
                    p = os.path.join(repo, base, "skills", n, "SKILL.md")
                    self.assertTrue(os.path.isfile(p),
                                    "%s/skills/%s does not resolve to a SKILL.md" % (base, n))
            errors = [f for f in validate.validate(repo) if f.level == "ERROR"]
            self.assertEqual([(f.path, f.message) for f in errors], [],
                             "the provisioning layer breaks the gate")
```

> The second half matters as much as the first: `check_owner_cards` ERRORs on a symlinked skill package directory, and `_instance_roots` skips dot-directories. This test proves the provisioning layer lives where those two facts make it harmless — if a future change makes the validator descend into `.claude/skills/`, this is what catches it.

- [ ] **Step 2: Prove it is load-bearing** (deliberate red, then revert)

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
# Break the symlink target name the guide's loop depends on.
t = pathlib.Path("tests/test_validate.py")
orig = t.read_text()
t.write_text(orig.replace('os.path.join("..", "..", "skills", n)',
                          'os.path.join("..", "..", "skillz", n)', 1))
r = subprocess.run([sys.executable, "-m", "unittest",
                    "tests.test_validate.TestGeneratedCompanyRepo"],
                   capture_output=True, text=True)
t.write_text(orig)
assert r.returncode != 0, "a dangling provisioning symlink passed — the test is not resolving them"
print("OK: a dangling provisioning symlink fails the build")
PY
```

- [ ] **Step 3: Gate + commit**

```bash
git add tests/test_validate.py
git commit -m "test: the provisioning symlink layer resolves and keeps the gate green

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The WARN for a company repo nothing can load

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`.

> The cut line: if the session runs long this becomes Slice **4.1b**.

- [ ] **Step 1: Tests first.**

```
pinned root, skills/ present, no .claude/skills and no .agents/skills -> exactly one WARN
pinned root, .agents/skills/<name> present                            -> silent
pinned root, .claude/skills/<name> present                            -> silent
pinned root, no skills/ at all                                        -> silent
unpinned root with skills/ (the engine case)                          -> silent
one WARN, not one per skill                                           -> assert len == 1
validate('.') unchanged                                               -> still 7 WARNs
```

- [ ] **Step 2: Extend `check_company_root`.** It already keys on a root `groundwork.pin`; add the second finding and widen the docstring:

```python
def check_company_root(root):
    """What a company repo owes, checked only when the validated root carries a
    #21 groundwork.pin — which is exactly the statement 'this is a company repo'
    (#10). Two findings, both WARN:

    1. No root AGENTS.md: an agent has no route into the OS. Everything else in
       §6's root set is already chained off AGENTS.md's presence by
       check_root_files, which is deliberately silent when it is absent — it
       checks a claim you make, not one you failed to make.
    2. Skills under skills/ with no harness-visible path: NO harness reads plain
       skills/. Claude Code reads .claude/skills/ and Codex/Cursor/Gemini read
       .agents/skills/ (verified 2026-07-18; the Claude Code symlink is
       load-bearing, not optional). A generated OS whose skills load nowhere is
       the worst silent first-run failure available — the adopter concludes
       groundwork does not work — so it gets one line pointing at delivery/.

    WARN and not ERROR because a stateless validator cannot tell a
    half-provisioned repo from a deliberately unprovisioned one, and ONE line
    rather than one per skill because four cry-wolf findings on a demo nobody is
    provisioning is how a validator teaches people to ignore it."""
    if not os.path.isfile(os.path.join(root, "groundwork.pin")):
        return []
    findings = []
    if not os.path.isfile(os.path.join(root, "AGENTS.md")):
        findings.append(Finding(
            "WARN", "AGENTS.md", None,
            "this repo carries a groundwork.pin but has no root AGENTS.md — "
            "a company OS with no root instruction file gives an agent no "
            "route into it (§6)"))

    sdir = os.path.join(root, "skills")
    if os.path.isdir(sdir) and not os.path.islink(sdir):
        try:
            packages = [n for n in sorted(os.listdir(sdir))
                        if os.path.isdir(os.path.join(sdir, n))]
        except OSError:
            packages = []
        # Opened BY PATH on purpose: iter_files skips every dot-directory, so a
        # walker-based version would measure nothing and pass (the corpus-void
        # trap D2 Move 2 hit with .claude/rules).
        visible = False
        for rel in ((".claude", "skills"), (".agents", "skills")):
            d = os.path.join(root, *rel)
            try:
                if os.path.isdir(d) and any(os.listdir(d)):
                    visible = True
            except OSError:
                pass
        if packages and not visible:
            findings.append(Finding(
                "WARN", "skills", None,
                "%d skill package(s) under skills/ and no harness-visible path — "
                "no harness reads skills/ directly (Claude Code reads "
                ".claude/skills/, Codex/Cursor/Gemini read .agents/skills/); see "
                "delivery/README.md" % len(packages)))
    return findings
```

- [ ] **Step 3: Gate.** `python3 scripts/validate.py . ; echo "exit: $?"` must still be exactly `0 error(s), 7 warning(s)` — **the engine root has no pin.** If the count moved, the check is finding `demo/groundwork.pin` instead of a *root* pin, which is the 2.3a scoping-bug class.

Then confirm the intended new behaviour:

```bash
python3 scripts/validate.py demo 2>&1 | tail -4
```
Expected: `0 error(s), 2 warning(s)` — no root AGENTS.md, and four skills nothing can load. Both are true of `demo/`, which is a worked example inside the engine and not a provisioned company repo.

- [ ] **Step 4: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): a company repo whose skills no harness can load says so

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Honesty — including one debt carried from Slice 3.3

**Files:** Modify `AGENTS.md`, `demo/README.md`, `docs/known-limitations.md`.

- [ ] **Step 1: `AGENTS.md`.** Move `delivery/` from "Not built yet" into "Built and working":

```markdown
- `delivery/` — the provisioning guide: the repo-local symlink layer that makes generated
  skills loadable in all four harnesses, the organization plugin upload and GitHub-synced
  marketplace paths, and how to install the runnable action-class gate with the re-copy
  obligation that comes with it. Every external fact carries the date it was verified.
```

Update the map table's `delivery/` row, and remove the "Not built yet" bullet for it. Then check the section's framing still reads true — after this slice, "Not built yet" holds `your-company/` semantics and README Tier 2 only.

> **`wc -l AGENTS.md` must stay under 200.** It is at 152.

- [ ] **Step 2: `demo/README.md` — the debt Slice 3.3 deferred.** Its "What this is not" section still says the interview "is Phase 3, not built yet", which stopped being true two slices ago. Replace that sentence with:

```markdown
Not a template to copy. The intended path for a real company OS is generation by the
interview into its own private repository (see [AGENTS.md](../AGENTS.md), "Two repos") —
a process you can run by hand today with an agent, following `interview/`. This directory
is a worked example to read, nothing more.
```

> `demo/README.md` is not a governed class (`_governed_class` returns `None` for a top-level `README.md`), so this needs no proposal. Confirm with `python3 scripts/validate.py . --diff main` after the edit: exit 0, no tripwire finding.

- [ ] **Step 3: `docs/known-limitations.md`.** Append to the appropriate section:

```markdown
- **Provisioning is manual, and the surfaces move.** Nothing in groundwork zips, uploads,
  or syncs anything: `delivery/README.md` is steps a maintainer runs. The reason it is
  written rather than scripted is that every surface it describes has changed at least
  once during groundwork's own build — the hook output contract, `AGENTS.override.md`
  precedence, and the org-plugin distribution model all moved. A script would encode a
  snapshot and fail silently when the snapshot expired; a dated document fails visibly.
- **A generated company repo's skills are invisible until provisioning runs.** The
  generator writes work packages to `skills/<name>/`, and no harness reads that path.
  `check_company_root` WARNs once when a pinned repo has skills and no
  `.claude/skills/` or `.agents/skills/` entry, but a WARN does not fail the gate — an
  adopter can ship an OS nothing loads.
- **Organization distribution is Team/Enterprise only, and Cowork-gated.** Plugin
  marketplaces require Cowork and Skills to be enabled for the organization, and only
  Owners and Primary Owners can manage them. There is no organization push surface for
  Codex, Cursor, or Gemini CLI at all — for those harnesses, provisioning means the
  person has the repository checked out.
- **A plugin is copied in isolation, so packaging the wrong directory is a privacy
  failure, not a build failure.** #10's guarantee that interview state and org memory are
  never distributed holds only when the plugin `source` is a subdirectory. Point it at
  the repository root and the company's own interview transcript ships to every employee
  who installs it. `delivery/README.md` states this as a hard rule; no check can enforce
  it, because the manifest lives in a dot-directory the validator never scans.
```

- [ ] **Step 4: The full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"` — green; record the count.
Run: `python3 scripts/validate.py . ; echo "exit: $?"` — exactly `0 error(s), 7 warning(s)`, exit 0.
Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"` — exit 0. `demo/README.md` is ungoverned, so the #18 tripwire must stay silent; if it fires, the classification is not what this plan assumed — stop and report.
Run: `wc -l AGENTS.md` — under 200.
Run: `python3 scripts/validate.py demo 2>&1 | tail -4` — `0 error(s), 2 warning(s)`.

Then print the provisioned-repo proof:

```bash
python3 - <<'PY'
import sys, os, tempfile
sys.path.insert(0, 'scripts'); sys.path.insert(0, 'tests')
import validate, test_validate as T
with tempfile.TemporaryDirectory() as d:
    repo = os.path.join(d, "acme-os")
    t = T.TestGeneratedCompanyRepo("test_provisioned_repo_still_validates_and_links_resolve")
    t._materialize(repo); names = t._provision(repo)
    print("provisioned skills:", names)
    for base in (".agents", ".claude"):
        print(" ", base, sorted(os.listdir(os.path.join(repo, base, "skills"))))
    f = validate.validate(repo)
    print("ERRORs:", len([x for x in f if x.level == "ERROR"]),
          " WARNs:", len([x for x in f if x.level == "WARN"]))
    for x in f: print("   ", x.level, x.path, x.message)
PY
```

Expected: both dot-directories list every skill, **0 ERRORs**, and no "no harness-visible path" WARN — because there now is one. Any remaining WARN must be explainable.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md demo/README.md docs/known-limitations.md
git commit -m "docs: delivery/ is built, and the demo stops calling the interview unbuilt

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No README changes.** Capability claims turn on in Phase **4.2** (README Tier 2),
  together with the "Not technical? Point your agent at this repo" move and the `validate`
  usage section. The README makes no provisioning claim today.
- **No `LICENSE` file, no security/privacy section, no versioned roadmap.** Slice **4.3**.
  Note the README's License section currently promises "an explicit README/NOTICE
  carve-out will ship with the generator" — the generator shipped in 3.3, so that promise
  is now due, and 4.3 owes it.
- **No automation.** Nothing zips, uploads, or syncs. Design call 1 and the known
  limitation say why.
- **No `marketplace.json` or `.claude-plugin/` committed anywhere.** Design call 5.
- **Still open for the maintainer:** the org-plugins terminology correction (design call
  1) and the confidentiality condition (design call 2) both amend locked decisions; the
  3.3 hook-set call; Codex's 3.1 finding 1; the health-metrics v2 candidate; three Slice
  1.5d-ii deferrals; the `SKIP_RELPATHS` sign-off; the standing re-review rule; the
  `Motion: assist` reading; the 2.3d carry-overs. **Also: issue #10 is covered by 3.3 + this
  slice and needs closing by hand (`gh issue close 10`).**

## Self-Review

- **Ticket coverage.** Brief §4 step 6 ("Provision: zip → org skills, or connect the repo
  as a Cowork plugin marketplace") is the whole slice, with both halves corrected against
  the live surfaces: the zip is a *plugin* zip and Cowork is the *prerequisite* rather
  than an alternative. #10's two-repo model gets its delivery half — the company repo as
  the marketplace, with the subdirectory condition its confidentiality guarantee actually
  depends on. #19's verified directory convention is section 1, with the empirical A/B
  result stated as the reason the Claude Code symlink is not optional, and #12's
  silent-degradation matrix is why compatibility notes exist. #8's hook set gets its
  install path with the re-copy obligation that Slice 3.3's design call 2 deferred here.
- **Five external contracts were fetched live on 2026-07-29, and they changed the plan.**
  The plugin-marketplace reference and the organization-plugins admin article between
  them corrected the unit of provisioning (plugin, not skill), supplied the real limits
  (50 MB, 100 manual / 500 synced, Team-Enterprise, Cowork-gated), confirmed the four
  distribution preferences that satisfy the brief's "curated core default-on" wish
  without groundwork building anything, and — most importantly — surfaced that #10's
  confidentiality guarantee is conditional on the plugin source being a subdirectory. The
  skills reference confirmed `.agents/skills/` still does not appear in Claude Code's
  discovery table, which is what keeps #19's symlink load-bearing. **Fourth time in this
  build that fetching the live contract changed the artifact.**
- **Design calls surfaced, not buried.** Five, each with its cost: the terminology
  correction that departs from two locked sources; the unwritten condition in #10; the
  silent-first-run failure that justifies a new WARN; the scope *reduction* on curation;
  and why no marketplace manifest ships here — where the second reason (a live external
  surface, invisible to `iter_files`) is the one that decides it.
- **Anti-hollow probes.** One planted violation (a dangling provisioning symlink must fail
  the build) plus an in-test guard (`assertGreater(len(names), 0)` — provisioning an empty
  skills directory would pass trivially), plus the trigger check on the 7-WARN invariant,
  plus the final report printing both dot-directories' contents and every finding. The
  provisioning test's second half is deliberately paired: it asserts the symlinks resolve
  *and* that the validator stays green, because `check_owner_cards` ERRORs on symlinked
  skill packages and this proves the layer lives where that cannot bite.
- **The trigger is checked, not assumed.** The new finding keys on `root/groundwork.pin`
  and the plan says explicitly that if `validate.py .` moves off 7 WARNs the check is
  finding `demo/groundwork.pin` instead — the 2.3a scoping-bug class, twice-burned.
- **One WARN, not one per skill.** Stated with its reason: cry-wolf findings on a demo
  nobody is provisioning are how a validator teaches people to ignore it, which
  `CONTEXT.md` already says about `your-company/`.
- **A carried debt is paid rather than re-deferred.** `demo/README.md` still called the
  interview unbuilt; Slice 3.3 could not touch `demo/`, and this slice can because a
  top-level `README.md` is not a governed class. The plan says how it verified that
  rather than assuming it.
- **Placeholder scan:** no TBD/TODO. The guide is given in full; the check and the test
  are given in full; every modification quotes its replacement text.
- **Pre-empts the recurring findings.** (a) *Corpus void* — the dot-directory check opens
  `.claude/skills` and `.agents/skills` **by path**, with the comment naming the D2 Move 2
  precedent where a walker-based version measured nothing and passed. (b) *Fail-open* — an
  unreadable `skills/` yields an empty package list and therefore no false WARN, and the
  pin check returns `[]` when absent, which is the correct silent case. (c) *Honesty* —
  four real limits are written down, including one that no check can enforce and says so.
  (d) *Dates on external facts* — the guide carries its verification date and the harness
  versions, and tells the reader to treat a mismatch as the document being stale.
- **Type consistency:** `check_company_root(root)` keeps its existing signature and stays
  wired where Slice 3.3 put it; no other function changes.
