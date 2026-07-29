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
change into the company repo is the maintainer's consent act, and — with automatic
syncing enabled — also the event that ships it; without it, shipping waits on the Update
click. Either way there is no second *approval* step to forget, and no way to distribute
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
