# Known limitations

Honest limits of the current build. This file grows as the product does (brief §7 — the finished-artifact bar). Overclaiming is trust debt; this is where the claims get their asterisks.

## Validator

- **The gate skips its own harness.** `scripts/validate.py .` does not scan `tests/` or `docs/superpowers/` — the validator's own fixtures and build specs necessarily quote example secret and broken-link patterns. A real secret committed *into those two trees* is therefore not caught by the gate; [Gitleaks](https://github.com/gitleaks/gitleaks) is the documented global backstop (#16). Everywhere else — all product content (`ontologies/`, `skills/`, `governance/`, `demo/`, `your-company/`, root files) — the secret scan runs at full strictness.
- **`.gitignore` matching is minimal.** The walker honors simple `.gitignore` entries (exact names and `*.ext` globs) so gitignored files like `.env` are not scanned. It does not implement full git ignore semantics (negation, nested ignores, path anchoring).
- **The secret floor is high-signal, not exhaustive** (#16): a curated regex set plus an entropy heuristic. Gitleaks is the real guarantee.
- **`--diff` is a gate, not a security boundary against a concurrent writer.** The memory-immutability scan rejects symlinked records and folders, but its check-then-read is not atomic: a process racing the validator could swap a path between the symlink check and the file read (TOCTOU). PR-time CI runs on a quiescent checkout; that is the supported setting.

## Governance — the action-class hook set

- **The hook's pattern set is high-signal, not exhaustive.** `governance/hooks/action_class_gate.py`
  blocks a curated list of high-risk command shapes (recursive delete, force push, hard
  reset, destructive SQL, raw disk writes, outbound write requests, mail, `terraform apply`,
  payments CLIs). It is a floor, not a sandbox — an unusual or deliberately obfuscated
  command can pass it. Treat it as one layer, not the guarantee.
- **Patterns match the raw command string, including quoted text.** A read-only command
  that merely *mentions* a risky string — `grep -R "DROP TABLE" .`, `printf 'terraform apply'` —
  may be denied. This is deliberate: a false positive fails safe (a human runs or approves
  the command), while teaching the gate to skip quoted or non-command positions would
  require a real shell parser and open genuine bypass holes (`sh -c "..."`, `env` prefixes).
  The gate errs toward deny. For the same reason, option *semantics* are not parsed:
  a dry-run `git clean -n -f` is denied like a real force-clean (the exemption was
  laundered three review rounds running and was removed — a denied dry run fails safe).
- **Hooks are Claude-Code-only.** Codex, Cursor, and Gemini CLI silently ignore hook
  configuration. On those harnesses the same rule ships as a review-gate *instruction*
  (`governance/hooks/review-gate.md`) — an instruction is not enforcement. Cross-harness
  runtime-enforcement parity is a deliberate later graduation, not a V1 claim.
- **The gate is not installed in this repo.** It is an artifact shipped for company
  repos; whether groundwork governs its own maintenance agents with it is an open
  question, not an oversight.

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

## Context budget (#13)

- **Only the repo-side instruction chain is measurable.** Codex's 32 KiB
  `project_doc_max_bytes` cap covers the *combined* chain, which begins with the user's
  own `~/.codex/AGENTS.md` (or `AGENTS.override.md`). That file is outside the repository
  and invisible to the validator, so a chain that passes here can still be truncated on a
  machine with a large global instruction file. The repo's own budget is what this gate
  governs.
- **Imports outside the repository are not counted.** `CLAUDE.md` may import
  `@~/.claude/…` or an absolute path; those load into context but cannot be measured from
  the repo, so they are skipped rather than guessed at.
- **Token counts are an estimate, not a tokenizer.** Bytes are measured; tokens are
  reported as `bytes / 4`. Real tokenization differs per model and per content; the
  thresholds are budget guidance, not an exact accounting.
- **The always-loaded set is a model of four harnesses, not a measurement of one.** It
  covers the root `AGENTS.md`, `CLAUDE.md` and its imports, unscoped `.claude/rules/`,
  always-apply `.cursor/rules/`, and skill descriptions capped at Claude Code's 1,536-char
  listing truncation. Harnesses differ in what else they preload (MCP tool names, system
  prompts); those are outside the repo and outside this check.
- **Skill bodies are deliberately excluded.** A `SKILL.md` body loads only when the skill
  is invoked, so its size is not part of the always-loaded budget. Before this slice these
  thresholds were applied per-file to every file in the repository, which produced false
  positives on files that never enter an agent's context (`scripts/validate.py` among
  them); the per-file application was retired, and with it any size ceiling on
  non-instruction files.
- **Dot-directories are not otherwise scanned.** `.claude/rules/` and `.cursor/rules/` are
  read by name for these checks, but the generic walker still skips dot-directories, so
  secret-scanning and link-checking do not cover them.
