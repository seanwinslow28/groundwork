#!/usr/bin/env python3
"""Umbercress meeting challenger — a worked, runnable rung-3 (reminder) rule.

Pairs with governance/constitution/every-meeting-names-a-decision.md: when an agent
schedules or extends a recurring meeting, remind it to name the decision the series
exists to make and the person who owns that decision.

RUNG 3 IS NOT RUNG 4. A reminder does not change what happens. This hook emits **no
`permissionDecision` at all** — it carries the reminder in `additionalContext` (for the
agent) and `systemMessage` (for the person) and leaves the permission outcome exactly
as it found it. It never denies, never auto-approves, and never prompts. A reminder
that blocks is rung inflation: machinery claiming more authority than the rule was
granted.

Every one of the four decision values would have been wrong here. `deny` is rung 4.
`allow` grants authority the rule was never given. `ask` turns a nudge into a gate.
`defer` reads like "use the normal flow" but is not: it is the headless signal that a
call was blocked without user input, it behaves as `ask` interactively, and
`additionalContext` is ignored alongside it — so it would both prompt the human and
drop the agent's half of the reminder. Emitting no decision is the only shape that
changes what people KNOW without touching what they MAY DO.

IT FIRES ON SHAPE, NEVER ON CONTENT. It does not try to decide whether an invite
"already names a decision" — that would be a guess about text nobody controls, with an
unbounded supply of ways to be wrong. It nudges every recurring-meeting-shaped call and
says so; a person decides whether the nudge applies.

Hand-authored and copied, never generated. Hooks are a Claude-Code-only surface; on
Codex / Cursor / Gemini this file is silently ignored and the same rule ships as the
review-gate paragraph in README.md.

Python 3 standard library only.
"""
import json
import re
import sys

RULE = "governance/constitution/every-meeting-names-a-decision.md"

REMINDER = (
    "Umbercress rule (rung 3, reminder): every recurring meeting names the decision it "
    "exists to make and the person who owns that decision. This is a reminder, not a "
    "block — the meeting still gets scheduled. If this series has no decision and no "
    "owner, say so in the invite, or send a written note instead. "
    "Rule: %s. Owner: Priya Raman. Disagree? Say so in the invite." % RULE
)

# Two independent signals, both required: the call must look like a MEETING and like it
# RECURS. Either alone is too broad — 'weekly report' is not a meeting, and a one-off
# invite is not the ritual this rule is about.
_RECURRING = re.compile(
    r"\b(recurring|recurrence|repeats?|repeating|weekly|bi-?weekly|fortnightly|monthly|"
    r"daily|standing|series|every\s+(?:week|month|other\s+week|"
    r"mon|tues?|wednes|thurs?|fri)\w*)\b", re.I)
_MEETING = re.compile(
    r"\b(meeting|invite|invitation|stand-?up|sync|check-?in|all-?hands|retro\w*|"
    r"one-on-one|1:1|calendar\s+event)\b", re.I)


_MAX_DEPTH = 6


def _strings(value, depth=0):
    """Every string anywhere inside a JSON-shaped value, nested dicts and lists
    included. A one-level scan would have missed the common calendar shape —
    {"event": {"title": ..., "recurrence": "weekly"}} — and a missed reminder is
    invisible, so this walks the whole payload. Depth is bounded because the
    payload comes from a tool call this hook does not control; anything deeper
    contributes nothing rather than raising."""
    if isinstance(value, str):
        return [value]
    if depth >= _MAX_DEPTH:
        return []
    out = []
    if isinstance(value, dict):
        for v in value.values():
            out.extend(_strings(v, depth + 1))
    elif isinstance(value, (list, tuple)):
        for v in value:
            out.extend(_strings(v, depth + 1))
    return out


def _text(tool_name, tool_input):
    """Flatten a tool call into one searchable string: the tool's name plus every
    string value anywhere in its input. Anything unreadable contributes nothing."""
    parts = []
    if isinstance(tool_name, str):
        parts.append(tool_name)
    parts.extend(_strings(tool_input))
    return "\n".join(parts)


def challenges(tool_name, tool_input):
    """Pure: does this tool call look like scheduling or extending a recurring meeting?"""
    blob = _text(tool_name, tool_input)
    if not blob:
        return False
    return bool(_RECURRING.search(blob) and _MEETING.search(blob))


def decide(payload):
    """Map a PreToolUse payload to a reminder dict, or None for 'say nothing'.

    Unreadable input is SILENT here — the opposite of the action-class gate, which
    escalates to 'ask'. That gate stands between an agent and a consequential action,
    so its failure mode must be loud. This is a nudge about a calendar entry: turning
    an unreadable payload into a prompt would make a rung-3 rule interrupt people on
    input it never understood. A missed nudge is recoverable; a reminder that becomes
    a gate is not the rule the company agreed to.
    """
    if not isinstance(payload, dict):
        return None
    if not challenges(payload.get("tool_name"), payload.get("tool_input")):
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            # No 'permissionDecision' key. Its absence IS the rung-3 mechanism: the
            # tool call goes through whatever permission flow it would have hit
            # anyway, and the only thing this hook changes is what the agent and
            # the human know. Adding any decision here would be rung inflation.
            "additionalContext": REMINDER,
        },
        # Universal field, shown to the person and not to the agent — the two
        # halves of the reminder reach two different readers.
        "systemMessage": REMINDER,
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # unreadable input: a reminder stays silent rather than interrupting
    reminder = decide(payload)
    if reminder is not None:
        print(json.dumps(reminder))
    return 0


if __name__ == "__main__":
    sys.exit(main())
