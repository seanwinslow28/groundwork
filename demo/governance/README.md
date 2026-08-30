# Umbercress — governance

Three rules Umbercress kept, each one compiled from a ritual somebody named. The engine
documents the compiler ([governance/README.md](../../governance/README.md)); this
directory is the output for one company.

| Rule | Rung | Governs |
|---|---|---|
| [Every recurring meeting names a decision](constitution/every-meeting-names-a-decision.md) | reminder (3) | Scheduling a recurring meeting |
| [No agent contacts a customer](constitution/no-agent-contacts-a-customer.md) | hard-block (4) | Anything that would reach a customer |
| [Writing a performance assessment is a human-owned decision](constitution/assessment-is-human-owned.md) | human-decision (5) | Evaluating a person |

The rungs are the point. A reminder nudges and gets out of the way. A hard block stops
the action. A human-owned decision never terminates in automation at all — which is why
that rule carries a named appeal path. There is no rung six.

## Who holds the owners

[roles.md](roles.md) is the roster: every owner these three rules name resolves against it.
These rules name people rather than offices, so every row is a holder with the Role cell
left empty — a name, no role asserted. That is what makes `owner: Ruth Okafor` resolve. The
offices those people hold are in [canon.md](../canon.md); no rule references one, so the
roster asserts none.

Its `review_by` is derived rather than chosen, and the roster shows the derivation: the
interview asked how often the org map should be re-confirmed, the answer was quarterly, and
the date is that cadence applied to the snapshot the map was last confirmed at. Getting
there took a turn of its own — [layer 6](../interview/06-org-map.md) re-confirmed all three
holders — and, because who holds an owner is governance, a proposal the maintainer had to
land. That proposal is no longer in [`proposals/`](../proposals/): it was applied, and an
applied proposal's file is removed. Until that turn ran, the date was a 90-day policy default
nobody had answered, and the gate warned that it had passed. That warning working is why the
turn happened.

## What is runnable here

One of the three ships as working machinery:
[the meeting challenger](reminders/meeting-challenger/README.md) is a real Claude Code
hook that fires the reminder rule at the moment somebody schedules a recurring meeting.
It is hand-authored and copied, never generated — the interview does not write hooks.

**The other two ship no runtime machinery at all,** and it would be dishonest to say
otherwise. They are typed records whose force comes from three places: what each skill
is permitted to reach in the first place, the forbidden actions on its Owner's Card, and
a named human reading the output before it matters. That is real, and it is weaker than
a hook — an instruction the agent is asked to follow can be talked out of; a permission
it was never granted cannot. Where the gap sits is written into each rule's
`runtime_check` rather than smoothed over, because a rule that claims enforcement it
does not have is worse than one that admits the gap.

## The changelog

[changelog.md](changelog.md) is the append-only index of changes an agent applied to a
track-1 skill body without asking. It is empty because nothing has been auto-applied
yet, which is the honest state of a company that just switched this on.
