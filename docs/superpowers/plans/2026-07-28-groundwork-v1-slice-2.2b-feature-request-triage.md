# groundwork V1 — Slice 2.2b: the PM feature-request-triage vertical + the Motion pivot proof — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the runway's 2.2 by repeating the proven vertical for **product → feature-request triage** (deep record → work package → Owner's Card → captured baseline → provisioned), close the one concrete gap left in the canonical grammar by 2.2a's unreviewed final commit, and prove the **Motion pivot** on real content with the repo's first non-automation-path deep record.

**Architecture:** No new schema and no new check types. Three pieces: (1) the executive-view grammar stops allowing *reference-style* link syntax in a cell — closed by constraining the **file** (no link reference definitions) rather than the cell, which keeps `Coverage [EMEA]` legal while making every bracket provably literal; (2) the third worked vertical, mirroring renewal-prep; (3) one cheap `Motion: hire` deep record, which is the first acted-on activity that is *not* on the automation path and therefore requires only the common core.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **The canonical grammar constrains the FILE, not just the cell.** That is the doctrine 2.2a established: when a construct is ambiguous, remove the thing that makes it ambiguous rather than enumerating its spellings. Task 1 applies it once more; do not add per-bracket-form matching.
- **#5's Motion pivot is a ceiling, not a floor.** Substrate, Shape, and the eight Gate fields are required **only** when Motion is `automate` or `build`. A `hire` record carrying only the common core must be completely silent.
- **Codebase conventions:** reuse `Finding`, `_read_utf8`, `_load_frontmatter`, `_blank`, `DIRECTIONS`, `MOTIONS`, `AUTOMATION_MOTIONS`, `WORK_TYPES`, `SCORE_FIELDS`, `SCORE_VALUES`, `GATE_FIELDS`, `ACTION_CLASSES`.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.2a merged to `main` (`36a236c`; 524 tests, 1 designed skip, gate exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.2b-feature-request-triage
```

---

## Design calls flagged for the maintainer

**1. Task 1 exists because 2.2a's last commit (`cfd3bcc`) was never independently reviewed — and it has one real gap.**
Fable flagged this honestly: `cfd3bcc` fixed the blockers from a `DO NOT MERGE` verdict and then merged without a third pass, so the syntax-vs-character rule carries only self-verification. I read the commit and probed it directly. **The rule holds for everything it claims to catch** — inline links, images, and `**bold**` are all rejected, and `Coverage [EMEA]` and `SOC_2 compliance` are correctly accepted. `_EXEC_CELL_OK` still bans `<`, `>`, `|`, `\`, and backticks in `_canonical_row`, so that concern was unfounded.

The gap is **reference-style link syntax**. Verified by direct probe against the merged code:

| Cell | Result |
|---|---|
| `[Renewals](x.md)` | REJECTED ✓ |
| `![i](x.md)` | REJECTED ✓ |
| `**Renewals**` | REJECTED ✓ |
| `[Renewals][r]` | **accepted** as plain text ✗ |
| `[Renewals]` | **accepted** as plain text ✗ |

`_EXEC_LINKISH` matches only `](`, so the reference and shortcut forms slip through. They render as links whenever a link reference definition (`[r]: https://…`) sits elsewhere in the file — and a definition line carries no `|`, so today it is legal in an executive view. That is the same code-vs-documentation gap as findings 2–4 (`ontologies/README.md` promises "no link or image syntax"), in the very commit that fixed them.

*Severity, honestly:* low. Nothing reads the Activity string as a link, so the consequence is cosmetic. But this grammar's entire value proposition is that it is exact and documented-exact, so a documented restriction that does not hold is the one defect it cannot carry.

*The fix, and why it is not whack-a-mole:* do not enumerate bracket forms. **Forbid link reference definitions in an executive view.** Then no bracket in any cell can resolve to a link — `Coverage [EMEA]` stays legal *and becomes provably literal*, and `[Renewals][r]` is unambiguously text. One rule, one file-level constraint, class closed. Same move as banning stray `|` lines.

*My recommendation on the third Codex pass Fable offered:* skip it. A billable review of one commit buys less than folding the concrete finding into this slice, where it gets reviewed as part of a normal gate. The process point worth keeping, though: **the review gate's value is in the fix being reviewed, not just the finding being found** — a self-fixed blocker that ships unreviewed is the gate running at half strength. Worth deciding as a standing rule rather than per-slice.

**2. `feature-request-triage` is `reversible-write` — a second track-1 skill, deliberately.**
It writes tracker labels, dedupe links, and a triage note; it never replies to a customer, changes roadmap priority, or closes a request as won't-do. That is honestly `reversible-write`. *Counter-argument:* it duplicates renewal-prep's action class rather than covering new ground, and a triage agent that posted "thanks, we're tracking this" to a community forum would be `external-side-effect`. The boundary is therefore stated in the skill body and `forbidden_actions`, not just the frontmatter — the same discipline 2.2a used.

**3. One extra file: the first non-automation-path deep record — because the Motion pivot has never run on real content.**
Onboarding and renewal-prep are both `automate`. Every acted-on activity this repo has ever had is on the automation path, so #5's central pivot — *Substrate, Shape, and the eight Gate fields are required only for `automate`/`build`; buy, hire, and wait stay cheap at ~4 answers* — has only ever been exercised by fixtures. Engineering → **Technical hiring loops** (`Direction: up`, `Motion: hire`) is ~15 lines and proves it. It also demonstrates something the ontology should be able to say and currently cannot: **a deliberate decision not to build an agent.** An ontology that only ever records automation verdicts reads as an automation funnel. *Counter-argument:* it is one file beyond the runway's 2.2. Accepted — the cost is small and the alternative is a pivot nobody has watched work.

---

## File Structure

- `scripts/validate.py` — **modify.** Add `_LINK_REF_DEF` and the link-reference-definition ERROR to `parse_exec_table`.
- `tests/test_validate.py` — **modify.** Reference-link rejection tests plus the real-name regressions.
- `ontologies/README.md` — **modify.** State why brackets are literal.
- `ontologies/product/feature-request-triage.md` — **create.**
- `ontologies/product/_executive-view.md` — **modify.** Link the deep record.
- `skills/feature-request-triage/SKILL.md` — **create.**
- `skills/feature-request-triage/owner-card.md` — **create.**
- `memory/feature-request-triage-baseline.md` — **create.**
- `memory/_index.md` — **modify.**
- `ontologies/engineering/technical-hiring-loops.md` — **create.** The Motion-pivot proof.
- `ontologies/engineering/_executive-view.md` — **modify.** Link it.
- `AGENTS.md` — **modify.** Status: three worked verticals.

---

## Task 1: Close the bracket class

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`, `ontologies/README.md`

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`, inside `TestCanonicalExecTable`:

```python
    def test_link_reference_definition_is_rejected(self):
        # A definition makes every bracket in the file a potential link, so the
        # file — not the cell — is what gets constrained.
        _rows, findings = self._parse(
            "[r]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_link_reference_definition_after_the_table_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON + "\n[r]: https://example.com\n")
        self.assertTrue(any(f.level == "ERROR" and "link reference definition"
                            in f.message for f in findings))

    def test_indented_link_reference_definition_is_rejected(self):
        _rows, findings = self._parse("   [r]: https://example.com\n\n" + EXEC_CANON)
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_reference_link_cell_is_literal_text(self):
        # With definitions banned, this renders as text — so it parses, and the
        # Activity string is exactly what was written.
        rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| [Renewals][r] | up | — |"))
        self.assertEqual(findings, [])
        self.assertEqual(rows[0][0], "[Renewals][r]")

    def test_real_world_bracket_names_still_parse(self):
        for name in ("Coverage [EMEA]", "SOC_2 compliance", "Tier 1 [P0] escalations"):
            rows, findings = self._parse(
                EXEC_CANON.replace("| Discovery calls | up | — |",
                                   "| %s | up | — |" % name))
            self.assertEqual(findings, [], name)
            self.assertEqual(rows[0][0], name)

    def test_a_colon_in_prose_is_not_a_definition(self):
        _rows, findings = self._parse(
            "See the note [below]. Ratio 3:1 applies.\n\n" + EXEC_CANON)
        self.assertEqual(findings, [])
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestCanonicalExecTable -v`
Expected: the three `link_reference_definition` tests FAIL; the rest pass.

- [ ] **Step 3: Implement.** Add the pattern next to `_EXEC_EMPHASIS` in `scripts/validate.py`:

```python
# A link reference definition anywhere in the file makes every bracketed span in
# every cell a potential link. Rather than enumerate bracket spellings — the
# whack-a-mole this grammar exists to end — forbid the definition, which makes
# every bracket provably literal. That is what keeps "Coverage [EMEA]" legal.
_LINK_REF_DEF = re.compile(r"^ {0,3}\[[^\]]+\]:")
```

and in `parse_exec_table`, immediately after `lines = text.split("\n")` and before the `pipe_lines` scan:

```python
    for i, ln in enumerate(lines):
        if _LINK_REF_DEF.match(ln):
            findings.append(Finding(
                "ERROR", path, i + 1,
                "an executive view carries no link reference definition — it would make "
                "every bracketed cell a potential link; write the one Deep record link "
                "inline instead (#5 canonical form)"))
    if findings:
        return rows, findings
```

- [ ] **Step 4: Make the README precise.** In `ontologies/README.md`, replace the "Activity and Direction are **plain text**" bullet with:

```markdown
- Activity and Direction are **plain text** — no link or image syntax, no emphasis
  markers. Only the Deep record cell may carry markup. This bans the *syntax*, not the
  characters it is spelled with: `Coverage [EMEA]` and `SOC_2 compliance` are fine,
  while a link, an image, or `**Coverage**` is not. Square brackets stay literal
  because the file may not contain a link reference definition (a `[label]: url`
  line) — without one, no bracketed span can resolve to a link.
```

- [ ] **Step 5: Verify**

Run: `python3 -m unittest tests.test_validate.TestCanonicalExecTable tests.test_validate.TestExecTableHardening -v`
Expected: PASS.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0 — no executive view carries a definition line.

Run this probe to confirm the class is closed in both directions:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
hdr = '| Activity | Direction | Deep record |\n|---|---|---|\n'
must_pass = ['Coverage [EMEA]', 'SOC_2 compliance', '[Renewals][r]', '[Renewals]']
must_fail = ['[R](x.md)', '![i](x.md)', '**R**', '_R_']
for n in must_pass:
    r, f = validate.parse_exec_table(hdr + '| %s | up | — |\n' % n, 't.md')
    print('%-20s %s' % (n, 'ok' if not f else 'REGRESSION: rejected'))
for n in must_fail:
    r, f = validate.parse_exec_table(hdr + '| %s | up | — |\n' % n, 't.md')
    print('%-20s %s' % (n, 'ok (rejected)' if f else 'REGRESSION: accepted'))
r, f = validate.parse_exec_table('[r]: http://e.com\n\n' + hdr + '| A | up | — |\n', 't.md')
print('%-20s %s' % ('[r]: definition', 'ok (rejected)' if f else 'REGRESSION: accepted'))
PY
```

Expected: every line ends `ok`; no `REGRESSION`.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py ontologies/README.md
git commit -m "fix(validate): ban link reference definitions in executive views

Closes the last gap in the canonical cell rule: '[x][r]' and '[x]' rendered as
links whenever a definition sat elsewhere in the file, contradicting the README's
'no link syntax'. Constrains the FILE rather than enumerating bracket spellings,
so 'Coverage [EMEA]' stays legal and becomes provably literal.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The feature-request-triage deep record

**Files:** Create `ontologies/product/feature-request-triage.md`; modify `ontologies/product/_executive-view.md`

- [ ] **Step 1: Create `ontologies/product/feature-request-triage.md`:**

```markdown
---
activity: Feature-request triage
function: Product
motion: automate
score_repetition: high
score_risk: low
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: routing
accountable_owner: Director of Product
substrate: The issue tracker + the support-ticket system + CRM opportunity notes + the community forum
shape: single-agent
gate_inputs: Every feature request raised in the last week across support tickets, sales-call notes on CRM opportunities, and the community forum, plus the existing tracker items they might duplicate
gate_output: Each request filed in the tracker as a new item or linked to the one it duplicates, tagged by theme and customer segment, carrying the accounts that asked and the ARR they represent, and assigned to the owning PM
gate_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days, and every request in the tracker names the accounts it came from
gate_source_of_truth: The issue tracker for what is already known; the CRM for account and ARR attribution
gate_exception_path: A request that matches no existing theme and no owning PM is left unassigned and raised to the Director of Product rather than being forced into the nearest tag
gate_error_cost: A misfiled or wrongly deduplicated request loses a customer signal until someone notices it in the next review — recoverable by refiling, invisible to the customer
gate_owner: Director of Product
gate_review_gate: The owning PM confirms the theme and the duplicate link when the request reaches their queue
---
# Feature-request triage

**Direction: down.** Reading every incoming request, checking whether it is already
known, attaching who asked and what they are worth, and routing it to the right PM is
high-volume clerical work that produces no product judgment. It should stop being
hand-run so PM time goes to deciding what to build.

**Motion: automate.** Repetition is high, the sources are all systems of record, and
the failure mode is recoverable. Judgment scores **medium** and stays with a human:
this activity decides where a request *goes*, never whether it gets built.

## Accountability

Which business process runs differently: triage stops being a PM working through a
week of tickets, calls, and forum posts before they can think about the roadmap, and
becomes an agent that files, deduplicates, attributes, and routes — leaving anything
it cannot place unassigned and visible rather than guessing at a tag.

Who is accountable for proving it improved: the **Director of Product**, measured
against a baseline of triage latency and attribution completeness captured **before**
provisioning (the captured baseline is a governed org-memory record, and no skill
provisions for this activity without one — the #5 provisioning gate).
```

- [ ] **Step 2: Link it.** In `ontologies/product/_executive-view.md`, replace line 16 with:

```markdown
| Feature-request triage | down | [deep record](feature-request-triage.md) |
```

- [ ] **Step 3: Verify**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0. The deep record's common core and all eight Gate fields are complete, so #5 has nothing to warn about, and the exec-view link means no "not listed" WARN.

- [ ] **Step 4: Commit**

```bash
git add ontologies/product
git commit -m "feat(ontologies): product feature-request-triage deep record (#5 automation path)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The feature-request-triage work package

**Files:** Create `skills/feature-request-triage/SKILL.md` and `skills/feature-request-triage/owner-card.md`

> **Drift checks are exact-string.** The card's `owner` must equal the deep record's `accountable_owner` (`Director of Product`) and its `source_of_truth` must equal the deep record's `gate_source_of_truth`, character for character. Copy them; do not retype them.

- [ ] **Step 1: Create `skills/feature-request-triage/SKILL.md`:**

```markdown
---
name: feature-request-triage
description: File, deduplicate, and route each week's incoming feature requests to the owning PM with the accounts that asked
action_class: reversible-write
provisioned: yes
baseline: memory/feature-request-triage-baseline.md
ontology: ontologies/product/feature-request-triage.md
---
# Feature-request triage

Once a week, collect every feature request raised in support tickets, sales-call notes
on CRM opportunities, and the community forum. For each one: check whether the tracker
already knows it and link the duplicate if so, tag it by theme and customer segment,
attach the accounts that asked and the ARR they represent, and assign it to the PM who
owns that theme.

Leave what you cannot place. A request that matches no existing theme and no owning PM
stays unassigned and goes to the Director of Product. Forcing it into the nearest tag
is how a signal disappears — an unassigned request is visible, a mis-tagged one is not.

This skill decides where a request goes, never whether it gets built. It does not set
or change roadmap priority, close a request as won't-do, or reply to the person who
raised it ([ontology record](../../ontologies/product/feature-request-triage.md)).

## Harness requirements
- A governed pre-provisioning baseline for triage latency and attribution
  completeness: [memory/feature-request-triage-baseline.md](../../memory/feature-request-triage-baseline.md)
  (the `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the support-ticket system, CRM opportunities and their notes, and the
  community forum.
- Write access to the issue tracker limited to creating items, editing labels and
  assignees, and adding duplicate links and triage notes.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. It is classified
  `reversible-write` because every write lands on an internal tracker item and is
  undone by relabelling or unlinking. Nothing it writes reaches the person who raised
  the request. Granting it the ability to comment on a public forum thread, close
  requests, or change priority would make it `external-side-effect` or higher, and the
  classification and Owner's Card would have to change before that shipped.
- Read-only access to the three source systems is a hard requirement, not a
  preference. A deployment that lets it edit CRM records breaks the claim above.

## Memory row
- **Reads:** the pre-provisioning triage baseline (latency, attribution completeness).
- **Writes:** a weekly note recording how many requests were filed, deduplicated, and
  left unassigned (observed provenance).
- **Run-only:** the per-request candidate-duplicate scores.

## Portability check

*If I had to move this skill tomorrow, what would break?* The tracker, support-system,
CRM, and forum connectors; the governed baseline record; the theme-to-PM ownership map
the assignment step reads; and the PM confirmation gate named in the Owner's Card.
```

- [ ] **Step 2: Create `skills/feature-request-triage/owner-card.md`:**

```markdown
---
owner: Director of Product
backup_owner: Principal Product Manager
job: File, deduplicate, and route each week's feature requests to the PM who owns the theme
action_class: reversible-write
allowed_actions: read support tickets, CRM opportunity notes, and community-forum posts; create tracker items; set labels, segments, and assignees; add duplicate links and triage notes
proposed_only_actions: merge two existing tracker items as duplicates after the owning PM confirms
forbidden_actions: set or change roadmap priority; close a request as won't-do; reply to the person who raised a request; edit CRM records
pause_condition: the tracker or CRM is unreachable; a request matches no existing theme and no owning PM; the theme-to-PM ownership map is stale or missing
retirement_condition: the tracker ships native deduplication and attribution the team trusts more, or requests stop arriving through three separate systems
source_of_truth: The issue tracker for what is already known; the CRM for account and ARR attribution
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; near-duplicate requests that use different vocabulary can be filed twice, which is why the weekly note reports the unassigned and duplicate counts
last_reviewed: 2026-07-27
next_review: 2026-10-27
success_standard: Every request raised in a week is filed, deduplicated, and assigned within five business days with its asking accounts attached, measured against the pre-provisioning baseline
evidence_required: The weekly triage note with filed, deduplicated, and unassigned counts, and the per-request duplicate links
sources_must_not_use: A PM's recollection or a Slack thread as evidence that a request is already tracked
review_sample: The owning PM confirms theme and duplicate link on every request that reaches their queue; the Director reviews the unassigned pile weekly
---
# Owner's Card — Feature-request triage

The **Director of Product** owns this skill; the **Principal Product Manager** is the
backup. It routes requests and stops there — it may not set priority, close a request,
or reply to whoever raised it. Merging two existing items is proposed-only and waits
on the owning PM.

The boundary is what keeps this skill track 1: every write lands on an internal tracker
item and is undone by relabelling or unlinking, and nothing reaches the requester. If
it is ever given a path to a public thread or the ability to close requests, it becomes
an external-side-effect skill and this card must be rewritten before that ships.

It leaves what it cannot place rather than guessing, because an unassigned request is
visible and a mis-tagged one is not. The PM confirmation on each request is the review
gate; the Director's weekly pass over the unassigned pile is the quality check.
```

- [ ] **Step 3: Verify the drift checks**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected at this point: **ERROR** — `provisioned: yes` cites `memory/feature-request-triage-baseline.md`, which Task 4 creates. That is the #5 provisioning gate working as designed and it clears next task. Confirm the message names the baseline, and confirm **no drift ERROR** on `action_class`, `owner`, or `source_of_truth` — those would mean a copy mismatch to fix now.

- [ ] **Step 4: Commit**

```bash
git add skills/feature-request-triage
git commit -m "feat(skills): feature-request-triage work package + Owner's Card

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The captured baseline and the index

**Files:** Create `memory/feature-request-triage-baseline.md`; modify `memory/_index.md`

- [ ] **Step 1: Create `memory/feature-request-triage-baseline.md`:**

```markdown
---
provenance: observed
owner: Director of Product
valid_at: 2026-07-22
review_by: 2026-10-22
source: The product team's Q2 2026 tracker export (214 requests, Apr–Jun 2026)
---
# Feature-request-triage baseline (pre-provisioning)

Captured before the feature-request-triage skill was provisioned, so its improvement
can be proven rather than assumed (#5 provisioning gate).

- Median time from a request being raised to being filed and assigned: **11 business
  days**.
- Requests filed within five business days: **63 of 214**.
- Filed requests naming the accounts that asked: **48 of 214**; the rest carried no
  attribution, so no one could weigh them by revenue.
- Duplicates found only at quarterly review rather than at triage: **29**.
```

- [ ] **Step 2: Add it to `memory/_index.md`**, below the existing two entries:

```markdown
- [Feature-request-triage baseline (pre-provisioning)](feature-request-triage-baseline.md) — Director of Product — observed
```

- [ ] **Step 3: Verify**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0. The Task 3 provisioning ERROR clears; the third live record is indexed, so no "live record not in index" WARN; the card is fresh, so no staleness WARN.

- [ ] **Step 4: Commit**

```bash
git add memory
git commit -m "feat(memory): feature-request-triage captured baseline + index entry

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: The Motion pivot proof — a non-automation-path deep record

**Files:** Create `ontologies/engineering/technical-hiring-loops.md`; modify `ontologies/engineering/_executive-view.md`, `AGENTS.md`

> **What this task is testing.** Every acted-on activity in this repo so far is `Motion: automate`. #5's pivot says Substrate, Shape, and the eight Gate fields are required **only** on the automation path, and that buy/hire/wait stay cheap at about four answers. That branch has never run on real content. This record is the probe.

- [ ] **Step 1: Create `ontologies/engineering/technical-hiring-loops.md`:**

```markdown
---
activity: Technical hiring loops
function: Engineering
motion: hire
score_repetition: medium
score_risk: high
score_judgment: high
score_company_specificity: high
score_market_maturity: low
work_type: accountability
accountable_owner: VP Engineering
---
# Technical hiring loops

**Direction: up.** Interviewing deserves *more* engineering time, not less. It is the
decision with the longest half-life the function makes, and the cost of getting it
wrong is paid for years.

**Motion: hire.** Repetition is only medium and every other score points away from
automation: risk is high, judgment is high, the loop is highly specific to how this
company works, and the market for tooling here is immature. The verdict is to invest
in people running the loop well — a hiring-ops partner and trained interviewers —
not to build an agent.

**This record carries no Substrate, Shape, or Describability Gate, and that is
correct.** Those fields are required only on the automation path (`automate` or
`build`). Recording a verdict of `hire` is a complete answer, and the ontology is not
an automation funnel: an activity worked to the point of a deliberate *no* is worked,
not unfinished.

## Accountability

Which business process runs differently: nothing is automated here. What changes is
that the loop now has a named owner and a scored verdict on the record, so the next
person who proposes automating interview scheduling can see why it was declined and
what would have to change first.

Who is accountable: the **VP Engineering**. No skill is generated for this activity, so
no captured baseline is required — the #5 provisioning gate binds skills, not verdicts.
```

- [ ] **Step 2: Link it.** In `ontologies/engineering/_executive-view.md`, replace line 15 with:

```markdown
| Technical hiring loops | up | [deep record](technical-hiring-loops.md) |
```

- [ ] **Step 3: Verify the pivot — this is the point of the task**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0 — **completely silent on the new record.**

Read the result carefully rather than just checking the exit code:

- If a **WARN or ERROR names `technical-hiring-loops.md` and mentions `substrate`, `shape`, or a `gate_` field**, the Motion pivot is not implemented as #5 specifies — automation-path fields are being demanded of a `hire` record. That is a real bug in `check_deep_record`, and fixing it (guarding those requirements behind `motion in AUTOMATION_MOTIONS`) **is in scope for this task**, with a regression test asserting a `hire` record with only the common core is silent. Proving the pivot is why this record exists.
- If a WARN names a **common-core** field (motion, a score, work type, accountable owner), that is a content bug — fill the field.

Run this to confirm the branch was genuinely exercised, not skipped:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
p = 'ontologies/engineering/technical-hiring-loops.md'
f = validate.check_deep_record(p, '.')
print('findings:', [(x.level, x.message) for x in f] or 'none')
data, _ = validate._load_frontmatter(p, p)
print('motion:', data.get('motion'), '| automation path:',
      data.get('motion') in validate.AUTOMATION_MOTIONS)
print('gate fields present:', [g for g in validate.GATE_FIELDS if g in data] or 'none')
PY
```

Expected: `findings: none`, `motion: hire | automation path: False`, `gate fields present: none`.

- [ ] **Step 4: Update `AGENTS.md`.** In the "Built and working" list, replace the `ontologies/` and `skills/` bullets with:

```markdown
- `ontologies/` — the two-tier ontology schema, all 8 function executive views, and
  four worked deep records: three on the automation path (People/HR onboarding,
  customer-success renewal prep, product feature-request triage) and one recording a
  deliberate decision *not* to automate (engineering hiring loops, `Motion: hire`).
- `skills/` — the work-package convention and three worked packages: one
  external-side-effect (`onboarding-orchestration`) and two reversible-write
  (`renewal-prep`, `feature-request-triage`), each with its `SKILL.md` and
  `owner-card.md`.
```

and replace the `memory/` bullet with:

```markdown
- `memory/` — the org-memory record schema with three captured baselines and an index.
```

- [ ] **Step 5: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0 — the new memory record is an addition, and the engine carries no `groundwork.pin`, so the #18 tripwire stays dormant.

Run the per-function parse report to confirm no view regressed:

```bash
python3 - <<'PY'
import sys, os; sys.path.insert(0, 'scripts'); import validate
for fn in sorted(os.listdir('ontologies')):
    p = os.path.join('ontologies', fn, '_executive-view.md')
    if os.path.isfile(p):
        r, f = validate.parse_exec_table(open(p, encoding='utf-8').read(), p)
        print('%-18s %2d activities, %d findings' % (fn, len(r), len(f)))
PY
```

Expected: 8 functions, 10 activities each, 0 findings each.

- [ ] **Step 6: Commit**

```bash
git add ontologies/engineering AGENTS.md
git commit -m "feat(ontologies): engineering hiring loops — the first non-automation-path record

Motion: hire, common core only. Proves #5's pivot on real content: Substrate,
Shape, and the Describability Gate are required only for automate/build, and an
activity worked to a deliberate 'no' is worked, not unfinished.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **Phase 2.3 (`demo/`) is next:** the pre-installed synthetic ~20-person B2B SaaS, the 15-minute 3-query script including the rung-5 governance block (#4), demo canon + the #16 synthetic-identifier check, the meeting-challenger runnable exemplar (#8 item 3), and the demo's real `groundwork.pin` — which is where the #18 tripwire and the #21 skew gate stop being dormant, and where a live proposal and a changelog entry can legitimately exist.
- **No new check types.** Task 1 adds one rule to an existing grammar; Task 5 may correct an existing check if the pivot proves broken, but adds nothing.
- **No `demo/`-scoped content.** The three worked verticals stay engine exemplars.
- **Still open for the maintainer:** the four Slice 1.5d-ii deferrals, the `SKIP_RELPATHS` gate-scoping sign-off, and the standing question of whether a self-fixed review blocker must be re-reviewed before merge (Design call 1).

## Self-Review

- **Ticket coverage:** #5 automation path (common core + Substrate + Shape + 8 Gate fields) → the triage deep record; **#5 Motion pivot** (buy/hire/wait need only the common core) → the hiring-loops record, exercised on real content for the first time; #5 provisioning gate → the captured baseline the skill cites; #6 card spine, track-2 trio, and the three drift checks → `owner-card.md`; #7 record shape + index → the baseline and `_index.md`; #11's restricted-grammar doctrine → extended once more, at the file level.
- **The unreviewed commit was checked, not assumed.** Design call 1 reports a direct probe of `cfd3bcc` against the merged code, in both directions: what it correctly rejects and what it wrongly accepts. The inline-link, image, and emphasis rules hold; only the reference forms leak. That claim is measured, not inferred.
- **Placeholder scan:** no TBD/TODO; every file's content and every code change is given in full, with verification commands and expected output — including the deliberate red gate in Task 3 Step 3.
- **Type consistency:** `parse_exec_table(text, path)` → `(rows, findings)` unchanged; `_LINK_REF_DEF` is a module-level compiled pattern beside its siblings; `Finding(level, path, line, message)` throughout. No new imports, no signature changes.
- **Pre-empts the recurring Codex findings.** (a) *Fail-open on malformed input* — the definition check runs before the table scan and returns early, so a file carrying one is rejected outright rather than parsed and then flagged. (b) *Whack-a-mole* — the fix constrains the file, so no future bracket spelling reopens the class; the probe in Task 1 Step 5 asserts both directions, so an over-tightening that rejects `Coverage [EMEA]` fails loudly (that regression is exactly what the 2.2a re-review caught). (c) *Non-scalar frontmatter* — new records use scalars only; existing guards cover them unchanged. (d) *Corpus void* — Task 5's probe prints the motion, the automation-path boolean, and the gate fields present, so "the check was silent" is distinguished from "the check never ran."
- **The extra file is justified and its cost stated:** the hiring-loops record is one file beyond the runway's 2.2, and it exists because #5's central pivot has only ever been tested by fixtures.
