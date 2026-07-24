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

# A run of global CLI options between a binary and its subcommand, each option
# optionally followed by one value token (git -C repo push, git -c k=v reset,
# terraform -chdir=infra apply). Standard automation forms, not obfuscation.
# A token may contain quoted spans holding whitespace (git -C "/tmp/my repo",
# -c user.name="A B"), so "one token" means a run of non-space chars or quotes.
# a token char is a plain char, a backslash-escaped char (my\ repo), or a
# quoted span ("a b", 'a b')
_TOKEN_CHARS = r"(?:[^\s\"'\\]|\\.|\"[^\"]*\"|'[^']*')+"
_OPTS = r"(?:\s+-" + _TOKEN_CHARS + r"(?:\s+(?![-\s])" + _TOKEN_CHARS + r")?)*"

# (category, human-readable action, pattern). Curated and auditable — add with care.
HIGH_RISK_PATTERNS = [
    # short clusters may carry -R (uppercase recursive); long spellings are named
    # explicitly so a benign long flag containing 'r' (--verbose) does not match;
    # the prefix accepts value-bearing options (--preserve-root=all)
    ("delete", "recursive/forced file deletion",
     re.compile(r"\brm\s+(?:-\S+\s+)*(?:(?<!-)-[A-Za-z]*[rRf][A-Za-z]*(?![\w-])|--(?:recursive|force)\b)")),
    # a leading-plus refspec (git push origin +main) is git's documented
    # force-update syntax — a force push without --force; -f may sit inside a
    # short-option cluster (git push -fu)
    ("delete", "force push (rewrites shared history)",
     re.compile(r"\bgit" + _OPTS + r"\s+push\b[^\n]*"
                r"(--force\b|(?<![\w-])-[A-Za-z]*f[A-Za-z]*(?![\w-])|\s\+\S+)")),
    # git accepts reset options before --hard (git reset -q --hard HEAD)
    ("delete", "hard reset (discards work)",
     re.compile(r"\bgit" + _OPTS + r"\s+reset" + _OPTS + r"\s+--hard\b")),
    # -n / --dry-run forces a dry run even alongside -f, so it is read-only.
    # Asymmetric scan windows, each failing safe: the dry-run EXEMPTION stops at
    # '#' (comment text must not launder a real clean — worst case we deny a dry
    # run), while the FORCE scan does not (a '#' inside an argument like
    # --exclude=#keep must not hide -f — worst case we deny a commented mention).
    ("delete", "force-clean untracked files",
     re.compile(r"\bgit" + _OPTS + r"\s+clean\b"
                r"(?![^;&|#\n]*(?:(?<![\w-])-[A-Za-z]*n[A-Za-z]*(?![\w-])|--dry-run\b))"
                r"[^;&|\n]*-\w*f")),
    ("delete", "destructive database statement", re.compile(r"\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+TABLE)\b", re.I)),
    ("delete", "raw disk write", re.compile(r"\b(mkfs(\.\w+)?|dd\s+[^\n]*\bof=[\"']?/dev/)")),
    # request/body options in their standard spellings: -X POST / -XPOST /
    # --request=DELETE; -d/-F/-T with the payload spaced or attached (-d'{}',
    # -dname=value, -Ffile=@x, -Tbackup.tar) or ending a short-option cluster
    # (-sd x=1, -sTbackup.tar) — cluster letters before the payload flag may
    # err toward deny (a value spelling like -od also matches; deny fails safe)
    ("external-send", "outbound write request",
     re.compile(r"\bcurl\b[^\n]*(?:(?:-X|--request)[\s=]*(?:POST|PUT|PATCH|DELETE)\b"
                r"|--data(?:-\w+)?\b|(?<![\w-])-[A-Za-z]*d"
                r"|--json\b"
                r"|--form\b|(?<![\w-])-[A-Za-z]*F"
                r"|--upload-file\b|(?<![\w-])-[A-Za-z]*T)")),
    ("external-send", "outbound post", re.compile(r"\bwget\b[^\n]*--post-(data|file)\b")),
    ("external-send", "outbound mail", re.compile(r"\b(sendmail|mailx|mutt)\b")),
    ("spend", "infrastructure apply (provisions billable resources)",
     re.compile(r"\bterraform" + _OPTS + r"\s+apply\b")),
    # action-based: only mutating subcommands are spend; list/retrieve are read-only
    ("spend", "payments CLI",
     re.compile(r"\bstripe\s+(charges?|payment_intents?|payouts?|refunds?)\s+(create|update|capture|confirm|cancel)\b")),
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
    # bash joins backslash-newline continuations before executing — match the
    # command that runs, not the raw text
    command = command.replace("\\\n", " ")
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
    if not isinstance(command, str) or not command.strip():
        # the shipped snippet matches Bash only, so a payload without a usable
        # non-blank command string is unexpected input, not a different tool —
        # fail loud
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
