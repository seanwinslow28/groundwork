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
- **Hooks are Claude-Code-only.** Codex, Cursor, and Gemini CLI silently ignore hook
  configuration. On those harnesses the same rule ships as a review-gate *instruction*
  (`governance/hooks/review-gate.md`) — an instruction is not enforcement. Cross-harness
  runtime-enforcement parity is a deliberate later graduation, not a V1 claim.
- **The gate is not installed in this repo.** It is an artifact shipped for company
  repos; whether groundwork governs its own maintenance agents with it is an open
  question, not an oversight.
