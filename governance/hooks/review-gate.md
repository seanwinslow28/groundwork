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
