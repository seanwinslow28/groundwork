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
  `groundwork.pin` (#21) — today the hand-authored `demo/` instance, tomorrow generated
  company content. The groundwork engine repo is pin-less by design, so its own `skills/` and
  `governance/constitution/` exemplars are not governed by it. Whether groundwork governs its own maintenance with its own consent gate is
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
- **Code-span detection is deliberately biased toward over-stripping.** `_strip_code`
  scans fences (backtick and tilde, any length ≥ 3, including fences nested under
  blockquote and list-item markers, with container context tracked across lines: blank
  lines and lazy paragraph continuation keep a list or quote open, and a dedented line
  after anything else ends it) and inline spans, but it does not
  implement backslash escapes: `` \` `` reads as opening a code span. The bias is
  chosen, not accidental — the root-file drift check is an ERROR-level guarantee where
  *under*-stripping fails open (a fenced `@AGENTS.md` would satisfy the check while
  Claude Code imported nothing), so ambiguity resolves toward stripping. The cost is a
  possible false drift ERROR next to an escaped backtick, and an undercount in the
  budget aggregate — in the worst case an unclosed fence (e.g. a list-nested fence that
  never sees a closing fence line) swallows everything to end of file, hiding every
  later import from both consumers: loud for the drift check (false ERROR), silent for
  the budget (the swallowed imports' bytes go uncounted).
- **The §6 drift check accepts exactly one form: the first content line of
  `CLAUDE.md` (after optional leading YAML front matter) is the standalone
  `@AGENTS.md` at under 4 columns of indent.** Claude Code's import walker skips
  code tokens (spans, fenced and indented blocks), every HTML token (comments
  included), link-reference definitions, image and link destinations — including
  MULTILINE destinations, where a `[x]:` line above re-tokens the import line — and
  leading front matter (stripped with the consumer's own regex, whose lazy closer
  may sit mid-line, using ECMAScript whitespace semantics — a set that
  neither contains nor is contained by Python's `\s`; an unclosed block strips nothing, leaving the literal `---` as the failing
  first content line). Trusting an import found anywhere richer therefore means
  betting on Markdown token classification, where any divergence makes a
  merely-documented import count as real. With nothing above it, the accepted line
  is a paragraph (or a heading if underlined) and both are import-scanned under
  every reading. Anything else — an import in prose, mid-file, below a code
  example — draws a loud false ERROR telling the author to use the canonical
  one-line `CLAUDE.md`. The budget aggregate still follows the full scanner, where
  a misread shifts measurement (bytes counted, imports followed, per-file read
  findings) rather than the §6 guarantee.
- **The always-loaded aggregate models the union of harnesses, deduplicated by real
  path.** `AGENTS.md` reached both directly and through `CLAUDE.md`'s import counts once:
  no single harness loads it twice, and double-counting could push a legitimate repo past
  the ERROR threshold for budget it does not spend.

## What the validator treats as an "instance"

- **An instance is any directory carrying `ontologies/`, `skills/`, `governance/`,
  `proposals/`, or `memory/`.** The validated root is one if it has them; so is
  `demo/`, and so is a `your-company/` checkout. Structural checks run once per
  instance, and findings are still reported relative to the validated root.
- **References resolve inside their own instance.** A skill's `ontology:` and
  `baseline:`, a proposal's `target:`, a changelog's skill path, and a memory record's
  `superseded_by` are all relative to the instance that contains them — matching a
  company repo, where those paths are relative to the repo root (#10). A nested
  instance therefore cannot reference the engine's exemplars by climbing out of itself.
- **A memory record belongs to exactly one instance** — the parent of the last
  `memory` component in its path — and only that instance may cite it as a
  `baseline:` or `superseded_by` target. Slice 2.3b closed the earlier
  outer-subsumes-inner asymmetry (a root skill could cite `demo/memory/...` while
  the reverse was blocked), so containment now holds in both directions. The cost,
  accepted deliberately: there is no shared memory pool across instances, and if one
  is ever wanted it must arrive as an explicit declaration, not as a side effect of
  how a walker recurses.
- **Instance discovery shares the stateless walker's traversal semantics**, including
  its fail-open on unreadable directories: `os.walk` skips a directory it cannot list,
  so an instance beneath an unreadable ancestor is silently not discovered — exactly
  as the same tree is silently skipped by the stateless file-level scans today. The
  `--diff` working-tree scan is the exception: it converts an unlistable directory
  into an ERROR and fails closed.
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

## Demo content (#16)

- **The synthetic ceiling.** groundwork mechanically verifies that structured
  identifiers in demo content resolve to reserved-for-fiction namespaces or the
  declared demo canon, and scans all committed content for high-signal secret
  patterns. It does not — and cannot, mechanically — prove that no real-world entity is
  referenced in free prose. That the demo's narrative names no real company, person, or
  customer rests on the fixed fictional canon plus maintainer review, not an automated
  check. The company name was searched for prior art before it was chosen; the person
  names cannot be searched in any meaningful sense, because every name is somebody's.
- **Bare-domain detection is high-signal, not exhaustive.** A hostname written without a
  scheme is only recognized when it ends in one of a curated list of public suffixes.
  That is what stops `canon.md` and `validate.py` reading as domains, and it means a
  real domain on an unlisted suffix would pass. Emails and `http(s)://` URLs are matched
  regardless of suffix. The same curated posture applies to the canon's own entries: a
  declared domain is rejected when it is a bare TLD or one of a curated list of
  multi-label public suffixes (`co.uk` and kin), not checked against the full Public
  Suffix List — an unlisted suffix (`com.sg`, say) could still be declared, so the
  canon's `domains:` list is maintainer-reviewed like the rest of the file.
- **The check is scoped by directory name.** Anything under a directory named `demo` is
  in scope; `your-company/` never is, by design — its identifiers are real and
  legitimate (#16's scope matrix). Running the validator with a demo directory *as* the
  root finds no `demo` component and skips the check; the repo gate runs from the repo
  root, which is the supported setting. This mirrors the existing limitation for
  `validate.py <memory-dir>`.
- **A four-number dotted string is treated as an IP address.** A version string like
  `10.4.2.1` in demo prose would be flagged. Failing toward a false positive is the
  intended direction here.
- **Phone detection is NANP-shaped.** The extractor recognizes 10-digit and
  separator-written 7-digit North American forms; an international number
  (`+44 20 7123 4567`) is not extracted and therefore not checked. The same
  false-positive bias applies in the other direction: a 7-digit range written like
  `555-2026` in prose would be flagged as a phone number outside the fiction range.
- **The demo cannot cite anything real, including documentation.** `demo/canon.md`
  declares `external_domains` empty, and the identifier check applies to every file
  under `demo/` — so no file there may carry a vendor, harness, or standards URL, even a
  correct one. This is deliberate (the demo company is fiction, and engine machinery
  belongs in engine artifacts), but it means the demo models a company OS that links
  nothing outward, which a real one would not. A generated `your-company/` is not
  scoped by this check at all and links whatever it needs.
- **The demo retains its interview state; that is a disposition, not a rule.**
  `demo/interview/` keeps the confirmed layers the demo's ontology was generated from,
  because that record is the provenance a future re-interview would merge against (#9).
  A real adopter may keep or clean theirs; #10 guarantees only that interview state is
  never *distributed* to employees, which is a different question from whether it is
  retained. Nothing in the validator requires an `interview/` directory to exist.

## The interview (#9, §4)

- **The schema has no field for "what must not degrade".** The question skeleton asks the
  Goodhart question — *how could an agent hit this standard in a way you would hate?* —
  because the intent-engineering 9-section spec makes health metrics a first-class
  section. groundwork has `success_standard` (what good looks like, against a captured
  baseline) and `known_failure_modes` (what has gone wrong), but no field for the thing
  that must not get worse while the standard is met. The answer is recorded in prose on
  the Owner's Card and the ontology record instead. Adding a field is a `SCHEMA_VERSION`
  bump now that `demo/` carries a pin, so it is named here as the **first candidate for a
  v2 schema change** rather than spending the first migration on one field.
- **Nothing checks interview prose.** `check_interview_state` validates the *shape* of
  what an interview captured, not whether the interview was any good — whether the role
  was defined first, whether questions came one at a time, whether a confirmed fact was
  actually confirmed by the person named. Those are properties of a conversation, and no
  file check can see them. The two engine tests cover what can be mechanized: that the
  documented examples validate, and that the question skeleton can fill every required
  field.

## Generation (#10)

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

## Provisioning (`delivery/`)

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
