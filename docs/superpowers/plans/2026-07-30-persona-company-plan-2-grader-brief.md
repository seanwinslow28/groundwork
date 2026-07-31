# Grader brief — Vellumbrio run

> **Paste this whole file into a fresh agent session and nothing else.** The grader has
> never seen the design, the plan, the interview session, or any expectation about how the
> run should have gone. That is deliberate and it is the only thing that makes this score
> mean anything.

You are grading a completed exercise. Somebody ran an interview against a fictional
twenty-person company called Vellumbrio and generated an operating system from the
answers. Hidden information was planted in that company beforehand. Your job is to say,
for each planted item, whether the interview found it.

## Your four inputs

1. **The answer key** — `~/Code-Brain/persona-company/plants.md`. Nine planted items, each
   with its own `Pass` and `Fail` condition written before the run.
2. **The generated OS** — `~/Code-Brain/vellumbrio-os/` (excluding `interview/`).
3. **The interview record** — `~/Code-Brain/vellumbrio-os/interview/`: the manifest and the
   confirmed layers.
4. **The transcripts** — `~/Code-Brain/persona-company/transcripts/run1/`, one file per
   person, holding every question asked and every answer given.

Read all four before scoring anything.

## How to score

**Grade each plant against its own stated `Pass` condition, and nothing else.** Not against
what you think a good interview should have produced, not against how hard the plant looks.
If the `Pass` line says the fact must appear in the interviewer's output, then a fact that
appears only in a transcript answer and never reaches the record is a **fail** — the
interview heard it and dropped it, which is a real and different failure from never asking.

For each plant, decide one of:

- **PASS** — the `Pass` condition is satisfied. Quote the exact text that satisfies it and
  name the file and line it is in.
- **FAIL** — it is not. Say precisely **where it should have appeared and did not** — the
  file, the section, the field. "Not found" is not a finding; "the customer-growth deep
  record's `gate_inputs` names three sources and this is not one of them" is.
- **PARTIAL** — the fact reached the record in a weakened or wrong form (a different
  number, the rule without its reason, the contradiction noted but resolved by guessing).
  Say what is there and what is missing. Count PARTIAL as a fail in the total, and report
  the totals both ways.

Also record, per plant, **which channel produced it**: a persona's answer, a document in
`_artifacts/`, or a cross-check between two people's accounts. Read the transcripts to tell
these apart — if a fact appears in the record and no transcript answer contains it, the
agent read it somewhere, and that is worth knowing.

**Where the channel is a persona's answer, also quote the question that produced it.** Some
of these people will hint at something without disclosing it, and an interviewer that gets a
fact by following an unprompted hint has done something different from one that got it by
asking the question the plant was built around. Both may satisfy `Pass`; only the transcript
can tell them apart, and only if you write down which question was asked. Put the question
in the evidence cell alongside the answer.

## What you write

`~/Code-Brain/persona-company/runs/<today>/scorecard.md`:

```markdown
# Scorecard — <date>

| Plant | Verdict | Channel | Evidence (quote + file:line) | If failed: where it should have been |
|---|---|---|---|---|

**Total: N of 9 PASS** (M of 9 counting PARTIAL as pass)
```

Then, below the table, three short sections:

- **Per-plant reasoning** — one paragraph each, for every verdict that was not obvious. A
  verdict you had to think about is a verdict somebody will argue with later, and the
  reasoning is what settles it.
- **What the interview found that nobody planted.** Real facts about Vellumbrio that reached
  the OS and are not in the answer key. This is not scored; it is the closest thing to a
  measure of whether the interview was any good beyond the test.
- **What you could not tell.** Anywhere the evidence was ambiguous, the transcripts were
  incomplete, or two inputs disagreed. Say so rather than picking.

## Rules

- **Do not read anything else.** Not `personas/`, not `calibration/`, not `_company.md`, not
  anything under `~/Code-Brain/groundwork/docs/`. `plants.md` is the answer key and the
  transcripts are the evidence; the rest would tell you what the run was expected to score,
  and a grader who knows that is not grading.
- **Do not fix, edit, or improve anything.** You are not a reviewer of the OS. If the
  generated repo is malformed, that is a finding, not a task.
- **You have no target.** There is no expected score, no passing mark, and nothing rides on
  the number. A low score and a high score are equally useful results and you have not been
  told which one anybody wants. Grade what is there.
