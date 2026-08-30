---
target: governance/roles.md
blast_radius: escalating
reason: The org map had not been re-confirmed since May and its review date was a policy default nobody had answered
evidence:
  - interview/06-org-map.md
status: pending
---
# Proposal: re-confirm the org map, and date it from an answered cadence

## Diff

```diff
--- a/governance/roles.md
+++ b/governance/roles.md
@@ frontmatter
-valid_at: 2026-05-11
-review_by: 2026-08-09
-source: Interview layers 01, 02 and 03, each confirmed by the person it names — Priya Raman, Marcus Bell, Ruth Okafor.
+valid_at: 2026-08-20
+review_by: 2026-11-18
+source: Interview layers 01, 02 and 03, each confirmed by the person it names — Priya Raman, Marcus Bell, Ruth Okafor — and re-confirmed together by layer 06, which is also where the cadence below comes from.
@@ the holders paragraph — one sentence added, one reworded
 a rule whose owner reads Ruth Okafor resolve.
+Asked directly in layer 06, each of the three said the accountability was theirs rather than their chair's.
-The offices these people hold are recorded in the demo's canon file; no rule references one, so no Role row asserts one.
+The offices they hold are recorded in the demo's canon file; no rule references one, so no Role row asserts one.
@@ a new paragraph after it
+No holder here is an agent. That was asked rather than assumed — nothing in the three rules terminates in a model, and the human-decision rule's appeal path is Ruth Okafor herself.
@@ the dates paragraph, replaced by two
-The valid_at date is a snapshot — the earliest date among the interview layers these entries came from, so no entry's staleness is hidden behind a newer one. The review_by date is the **policy default of 90 days**, not an elicited cadence: nothing in the interview asked how often the org map should be re-confirmed, so nothing here may claim an answer. That default has now passed, and the validator says so — which is the mechanism working, not a defect to date around.
+The valid_at date is a snapshot — the earliest date among the layers these entries came from, where each entry is dated by its most recent confirming layer. All three were re-confirmed together on 2026-08-20, which is why that date is not May.
+
+The review_by date is derived, and here is the derivation: the cadence answered was **quarterly**, the base date was valid_at 2026-08-20, and the date that produces is 2026-11-18. Nobody named a date; the cadence was the answer and this file did the conversion. It is not the 90-day policy default a generator falls back to when the cadence question goes unanswered — the two spans happen to be the same length, which is exactly why a roster that does not say which one it used cannot be read.
@@ the table
 Unchanged. No row is added, removed, or retyped.
```

## Why

Two separate problems, one turn.

**The map was five months old.** The roster's entries were written from layers 01, 02 and
03, confirmed in May and early June, and nothing had asked those three people since whether
the answer still held. A roster is repo-internal consistency, not reality, and the only
thing standing between it and a confident wrong answer is somebody re-reading it. The
[org-map session](../interview/06-org-map.md) is that re-reading: all three owners present,
each asked directly, all three re-confirmed on 2026-08-20.

**The review date was not an answer.** It was the generator's 90-day fallback, used because
nothing in the interview had asked how often the map should be re-checked. The file said so,
honestly, and the gate warned that it had passed — but a date nobody chose cannot be
defended and cannot be changed for a reason. The same session asked the question. The answer
was quarterly, with Priya's reasoning recorded, and the new date is that cadence converted
from the new snapshot rather than a span picked to clear a warning.

**What this does not change.** No holder is added, removed or retyped, and no Role row
appears. The three rules resolve to exactly the people they resolved to before. This is a
change to when the record was last true and when it should next be checked — which is
governance rather than bookkeeping, and why it is here rather than in a commit.
