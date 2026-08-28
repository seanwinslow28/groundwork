# The evidence floor (S1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (or
> superpowers:subagent-driven-development) to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land mechanic 5 — the evidence floor — across the four interview documents
and the two surface files, exactly as decided in
`docs/superpowers/specs/2026-08-15-s1-evidence-floor-design.md` (the spec; four review
rounds, eighteen findings resolved, decisions 1–14 locked).

**Architecture:** Content-only slice. Six files gain pre-made text; no code changes.
The spec is the authority for every decision — this plan transcribes it into exact
before/after edits. Where a "Before" anchor does not match the file byte-for-byte,
**stop and report; never improvise.**

**Tech Stack:** Markdown; `scripts/validate.py` as the gate; `grep` for the sweep.

**Preconditions:** `docs/honesty-run1` and `spec/s1-evidence-floor` are merged to
`main` (this plan's anchors were verified against both). Branch `docs/s1-evidence-floor`
from the post-merge `main`.

## Global Constraints

1. **The genericity rule is absolute** (spec decision 1). No plant-shaped topic or
   phrasing enters any edited file. Task 6 runs the tripwire grep over the whole slice
   diff and it must return nothing.
2. **Content slices change no code.** Nothing under `scripts/` or `tests/` changes. If
   content trips a check, the content is wrong — reword it.
3. **Transcribe, do not re-draft.** The After blocks below carry decided design;
   synonyms and "improvements" are how a reviewed decision drifts. Wrap lines to ~90
   columns as the files do; change nothing else.
4. **Regression tripwires** — identical before and after:
   `python3 -m unittest discover -s tests 2>&1 | grep -E "^Ran |^OK|^FAILED"` →
   **Ran 709 … OK (skipped=1)**; `python3 scripts/validate.py . | tail -1` →
   **0 error(s), 7 warning(s)**; `python3 scripts/validate.py . --diff main` →
   **exit 0**; `python3 scripts/validate.py demo | tail -1` →
   **0 error(s), 2 warning(s)**; `wc -l AGENTS.md` → **≤ 200**.
5. **This slice does not split.** All six files promote one thing; a partial landing
   ships the multi-file contradiction this build has been burned by three times. If the
   session cannot finish, stop before committing anything and report.
6. **One commit per task**, branch `docs/s1-evidence-floor`, Codex review at the end
   (fresh review after any fix commits), maintainer lands the merge.

---

### Task 1: `interview/protocol.md` — Mechanic 5

**Files:**
- Modify: `interview/protocol.md` (heading at :23, new mechanic after mechanic 4, the
  stop-rule sentence at :147-152, the closing list at :184-193)

- [ ] **Step 1: Retitle the mechanics heading.** Replace exactly:

```markdown
## The four mechanics
```

with:

```markdown
## The five mechanics
```

- [ ] **Step 2: Insert Mechanic 5.** Find the end of mechanic 4 — the line
  `one thing the checkpoint was for.` — and insert after that paragraph, before the
  `## The rule when nobody can answer` heading:

```markdown
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
```

- [ ] **Step 3: Extend the stop-rule sentence.** Replace exactly:

```markdown
`buy`, `hire`, and `wait` stop after the common core — the Motion and its five scores,
the work type (section 1), and the accountable owner (section 7's one-name question).
```

with:

```markdown
`buy`, `hire`, and `wait` stop after the common core — the Motion and its five scores,
the work type (section 1), the accountable owner (section 7's one-name question), plus
the grounding row (section 1, mechanic 5).
```

- [ ] **Step 4: Add the closing-list bullet.** In "What good looks like at the end",
  insert after the bullet ending `An interview that examined
  nothing is a failure; one that honestly found nothing to repeal is not.`:

```markdown
- Every acted-on record names its grounding in all three dimensions — an instance or
  record, a confirmed absence, an honest unknown, or a recorded refusal — every
  practice claim carries its evidential basis, unverified where that is the truth, and
  every stated-vs-practised divergence carries its operating truth, evidenced or
  explicitly unresolved.
```

- [ ] **Step 5: Verify and commit.**

Run: `python3 scripts/validate.py . | tail -1` → `0 error(s), 7 warning(s)`
Run: `grep -c "The five mechanics" interview/protocol.md` → `1`;
`grep -rn "four mechanics" interview/` → no output;
`grep -c "confirmed unknown" interview/protocol.md` → ≥ 1

```bash
git add interview/protocol.md
git commit -m "docs(interview): mechanic 5 — the evidence floor"
```

### Task 2: `interview/questions.md` — the grounding rows

**Files:**
- Modify: `interview/questions.md` (intro stop-rule at :20-25, section 1 table, the
  constitution pass table)

- [ ] **Step 1: Extend the intro stop-rule.** Replace exactly:

```markdown
`buy`, `hire`, and `wait`, stop after the common core — the Motion and its five scores,
the work type (section 1), and the accountable owner (section 7); every other row is
automation-path only.
```

with:

```markdown
`buy`, `hire`, and `wait`, stop after the common core — the Motion and its five scores,
the work type (section 1), the accountable owner (section 7), plus the grounding row
(section 1); every other row is automation-path only.
```

- [ ] **Step 2: Add the section-1 grounding row.** Insert directly after the row
  `| Is this routing, sensemaking, or accountability? | ontology:work_type | Accountability work rarely leaves a person. |`:

```markdown
| When did this last run, who did it, and what does the record show? | — | The evidence floor (mechanic 5), asked regardless of Motion. Confirmed absence, unknown, and refused are all honest answers; record which one. |
```

- [ ] **Step 3: Add the constitution-pass grounding row.** Insert directly after the
  row `| Name the ritual, in plain words. What do we actually do? | rule:ritual | Not what the policy says. What happens. |`:

```markdown
| When did this ritual last actually run, who worked it, and what does the record show? | — | Mechanic 5. The last enforcement instance, not the policy. |
```

- [ ] **Step 4: Verify and commit.**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^Ran |^OK|^FAILED"` →
`Ran 709 … OK (skipped=1)` (the coverage test tolerates dash-Fills rows; a failure
here means the row broke the canonical table grammar — fix the row, not the test)
Run: `grep -c "When did this last run" interview/questions.md` → `1`;
`grep -c "When did this ritual last actually run" interview/questions.md` → `1`

```bash
git add interview/questions.md
git commit -m "docs(interview): the grounding row, in the skeleton and the constitution pass"
```

### Task 3: `interview/README.md` — the disposition convention and C3

**Files:**
- Modify: `interview/README.md` (the confirmed-layer example at :69-78, a new
  subsection after it, the finishing section at :143-146)

- [ ] **Step 1: Add grounding lines to the worked layer example.** In the fenced
  `02-customer-success.md` example, replace the body lines:

```markdown
Renewal prep is the one acted-on activity: Motion automate, run from the CRM as the
source of truth. Health-check calls stay human — Direction up, and Mara said why.
```

with:

```markdown
Renewal prep is the one acted-on activity: Motion automate, run from the CRM as the
source of truth. Health-check calls stay human — Direction up, and Mara said why.

Grounding: renewal prep — last_run: the 12 August renewal; performed_by: Mara Voss;
  record: Q2 renewal log, fifteen of twenty-six briefs written; practice_basis: execution-record
```

- [ ] **Step 2: Insert the convention subsection.** After the confirmed-layer section
  (immediately before the `### The turn in flight — `_working.md`` heading), insert:

````markdown
### The grounding disposition

A layer covering an acted-on activity (or a ritual the constitution pass kept or
repealed) carries one grounding disposition per activity in its body — a composable
line mirroring the evidence floor's three questions (mechanic 5), plus a divergence
line when one exists:

```
Grounding: <activity> — last_run: <date or instance | unknown | refused>;
  performed_by: <name | unknown | refused>;
  record: <record named, what it showed | none (confirmed by <name>) | unknown | refused>;
  practice_basis: <execution-record | instance-testimony | general-account-only | disputed | none-established>
```

Each slot is answered independently — a known instance with an unknown performer and a
refused record is one honest line. `none` is confirmed absence and names its
confirmer; `unknown` is nobody-could-say, and it is a **confirmed** unknown — "we
don't track this," attested, not "I don't know" from one person; `refused` is access
not granted, a fact about the company. Lack of evidence is never written as `none`:
lack of evidence is not evidence of absence.

`practice_basis` is a weakest-link summary — the weakest basis among the record's
load-bearing practice claims, so a strong claim can never launder a weak one; the
per-claim truth lives in the record prose, each claim marked, and a claim resting on a
general account alone carries **unverified** wherever it appears. `none-established`
is the honest value when nothing about current practice could be attested at all.

A divergence, when present, is its own second line in one of two forms:

```
Diverges (evidenced by <execution record | instance testimony>): <side> states <X>; <evidence> shows <Y> — operating truth: <Y>
Diverges (unresolved): <side A> states <X>; <side B> states <Y> — operating truth: unresolved
```

This is what the operator checks at the freeze: an acted-on activity with no
disposition, a blank slot, or a value that fits no legal form is grounds for a
procedural rejection. A restated general account is not an instance — testimony
without a nameable instance or record fills its slot as `unknown`.
````

- [ ] **Step 3: Land C3 in the finishing section.** Replace exactly:

```markdown
Set `status: complete` and `open_question: none`, and delete `_working.md`. A completed
interview with a turn still in flight is a contradiction, and it ERRORs.
```

with:

```markdown
Set `status: complete` and `open_question: none`, and delete `_working.md`. A completed
interview with a turn still in flight is a contradiction, and it ERRORs.

`open_question` tracks a **turn in flight, not a knowledge gap**. An unanswered
question does not hold the interview open forever — it closes the field by being
recorded in a frozen layer's grounding disposition or body as an explicit unknown,
which is how a halt the operator closes with "nobody knows" resolves: the gap travels
into the record, never blocks completion, and is never estimated.
```

- [ ] **Step 4: Verify and commit.**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^Ran |^OK|^FAILED"` →
`Ran 709 … OK (skipped=1)` (the executable-example tests re-validate the fenced
blocks; body prose passes shape checks — a failure means a fence or frontmatter was
disturbed)
Run: `grep -c "practice_basis" interview/README.md` → ≥ 2;
`grep -c "turn in flight, not a knowledge gap" interview/README.md` → `1`

```bash
git add interview/README.md
git commit -m "docs(interview): the grounding disposition convention; C3 — open_question tracks a turn in flight"
```

### Task 4: `interview/generate.md` — carry the basis, never resolve

**Files:**
- Modify: `interview/generate.md` (the Motion-pivot paragraph at :90-94, one new
  paragraph after the Gate paragraph at :96-99)

- [ ] **Step 1: Extend the Motion-pivot sentence.** Replace exactly:

```markdown
The **Motion is the pivot**: `automate` and `build` carry the common core *plus*
Substrate, Shape, and all eight Describability Gate fields. `buy`, `hire`, and `wait`
carry only the common core — Motion, the five scores, work type, and the accountable
owner. **Write the `wait` records.** A recorded decision not to build something is a
decision, and an ontology holding only automation verdicts reads as an automation funnel.
```

with:

```markdown
The **Motion is the pivot**: `automate` and `build` carry the common core *plus*
Substrate, Shape, and all eight Describability Gate fields. `buy`, `hire`, and `wait`
carry only the common core — Motion, the five scores, work type, and the accountable
owner — plus the grounding paragraph every deep record carries, whatever its Motion.
**Write the `wait` records.** A recorded decision not to build something is a
decision, and an ontology holding only automation verdicts reads as an automation funnel.
```

- [ ] **Step 2: Insert the grounding-and-divergence paragraph.** After the paragraph
  ending `it is named in the generation report as a question for the next
interview pass.`, insert:

```markdown
**Grounding and divergence carry through.** Every deep record carries a grounding
paragraph transcribed from the layer's disposition — its three dimensions and its
`practice_basis`. A claim whose basis is a general account alone carries
**unverified** wherever it appears, including the Motion rationale. A divergence
recorded in a layer lands in the record's body with its operating truth as the layer
states it — generation never resolves it, and a record that states the policy side as
practice is laundering, the same refusal class as inventing an owner. An untested
cited claim is carried as *stated in the document, untested*, never as practice.
Layers carrying no grounding dispositions are generated without grounding paragraphs,
and the report says so: "these layers carry no grounding dispositions; grounding
paragraphs not generated."
```

- [ ] **Step 3: Verify and commit.**

Run: `python3 scripts/validate.py . | tail -1` → `0 error(s), 7 warning(s)`
Run: `grep -c "practice_basis" interview/generate.md` → ≥ 1;
`grep -c "no grounding dispositions" interview/generate.md` → ≥ 1;
`grep -c "unverified" interview/generate.md` → ≥ 1;
`grep -c "untested" interview/generate.md` → ≥ 1

```bash
git add interview/generate.md
git commit -m "docs(interview): generation preserves the basis and the divergence; observables, never history"
```

### Task 5: the surface files

**Files:**
- Modify: `README.md` (the interview-section parenthetical), `docs/known-limitations.md`
  (the "Nothing checks interview prose" bullet)

- [ ] **Step 1: The README parenthetical.** Replace exactly:

```markdown
first, one question at a time, no generation until understanding is complete), a
```

with:

```markdown
first, one question at a time, ground every acted-on activity in evidence, no
generation until understanding is complete), a
```

- [ ] **Step 2: The known-limitations sentence.** In the bullet beginning
  `- **Nothing checks interview prose.**`, insert after its final sentence (ending
  `and that the question skeleton can fill every required
  field.`):

```markdown
  The evidence floor (protocol mechanic 5) is the same posture deliberately: an
  instruction plus a freeze-visible convention — no check enforces it, and no run has
  yet measured whether instruction-strength suffices. If a measured run shows it does
  not, a validator-checked grounding rule becomes a candidate alongside the other v2
  discussions.
```

- [ ] **Step 3: Verify and commit.**

Run: `grep -c "ground every acted-on activity" README.md` → `1`
Run: `grep -c "evidence floor" docs/known-limitations.md` → ≥ 1
Run: `python3 scripts/validate.py . | tail -1` → `0 error(s), 7 warning(s)`

```bash
git add README.md docs/known-limitations.md
git commit -m "docs: the evidence floor on the surface — README parenthetical and the unchecked-floor limitation"
```

### Task 6: the closing sweep

**Files:** none — this task fails the slice or closes it.

- [ ] **Step 1: The five tripwires** (Global Constraint 4), all five commands, all
  five expected values.

- [ ] **Step 2: The spec's smoke-check matrix, rows 1–15, verbatim.** Run every grep
  in the spec's "Done looks like" table
  (`docs/superpowers/specs/2026-08-15-s1-evidence-floor-design.md`) and record each
  result. Row 1 is the genericity tripwire and it is absolute:

```bash
git diff main -- interview/ README.md docs/known-limitations.md | grep -i -E "offended|midnight|three recent|cannot get worse|insurance|liabilit|certificat|appendice|email thread|last delivery|who signed|dBA|fax|lyric|playback"
```

  → no output. Any hit means plant knowledge leaked into the fix: stop and fix before
  review.

- [ ] **Step 3: Hand the reviewer the scenarios.** The Codex review request must name
  the spec's six acceptance scenarios ("Acceptance scenarios — reviewer-executed") as
  part of the review: the reviewer walks each against the implemented documents and
  confirms the expected outcome is what the documents now instruct. A review that only
  smoke-checks has not reviewed this slice.

- [ ] **Step 4: Request the Codex review of the branch** (background launch; fresh
  review after any fix commits), report the evidence block, and stop. **Do not merge.**

## What NOT to change

- **Mechanic 3's permission framing** — run 1's only PASS came through it; the floor
  obliges its spirit, not its shape.
- **The halt rule, verbatim** — mechanic 5 routes through it and adds no exception.
- **The Motion pivot's field requirements** — no schema fields anywhere; grounding is
  prose.
- **The executive tier, `demo/` (including `demo/interview/`), `scripts/`, `tests/`,
  `AGENTS.md`, `CONTEXT.md`** — untouched.
- **The spec itself** — the slice implements it; a mid-slice spec edit is a design
  change and goes back to the maintainer.

## Band-aid tripwires — reject these in review

All eight from the spec's "Band-aid tripwires" section apply verbatim; the two most
likely under transcription pressure: prose that outruns its `practice_basis`
(unverified dropped from a general-account claim), and the disposition grammar
loosened "for readability" (a slot made optional is a dimension hidden).

## Deferrals

- **S2** (next slice: the `generate.md` `--diff` base fix), **S4, S5, S6**, and the
  clarifications other than C3 — their own slices.
- **A validator-checked grounding rule** — only if a measured run shows
  instruction-strength fails.
- **Run 2** — undecided; the apparatus is versioned, and if it runs, the floor is what
  it measures.
