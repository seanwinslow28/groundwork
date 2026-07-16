# SKILL.md portability — research findings (2026-07-16)

> Wayfinder research ticket: [#12](https://github.com/seanwinslow28/groundwork/issues/12). Produced by an AFK research subagent; first-party sources only for load-bearing claims.

## Distilled answer

The landscape flipped between late 2025 and early 2026: **Anthropic's skill format was released as the open "Agent Skills" standard (agentskills.io) and Codex, Cursor, and Gemini CLI now all load SKILL.md skills natively.** The portable core is real: a folder with `SKILL.md` (`name` + `description` frontmatter, markdown body), plus `scripts/`, `references/`, `assets/`, with description-based auto-invocation and progressive disclosure — that works in all four harnesses today.

Per-harness verdict:

- **Claude Code** — baseline; full feature set including the extensions (`context: fork`, skill-scoped `hooks`, `allowed-tools`, dynamic `` !`cmd` `` injection, `$ARGUMENTS`).
- **Codex CLI/IDE** — native skills. Repo scope is `.agents/skills/` (walked CWD → repo root), user scope `~/.codex/skills` / `~/.agents/skills`. Explicit (`/skills`, `$` mention) + implicit invocation. Only `name`/`description` frontmatter documented. Unique: `agents/openai.yaml` sidecar for invocation policy and **declared MCP dependencies**.
- **Cursor** — native skills at `.cursor/skills/` and `.agents/skills/`, and it **reads `.claude/skills/` and `.codex/skills/` directly for compatibility**. Supports `disable-model-invocation` and `paths`. Closest drop-in to Claude Code.
- **Gemini CLI** — native skills at `.gemini/skills/` / `.agents/skills/`, **enabled by default since v0.25–0.26 (Jan 2026)**. Model-driven activation only (no user `/skill-name`), with a per-activation consent prompt.

**Recommended V1 "tested-in" matrix:** all four harnesses can honestly earn tested-in status for the portable core (discovery → auto-invocation → body load → reference load → script run). Ship work packages with canonical home **`.agents/skills/<name>/`** (the only directory all four read, Claude via symlink from `.claude/skills/`), keep frontmatter to spec fields + `compatibility`, and move every Claude extension (hooks, subagents, dynamic context, allowed-tools) behind explicit per-harness compatibility notes. The known claim ("copying a SKILL.md alone fails") is **now false for the core and still true for the extensions** — see below.

## Per-harness findings

### Claude Code (baseline)

Source: https://code.claude.com/docs/en/skills (fetched 2026-07-16)

- **Locations:** `~/.claude/skills/` (personal), `.claude/skills/` (project, discovered in parents up to repo root and in nested subdirectories), plugins (`plugin:skill` namespace), enterprise managed. Symlinked skill directories are followed. `.claude/commands/*.md` merged into skills. Live change detection watches skill dirs.
- **Standard alignment:** "Claude Code skills follow the Agent Skills open standard… Claude Code extends the standard with additional features like invocation control, subagent execution, and dynamic context injection."
- **Frontmatter (all optional in Claude Code):** `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`. Note: Claude Code lets you omit `name`/`description` (defaults to directory name / first paragraph) — the open spec *requires* both, so a lazy Claude skill can fail validation elsewhere.
- **Invocation:** description-based auto-invocation + `/skill-name`; descriptions listed at ~1% of context budget, 1,536-char cap per entry.
- **Extensions that matter for portability:** skill-scoped `hooks` frontmatter; `context: fork` + `agent:` to run in a subagent; `` !`command` `` pre-render shell injection ("This is preprocessing, not something Claude executes"); `$ARGUMENTS`/`$N`/`${CLAUDE_SKILL_DIR}` substitution; `allowed-tools` pre-approval gated on workspace trust. A skill folder can also carry `.claude-plugin/plugin.json` to become a plugin bundling "agents, hooks, and MCP servers" — the only Claude path for a skill to ship MCP config.

### OpenAI Codex (CLI/IDE)

Source: https://developers.openai.com/codex/skills (canonical; currently 308-redirects to https://learn.chatgpt.com/docs/build-skills.md — fetched 2026-07-16). github.com/openai/codex/docs/skills.md is a stub pointing there.

- **Native SKILL.md support: yes.** "A skill is a directory with a SKILL.md file plus optional scripts and references"; builds on "the open agent skills standard" (links agentskills.io).
- **Locations (documented scope table):** REPO `.agents/skills/` — Codex "scans `.agents/skills` in every directory from your current working directory up to the repository root"; USER `$HOME/.agents/skills`; ADMIN `/etc/codex/skills`; SYSTEM (bundled). The same doc family also references user-installed skills at `$CODEX_HOME/skills` (default `~/.codex/skills`, with built-ins under `.system/`). Symlinked folders supported. **Codex does NOT read `.claude/skills/`.**
- **Frontmatter:** only `name` and `description` are documented. No `disable-model-invocation`, no `allowed-tools`, no `context`/`agent`/`hooks`.
- **Invocation:** explicit — `/skills` or `$` mention in CLI/IDE; implicit — "Codex can choose a skill when your task matches the skill `description`". Implicit invocation is toggled per-skill via the sidecar `agents/openai.yaml` → `policy.allow_implicit_invocation` (default `true`) — Codex's functional equivalent of `disable-model-invocation`, but in a different file.
- **Codex-specific sidecar `agents/openai.yaml`:** UI metadata (display name, icons, brand color), invocation policy, and **`dependencies.tools` declaring MCP servers** (`type`, `value`, `transport`, `url`) — skills can *declare* MCP requirements, though the MCP server itself is still configured harness-side.
- **Scripts:** `scripts/` supported; doc advises "Prefer instructions over scripts unless you need deterministic behavior or external tooling." Execution runs under Codex's sandbox/approval model (skill docs don't detail sandboxing).
- **Not present:** hooks, skill-scoped subagent execution, dynamic context injection, allowed-tools — none documented.

### Cursor

Source: https://cursor.com/docs/skills (fetched 2026-07-16; also listed on agentskills.io as a supporting client)

- **Native SKILL.md support: yes** — "Agent Skills is an open standard for extending AI agents with specialized capabilities."
- **Locations:** project `.agents/skills/` and `.cursor/skills/`; user `~/.agents/skills/` and `~/.cursor/skills/`; discovered recursively for monorepos. Critically: "For compatibility, Cursor also loads skills from Claude and Codex directories: `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, and `~/.codex/skills/`." **A Claude Code project skill is picked up by Cursor with zero moves.**
- **Frontmatter:** required `name` (must match folder), `description`; optional `paths` (glob scoping), `disable-model-invocation` ("only included when explicitly invoked via `/skill-name`"), `metadata`. No `allowed-tools`, `hooks`, `context`, `agent`, `model` documented.
- **Invocation:** auto (agent decides from description) + manual `/skill-name`.
- **Scripts:** `scripts/` = "Executable code that agents can run", any language. `references/`, `assets/` supported.
- **Adjacent systems, not skill-scoped:** Cursor has hooks (`hooks.json`, via `/create-hook`) and subagents (`/create-subagent`), but neither is wired to skill frontmatter — a Claude skill's `hooks:` or `agent:` fields have no Cursor semantics. Rules (`.cursor/rules/*.mdc`) remain a separate system; Cursor ships a `/migrate-to-skills` converter.

### Gemini CLI

Sources: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md, …/creating-skills.md, …/using-agent-skills.md (raw fetched 2026-07-16); https://geminicli.com/docs/changelogs/

- **Native SKILL.md support: yes** — "Based on the Agent Skills open standard." Timeline: introduced as "Experimental Agent Skills Support in Preview" in v0.23.0 (2026-01-07, required enabling in `/settings`); "enabled skills by default" in v0.25.0 (2026-01-20) / v0.26.0 (2026-01-27). **Stable and on by default as of July 2026.**
- **Locations (precedence low→high):** built-in → extension skills → user (`~/.gemini/skills/` or `~/.agents/skills/` alias) → workspace (`.gemini/skills/` or `.agents/skills/` alias). Within a tier, `.agents/skills/` beats `.gemini/skills/`. The alias "is compatible with other AI agent tools following the Agent Skills standard." **Gemini does NOT read `.claude/skills/`.**
- **Frontmatter:** `name` ("should match the directory name") and `description` ("**CRITICAL.** This is how Gemini decides when to use the skill"). No optional fields documented — `disable-model-invocation`, `allowed-tools`, etc. are unsupported as far as the docs go.
- **Invocation:** discovery injects name+description of all enabled skills into the system prompt; when a task matches, the model calls the `activate_skill` tool and "the agent must ask for permission to activate it" (per-activation consent). On approval, "The `SKILL.md` body and folder structure is added to the conversation history. The skill's directory is added to the agent's allowed file paths." **No `/skill-name` user invocation** — `/skills` is management only (`list`, `reload`, `enable`, `disable`, `link`, `install`, `uninstall`). User-triggered "command-style" skills need Gemini's separate custom-commands system instead.
- **Scripts:** bundled scripts execute after user approval ("Once you approve, Gemini executes the bundled script"). Validation via bundled `validate_skill.cjs` / built-in `skill-creator` meta-skill.

### The open standard itself

Source: https://agentskills.io and https://agentskills.io/specification (fetched 2026-07-16)

- Spec frontmatter: **required** `name` (1–64 chars, lowercase/digits/hyphens, must match directory) and `description` (1–1024 chars); **optional** `license`, `compatibility` (≤500 chars — "Indicates environment requirements (intended product, system packages, network access, etc.)"), `metadata` (arbitrary string map), `allowed-tools` ("Experimental. Support for this field may vary between agent implementations").
- Progressive disclosure is normative (metadata ~100 tokens at startup → body on activation → resources on demand; keep SKILL.md < 500 lines / body < 5k tokens).
- Everything else Claude does — hooks, subagents, invocation control, dynamic context, argument substitution — is **outside the spec** (vendor extension territory). Reference validator: `skills-ref validate ./my-skill`.
- Maintained as an open standard, "originally developed by Anthropic"; client showcase confirms Claude Code, OpenAI Codex, Cursor, Gemini CLI, GitHub Copilot/VS Code, Goose, OpenCode, Amp, Roo Code, Kiro, Factory, and others.

## What breaks when a skill moves

Verdict on the known claim ("copying a SKILL.md alone fails across harnesses — loading rules differ, hooks become prose, subagents don't exist, MCP configs vanish"): **outdated in its headline, correct in its parts list.** As of July 2026 a *spec-clean* SKILL.md ports to all four harnesses. What breaks is exactly the Claude-extension surface:

| Ingredient | Claude Code | Codex | Cursor | Gemini CLI |
|---|---|---|---|---|
| `name`/`description` frontmatter | ✅ (optional!) | ✅ required | ✅ required | ✅ required |
| Description-based auto-invocation | ✅ | ✅ implicit invocation | ✅ | ✅ but per-activation **consent prompt** |
| User `/skill-name` invocation | ✅ | ✅ (`/skills`, `$` mention) | ✅ | ❌ model-driven only |
| `disable-model-invocation` | ✅ | ❌ field ignored; equivalent lives in `agents/openai.yaml` `policy.allow_implicit_invocation` | ✅ documented | ❌ not documented |
| `allowed-tools` pre-approval | ✅ | ❌ not documented | ❌ not documented | ❌ not documented (spec marks it "Experimental… may vary") |
| Skill-scoped `hooks` frontmatter | ✅ | ❌ no hooks system documented for skills | ❌ hooks exist (`hooks.json`) but not skill-scoped — must be re-implemented | ❌ none documented |
| Subagents (`context: fork`, `agent:`) | ✅ | ❌ | ❌ (subagents exist, no skill linkage) | ❌ |
| Dynamic context injection `` !`cmd` `` | ✅ (pre-render, explicitly a Claude extension) | ❌ becomes literal text in the body | ❌ same | ❌ same |
| `$ARGUMENTS` / `$N` substitution | ✅ | ❌ not documented | ❌ not documented | ❌ (no manual invocation at all) |
| MCP requirements | ❌ in SKILL.md (plugin wrapper needed) | ⚠️ **declarable** via `agents/openai.yaml` `dependencies.tools`; server config still separate | ❌ re-declare in Cursor MCP config | ❌ re-declare in Gemini settings/extensions |
| `scripts/` execution | ✅ | ✅ (sandbox/approvals apply) | ✅ | ✅ after user approval |
| `references/` progressive load | ✅ | ✅ | ✅ | ✅ (skill dir added to allowed paths) |
| Directory convention | `.claude/skills/`, `~/.claude/skills/` (symlinks followed) | `.agents/skills/` (CWD→repo root), `~/.codex/skills`, `~/.agents/skills` | `.agents/skills/`, `.cursor/skills/`, **plus `.claude/skills/` + `.codex/skills/` compat** | `.agents/skills/` or `.gemini/skills/` (+ user tiers) |

Refinements to the original claim:

1. **"Loading rules differ"** — still true but now convergent: `.agents/skills/` is read by Codex, Cursor, and Gemini; Claude Code's docs do not list it (see Unverified). Practical fix: canonical `.agents/skills/<name>/` + a `.claude/skills/<name>` symlink (Claude Code explicitly follows symlinks).
2. **"Hooks become prose"** — verified in effect: skill-frontmatter `hooks` is Claude-only; elsewhere the YAML is inert and the hook scripts are just files. In Cursor, deterministic enforcement must be rebuilt as `hooks.json`; in Codex and Gemini there is no documented equivalent, so enforcement degrades to instructions the model may or may not follow.
3. **"Subagents don't exist"** — as a *skill ingredient*, verified: `context: fork`/`agent:` is a documented Claude extension; nothing reads it elsewhere. The skill still runs, but inline — context isolation and tool restriction are silently lost (a behavior change, not an error).
4. **"MCP configs vanish"** — verified, with one twist: Codex is the only harness where a skill can *declare* its MCP dependency (`agents/openai.yaml`). Everywhere the actual server config must be provisioned per harness.
5. **New break the claim missed:** Gemini's consent-per-activation and lack of user invocation change the UX contract — an "auto-firing" skill becomes an "ask-every-time" skill, and a `/deploy`-style manual skill has no invocation path at all in Gemini.
6. **Silent-degradation hazard:** unknown frontmatter handling is undefined by the spec; Claude Code loads a skill with malformed YAML "with empty metadata." No harness documents *erroring* on Claude-extension fields — the failure mode is silence, which is why explicit compatibility notes are the right product answer.

## Recommended compatibility-notes template fields

For each groundwork work package:

```yaml
compatibility_notes:
  spec_conformance: pass | fail        # skills-ref validate output; name+description explicit (Claude leniency doesn't port)
  canonical_path: .agents/skills/<name>/
  claude_code_path: .claude/skills/<name>   # symlink to canonical
  tested_in:                            # only entries with an actual test run
    - harness: claude-code | codex-cli | cursor | gemini-cli
      version: "<exact version>"
      date: YYYY-MM-DD
      checks: [discovered, auto_invoked, body_loaded, reference_loaded, script_executed]
  invocation:
    auto: {claude: yes, codex: yes, cursor: yes, gemini: yes-with-consent}
    manual: {claude: /name, codex: "$name or /skills", cursor: /name, gemini: none — use custom command}
  degradations:                         # one entry per Claude-extension ingredient used
    - ingredient: hooks | subagent | dynamic-context | allowed-tools | arguments | model-pin
      behavior_elsewhere: "<what actually happens>"
      mitigation: "<re-implement as X / accept / do not port>"
  external_requirements:                # maps to spec `compatibility:` field in frontmatter
    mcp_servers: [...]                  # + per-harness provisioning note (Codex: agents/openai.yaml declarable)
    system_packages: [...]
    network: yes | no
```

And the V1 "tested-in" bar per harness: **Claude Code** = full feature test (baseline). **Codex** = place in `.agents/skills/`, verify implicit + `$` invocation, script run under sandbox; add `agents/openai.yaml` only if invocation policy or MCP deps needed. **Cursor** = verify pickup from `.claude/skills/` compat path *and* canonical path (watch for duplicates); `disable-model-invocation` ports. **Gemini CLI** = verify `activate_skill` consent flow and script approval; document that manual invocation doesn't exist; ship command-style workflows as Gemini custom commands instead.

## Unverified / open items

- **Whether Claude Code reads `.agents/skills/`** — not listed in code.claude.com skill locations as of 2026-07-16; the symlink recommendation assumes it does not. Re-check before locking the directory convention.
- **Cursor deduplication** when the same skill is visible via both `.claude/skills/` and `.agents/skills/` (e.g., symlink layout) — undocumented; test empirically before recommending dual paths.
- **Unknown-frontmatter handling** in Codex/Cursor/Gemini (ignore vs warn vs reject) — undocumented in all three; assume silent-ignore but verify in the test matrix.
- **Argument passing** to Codex `$` mentions and Cursor `/skill-name` — undocumented; treat `$ARGUMENTS` as Claude-only until tested.
- **Codex user-dir duality** (`~/.codex/skills` vs `~/.agents/skills`): both appear in current OpenAI doc surfaces; which is preferred/deprecated is unclear. The doc redirect to learn.chatgpt.com ("ChatGPT Learn") suggests active doc migration — re-fetch before publishing exact paths.
- **Codex/Gemini script sandboxing specifics** (network access, approval granularity) for bundled scripts — not detailed in skills docs; relevant for skills whose scripts need network.
- **AGENTS.md native reading by all three harnesses** — taken from the repo's existing convention; not re-verified first-party in this pass (out of ticket scope but adjacent).
- Third-party claims not used as evidence: Simon Willison's post, blog.fsck.com, agensi.io guides (pointers only).

## Sources

All accessed 2026-07-16:

- https://code.claude.com/docs/en/skills — Claude Code skills reference (baseline + extensions)
- https://developers.openai.com/codex/skills — Codex skills doc (canonical; 308 → https://learn.chatgpt.com/docs/build-skills.md, content fetched there)
- https://github.com/openai/codex/blob/main/docs/skills.md — stub confirming canonical location
- https://cursor.com/docs/skills — Cursor Agent Skills doc (incl. `.claude/skills/` compat loading)
- https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md — Gemini CLI skills overview (tiers, activation)
- https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/creating-skills.md — Gemini frontmatter/consent/validation
- https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/using-agent-skills.md — Gemini `/skills` management, security note
- https://geminicli.com/docs/changelogs/ — v0.23.0 (experimental, 2026-01-07), v0.25.0/v0.26.0 (enabled by default, 2026-01-20/27)
- https://agentskills.io — standard overview + client showcase
- https://agentskills.io/specification — normative frontmatter spec (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` experimental)
