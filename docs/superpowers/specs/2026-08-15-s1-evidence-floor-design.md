# The evidence floor (finding S1) — design

> **Workbench artifact, not product content.** The design for fixing run 1's headline
> finding — S1, *the interview has no evidence floor off the automation path*
> (`~/Code-Brain/persona-company/runs/2026-07-31/findings.md`). Brainstormed and
> decision-locked 2026-08-01; design approved by the maintainer 2026-08-15, subject to
> Codex review. It feeds a Fable implementation plan through the ordinary slice loop.
> S1 is structural, so it was reported first and is patched here, never mid-run.

## Why this exists

Run 1 measured the failure precisely. Across 71 questions to seven personas, not one
question went past the general case — no specific recent instance, no document request,
no concrete scenario. That is not interviewer laziness; it is the skeleton working as
built: every row asks for the general case because general-case answers are what fill
schema fields, and the one row demanding a record is scoped to the pre-provisioning
baseline on the automation path. Mechanic 3 calls reading the records "the highest-yield
move in the interview" — and it is a once-per-engagement permission ask that binds
nothing per claim.

The measured cost is not silence but **confident error**:
`ontologies/operations/finance-sign-off.md` is a complete deep record — five scores, a
`wait` verdict, a named accountable owner — describing a checkpoint the company stopped
performing six months ago, generated from an interview whose gate passed at 0 errors.
**The interview's stopping condition is schema completeness, not evidential grounding.**
This design makes those the same stopping condition.

## Decisions locked (maintainer, 2026-08-01; rituals and approach approved 2026-08-15)

1. **Generic design; run 2 is the measurement.** The fix is written from the failure
   class — ungrounded process claims — never from the nine known plants. Nothing
   plant-shaped (topics, phrasings, yield triggers) may appear in any edited file; the
   done-criteria carry a grep tripwire proving it. If a run 2 happens, it measures this
   floor; whether it happens stays undecided.
2. **The floor binds per acted-on activity, all Motions.** One grounding obligation for
   each of the three-to-five acted-on activities, `wait` and `buy` included — the
   measured failure was a `wait` record. Not per current-practice claim (unbounded; the
   trade Part 5 of the findings warns against) and not only-where-documents-exist (the
   worst-record companies would get the weakest floor). The executive tier stays cheap.
3. **Cited sources must be tested.** A document a layer names in `source:` must have had
   its operational claims touching acted-on activities quoted back and confirmed or
   recorded as divergence — or the layer says why not. Citing is claiming you tested.
   (Run 1's grader could not even tell whether the cited handbook had been read.)
4. **Enforcement is protocol plus a freeze-visible convention — no validator change.**
   The floor lives in the interview documents, and the state format's layer convention
   gains a per-activity grounding disposition line the operator can see at the freeze
   checkpoint, where run 1 showed the human gate catches what conversation cannot
   (finding S6). "Nothing checks interview prose" stays true and stays documented; a
   validator-checked floor is deliberately deferred until a run measures whether
   instruction-strength suffices.
5. **Packaging: a fifth mechanic.** `protocol.md`'s "The four mechanics" becomes five,
   with the floor owned in one named home. Run 1 showed distributed guidance does not
   bind — mechanic 3's "highest-yield move" framing was exercised once in 71 questions.
   A named mechanic is also one changed thing a second run can measure.
6. **Rituals are in scope.** The grounding triplet applies to any ritual the
   constitution pass keeps or repeals, asked about its last enforcement instance. A kept
   rule is an acted-on decision, and run 1's P1-a failed exactly here: a grid accepted
   as "uniformly practised" without anyone asking who worked it last time. Cost is
   bounded by the handful of rituals a constitution pass examines.

## The change — one new mechanic, six files

### 1. `interview/protocol.md` — Mechanic 5: the evidence floor

"The four mechanics" retitles to "The five mechanics". The new mechanic lands after
mechanic 4 (checkpoint approvals) and owns three rules:

**Rule 1 — the grounding triplet.** Before a layer covering an acted-on activity is
frozen, ask — one question at a time, regardless of Motion — *when did this last run?*
*who did it?* *what does the record show?* The same triplet applies to every ritual the
constitution pass keeps or repeals, aimed at its last enforcement instance. A confirmed
**"no record exists" is an honest answer** and is recorded as one — the same
confirmed-absence pattern the baseline row already established. An acted-on activity
whose last run *nobody can name* is recorded as exactly that, because a current process
nobody can instance is a finding, not a gap in the notes.

**Rule 2 — the cited-source obligation.** A document named in a layer's `source:` is a
document whose operational claims touching acted-on activities were quoted back to a
person and either confirmed or recorded as divergence — or the layer records why that
did not happen. Citing is claiming you tested.

**Rule 3 — the divergence rule.** When evidence contradicts testimony — or two people
contradict each other about practice — the divergence is recorded, never silently
resolved and never talked into agreement. The record carries **practice as evidenced**
as the operating truth, the Motion verdict binds to practice, and the stated policy is
preserved in the record as stated. (This is the stated-vs-practised sibling of finding
S4's disputed-classification rule; S4 remains its own finding and its own slice.)

**The reasoning paragraph the mechanic carries** (so an interviewer can decide from it
in cases the rules do not enumerate): people report the rules they wish they had.
General-case questions fill schema fields with the designed process; only instance-level
questions surface the run one. A complete record of a stopped process is worse than a
gap — it is confident error, and everything downstream is generated from it. The floor
exists so "schema complete" and "grounded" are the same stopping condition.

**Cost, stated honestly in the mechanic:** roughly three extra questions per acted-on
activity and per examined ritual, bounded because the floor deliberately does not extend
to the executive tier. The Motion pivot's cheap path stays cheap: the triplet is the
only addition to `buy`, `hire`, and `wait`.

**One generic probe principle, no enumeration:** when an answer comes back as a general
case, go one level down before recording it — a specific recent instance, a concrete
scenario, the document behind it. (Enumerating probe types further is deliberately
avoided: the design must not be shaped by the known plants.)

**"What good looks like at the end"** gains one bullet: every acted-on record names its
grounding — an instance, a record, or a confirmed absence — and every stated-vs-practised
divergence is recorded, not resolved.

### 2. `interview/questions.md` — the grounding row, twice

**Section 1** gains one row, directly after the work-type row:

> When did this last run, who did it, and what does the record show? | — | The evidence
> floor (protocol mechanic 5). Regardless of Motion. A confirmed "no record exists" is
> an answer; record it.

**The constitution pass table** gains one row:

> When did this ritual last actually run, who worked it, and what does the record show? | — | Mechanic 5. The last
> enforcement instance, not the policy.

The intro's stop-rule sentence extends: `buy`, `hire`, and `wait` stop after the common
core **plus the grounding row**. Rows are asked in parts under the existing rule. Both
new rows carry `—` in Fills — the answers land in the record's grounding prose and the
layer's disposition line, not in a frontmatter field. **No schema field is added
anywhere in this design**; the 3.2 coverage test binds rows to schema fields in both
directions and dash-Fills rows are already legal, so the test suite is expected to pass
unchanged (verified by running it, not assumed).

### 3. `interview/README.md` — the freeze-visible disposition

The confirmed-layer convention gains one grounding disposition line per acted-on
activity (and per kept/repealed ritual) in the layer **body**, with exactly four legal
forms:

- `Grounding: <activity> — record: <record named>, <what it showed>`
- `Grounding: <activity> — instance: <specific recent instance, named by <person>>`
- `Grounding: <activity> — no record exists; confirmed by <name>`
- `Grounding: <activity> — diverges: <document> states <X>; practice is <Y> (recorded, unresolved)`

**Strictness that makes the line mean something:** a restated general account is not an
instance. "Grounded on what the owner said" is not a legal form — testimony without a
nameable instance or record is recorded as *no record exists*. This is what the operator
checks at the freeze: an acted-on activity with no disposition line, or a disposition
that names no instance, record, absence, or divergence, is grounds for a procedural
rejection — the same class as run 1's stale-`source:` rejection.

The worked layer example in the README gains a disposition line so the convention is
shown, not just stated. Prose convention only: no frontmatter, no validator rule.

### 4. `interview/generate.md` — carry, never resolve

Two amendments. The Motion-pivot sentence ("carry only the common core — Motion, the
five scores, work type, and the accountable owner") gains the grounding prose: every
deep record carries its grounding paragraph, whatever the Motion. And one new
instruction: **a divergence recorded in a layer lands in the record's body as a
divergence — generation never resolves it, and a generated record that states the
policy side as practice is laundering** (the same refusal class as inventing an owner).

### 5. `README.md` (root) — one parenthetical

The interview section's description of the consultant protocol gains the floor in its
existing parenthetical list ("define the role first, one question at a time, ground
every acted-on activity in evidence, no generation until understanding is complete").

### 6. `docs/known-limitations.md` — the floor is instruction-strength

The "Nothing checks interview prose" bullet gains: the evidence floor (protocol
mechanic 5) is instruction-strength plus a freeze-visible convention — no check enforces
it, and no run has yet measured whether instruction-strength suffices. If a measured run
shows it does not, a validator-checked grounding rule becomes a candidate alongside the
other v2 discussions.

## What NOT to change

- **Mechanic 3's permission framing.** It earned its place (run 1's only PASS came
  through it). The floor obliges its *spirit* per acted-on activity; reading what exists
  stays a permission ask, and refusal stays a recorded fact about the company.
- **The Motion pivot's field requirements.** No new schema fields, no Gate changes, no
  `SCHEMA_VERSION` implications. Grounding is prose.
- **The executive tier.** Fifteen-activity sweeps stay cheap; the floor does not reach
  them.
- **The halt rule, the checkpoint flow, the owner rules, the action-class taxonomy** —
  S4, S5, S6 are their own findings and their own slices.
- **`scripts/validate.py` and `tests/`** — content slice; if content trips a check, the
  content is wrong.

## Done looks like

- The five regression tripwires unchanged: 709 tests OK (skipped=1) via
  `grep -E "^Ran |^OK|^FAILED"`; `validate.py .` 0 error(s) 7 warning(s);
  `--diff main` exit 0; `validate.py demo` 0 error(s) 2 warning(s); `AGENTS.md` ≤ 200
  lines.
- `grep -rn "four mechanics" interview/` → no output; "The five mechanics" present.
- The floor named in the five interview-side files: `grep -l "evidence floor"` matches
  `interview/protocol.md`, `interview/questions.md`, `interview/README.md`,
  `interview/generate.md`, `docs/known-limitations.md`; the root README carries the
  parenthetical: `grep -c "ground every acted-on activity" README.md` → 1.
- Both stop-rule sentences agree:
  `grep -n "plus the grounding row" interview/questions.md interview/protocol.md` → one
  hit each (and `generate.md` carries the grounding-paragraph amendment).
- **The genericity tripwire:** the run-1 yield-trigger phrase list greps to zero on the
  slice diff —
  `git diff main -- interview/ README.md docs/known-limitations.md | grep -i -E "offended|midnight|three recent|cannot get worse|insurance|liabilit|certificat|appendice|email thread|last delivery|who signed|dBA|fax|lyric|playback"`
  → no output. No plant knowledge leaked into the fix.
- All four disposition forms appear verbatim in `interview/README.md`.

## Band-aid tripwires — reject these in review

- Floor text enumerating plant-shaped topics (insurance clauses, playback rules,
  communications policy, noise ceilings) — the genericity rule is absolute.
- The triplet scoped to the automation path only, or asked only when a record is
  already suspected — the letter-not-spirit failure S1 documents.
- A disposition line satisfiable by restating the general account — testimony without a
  nameable instance or record is *no record exists*, and the legal forms stay strict.
- Mechanic 3 softened, reworded, or made conditional to "fund" mechanic 5.
- Any edit to `scripts/validate.py` or `tests/` to accommodate wording.
- A claim anywhere that the floor is *proven* — it is designed from measured failure and
  untested until a run measures it.

## Deferrals — explicitly not in this design

- **A validator-checked grounding rule** — candidate only if a measured run shows
  instruction-strength fails; would join the v2 discussion, not precede it.
- **Probe-repertoire enumeration** beyond the one generic principle.
- **S2, S4, S5, S6 and the thirteen clarifications** — their own slices.
- **Run 2 itself** — still undecided; this design only makes it the designated
  measurement if it happens. The apparatus is versioned so the comparison is honest,
  and the expected observable is specific: run 1 contained zero grounding-class
  questions, so their presence and their yield are the delta to read.
