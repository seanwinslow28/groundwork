# groundwork V1 — Slice 2.2a: the canonical executive-view grammar + the CS renewal-prep vertical — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** End the GFM-exactness treadmill by replacing the executive-view table parser with a **restricted canonical grammar** — the doctrine #11 already locked for frontmatter, applied to the repo's second structured surface — and then repeat the proven vertical for **customer success → renewal preparation**: deep record → work package → Owner's Card → captured baseline → provisioned.

**Architecture:** `parse_exec_table` stops emulating GFM and starts *defining* a format. An `_executive-view.md` holds exactly one table in exactly one shape; anything else is an ERROR. The ~150 lines of accreted GFM emulation (`_parse_exec_tables`, `_split_cells`, `_cell_link`, `_is_separator`, `_QUOTE_PREFIX`, `_INLINE_TAG`, and `_strip_code`'s `table_mode` branch) retire, and every adversarial input those 8 rounds discovered is **kept as a rejection test**. Then the content: renewal-prep becomes the repo's first **track-1** (`reversible-write`) provisioned skill, which is the piece the #17/#18 auto-apply path has never had.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **The 32 rounds of adversarial inputs are not discarded — they are converted.** Every input Codex found must survive in the test file, asserting **rejection** instead of asserting a parse result. Proving a decoy table is *refused* is strictly stronger than proving it is parsed a particular way. The test count for the table classes must not drop.
- **#5 severity contract is a ceiling.** ERROR only where a field backs running machinery; WARN on incomplete thinking about an acted-on activity; silent on untouched worksheets.
- **Codebase conventions:** reuse `Finding`, `_read_utf8`, `_load_frontmatter`, `_blank`, `_parse_date`, `DIRECTIONS`, `MOTIONS`, `WORK_TYPES`, `SHAPES`, `SCORE_FIELDS`, `SCORE_VALUES`, `GATE_FIELDS`, `ACTION_CLASSES`.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.1 merged to `main` (`5fc61c6`; 492 tests, 1 designed skip, gate exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.2a-renewal-prep
```

---

## Design calls flagged for the maintainer

**1. The canonical-form pin — and why it is *not* a new check type.**
Fable framed this as exceeding the "no new check types" clause and needing sign-off. I think the framing understates the case in one direction and overstates it in the other, so here it is precisely.

*The root cause of 32 rounds.* There are two kinds of parser in this repo. The **hook's regex floor** (1.5b) reads adversary-supplied shell commands — input groundwork does not control — so its false-negative supply is unbounded and the honest stopping rule is "the artifact's documented posture, not review silence." The **frontmatter reader** (#11) reads a file groundwork's own generator writes — input groundwork *does* control — so its rule is a restricted grammar where "any other syntax ERRORs." The executive-view table is squarely in the second category and was built like the first. That mismatch is why rounds 24–32 kept finding divergences, and why round 33 would find more: GFM is a large spec and each round only closes the case it found.

*So this is not a new doctrine.* It is the repo's own locked #11 doctrine applied to the second structured surface — the only one that tried to be permissive. Applying it makes the two structured readers consistent rather than adding a third philosophy.

*What it buys.* The round-32 list — delimiter arity and position, `||` boundary pipes, duplicate `Direction` columns, span-vs-cell precedence, indented tables, Activity-column deletion — plus the earlier classes (decoy tables, fenced and comment-wrapped examples, blockquoted rows, no-leading-pipe rows) all stop being *handled* and become *unreachable*. There is nothing to disambiguate when only one shape is legal. ~150 lines retire.

*The honest cost, which is real.* Benign formatting variance becomes a gate failure: reordering the columns, using `| :--- |` alignment, indenting the table, or writing a row without a trailing pipe all ERROR. #11 already accepted exactly this trade for frontmatter. The mitigation is that the error messages name the canonical form, and `ontologies/README.md` shows it.

*My recommendation:* take it. The alternative — "accept and document the residuals" — leaves a check whose failures are accident-shaped (a typo in a header silently disabling every Direction check in the file) sitting under a severity contract that says machinery-backing fields must ERROR.

**2. Renewal-prep is `reversible-write` — deliberately the repo's first track-1 skill.**
Onboarding is `external-side-effect` (track 2), so every governance path the repo exercises today is the escalating one. Nothing has ever exercised **track 1**: the auto-apply boundary, the changelog entry requirement, and the `track1-body` branch of the #18 tripwire have only ever run against fixtures. Scoping renewal-prep as *assemble the brief, do not send it or change the contract record* makes it genuinely `reversible-write` and gives that half of the governance model real content. *Counter-argument:* it is a modelling choice, and a renewal-prep agent that wrote back to the CRM would be track 2 — so the scoping has to be honest in the skill body, not just in the frontmatter. The plan's content states the boundary explicitly in `allowed_actions` and `forbidden_actions`.

**3. Only CS renewal-prep lands here; PM feature-request-triage is 2.2b.**
The runway lists both as one item. In Phase 1 a single function's vertical took three slices (1.2 ontology, 1.3 skill + card, 1.4 baseline + provisioning). The schema is proven now so this is content rather than discovery, but two full verticals plus a parser replacement in one session is how a slice turns into another 32-round evening. One vertical per slice.

---

## File Structure

- `scripts/validate.py` — **modify.** Replace `parse_exec_table` with the canonical grammar; delete `_parse_exec_tables`, `_split_cells`, `_cell_link`, `_is_separator`, `_QUOTE_PREFIX`, `_INLINE_TAG`, and `_strip_code`'s `table_mode` branch; update `check_ontology`'s exec-view branch.
- `tests/test_validate.py` — **modify.** Convert the table-parsing tests to rejection tests; keep every adversarial input.
- `ontologies/customer-success/renewal-prep.md` — **create.** The deep record.
- `ontologies/customer-success/_executive-view.md` — **modify.** Link the deep record.
- `skills/renewal-prep/SKILL.md` — **create.**
- `skills/renewal-prep/owner-card.md` — **create.**
- `memory/renewal-prep-baseline.md` — **create.**
- `memory/_index.md` — **modify.** List the new live record.
- `ontologies/README.md` — **modify.** Document the canonical table form.
- `AGENTS.md` — **modify.** Status list: two worked verticals.

---

## Task 1: The canonical executive-view grammar

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:** `parse_exec_table(text, path="<unknown>")` now returns `(rows, findings)` — rows are `(activity, direction_lower, deep_link_or_None, line_no)`.

- [ ] **Step 1: Inventory what you are about to change.** Before editing, capture the baseline so nothing is dropped silently:

```bash
cd "$(git rev-parse --show-toplevel)"
grep -c "def test_" tests/test_validate.py
awk '/^class TestExecTable\b/,/^class TestOntology\b/' tests/test_validate.py | grep -c "def test_"
awk '/^class TestExecTableHardening\b/,/^class TestAggregateListingFailures\b/' tests/test_validate.py | grep -c "def test_"
```

Record all three numbers. The first must not decrease by the end of this task; the second and third are the classes you are converting.

- [ ] **Step 2: Add the canonical-grammar tests** to `tests/test_validate.py`. These are new and must fail first:

```python
EXEC_CANON = (
    "# Sales — executive view\n\n"
    "Frame paragraph.\n\n"
    "| Activity | Direction | Deep record |\n"
    "|---|---|---|\n"
    "| Discovery calls | up | — |\n"
    "| Forecast roll-up | down | [deep record](forecast.md) |\n"
)


class TestCanonicalExecTable(unittest.TestCase):
    def _parse(self, text):
        return validate.parse_exec_table(text, "x.md")

    def test_canonical_table_parses(self):
        rows, findings = self._parse(EXEC_CANON)
        self.assertEqual(findings, [])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][:3], ("Discovery calls", "up", None))
        self.assertEqual(rows[1][2], "forecast.md")

    def test_spaced_delimiter_is_accepted(self):
        rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|",
                                                        "| --- | --- | --- |"))
        self.assertEqual(findings, [])
        self.assertEqual(len(rows), 2)

    # --- the round-32 six, now unreachable rather than handled ---

    def test_alignment_colons_are_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|",
                                                         "|:---|---:|---|"))
        self.assertTrue(any(f.level == "ERROR" and "delimiter" in f.message
                            for f in findings))

    def test_wrong_delimiter_arity_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|", "|---|---|"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_missing_delimiter_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON.replace("|---|---|---|\n", ""))
        self.assertTrue(any(f.level == "ERROR" and "delimiter" in f.message
                            for f in findings))

    def test_boundary_double_pipe_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "|| Discovery calls | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_duplicate_direction_column_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Activity | Direction | Deep record |",
                               "| Activity | Direction | Direction |"))
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_deleted_activity_column_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Activity | Direction | Deep record |",
                               "| Direction | Deep record |"))
        self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                            for f in findings))

    def test_indented_table_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "    | Discovery calls | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    # --- the earlier classes, likewise ---

    def test_second_table_anywhere_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON + "\n| Other | table |\n")
        self.assertTrue(any(f.level == "ERROR" and "exactly one" in f.message
                            for f in findings))

    def test_fenced_example_table_is_rejected(self):
        # No fence awareness: any '|' outside the one table is an error, so a
        # fenced example cannot shadow or decoy anything.
        _rows, findings = self._parse(
            EXEC_CANON + "\n```\n| Activity | Direction |\n```\n")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_blockquoted_row_is_rejected(self):
        _rows, findings = self._parse(EXEC_CANON + "\n> | a | b | c |\n")
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_no_leading_pipe_row_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "Discovery calls | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_html_comment_in_a_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| <!--x--> | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_escaped_pipe_in_a_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| Quote \\| order | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_code_span_in_a_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |",
                               "| `Discovery` | up | — |"))
        self.assertTrue(any(f.level == "ERROR" for f in findings))

    def test_image_in_deep_record_cell_is_rejected(self):
        _rows, findings = self._parse(
            EXEC_CANON.replace("[deep record](forecast.md)",
                               "![img](forecast.md)"))
        self.assertTrue(any(f.level == "ERROR" and "Deep record" in f.message
                            for f in findings))

    def test_empty_activity_still_parses_as_a_row(self):
        # The empty-Activity ERROR belongs to check_ontology; the row must reach it.
        rows, findings = self._parse(
            EXEC_CANON.replace("| Discovery calls | up | — |", "|  | up | — |"))
        self.assertEqual(findings, [])
        self.assertEqual(rows[0][0], "")

    def test_no_table_at_all_is_not_a_parse_error(self):
        # Absence is check_ontology's call (an untouched worksheet stays silent).
        rows, findings = self._parse("# Sales\n\nProse only.\n")
        self.assertEqual((rows, findings), ([], []))
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestCanonicalExecTable -v`
Expected: FAIL — `parse_exec_table()` takes 1 positional argument / returns a list, not a tuple.

- [ ] **Step 4: Replace the parser.** In `scripts/validate.py`, **delete** `_split_cells`, `_QUOTE_PREFIX`, `_INLINE_TAG`, `_is_separator`, `_cell_link`, `_parse_exec_tables`, and the old `parse_exec_table` wrapper — the whole span from `def _split_cells(line):` through the end of the `parse_exec_table` wrapper. Put this in their place:

```python
_EXEC_HEADER = ("activity", "direction", "deep record")
_EXEC_DELIM_CELL = re.compile(r"^-{3,}$")
# canonical cells are plain text: no inline markup, no escapes, no cell pipes
_EXEC_CELL_OK = re.compile(r"^[^<>|\\`]*$")
_EXEC_LINK = re.compile(r"^\[[^\[\]]+\]\(([^()\s]+)\)$")
_EXEC_NO_RECORD = {"—", "–", "-", ""}


def _canonical_row(line):
    """The three cells of one canonical table line, or None when the line is not
    canonical: it must start with '|', end with '|', hold exactly three cells
    between them, and carry no escapes or inline markup. Leading whitespace is
    NOT tolerated — an indented line is a code block to a markdown reader."""
    s = line.rstrip()
    if len(s) < 2 or not s.startswith("|") or not s.endswith("|"):
        return None
    cells = [c.strip() for c in s[1:-1].split("|")]
    if len(cells) != 3 or not all(_EXEC_CELL_OK.match(c) for c in cells):
        return None
    return cells


def parse_exec_table(text, path="<unknown>"):
    """Parse the ONE canonical executive-view table. Returns (rows, findings);
    rows are (activity, direction_lower, deep_link_or_None, line_no).

    DOCTRINE — #11 applied to the second structured surface. This is a
    RESTRICTED GRAMMAR, not a markdown-table parser. groundwork owns this format
    (its own generator writes it), so the honest design is to define one exact
    shape and ERROR on everything else, exactly as the frontmatter reader does:
    "any other syntax ERRORs". Emulating GFM here cost eight review rounds and
    still diverged, because GFM is a large spec and each round only closes the
    case it found. Under a canonical grammar the whole class — decoy tables,
    fenced or comment-wrapped examples, blockquoted or non-leading-pipe rows,
    delimiter arity and position, boundary pipes, duplicate columns, span-vs-cell
    precedence, indentation, column deletion — is not handled. It is unreachable.

    Absence of a table is NOT a finding here; check_ontology decides whether an
    empty worksheet is silent (#5) or a missing table is an error."""
    rows, findings = [], []
    lines = text.split("\n")
    pipe_lines = [i for i, ln in enumerate(lines) if "|" in ln]
    if not pipe_lines:
        return rows, findings

    start = pipe_lines[0]
    end = start
    while end + 1 < len(lines) and "|" in lines[end + 1]:
        end += 1
    if pipe_lines[-1] != end:
        findings.append(Finding(
            "ERROR", path, pipe_lines[-1] + 1,
            "an executive view holds exactly one activity table; this line carries a "
            "'|' outside it (#5 canonical form)"))
        return rows, findings

    header = _canonical_row(lines[start])
    if header is None or tuple(c.lower() for c in header) != _EXEC_HEADER:
        findings.append(Finding(
            "ERROR", path, start + 1,
            "executive-view table header must be exactly "
            "'| Activity | Direction | Deep record |' (#5 canonical form)"))
        return rows, findings

    if end < start + 2:
        findings.append(Finding(
            "ERROR", path, start + 1,
            "executive-view table needs its delimiter row and at least one activity "
            "row (#5 canonical form)"))
        return rows, findings

    delim = _canonical_row(lines[start + 1])
    if delim is None or not all(_EXEC_DELIM_CELL.match(c) for c in delim):
        findings.append(Finding(
            "ERROR", path, start + 2,
            "the row under the header must be the delimiter '|---|---|---|' — no "
            "alignment colons, exactly three cells (#5 canonical form)"))
        return rows, findings

    for j in range(start + 2, end + 1):
        cells = _canonical_row(lines[j])
        if cells is None:
            findings.append(Finding(
                "ERROR", path, j + 1,
                "executive-view row is not canonical — exactly three plain-text cells "
                "between a leading and a trailing '|' (#5 canonical form)"))
            continue
        activity, direction, deep = cells
        link = None
        if deep not in _EXEC_NO_RECORD:
            m = _EXEC_LINK.match(deep)
            if m is None:
                findings.append(Finding(
                    "ERROR", path, j + 1,
                    "Deep record cell must be '—' or exactly one link '[text](path)' "
                    "(#5 canonical form)"))
                continue
            link = m.group(1)
        rows.append((activity, direction.lower(), link, j + 1))
    return rows, findings
```

- [ ] **Step 5: Retire `_strip_code`'s `table_mode`.** `table_mode=True` had exactly one caller — the parser you just deleted. Confirm and remove:

Run: `grep -n "table_mode" scripts/validate.py`
Expected after the parser replacement: only the definition and its internal branches remain (no call site passing `True`).

Then delete the `table_mode` parameter and every `if table_mode:` branch, restoring `_strip_code(text)` to the import-only scanner Move 2 and Slice 2.1 built. **Do not touch** the fence/span scanning itself — `TestStripCode` is its regression proof and must stay green.

- [ ] **Step 6: Update `check_ontology`'s executive-view branch.** Replace the `rows = ...` line and the "no parsable activity table" ERROR with:

```python
            rows, table_findings = ((), [])
            if exec_text is not None:
                rows, table_findings = parse_exec_table(exec_text, rel_exec)
            findings += table_findings
            if exec_text is not None and exec_text.strip() and not rows \
                    and not table_findings:
                findings.append(Finding("ERROR", rel_exec, None,
                                        "executive view has no activity table — a canonical "
                                        "'| Activity | Direction | Deep record |' table with at "
                                        "least one row is required (#5 exec tier)"))
```

The `for activity, direction, link, ln in rows:` loop below it is unchanged.

- [ ] **Step 7: Convert the old table tests to rejection tests.** Work through `TestExecTable` (around line 246) and `TestExecTableHardening` (around line 4054). For each test:

  - **Keep the input string verbatim.** It is the artifact of a real review round; it must stay in the file.
  - If the input is the canonical shape, update the call to the new two-value return and keep the assertion.
  - If the input is anything else — a decoy header, a fenced or commented example, a blockquoted table, a no-leading-pipe row, an escaped pipe, an image link, a shadowed table, a missing delimiter — change the assertion to: parsing yields **an ERROR finding**, and no rows are silently accepted from it. Rename the test to say what it rejects (e.g. `test_decoy_header_table_is_rejected`).
  - Delete a test only if its input is now *byte-identical* to another test's; note any such merge in the commit message.

- [ ] **Step 8: Verify no coverage was dropped**

Run: `grep -c "def test_" tests/test_validate.py`
Expected: **greater than or equal to** the number recorded in Step 1. If it is lower, you deleted adversarial coverage — restore it as a rejection test.

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0 — **all eight existing executive views must satisfy the canonical form.** If one does not, fix the *view* to be canonical; do not loosen the grammar.

Run: `python3 -c "
import sys, os; sys.path.insert(0, 'scripts'); import validate
for fn in sorted(os.listdir('ontologies')):
    p = os.path.join('ontologies', fn, '_executive-view.md')
    if os.path.isfile(p):
        r, f = validate.parse_exec_table(open(p, encoding='utf-8').read(), p)
        print('%-18s %2d activities, %d findings' % (fn, len(r), len(f)))
"`
Expected: 8 functions, 10 activities each, **0 findings** each.

- [ ] **Step 9: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "refactor(validate): canonical executive-view grammar, retiring GFM emulation

#11's restricted-grammar doctrine applied to the second structured surface.
One legal table shape; everything else ERRORs. The decoy/fence/blockquote/
delimiter/boundary-pipe/duplicate-column/indent classes become unreachable
rather than handled. Every adversarial input from rounds 24-32 is kept as a
rejection test.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The renewal-prep deep record

**Files:** Create `ontologies/customer-success/renewal-prep.md`; modify `ontologies/customer-success/_executive-view.md`, `ontologies/README.md`

- [ ] **Step 1: Create `ontologies/customer-success/renewal-prep.md`:**

```markdown
---
activity: Renewal preparation
function: Customer success
motion: automate
score_repetition: high
score_risk: low
score_judgment: medium
score_company_specificity: medium
score_market_maturity: medium
work_type: sensemaking
accountable_owner: VP Customer Success
substrate: The CRM opportunity and contract records + the product-usage warehouse + the support-ticket system
shape: single-agent
gate_inputs: The renewing account's contract terms and renewal date from the CRM, its last-90-day product usage, its open and recently closed support tickets, and the notes from the most recent business review
gate_output: A renewal brief in the CS workspace — contract terms, usage trend against the account's own history, support history, named risks, and an expansion or contraction read — with every claim linked to the record it came from
gate_standard: Every renewal has a brief in the CSM's hands 45 days before the renewal date, and every number in it resolves to a source record
gate_source_of_truth: The CRM contract record for terms and dates; the usage warehouse for product adoption
gate_exception_path: A missing or contradictory contract record, or usage data more than seven days stale, halts the brief and routes to the VP Customer Success rather than shipping a brief with a gap in it
gate_error_cost: A wrong or missing brief sends a CSM into a renewal conversation underprepared — costly if it goes unnoticed, but caught by the CSM's own review before any customer sees it
gate_owner: VP Customer Success
gate_review_gate: The account's CSM reads the brief and confirms it matches what they know before the renewal conversation
---
# Renewal preparation

**Direction: down.** Assembling the picture before a renewal — pulling contract terms,
reading the usage trend, re-reading the support history — is hours of gathering that
produces no judgment. It should stop being hand-run so the CSM's time goes to the
renewal conversation itself.

**Motion: automate.** Repetition is high and the sources are all systems of record.
Judgment scores **medium**, and that is the point of the boundary: the *gathering* is
mechanical, the *decision* is not. This activity ends at a brief a human reads; it
never decides the renewal, prices it, or contacts the customer.

## Accountability

Which business process runs differently: renewal prep stops being a CSM working
through four systems the week before a renewal and becomes an agent that assembles a
sourced brief 45 days out, halting to a human when a record is missing or stale rather
than filling the gap with an assumption.

Who is accountable for proving it improved: the **VP Customer Success**, measured
against a baseline of brief lead time and sourcing completeness captured **before**
provisioning (the captured baseline is a governed org-memory record, and no skill
provisions for this activity without one — the #5 provisioning gate).
```

- [ ] **Step 2: Link it from the executive view.** In `ontologies/customer-success/_executive-view.md`, replace the renewal row with:

```markdown
| Renewal preparation | down | [deep record](renewal-prep.md) |
```

- [ ] **Step 3: Document the canonical table form** in `ontologies/README.md`. Add this section immediately after the "The two tiers (#5)" section:

```markdown
## The executive-view table has exactly one legal shape

The validator does not parse markdown tables generously — it accepts one canonical
form and ERRORs on everything else, the same way the frontmatter reader accepts one
restricted grammar (#11). This is a format groundwork writes, so defining it beats
guessing at it.

```
| Activity | Direction | Deep record |
|---|---|---|
| Some activity | down | — |
| Another activity | up | [deep record](another-activity.md) |
```

- The header row is exactly those three columns, in that order.
- The delimiter row comes immediately after it: three cells of three-or-more dashes,
  no alignment colons.
- Every row starts and ends with `|` and has exactly three cells, unindented.
- Cells are plain text — no code spans, HTML, escaped pipes, or images.
- The Deep record cell is `—` or exactly one link.
- The file contains **one** such table and no other line carrying a `|`.
```

- [ ] **Step 4: Verify**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s)`, exit 0. A WARN appears: `ontologies/customer-success/renewal-prep.md  deep record not listed in the executive view` must **not** appear — Step 2 links it. What *will* be silent is the deep record itself: its common core and Gate are complete, so #5 has nothing to warn about.

> Note: `ontologies/README.md` now contains a fenced example table. That is fine — `check_ontology` only reads `_executive-view.md` and deep records inside function directories, and `README.md` sits at `ontologies/`, not in one.

- [ ] **Step 5: Commit**

```bash
git add ontologies
git commit -m "feat(ontologies): customer-success renewal-prep deep record (#5 automation path)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The renewal-prep work package

**Files:** Create `skills/renewal-prep/SKILL.md` and `skills/renewal-prep/owner-card.md`

> **Drift checks are exact-string.** `owner-card.md`'s `owner` must equal the deep record's `accountable_owner`, and its `source_of_truth` must equal the deep record's `gate_source_of_truth`, character for character. The card's `action_class` must equal the skill's. Copy them; do not retype them.

- [ ] **Step 1: Create `skills/renewal-prep/SKILL.md`:**

```markdown
---
name: renewal-prep
description: Assemble a sourced renewal brief before a contract renewal so the CSM walks in prepared
action_class: reversible-write
provisioned: yes
baseline: memory/renewal-prep-baseline.md
ontology: ontologies/customer-success/renewal-prep.md
---
# Renewal preparation

Forty-five days before a contract renewal, assemble a brief for the account's CSM:
contract terms and dates, the last 90 days of product usage read against the account's
own history, open and recently closed support tickets, and the notes from the most
recent business review. Name the risks you can see and give an expansion-or-contraction
read. Every number and claim carries a link to the record it came from.

Halt rather than guess. A missing or contradictory contract record, or usage data more
than seven days stale, stops the brief and routes to the VP Customer Success. A brief
with an unmarked gap is worse than no brief, because it will be trusted.

This skill stops at the brief. It does not decide the renewal, propose pricing, edit
the contract or CRM opportunity record, or contact the customer
([ontology record](../../ontologies/customer-success/renewal-prep.md)).

## Harness requirements
- A governed pre-provisioning baseline for brief lead time and sourcing completeness:
  [memory/renewal-prep-baseline.md](../../memory/renewal-prep-baseline.md) (the
  `baseline:` this skill cites — the #5 provisioning gate).
- Read access to the CRM contract and opportunity records, the product-usage
  warehouse, the support-ticket system, and the business-review notes.
- Write access to the CS workspace location where briefs are filed — and nowhere else.

## Compatibility notes
- Claude Code / Codex / Cursor / Gemini CLI load the `SKILL.md` convention (#19).
- This package ships no runtime action-class hook. Its writes are confined to the
  brief document, which is why it is classified `reversible-write` rather than
  `external-side-effect`: a wrong brief is corrected by rewriting the file, and no
  message reaches the customer. Widening it to write CRM fields or send the brief to
  a customer would make it track 2, and the classification and Owner's Card would have
  to change with it.
- Read-only access to the four source systems is a hard requirement, not a
  preference. A deployment that grants write access to the CRM breaks the action-class
  claim above.

## Memory row
- **Reads:** the pre-provisioning renewal-prep baseline (brief lead time, sourcing
  completeness).
- **Writes:** a per-renewal note recording which sources were available and which were
  stale at brief time (observed provenance).
- **Run-only:** the assembled brief's intermediate query results.

## Portability check

*If I had to move this skill tomorrow, what would break?* The CRM, usage-warehouse,
support-system, and business-review connectors; the governed baseline record; the CS
workspace write location; and the CSM review gate named in the Owner's Card.
```

- [ ] **Step 2: Create `skills/renewal-prep/owner-card.md`:**

```markdown
---
owner: VP Customer Success
backup_owner: Director of Customer Success
job: Assemble a sourced renewal brief 45 days before each contract renewal
action_class: reversible-write
allowed_actions: read CRM contract and opportunity records, product-usage data, support tickets, and business-review notes; write and revise the renewal brief in the CS workspace
proposed_only_actions: flag an account as a churn risk on the CRM record after the CSM confirms the read
forbidden_actions: edit contract or opportunity records; propose or quote pricing; contact the customer; send the brief outside the CS workspace
pause_condition: the contract record is missing or contradicts the CRM opportunity; usage data is more than seven days stale; the support system is unreachable
retirement_condition: the CRM ships a renewal-brief view the team trusts more, or renewals move to a motion that does not start from a written brief
source_of_truth: The CRM contract record for terms and dates; the usage warehouse for product adoption
review_cadence: monthly
known_failure_modes: no runtime action-class hook ships with this package; a brief assembled from a partially stale warehouse can look complete, which is why staleness halts rather than annotates
last_reviewed: 2026-07-24
next_review: 2026-10-24
success_standard: Every renewal has a sourced brief in the CSM's hands 45 days ahead, with every number resolving to a source record, measured against the pre-provisioning baseline
evidence_required: The brief itself with its per-claim source links, and the source-availability note recorded for the run
sources_must_not_use: Slack threads, email, or a CSM's recollection as a source of truth for contract terms or usage numbers
review_sample: Every brief is read by the account's CSM before the renewal conversation; the VP reviews two briefs a month against their source records
---
# Owner's Card — Renewal preparation

The **VP Customer Success** owns this skill; the **Director of Customer Success** is
the backup. It assembles a sourced renewal brief and stops there — it may not touch
contract or opportunity records, propose pricing, or contact a customer. Flagging an
account as a churn risk is proposed-only and waits on the CSM's confirmation.

The boundary is what keeps this skill track 1: everything it writes is a document a
human reads and can rewrite. If it is ever given write access to the CRM or a path to
the customer, it becomes an external-side-effect skill and this card must be rewritten
before that ships.

It pauses rather than papering over a gap, because a brief that looks complete is
trusted. The CSM's read before every renewal conversation is the review gate; the VP's
twice-monthly sample against source records is the quality check.
```

- [ ] **Step 3: Verify the drift checks**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected at this point: **ERROR** — `provisioned: yes` cites `memory/renewal-prep-baseline.md`, which Task 4 creates. That failure is the #5 provisioning gate working exactly as designed; it clears in the next task. Confirm the message names the baseline, and confirm **no drift ERROR** appears about `action_class`, `owner`, or `source_of_truth` — those would mean a copy mismatch to fix now.

- [ ] **Step 4: Commit**

```bash
git add skills/renewal-prep
git commit -m "feat(skills): renewal-prep work package + Owner's Card (first track-1 skill)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The captured baseline, the index, and the full gate

**Files:** Create `memory/renewal-prep-baseline.md`; modify `memory/_index.md`, `AGENTS.md`

- [ ] **Step 1: Create `memory/renewal-prep-baseline.md`:**

```markdown
---
provenance: observed
owner: VP Customer Success
valid_at: 2026-07-20
review_by: 2026-10-20
source: The CS team's H1 2026 renewal log (31 renewals, Jan–Jun 2026)
---
# Renewal-prep baseline (pre-provisioning)

Captured before the renewal-prep skill was provisioned, so its improvement can be
proven rather than assumed (#5 provisioning gate).

- Median brief lead time: **6 days** before the renewal date.
- Renewals with a written brief at all: **19 of 31**.
- Briefs whose usage numbers resolved to a source record: **7 of 19**; the rest cited
  a number with no link back to the warehouse.
- Most common gap: support history summarized from memory rather than the ticket system.
```

- [ ] **Step 2: List it in `memory/_index.md`.** Add below the existing entry:

```markdown
- [Renewal-prep baseline (pre-provisioning)](renewal-prep-baseline.md) — VP Customer Success — observed
```

- [ ] **Step 3: Update `AGENTS.md`.** In the "Built and working" list, replace the `skills/` bullet with:

```markdown
- `skills/` — the work-package convention and two worked packages
  (`onboarding-orchestration`, an external-side-effect skill, and `renewal-prep`, a
  reversible-write one), each with its `SKILL.md` and `owner-card.md`.
```

and replace the `memory/` bullet with:

```markdown
- `memory/` — the org-memory record schema with two captured baselines and an index.
```

- [ ] **Step 4: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0. The provisioning ERROR from Task 3 is cleared by the baseline; the second live memory record is in the index, so no "live record not in index" WARN appears; the card is fresh, so no staleness WARN appears. **If the WARN count moved, read the new warning** — with two provisioned skills the freshness and drift checks now run on twice the content.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. The new memory record is an addition (additions are fine), and the engine carries no `groundwork.pin`, so the #18 tripwire stays dormant.

- [ ] **Step 5: Commit**

```bash
git add memory AGENTS.md
git commit -m "feat(memory): renewal-prep captured baseline + index entry (provisioning gate)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **PM feature-request-triage** is Slice **2.2b** — the same vertical for the product function, and the second half of the runway's 2.2.
- **No `demo/`.** Phase 2.3: the synthetic ~20-person B2B SaaS, the 15-minute 3-query script, demo canon + the #16 synthetic-identifier check, the meeting-challenger exemplar, and the demo's real `groundwork.pin` — where the #18 tripwire and the #21 skew gate stop being dormant.
- **No new check types.** Task 1 replaces a parser; it does not add a check. The #5 severity contract is untouched.
- **No changelog or proposal content.** Renewal-prep makes a track-1 skill *exist*; exercising the auto-apply path end to end (a real proposal, a real changelog line) belongs with `demo/`, where transient governance artifacts are legitimate.
- **Still open for the maintainer:** the four Slice 1.5d-ii deferrals and the `SKIP_RELPATHS` gate-scoping sign-off. None blocks this slice.

## Self-Review

- **Ticket coverage:** #5 automation path (common core + Substrate + Shape + all 8 Gate parts) → the renewal-prep deep record; #5 provisioning gate → the captured baseline the skill cites; #6 card spine + track-2 trio + the three drift checks → `owner-card.md`; #7 record shape + index → the baseline and `_index.md`; #11's restricted-grammar doctrine → extended to the executive-view table.
- **The 32 rounds are converted, not discarded.** Step 7 keeps every adversarial input as a rejection test, and Step 8 fails the task if the test count drops. Proving a decoy is *refused* is stronger than proving it is parsed a particular way.
- **Placeholder scan:** no TBD/TODO; every file's content and every code change is given in full, with verification commands and expected output — including the *deliberate* intermediate failure in Task 3 Step 3, so a red gate mid-slice is not mistaken for a mistake.
- **Type consistency:** `parse_exec_table(text, path)` → `(rows, findings)` — a signature change, with its call site in `check_ontology` and its tests updated in the same task. `_canonical_row` → `list[str] | None`. `Finding(level, path, line, message)` throughout. No new imports.
- **Pre-empts the recurring Codex findings.** (a) *Fail-open on malformed input* — the grammar's default branch is ERROR; there is no path where a non-canonical line is silently parsed. (b) *Alias laundering* — deep-record links are matched by realpath in `check_ontology` (unchanged from 2.1), and the link cell now admits exactly one anchored `[text](path)` form, so image and nested-bracket variants cannot smuggle a target. (c) *Non-scalar frontmatter* — the new deep record, skill, and card use scalars only; `_blank`/`isinstance` guards on the existing checks cover them unchanged. (d) *Corpus void* — Task 1 Step 8's per-function parse report prints activity and finding counts, so a view that silently stops parsing shows as `0 activities` rather than as an absent finding.
- **The honest cost is stated, not buried:** the canonical form turns benign formatting variance (alignment colons, indentation, column reordering) into gate failures. That is the same trade #11 already accepted for frontmatter, the error messages name the required shape, and `ontologies/README.md` shows it.
