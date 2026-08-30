# The interview — how to run it

This is the procedure. [questions.md](questions.md) is what to ask;
[README.md](README.md) is the state format the answers are written into. Read all
three before starting, and read this one again at every checkpoint.

An interview produces the record a company's operating system is generated from. It is
not a form, and filling it in faster does not make it better — a wrong answer captured confidently is worse than a
question still open, because everything downstream is generated from it.

## Before anything: the private repo

The first act is creating the company's own **private** repository. Every answer, every
checkpoint, and every generated file lives there. Nothing organizational is ever written
into the public groundwork clone, which stays a pull-only engine (#10).

```
gh repo create <company>-os --private
```

Then `interview/` is created inside it, and the manifest is the first commit.

## The five mechanics

### 1. Define the role first, then act as it

Before the first question, ask the human this, and wait:

> "What does a *good* organizational analyst do here, and what does a bad one do?"

Their answer is the role, and it goes in the manifest's `role:` field verbatim enough
that a resuming agent inherits it. Write it down before asking anything else.

The reason is not ceremony. An analyst who has not agreed what good looks like defaults
to the shape of its training — arriving with a solution and interviewing for permission.
The role, stated by the person who has to live with the result, is the thing you check
your own behaviour against when the conversation gets interesting.

A reasonable default, if they ask for one: *a good analyst asks what the work actually
is before asking what to do about it, says "that is not worth automating" out loud, and
never proposes machinery for a problem nobody has named.* Offer it as a starting point,
not as the answer.

### 2. One question at a time — and no generation until understanding is complete

One question. Wait for the answer. Then the next.

Batched questions get batched answers, and batched answers are where detail goes to die:
the person answers the easy one, gestures at the rest, and the gaps are invisible because
the shape of a reply looks complete.

**No file outside `interview/` is written until the interview is complete.** Not a draft
ontology, not a sample skill, not "here is what I would generate." The reason is that a
generated artifact stops being a question — the person starts editing your draft instead
of telling you how the work actually happens, and you have replaced their model of their
company with yours. The generation protocol holds the same line from its side:
[generate.md](generate.md)'s first precondition is to stop while the manifest says
`status: in-progress`.

If the person asks to see something concrete, show them `demo/` — a company that is
already finished, and not theirs.

### 3. Read what exists, with permission, and reflect it back

Ask:

> "May I read what you already have — the handbook, a calendar export, the tracker, the
> repo, a quarter of meeting notes? I will tell you what I think the rules actually are,
> and you tell me where I am wrong."

This is the highest-yield move in the interview, and the reason is uncomfortable: people
report the rules they wish they had. Asked "what is your renewal process," you get the
process as designed. Read the renewal log and you get the process as run — and the gap
between them is usually the thing worth acting on.

What comes back from a read is **`observed`**, and what you conclude from it is
**`inferred`**. Neither is `confirmed`. Both go in `_working.md` with a `source:` naming
what you read, and both stay provisional until a person says otherwise. Reflect the
finding back as a claim they can correct, with the evidence attached:

> "The log says fifteen of twenty-six renewals had a written brief, median eight days
> out. Is that the process, or is that the process failing?"

If permission is refused, say what that costs — the interview will record what people
report rather than what the records show — and continue. Refused permission is a fact
about the company, not an obstacle.

### 4. Checkpoint approvals, one layer at a time

A **layer** is one coherent chunk of understanding — a function, or the opening scope.
When a layer feels settled:

1. State back what you believe is now true, in the person's own terms, short enough to
   read in one go.
2. Ask: **"Is this right, and may I freeze it?"**
3. Only their yes confirms it. Your confidence does not.
4. On yes: promote `_working.md` to the next `NN-slug.md`, set `provenance: confirmed`,
   record `confirmed_by` and `confirmed_at`, update the manifest, and commit them
   together in one commit.

That commit is the approval record. The promote-and-commit protocol is specified in
[README.md](README.md); this is the conversational half of it.

**A layer is frozen once committed.** If a confirmed fact turns out to be wrong, the next
layer records the correction and says what it corrects. You do not go back and rewrite
what somebody approved — `--diff` will catch it wherever the base you name holds both the
layer and its `00-manifest.md` ([README.md](README.md) states the condition), and more
importantly it destroys the one thing the checkpoint was for.

### 5. The evidence floor — ground every acted-on activity

Before a layer covering an acted-on activity is frozen, ask — one question at a time,
regardless of Motion — **When did this last run? Who did it? What does the record
show?** The same three questions go to every ritual the constitution pass keeps or
repeals, aimed at its last enforcement instance. A `wait` is acted on; a kept rule is
acted on. The floor does not extend to the executive tier — fifteen-activity sweeps
stay cheap.

The reason is the same uncomfortable one behind mechanic 3: people report the rules
they wish they had. A general-case question fills a schema field with the process as
designed; only an instance-level question surfaces the process as run. A complete
record of a stopped process is worse than a gap — it is confident error, and
everything downstream is generated from it. The floor exists so "schema complete" and
"grounded" are the same stopping condition. When any answer comes back as a general
case, go one level down before recording it — a specific recent instance, a concrete
scenario, the document behind it.

Three rules bind:

**"No record is kept" is an answer.** It is recorded as confirmed absence, naming who
confirmed it. **An unknown freezes only as a confirmed unknown**: the person answering
for the activity, or whoever they name as closest, confirms the company cannot say —
"we don't track who runs it" is an answer, and it freezes. "I don't know, someone
might" is not; it leaves the question open — ask the person they point to, and when
nobody in reach can answer, the halt rule fires unchanged (next section): the operator
may route the question or close it, and the outcome lands in the layer's grounding
disposition ([README.md](README.md)). Never convert an unknown into an absence: lack
of evidence is not evidence of absence.

**Citing is claiming you tested.** For each acted-on activity, a document named in a
layer's `source:` that makes an operational claim about that activity — how it runs,
who performs it, what gate it passes — has that claim quoted back to a person and
either confirmed or recorded as divergence, or the layer records why not. The unit is
the claim-about-the-activity, never the whole document; you test what you cite, and
you cite what the layer uses. An untested cited claim is never stated as practice in
any record — it enters as *stated in the document, untested*. Skipping the test
degrades a claim's status; it never launders it.

**A document proves what it is, and divergence is recorded, never resolved.** An
execution record — a log, a tracker, an artifact of runs — is evidence of practice; a
policy document is evidence only of the stated rule. When accounts and evidence
conflict: execution evidence establishes practice and the Motion verdict binds to it;
with no execution evidence, an instance-grade account outweighs a policy statement;
with no practice evidence on either side, record both sides with attribution and an
explicitly unresolved operating truth. A layer may freeze with an unresolved operating
truth — the dispute is the finding — and the Motion verdict ships only with the
dispute stated on the record. Never talk one side into the other.

Above all: **a practice claim carries its evidential basis, and the record preserves
it.** The layer's grounding disposition states the basis at the freeze; a claim
resting on a general account alone carries **unverified** wherever it appears,
including the Motion rationale. Uncertainty is recorded; it is never converted into
fact by prose that outruns its basis.

The cost, honestly: roughly three extra questions per acted-on activity and per
examined ritual, plus a variable source-testing cost that scales with what you choose
to cite. That is the price of records that describe the company that exists rather
than the one in the handbook.

## The rule when nobody can answer

**An unanswerable question halts the interview.** It does not get resolved by inference.

Write the question into `_working.md`, name it in the manifest's `open_question`, commit
`_working.md` and the manifest together, and stop — a manifest that names an open
question with no `_working.md` beside it is exactly the drift `check_interview_state`
rejects, and a working file left uncommitted does not survive the harness switch this
rule exists for. A resuming agent — possibly in a different harness, possibly
weeks later — picks it up from there.

This matters most in the places it is most tempting to skip. Five answers **may only
come from a human**, and no amount of reading produces them (#6):

- the **owner** and the **backup owner** of any skill,
- the **forbidden actions**,
- the **pause condition** and the **retirement condition**.

They are marked *human-only* in [questions.md](questions.md). An agent that fills one of
them from context has invented an accountability structure, and the person named will
find out when something goes wrong.

## The shape of the interview

**Layer 1 — role and scope.** The role (mechanic 1). Then: how many people, what the
company sells, what its shape rules out. Then the decision that governs everything after
it — **which functions go deep.**

Steer toward **three to five acted-on activities** on a first pass. This is doctrine, not
a validator rule: *depth is earned by acting, not by planning to act.* An organization
that deep-records twelve activities has written twelve worksheets and changed nothing. If
they want more, agree to come back — the state format is resumable precisely so a second
pass is cheap.

**Layers 2..N — one function each.** For each function: name every activity and give each
one a **Direction** — up (deserves more human time) or down (should stop being hand-run).
That is the whole executive tier, and most activities never get more than it.

For the activities they have chosen to act on, work the question skeleton
([questions.md](questions.md)) in section order. The Motion verdict is the pivot: only
`automate` and `build` need Substrate, Shape, and all eight Describability Gate answers.
`buy`, `hire`, and `wait` stop after the common core — the Motion and its five scores,
the work type (section 1), the accountable owner (section 7's one-name question),
plus the grounding row (section 1, mechanic 5).

**A `wait` is a real answer.** Record it, with its reasoning. An ontology that only ever
records automation verdicts reads as an automation funnel, and in a year somebody will
want to know whether a function was considered and dismissed or simply never asked.

**The constitution pass.** Once the functions are mapped, run the
[five-question worksheet](../governance/worksheets/five-question-worksheet.md) over the
company's rituals — **starting with the rule everybody resents**, because it is the one
where the answer to "is that scarcity still real?" is most often no, and because getting
one repeal right buys the credibility for the rest.

Each surviving rule is typed as four owned objects, placed on a rung, and given a sunset
date. Section 6 and 7 of the question skeleton carry those questions. Two hard rules the
compiler does not negotiate: a `high-risk` rule must carry a human appeal path — **there
is no rung six** — and a repealed ritual's surviving job must be reassigned to a named
person before the repeal ships.

**The last layer — the baselines.** For every activity that will get a provisioned
skill, capture what is true today, measured, before anything is generated. Not an
estimate; a number from a record, with the record named. This is #5's provisioning gate:
no skill ships for an activity without a captured baseline, because "it got better" is
not a claim you can make later if you never wrote down what it was like.

## Finishing

Set `status: complete` and `open_question: none`, delete `_working.md`, and commit.

Then generation runs — [generate.md](generate.md), a protocol you follow rather than a
program you invoke. The interview has produced a complete, checked, resumable record of
what the company decided; the generation protocol says how the confirmed layers become
`ontologies/`, `skills/`, and `governance/`, and the validator proves the result.

## What good looks like at the end

- Every acted-on activity has an owner — **a role or a named holder** — that the roster
  resolves, and whoever holds it knows. The interview asks for that last part; nothing in
  the repository verifies it (see `docs/known-limitations.md`).
- Every automation-path activity answers all eight Gate questions. A truthful "none" is
  an answer; "N/A" is not, and there is no waiver.
- At least one activity is recorded as **not** worth automating.
- At least one rule was **repealed** with its surviving job reassigned — or the
  confirmed layers record why no ritual deserved repeal. An interview that examined
  nothing is a failure; one that honestly found nothing to repeal is not.
- Every acted-on record names its grounding in all three dimensions — an instance or
  record, a confirmed absence, an honest unknown, or a recorded refusal — every
  practice claim carries its evidential basis, unverified where that is the truth, and
  every stated-vs-practised divergence carries its operating truth, evidenced or
  explicitly unresolved.
- Every provisioned skill cites a baseline captured before it was provisioned.
