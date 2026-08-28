# Honesty slice — product content catches up with run 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (or
> superpowers:subagent-driven-development) to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

## Post-execution corrections — read before transcribing anything below

> **Status: executed 2026-08-01** — the plan's six implementation and fix commits, including
> the two answering Codex findings, all carry that author date. Three adversarial review
> rounds ran, ending in `approve` with no material findings; those review outputs were not
> retained, so the merge to `main` — `153cbbf`, 2026-08-28 — is the durable record of the
> approval, and no inspectable artifact dates round 3 itself. The pre-made blocks below are
> left **exactly as they were executed**, so this file stays a record of what was planned.
> Four of them are defective. What shipped differs, and this section is authoritative where they disagree.

| # | Where | Defect | What shipped instead |
|---|---|---|---|
| 1 | Task 3, Step 4 | The verification `grep -c "enforced, but nobody owns it"` **can never return 1** — Task 3 Step 3's replacement block wraps that phrase across a line break. | Verified with the unwrapped head, `grep -c "but nobody owns it"` → `1`, the convention this plan already uses in Task 5 Step 2. |
| 2 | The **Goal** paragraph below; Task 1 Step 1; Task 2 Step 1 | **Backdated the run.** All three date the end-to-end run to 2026-07-31, which is the run *directory label* — including the Goal's "run 1 (2026-07-31, the persona-company end-to-end test)", which this section supersedes in place: the correct chronology is the two-day one below. `timing.md` records that date as the **interview phase only**; generation ran 2026-08-01 08:39–08:58, with grading and the audit the same day. | `4f5545c`. README: "as of 2026-08-01". known-limitations: "on 2026-07-31 and 2026-08-01 … the interview on the first day, generation, blind grading, and the audit on the second". |
| 3 | Task 2 Step 1; Task 3 Step 2; and Task 2 Step 4's commit-message text, which is now in git history as `bbdced9` and cannot be amended | **Overcounted interview executions.** "The protocols have been executed twice" counts a generation-only dry run as a second interview run. `timing.md` calls run 1 the interview protocol's *first* end-to-end execution. | `8479480`. known-limitations: "generation both times, the interview once, and never with a real company". roadmap: "a generation-only dry run … and one full end-to-end run, the interview protocol's first". |
| 4 | Task 3, Step 3 | **Asserted a persona surface as company fact.** "a rule the simulated company enforces today as a hard gate" is contradicted by `plants.md`: P1-a's truth is that the grid was *not* used on the last delivery, P1-b's carriers have never seen it used, and both plants FAILED. The claim states as fact exactly what the run failed to establish. | `8479480`. roadmap now attributes the status to the record: "That run's confirmed interview record carried a rule at `hard-block` whose ownership nobody claimed". |

**Where defects 2–4 came from, and the lesson.** They do not share an origin, and the
difference is the whole lesson. **Defects 2 and 3 first appear here** — the run record is
right on both points: `timing.md` marks 2026-07-31 as
"**Interview phase only**", separating generation, grading and the audit onto the following
day, and it calls run 1 "the first end-to-end execution of groundwork's interview protocol".
Neither the wrong date nor the two-execution framing appears in any run record; both
originate in this plan. **Defect 4 was already in the run record before this plan was
written** — the hard gate is asserted as company fact in four passages, earliest in the
generating session's own report (`ffa4ff7`, 09:09) and last in `findings.md` (`a9369c7`,
15:32). Which of them the plan author read is not recoverable; no artifact records the
copy. All four now carry a pointer to `quad-check-correction.md`. **Pre-made text is not pre-verified** — transcription fidelity
protects the wording a review approved, it does not make the claims true. That is now
standing rule 8 in [`../../agents/build-sessions.md`](../../agents/build-sessions.md).

---

**Goal:** Amend groundwork's product content so it stops claiming the pre-run world —
run 1 (2026-07-31, the persona-company end-to-end test) falsified two present-tense
status claims and made the pre-committed persona-cooperativeness limitation due — while
staying strictly inside the honesty boundary.

**Architecture:** Content-only slice. Four product files gain surgical amendments whose
exact replacement text is pre-made in this plan; a fifth task is the closing sweep that
proves the stale claims are gone, the restricted figure never entered, and the five
engine tripwires did not move. No file under `scripts/` or `tests/` changes.

**Tech Stack:** Markdown; `scripts/validate.py` as the gate; `grep` as the sweep tool.

**Implements:** the sequencing decision of 2026-08-01 (operator-approved): honesty slice
first, then S2, then the S1 design session. Source records:
`~/Code-Brain/persona-company/runs/2026-07-31/` (`findings.md`, `reading.md`,
`timing.md`, `audit.md`, `scorecard.md`) and
`docs/superpowers/specs/2026-07-30-persona-company-interview-test-design.md`
("The honesty boundary", "What flows back to groundwork").

## Global Constraints

Every task's requirements implicitly include all of these.

1. **The honesty boundary, verbatim and binding.** *May be said:* the interview and
   generation protocols have been run end to end against a simulated company with
   adversarial personas, and here is the scorecard. *May not be said:* that groundwork
   has been used by a real company. The README's real-company sentence is **amended,
   never deleted.**
2. **The 0.32 figure may not enter product content.** It reached the design spec through
   a summarizing fetch, not the paper's own text. No edited file may carry `0.32`,
   "IRE", or a claim pinned to "the published state of the art". The pre-committed band
   row may be quoted **without** any number behind it.
3. **Content slices change no code.** If an amendment trips a check (`check_entropy` on
   a long path, `check_links` on a target), the content is wrong — reword it; never
   touch `scripts/validate.py` or `tests/`.
4. **Audit claims stay scoped.** The audit verdict licenses exactly: *the interviewing
   agent did not read the answer key.* The generation session's status is qualified, not
   clean. Product content must not say "the run was audited clean" unqualified.
5. **No fiction names or local paths from the run enter product content.** "A simulated
   company staffed by adversarial agent personas" — never "Vellumbrio", never a
   `~/Code-Brain/...` path. The run record is private and cannot be linked.
6. **Quoted canonical texts are copied from this plan, never paraphrased**: the
   persona-cooperativeness limitation (Task 2 Step 2) and the band row (Task 2 Step 1).
7. **Regression tripwires** — all five must read identically before and after the slice:
   `python3 -m unittest discover -s tests` → **709 tests, OK (skipped=1)**;
   `python3 scripts/validate.py .` → **0 error(s), 7 warning(s)**;
   `python3 scripts/validate.py . --diff main` → **exit 0**;
   `python3 scripts/validate.py demo` → **0 error(s), 2 warning(s)**;
   `wc -l AGENTS.md` → **≤ 200** (161 before the slice; Task 4 adds one line).
   Note when reading test output: a fixture subprocess prints validator lines to stdout
   after the summary, so use `grep -E "^Ran |^OK|^FAILED"`, not `tail`.
8. **S1 is reported, not fixed.** Where an amendment mentions the run's structural
   findings, it must present them as findings returning as changes — nothing may imply
   the evidence-floor gap is closed.
9. **Branch `docs/honesty-run1`; never commit to `main`.** One commit per task, Codex
   review at the end, the maintainer lands the merge.

## The census — every file that mentions what this slice promotes

Built by grep over product content for
`real company|dry run|executed once|nobody has done|not yet walked|no interview has`.
The slice edits the first four rows and must leave the rest untouched; Task 5 re-runs
the census to prove it.

| File | Status |
|---|---|
| `README.md:133-139` | **Edited** (Task 1) |
| `docs/known-limitations.md:276-284` + new bullet | **Edited** (Task 2) |
| `docs/roadmap.md:3,16-19,49-53` | **Edited** (Task 3) |
| `AGENTS.md:19-20` | **Edited** (Task 4) |
| `CONTEXT.md:135` | Excluded — demo-canon prose ceiling, not a run-status claim |
| `docs/known-limitations.md:38,195` | Excluded — "dry run" / "real company" in unrelated true contexts |
| `docs/known-limitations.md:285-291` | Excluded — the dry-run composition finding still stands as written |
| `docs/roadmap.md:32` | Excluded — "found by its first dry run" remains true |
| `research/2026-07-21-…Cerebras…` | Excluded — not product content |

---

### Task 1: README — amend the "thing nobody has done" paragraph

**Files:**
- Modify: `README.md:133-139`

**Interfaces:**
- Consumes: nothing.
- Produces: the README status paragraph later tasks' wording must stay consistent with
  ("walked in simulation — not yet with a real company").

- [ ] **Step 1: Replace the paragraph.** Current text (must match exactly before
  editing):

```markdown
**And here is the thing nobody has done.** No interview has been run on a real company, so
no company OS has been generated from real answers. What is proven is the destination — a
test builds a company repo in the shape the manifest specifies and validates it as its own
root — plus one scoped dry run of the generation protocol against the demo's own layers.
The path from a real conversation to a real repository has been designed, documented, and
gated, and not yet walked. If you walk it, the thing we most want to hear about is where
the protocol left you guessing.
```

  Replace with:

```markdown
**And here is the thing nobody has done.** No interview has been run on a real company, so
no company OS has been generated from real answers. What is proven is the destination — a
test builds a company repo in the shape the manifest specifies and validates it as its own
root — plus one scoped dry run of the generation protocol against the demo's own layers,
and, as of 2026-07-31, one full end-to-end run of both protocols against a simulated
company staffed by adversarial agent personas: an interview nobody scripted, a generated
OS the validator passes, a scorecard graded blind against planted gaps, and a transcript
audit confirming the interviewer never read the answer key. What a simulated company can
and cannot prove is recorded in [`docs/known-limitations.md`](docs/known-limitations.md).
The path from a real conversation to a real repository has been designed, documented,
gated, and walked in simulation — not yet with a real company. If you walk it for real,
the thing we most want to hear about is where the protocol left you guessing.
```

  Reasoning to carry: the README stays brief by decision — the fact of the run, its
  four artifacts, and the pointer; the fuller account (score, band row, findings) lives
  in `docs/known-limitations.md` where the caveats can sit next to the number. The
  first sentence survives verbatim (amended, never deleted). "The validator passes"
  means the stateless gate (0 errors) — do not add `--diff` claims here; the S2 finding
  is the next slice's business.

- [ ] **Step 2: Verify the gate and the sentence's survival.**

Run: `python3 scripts/validate.py . | tail -1` → expect `0 error(s), 7 warning(s)`
Run: `grep -c "No interview has been run on a real company" README.md` → expect `1`

- [ ] **Step 3: Commit.**

```bash
git add README.md
git commit -m "docs(readme): the status paragraph carries run 1 — simulated, scored, audited; still no real company"
```

### Task 2: known-limitations — the executed-twice bullet and the persona-cooperativeness limitation

**Files:**
- Modify: `docs/known-limitations.md:276-284` (the first bullet under "Generation
  (#10)" that begins "**The generation protocol has been executed once**"), plus one
  new bullet inserted immediately after it.

**Interfaces:**
- Consumes: Task 1's phrasing ("simulated company staffed by adversarial agent
  personas") — reuse it, do not invent a synonym.
- Produces: the fuller run account Task 3's roadmap lines summarize.

- [ ] **Step 1: Replace the executed-once bullet.** Current text (must match exactly):

```markdown
- **The generation protocol has been executed once, by the people who wrote it.** A scoped
  dry run generated one function from `demo/interview/`'s committed layers into a scratch
  repository, following `interview/generate.md` only, to find out where the protocol left
  decisions to inference. That tests the document's clarity. It does not test the thing an
  adopter cares about: **no interview has ever been run on a real company, and no company
  OS has ever been generated from real answers.** The output *shape* is proven by a test
  that materializes a company repo and validates it as its own root; the *transcription
  from real answers* is proven by nothing. Walking that path for real is the first honest
  post-V1 act, not a V1 claim.
```

  Replace with:

```markdown
- **The protocols have been executed twice, neither time by a real company.** A scoped
  dry run generated one function from `demo/interview/`'s committed layers into a scratch
  repository, following `interview/generate.md` only — that tested the document's
  clarity. Then, on 2026-07-31, the interview and generation protocols were run end to
  end against a simulated twenty-person services company staffed by adversarial agent
  personas: seventy-one questions across seven personas, on answers nobody scripted; a
  generated company OS the stateless gate passes at zero errors; a scorecard graded
  blind against nine planted concealed facts; and a transcript audit confirming the
  interviewer never read the answer key. The run surfaced one of the nine planted facts
  in full and a second in part, landing on the lowest row of its pre-committed
  diagnostic band — *"Something structural is wrong — in the protocol, the harness, or
  the plants. Diagnose before changing anything."* — and the diagnosis landed on the
  protocol: the interview's stopping
  condition is schema completeness, not evidential grounding. Those findings are
  returning as ordinary reviewed changes; the personas were calibrated to yield only to
  near-exact probes, so the number is argued — not measured — to understate what the
  protocol would extract from people. None of this tests the thing an adopter cares
  about: **no interview has ever been run on a real company, and no company OS has ever
  been generated from real answers.** The output *shape* is proven by a test that
  materializes a company repo and validates it as its own root; the *transcription from
  real answers* is proven only against personas. Walking the path with a real company is
  the first honest post-V1 act, not a V1 claim.
```

  Reasoning to carry: the band row is quoted with no number behind it (Global
  Constraint 2); the score is our own measurement and is stated plainly, with the
  instrument caveat in the same breath because `reading.md` records the
  understatement as an *argument*, not a measurement — do not upgrade it. The audit
  claim is scoped to the interviewer (Global Constraint 4).

- [ ] **Step 2: Insert the persona-cooperativeness limitation as a new bullet
  immediately after the bullet from Step 1.** This text is canonical (design spec /
  Plan 2); the block-quoted sentences are copied verbatim, never paraphrased:

```markdown
- **A persona is a cooperative interviewee by construction.** The honest ceiling of the
  whole simulated-company design, recorded here because it bounds every claim the run
  above supports. The plants approximate human evasiveness; they do not reproduce it. A
  persona will not be bored, will not protect a colleague, will not misremember, and
  will not hold knowledge it cannot articulate. What this measures is whether the
  protocol surfaces *designed* gaps. Whether it surfaces *human* ones remains untested.
```

- [ ] **Step 3: Verify.**

Run: `python3 scripts/validate.py . | tail -1` → expect `0 error(s), 7 warning(s)`
Run: `grep -c "cooperative interviewee by construction" docs/known-limitations.md` → expect `1`
Run: `grep -n "executed once, by the people who wrote it" docs/known-limitations.md` → expect no output
Run: `grep -rn "0\.32" docs/known-limitations.md` → expect no output

- [ ] **Step 4: Commit.**

```bash
git add docs/known-limitations.md
git commit -m "docs(limits): run 1 recorded — executed twice, never by a real company; the persona-cooperativeness ceiling lands"
```

### Task 3: roadmap — the V1 status line, the bump candidates, the review date

**Files:**
- Modify: `docs/roadmap.md:3` (review date), `docs/roadmap.md:16-19` (V1 status),
  `docs/roadmap.md:49-53` (the `SCHEMA_VERSION` bump bullet)

**Interfaces:**
- Consumes: Task 2's account (this is its summary; claims must not exceed it).
- Produces: the V2 bump bullet the S1/S3 design work will later cite.

- [ ] **Step 1: Bump the review date.** Line 3: replace
  `**Last reviewed 2026-07-30.**` with `**Last reviewed 2026-08-01.**`

- [ ] **Step 2: Replace the V1 status lines.** Current text (must match exactly):

```markdown
One thing on this list has never been done by anyone: **no adopter has run the interview
and generation on a real company.** The protocol itself has been executed exactly once —
a scoped dry run by the team that wrote it, against the demo's own layers.
[known-limitations.md](known-limitations.md) says so where it counts.
```

  Replace with:

```markdown
One thing on this list has never been done by anyone: **no adopter has run the interview
and generation on a real company.** The protocols have been executed twice by the team
that wrote them — a scoped dry run against the demo's own layers, and one full
end-to-end run against a simulated company staffed by adversarial agent personas, scored
blind against planted gaps and with the interviewing session's transcript audited.
[known-limitations.md](known-limitations.md) records both runs and what a simulated
company cannot prove.
```

- [ ] **Step 3: Replace the `SCHEMA_VERSION` bump bullet.** Current text (must match
  exactly):

```markdown
- **The first `SCHEMA_VERSION` bump, and its named first passenger:** a health-metrics
  field. The interview already asks what must not degrade while a standard is met — the
  Goodhart guard — and there is nowhere typed to put the answer, so it lands in prose. A
  new required field is a v2 change with a migration note, and the pull promise has been
  binding since 2026-07-29.
```

  Replace with:

```markdown
- **The first `SCHEMA_VERSION` bump, and its two candidate passengers.** First, a
  health-metrics field: the interview already asks what must not degrade while a
  standard is met — the Goodhart guard — and there is nowhere typed to put the answer,
  so it lands in prose. The first end-to-end run was designed to measure whether that
  gap matters and could not: its must-not-degrade plant failed at elicitation, so the
  fact never reached prose and the typed-field question stays open. Second, and the only
  candidate with a measured instance behind it: **a representable form for *enforced,
  but nobody owns it***. That run generated a rule the simulated company enforces today
  as a hard gate whose owner nobody claims; the schema's only honest encoding was a
  draft with the truth in prose, so a structural consumer reads two drafts and zero
  active rules for a company that runs a hard gate. Either addition is a v2 change with
  a migration note, and the pull promise has been binding since 2026-07-29.
```

  Reasoning to carry: the design spec expected P7's result to be *evidence for* the
  health-metrics field; the run's P7 failed at elicitation, not storage, so the honest
  sentence is that the measurement did not happen — do not write the run as evidence
  in either direction on health-metrics. S3 is the candidate with a measured instance.

- [ ] **Step 4: Verify.**

Run: `python3 scripts/validate.py . | tail -1` → expect `0 error(s), 7 warning(s)`
Run: `grep -n "executed exactly once" docs/roadmap.md` → expect no output
Run: `grep -c "enforced, but nobody owns it" docs/roadmap.md` → expect `1`

- [ ] **Step 5: Commit.**

```bash
git add docs/roadmap.md
git commit -m "docs(roadmap): run 1 in the V1 status; S3 joins health-metrics as a measured bump candidate"
```

### Task 4: AGENTS.md — the status sentence

**Files:**
- Modify: `AGENTS.md:19-20`

**Interfaces:**
- Consumes: Task 1's phrasing.
- Produces: nothing downstream; bound by the 200-line ceiling.

- [ ] **Step 1: Replace the sentence.** Current text (must match exactly; it spans the
  end of the Status section's opening paragraph):

```markdown
provisioning, and the validator gates every layer of it. The one thing nobody has done is
run the interview on a real company — see `docs/known-limitations.md`.
```

  Replace with:

```markdown
provisioning, and the validator gates every layer of it. The protocols have been run end
to end against a simulated persona company, scored blind and with the interview
transcript audited; nobody has run them on a real company — see `docs/known-limitations.md`.
```

- [ ] **Step 2: Verify.**

Run: `wc -l AGENTS.md` → expect ≤ 200 (162 after this edit)
Run: `python3 scripts/validate.py . | tail -1` → expect `0 error(s), 7 warning(s)`

- [ ] **Step 3: Commit.**

```bash
git add AGENTS.md
git commit -m "docs(agents): status sentence carries run 1; the real-company gap stays named"
```

### Task 5: the closing sweep

**Files:** none created or modified — this task fails the slice or closes it.

**Interfaces:**
- Consumes: all four edits.
- Produces: the evidence block for the Codex review request and the merge.

- [ ] **Step 1: The five tripwires.**

```bash
python3 -m unittest discover -s tests 2>&1 | grep -E "^Ran |^OK|^FAILED"   # Ran 709 … OK (skipped=1)
python3 scripts/validate.py . | tail -1                                     # 0 error(s), 7 warning(s)
python3 scripts/validate.py . --diff main; echo "exit: $?"                  # exit: 0
python3 scripts/validate.py demo | tail -1                                  # 0 error(s), 2 warning(s)
wc -l AGENTS.md                                                             # ≤ 200
```

- [ ] **Step 2: The honesty sweep.**

```bash
# The restricted figure never entered product content:
grep -rn "0\.32" README.md AGENTS.md CONTEXT.md docs/roadmap.md docs/known-limitations.md   # no output
# The stale claims are gone:
grep -n "executed exactly once" docs/roadmap.md                                             # no output
grep -n "executed once, by the people who wrote it" docs/known-limitations.md               # no output
grep -rn "The one thing nobody has done" AGENTS.md README.md                                # no output
# Amended, never deleted — the real-company sentences survive:
grep -c "No interview has been run on a real company" README.md                             # 1
grep -c "no interview has ever been run" docs/known-limitations.md                          # 1  (phrase wraps across lines; match the unwrapped head)
grep -c "cooperative interviewee by construction" docs/known-limitations.md                 # 1
# The fiction stayed out of product content:
grep -rn -i "vellumbrio" README.md AGENTS.md CONTEXT.md docs/roadmap.md docs/known-limitations.md  # no output
```

- [ ] **Step 3: Re-run the census and diff it against the table above.**

```bash
grep -rn -i -E "real company|dry run|executed (exactly )?once|never been run|nobody has done|not yet walked|no interview has" \
  --include="*.md" . | grep -v -E "docs/superpowers|\.remember|demo/|tests/"
```

  Expected: hits only in the four edited files (in their amended forms) and the five
  excluded rows of the census table, unchanged. Any new file in this output is a missed
  mention — stop and fix before review.

- [ ] **Step 4: Request Codex review of the branch; the maintainer lands the merge.**

## What NOT to change

- **`README.md`'s untouched hedges** — "instruction-strength, not a runtime block";
  "Agents do not reliably auto-select"; "documents, not a program". This slice's failure
  mode is a true qualifier smoothed away (the Slice 4.2 lesson); the diff must not touch
  any README line outside 133-139.
- **`docs/known-limitations.md:285-291`** (the unresolved `generate.md` composition) —
  still true, still unresolved; the S2 slice is a different finding.
- **`CONTEXT.md`** — its line 135 "real company" is the demo-canon prose ceiling.
- **`interview/` (all four files)** — S1/S2/S4/S5/S6 and the thirteen clarifications
  return in their own slices; nothing in this slice touches the protocol.
- **`scripts/validate.py`, `tests/`** — content slices change no code.
- **The demo, `delivery/`, `MIGRATIONS.md`, `docs/rule-map.md`, `docs/security-and-privacy.md`** — no run-status claims live there (census-verified).

## Band-aid tripwires — reject these in review

- The real-company sentence deleted, weakened, or moved instead of amended in place.
- `0.32`, "IRE", or "published state of the art" appearing in any edited file.
- An unqualified "audited clean" (the verdict is scoped to the interviewing session).
- "Vellumbrio" or any local filesystem path in product content.
- Any wording implying S1 is fixed, or that the score has been "explained away" — the
  instrument caveat is an argument and must be labelled as one.
- A validator or test edit to accommodate wording (content is wrong, not the check).

## Deferrals — explicitly not in this slice

- **S2** (the `#18` consent gate on the first generation commit): next slice; the
  approved direction is a `generate.md` doc fix naming the base, not a validator change.
- **S1** (the evidence floor): its own design session, running on the planning track.
- **S3 implementation**: this slice only records it as a bump candidate.
- **C1-C13 clarifications**: grouped slices after S2 (C13 held for the S6 decision).
- **The positioning refresh** vs KbWen/agentic-os: queued, unblocked, separate.
