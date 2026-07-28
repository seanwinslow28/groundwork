# The meeting challenger — one runnable rule

This is the one piece of Umbercress's constitution that is **working machinery** rather
than a typed record. It is the runnable form of
[every recurring meeting names a decision](../../constitution/every-meeting-names-a-decision.md),
a rung-3 rule: when an agent schedules or extends a recurring meeting, it gets reminded
to name the decision the series exists to make and who owns it.

It is **hand-authored and copied, never generated**. groundwork's interview does not
write hooks. This exists so the shape of a runnable rule is concrete and copyable —
take it, change the rule text, ship your own.

## What a rung-3 hook looks like

The five-rung ladder is `value` → `instruction` → `reminder` → `hard-block` →
`human-decision`, and the rung a rule sits on should be visible in what its machinery
*does*:

| Rung | What the hook returns |
|---|---|
| hard-block (4) | `permissionDecision: "deny"` — the action does not run |
| **reminder (3)** | **`permissionDecision: "defer"` plus the reminder text** — the action runs as it otherwise would; only what the agent and the human *know* changes |

A reminder that returns `"ask"` has quietly become a gate. That is rung inflation, and
it is how a company ends up with machinery nobody agreed to.

## Install (Claude Code, in your company repo)

Merge this into `.claude/settings.json`, keeping any hooks already there:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/governance/reminders/meeting-challenger/meeting_challenger.py\"",
            "timeout": 30,
            "statusMessage": "Checking the meeting rule..."
          }
        ]
      }
    ]
  }
}
```

The matcher is `*` on purpose: a meeting gets scheduled through whatever calendar tool
the company has connected, and the hook decides from the call rather than from a tool
name it would have to guess.

## Verify it

A recurring-meeting-shaped call gets the reminder:

```
echo '{"hook_event_name":"PreToolUse","tool_name":"calendar_create_event","tool_input":{"title":"Weekly ops sync","recurrence":"weekly"}}' \
  | python3 governance/reminders/meeting-challenger/meeting_challenger.py
```

You should see JSON containing `"permissionDecision": "defer"` and the reminder text.
Anything else prints nothing at all:

```
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"npm test"}}' \
  | python3 governance/reminders/meeting-challenger/meeting_challenger.py
```

(The paths above are written as they resolve inside a company repo, where this
directory sits at the root. Inside this engine repo, prefix them with `demo/`.)

## Install (Codex / Cursor / Gemini CLI)

These harnesses **silently ignore** hooks — no warning, no rejection. Copy this
paragraph into the harness's instruction file instead:

> **Umbercress meeting rule.** Before scheduling or extending a recurring meeting,
> state the decision the series exists to make and the person who owns that decision.
> If it has neither, it is a broadcast — send a written note instead. This is a
> reminder, not a block: if the person disagrees, schedule the meeting.

Same rule, weaker enforcement. That asymmetry is stated rather than papered over, and
cross-harness runtime parity is a named later graduation, not something V1 claims.

## What it does and does not do

- **Does:** remind, on every tool call that looks like scheduling or extending a
  recurring meeting, and stay completely silent otherwise.
- **Does:** leave the permission outcome exactly as it found it.
- **Does not:** judge whether an invite already names a decision. It fires on *shape*,
  never on content — guessing at the meaning of text nobody controls has an unbounded
  supply of ways to be wrong, and a reminder that fires on a well-formed invite is
  cheap while a reminder suppressed by a bad guess is invisible.
- **Does not:** run anywhere in this repository. Nothing here registers it; it is an
  artifact to copy into a company repo. `demo/` is a worked example, not an installed
  system.
- **Does not:** import anything outside the Python standard library — checked by the
  repo's test suite along with every other shipped script.
