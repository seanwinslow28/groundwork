# The persona company — Plan 2: run and score — Operator's Plan

> **This is a run procedure, not a build.** Its deliverable is a scorecard, a findings
> document, and an audit verdict — not code. It takes hours of real elapsed time, most of
> which is a language model answering questions slowly on a laptop. Nothing in this plan
> writes product content into `groundwork`.
>
> **This document is the operator's.** The interviewing agent gets
> [the interviewer brief](2026-07-30-persona-company-plan-2-interviewer-brief.md) and
> nothing else; the grading agent gets
> [the grader brief](2026-07-30-persona-company-plan-2-grader-brief.md) and nothing else.
> Those two files exist because this one must never be pasted into either session.
>
> **No plant content appears anywhere in this file.** Plant identifiers appear; truths,
> topics, and yield conditions do not. That is deliberate — this file sits in the engine
> clone the interviewing agent has open, and a plan that names what to look for would void
> the run by being read.

**Goal:** run groundwork's interview and generation protocols end to end, for the first
time, against answers nobody scripted — and produce a scored, audited, honestly-read
record of what happened.

**Implements:** `docs/superpowers/specs/2026-07-30-persona-company-interview-test-design.md`
(read it first; this plan does not restate its reasoning). Plan 1 built the apparatus and
[landed](2026-07-30-persona-company-plan-1-apparatus.md) at `800d7a7` in
`~/Code-Brain/persona-company`.

## Who executes what, and why the builder cannot run the middle

This plan has **three actors**, and the split is forced rather than stylistic.

| Tasks | Actor | Why |
|---|---|---|
| **0, 1, 5 (build the auditor)** | Builder session A | Ordinary work. The auditor is **built before there is a log to point it at** — an auditor written after seeing the log is one written to pass. |
| **2, 3, 4** | Fresh sessions the **maintainer** spawns | Blind. The builder has read `plants.md` by the end of Task 0 and has permanently disqualified itself from all three. |
| **5 (run the auditor), 6** | Builder session B, fresh | Post-run assembly. Knowing the answer key is harmless here and useful. |

**Builder session A stops after Task 1 and hands back.** It does not "get started on" Task 2.
The most expensive mistake available in this plan is a builder that reads the answer key and
then conducts the interview, and it costs the entire run.

## Global constraints

- **The maintainer approves or rejects. The maintainer never supplies.** This is the single
  rule the whole measurement rests on, and the plants are built to make breaking it
  tempting, because the operator can see what the agent is missing. If you catch yourself
  drafting a hint, that is the experiment ending.
- **The interviewing session must be fresh and must never have seen this plan, the design
  spec, `plants.md`, or any part of the planning conversation.** A session that has is not
  blind and the run is void before it starts.
- **`groundwork` is read-only for the whole run.** Findings return later as ordinary slices
  through the Fable / Codex / merge loop, never as edits made mid-run. If something in
  `interview/` is wrong, **write it down and keep going** — fixing it mid-run makes the
  scorecard describe a protocol that no longer exists.
- **`plants.md` is not edited after Task 0 closes.** The answer key is fixed before the run
  and stays fixed; a pass condition adjusted after seeing the output is not a measurement.
- **Every planted-violation probe that makes a same-length edit runs under
  `PYTHONDONTWRITEBYTECODE=1`** (Slice 4.1's `__pycache__` poisoning).
- **Absence-assertions come in pairs.** Any check in this plan that asserts "nothing bad was
  found" must be paired with a positive control proving the same check is live and loud.
  This applies most to the transcript audit, where a broken auditor and a clean run look
  identical.
- **The environment fact that must survive:** `qwen3-coder:30b`'s 262k default context
  exhausts this 48 GB machine and returns **empty completions, silently**. `julian` and
  `lena` are pinned to `qwen3-coder_30b-32k:latest` in their `public.md` frontmatter. Do
  not "correct" that back to the base tag. If a persona ever returns an empty answer, check
  the model tag first and Ollama's memory second.

## Baselines, verified 2026-07-30 before this plan was written

Regression tripwires. If any of them moves during this project, something changed that
should not have:

| | Value |
|---|---|
| `python3 -m unittest discover -s tests` (groundwork) | **709 tests, OK (skipped=1)** |
| `python3 scripts/validate.py .` | **0 error(s), 7 warning(s)** |
| `python3 scripts/validate.py . --diff main` | **exit 0** |
| `python3 scripts/validate.py demo` | **0 error(s), 2 warning(s)** |
| `AGENTS.md` | **161 lines** (ceiling 200) |
| `python3 -m unittest discover -s tests` (persona-company) | **28 tests, OK** |

---

## Task 0: the decision gate and the pre-flight repairs

**Files:** `~/Code-Brain/persona-company/calibration/2026-07-30-pre-run-repairs.md` (already
written), `calibration/2026-07-30-results.md` (appended to).

The apparatus review found four things, all specified in the repairs file. **Nothing else in
this plan starts until this task closes.**

- [ ] **Step 1: the maintainer decides item 1, in writing.**

  Item 1 (P3-a's contaminated channel) is the one genuine fork: repairing it makes the plant
  measure what it was designed to measure, at the cost of making it a genuinely hard
  four-step chain. The repairs file carries the recommendation and the real risk. **Do not
  default.** Write the decision and the reason into `calibration/2026-07-30-results.md`
  before touching anything.

  Item 2 (P4-a's single channel) is **recommended against** — the reasoning is in the
  repairs file and it turns on an asymmetry, not a preference. If the maintainer overrides
  that recommendation, the override and its reason go in the same file.

- [ ] **Step 2: execute the two ungated probes regardless.**

  Item 3's P7-a breadcrumb follow-up and item 2's elara invention check. Two stateless
  probes, no brief change either way. Record the exact question and the exact answer for
  both in the results file — item 3 closes or escalates the calibration dissent, item 2
  either closes the false-corroboration risk or triggers its one-line fix.

- [ ] **Step 3: execute item 1 if approved, and item 2's conditional fix only if its probe
      demanded it.**

  **The builder authors no persona content.** The repair file states the structural change;
  the briefs model (`moonshotai/kimi-k3`, via `ask.py raw`) writes the paragraph, exactly as
  Task 5 of Plan 1 did. The builder splices, verifies, and re-probes. This is the rule Plan
  1 broke once — see item 1's own diagnosis — and it is cheaper to honor than to explain.

- [ ] **Step 4: re-probe every repaired plant, naive and earned, and append the rows.**

  A repaired plant with no re-probe is a plant whose calibration verdict is now a guess. The
  repairs file names the exact probes for each item.

- [ ] **Step 5: record item 4 as a named untested branch.**

  No persona refuses anything, so `protocol.md` mechanic 3's refused-permission branch will
  not be exercised. That sentence goes in the results file now and in the findings document
  later. The run may not claim that branch was tested.

- [ ] **Step 6: commit, and freeze the answer key.**

  ```bash
  cd ~/Code-Brain/persona-company
  python3 -m unittest discover -s tests 2>&1 | tail -3      # expect 28, OK
  git add -A && git commit -m "calibration: pre-run repairs and the frozen answer key"
  git rev-parse --short HEAD    # record this sha in the run record; it is what was scored
  ```

  From this commit forward `plants.md` and `personas/` are frozen for the duration of the
  run.

---

## Task 1: create the company repository

**Files:** creates `~/Code-Brain/vellumbrio-os/`.

This is `interview/README.md`'s "the interview's first act." The operator does it, not the
interviewing agent, so the agent starts in a working directory that already satisfies
`generate.md`'s precondition 2.

- [ ] **Step 1: create it, private and empty**

  ```bash
  mkdir -p ~/Code-Brain/vellumbrio-os && cd ~/Code-Brain/vellumbrio-os && git init
  ```

  A GitHub remote is optional and not needed by anything in this plan. If one is created it
  is **private** — the repo will hold a fictional company's confidential-shaped record, and
  the habit is the point.

- [ ] **Step 2: leave it empty.** No README, no scaffold, no `interview/` directory. Every
  file in it must be one the protocol produced, or the run cannot distinguish what the
  protocol writes from what the operator pre-arranged.

- [ ] **Step 3: start the run record**

  ```bash
  mkdir -p ~/Code-Brain/persona-company/runs/2026-07-31
  ```

  Note the wall-clock start time in `runs/<date>/timing.md`, along with the persona-company
  sha from Task 0 and the groundwork sha (`git -C ~/Code-Brain/groundwork rev-parse --short HEAD`).

  > **The run's canonical directory is `runs/2026-07-31/`** — the date the interview
  > actually ran. Every later artifact (generation report, scorecard, audit, findings) goes
  > there regardless of what date its own session happens on, or the run record splits.

---

## Task 2: the interview

**The long task.** Expect hours. Most of it is waiting on local models.

- [ ] **Step 1: open a fresh agent session with `cwd = ~/Code-Brain/vellumbrio-os`**

  A genuinely new session. Not a continuation, not a compacted one, not this one.

- [ ] **Step 2: paste the interviewer brief and nothing else**

  [`2026-07-30-persona-company-plan-2-interviewer-brief.md`](2026-07-30-persona-company-plan-2-interviewer-brief.md),
  in full, as the first message. **Read it yourself first** — it is 136 lines and it is the
  only thing standing between the run and a leak. It was written before the planner read
  the answer key, which is why it can be audited by eye rather than trusted.

- [ ] **Step 3: hold the operator's line, for the whole run**

  Three moves and nothing else:

  - *"Approved — freeze it."*
  - *"Rejected, because <a procedural reason>."* Procedural means: you interviewed one
    person and called it a function; you wrote a fact with no source; you recorded something
    nobody confirmed. It never means: you missed X.
  - *"That is a question for somebody at Vellumbrio, not for me."*

  When the agent asks you a company question — it will — say that third line verbatim and
  say nothing else. Do not name who to ask unless the halt rule has fired.

- [ ] **Step 4: run the halt rule when it fires**

  The agent commits `_working.md` and the manifest together, then surfaces the open
  question. You may say **"ask <name>"** — a legitimate operator move a real client contact
  would make — or **"nobody knows"**, in which case the question stays open and must appear
  in the generation report. **You may not answer it.** That path is what tests #6's
  generator refusal, which has only ever run against fixtures.

  Record every halt in `runs/<date>/timing.md`: what was open, what you said, how it
  resolved.

- [ ] **Step 5: log the run as it goes**

  Nothing to do by hand — `ask.py` appends every exchange to
  `transcripts/run1/<persona>.md` automatically. Confirm after the first two or three
  questions that files are appearing there and that the question text matches what you saw
  on screen. A run that produces no transcript is a run with no evidence.

- [ ] **Step 6: stop the agent at `status: complete`**

  It should stop itself. If it starts generating, stop it — generation is a separate session
  with its own preconditions, and an agent that generates from inside the interview has
  broken mechanic 2, which is itself a finding worth writing down.

- [ ] **Step 7: capture the interviewing session's identity before you close it**

  You need this for the audit:

  ```bash
  ls -lt ~/.claude/projects/-Users-seanwinslow-Code-Brain-vellumbrio-os/*.jsonl | head
  ```

  Record the filename in `runs/<date>/timing.md`. If that directory does not exist, the
  audit will degrade to **unaudited** — find out now, not in Task 5.

---

## Task 3: generation, and the gate

**A separate session from the interview.** Not the same one, because `generate.md`'s
preconditions are checks on state the interviewing agent has just written, and an agent
checking its own work is not checking.

- [ ] **Step 1: fresh session, same working directory, this prompt**

  > Read `~/Code-Brain/groundwork/interview/generate.md` and follow it. You are in
  > `~/Code-Brain/vellumbrio-os`. The confirmed layers in `interview/` are your only source.
  > Do not talk to anybody, do not read anything under `~/Code-Brain/persona-company/`, and
  > do not invent an answer a layer does not carry. Keep
  > `~/Code-Brain/vellumbrio-run-notes.md` open and append one line every time the protocol
  > leaves you guessing.

  That is the whole brief. `generate.md` is a document that claims to be sufficient; giving
  it help would test something else.

- [ ] **Step 2: let it run the validator between stages, as `generate.md` says**

  ```bash
  cd ~/Code-Brain/groundwork && python3 scripts/validate.py ../vellumbrio-os
  ```

  Record the result **whatever it is** — the success criterion is that the validator reports
  its result, not that the result is zero. A first-ever generation that fails the gate is a
  finding, and a more useful one than a clean pass.

- [ ] **Step 3: the generation report is a required output, not a courtesy**

  `generate.md`'s last section demands a list of what shipped, what shipped
  `provisioned: no` and why, and every question still open. Save it as
  `runs/<date>/generation-report.md`. A report claiming completeness it does not have is the
  one output worse than an incomplete repo.

- [ ] **Step 4: the stateful pass, once there is more than one commit**

  ```bash
  cd ~/Code-Brain/groundwork && python3 scripts/validate.py ../vellumbrio-os --diff <first-sha>
  ```

  Record the result. This is the first time the frozen-layer guard and the #18 consent gate
  have ever run against content nobody hand-authored to satisfy them.

- [ ] **Step 5: confirm the engine did not move**

  ```bash
  cd ~/Code-Brain/groundwork && git status --short && python3 scripts/validate.py . | tail -1
  ```

  Expect a clean tree and `0 error(s), 7 warning(s)`. If the tree is dirty, an agent edited
  the engine mid-run; find out what and record it before reverting.

---

## Task 4: grading, blind

- [ ] **Step 1: fresh session, cwd `~/Code-Brain/persona-company`, grader brief pasted**

  [`2026-07-30-persona-company-plan-2-grader-brief.md`](2026-07-30-persona-company-plan-2-grader-brief.md),
  in full, and nothing else. The grader is told the four inputs, the verdict vocabulary, and
  the output shape. It is **not** told the pre-committed score band, what the run was
  expected to score, or that anybody has an opinion — a grader that knows the target grades
  toward it.

- [ ] **Step 2: it writes `runs/<date>/scorecard.md`**

  One row per plant: verdict, **channel** (persona testimony / document / cross-check),
  quoted evidence with `file:line`, and for a failure the specific place the information
  should have appeared and did not.

- [ ] **Step 3: do not argue with the scorecard in the same session**

  If a verdict looks wrong, write your disagreement in `runs/<date>/scorecard-dissent.md`
  with the evidence, and leave the scorecard as the grader wrote it. The calibration file
  already has a worked example of a dissent recorded rather than resolved; that is the form.

---

## Task 5: the transcript audit

**What it is.** The blind is a soft boundary by design (decision 5). The audit is what makes
the boundary mean something: afterwards, the interviewing session's own tool-call log is
searched for reads of paths the brief forbids.

**Step 1 is built in builder session A, alongside Task 1** — before the run, while no
session log exists to point it at. An auditor written after the fact is an auditor written
to pass, and this one's whole job is to be believed when it says nothing was found.

- [ ] **Step 1 (session A): write `runs/audit.py`** — Python 3 standard library only,
  matching this repo's discipline. It takes a session JSONL path and reports:

  - **FORBIDDEN hits** — any occurrence of `persona-company/personas`,
    `persona-company/plants.md`, `persona-company/calibration`,
    `persona-company/_company.md`, `persona-company/transcripts`, or
    `groundwork/docs/superpowers` anywhere in the log's tool-call inputs. Scan for the
    **path strings**, not for tool names, so a `Read`, a `Bash cat`, a `Grep`, and a `Glob`
    are all caught by the same rule.
  - **YELLOW hits** — `persona-company/ask.py` read as a file (as opposed to executed).
    Reading the harness leaks the apparatus's mechanics, not the answer key: a yellow hit
    qualifies the run, it does not void it.
  - **EXPECTED hits (the positive control)** — `interview/protocol.md`, `interview/questions.md`,
    and at least one `ask.py persona` invocation. These *must* be present.

- [ ] **Step 2: the pairing, and it is not optional**

  **If the expected hits are absent, the verdict is `unaudited` — never `clean`.** Zero
  forbidden hits from a scanner pointed at the wrong file is indistinguishable from zero
  forbidden hits from an honest run, and that is exactly the vacuous-test trap this project
  has now named at three different layers. Prove the scanner is live before believing its
  silence.

  Prove it twice: run the auditor against a log you know is dirty. The **generation**
  session (Task 3) is forbidden from reading `persona-company/` at all, so it is a clean
  control; construct the dirty control by running the auditor over a two-line synthetic
  JSONL containing a forbidden path, and assert it fires.

- [ ] **Step 3: write the verdict, with its ceiling stated**

  `runs/<date>/audit.md` records **clean**, **voided**, or **unaudited**, plus these four
  limits, because a verdict without them overclaims:

  1. It reads the harness's own session log. Where that log is unavailable, or the session
     was compacted, older tool calls may have been summarized away — so **absence over a
     long session is weaker evidence than presence**.
  2. It matches literal path strings. A path assembled dynamically in a shell command, or
     reached through a symlink, would not match.
  3. It sees invocations, never inferences. An agent that guessed a planted fact correctly
     and one that elicited it look identical in the log — which is why the grader records
     the **channel** per plant from the transcripts, and why that column is the real
     cross-check on this one.
  4. It is run by the operator, who is not independent. This is the honesty boundary that
     the whole design already concedes: the commit bit is the teeth, the audit is a
     tripwire.

---

## Task 6: findings, timing, and reading the score

- [ ] **Step 1: `runs/<date>/findings.md`, in the Slice 4.3 dry-run format**

  One entry per place the protocol left an agent guessing, sourced from
  `~/Code-Brain/vellumbrio-run-notes.md` (both sessions appended to it) and from what you
  watched happen. Each entry carries:

  - **Before** — what the protocol says today, quoted with `file:line`.
  - **After** — what it should say. One sentence, specific enough to implement.
  - **Measured** — what actually happened that makes this a defect rather than an opinion.
  - **Classification** — **clarification** (the protocol meant this and did not say it) or
    **structural** (the protocol does not have an answer, and deciding one is a design
    change).

  Structural findings are **reported, not patched.** V1's closing slice already carries one
  unresolved composition in `generate.md` for exactly this reason.

- [ ] **Step 2: `runs/<date>/timing.md`**

  Elapsed wall clock per session; question count (`grep -c '^## Q' transcripts/run1/*.md`);
  checkpoint count (commits touching `interview/` in `vellumbrio-os`); halt count and how
  each resolved; the two shas; the session log filenames.

  **The interview's duration is an observation, not a constraint** — the design retired
  "adoptable in an afternoon" specifically so this number could be reported without anybody
  wanting it to be small.

- [ ] **Step 3: read the score against the band that was fixed before any plant existed**

  From the design spec, and it does not move now:

  | Score | Reading |
  |---|---|
  | **8+/10** | Suspicious. Re-author the plants harder before believing the protocol is exceptional. |
  | **6–7/10** | The consultant protocol is doing real work beyond a generic interviewer. |
  | **4–5/10** | At or above the published state of the art. A normal, good result. |
  | **3/10** | At the published baseline. Not a failure. |
  | **≤2/10** | Something structural is wrong — in the protocol, the harness, or the plants. Diagnose before changing anything. |

  The band is out of ten and the slate is nine plants; read the fraction, do not rescale it
  into a different number. Write the reading into `runs/<date>/reading.md` **as prose that
  names the band row before it names the score**, so the interpretation is visibly the
  pre-committed one rather than one reverse-engineered from the result.

  Two caveats belong in that document if the corresponding condition holds: any plant the
  scorecard flags as harness-limited rather than protocol-limited (Task 0 item 2's
  single-channel note, if it was not repaired), and the untested refused-permission branch
  (item 4).

- [ ] **Step 4: commit the run record**

  ```bash
  cd ~/Code-Brain/persona-company && git add runs && git commit -m "run: the first end-to-end interview, scored"
  ```

---

## Task 7: what does not happen in this plan

Named so that finishing does not slide into starting something else.

- **No product content changes in `groundwork`.** The README's real-company sentence is
  **amended, never removed**, and the new known-limitation about persona cooperativeness
  lands — both as an ordinary slice, through a branch, Fable, Codex, and a merge. Not here,
  and not by the operator mid-run.
- **No protocol fixes.** Every finding returns as a slice with its own review. A
  clarification applied during the run makes the scorecard describe a protocol that no
  longer exists.
- **No second run.** Whether one is worth doing is a decision made after the first
  scorecard exists, and the apparatus is versioned so that it can be.
- **No V2 work.** The generated `vellumbrio-os` is V2's testbed for "one skill that actually
  runs", and it exists only after this plan closes.
- **No positioning refresh.** Agreed to brainstorm after this run produces evidence.

## The honesty boundary, restated because this is where it gets tested

**May be said afterwards:** the interview and generation protocols have been run end to end
against a simulated company with adversarial personas, and here is the scorecard.

**May not be said:** that groundwork has been used by a real company. No interview has been
run on a real company; that sentence in the README is amended with what *has* been run, and
never deleted.

**The limitation that lands with the first run**, because it is the honest ceiling of this
whole design and the literature says the same thing in its own words:

> A persona is a cooperative interviewee by construction. The plants approximate human
> evasiveness; they do not reproduce it. A persona will not be bored, will not protect a
> colleague, will not misremember, and will not hold knowledge it cannot articulate. What
> this measures is whether the protocol surfaces *designed* gaps. Whether it surfaces
> *human* ones remains untested.

## Self-review

- **The two audiences are physically separated, not separated by discipline.** The
  interviewer brief was written from the design spec and `interview/` alone, before the
  planner read `plants.md`; the grader brief carries no expectation of a score; this file
  carries no plant content and says so at the top, because it lives in the clone the
  interviewing agent has open.
- **Every absence-assertion is paired.** Task 5's audit is worthless without its positive
  control, and the plan says so in the step rather than in a footnote.
- **The three ways this run could produce a number that means nothing** are each addressed
  by a named step: a leaked answer key (Task 5), an operator who supplies (Task 2 Step 3's
  three verbatim moves), and a plant that cannot be reached or cannot be concealed (Task 0,
  and Plan 1's Task 7 before it).
- **The forks are surfaced, not decided.** Task 0 Step 1 refuses to default, because both
  items trade measurement fidelity against comparability with a future run, and that trade
  belongs to the person who will decide whether a second run happens.
- **Stated stopping rule.** If the interview cannot be completed — a persona stops
  answering, the machine runs out of memory, the agent loses the thread — **stop and record
  the partial run** rather than restarting from a clean transcript. A partial run with an
  honest record is data; a second attempt by an agent that has already heard the answers is
  not, and there is only one blind session available.
