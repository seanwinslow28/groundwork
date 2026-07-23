# groundwork V1 — Slice 1.5b: The fixed Claude-Code hook set + #19 degradation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship V1's *runnable* governance floor — a fixed, hand-authored, auditable Claude-Code hook set that hard-blocks high-risk actions (spend / delete / external-send) until a human signs off, with the honest #19 degradation (a review-gate instruction) for Codex / Cursor / Gemini. Plus close the two deferred Slice-1.5a calls.

**Architecture:** The hook set is a **shipped artifact**, not engine configuration: it lives in `governance/hooks/` (auditable source of truth) and is *installed* into a company repo's `.claude/settings.json`. The hook itself is **Python 3 stdlib** (not the docs' `bash`+`jq` example — groundwork cannot assume `jq`), split the way 1.4b split its git layer: a pure `classify(command)` holding the curated pattern set (exhaustively unit-testable) behind a thin stdin/stdout `main()`. The validator gains `check_hooks` to **existence-check the enforcement claim** — a hook set whose `command` path doesn't resolve is a named-but-unwired guard, which is worse than an admitted gap.

**Tech Stack:** Python 3.9+ standard library only (`json`, `re`, `sys`); stdlib `unittest`; JSON + Markdown.

## Global Constraints

- **Zero-dep applies to every shipped executable**, not just the validator: `governance/hooks/*.py` must import stdlib only. **Extend `TestZeroDep` to cover shipped hook scripts** and add `json` to its allowlist.
- **No `jq`.** The upstream docs' example hook uses `bash` + `jq`; groundwork cannot assume `jq` is installed. Use Python 3 stdlib.
- **The live hooks contract (fetched from the official docs, 2026-07-23) — use these exact field names:**
  - Register under `hooks.PreToolUse[].matcher` (tool name) with entries `{"type": "command", "command": ..., "timeout": ...}`; `${CLAUDE_PROJECT_DIR}` resolves to the project root.
  - stdin JSON carries `hook_event_name`, `tool_name`, `tool_input` (for Bash: `tool_input.command`), `cwd`, `permission_mode`.
  - To block, print to stdout and **exit 0**:
    `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`
  - `permissionDecision` values: `"allow"` / `"deny"` / `"ask"` / `"defer"`. **Do NOT** use the legacy top-level `{"decision": "block"}` form for `PreToolUse` — that pattern is for other events.
  - Exit 0 with **no output** = no decision (normal permission flow). Exit 2 = blocking error using stderr.
- **Fail loud, never silently allow:** matched high-risk → `deny`; unmatched → exit 0 with no output (defer); **unparseable/unexpected input → `"ask"`** (escalate to the human) — never a silent allow, never a hard block on malformed input.
- **Honesty:** the pattern set is **high-signal, not exhaustive** (same posture as the #16 secrets floor). It must be documented as such in `docs/known-limitations.md`. Do not claim complete enforcement.
- **#19 degradation:** hooks are a Claude-Code-only surface, **silently ignored** by Codex / Cursor / Gemini. The same rule must ship as a review-gate instruction for those harnesses.
- **Do NOT install the hook set into this engine repo.** Adding a tracked `.claude/settings.json` here would silently govern groundwork's own build sessions. Whether groundwork dogfoods its own machinery is explicitly-retained fog on the map — out of scope.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** the builder's honest identity (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).

## Prerequisite

Slice 1.5a merged to `main` (done: `2226d94`). Branch: `git checkout main && git pull && git checkout -b build/slice-1.5b-hook-set`.

---

## File Structure

- `scripts/validate.py` — **modify.** Add the active-rule provenance WARN to `check_constitution`; add `check_hooks(root)`; wire into `validate()`.
- `tests/test_validate.py` — **modify.** Provenance-WARN tests, hook `classify` tests, `check_hooks` tests, extended `TestZeroDep`.
- `governance/README.md` — **modify.** Document where worksheets live (they are not rules).
- `governance/worksheets/five-question-worksheet.md` — **create.** The blank compiler input, explicitly outside `governance/constitution/`.
- `governance/hooks/README.md` — **create.** What it enforces, how to install, the #19 degradation, the honest limits.
- `governance/hooks/action_class_gate.py` — **create.** The hook: pure `classify()` + stdin/stdout `main()`.
- `governance/hooks/settings.snippet.json` — **create.** The Claude Code registration snippet.
- `governance/hooks/review-gate.md` — **create.** The prose review gate for non-Claude harnesses.
- `docs/known-limitations.md` — **modify.** The hook set's honest limits.

> **Design notes.**
> 1. **Deferred 1.5a call #1 — untouched-worksheet silence: resolved by location, not severity.** #8's silence clause is the #5 parallel (an activity with no deep record is silent; a record that exists is acted-on). So a file in `governance/constitution/` is a kept rule and is never silent; blank worksheets live in `governance/worksheets/`, which `check_constitution` does not scan. Task 1 makes that concrete.
> 2. **Deferred 1.5a call #2 — active-rule provenance is a WARN, not an ERROR.** #8's ERROR tier is "strict exactly where a field backs a running agent or a safety invariant"; `ritual`/`scarcity`/`surviving_job` are thinking-quality, so they sit in the WARN ("incomplete thinking") tier. The one place provenance *is* load-bearing — orphan-prohibition — already requires `surviving_job` when `repeals` is present.
> 3. **The hook set ships, it does not run here.** `governance/hooks/` is the auditable artifact; installation into a company repo's `.claude/settings.json` is documented, not performed on this repo.

---

## Task 1: Close the two deferred 1.5a calls (provenance WARN + worksheet location)

**Files:**
- Modify: `scripts/validate.py`, `tests/test_validate.py`, `governance/README.md`
- Create: `governance/worksheets/five-question-worksheet.md`

**Interfaces:**
- Extends `check_constitution`: on an **active** rule, each of `ritual`, `scarcity`, `surviving_job` that is blank → WARN "incomplete thinking".

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestConstitutionProvenance(unittest.TestCase):
    def test_active_rule_missing_provenance_warns(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/access.md",
                   RULE_OK.replace("scarcity: Security-review time — every grant got a human's eyes\n", ""))
            findings = validate.check_constitution(d)
            self.assertTrue(any(f.level == "WARN" and "scarcity" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "scarcity" in f.message for f in findings))

    def test_complete_rule_has_no_provenance_warn(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/access.md", RULE_OK)
            self.assertFalse(any("incomplete thinking" in f.message
                                 for f in validate.check_constitution(d)))

    def test_worksheets_dir_is_not_scanned_as_rules(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/worksheets/blank.md", "# Blank worksheet\n\nNothing filled in.\n")
            self.assertEqual(validate.check_constitution(d), [])
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestConstitutionProvenance -v`
Expected: FAIL — the provenance WARN is not emitted.

- [ ] **Step 3: Implement** — in `check_constitution`, inside the `else:` (active) branch, after the sunset block, add:

```python
            for field in ("ritual", "scarcity", "surviving_job"):
                if _blank(data.get(field)):
                    findings.append(Finding("WARN", rel, None,
                                            "missing '%s' (incomplete thinking — the five-question "
                                            "worksheet's provenance)" % field))
```

(The third test already passes if `check_constitution` scans only `governance/constitution/`; confirm it does and do not widen the scan.)

- [ ] **Step 4: Create `governance/worksheets/five-question-worksheet.md`:**

```markdown
# Five-question worksheet (blank)

The constitution compiler's input. Copy this per ritual. **Files in this folder are
not rules** — they are unfinished thinking, and the validator does not check them.
A ritual becomes a rule only when a filled worksheet is compiled into a record in
`governance/constitution/`.

Start with the rule everybody resents.

1. **Name the ritual.** What do we actually do, in plain words?
2. **Name the scarcity it protected.** What was expensive or rare when this started?
3. **Is that scarcity still real — and what job survives?** If the scarcity is gone,
   some job it was doing usually remains. Name it.
4. **Rewrite it as a rule a person can verify.** No vibes: a statement someone can
   check.
5. **Decide the machinery.** Trigger, evidence, action, owner, appeal — and which
   rung of the ladder it sits on.

If the ritual is repealed, its **surviving job must be reassigned to a named owner
before the repeal ships** (orphan-prohibition).
```

- [ ] **Step 5: Document the location rule** — append to `governance/README.md`:

```markdown

## Where worksheets live (and why it matters)

Blank and in-progress five-question worksheets live in `governance/worksheets/`.
Kept, compiled rules live in `governance/constitution/`. The validator checks only
`governance/constitution/` — so an unfinished worksheet for a ritual nobody has acted
on is silent, exactly as the doctrine requires, while every file that *is* a rule is
held to the full contract. Silence is decided by **location**, not by leniency.
```

- [ ] **Step 6: Run the suite and validate**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate.py .`
Expected: tests PASS; validator exit 0. (The shipped rule `access-grants-need-human-signoff.md` already carries all three provenance fields, so no new WARN appears against real content.)

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py governance/README.md governance/worksheets/
git commit -m "feat(governance): active-rule provenance WARN + worksheet location convention (1.5a deferrals)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The hook — `classify()` + stdin/stdout gate

**Files:**
- Create: `governance/hooks/action_class_gate.py`
- Modify: `tests/test_validate.py`

**Interfaces:**
- Produces:
  - `classify(command) -> (category, reason) | (None, None)` — pure; matches a curated high-risk pattern set.
  - `decide(payload) -> dict | None` — pure; maps a hook payload to the decision JSON (or `None` for "no decision").
  - `main()` — reads stdin JSON, prints the decision JSON, exits 0.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py` (import the hook module by path):

```python
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "governance" / "hooks"))
import action_class_gate  # noqa: E402


class TestActionClassGate(unittest.TestCase):
    def test_destructive_delete_blocked(self):
        cat, _ = action_class_gate.classify("rm -rf /var/data")
        self.assertEqual(cat, "delete")

    def test_force_push_blocked(self):
        cat, _ = action_class_gate.classify("git push --force origin main")
        self.assertEqual(cat, "delete")

    def test_external_send_blocked(self):
        cat, _ = action_class_gate.classify("curl -X POST https://api.example.com/pay -d '{}'")
        self.assertEqual(cat, "external-send")

    def test_benign_command_not_blocked(self):
        self.assertEqual(action_class_gate.classify("npm test")[0], None)
        self.assertEqual(action_class_gate.classify("git status")[0], None)

    def test_decide_denies_high_risk(self):
        out = action_class_gate.decide(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": "rm -rf /"}})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PreToolUse")

    def test_decide_defers_on_benign(self):
        self.assertIsNone(action_class_gate.decide(
            {"hook_event_name": "PreToolUse", "tool_name": "Bash",
             "tool_input": {"command": "ls"}}))

    def test_decide_asks_on_malformed_input(self):
        out = action_class_gate.decide({"hook_event_name": "PreToolUse", "tool_name": "Bash"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestActionClassGate -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'action_class_gate'`.

- [ ] **Step 3: Create `governance/hooks/action_class_gate.py`:**

```python
#!/usr/bin/env python3
"""groundwork action-class gate — a fixed, hand-authored Claude Code PreToolUse hook.

Hard-blocks high-risk actions (spend / delete / external-send) so a named human
signs off first: consequential actions never terminate in automation ("there is no
rung six"). This file is the SAME for every company and is never generated — that is
what makes it auditable.

HIGH-SIGNAL, NOT EXHAUSTIVE. It matches a curated pattern set, not every dangerous
command. See docs/known-limitations.md. Hooks are a Claude-Code-only surface; on
Codex / Cursor / Gemini this file is silently ignored and the same rule ships as a
review-gate instruction (governance/hooks/review-gate.md).

Python 3 standard library only — no jq, no third-party deps.
"""
import json
import re
import sys

# (category, human-readable action, pattern). Curated and auditable — add with care.
HIGH_RISK_PATTERNS = [
    ("delete", "recursive/forced file deletion", re.compile(r"\brm\s+(-\w*\s+)*-\w*[rf]")),
    ("delete", "force push (rewrites shared history)", re.compile(r"\bgit\s+push\b[^\n]*(--force\b|(?<!\w)-f\b)")),
    ("delete", "hard reset (discards work)", re.compile(r"\bgit\s+reset\s+--hard\b")),
    ("delete", "force-clean untracked files", re.compile(r"\bgit\s+clean\b[^\n]*-\w*f")),
    ("delete", "destructive database statement", re.compile(r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b", re.I)),
    ("delete", "raw disk write", re.compile(r"\b(mkfs(\.\w+)?|dd\s+[^\n]*\bof=/dev/)")),
    ("external-send", "outbound write request", re.compile(r"\bcurl\b[^\n]*(-X\s*(POST|PUT|PATCH|DELETE)\b|--data\b|(?<!\w)-d\s)")),
    ("external-send", "outbound post", re.compile(r"\bwget\b[^\n]*--post-(data|file)\b")),
    ("external-send", "outbound mail", re.compile(r"\b(sendmail|mailx|mutt)\b")),
    ("spend", "infrastructure apply (provisions billable resources)", re.compile(r"\bterraform\s+apply\b")),
    ("spend", "payments CLI", re.compile(r"\bstripe\s+(charges?|payment_intents?|payouts?|refunds?)\b")),
]

_DENY_REASON = (
    "Blocked by the groundwork action-class gate: this looks like a HIGH-RISK "
    "action ({category} — {action}). The constitution requires a named human's "
    "sign-off before a consequential action runs; an agent may propose it, not "
    "perform it. There is no rung six. If this is legitimate, a human should run "
    "it or explicitly approve it."
)


def classify(command):
    """Return (category, action) for a curated high-risk match, else (None, None)."""
    if not isinstance(command, str):
        return None, None
    for category, action, pattern in HIGH_RISK_PATTERNS:
        if pattern.search(command):
            return category, action
    return None, None


def _output(decision, reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": decision,
                                   "permissionDecisionReason": reason}}


def decide(payload):
    """Map a PreToolUse payload to a decision dict, or None for 'no decision'.

    Never silently allows: an unreadable payload escalates to 'ask' rather than
    passing through or hard-blocking.
    """
    if not isinstance(payload, dict):
        return _output("ask", "groundwork action-class gate could not read the tool call; "
                              "asking a human rather than guessing.")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return _output("ask", "groundwork action-class gate could not read the tool input; "
                              "asking a human rather than guessing.")
    command = tool_input.get("command")
    if command is None:
        return None  # not a command-bearing tool call; nothing for this gate to say
    if not isinstance(command, str):
        return _output("ask", "groundwork action-class gate could not read the command; "
                              "asking a human rather than guessing.")
    category, action = classify(command)
    if category is None:
        return None  # defer to the normal permission flow
    return _output("deny", _DENY_REASON.format(category=category, action=action))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:  # unreadable stdin — ask, never silently allow
        print(json.dumps(_output("ask", "groundwork action-class gate received unreadable input; "
                                        "asking a human rather than guessing.")))
        return 0
    decision = decide(payload)
    if decision is not None:
        print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Make it executable**

Run: `chmod +x governance/hooks/action_class_gate.py`

- [ ] **Step 5: Run to verify pass, plus a real end-to-end stdin check**

Run: `python3 -m unittest tests.test_validate.TestActionClassGate -v`
Expected: PASS.

Run: `echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/x"}}' | python3 governance/hooks/action_class_gate.py`
Expected: JSON on stdout containing `"permissionDecision": "deny"`, exit 0.

Run: `echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"npm test"}}' | python3 governance/hooks/action_class_gate.py`
Expected: **no output**, exit 0 (defer to the normal permission flow).

- [ ] **Step 6: Commit**

```bash
git add governance/hooks/action_class_gate.py tests/test_validate.py
git commit -m "feat(governance): fixed Claude-Code action-class gate hook (high-risk hard-block, stdlib-only)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: Registration snippet, the #19 review-gate degradation, and the docs

**Files:**
- Create: `governance/hooks/settings.snippet.json`, `governance/hooks/review-gate.md`, `governance/hooks/README.md`
- Modify: `docs/known-limitations.md`

**Interfaces:** the snippet's `command` path must resolve — Task 4's `check_hooks` enforces it.

- [ ] **Step 1: Create `governance/hooks/settings.snippet.json`:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PROJECT_DIR}/governance/hooks/action_class_gate.py",
            "timeout": 30,
            "statusMessage": "Checking action class..."
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Create `governance/hooks/review-gate.md`:**

```markdown
# Review gate — high-risk actions (non-Claude harnesses)

Hooks are a **Claude-Code-only** surface. Codex, Cursor, and Gemini CLI read this
repo's skills but **silently ignore** hook configuration — no warning, no rejection.
So on those harnesses the action-class gate ships as an instruction instead of a
block. Copy this text into the harness's instruction file (`AGENTS.md`, Cursor rules).

## The rule

You may **propose** a high-risk action. You may not **perform** one. High-risk means
**spend**, **delete**, or **external-send** — anything that moves money, destroys
data or history, or sends something outside the company.

Before any such action:

1. **Stop.** Do not run the command.
2. **Say what you would do**, in one line, and why.
3. **Name the human** who has to approve it (the owner on the relevant Owner's Card).
4. **Wait** for that person's explicit approval in the session.

There is no rung six: a consequential action never terminates in automation. If you
are unsure whether an action is high-risk, treat it as high-risk and ask.

**Honest limitation:** this is an instruction, not enforcement. On Claude Code the
same rule is a hard block. Cross-harness runtime-enforcement parity is a named,
deliberate later graduation — not something V1 claims to have.
```

- [ ] **Step 3: Create `governance/hooks/README.md`:**

```markdown
# The action-class gate (V1's runnable governance floor)

A **fixed, hand-authored, audited** hook set that enforces the four action classes
(`read-only` / `reversible-write` / `external-side-effect` / `high-risk`). High-risk
actions — spend, delete, external-send — are **hard-blocked** until a named human
signs off. It is the same for every company and is **never generated by the
interview**, which is what makes it auditable: you can read all of it.

## Files

| File | What it is |
|---|---|
| `action_class_gate.py` | The hook. Python 3 stdlib only (no `jq`). Pure `classify()` behind a stdin/stdout `main()`. |
| `settings.snippet.json` | The Claude Code registration snippet. |
| `review-gate.md` | The #19 degradation: the same rule as an instruction, for harnesses without hooks. |

## Install (Claude Code, in your company repo)

Merge `settings.snippet.json` into your repo's `.claude/settings.json` (create it if
absent), keeping any hooks you already have. Then verify:

```
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/x"}}' \
  | python3 governance/hooks/action_class_gate.py
```

You should see a JSON decision with `"permissionDecision": "deny"`. A benign command
(`npm test`) should print nothing.

## Install (Codex / Cursor / Gemini CLI)

These harnesses **silently ignore** hooks. Copy `review-gate.md` into the harness's
instruction file instead. The rule is identical; the enforcement is a human review
gate rather than a block. This asymmetry is stated plainly rather than papered over.

## What it does and does not do

- **Does:** deny a curated set of high-risk command patterns before they run, with a
  reason that names the action class and points at human sign-off.
- **Does:** escalate to `ask` — never a silent allow — when it cannot read a tool call.
- **Does not:** claim completeness. The pattern set is **high-signal, not exhaustive**;
  a determined or unusual command can slip past it. It is a floor, not a sandbox.
- **Does not:** run in this engine repo. It is an artifact you install into a company
  repo.
```

- [ ] **Step 4: Append to `docs/known-limitations.md`:**

```markdown

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
```

- [ ] **Step 5: Validate**

Run: `python3 scripts/validate.py .`
Expected: exit 0 (the new docs and JSON introduce no ERRORs).

- [ ] **Step 6: Commit**

```bash
git add governance/hooks/ docs/known-limitations.md
git commit -m "feat(governance): hook registration snippet, #19 review-gate degradation, honest limits

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: `check_hooks` — existence-check the enforcement claim

**Files:**
- Modify: `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:**
- Produces: `check_hooks(root) -> list[Finding]`, wired into `validate(root)`.
- Behavior: if `governance/hooks/` exists — the snippet must be **valid JSON** (ERROR otherwise); every hook `command` it declares must reference a file that **exists** (ERROR otherwise, after stripping a leading interpreter and resolving `${CLAUDE_PROJECT_DIR}` to the repo root); a missing `review-gate.md` is a **WARN** (the degradation story is incomplete, but nothing is mis-wired).
- Also: **extend `TestZeroDep`** to assert every `governance/hooks/*.py` imports stdlib only (allowlist gains `json`).

> Why this check exists: *"enforced via X" is a claim about the world.* A hook set whose `command` path does not resolve is a named-but-unwired guard — a false sense of safety, which is worse than an admitted gap.

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
SNIPPET_OK = """{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command",
                  "command": "python3 ${CLAUDE_PROJECT_DIR}/governance/hooks/action_class_gate.py"}]}
    ]
  }
}
"""


class TestHooks(unittest.TestCase):
    def _set(self, d, snippet=SNIPPET_OK, script=True, review=True):
        _write(d, "governance/hooks/settings.snippet.json", snippet)
        if script:
            _write(d, "governance/hooks/action_class_gate.py", "# hook\n")
        if review:
            _write(d, "governance/hooks/review-gate.md", "# review gate\n")

    def test_wired_hook_set_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d)
            self.assertEqual([f for f in validate.check_hooks(d) if f.level == "ERROR"], [])

    def test_unwired_command_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, script=False)
            errs = [f for f in validate.check_hooks(d) if f.level == "ERROR"]
            self.assertTrue(any("not found" in f.message for f in errs))

    def test_invalid_json_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, snippet="{ not json ")
            self.assertTrue(any(f.level == "ERROR" and "JSON" in f.message
                                for f in validate.check_hooks(d)))

    def test_missing_review_gate_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._set(d, review=False)
            findings = validate.check_hooks(d)
            self.assertTrue(any(f.level == "WARN" and "review-gate" in f.message for f in findings))
            self.assertFalse(any(f.level == "ERROR" and "review-gate" in f.message for f in findings))

    def test_no_hooks_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_hooks(d), [])
```

And **extend `TestZeroDep`** so shipped hook scripts are covered:

```python
    def test_shipped_hook_scripts_only_stdlib(self):
        allowed = {"os", "sys", "re", "ast", "math", "fnmatch", "collections",
                   "pathlib", "datetime", "subprocess", "unicodedata", "json"}
        hooks_dir = REPO / "governance" / "hooks"
        if not hooks_dir.is_dir():
            self.skipTest("no shipped hooks")
        for py in sorted(hooks_dir.glob("*.py")):
            tree = ast.parse(py.read_text())
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        mods.add(n.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods.add(node.module.split(".")[0])
            self.assertEqual(mods - allowed, set(), "%s imports non-stdlib: %s" % (py.name, mods - allowed))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestHooks -v`
Expected: FAIL — no attribute `check_hooks`.

- [ ] **Step 3: Implement** — add `import json` to `scripts/validate.py`'s imports, then add:

```python
def _hook_command_target(command, root):
    """Best-effort: pull the script path out of a hook command string.
    Strips a leading interpreter and resolves ${CLAUDE_PROJECT_DIR} to root."""
    if not isinstance(command, str) or not command.strip():
        return None
    parts = command.split()
    # drop a leading interpreter (python3, python, bash, sh, node, ...)
    if parts and os.path.basename(parts[0]) in {"python3", "python", "bash", "sh", "node"}:
        parts = parts[1:]
    if not parts:
        return None
    target = parts[0].replace("${CLAUDE_PROJECT_DIR}", root).replace("$CLAUDE_PROJECT_DIR", root)
    if not os.path.isabs(target):
        target = os.path.join(root, target)
    return os.path.normpath(target)


def check_hooks(root):
    """Existence-check the enforcement claim: a hook set whose command path does not
    resolve is a named-but-unwired guard — false safety, worse than an admitted gap."""
    findings = []
    hooks_dir = os.path.join(root, "governance", "hooks")
    if not os.path.isdir(hooks_dir):
        return findings
    rel_dir = os.path.relpath(hooks_dir, root)
    snippet = os.path.join(hooks_dir, "settings.snippet.json")
    if not os.path.isfile(snippet):
        findings.append(Finding("WARN", os.path.join(rel_dir, "settings.snippet.json"), None,
                                "hook set has no settings.snippet.json (nothing to install)"))
    else:
        rel_snip = os.path.relpath(snippet, root)
        try:
            with open(snippet, encoding="utf-8") as fh:
                data = json.load(fh)
        except (ValueError, OSError) as exc:
            findings.append(Finding("ERROR", rel_snip, None,
                                    "hook settings snippet is not valid JSON (%s)" % exc))
            data = None
        if isinstance(data, dict):
            events = data.get("hooks")
            groups = []
            if isinstance(events, dict):
                for entries in events.values():
                    if isinstance(entries, list):
                        groups.extend(entries)
            declared = 0
            for group in groups:
                if not isinstance(group, dict):
                    continue
                for hook in group.get("hooks", []) if isinstance(group.get("hooks"), list) else []:
                    if not isinstance(hook, dict) or hook.get("type") != "command":
                        continue
                    declared += 1
                    target = _hook_command_target(hook.get("command"), root)
                    if target is None:
                        findings.append(Finding("ERROR", rel_snip, None,
                                                "hook declares no runnable command"))
                    elif not os.path.isfile(target):
                        findings.append(Finding("ERROR", rel_snip, None,
                                                "hook command not found: %s (a named-but-unwired "
                                                "guard is false safety)" % hook.get("command")))
            if declared == 0:
                findings.append(Finding("WARN", rel_snip, None,
                                        "hook settings snippet declares no command hooks"))
    if not os.path.isfile(os.path.join(hooks_dir, "review-gate.md")):
        findings.append(Finding("WARN", os.path.join(rel_dir, "review-gate.md"), None,
                                "hook set has no review-gate.md — the non-Claude degradation (#19) is undocumented"))
    return findings
```

- [ ] **Step 4: Wire into `validate()`** — at the end of `validate(root)`, after `findings += check_constitution(root)`, add:

```python
    findings += check_hooks(root)
```

- [ ] **Step 5: Run the full suite and the real gate**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS (including both zero-dep tests).

Run: `python3 scripts/validate.py .`
Expected: exit 0 — the real hook set is wired (the snippet's command resolves to the committed script) and `review-gate.md` exists, so no ERROR or WARN fires against it.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): check_hooks — existence-check the hook set's enforcement claim + wire in

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes (next sub-slices)

- **Slice 1.5c:** version pin (#21) + skew checks (`SCHEMA_VERSION`, `MIGRATIONS.md`, per-check `since:` tags, the migration gate) + the deferred stateless-walker symlinked-`memory/`-directory hardening.
- **Slice 1.5d:** proposal schema (#17) + consent gate (#18) + the blast-radius match tripwire (reuses 1.4b `--diff`) + the governance changelog.
- **Phase 2.3:** demo canon (#16) + synthetic-identifier check; the one runnable rung-3 exemplar (#8 item 3 — the **meeting-challenger**), which ships *inside the demo company*, not here.
- **Deliberately not done:** installing the gate into this engine repo's `.claude/settings.json` (dogfooding groundwork's own machinery is retained fog on the map).

## Self-Review

- **Ticket coverage (#8 item 2, #19):** fixed hand-authored hook set enforcing the four action classes with high-risk hard-block → Task 2; not generated / auditable → it is one committed file, documented as fixed; degrades to a review-gate instruction on Codex/Cursor/Gemini → Task 3 `review-gate.md`; the honest asymmetry → Task 3 docs + known-limitations. **1.5a deferrals** → Task 1 (provenance WARN; worksheet location).
- **Live-contract fidelity:** field names (`hook_event_name`, `tool_name`, `tool_input.command`, `hookSpecificOutput.hookEventName/permissionDecision/permissionDecisionReason`), the `allow|deny|ask|defer` values, exit-0-with-JSON semantics, `${CLAUDE_PROJECT_DIR}`, and the `hooks.PreToolUse[].matcher` shape all come from the official hooks reference fetched 2026-07-23 — not from memory. The docs' `bash`+`jq` example is deliberately **not** followed (zero-dep).
- **Placeholder scan:** no TBD/TODO/"handle edge cases"; complete code and content; verification commands have expected output, including two real stdin round-trips.
- **Type consistency:** `Finding`, `_blank`, `parse_frontmatter` reused unchanged; `classify`/`decide`/`main` in `action_class_gate` match their test call sites; `check_hooks(root)` and `_hook_command_target(command, root)` match their call sites; `json` added to both the validator imports and both zero-dep allowlists.
- **Fail-closed posture:** `decide` returns `ask` (never a silent allow) on unreadable payloads; `main` catches stdin errors and still emits `ask`. `check_hooks` ERRORs on an unwired command rather than assuming the guard works.
```

