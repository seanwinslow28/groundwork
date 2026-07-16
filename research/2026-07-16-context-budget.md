# Context-budget measurement & thresholds — research findings (2026-07-16)

> Wayfinder research ticket: [#13](https://github.com/seanwinslow28/groundwork/issues/13). Produced by an AFK research subagent; first-party sources preferred, motivating numbers traced to origin.

## Distilled answer

**Measure in bytes, report in estimated tokens, threshold on both.** Bytes are the only unit a stdlib Python validator can compute deterministically, and both vendors already govern boot surfaces in bytes/lines: Claude Code auto-memory loads "the first 200 lines or 25KB, whichever comes first" (≈125 bytes/line), and Codex hard-caps the combined AGENTS.md chain at **32 KiB** (`project_doc_max_bytes`) — silently truncating beyond it.

**Recommended thresholds for the always-loaded surface** (root instruction file + AGENTS.md/CLAUDE.md + always-on rules + the sum of all provisioned skill descriptions):

- **WARN at ~20K estimated tokens (~80 KB of text)** — grounded in a first-party anchor: Claude Code's own tool-search feature only front-loads schemas "when they fit within 10% of the context window" (10% of the 200K default = 20K). Anthropic treats 10% as the acceptable ceiling for always-on overhead.
- **ERROR at ~50K estimated tokens (~200 KB)** — the documented pathological case is 66K tokens (~33% of the window) measured via `/context`; 50K puts the error line safely below "documented disaster."
- **Per-file checks:** WARN any instruction file over **200 lines** (Claude Code first-party: "target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence"); ERROR if the AGENTS.md chain exceeds **32 KiB** (Codex silently truncates — data loss, not just bloat); WARN rules files over **500 lines** (Cursor first-party: "Keep rules under 500 lines"); WARN any skill `description` + `when_to_use` over **1,536 characters** (Claude Code truncates the listing there).
- **Skill-count check:** WARN above **~30 model-invocable skills**, ERROR/strong-warn approaching **100** (research chain verified below; small local models degrade from ~19).

**Estimation method for the validator:** `len(text) / 4` chars-per-token, stdlib-only, with a documented caveat that Claude's post-Opus-4.7 tokenizer produces ~30% more tokens (so `/3.5` is the conservative divisor for Claude-family targets). Strip HTML comments before counting (Claude Code strips them pre-injection). Precision doesn't matter at these thresholds — even Claude Code's own docs label their startup token figures "illustrative."

## Per-harness boot-context loading

**Claude Code** — Documented startup sequence ("Before you type anything: CLAUDE.md, auto memory, MCP tool names, and skill descriptions all load into context"): system prompt → auto memory (first 200 lines/25KB of MEMORY.md) → environment info → MCP tool *names* (schemas deferred by default via tool search) → **skill descriptions** ("One-line descriptions of available skills… Full skill content loads only when Claude actually uses one"; `disable-model-invocation: true` skills stay fully out of context) → user CLAUDE.md → project CLAUDE.md (loaded **in full** regardless of length, plus `@import`s, max depth 4; unscoped `.claude/rules/*.md` load at launch, path-scoped rules load on file match). **Measurement exposed:** `/context` gives a live token breakdown by category ("system prompt, tools, memory files, skills, and conversation history"); `/memory` lists which files loaded; the `InstructionsLoaded` hook logs exactly which instruction files loaded and why — a scriptable measurement surface. Claude Code also visibly warns at launch when CLAUDE.md is too large, and `/doctor` (v2.1.206+) proposes CLAUDE.md trims. (code.claude.com/docs/en/context-window, /en/memory, /en/skills)

**OpenAI Codex** — Builds an "instruction chain" once per session: `~/.codex/AGENTS(.override).md`, then AGENTS.md files walking from repo root down to cwd, concatenated root-down. "Codex skips empty files and stops adding files once the combined size reaches the limit defined by `project_doc_max_bytes` (32 KiB by default)." Source constant: `PROJECT_DOC_MAX_BYTES: usize = 32 * 1024`, with the comment "Larger files are *silently truncated* to this size so we do not take up too much of the context window." **No per-session context breakdown is exposed, and no truncation warning is shown** — openai/codex issue #7138 asked for one and was closed as not planned. For Codex the validator IS the missing warning: the byte cap is the governing rule. (developers.openai.com/codex/guides/agents-md; github.com/openai/codex/issues/7138)

**Cursor** — Rules "provide persistent, reusable context at the prompt level"; "rule contents are included at the start of the model context." Four application modes; `alwaysApply: true` rules load into every request. First-party size guidance: "Keep rules under 500 lines" and "Split large rules into multiple, composable rules." AGENTS.md is supported as a plain-markdown alternative with nested precedence. **No first-party `/context`-style token breakdown is documented** — bytes/lines of always-apply rules are the only thing a validator can check. (cursor.com/docs/rules)

**Claude Cowork / claude.ai org provisioning** — Admins upload skill zips under Organization settings; "Admin-provisioned skills are enabled by default for everyone, but members can toggle individual skills off." Plugins have graded install preferences, including org-**required** plugins that "install automatically… you can't remove them." This is the mechanism that makes org-wide boot tax structural rather than personal. **No user-facing token measurement is documented for Cowork/web** — no `/context` equivalent — so the repo-side validator is the only pre-provisioning gate. (support.claude.com articles 13119606, 13837433/13837440)

## Verifying the motivating numbers

**66K boot tax — VERIFIED number, CORRECTED scenario.** Original source: Nate B. Jones, "You're Loading 66,000 Tokens of Plugins Before You Even Type. That's Why Your Limit Disappears" (natesnewsletter.substack.com/p/your-claude-sessions-cost-10x-what, pub. 2026-04-01). Exact claim: "One of our community members ran `/context` in Claude Code last week and discovered he was loading **66,000 tokens in every single session before doing anything**… just the overhead of skills, plugins, and custom frontmatter he'd accumulated was eating over half his context window on boot. He halved it by removing 36 plugins and cleaning up skill frontmatter." **Nuance for the design brief:** this was an *individual power user who self-accumulated ~36 plugins*, measured via `/context` — not an org-wide default-on deployment. The org-wide framing is a legitimate extrapolation (Cowork admin-provisioned skills ARE default-on for everyone, per the help center), but groundwork should cite it as "documented individual case + documented org default-on mechanism," not as a documented org incident. The brief's §2 wording should be adjusted accordingly.

**30/100 skill bounds — VERIFIED as a citation chain, with caveats.** Chain: Aakash Gupta ("Research on MCP tool selection shows agents start failing at 30+ tools when descriptions overlap, and virtually guarantee wrong picks at 100+") → Speakeasy "Tool design: Less is more" ("Thirty tools is the critical threshold at which tool descriptions begin to overlap and create confusion"; "Models are virtually guaranteed to fail at tool selection tasks when choosing from over 100 tools" — DeepSeek-v3; plus Llama 3.1 8B succeeding at 19 tools and failing at 46) → Drew Breunig "How to Fix Your Context," citing two papers incl. arxiv.org/pdf/2411.15399. Caveats: benchmarks used *tools* not *skills*; numbers are model-specific (small local models fail far earlier, ~19–46); and independent corroboration exists (semantic-selection studies report sub-50% accuracy at 100+ tools; 13.62%→43.13% via retrieval filtering). Defensible for a WARN, too soft for a hard ERROR. Speakeasy's Playwright case (26→8 tools) supports the "curated core" default.

**200-line / 25KB memory discipline — VERIFIED first-party.** code.claude.com/docs/en/memory: "The first 200 lines of `MEMORY.md`, or the first 25KB, whichever comes first, are loaded at the start of every conversation." Same page: "CLAUDE.md files are loaded in full regardless of length, though shorter files produce better adherence," and "**Size**: target under 200 lines per CLAUDE.md file." Note the direction: 25KB is Anthropic's *self-imposed load cap* on their own always-loaded file — a strong precedent for byte-capping any always-loaded surface.

## Validator estimation options

| Method | Deps | Accuracy | Verdict |
|---|---|---|---|
| **chars/4 heuristic** | stdlib | ±10–20% on English prose; undercounts dense code/markdown; Claude post-Opus-4.7 tokenizer runs ~30% heavier (use /3.5 for Claude targets) | **Recommended.** Threshold decisions here are order-of-magnitude; vendor docs themselves call their numbers "illustrative" |
| **tiktoken** | pip dep + downloads BPE files at first use | Exact for OpenAI models only; wrong tokenizer for Claude (not public for Claude 3+) and Cursor's model mix | Rejected: adds a dep for false precision on 3 of 4 harnesses |
| **Anthropic `count_tokens` API** | network + API key | Exact per Claude model; free endpoint (2,000 RPM at Start tier) | Optional `--precise` flag at most; a repo validator must work offline/keyless |
| **Byte/line caps** | stdlib | Not tokens, but matches how vendors themselves regulate (25KB memory, 32 KiB Codex, 200/500-line guidance) | **Use as the primary enforced unit**; report token estimates alongside |

Practical validator spec: sum `len(file.read())` over the always-loaded set; skill contribution = `min(len(description + when_to_use), 1536)` per skill (matching Claude Code's real truncation); strip `<!-- -->` block comments (stripped before injection anyway); emit both bytes and `bytes/4` est. tokens; make the warn/error thresholds config-overridable with a `percent-of-window` alternative (window sizes differ: 200K default, 1M variants).

## Unverified / open items

- The two primary papers behind Speakeasy's 30/100 numbers are only partially identified (arxiv 2411.15399 confirmed as one; the DeepSeek-v3 paper title unconfirmed — reachable via Drew Breunig's "How to Fix Your Context" if a hard citation is wanted).
- Cursor: no first-party token-measurement surface or always-apply token budget found; the circulating "keep always-apply rules under 2,000 tokens combined" figure is community guidance, not docs.
- Cowork/claude.ai: no documented per-session context breakdown, and no documented skill-upload size limit in the provisioning article.
- Nate's article headline framing vs. body: the 66K case is one anecdote inside a broader piece; a second anecdote cites "over 50,000 tokens" for another user. Both are self-reported community measurements, not vendor telemetry.
- Claude Code's exact system-prompt + built-in tool overhead varies by version (~2.5K–4.2K prompt, ~14–17K tools per community measurements) — the validator should only budget the *repo-controlled* surface, since harness overhead is outside its control.

## Sources

All accessed 2026-07-16.

- https://code.claude.com/docs/en/context-window — /context, startup load order, skill-description loading, compaction budgets (5K/skill, 25K total), tool-search 10%-of-window rule
- https://code.claude.com/docs/en/memory — 200-line/25KB MEMORY.md cap, CLAUDE.md loaded in full, "target under 200 lines," imports, comment stripping, claudeMdExcludes
- https://code.claude.com/docs/en/skills — 1,536-char description truncation, "Keep SKILL.md under 500 lines," disable-model-invocation, invocation table
- https://developers.openai.com/codex/guides/agents-md (→ learn.chatgpt.com/docs/agent-configuration/agents-md) — project_doc_max_bytes 32 KiB, instruction chain
- https://github.com/openai/codex/issues/7138 — silent truncation, PROJECT_DOC_MAX_BYTES source constant, closed not-planned
- https://cursor.com/docs/rules — rule types, prompt-level injection, "Keep rules under 500 lines"
- https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization — admin skills enabled by default for everyone
- https://support.claude.com/en/articles/13837433 + 13837440 — Cowork plugin install preferences, required plugins
- https://natesnewsletter.substack.com/p/your-claude-sessions-cost-10x-what — 66K boot-tax case
- https://www.news.aakashg.com/p/master-ai-agent-distribution-channel — 30/100 claim + GitHub 2,500-AGENTS.md analysis
- https://www.speakeasy.com/mcp/tool-design/less-is-more — 19/30/46/100 thresholds, Playwright 26→8, cites Drew Breunig + arxiv.org/pdf/2411.15399
- https://platform.claude.com/docs/en/build-with-claude/token-counting — free count_tokens endpoint, post-Opus-4.7 tokenizer ~30% heavier

**Design-brief correction to carry forward:** §2's "documented case: 66K tokens loaded before typing" should be reframed from "org-wide default-on plugins" to "individual accumulation case, measured via /context, with org-wide default-on provisioning (Cowork admin skills) as the structural amplifier" — the number is solid, the scenario attribution was not.
