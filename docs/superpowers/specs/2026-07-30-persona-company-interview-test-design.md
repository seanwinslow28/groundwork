# The persona company — design

> **Workbench artifact, not product content.** This is the design for groundwork's first end-to-end execution of the interview and generation protocols, against a synthetic company staffed by adversarial agent personas. It lives under `docs/superpowers/` and is superseded by the implementation plan it feeds. Date: 2026-07-30.

## Why this exists

Slice 4.3's success-criteria audit found that V1's first criterion — *the adopter's required path runs end-to-end* — is only partially met. The path exists, its **output shape** is proven (`TestGeneratedCompanyRepo` materializes a company repo and validates it as its own root), and a scoped dry run executed `interview/generate.md` once. What has never happened is an interview: **nobody has ever answered `interview/questions.md` and had an operating system generated from their answers.**

The obvious discharge is to interview a real company. That is not available — this is a solo operation, and spending weeks recruiting a subject costs more than the weeks are worth. The chosen alternative is to build the subject: a synthetic services business staffed by agent personas who behave the way real interviewees behave, which is to say **badly** — contradicting each other, deflecting the embarrassing question, and stating rules they wish were true.

This is not a substitute for a real adopter and this document never treats it as one. It is a way to put the protocol under load before a real person is exposed to it.

## Decomposition — what this spec does and does not cover

The original request bundled five things. They are not one project.

| | What it is | Status |
|---|---|---|
| **A** | The persona company — fiction, cast, public and hidden briefs | **This spec** |
| **B** | The persona runtime — how a persona is invoked and stays consistent | **This spec** |
| **C** | The interview walk — the agent interviewing them, producing an OS and findings | **This spec** |
| **D** | V2's walking skeleton — one skill that actually runs | Separate; depends on C's output |
| **E** | A company of agents — personas as staff, not subjects | Documented direction; depends on D |

A + B + C is one coherent project because they share one deliverable: a scored run. **D is deliberately excluded** — it operates on the generated OS, and designing it before that OS exists means designing against an imagined artifact. E is recorded at the end of this document as a named direction with its dependencies stated.

**The cost framing that matters:** this is not a detour from V2. The generated company OS *is* V2's testbed — "one skill that actually runs" needs a company with real data, a real constitution, and a real Owner's Card to run under, and V2 would otherwise have to invent one.

## Decisions locked (maintainer, 2026-07-30)

1. **The goal is testing elicitation, not mechanics.** Success is measured by whether the protocol surfaced what the personas would not volunteer — not by whether a repository got generated. Cooperative personas answering straight would have tested transcription and said nothing about whether the consultant protocol earns its complexity.
2. **The interviewing agent queries personas directly; the maintainer approves at layer checkpoints.** This uses a real feature of `interview/protocol.md` rather than inventing a loop. Rejected: relaying every answer by hand (slow across a full interview, and the relayer unconsciously tidies up the evasiveness the test depends on), and fully autonomous (a run that goes wrong early burns the whole session unseen).
3. **Persona prompts are portable, human-readable artifacts.** A persona must be pasteable into Gemini, ChatGPT, Claude, or a browser tab and produce a real response. This is the requirement that eliminates the runtime: a persona is a file, and running one is assembling a prompt and sending it somewhere.
4. **The test apparatus lives in its own versioned repository.** Three repos: the engine (untouched), the personas repo, the generated OS. Versioning the apparatus is what makes a second run after a protocol change comparable to the first — the only way to tell whether a protocol change actually improved elicitation.
5. **Blinding is a soft boundary plus a transcript audit.** The interviewing agent could read a hidden brief; instead of pretending otherwise, a read of a private path voids the run. This is groundwork's own doctrine — the commit bit is the teeth, the validator is a tripwire — applied to its own test. Rejected: a process wall (airtight, but buys protection against a failure the audit already catches), and no blind at all (an interviewer that knows the answer key cannot test elicitation).
6. **The company is a services or agency business, roughly twenty people.** Every worked record in groundwork was built against Umbercress, a B2B SaaS. A services business stresses the schema where it is most likely to strain: "product" is thin, "delivery" is the whole company, and accountability sits with account leads rather than function heads. A second finding for free — whether the eight-function template is genuinely general or quietly SaaS-shaped.
7. **The company cannot be Umbercress.** Its OS already exists in `demo/`, so an interviewing agent could read the answers instead of eliciting them. New fiction, new canon, and the name gets the same treatment Umbercress got in Slice 2.3b: web-searched before adoption to confirm it is not a real business, with an RFC-reserved domain.
8. **Approach A — files plus a thin CLI.** Rejected: a subagent per persona (every persona would be Claude, prompts would not be portable, and the blind weakens inside one process), and a full simulation harness (that is direction E, and building it before a single interview has run means designing a simulator for a test never performed).

## Research grounding

Searched 2026-07-30 for comparable work published April 2026 onward. The design was arrived at independently and lands on the same three principles a peer-reviewed evaluation environment uses, which is corroboration rather than coincidence — and the literature supplies one number that changes what we expect.

> **Provenance caveat, per the Slice 3.2 lesson.** The ReqElicitGym figures and phrasings below reached this document through a **summarizing fetch**, not through the paper's own text. A fetch result is evidence *about* a document, not the document. The figures are strong enough to set expectations in a workbench spec, and **none of them may enter product content — the README, `docs/`, or any adopter-facing claim — until re-verified against the paper itself.** Same rule that stopped a reconstructed hooks quote shipping in 2.3d.

### The method has published precedent

[**ReqElicitGym**](https://arxiv.org/html/2602.18306) is an evaluation environment for interview competence in conversational requirements elicitation. Its simulated interviewee — the *oracle user* — rests on three principles this design adopts by name:

- **Groundedness.** The oracle reveals only what is annotated as ground truth. Here: the hidden brief bounds what can be revealed, and a persona may not invent.
- **Passive response.** A controlled, non-proactive style; nothing is volunteered unless asked. Here: the yield condition.
- **Context awareness.** Consistency across turns using full conversation history. Here: prior transcript prepended on every call.

It reports **Cohen's κ 0.73** for the oracle user against real users — substantial behavioral alignment, which is the strongest available justification that this method measures something real. It also states this design's ceiling in its own words: the oracle is "a controlled abstraction of real-world requirements elicitation" and "may reduce overall elicitation difficulty."

### The number that recalibrates the whole experiment

**Even top-performing models achieve only 0.32 IRE** — the proportion of ground-truth implicit requirements successfully elicited. State-of-the-art interviewers miss roughly two-thirds of what is hidden.

Without this number in hand, a run scoring 3 of 10 reads as a catastrophe and triggers "fixes" to a protocol that is performing at the published bar. **So the score band is pre-committed here, before any plant is written:**

| Score | Reading |
|---|---|
| **8+/10** | Suspicious. The plants were too easy; re-author them harder before believing the protocol is exceptional. |
| **6–7/10** | The consultant protocol is doing real work beyond a generic interviewer. |
| **4–5/10** | At or above the published state of the art. A normal, good result. |
| **3/10** | At the published baseline. Not a failure. |
| **≤2/10** | Something structural is wrong — in the protocol, the harness, or the plants. Diagnose before changing anything. |

This is the same discipline as naming a deliberate red before running it: the interpretation is fixed while nobody is attached to the outcome.

Two further transferable findings. Interviewers **overwhelmingly prefer probing over clarification**, even where clarification is what resolves ambiguity — `interview/protocol.md` should be checked against that specific bias. And their **turn-discounted key-question metric** rewards asking important questions early, which is question-efficiency rendered as a measurement.

### Known failure modes of persona simulation, and the mitigation for each

From the [multi-LLM persona generation](https://doi.org/10.1145/3808098) and [persona-conditioned reliability](https://arxiv.org/html/2602.18462v1) literature:

| Failure mode | Mitigation in this design |
|---|---|
| **Over-politeness** — the persona is helpful when a person would not be | The yield condition, written per plant, is the whole answer to this |
| **Persona drift** — voice and facts wander across turns | Fixed model assignment per persona; prior transcript prepended every call |
| **Behavioral artifacts** — the model performs "being interviewed" | Briefs written by a different model than the one that plays the persona |
| **Lack of negative feedback** — nobody pushes back or refuses | At least two personas carry an explicit refusal, and one plant (P5) requires a refusal to pass |

Multi-model persona authoring is itself an established technique for diversity — which independently supports using OpenRouter for authoring, and does double duty here as the blind.

### The landscape, first-party as of 2026-07-30

| Project | Stars | Last push |
|---|---|---|
| clawcompany | 580 | 2026-04-25 |
| Sylph | 170 | 2026-05-21 |
| KbWen/agentic-os | 107 | 2026-07-29 |
| dswh/company-os | 25 | 2026-06-19 |

One new entrant is relevant: **`KbWen/agentic-os`**, active, and using the word "governance" — which ticket #15 named as groundwork's one fully-owned contrast. Read closely it occupies an adjacent lane: it governs *how an AI coding agent does engineering work* through a five-step plan/build/review/test/ship workflow with evidence gates, delivered via AGENTS.md. groundwork governs *what a company permits agents to do and who is accountable when they do it*. Developer tooling versus company operations — different lane, overlapping vocabulary.

**Queued, not done here:** a positioning refresh distinguishing groundwork from `agentic-os`, to be brainstormed after this project's first run, when there is evidence rather than an argument. The two named competitors have both been quiet for over two months; under #15's punch-down rule that is a strategic fact for the maintainer and **may not enter the README**.

## Architecture

### Three repositories

**`groundwork`** — the engine. Untouched by this project. Findings return only as ordinary slices through the build loop.

**`<company>-personas`** — the test apparatus.

```
_company.md          the fiction: org chart, canon (domains, phone range), what the business does
_artifacts/          the messy shared drive: an escalation log, a half-current handbook page,
                     a tracker export — the corpus the evidence-based option reads
personas/
  <person>/
    public.md        who they are and what they will say freely
    private.md       what is actually true, and what it takes to get it out of them
plants.md            the answer key: every planted gap, with its pass condition
ask.py               assemble a persona prompt; send it or print it
transcripts/         one append-only file per persona, per run
runs/<date>/         scorecard, findings, timing, audit, raw transcript
```

**`<company>-os`** — the generated company OS. Private, carries `groundwork.pin`, and is what the validator runs against.

### The persona format

`public.md` carries flat frontmatter — `name`, `role`, `function`, `reports_to`, `tenure`, `speaks`, `model` — and a body: how they talk, what they are proud of, what they volunteer unprompted.

`private.md` carries the plant identifiers they hold, what is actually true, what they deflect, and **what it takes to get it out of them.**

### The yield condition is the load-bearing invention

An adversarial persona has two failure modes and both are fatal. Never yield, and the test fails regardless of how good the protocol is. Yield immediately, and it passes regardless. Either way the run measures nothing.

So every plant carries an explicit yield condition, written into the brief in the second person:

> *You believe ops owns escalations. You are wrong — CS has quietly owned them since March. You will not volunteer this. If the interviewer tells you someone else said CS owns it, you become defensive and say "that's news to me, but Priya would know." If the interviewer asks to see the escalation log, you say it is in the shared drive and you have not looked in months.*

That sentence is simultaneously the persona's instruction and the answer key's pass condition. It is why the plants must be authored by a different model from the one conducting the interview: **a yield condition I wrote is one I would unconsciously interview toward.**

### Cast size

Roughly twenty people on the org chart; **six to eight with full briefs.** A real interview talks to a handful — the founder or COO, plus one lead per function going deep. The remaining names exist so ontologies and Owner's Cards can point at realistic people. Authoring twenty full brief pairs for people who never speak is cost with no return, and the protocol's own depth doctrine (three to five acted-on activities on a first pass) sets the ceiling anyway.

### Transport and consistency

Model assignment is **fixed per persona** in `public.md` frontmatter; a persona that changes model changes voice, which is persona drift by construction. Local Qwen variants (Ollama, LM Studio) for most personas — free and unlimited. OpenRouter for two or three where voice distinctness matters most. `ask.py --print` emits the assembled prompt for a browser tab without sending it.

`ask.py` prepends that persona's prior transcript for the current run on every call. That is the memory, and it is bounded by transcript length rather than by any state machine.

**The OpenRouter key is read from the environment at run time and never enters a file, a prompt, or a transcript.**

## The run loop

### The rule that comes before the loop

**The interviewing agent must be a fresh session that has never seen this design conversation.** An agent carrying an hour of plant-design reasoning is not blind. Start a new session, point it at `interview/` and the harness, and nothing else. This is the cheapest available way to void the experiment, so it is stated first.

### Setup

The interviewing agent's working directory is `<company>-os` — precondition 2 of `generate.md`, *you are in the company's private repo, not the groundwork clone*. It reads `interview/` from the engine clone and reaches personas only through `python3 ../<company>-personas/ask.py`.

### The loop

1. The agent reads `interview/README.md`, `protocol.md`, and `questions.md`. **Not `generate.md`** — generation is a separate act with its own preconditions.
2. It defines the analyst role first, then asks one question at a time, each routed to one persona.
3. Answers accumulate in `<company>-os/interview/_working.md`.
4. At each layer boundary the agent proposes the confirmed layer. The maintainer approves. It promotes to `NN-<layer>.md`, commits, and updates `00-manifest.md`.
5. Repeat until `status: complete` and `open_question: none`.
6. **Then** generation, following `generate.md` — the second-ever execution of that protocol, this time on answers nobody scripted.
7. Then `python3 scripts/validate.py ../<company>-os` from the engine clone.

### The artifacts corpus is a requirement, not a nicety

`protocol.md` includes the evidence-based option: with permission, the agent reads what exists and reflects back the rules the company is *actually* running. That mechanic is the operational form of the insight the whole interview rests on — people report the rules they wish they had — and **it is untestable unless the artifacts exist.** Plant P3 has nowhere to live without `_artifacts/`, and P3 is what tests whether the evidence-based option earns its place.

`_artifacts/` is deliberately not blinded. A real company would show you these.

### The maintainer's rule at checkpoints

**Approve or reject. Never supply.** Handing over a fact the interview failed to elicit contaminates the measurement — and the plants are specifically designed to make that tempting, because the maintainer can see what the agent is missing.

### The halt rule, specified

`protocol.md` says an unanswerable question halts and is recorded, never resolved by inference. Here, *unanswerable* means the persona refuses, deflects, or does not know, and no other persona holds it.

Defined behavior: the agent records it as an open question in `_working.md` and commits **`_working.md` and the manifest together** — the Slice 3.2 lesson, that a rule which writes state must name every file the state lives in — then surfaces it to the maintainer.

The maintainer may say *"ask Priya"* — a legitimate operator move a real maintainer would make. The maintainer may say *"nobody knows"* — the item stays open and must appear in the generation report. **The maintainer may not answer it.** That path is exactly what tests #6's generator refusal, which has only ever run against fixtures.

### The audit, and its ceiling

`ask.py` appends every exchange to `transcripts/<persona>.md` and to `runs/<date>/transcript.jsonl`. Afterward the interviewing agent's own session log is searched for reads of `private.md` or `plants.md`; a hit voids the run.

Honest ceiling: the audit is only as good as access to the agent's tool-call log. Where that log is unavailable the audit degrades to the maintainer's observation, and the result is recorded as **unaudited** rather than clean.

## The plants

Every plant carries seven fields: `id`, `type`, `carried_by`, `truth`, `surface` (what a naive interview concludes), `yield_condition`, and explicit `pass` / `fail`.

| # | Plant | Passes if | Tests |
|---|---|---|---|
| **P1** | Two people give incompatible accounts of one process | The contradiction reaches the interview state as an open question, or the OS records the resolution with evidence of how | One-question-at-a-time, checkpoints, confirmed-versus-provisional |
| **P2** | A real rule nobody volunteers because it is embarrassing | It lands in `governance/constitution/` **with its ritual and scarcity provenance** | The five-question worksheet — "start with the rule everybody resents" — which has only ever run on fixtures |
| **P3** | A fact that lives only in `_artifacts/` | The fact reaches the OS | The evidence-based option |
| **P4** | A rule someone states confidently that is not actually followed | The OS records actual practice, or flags the divergence | The sharpest claim in the whole interview design |
| **P5** | An automatable activity nobody will own | The skill ships `provisioned: no` and the generation report names the missing answer | #6's generator refusal |
| **P6** | An activity everyone *wants* automated that should not be | It returns `hire`, `wait`, or `buy` — or `automate` with a Describability Gate that honestly fails | The Motion pivot and the no-waiver Gate |
| **P7** | Something that must not degrade | It survives into prose somewhere retrievable | The known health-metrics schema gap |

**Eight to ten instances across the seven types** — two each of P1 and P2, one of the rest.

**P6 is the one to defend hardest.** groundwork's differentiating claim is not that it automates things; it is that it says what *not* to automate and gives human time back. Nothing has ever tested whether the protocol protects a company from over-automating when the company is enthusiastic about it. P6 is the north star rendered as a test case.

**P7 turns a documented gap into a measured one**, producing real evidence for whether the health-metrics field is worth spending the first `SCHEMA_VERSION` bump on — a decision currently resting on judgment alone.

## Scoring

Each plant is pass or fail against its own stated condition, graded by a **fresh grading session** — a new agent session, spawned by the maintainer after the run ends, given exactly four inputs: `plants.md`, the generated OS, the interview state, and the transcripts. It is given no design context and does not read this document. Not graded by the maintainer, who is already out of the answering loop; staying out of the grading loop is the same discipline and is what makes a second run comparable to the first.

The grader writes `runs/<date>/scorecard.md`: one row per plant with the verdict, the evidence it relied on, and — where a plant failed — the specific place the information should have appeared and did not.

Four run-level observations sit alongside the scorecard, none of them pass/fail:

1. **Where the protocol left the agent guessing** — in the format Slice 4.3's dry run produced: before, after, measured. Qualitatively the most valuable output, and the dry run proved it by finding four real defects nobody could have found by reading.
2. **Whether the generated OS passes the gate** — binary, and the least interesting, since the fixture already proves the shape validates.
3. **Elapsed time, question count, checkpoint count.**
4. **The audit verdict** — clean, or voided, or unaudited.

### What the score is not

It is not a grade for groundwork. Every failed plant points at one named protocol weakness with a specific fix — a question the skeleton does not ask, a checkpoint that does not force a comparison, a place where `generate.md` picks the wrong instruction. A run where everything passes first time is the *least* useful outcome, and the honest conclusion would be that the plants were too easy.

## Retiring "adoptable in an afternoon"

Brief §7 set V1's constraint as *adoptable in an afternoon*, binding on the adopter's required path. That phrase appears in product content exactly once, as an aside in `CONTEXT.md`; the README and `AGENTS.md` make no time claim. So this is a design-constraint change rather than an honesty cleanup.

**The constraint is retired and replaced by two metrics that can pull against each other**, because a single number is what allowed a proxy to stand in for the real goal:

1. **Time-to-first-value for a non-technical person**, measured on the **walkthrough** — the actual onboarding moment, which already claims fifteen minutes.
2. **Depth of the resulting OS** — how much of the company's real operating truth was captured. That is the plant score.

The interview's own duration becomes an **observation, not a constraint.** A serious consulting engagement takes days; requiring the interview to fit an afternoon is the exact pressure that would make the product shallower. The original intent — *a non-technical person should never be confused* — is preserved by metric 1 and belongs to the walkthrough and the README, not to the interview.

### The tension this creates, named on purpose

"Depth under the hood, simplicity on the surface" is the phrase that historically produces overbuilt systems, and groundwork's Never list — no hosted anything, no runtime, no memory engine, no dependencies — is a large part of why it is not a runtime today.

These are compatible only if the sophistication lives in **the conventions and the questions** rather than in machinery. That is already true, and it is the actual moat: a competitor copies the folder structure in an afternoon and cannot copy nineteen resolved decisions, an elicitation protocol built to defeat a known human failure mode, and a governance model with typed rules, named owners, and appeals.

**The jet engine is the thinking. The family car is the file.** If hardening ever takes the form of adding machinery, that is the signal the two have been mistaken for each other.

## What flows back to groundwork

Findings return as changes, never as a pile of notes:

- **Protocol defects** become ordinary slices touching `interview/protocol.md`, `questions.md`, or `generate.md`, through the existing build-and-review loop.
- **Measured limits** go to `docs/known-limitations.md`.
- **P6 and P7 results** become evidence in `docs/roadmap.md` for whether the health-metrics field earns the first `SCHEMA_VERSION` bump.
- **A queued roadmap line** commits to keeping the README's comparison current as the landscape moves — the maintenance commitment, not the competitor analysis, which is workbench material. Exact text, to land under V1.5 in `docs/roadmap.md`:

  > - **Keep the comparison current.** [How groundwork compares](../README.md#how-groundwork-compares) is a claim about a landscape that moves, and a comparison written once and left alone becomes wrong without anyone editing it. It gets re-verified against the named projects rather than left to rot, on the same principle as this document's review date.

  Product content, so it lands through a branch and a merge like any other change — not written into `main` by the planner.

### The honesty boundary

**May be said:** the interview and generation protocols have been run end to end against a simulated company with adversarial personas, and here is the scorecard.

**May not be said:** that groundwork has been used by a real company. The README's "no interview has been run on a real company" is **amended, not removed** — still no real company, and here is what has been run and what it showed.

A new known-limitation lands with the first run, because it is the honest ceiling of this entire design and the literature says the same thing in its own words:

> A persona is a cooperative interviewee by construction. The plants approximate human evasiveness; they do not reproduce it. A persona will not be bored, will not protect a colleague, will not misremember, and will not hold knowledge it cannot articulate. What this measures is whether the protocol surfaces *designed* gaps. Whether it surfaces *human* ones remains untested.

## Direction E — a company of agents

Recorded as a named direction, not scheduled.

E is the personas as **staff** rather than subjects: holding jobs, doing work, proposing changes, and governed at runtime by the constitution the interview produced. It is a genuine V3 or V4 thesis — an agent-run company — and the reason to write it down now is that this project hands it three of its four ingredients for free: the persona files, the company fiction and its artifacts, and a generated OS with a real constitution.

What it needs that does not exist is all V2 work: runtime enforcement beyond Claude Code, governed autonomous application, and some way for a persona to **hold a job over time** rather than answer a question. The honest sequence is therefore:

**this project → V2's one-skill skeleton → E.**

A line under V3 in `docs/roadmap.md` records the direction; this section records what it would need.

## This needs two implementation plans, not one

Stated here so the split is a decision rather than a discovery mid-session. The two halves have different actors and different failure modes, and merging them would put the answer key in the same session as the run.

**Plan 1 — build the apparatus.** The fiction and canon, the cast, the public and private briefs (authored through OpenRouter by models other than the one that will interview), `_artifacts/`, `plants.md`, and `ask.py` with its three transports. Ends when a persona can be asked a question from the command line and answers in character, and when `--print` emits a prompt that works pasted into a browser.

**Plan 2 — run and score.** A fresh blind session conducts the interview, generation runs, the validator runs, a separate grading session produces the scorecard, and the findings and audit are written. Ends when `runs/<date>/` is complete and the score has been read against the pre-committed band.

Plan 2 cannot be written in detail until Plan 1 lands, because its inputs are the artifacts Plan 1 produces.

## What this design does not cover

- **V2's walking skeleton (D).** It operates on the generated OS and should not be designed before that OS exists.
- **Any change to `scripts/validate.py`.** The engine is untouched by this project.
- **A second run.** The apparatus is versioned so a second run is possible and comparable; whether to run one is a decision made after the first scorecard exists.
- **The company's name, cast, and specific plants.** Those are authored in the implementation plan's first tasks, by models other than the one that will conduct the interview. Specifying them here would defeat the blind — this document is read by the planner, and the planner must not know the answer key.

## Success criteria for this project

1. A generated `<company>-os` exists, produced from answers given by personas rather than copied from a fixture, and `scripts/validate.py` reports its result — whatever that result is.
2. A scorecard exists, graded blind against `plants.md`, with each plant marked pass or fail against its own stated condition.
3. The score is interpreted against the pre-committed band above, not against a number invented after seeing it.
4. A findings document exists in the Slice 4.3 dry-run format, naming every place the protocol left the interviewing agent guessing, with each finding classified as clarification or structural.
5. The audit verdict is recorded as clean, voided, or unaudited.
6. Every claim groundwork makes afterward stays inside the honesty boundary, and the README's real-company sentence is amended rather than deleted.
