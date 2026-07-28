---
owner: Priya Raman
rung: reminder
action_class: reversible-write
sunset: 2027-06-30
value: A recurring meeting spends the company's scarcest resource, so it should exist to make a decision somebody owns
value_owner: Priya Raman
runtime_check: When an agent schedules or extends a recurring meeting, it is reminded — not blocked — to state the decision the series exists to make and the person who owns that decision. The reminder ships as a Claude Code hook and as a review-gate instruction elsewhere
runtime_check_owner: Priya Raman
human_appeal: Anyone who thinks the reminder is wrong for a given series says so in the invite and schedules it anyway. Nobody at Umbercress has to justify a meeting to an agent
human_appeal_owner: Priya Raman
repeals: The Monday all-hands status round
reassigned_to: Priya Raman
ritual: The Monday all-hands status round — thirty minutes, everyone, no decision on the agenda
scarcity: Uninterrupted engineering and support time
surviving_job: Making sure the whole company hears what it needs to hear, which moved to a written Monday note Priya Raman posts
---
# Every recurring meeting names a decision

**The rule.** A recurring meeting states the decision it exists to make and the person
who owns that decision. If it has neither, it is a broadcast, and a broadcast is cheaper
written down.

**Why it sits at the reminder rung.** The failure this catches is drift, not danger. A
meeting that has outlived its decision is a slow tax, and the fix is a person noticing —
so the machinery nudges at the moment of scheduling and then gets out of the way. Making
this a hard block would put an agent in charge of the company's calendar, which is a
larger transfer of authority than the problem justifies.

**What it repealed.** The Monday all-hands status round. Its surviving job — making sure
the whole company hears what it needs to hear — moved to a written Monday note, and
Priya Raman owns it; a ritual is not repealed until its surviving job has somewhere to
live. Engineering had already run this argument once and written down what it cost:
[the move to asynchronous standups](../../memory/async-standups.md) records both the
saved hours and the incidental conversation that was given up.

**Appeal.** Say so in the invite. The reminder is a question, not a gate.

**The machinery.** [The meeting challenger](../reminders/meeting-challenger/README.md)
is the runnable form of this rule.
