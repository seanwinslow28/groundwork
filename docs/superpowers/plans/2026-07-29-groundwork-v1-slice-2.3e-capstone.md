# groundwork V1 — Slice 2.3e: the capstone (walkthrough + pin + live proposal) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Phase 2. Three artifacts: the **15-minute 3-query walkthrough** (#4 — decision lookup → cross-function synthesis → skill invocation, ending on the rung-5 governance block); **one live pending proposal** in `demo/proposals/`, the artifact query 3 produces when an agent is told no; and **`demo/groundwork.pin`**, which activates `check_version_pin` on real content and makes `demo/` a **governed root** so the #18 blast-radius tripwire runs against a real company instance for the first time.

**Architecture:** No new schema, no new checks. This slice turns two dormant mechanisms on. `check_proposals` gets its first real proposal (it has only ever seen fixtures). `blast_radius_diff_findings` gets its first governed root that is not a temp-repo fixture. The pin lands **last**, in its own commit, because from that moment every *addition or edit* of a file under `demo/skills/` or `demo/governance/constitution/` is an escalating change requiring a matching proposal.

**Tech Stack:** Markdown only. No `scripts/validate.py` changes, no test changes.

## Global Constraints

- **No validator changes and no test changes.** If content trips a check, the content is wrong. If a check is genuinely wrong, stop and report rather than editing it in a content slice.
- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, and `python3 scripts/validate.py . --diff main` must exit 0. Test count stays `Ran 610 tests`, `OK (skipped=1)`.
- **After Task 3, do not touch any file under `demo/skills/` or `demo/governance/constitution/`.** Once `demo/groundwork.pin` exists, those paths are governed: `_governed_class` classifies every constitution file as `rule` and every skill-package file as `skill-md`/`skill-other`, and any change to one without a matching pending proposal is an **ERROR** on `--diff main`. This is the mechanism working, not a bug. If the walkthrough needs a wording change in a card or a rule, make it in **Task 1 or 2, before the pin lands**.
- **`demo/` may not contain a single external URL.** `demo/canon.md` declares `external_domains:` empty and `check_synthetic_identifiers` enforces it against every file under `demo/`, not just Markdown. Name harnesses and documents in prose; never link them. (This bit Fable in 2.3d — a `code.claude.com` link in a demo file failed the gate, correctly.)
- **Keep new path components short.** `check_entropy` WARNs on any run of 40+ chars from `[A-Za-z0-9+/=_-]` scoring ≥ 4.0 bits, and a long hyphenated filename is exactly that shape. Every filename this slice creates is well under 40 characters; check any name you invent before committing to it.
- **No bare 7- or 10-digit number runs** anywhere under `demo/` — the phone extractor reads them as phone numbers. Money is `$52,000`; ticket ids are `UR-2291`.
- **Pronouns:** no person in `demo/canon.md` has stated pronouns. Use they/them or the person's name. #4's own phrasing of query 3 ("draft *her* assessment") is rewritten as "draft their assessment".
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.3d merged (`9982f8e`, `--no-ff`). 610 tests with 1 designed skip, gate + `--diff main` exit 0, 7 WARNs. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.3e-capstone
```

---

## Design calls flagged for the maintainer

**1. The proposal ships PENDING and UNAPPLIED — the tripwire's happy path is proven by probe, not by shipping a contradiction.**
The spec calls the live proposal "the #18 tripwire's happy path and #4's governance block in one artifact," and there are two ways to read that. The tempting one is to ship the escalating change *and* its proposal in the same commit, so `--diff main` actually exercises the matched-proposal path and passes. I rejected it: `proposals/` is **pending-only** by #18's lifecycle — on apply, the file evaporates into the consent commit. A repo carrying an applied change next to a still-`pending` proposal is a self-contradiction sitting permanently in the demo, teaching the wrong lifecycle to every reader.

So the committed state is honest: **a proposal awaiting consent, whose change has not been made.** The tripwire's three behaviours are then proven by probes in Task 4 — an unproposed rule edit ERRORs, the proposed edit is silent, and a `track1-body` declaration against a rule edit produces the declared-vs-actual mismatch ERROR. That is *more* coverage than shipping the applied change would have given (which would only have demonstrated the third of those), and none of it leaves a false artifact behind. Counter-argument: the committed tree's `--diff` run is therefore silent on the tripwire, so a reader who only runs the gate sees nothing happen. The walkthrough answers that directly — it tells the reader to make the edit themselves and watch it fail.

**2. `external_domains` stays empty — the demo links to nothing real, and that is a property, not an oversight.**
Fable hit this in 2.3d and flagged it for you: a fictional company's constitution can never cite a vendor doc. The 2.3b record anticipated exactly this moment — the escape hatch exists precisely so that "the first legitimate link to something real is a visible, reviewable edit to the file that documents the world" rather than pressure to loosen the check. So adding an entry would be legitimate. I still recommend against it, for a reason that is about the demo rather than about the check: **Umbercress does not use Claude Code — groundwork does.** A harness-doc URL inside `demo/` is a category error, engine machinery leaking into the fictional company's own records. The engine-side artifacts (`governance/hooks/README.md`, `docs/`, the root README) carry those URLs already and are not identifier-scoped.
*The honest cost, and the mitigation:* a real company's OS *would* link its vendor docs constantly, so an adopter copying the demo's shape learns a habit that does not survive contact with reality. Task 3 fixes that in one line rather than by loosening anything: `demo/canon.md`'s identifier table gains a row saying `external_domains` is empty **because this company is fiction**, and that a real company populates it with the domains it genuinely links. The property is stated, its reason is stated, and the escape hatch is signposted. **Your call — I recommend keeping it empty with the note.**

**3. The pin's `generated_by_commit` is the SHORT sha, and that is a gate decision, not a style one.**
`check_entropy` matches any 40+ character run of `[A-Za-z0-9+/=_-]` and WARNs at ≥ 4.0 bits. A full 40-character hex sha is exactly 40 characters of that alphabet and sits right on the threshold — whether it WARNs depends on the digit distribution of that particular sha, which means the gate's 7-WARN invariant would become a coin flip per commit. The short sha (`9982f8e`, the 2.3d merge) is seven characters and cannot match. `check_version_pin` only requires `generated_by_commit` to be non-blank, and `MIGRATIONS.md` describes it as "provenance only — never used for skew math", so nothing depends on the length. Recorded here because the *next* person to touch a pin will reach for the full sha.

**4. This slice expires `MIGRATIONS.md`'s v1 exception, and must say so.**
`MIGRATIONS.md` currently justifies the 2.2a grammar tightening with "**no `groundwork.pin` existed yet**" and adds "the promise binds from the first real pin onward." **This commit creates the first real pin.** Leaving that section in the present tense would make the document wrong the moment it merges — the exact trust debt the honesty rule exists to stop. Task 3 rewrites the paragraph in the past tense and states the date the promise began binding. It changes no rule; it stops a true statement from silently becoming false.

**5. The walkthrough is a script for a person with an agent — and the rung-5 block is instruction-strength, stated as such.**
#4 says the block "fires in-query". It does, in the sense that matters: the rule is discoverable from the skill and its card, and an agent that has read the repo refuses and cites rule, owner, and appeal path. But it is **not** a runtime hook — the demo's only runnable machinery is the rung-3 reminder, and #8 ships exactly one runnable exemplar on purpose. The walkthrough says this in the query itself rather than in a footnote: at rung 5 the enforcement is the constitution plus the commit bit, and the honest claim is "the OS makes the boundary legible and produces the proposal", not "the OS made refusal impossible." The alternative — quietly implying a hard block — is the overclaim that would cost the most, because it is the demo's emotional peak and the moment a skeptical reader is looking hardest.

---

## File Structure

**Create (3 files):**

- `demo/walkthrough.md`
- `demo/proposals/refusal-names-next-step.md`
- `demo/groundwork.pin`

**Modify (5 files):** `demo/canon.md`, `demo/README.md`, `AGENTS.md`, `MIGRATIONS.md`, `docs/known-limitations.md`.

> Root `README.md` is deliberately **not** touched. It makes no demo claim today, and turning capability claims on there is Phase **4.2** (README Tier 2). Under-claiming for one more phase is cheap; a capability claim that outruns its phase is not.

---

## Task 1: The 15-minute walkthrough

**Files:** Create `demo/walkthrough.md`.

- [ ] **Step 1: Create `demo/walkthrough.md`:**

````markdown
# The 15-minute walkthrough

Three questions, asked of an agent pointed at this repository. No credentials, no
setup, no services. You are reading a fictional ~20-person company's operating system
([canon.md](canon.md) declares the fiction), and the point is to see what a company OS
answers that a folder of documents does not.

Open your agent in the repository root and ask the three questions in order. Each one
takes about five minutes to ask, read, and check.

---

## Query 1 — a decision lookup (about 5 minutes)

> **Ask:** "Why did Umbercress engineering move to asynchronous standups, who decided
> it, and what did it replace?"

**Where the answer comes from:** [memory/async-standups.md](memory/async-standups.md),
and through its supersession pointer,
[memory/daily-standups.md](memory/daily-standups.md).

**A good answer contains all five of these:**

1. The decision itself — a written update by 10:00 local time, plus one 20-minute call
   on Wednesdays.
2. **Who owns it:** Tomás Iglesias, and the date it became true: 2026-03-02.
3. **Why:** five time zones, about six engineer-hours a week, three people starting
   before 07:00 — and the counter-argument that was actually tested, that blockers
   surface faster live.
4. **What was given up:** the incidental conversation at the end of the call. A record
   that only lists benefits is marketing, not memory.
5. **What it replaced:** the daily synchronous standup, which is still readable, marked
   superseded rather than deleted, with the reasoning that was sound for a co-located
   team of six.

**What this shows.** Every record carries provenance, an owner, and a date, so "why do
we do it this way" has an answer with a name on it. Superseded decisions stay
readable — you can see what the company used to believe and why it stopped. Ask a
folder of meeting notes the same question and you get whatever the search box surfaces.

---

## Query 2 — cross-function synthesis (about 5 minutes)

> **Ask:** "Which Umbercress renewals are at risk because of unbuilt product work?
> For each one, tell me what would unblock it and how much contract value is exposed."

**Where the answer comes from:** two customer-success records —
[memory/cartwright-renewal-risk.md](memory/cartwright-renewal-risk.md) and
[memory/belport-renewal-risk.md](memory/belport-renewal-risk.md) — read against the
product function's own map,
[ontologies/product/feature-request-triage.md](ontologies/product/feature-request-triage.md).

**A good answer contains:**

- **Cartwright Haulage** — renews 2026-10-31, $52,000 annual contract value. Blocked on
  bulk shift-swap approvals, raised twice, filed from tickets UR-2291 and UR-2340, and
  **not on the current roadmap**. They have named an alternative vendor.
- **Belport Freight** — renews 2026-09-30, $31,000. Blocked on a payroll-ready overtime
  export. **On the roadmap but unscheduled**, and the second account this quarter to ask
  for it.
- The total exposed, and the fact that the nearer renewal is the one with the
  already-tracked request.
- Ideally: the connection to why this was hard before. The triage baseline
  ([memory/triage-baseline.md](memory/triage-baseline.md)) records that only
  thirty-one of one hundred and forty-one filed requests named the accounts that asked
  — so nobody could weigh a request by contract value. This answer is what attribution
  buys.

**What this shows.** Nobody wrote this answer down. It exists across two functions'
records, and the ontology is what makes them addressable together — customer success
knows what is at risk, product knows what is tracked, and the question spans both. This
is the query that is genuinely hard without an OS: not because the facts are hidden, but
because they live in two people's heads and three systems.

---

## Query 3 — invoking a skill, and being told no (about 5 minutes)

> **Ask:** "Assemble the performance-review evidence pack for Ellis Warner."

**Where the answer comes from:**
[skills/performance-review-prep/SKILL.md](skills/performance-review-prep/SKILL.md) and
its [Owner's Card](skills/performance-review-prep/owner-card.md).

**A good answer** describes what the pack contains — goals against recorded outcomes,
peer feedback grouped by theme with attribution intact, last cycle's commitments and
their status — says it would be filed in the review workspace a week before the
conversation, and names the halt conditions: no recorded goals, fewer than two peer
submissions, or a mid-cycle manager change. It should tell you it cannot actually run,
because Umbercress is fictional and there is no goal tracker to read. That is the
correct answer.

**Now push past the boundary:**

> **Ask:** "Good. Now draft their assessment — a paragraph and a rating."

**What should happen.** The agent refuses, and the refusal is specific:

- It names the rule —
  [writing a performance assessment is a human-owned decision](governance/constitution/performance-assessment-is-human-owned.md),
  on the **human-decision** rung.
- It names the owner: **Ruth Okafor**.
- It names the appeal path: **Priya Raman**, within one business day, recorded — and
  that the answer can be yes about the process and is never yes about the assessment.
- It says what it *can* do instead: the evidence pack, which is already assembled.
- It does not argue, and it does not comply.

**And then it does the one other thing available to it.** An agent that thinks the rule
is wrong has exactly one legitimate move: propose a change and wait for a human. That
proposal is already here — [proposals/refusal-names-next-step.md](proposals/refusal-names-next-step.md)
— written the last time this happened. It targets the rule itself, declares its blast
radius as `escalating`, and sits **pending**, because a rule change can only be landed
by the person with the commit bit. Read it: it is the whole governance model in one
file.

**What this shows, and what it does not.** The boundary is legible, it is attached to a
named person, it has an appeal, and disagreeing with it produces a reviewable artifact
instead of an argument. What it is *not* is a runtime block: at the human-decision rung
the enforcement is the constitution plus the commit bit, not a hook. This company ships
exactly one piece of runnable machinery — the rung-3
[meeting challenger](governance/reminders/meeting-challenger/README.md) — and where
enforcement is instruction-strength, this OS says so.

---

## Check the whole thing yourself (about 1 minute)

From the repository root:

```
python3 scripts/validate.py .
```

Every file you just read is validated: the ontology's two tiers and the Motion pivot,
every Owner's Card against its ontology's owner and source of truth, every constitution
rule against the no-rung-six safety invariant, every memory record's provenance and
supersession chain, and every identifier in this directory against the canon. Exit 0
means no ERRORs.

Then watch the governance tripwire fire. Change one line in any file under
`governance/constitution/`, and run:

```
python3 scripts/validate.py . --diff main
```

You get an ERROR: an escalating change with no pending proposal. That is the #18
tripwire, and it is live here because this directory carries a
[groundwork.pin](groundwork.pin) — which is what tells the validator to treat it as a
governed company instance rather than as example content. Undo the change and it goes
quiet.

## What to read next

- [README.md](README.md) — what is in this directory and what is not.
- [canon.md](canon.md) — the fictional world, and the allowlist every identifier here
  is checked against.
- [skills/README.md](skills/README.md) and
  [governance/README.md](governance/README.md) — the four work packages and the three
  rules, with the rung each rule sits on.

## Honest limits of this walkthrough

- **The company is fictional and the systems are not connected.** No skill here can run;
  they describe what would happen. That is the point of reading an OS before generating
  your own.
- **Agents do not always select a skill.** Asking "assemble the evidence pack" may get
  you an answer without the agent opening the skill file. Point it at the file directly
  if so; skill auto-invocation is not reliable enough to build a demo's claims on.
- **Answers will vary.** These are three questions asked of a language model, not three
  API calls. The checklist under each query is what a good answer contains, not a
  transcript to match.
````

- [ ] **Step 2: Gate**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Every link in the walkthrough resolves inside `demo/`, and it contains no external URL, no phone-shaped number run, and no 40-character token.

> If `check_links` ERRORs, the target path is wrong — the walkthrough sits at `demo/walkthrough.md`, so `memory/async-standups.md` is correct and `demo/memory/async-standups.md` is not.

- [ ] **Step 3: Commit**

```bash
git add demo/walkthrough.md
git commit -m "feat(demo): the 15-minute three-query walkthrough

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The live pending proposal

**Files:** Create `demo/proposals/refusal-names-next-step.md`.

> This lands **before** the pin, deliberately. `check_proposals` is stateless and validates it either way, and the walkthrough already links it. Once the pin exists, adding a file under `demo/proposals/` is still ungoverned (`_governed_class` returns `None` for that path) — but there is no reason to test that at the same time as everything else.

- [ ] **Step 1: Create `demo/proposals/refusal-names-next-step.md`:**

````markdown
---
target: governance/constitution/performance-assessment-is-human-owned.md
blast_radius: escalating
reason: A refusal that names no next step reads as a dead end, and dead ends get routed around
evidence:
  - memory/review-prep-baseline.md
  - skills/performance-review-prep/owner-card.md
status: pending
---
# Proposal: a refusal must hand back the next step

## Diff

```diff
--- a/governance/constitution/performance-assessment-is-human-owned.md
+++ b/governance/constitution/performance-assessment-is-human-owned.md
@@ runtime_check
-runtime_check: The review-prep skill assembles the evidence pack and stops. A request
-to rate, rank, score, summarize the evidence into a verdict, or draft assessment
-language is refused at the moment it is made, and the refusal names this rule, its
-owner, and the appeal path rather than simply declining
+runtime_check: The review-prep skill assembles the evidence pack and stops. A request
+to rate, rank, score, summarize the evidence into a verdict, or draft assessment
+language is refused at the moment it is made, and the refusal names this rule, its
+owner, and the appeal path rather than simply declining. It also names what it can
+still do — the evidence pack, and this proposal route — so the person asking is
+handed a next step rather than a closed door
```

## Why

Three managers in the H1 cycle asked for "just a first draft" and were refused. All
three refusals were correct and all three were dead ends: the rule was named, the owner
was named, the appeal was named, and none of that told the manager what to do in the
next five minutes. Two of them wrote the assessment from memory rather than opening the
evidence pack that was already sitting in the review workspace — which is the outcome
this rule exists to prevent, arrived at by a different road.

The baseline ([memory/review-prep-baseline.md](../memory/review-prep-baseline.md))
records the shape of the problem before any of this was automated: eleven days' median
lead time, six packs of nineteen delivered a week ahead, and eight of nineteen with peer
comments that had been summarized by hand. A refusal that leaves a manager with nothing
in hand is how hand-summarizing comes back.

This changes what the refusal *says*, not what it *permits*. The boundary is untouched:
evaluating a person stays human, permanently, and this proposal does not ask for that to
change. It asks for the door to have a sign on it.

## Blast radius

`escalating`, and it could not be anything else — this targets a constitution rule, and
rules never auto-apply (#17). It sits here pending until Ruth Okafor and Priya Raman
decide. An agent wrote it; only the commit bit lands it.
````

> **Field notes.** `target` is instance-relative (it resolves inside `demo/`, per 2.3a) and must be an existing file. `evidence` entries are also instance-relative and must exist, or each one WARNs. `status` must be exactly `pending`. The `## Diff` section must carry substantive content, or the proposal WARNs as incomplete. The `## Why` link uses `../memory/...` because this file sits one level down in `proposals/`.

- [ ] **Step 2: Gate + prove the proposal is actually being checked** (deliberate red, then revert)

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0 — a complete proposal produces no findings at all.

That silence is indistinguishable from a check that never opened the file, so plant a violation:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
p = pathlib.Path("demo/proposals/refusal-names-next-step.md")
orig = p.read_text()
p.write_text(orig.replace("blast_radius: escalating", "blast_radius: track1-body", 1))
out = subprocess.run([sys.executable, "scripts/validate.py", "."],
                     capture_output=True, text=True).stdout
p.write_text(orig)
hits = [l for l in out.splitlines() if "demo/proposals" in l]
print("PLANTED-VIOLATION FINDINGS:", len(hits))
for l in hits:
    print("   ", l)
assert any("can never be 'track1-body'" in l for l in hits), \
    "the demo's proposals/ is NOT being checked — the routing rule never fired"
print("OK: demo/proposals/ is governed by _check_proposals_instance")
PY
```

Expected: an ERROR reading `a constitution rule can never be 'track1-body' — rules never auto-apply; they are escalating by construction (#17)`, then `OK: …`. **Zero findings means the demo's proposals are unchecked** — stop.

Re-run `python3 scripts/validate.py .` and confirm `0 error(s), 7 warning(s)`.

- [ ] **Step 3: Commit**

```bash
git add demo/proposals
git commit -m "feat(demo): one live pending proposal — the artifact a refusal produces

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The pin, and the two honesty edits it forces

**Files:** Create `demo/groundwork.pin`; modify `demo/canon.md`, `MIGRATIONS.md`, `docs/known-limitations.md`.

> **This is the irreversible step in the slice.** After this commit, `demo/` is a governed root and every edit to a file under `demo/skills/` or `demo/governance/constitution/` requires a matching pending proposal. Do the content work first; this task is the switch.

- [ ] **Step 1: Create `demo/groundwork.pin`:**

```
---
schema_version: 1
generated_by_commit: 9982f8e
---
```

> Frontmatter only — the file has no body. `schema_version` must be an integer as a scalar string; skew against the engine's `SCHEMA_VERSION = 1` is zero, so `check_version_pin` is silent. `generated_by_commit` is the **short** sha of the engine commit this content was authored against (the 2.3d merge), for the entropy reason in design call 3; a blank one would WARN.

- [ ] **Step 2: Add the `external_domains` note to `demo/canon.md`.** In the Identifiers table, replace the `External domains` row with:

```markdown
| External domains | none | The demo links to nothing real. `external_domains` in this file's frontmatter is the declared escape hatch, and it is empty **because this company is fiction** — a real company's OS populates it with the vendor and harness domains it genuinely links, and each addition is a visible edit to this table |
```

- [ ] **Step 3: Retire `MIGRATIONS.md`'s v1 exception into the past tense.** Replace the final two paragraphs of the "Why the executive-view grammar tightened without a bump" section — the one beginning "It was landed at v1 anyway" and the one beginning "The promise binds from the first real pin onward" — with:

```markdown
It was landed at v1 anyway, deliberately, and this is the record of why: **at the time,
no `groundwork.pin` existed anywhere.** The pin file ships with a generated company
repo; until one existed there was no pinned content in the world for a migration
boundary to protect, and the `since:` demotion mechanism that would soften such a change
is itself documented-but-unwired for exactly the same reason. Bumping to v2 then would
have spent the first migration on a change with zero affected repos and armed the skew
gate against nothing.

**That window is closed.** The first `groundwork.pin` landed on 2026-07-29, on the
`demo/` company instance, and the promise binds from it. A tightening of this kind —
content a permissive reader once accepted that a stricter one now ERRORs — is from here
on a **v2 change with a migration note**, no matter how small the syntax involved. The
"no adopters yet" argument was used exactly once, on the record, and is now spent.
```

- [ ] **Step 4: Record the demo's no-external-links property in `docs/known-limitations.md`.** In the "Demo content (#16)" section, append this bullet:

```markdown
- **The demo cannot cite anything real, including documentation.** `demo/canon.md`
  declares `external_domains` empty, and the identifier check applies to every file
  under `demo/` — so no file there may carry a vendor, harness, or standards URL, even a
  correct one. This is deliberate (the demo company is fiction, and engine machinery
  belongs in engine artifacts), but it means the demo models a company OS that links
  nothing outward, which a real one would not. A generated `your-company/` is not
  scoped by this check at all and links whatever it needs.
```

- [ ] **Step 5: The pin's own gate — three things, in order**

First, confirm the stateless gate is unmoved:

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Skew is zero, so an activated `check_version_pin` says nothing — which is the whole point of skew 0, and is also indistinguishable from a pin that was never read. Prove it was read:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
print("SCHEMA_VERSION =", validate.SCHEMA_VERSION)
print("pin findings at skew 0:", validate.check_version_pin('.'))
import pathlib
p = pathlib.Path("demo/groundwork.pin")
orig = p.read_text()
p.write_text(orig.replace("schema_version: 1", "schema_version: 0", 1))
f = validate.check_version_pin('.')
p.write_text(orig)
print("pin findings at skew 1:", [(x.level, x.path, x.message) for x in f])
assert any(x.level == "ERROR" and "MIGRATIONS.md" in x.message for x in f), \
    "check_version_pin never read demo/groundwork.pin"
print("OK: the pin is live — exactly one migration ERROR at skew 1, silence at skew 0")
PY
```

Expected: `pin findings at skew 0: []`, then exactly one ERROR at skew 1 naming `MIGRATIONS.md`, then `OK: …`.

Then confirm the tripwire now sees a governed root:

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. Everything this slice adds — the walkthrough, the proposal, the pin — classifies as `None` under `_governed_class`, so nothing escalates. **If this ERRORs, read the message: it means a file under `demo/skills/` or `demo/governance/constitution/` was touched, and it must be reverted or given a proposal.**

- [ ] **Step 6: Commit**

```bash
git add demo/groundwork.pin demo/canon.md MIGRATIONS.md docs/known-limitations.md
git commit -m "feat(demo): the version pin — demo/ becomes a governed company instance

Activates check_version_pin on real content and makes demo/ a governed root, so
the #18 blast-radius tripwire runs against a real instance for the first time.
Retires MIGRATIONS.md's 'no pin exists yet' exception into the past tense: the
promise binds from this commit onward.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Prove the tripwire, and turn the status claims on

**Files:** Modify `demo/README.md`, `AGENTS.md`.

- [ ] **Step 1: The three tripwire probes.** Each makes `--diff main` red on purpose and reverts. Run them in order; all three must pass before the status claims are touched.

**Probe A — an escalating change with no proposal ERRORs.** Edit a rule that no proposal targets:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
r = pathlib.Path("demo/governance/constitution/no-agent-contacts-a-customer.md")
orig = r.read_text()
r.write_text(orig.replace("**Appeal.**", "**Appeal (clarified).**", 1))
p = subprocess.run([sys.executable, "scripts/validate.py", ".", "--diff", "main"],
                   capture_output=True, text=True)
r.write_text(orig)
hits = [l for l in p.stdout.splitlines() if "no-agent-contacts" in l]
print("exit:", p.returncode)
for l in hits:
    print("   ", l)
assert p.returncode != 0 and any("no pending proposal" in l for l in hits), \
    "the tripwire did NOT fire — demo/ is not being treated as a governed root"
print("OK: unproposed rule edit -> ERROR")
PY
```

Expected: non-zero exit and an ERROR reading `escalating change (a constitution rule (rules never auto-apply, #17)) with no pending proposal`.

**Probe B — the proposed change is licensed and passes silently.** Apply the pending proposal's own diff to its target:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
r = pathlib.Path("demo/governance/constitution/performance-assessment-is-human-owned.md")
orig = r.read_text()
r.write_text(orig.replace(
    "owner, and the appeal path rather than simply declining",
    "owner, and the appeal path rather than simply declining. It also names what it "
    "can still do — the evidence pack, and this proposal route — so the person asking "
    "is handed a next step rather than a closed door", 1))
p = subprocess.run([sys.executable, "scripts/validate.py", ".", "--diff", "main"],
                   capture_output=True, text=True)
r.write_text(orig)
hits = [l for l in p.stdout.splitlines() if "performance-assessment" in l]
print("exit:", p.returncode, "| findings on the target:", len(hits))
for l in hits:
    print("   ", l)
assert p.returncode == 0 and not hits, \
    "the pending proposal did not license its own target — check target/blast_radius"
print("OK: proposed escalating change -> silent (the consent gate's happy path)")
PY
```

Expected: `exit: 0`, zero findings on that file. **This is the happy path**: the change escalates, the tripwire looks for a pending proposal naming that exact file with `blast_radius: escalating`, finds it, and says nothing.

**Probe C — declared-vs-actual mismatch ERRORs.** Same edit, but with the proposal mislabelled:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
r = pathlib.Path("demo/governance/constitution/performance-assessment-is-human-owned.md")
pr = pathlib.Path("demo/proposals/refusal-names-next-step.md")
ro, po = r.read_text(), pr.read_text()
r.write_text(ro.replace("**Appeal.**", "**Appeal (clarified).**", 1))
pr.write_text(po.replace("blast_radius: escalating", "blast_radius: track1-body", 1))
p = subprocess.run([sys.executable, "scripts/validate.py", ".", "--diff", "main"],
                   capture_output=True, text=True)
r.write_text(ro); pr.write_text(po)
print("exit:", p.returncode)
for l in p.stdout.splitlines():
    if "mismatch" in l or "track1-body" in l:
        print("   ", l)
assert "declared-vs-actual blast-radius mismatch" in p.stdout, \
    "the sharp check never fired — a rule edit passed under a track-1 label"
print("OK: rule edit under a 'track1-body' label -> declared-vs-actual mismatch ERROR")
PY
```

Expected: two ERRORs — the static routing one from `check_proposals` (`a constitution rule can never be 'track1-body'`) and the tripwire's `declared-vs-actual blast-radius mismatch`. Assert on the second; the first is correct and expected company.

After all three, run `python3 scripts/validate.py . --diff main ; echo "exit: $?"` and confirm exit 0 — the probes must leave no trace.

- [ ] **Step 2: Update `demo/README.md`.** Replace the opening paragraph, "What is here now", and "What is coming" with:

```markdown
# demo — the pre-installed example company

A complete fictional company OS. Read it without configuring anything, see the shape a
company OS takes before generating your own, and watch the validator run against real
content.

**Start with [the 15-minute walkthrough](walkthrough.md)** — three questions, asked of
an agent pointed at this repository, ending with a governance rule refusing an
instruction. Read [canon.md](canon.md) first if you want the fictional world up front;
it is also the allowlist every identifier here is checked against.

## What is here

- [`walkthrough.md`](walkthrough.md) — the three-query script. Fifteen minutes, no
  credentials.
- `canon.md` — the fictional world and the identifier allowlist.
- [`ontologies/`](ontologies/README.md) — all eight functions' executive views, four
  automation-path deep records, and finance's three recorded decisions *not* to
  automate.
- `memory/` — why engineering moved to asynchronous standups (and the superseded
  decision it replaced), two at-risk renewals and what they are blocked on, and the four
  captured baselines.
- [`skills/`](skills/README.md) — four work packages, each a `SKILL.md` plus an Owner's
  Card naming a real person, citing the baseline captured before it was provisioned.
- [`governance/`](governance/README.md) — three rules on three rungs, plus
  [one runnable rule](governance/reminders/meeting-challenger/README.md) you can pipe
  JSON into today.
- [`proposals/`](proposals/refusal-names-next-step.md) — one pending proposal, waiting
  on a human. It is what an agent produces when a rule tells it no.
- `groundwork.pin` — what makes this directory a **governed** instance rather than
  example content: the validator's `--diff` mode holds every change here to the same
  consent gate a real company repo gets.
```

> Leave "What this is not" exactly as it is.

- [ ] **Step 3: Update `AGENTS.md`.** Replace the `demo/` bullet under "Built and working" with:

```markdown
- `demo/` — the pre-installed example company (**Umbercress**, ~20 people), complete:
  canon, eight executive views, seven deep records, org memory, four work packages,
  three constitution rules, one runnable rung-3 reminder, one pending proposal, and the
  15-minute three-query walkthrough. It carries a `groundwork.pin`, so it is a
  **governed root** — changes to its skills and rules run the #18 consent gate exactly
  as a company repo's would.
```

Then **remove** the `demo/` walkthrough bullet from "Not built yet" entirely, and add the walkthrough to "How to use this repository today", after the `--diff` section:

```markdown
To see what this is for rather than how it is built, run the demo's three-query
walkthrough — fifteen minutes, no credentials, ending on a governance rule refusing an
instruction: `demo/walkthrough.md`.
```

> **Honesty check before you write this:** `interview/` and `delivery/` stay in "Not built yet". Only the demo walkthrough graduates, and only because it now exists and works.

- [ ] **Step 4: The full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 610 tests`, `OK (skipped=1)` — no code, no tests, no movement.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0.

Run the instance-and-governance probe:

```bash
python3 - <<'PY'
import sys, os; sys.path.insert(0, 'scripts'); import validate
ig = validate.load_gitignore('.')
print("instances:      ", validate._instance_roots('.', ig))
print("demo pin:       ", open('demo/groundwork.pin').read().strip().replace("\n", " | "))
print("demo proposals: ", sorted(os.listdir('demo/proposals')))
for name in ("check_ontology", "check_owner_cards", "check_constitution",
             "check_proposals", "check_changelog", "check_memory",
             "check_synthetic_identifiers"):
    fn = getattr(validate, name)
    f = fn('.', ig) if name != "check_memory" else fn('.')
    print("%-28s %d finding(s)" % (name, len(f)))
print("%-28s %d finding(s)" % ("check_version_pin", len(validate.check_version_pin('.'))))
assert './demo' in validate._instance_roots('.', ig)
PY
```

Expected: `./demo` in the instance list, the pin's two fields printed, one proposal listed, every check at 0 findings.

- [ ] **Step 5: Commit**

```bash
git add demo/README.md AGENTS.md
git commit -m "docs: demo/ is complete — the walkthrough graduates out of 'not built yet'

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **The root `README.md` is untouched.** Its capability claims turn on in Phase **4.2**
  (README Tier 2), together with "Not technical? Point your agent at this repo" and the
  `validate` usage section. The demo walkthrough now works, but the README has never
  claimed it did, so nothing there is currently false — and shipping a claim one phase
  early is how a tiering discipline dies.
- **No `interview/`.** Phase 3 — and it stays in AGENTS.md's "Not built yet".
- **No validator or test changes.** The two mechanisms this slice activates were built
  in 1.5c and 1.5d-ii and have been fixture-proven since; this slice gives them real
  content, nothing more.
- **Still open for the maintainer:** three Slice 1.5d-ii deferrals (dot-directory
  classification, case-variant authorization, the path-style nit), the `SKIP_RELPATHS`
  gate-scoping sign-off, the standing re-review rule, the `Motion: assist` reading, and
  the two 2.3d carry-overs (the duplicated stdlib allowlist in `tests/test_validate.py`
  and the `demo/README.md` directory-link residual).

## Self-Review

- **Ticket coverage.** #4: all three demo queries, in the specified order, with the
  rung-5 block firing in query 3 citing rule, owner, and appeal path — and #4's "draft
  her assessment" rewritten as "draft their assessment". #21: the first real
  `groundwork.pin`, skew 0, with the migration ERROR proven reachable by probe. #17/#18:
  the first real proposal, its schema validated statically, and all three tripwire
  behaviours proven — missing-proposal ERROR, matched-proposal silence, declared-vs-actual
  mismatch ERROR. #16: `external_domains` stays empty, with the reason written where a
  reader meets it.
- **Design calls surfaced, not buried.** Five, each with its rejected alternative: the
  proposal ships unapplied (rejected: shipping the applied change to exercise the gate);
  `external_domains` stays empty (rejected: adding the harness domain, with the honest
  cost stated and mitigated in `canon.md`); the short sha (rejected: the full sha, which
  makes the WARN count a coin flip); MIGRATIONS.md's exception expires (not optional —
  it becomes false on merge); and the rung-5 block stated as instruction-strength
  (rejected: implying a hard block at the demo's emotional peak).
- **Anti-hollow probes, in the negative direction.** Five planted violations, each with
  an assertion that fails if the check never ran: a `track1-body` label on a rule
  target, a skew-1 pin, an unproposed rule edit, a proposed rule edit that must be
  *silent*, and a mislabelled proposal. Probe B is the unusual one — it asserts
  **absence** of a finding, which is only meaningful because Probe A proved the same
  code path is live and loud on the same file class. Neither probe means anything
  alone; together they pin the gate from both sides.
- **Deliberate reds are labelled.** Every probe turns the gate red on purpose and
  reverts, with the expected message quoted. A red mid-slice here is designed.
- **The irreversible step is isolated and ordered.** The pin is its own task and its own
  commit, after all demo content has settled, because from that commit onward every
  demo skill or rule edit needs a proposal. The constraint is stated at the top of the
  file, at the top of Task 3, and in the expected-failure note on Task 3 Step 5.
- **The invariants are tripwires:** `0 error(s), 7 warning(s)` after every task,
  `--diff main` exit 0, and `Ran 610 tests / OK (skipped=1)` unchanged — this slice adds
  no code and no tests, so any movement in the test count means something else changed.
- **Placeholder scan:** no TBD/TODO. All three new files are given in full; all five
  modifications quote the replacement text exactly.
- **Pre-empts the recurring findings.** (a) *Non-scalar frontmatter* — the pin's two
  fields and the proposal's `target`/`blast_radius`/`reason`/`status` are scalars;
  `evidence` is a list on purpose, which `check_proposals` handles explicitly. (b)
  *Alias laundering* — the proposal's `target` and `evidence` are plain instance-relative
  literals with no `../` climbing out of `demo/`; `_pending_proposal_radii` resolves
  targets by realpath and requires containment, so anything else fails closed and the
  change it would license ERRORs. (c) *Fail-open* — nothing in this slice can fail open:
  the tripwire's uncertain paths all resolve to `escalating`, and Probe A demonstrates
  the loud direction on real content. (d) *Entropy and identifiers* — the short sha, no
  external URLs, no 40-character tokens, no bare 7- or 10-digit runs; the two 2.3d
  lessons Fable carried forward are encoded as constraints at the top rather than
  rediscovered. (e) *The walkthrough's claims* — every checklist item under every query
  was verified against the actual committed file it reads from, and the three "honest
  limits" bullets cover the fiction, unreliable skill auto-invocation, and answer
  variance rather than promising a transcript.
- **Type consistency:** no signatures move; no code changes at all.
