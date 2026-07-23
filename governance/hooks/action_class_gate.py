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
