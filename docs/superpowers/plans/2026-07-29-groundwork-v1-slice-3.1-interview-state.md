# groundwork V1 — Slice 3.1: the resumable interview state (#9) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Open Phase 3 with the artifact everything else in it writes to: **#9's resumable interview state**. A fixed `00-manifest.md` pointer, one frozen committed file per confirmed layer, and a single dirty `_working.md` — with `check_interview_state` enforcing the manifest-vs-files drift #9 named as the accepted cost, and a `--diff` guard freezing confirmed layers so *"confirmed-vs-provisional is git structure, not an agent-honored label"* is true rather than merely intended. Plus the worked example: `demo/interview/`, the interview that produced Umbercress.

**Architecture:** Two new checks in `scripts/validate.py`, both reusing existing primitives. `check_interview_state` walks like every other structural check and discovers state **by content** — a directory is interview state exactly when it carries a `00-manifest.md`, so the engine's own `interview/` (which ships the format spec and no manifest) is silent. `interview_diff_findings` reuses `_git_diff_context` / `_git_show` / `_committed_path_status` — the plumbing 1.4b built and 1.5d-ii extracted, gaining a third consumer rather than a third implementation.

**Tech Stack:** Python 3 standard library only. Markdown content.

## Global Constraints

- **Zero dependencies.** `scripts/validate.py` imports the standard library only; `TestZeroDep` scans every shipped `.py` in the repo and will catch a slip.
- **Check conventions.** New checks take `(root, ignore=())`, honor `_ignored` for `.gitignore` parity, read structured files through `_load_frontmatter` / `_read_utf8` (fail-closed, never crash), reuse `_blank`, `_parse_date`, `_H1`, `_substantive_line`, and `Finding(level, path, line, message)`. ERROR fails the gate; WARN does not. Wire new checks at the **end** of `validate()`.
- **The engine output is an invariant:** `python3 scripts/validate.py .` must print exactly `0 error(s), 7 warning(s)` after every task, and `--diff main` must exit 0. **The test count moves in this slice** (it adds code) — record the number after each task and never let it drop.
- **Restricted grammar, not a permissive reader** (the 2.2a lesson). This is a format groundwork's own generator writes, so it is the #11 kind of parser: one legal shape, anything else ERRORs with a message naming the required shape. Do **not** accept a scalar where a list is specified, or a loose filename where `NN-slug.md` is specified, on the grounds that it "obviously means" the right thing.
- **`demo/` is a governed root now.** `demo/interview/**` is *not* a governed class (`_governed_class` returns `None` for it), so no proposal is needed — but do not touch anything under `demo/skills/` or `demo/governance/constitution/` in this slice, or `--diff main` will ERROR.
- **`demo/` may not contain a single external URL** (`external_domains` is empty and `check_synthetic_identifiers` scans every file there). No bare 7- or 10-digit number runs; money is `$52,000`.
- **Keep path components short** — `check_entropy` WARNs on 40+ character runs of `[A-Za-z0-9+/=_-]` at ≥ 4.0 bits. Every filename here is well under that.
- **Pronouns:** they/them or the person's name. No person in `demo/canon.md` has stated pronouns.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.3e merged and pushed (`098712d`). 610 tests with 1 designed skip, gate + `--diff main` exit 0, 7 WARNs. Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-3.1-interview-state
```

---

## Design calls flagged for the maintainer

**1. Phase 3 is re-ordered, and this is the call I most want you to look at.**
The spec sequences Phase 3 as **3.1** consultant protocol + resumable state → **3.2** the generator → **3.3** the question skeleton. I recommend **3.1** resumable state (this plan) → **3.2** consultant protocol + question skeleton + constitution worksheet → **3.3** the generator.

*Why.* A protocol without a question bank is inert prose — §4's four mechanics (define-the-role-first, one-question-at-a-time, evidence-based read-what-exists, checkpoint approvals) tell an agent *how* to ask, and the 9-section skeleton tells it *what* to ask. Shipping them one slice apart means 3.1 lands an artifact nobody can use and 3.2 lands the half that makes it work — and in between, `AGENTS.md` has to describe a half-built interview, which is exactly the surface where this project's honesty rule is hardest to hold. Meanwhile the *state format* is genuinely separable: it is a schema plus two checks plus a worked example, it is verifiable on its own, and both the protocol and the generator write to it, so building it first means neither of them invents its own.

*The counter-argument, honestly:* #9's decision is **about** the protocol's resumability, and the promote-and-commit step (when `_working.md` becomes `NN-*.md`) is a protocol rule, not a schema rule. Shipping the state format without the protocol risks a format whose lifecycle lives nowhere. **The plan answers that by putting the promote/commit protocol in `interview/README.md` with the schema** — the state machine ships here; the interviewing *style* and the questions ship in 3.2. Total scope across Phase 3 is unchanged; only the cut lines move.

**2. The manifest's "layer table" is a frontmatter list, not a Markdown table — and it deliberately carries no status column.**
#9 specifies "a layer table" with `phase`, `status`, the open-question id, and the role frame. Two calls fall out of that:

*Frontmatter, not a table.* This repo has one canonical table parser, it governs `_executive-view.md` only, and it cost **32 review rounds** to get right (the 2.2a diagnosis). Adding a second table surface would either reuse that grammar in a place it was not designed for or start the same treadmill again. A `layers:` list in #11 frontmatter uses the reader that already exists, is just as readable to a human, and is checked by machinery that has been stable since Slice 1.1. The manifest stays small — it grows one line per layer, which is bounded by layer count rather than by transcript length, and that is the property #9 actually wanted.

*No status column, and this one is load-bearing.* A layer table that declares `confirmed | in flight` per row would be **precisely the agent-honored label #9 rejected Shape A for**. Status is derived from structure: a numbered file that appears in `layers:` and carries `provenance: confirmed` **is** confirmed; `_working.md` **is** the provisional turn; `git log` is the approval trail. If the manifest could *declare* a layer confirmed, a fumbled edit could confirm one that was never approved — the exact failure mode the whole shape exists to prevent. So the manifest points; it never labels.

**3. Interview state is discovered by CONTENT, not by directory name — and that is what makes the engine's own `interview/` silent.**
The engine ships `interview/README.md` (the format spec). A company repo ships `interview/00-manifest.md` + layers. Same directory name, completely different things. A name-based check would scan the engine's spec as if it were state and fail vacuously or noisily. So: **a directory is interview state exactly when it carries a `00-manifest.md`.** This is the doctrine already in the repo — #8's blank worksheets are silent because they live in `governance/worksheets/`, and #5 is silent on an untouched worksheet because no file exists. *Consequence, stated so it is not discovered later:* the format spec's example manifest lives in a **fenced block inside `interview/README.md`**, never as a `templates/00-manifest.md` file — a template that looks like state is a trap, and the same reasoning kept `settings.snippet.json` out of `demo/` in 2.3d.

**4. `demo/interview/` ships as a worked example — which answers a question the map left open.**
The #9 fog note says "whether `interview/` is *retained* post-generation or cleaned is the open sub-question" for the V3 re-interview flow. Shipping `demo/interview/` answers it in the **retained** direction, at least for the demo. I recommend retained: the interview state is the provenance substrate a re-interview merges against (#9's own words), and a company that throws away the record of how its OS was decided has thrown away the answer to "why is renewal prep scoped this way." It costs one directory in a private repo. *Counter:* #10 guarantees interview state is never *distributed* to employees, which is not the same as retained forever, and some adopters will want it cleaned; V3's re-interview flow may decide otherwise. Nothing here forecloses that — this is the demo's disposition, documented as such, not a rule. Without it the check has no corpus and ships as a scan that scans nothing.

**5. This slice adds a third `--diff` pass, which changes `main()`'s dedupe from a pairwise special case to an accumulator.**
`main()` currently dedupes the blast-radius pass against the memory pass, because both resolve the git context independently and a fatal context ERROR (bad ref, not a repo) would otherwise print twice. A third pass makes the pairwise form wrong — an interview-pass context ERROR would print again. Task 4 replaces it with a `seen` accumulator that each diff pass filters against. Same semantics, extended; flagged because it edits working code that no failing test currently covers, and Task 4 adds the regression that does.

---

## File Structure

**Create (10 files):**

- `interview/README.md` — the state format and the promote/commit protocol
- `demo/interview/00-manifest.md`
- `demo/interview/01-role-and-scope.md`
- `demo/interview/02-customer-success.md`
- `demo/interview/03-people-hr.md`
- `demo/interview/04-product.md`
- `demo/interview/05-finance.md`
- `demo/interview/_working.md`
- (two new test classes live in the existing `tests/test_validate.py`)

**Modify (5 files):** `scripts/validate.py`, `tests/test_validate.py`, `AGENTS.md`, `demo/README.md`, `docs/known-limitations.md`.

---

## Task 1: The state format (schema before enforcement)

**Files:** Create `interview/README.md`.

- [ ] **Step 1: Create `interview/README.md`:**

````markdown
# The interview state format

An interview is a conversation that has to survive being interrupted — by a meeting, by
a week, by switching from one agent harness to another. This directory documents the
shape that state takes so it survives all three.

**What is here today is the format and its checks.** The consultant protocol that runs
the interview, the question skeleton it asks from, and the generator that turns confirmed
answers into a company OS are **not built** — Slices 3.2 and 3.3. Pointing an agent at
this repository does not yet run an interview.

## Where the state lives

In the **company's private repo**, never in the public groundwork clone (#10). The
interview's first act is creating that repo; every confirmed answer is committed there
from the start, so confidential organizational facts never sit in a public working tree.
The validator runs from the engine clone *against* that repo.

## The three kinds of file

```
interview/
  00-manifest.md      the pointer. Small, fixed shape, rewritten every turn.
  01-role-and-scope.md    a confirmed layer. Frozen at its checkpoint commit.
  02-customer-success.md  a confirmed layer.
  _working.md         the turn in flight. Provisional. Dirty until approved.
```

**The manifest points; it never labels.** There is no "status: confirmed" column,
because a label an agent writes is a label an agent can get wrong. What makes a layer
confirmed is *structure*: it is a numbered file, it is listed in the manifest, it carries
`provenance: confirmed`, and it is committed. `git log` is the approval trail.

### `00-manifest.md`

```markdown
---
company: <the company being interviewed>
role: <one line: the role the agent was given and the human agreed to>
phase: <what is being interviewed right now>
status: in-progress | complete
open_question: <the id of the question awaiting an answer, or `none`>
last_checkpoint: <ISO date of the most recent approved layer>
layers:
  - 01-role-and-scope.md
  - 02-customer-success.md
---
# Interview manifest — <company>

<prose: where this stands and what happens next>
```

A resuming agent reads this file **first**, and only then the layers it needs. That is
what keeps the boot cost bounded: the manifest grows one line per layer, not one line per
turn.

`layers:` must be a **list**, even with one entry, and every entry must be a real file in
this directory named `NN-slug.md` with `NN` from `01`. `00` is reserved for the manifest.
The list and the directory must agree in **both** directions — a layer file nobody listed
is a layer a resuming agent will not read, and a listed file that does not exist sends it
looking for an answer that was never captured. That drift is the one cost #9 accepted
when it chose this shape, and this is the check that pays it.

### A confirmed layer — `NN-slug.md`

```markdown
---
provenance: confirmed
confirmed_by: <the person who approved it at the checkpoint>
confirmed_at: <ISO date>
source: <the interview turn, handbook, calendar export, or repo read behind it>
---
# Layer N — <what it covers>

<the confirmed facts>
```

**Frozen at its checkpoint.** Once committed, a layer file never changes — not the
frontmatter, not the body. Run `python3 scripts/validate.py <repo> --diff <base>` and any
edit to a committed layer is an ERROR, exactly as it is for an org-memory record (#7).
If a confirmed fact turns out to be wrong, the next layer records the correction and says
so; you do not go back and rewrite what a person approved.

`provenance`, `source`, and the ERROR-vs-WARN split on them are #7's vocabulary, not a
parallel one: `confirmed` means a human approved it at a checkpoint, and a confirmed fact
without a source is an ERROR.

### The turn in flight — `_working.md`

```markdown
---
provenance: inferred | observed
source: <where this came from>
open_question: <the id, matching the manifest>
---
# In flight — <what is being asked about>

<the provisional facts>

## Open question

<the question waiting on a human>
```

`provenance` here can never be `confirmed`. A working file that calls itself confirmed is
the exact laundering this shape exists to stop, and it is an ERROR — the way to confirm a
fact is to **promote** the file, not to relabel it.

`observed` means the agent read it somewhere; `inferred` means the agent concluded it.
Both are the agent's, not the company's, until a person says otherwise. This is where
§4's evidence-based move lands: an agent that reads the handbook and reflects back the
rules the company is *actually* running produces `observed` facts with a `source:`,
because people report the rules they wish they had.

## The promote-and-commit protocol

One layer, one checkpoint, one commit:

1. **Ask.** The open question goes in `_working.md` along with whatever the agent has
   provisionally gathered. The manifest's `open_question` names it. Nothing is committed.
2. **Answer.** The human answers. The agent updates `_working.md`. Still nothing is
   committed — a fact is not confirmed because an agent heard it.
3. **Checkpoint.** The agent states back what it believes is now settled and asks for
   approval. This is the approval; there is no other one.
4. **Promote.** On approval, `_working.md` is renamed to the next `NN-slug.md`, its
   `provenance` becomes `confirmed`, and `confirmed_by` / `confirmed_at` record who
   approved it and when.
5. **Commit.** The promoted layer and the updated manifest are committed together, in one
   commit. That commit *is* the record of consent — the same substrate the constitution's
   proposals use (#18).

A turn that half-commits — a promoted layer without a manifest update, or the reverse —
is what `check_interview_state` catches on the next run.

## When the interview is finished

Set `status: complete` and `open_question: none`, and delete `_working.md`. A completed
interview with a turn still in flight is a contradiction, and it ERRORs.

## What is checked, and how hard

| Rule | Level |
|---|---|
| Manifest missing `company` / `role` / `phase` / `status` / `open_question` / `last_checkpoint` | ERROR |
| `status` not `in-progress` or `complete`; `layers` not a list | ERROR |
| A listed layer that does not exist, or an existing layer nobody listed | ERROR |
| A layer file whose `provenance` is not `confirmed` | ERROR |
| A layer file with no `confirmed_by`, no `confirmed_at`, no `source`, or no rule content | ERROR |
| `_working.md` claiming `provenance: confirmed` | ERROR |
| `_working.md` present while `status: complete` | ERROR |
| `_working.md` missing while a question is open, or naming a different question than the manifest | ERROR |
| An edit to, or deletion of, a committed layer (`--diff`) | ERROR |
| `confirmed_at` unparseable or in the future; a gap or a wrong order in the numbering; `_working.md` with no `source` | WARN |

Strict exactly where the state backs a resuming agent, because a manifest that points at
the wrong thing does not fail loudly — it silently re-asks a settled question or skips one
that was never settled. Everything that is only thinking-quality warns.

**Silence is decided by content.** A directory is interview state when it carries a
`00-manifest.md`. This directory has none — it is documentation — so nothing here is
checked as state, and a company repo that has not started an interview is silent rather
than nagged.
````

- [ ] **Step 2: Gate**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. The new file adds no findings — every link is internal, no external URL, no long token.

- [ ] **Step 3: Commit**

```bash
git add interview/README.md
git commit -m "docs(interview): the resumable state format and the promote-and-commit protocol (#9)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: `check_interview_state`

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`.

- [ ] **Step 1: Write the tests first.** Add a `TestInterviewState` class to `tests/test_validate.py`. Each test builds a temp directory with `tmp_path`-style `tempfile.TemporaryDirectory()` (match the surrounding file's existing helper style) and calls `validate.check_interview_state(d)`.

Cover, at minimum:

```
happy path:            a complete, correct state dir produces ZERO findings
no manifest:           a directory of .md files with no 00-manifest.md is SILENT
missing field:         each of company/role/phase/status/open_question/last_checkpoint blank -> ERROR
bare key:              'role:' with no value (parses as []) -> ERROR, not a crash
bad status:            status: paused -> ERROR naming the two legal values
layers not a list:     'layers: 01-x.md' (scalar) -> ERROR naming the required shape
listed-but-missing:    layers names 02-x.md, no such file -> ERROR
present-but-unlisted:  03-y.md on disk, not in layers -> ERROR
duplicate number:      01-a.md and 01-b.md both listed -> ERROR
gap / wrong order:     01, 03 listed -> WARN (not ERROR)
manifest is 00:        00-manifest.md is never treated as a layer
layer provenance:      a layer with provenance: inferred -> ERROR
layer spine:           blank confirmed_by / confirmed_at / source -> ERROR each
layer body:            H1 with no substantive body -> ERROR
confirmed_at:          unparseable -> WARN; future date -> WARN
working confirmed:     _working.md with provenance: confirmed -> ERROR
working invalid:       _working.md with provenance: banana -> ERROR
working on complete:   status: complete + _working.md present -> ERROR
working missing:       status: in-progress + open_question set + no _working.md -> ERROR
open_question none:    status: in-progress + open_question: none + no _working.md -> SILENT
question drift:        _working.md open_question != manifest open_question -> ERROR
working source:        _working.md with no source -> WARN (not ERROR)
symlinks:              symlinked manifest / layer / _working.md -> ERROR each
unreadable:            non-UTF-8 manifest -> ERROR (fail closed), no crash
gitignore parity:      an ignored state dir is not scanned
nested dirs:           two independent state dirs under one root are both checked
```

**Test the negative direction first.** A check that never finds the directory produces zero findings, which is indistinguishable from a clean corpus — so every "this is valid" test is only meaningful next to a "this violation is caught" test on the same file.

- [ ] **Step 2: Implement.** Add to `scripts/validate.py`, immediately after `check_constitution`'s helpers and before `_hook_command_target`:

```python
INTERVIEW_MANIFEST = "00-manifest.md"
INTERVIEW_WORKING = "_working.md"
INTERVIEW_STATUSES = ("in-progress", "complete")
# The agent's own, unconfirmed. #7's vocabulary, not a parallel one.
INTERVIEW_PROVISIONAL = ("observed", "inferred")
MANIFEST_REQUIRED = ("company", "role", "phase", "status",
                     "open_question", "last_checkpoint")
# A layer is NN-slug.md with NN from 01: '00' is reserved for the manifest, so
# the manifest can never be mistaken for a layer of itself.
_LAYER_FILE = re.compile(r"(0[1-9]|[1-9][0-9])-[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")


def _interview_dirs(root, ignore=()):
    """Every directory holding interview state — one carrying a 00-manifest.md.

    Discovery is by CONTENT, never by directory name. The engine's own
    interview/ ships the format spec and no manifest, and a company repo that
    has not started an interview has no state to check; a name-based rule would
    scan the first as if it were state and nag the second. Same doctrine as #8's
    governance/worksheets/ (silence decided by location) and #5's untouched
    worksheet (silence decided by absence)."""
    dirs = set()
    for abspath in iter_files(root, ignore):
        if os.path.basename(abspath) == INTERVIEW_MANIFEST:
            dirs.add(os.path.dirname(abspath))
    return sorted(dirs)


def check_interview_state(root, ignore=()):
    """#9's resumable interview state: a fixed manifest pointer, one frozen file
    per confirmed layer, and a single dirty _working.md.

    Strict exactly where the state backs a resuming agent — a manifest that
    points at the wrong thing does not fail loudly, it silently re-asks a settled
    question or skips one that was never settled. Freezing committed layers is
    the --diff mode (interview_diff_findings)."""
    findings = []
    for d in _interview_dirs(root, ignore):
        findings += _check_interview_dir(d, root, ignore)
    return findings


def _check_interview_dir(d, root, ignore=()):
    findings = []
    today = datetime.date.today()
    rel_dir = os.path.relpath(d, root)

    man_abs = os.path.join(d, INTERVIEW_MANIFEST)
    rel_man = os.path.relpath(man_abs, root)
    if os.path.islink(man_abs):
        return [Finding("ERROR", rel_man, None,
                        "interview manifest must not be a symlink")]
    data, fm = _load_frontmatter(man_abs, rel_man)
    findings += fm
    if data is None:
        return findings  # unreadable manifest already ERRORed, fail closed

    for field in MANIFEST_REQUIRED:
        v = data.get(field)
        if _blank(v):
            findings.append(Finding("ERROR", rel_man, None,
                                    "interview manifest missing '%s'" % field))
        elif not isinstance(v, str):
            findings.append(Finding("ERROR", rel_man, None,
                                    "manifest '%s' must be a single value" % field))

    status = data.get("status")
    status = status.strip() if isinstance(status, str) else None
    if status is not None and status not in INTERVIEW_STATUSES:
        findings.append(Finding("ERROR", rel_man, None,
                                "invalid interview status %r (one of %s)"
                                % (status, list(INTERVIEW_STATUSES))))
        status = None

    lc = data.get("last_checkpoint")
    if isinstance(lc, str) and lc.strip() and _parse_date(lc) is None:
        findings.append(Finding("WARN", rel_man, None,
                                "'last_checkpoint' is not an ISO date (YYYY-MM-DD)"))

    # `none` is the explicit no-open-question answer, the same way `repeals: none`
    # is an explicit no-repeal (#8). It is a value here, not a placeholder.
    oq = data.get("open_question")
    oq = oq.strip() if isinstance(oq, str) else ""
    question_open = bool(oq) and oq.lower() != "none"

    # --- the layer list: a restricted grammar, not a permissive reader ---
    raw_layers = data.get("layers")
    declared = []
    if raw_layers is None or raw_layers == []:
        declared = []
    elif not isinstance(raw_layers, list):
        findings.append(Finding("ERROR", rel_man, None,
                                "manifest 'layers' must be a list of layer filenames, "
                                "one per '- ' line — even when there is only one"))
        raw_layers = []
    if isinstance(raw_layers, list):
        for entry in raw_layers:
            if not isinstance(entry, str) or not entry.strip():
                findings.append(Finding("ERROR", rel_man, None,
                                        "manifest 'layers' entry is blank"))
                continue
            name = entry.strip()
            if _LAYER_FILE.fullmatch(name) is None:
                findings.append(Finding(
                    "ERROR", rel_man, None,
                    "manifest 'layers' entry %r is not a layer filename "
                    "(NN-slug.md, NN from 01; 00 is the manifest)" % name))
                continue
            if name in declared:
                findings.append(Finding("ERROR", rel_man, None,
                                        "manifest 'layers' lists %r twice" % name))
                continue
            declared.append(name)

    numbers = [int(n[:2]) for n in declared]
    if len(set(numbers)) != len(numbers):
        findings.append(Finding("ERROR", rel_man, None,
                                "two layers share a number — the number is the "
                                "layer's identity"))
    elif numbers and numbers != sorted(numbers):
        findings.append(Finding("WARN", rel_man, None,
                                "layers are not listed in ascending order"))
    elif numbers and numbers != list(range(1, len(numbers) + 1)):
        findings.append(Finding("WARN", rel_man, None,
                                "layer numbering has a gap (a layer was removed?)"))

    # --- both directions of the drift check (#9's one accepted cost) ---
    try:
        on_disk = sorted(n for n in os.listdir(d)
                         if _LAYER_FILE.fullmatch(n) and not _ignored(n, ignore))
    except OSError as e:
        return findings + [Finding("ERROR", rel_dir, None,
                                   "cannot list interview state directory — "
                                   "fail closed: %s" % e)]
    for name in declared:
        if name not in on_disk:
            findings.append(Finding(
                "ERROR", rel_man, None,
                "manifest lists a layer that does not exist: %s — a resuming "
                "agent would look for an answer that was never captured" % name))
    for name in on_disk:
        if name not in declared:
            findings.append(Finding(
                "ERROR", os.path.join(rel_dir, name), None,
                "layer file is not listed in the manifest — a resuming agent "
                "will never read it"))

    for name in on_disk:
        findings += _check_interview_layer(os.path.join(d, name), root, today)

    # --- the turn in flight ---
    work_abs = os.path.join(d, INTERVIEW_WORKING)
    rel_work = os.path.join(rel_dir, INTERVIEW_WORKING)
    work_exists = os.path.lexists(work_abs) and not _ignored(INTERVIEW_WORKING, ignore)
    if work_exists and os.path.islink(work_abs):
        findings.append(Finding("ERROR", rel_work, None,
                                "_working.md must not be a symlink"))
    elif work_exists:
        if status == "complete":
            findings.append(Finding(
                "ERROR", rel_work, None,
                "a completed interview has no turn in flight — promote or delete "
                "_working.md before setting status: complete"))
        wdata, wfm = _load_frontmatter(work_abs, rel_work)
        findings += wfm
        if wdata is not None:
            prov = wdata.get("provenance")
            prov = prov.strip() if isinstance(prov, str) else None
            if prov == "confirmed":
                findings.append(Finding(
                    "ERROR", rel_work, None,
                    "_working.md cannot be 'confirmed' — the way to confirm a "
                    "fact is to promote the file to a numbered layer, not to "
                    "relabel it (#9)"))
            elif prov not in INTERVIEW_PROVISIONAL:
                findings.append(Finding(
                    "ERROR", rel_work, None,
                    "_working.md provenance must be one of %s"
                    % list(INTERVIEW_PROVISIONAL)))
            if _blank(wdata.get("source")):
                findings.append(Finding("WARN", rel_work, None,
                                        "_working.md has no 'source' (what is this "
                                        "provisional fact based on?)"))
            woq = wdata.get("open_question")
            woq = woq.strip() if isinstance(woq, str) else ""
            if question_open and woq != oq:
                findings.append(Finding(
                    "ERROR", rel_work, None,
                    "_working.md names open question %r but the manifest names "
                    "%r — a half-committed turn" % (woq, oq)))
    elif question_open and status != "complete":
        findings.append(Finding(
            "ERROR", rel_man, None,
            "manifest names an open question (%s) but there is no _working.md — "
            "the question a human still owes an answer to lives nowhere" % oq))
    return findings


def _check_interview_layer(abspath, root, today):
    """A confirmed layer: #7's provenance vocabulary, plus the checkpoint's
    accountable half. A layer with no named approver is the agent-honored label
    the whole shape exists to replace."""
    rel = os.path.relpath(abspath, root)
    if os.path.islink(abspath):
        return [Finding("ERROR", rel, None, "interview layer must not be a symlink")]
    text, rd = _read_utf8(abspath, rel)
    if text is None:
        return rd
    findings = list(rd)
    data, body, fm = _frontmatter_and_body(text, rel)
    findings += fm

    prov = data.get("provenance")
    prov = prov.strip() if isinstance(prov, str) else None
    if prov != "confirmed":
        findings.append(Finding(
            "ERROR", rel, None,
            "a numbered layer is a confirmed layer: provenance must be "
            "'confirmed' (got %r) — provisional facts live in _working.md" % prov))

    for field in ("confirmed_by", "confirmed_at", "source"):
        v = data.get(field)
        if _blank(v):
            findings.append(Finding("ERROR", rel, None,
                                    "confirmed layer missing '%s'" % field))
        elif not isinstance(v, str):
            findings.append(Finding("ERROR", rel, None,
                                    "'%s' must be a single value" % field))

    ca = data.get("confirmed_at")
    if isinstance(ca, str) and ca.strip():
        d = _parse_date(ca)
        if d is None:
            findings.append(Finding("WARN", rel, None,
                                    "'confirmed_at' is not an ISO date (YYYY-MM-DD)"))
        elif d > today:
            findings.append(Finding("WARN", rel, None,
                                    "'confirmed_at' is in the future"))

    rendered = _HTML_COMMENT.sub("", body)
    if _H1.search(rendered) is None or not any(
            _substantive_line(ln) for ln in rendered.split("\n")):
        findings.append(Finding("ERROR", rel, None,
                                "confirmed layer has no content (H1 title + body) — "
                                "an empty checkpoint records nothing"))
    return findings
```

- [ ] **Step 3: Wire it into `validate()`.** Add at the end, after `check_root_files(root)`:

```python
    findings += check_interview_state(root, ignore)
```

- [ ] **Step 4: Gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"` — all green; record the new count.
Run: `python3 scripts/validate.py . ; echo "exit: $?"` — exactly `0 error(s), 7 warning(s)`, exit 0. The check is dormant: `interview/README.md` carries no manifest, so nothing is scanned yet. **That is expected here and dangerous to leave** — Task 3 gives it a corpus, and Task 5 proves it is scanning.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): check_interview_state — #9's manifest, layers, and working file

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: The worked example — Umbercress's interview

**Files:** Create seven files under `demo/interview/`.

> Every fact in these layers must match what the demo already committed — the owner names, the scoping, the numbers. A layer that says something `demo/ontologies/` contradicts is worse than no layer, because it is a record of a decision that did not happen.

- [ ] **Step 1: Create `demo/interview/00-manifest.md`:**

```markdown
---
company: Umbercress
role: An organizational analyst who maps what each function actually does, and what it costs, before proposing that anything be automated
phase: marketing
status: in-progress
open_question: q-case-study-bottleneck
last_checkpoint: 2026-06-15
layers:
  - 01-role-and-scope.md
  - 02-customer-success.md
  - 03-people-hr.md
  - 04-product.md
  - 05-finance.md
---
# Interview manifest — Umbercress

Five layers confirmed, one turn in flight. Read this file first; then read only the
layers you need for the question in front of you.

**Where this stands.** Scope, customer success, People operations, product, and finance
are settled and committed — those five layers are what
[the ontology](../ontologies/README.md), the four work packages, and the constitution
were generated from. Marketing is open: the company thinks customer-story production
deserves *more* human time, not less, and the question in
[_working.md](_working.md) is what is actually slowing it down.

**Where this does not stand.** Sales, engineering, and legal have executive views and
nothing deeper. That is the two-tier schema working as intended — depth is earned by
acting, not by planning to act — and not an unfinished interview.
```

- [ ] **Step 2: Create `demo/interview/01-role-and-scope.md`:**

```markdown
---
provenance: confirmed
confirmed_by: Priya Raman
confirmed_at: 2026-05-11
source: Opening interview session 2026-05-04, confirmed at the checkpoint on 2026-05-11
---
# Layer 1 — The role, and what is in scope

**The role, agreed first.** A good organizational analyst asks what the work actually is
before asking what to do about it, says "that is not worth automating" out loud, and
never proposes machinery for a problem nobody has named. A bad one arrives with a
solution and interviews for permission. Umbercress asked for the first.

**The company.** About twenty people. One product, Umbercress Relay, sold to mid-market
logistics operators. Around sixty paying customers on annual contracts. One office, no
subsidiaries.

**What that shape rules out.** No finance department — a fractional CFO and a bookkeeper.
No legal team — outside counsel. Founder-led sales. One person, Ruth Okafor, running all
of People operations. Any recommendation that assumes a team where there is a person is
wrong before it is evaluated.

**Where the interview goes deep, decided here:** customer success, People operations, and
product. Those are the three functions where a named person said the same sentence twice
— *"I spend the first day of every week assembling things nobody reads until Thursday."*
Sales, marketing, engineering, legal, and finance get an executive view: every activity
named, with a Direction, and nothing more until somebody acts on one.
```

- [ ] **Step 3: Create `demo/interview/02-customer-success.md`:**

```markdown
---
provenance: confirmed
confirmed_by: Marcus Bell
confirmed_at: 2026-05-26
source: Customer-success session 2026-05-19; the H1 renewal log read with permission on 2026-05-21
---
# Layer 2 — Customer success

**The activity that came up first.** Renewal preparation. Three people cover about sixty
accounts on annual contracts, and every renewal starts with the same gathering: contract
terms out of the CRM, ninety days of Relay usage, open and recently closed tickets, and
the notes from the last quarterly check-in.

**What the record said, rather than what the room said.** The team's estimate was "a
couple of hours per renewal." The renewal log for the first half of 2026 said something
sharper, and this is the number the baseline was captured from: of twenty-six renewals,
fifteen had a written brief at all, the median brief landed eight days before the renewal
date, and six of those fifteen had usage figures that resolved to a source record. The
rest cited a number with nothing behind it.

**The line the team drew, unprompted.** The gathering is mechanical; the renewal
conversation is not. Marcus Bell's words at the checkpoint: *"I want it to hand me the
picture. I do not want it deciding anything, and it does not talk to the customer."*
That sentence became the activity's scope, the Owner's Card's forbidden actions, and a
constitution rule.

**Direction: down.** This should stop being hand-run.

Generated from this layer:
[renewal preparation](../ontologies/customer-success/renewal-preparation.md).
```

- [ ] **Step 4: Create `demo/interview/03-people-hr.md`:**

```markdown
---
provenance: confirmed
confirmed_by: Ruth Okafor
confirmed_at: 2026-06-02
source: People operations session 2026-05-28; the onboarding tracker and the H1 review-cycle debrief notes, read with permission
---
# Layer 3 — People operations

**Two activities, and they are not the same kind of thing.**

**Onboarding orchestration** is routing: accounts, equipment, a first-week schedule,
against a checklist with a clear source of truth. The tracker for the first half of 2026
shows nine hires, a median of five business days to day-one-ready, and five of nine
actually ready on the first morning — the recurring gap being a system access nobody
granted in time. High repetition, low judgment. **Direction: down.**

**Performance-review prep** is gathering evidence about people, and this is where the
interview slowed down on purpose. The mechanical part is real: eleven days' median from
cycle open to a manager holding a pack, six packs of nineteen delivered a week ahead of
the conversation. But eight of nineteen had peer comments that had been summarized by
hand, and Ruth Okafor named that as the failure that matters — a paraphrase of what a
colleague wrote is not what they wrote.

**The boundary, stated by the company and not proposed by the analyst.** Assemble the
evidence; never evaluate. No rating, no ranking, no summary judgment, no drafted
assessment language. Asked what should happen if someone asks the agent for a draft
anyway, Ruth Okafor's answer was that it should refuse and say who to talk to. That is
now a rung-five rule with a named appeal, not a line in a document.

**Direction: down**, for the gathering only.

Generated from this layer:
[onboarding orchestration](../ontologies/people-hr/onboarding-orchestration.md) and
[performance-review prep](../ontologies/people-hr/performance-review-prep.md).
```

- [ ] **Step 5: Create `demo/interview/04-product.md`:**

```markdown
---
provenance: confirmed
confirmed_by: Dana Whitfield
confirmed_at: 2026-06-09
source: Product session 2026-06-04; the Q2 product-tracker export read with permission on 2026-06-05
---
# Layer 4 — Product

**The activity.** Feature-request triage. Two people in product, and requests arrive
through support tickets, CRM opportunity and check-in notes, and the customer-success
team — three routes, no single queue.

**What the export showed.** One hundred and forty-one requests in the second quarter. A
median of nine business days from a request being raised to being filed and assigned, and
forty-four of the one hundred and forty-one filed within five. Thirty-one named the
accounts that asked; the rest carried no attribution at all, which is why nobody could
weigh a request by what it was worth. Seventeen duplicates were only caught at the
quarterly roadmap review.

**The consequence the company had already felt.** Two accounts renewing this year are at
risk on requests that were in the tracker the whole time. Attribution is not
bookkeeping — it is the difference between a renewal conversation and a surprise.

**The line.** Triage decides where a request goes, never whether it gets built. A request
matching no theme and no owning manager stays unassigned and visible rather than being
forced into the nearest tag.

**Direction: down.**

Generated from this layer:
[feature-request triage](../ontologies/product/feature-request-triage.md).
```

- [ ] **Step 6: Create `demo/interview/05-finance.md`:**

```markdown
---
provenance: confirmed
confirmed_by: Priya Raman
confirmed_at: 2026-06-15
source: Finance session 2026-06-11, with the fractional CFO present
---
# Layer 5 — Finance, and the decision not to build anything

**Three activities, all high-risk, all recorded as `wait`.** Spend approval, payroll
runs, and vendor payments each move money or touch compensation, and each is currently
done by a person who knows the company.

**Why `wait` and not `automate`.** Not because the work is unusual — approving an invoice
is about as describable as work gets — but because at twenty people the volume does not
justify it and the error cost is not recoverable by editing a file. Priya Raman owns all
three today and the honest answer was that this is fine for now.

**Why record it at all.** An ontology that only ever records automation verdicts reads as
an automation funnel. A recorded decision *not* to build something is a decision, and in
a year somebody will want to know whether finance was considered and dismissed or simply
never asked. It was considered.

**Direction: up** for spend approval — it deserves more of a person's attention, not less.

Generated from this layer:
[spend approval](../ontologies/finance/spend-approval.md),
[payroll runs](../ontologies/finance/payroll-runs.md), and
[vendor payments](../ontologies/finance/vendor-payments.md).
```

- [ ] **Step 7: Create `demo/interview/_working.md`:**

```markdown
---
provenance: observed
source: Marketing session 2026-06-22; the published customer-story archive, read with permission
open_question: q-case-study-bottleneck
---
# In flight — Marketing

**Provisional, not confirmed.** Nobody has approved anything below this line, and the
`observed` label means the analyst read it rather than being told it.

Marketing's executive view puts customer-story production at **Direction: up** —
more human time, not less. That much is settled. What is not settled is why so few get
published.

**What the archive shows.** Four customer stories published in the last twelve months
against a stated target of one a quarter plus two at the annual user event. Six more
exist as drafts. Every one of the six has a date on the draft and no date on anything
after it.

**What that might mean, and this is the analyst's inference rather than anybody's
statement:** the bottleneck is not writing. Six drafts exist. It is what happens between
a draft and a published story — which at Umbercress means a named customer reading it and
saying yes.

## Open question

`q-case-study-bottleneck` — For the six unpublished drafts: how many are waiting on
customer approval, and how many are waiting on somebody here? If it is customer approval,
this is a relationship activity and stays entirely human. If it is internal, there may be
a coordination activity worth naming — but not an automation one, and not until somebody
says which it is.
```

- [ ] **Step 8: Gate**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. Seven new files, zero findings.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. `demo/interview/**` is not a governed class, so the #18 tripwire ignores it, and everything here is an addition.

- [ ] **Step 9: Commit**

```bash
git add demo/interview
git commit -m "feat(demo): the interview that produced Umbercress — five confirmed layers and a turn in flight

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The frozen-layer guard (`--diff`)

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`.

> This is the half that makes #9's decision true. Without it, "confirmed" is a word in a file that a resuming agent can edit — which is exactly what Shape A was rejected for. **If this task cannot be completed in this session, it does not get dropped: it becomes named Slice 3.1b and the spec's Build log says so.** Shipping the shape without the property that justified choosing it is the one outcome to refuse.

- [ ] **Step 1: Write the tests first.** Add a `TestInterviewDiff` class, following the existing memory-diff tests' pattern of building a real temp git repo (`git init`, commit a base, mutate the working tree, call the function with the base ref).

Cover:

```
unchanged layer:       committed layer untouched -> no findings
edited body:           one word changed in a committed layer -> ERROR
edited frontmatter:    confirmed_by changed -> ERROR
whitespace only:       trailing newline added -> NO finding (memory precedent)
CRLF base blob:        base committed with CRLF, working LF -> NO finding
deleted layer:         committed layer removed -> ERROR
new layer:             a layer added since base -> no finding (additions are fine)
manifest changes:      00-manifest.md edited -> no finding (it is the pointer)
working changes:       _working.md edited -> no finding (it is provisional)
manifest deleted:      layers stay frozen (the dir was state AT BASE) -> ERROR on edit
unknown base ref:      one context ERROR, no crash
symlinked layer:       committed path is a symlink -> ERROR (fail closed)
unreadable base blob:  non-UTF-8 base -> ERROR, never "unchanged"
outside a repo:        no crash
```

- [ ] **Step 2: Implement.** Add after `memory_diff_findings`:

```python
def interview_diff_findings(root, base):
    """#9's frozen-layer guard: a confirmed layer is immutable once committed, so
    'confirmed' is git structure rather than a label an agent can rewrite.

    Driven by the BASE file list (the 1.4b lesson: a working-tree walk lets
    .gitignore or a skip exempt a committed file). A directory counts as
    interview state when it carried a 00-manifest.md AT BASE — deleting the
    manifest in the same diff must not un-freeze the layers under it. The
    manifest and _working.md are excluded on purpose: they change every turn."""
    ctx, ctx_findings = _git_diff_context(root, base)
    if ctx is None:
        return ctx_findings
    toplevel, scope = ctx["toplevel"], ctx["scope"]
    findings = []
    listdir_cache = {}

    state_dirs = set()
    for bf in ctx["base_files"]:
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        if os.path.basename(bf) == INTERVIEW_MANIFEST:
            state_dirs.add(os.path.dirname(bf))

    for bf in ctx["base_files"]:
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        if os.path.dirname(bf) not in state_dirs:
            continue
        if _LAYER_FILE.fullmatch(os.path.basename(bf)) is None:
            continue
        rel = bf if scope == "." else bf[len(scope) + 1:]
        if _diff_in_workbench_skips(rel):
            continue
        parts = bf.split("/")
        abspath = os.path.join(toplevel, *parts)
        status = _committed_path_status(toplevel, parts, listdir_cache)
        if status == "symlink":
            findings.append(Finding("ERROR", bf, None,
                                    "confirmed layer is or sits behind a symlink "
                                    "(cannot verify it is frozen)"))
            continue
        if status == "unreadable":
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify this layer is frozen: a directory "
                                    "on its path is unreadable — fail closed"))
            continue
        if status == "missing":
            findings.append(Finding("ERROR", bf, None,
                                    "confirmed layer deleted — a checkpoint a person "
                                    "approved is a record, not a draft (#9)"))
            continue
        old = _git_show(toplevel, base, bf)
        if old is None:
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify this layer is frozen: its base "
                                    "version is unreadable or not valid UTF-8"))
            continue
        new, rd = _read_utf8(abspath, rel)
        if new is None:
            findings += rd
            continue
        def _norm(t):
            return t.replace("\r\n", "\n").replace("\r", "\n").strip()
        if _norm(old) != _norm(new):
            findings.append(Finding(
                "ERROR", rel, None,
                "confirmed layer edited — a layer is frozen at its checkpoint "
                "commit; record the correction in the next layer instead (#9)"))
    return findings
```

- [ ] **Step 3: Wire it into `main()`, replacing the pairwise dedupe with an accumulator.** Replace this block:

```python
    if diff_base is not None:
        mem = memory_diff_findings(root, diff_base)
        findings += mem
        # Both diff modes resolve the git context independently, so a fatal
        # context ERROR (bad ref, not a repo) arrives identically from each —
        # print it once. Dedupe against the memory pass ONLY (Codex r2): a
        # stateless finding that legitimately recurs in the blast pass must
        # not be swallowed.
        mem_set = set(mem)
        findings += [f for f in blast_radius_diff_findings(root, diff_base) if f not in mem_set]
```

with:

```python
    if diff_base is not None:
        # Every diff pass resolves the git context independently, so a fatal
        # context ERROR (bad ref, not a repo) arrives identically from each —
        # print it once. Each pass dedupes against the passes BEFORE it, never
        # against the stateless findings (Codex r2 of 1.5d-ii): a stateless
        # finding that legitimately recurs in a diff pass must not be swallowed.
        seen = set()
        for diff_pass in (memory_diff_findings,
                          blast_radius_diff_findings,
                          interview_diff_findings):
            fresh = [f for f in diff_pass(root, diff_base) if f not in seen]
            seen.update(fresh)
            findings += fresh
```

> Add a regression test asserting that an unknown `--diff` ref produces **exactly one** context ERROR through `main()`, not three. That test is the only thing standing between this refactor and a silent triple-print.

- [ ] **Step 4: Prove the guard is live on real content** (deliberate red, then revert)

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
p = pathlib.Path("demo/interview/02-customer-success.md")
orig = p.read_text()
p.write_text(orig.replace("fifteen had a written brief", "sixteen had a written brief", 1))
r = subprocess.run([sys.executable, "scripts/validate.py", ".", "--diff", "main"],
                   capture_output=True, text=True)
p.write_text(orig)
hits = [l for l in r.stdout.splitlines() if "02-customer-success" in l]
print("exit:", r.returncode)
for l in hits:
    print("   ", l)
assert r.returncode != 0 and any("frozen at its checkpoint" in l for l in hits), \
    "the frozen-layer guard did NOT fire — committed layers are not actually frozen"
print("OK: a committed layer is frozen")
PY
```

Expected: non-zero exit and the frozen-layer ERROR. Then confirm a `_working.md` edit is *not* an error:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
p = pathlib.Path("demo/interview/_working.md")
orig = p.read_text()
p.write_text(orig + "\nA provisional note added this turn.\n")
r = subprocess.run([sys.executable, "scripts/validate.py", ".", "--diff", "main"],
                   capture_output=True, text=True)
p.write_text(orig)
print("exit:", r.returncode)
assert r.returncode == 0 and "_working.md" not in r.stdout, \
    "the working file is being frozen — only NN-*.md layers are"
print("OK: the turn in flight is free to change")
PY
```

> These two probes only mean something as a pair: the second asserts an **absence**, which is worthless alone and load-bearing next to the first, which proves the same code path is live and loud on the same directory.

- [ ] **Step 5: Gate + commit**

Run the three gate commands. Test count is up again; record it.

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): freeze confirmed interview layers on --diff (#9)

A confirmed layer is immutable once committed, so 'confirmed' is git structure
rather than a label a resuming agent can rewrite. Third diff pass, so main()'s
pairwise dedupe becomes an accumulator.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: Honesty, the anti-hollow probe, and the full gate

**Files:** Modify `AGENTS.md`, `demo/README.md`, `docs/known-limitations.md`.

- [ ] **Step 1: Update `AGENTS.md`.** In "Built and working", add after the `memory/` bullet:

```markdown
- `interview/` — the **state format** an interview writes: a fixed `00-manifest.md`, one
  frozen file per confirmed layer, one dirty `_working.md`, and the promote-and-commit
  protocol (#9). `check_interview_state` enforces the manifest-vs-files drift and
  `--diff` freezes committed layers, so "confirmed" is git structure rather than a label.
```

In "Not built yet", **replace** the `interview/` bullet with:

```markdown
- `interview/` — the **interview itself**. The state format is built (above); the
  consultant protocol, the question skeleton, and the generator that writes a company OS
  are Slices 3.2 and 3.3. **Pointing your agent at this repo does not yet run an
  interview.**
```

In "The map" table, add a row after `memory/`:

```markdown
| `interview/` | The resumable interview-state format (#9). The interview itself is not built. |
```

And update the "The interview (not built — Phase 3)" section's closing line to:

```markdown
**That generator does not exist yet.** What exists is the *state format* it will write
into — `interview/README.md` — proven against a worked example in `demo/interview/`.
Anything describing the interview as runnable is wrong.
```

> **Check the line count before committing:** `wc -l AGENTS.md` must stay under 200.

- [ ] **Step 2: Update `demo/README.md`.** Add to the "What is here" list, after the `governance/` bullet:

```markdown
- [`interview/`](interview/00-manifest.md) — the interview that produced all of the
  above: five confirmed layers, each frozen at the checkpoint a named person approved,
  and one turn still in flight. It is the record of *why* this company OS says what it
  says.
```

- [ ] **Step 3: Add the disposition note to `docs/known-limitations.md`.** In the "Demo content (#16)" section, append:

```markdown
- **The demo retains its interview state; that is a disposition, not a rule.**
  `demo/interview/` keeps the confirmed layers the demo's ontology was generated from,
  because that record is the provenance a future re-interview would merge against (#9).
  A real adopter may keep or clean theirs; #10 guarantees only that interview state is
  never *distributed* to employees, which is a different question from whether it is
  retained. Nothing in the validator requires an `interview/` directory to exist.
```

- [ ] **Step 4: The anti-hollow probe.** A dormant check and a clean corpus produce identical output, so plant a violation in the demo's real state:

```bash
python3 - <<'PY'
import subprocess, sys, pathlib
m = pathlib.Path("demo/interview/00-manifest.md")
orig = m.read_text()
m.write_text(orig.replace("  - 04-product.md\n", "", 1))
out = subprocess.run([sys.executable, "scripts/validate.py", "."],
                     capture_output=True, text=True).stdout
m.write_text(orig)
hits = [l for l in out.splitlines() if "demo/interview" in l]
print("PLANTED-VIOLATION FINDINGS:", len(hits))
for l in hits:
    print("   ", l)
assert any("not listed in the manifest" in l for l in hits), \
    "check_interview_state is NOT scanning demo/interview/ — it is a dormant check"
print("OK: demo/interview/ is governed by check_interview_state")
PY
```

Expected: an ERROR reading `layer file is not listed in the manifest — a resuming agent will never read it`, then `OK: …`.

And prove the engine's own `interview/` is silent **by content, not by luck**:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
ig = validate.load_gitignore('.')
dirs = validate._interview_dirs('.', ig)
print("interview state dirs:", dirs)
assert any(d.endswith('demo/interview') for d in dirs), "the demo state dir was not found"
assert not any(d.rstrip('/').endswith('/interview') and 'demo' not in d for d in dirs), \
    "the engine's own interview/ was picked up as state — discovery is name-based, not content-based"
print("OK: state is discovered by 00-manifest.md, so the format spec is silent")
PY
```

- [ ] **Step 5: The full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"` — green; record the final count.
Run: `python3 scripts/validate.py . ; echo "exit: $?"` — exactly `0 error(s), 7 warning(s)`, exit 0.
Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"` — exit 0.
Run: `wc -l AGENTS.md` — under 200.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md demo/README.md docs/known-limitations.md
git commit -m "docs: the interview state format is built; the interview is not

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No consultant protocol and no question skeleton.** Slice **3.2**: §4's four mechanics
  (define-the-role-first, one-question-at-a-time, evidence-based read-what-exists,
  checkpoint approvals), the intent-engineering 9-section skeleton, and the
  constitution-compiler five-question worksheet. `interview/README.md` documents the
  *state machine* — when a working file is promoted — not the interviewing style.
- **No generator.** Slice **3.3**: writing `your-company/` in the demo-proven shape, plus
  #10's two-repo semantics. Nothing in this slice generates anything.
- **No `your-company/`.** Per #10 it is not a committed directory in this repo at all;
  it survives only as documentation of the two-repo model.
- **Still open for the maintainer:** the Phase 3 re-ordering (design call 1), three Slice
  1.5d-ii deferrals, the `SKIP_RELPATHS` gate-scoping sign-off, the standing re-review
  rule, the `Motion: assist` reading, and the two 2.3d carry-overs (the duplicated stdlib
  allowlist and the `demo/README.md` directory-link residual).

## Self-Review

- **Ticket coverage.** #9 in full: the fixed `00-manifest.md` pointer with `phase`,
  `status`, the open-question id, the role frame and the layer list; one frozen committed
  file per confirmed layer; a single dirty `_working.md`; #7's provenance vocabulary
  reused rather than duplicated (`confirmed` vs `observed`/`inferred`, and #7's own
  ERROR-for-confirmed / WARN-otherwise split on `source`); the manifest-vs-file drift
  that #9 explicitly accepted as this shape's cost, now the check that pays it; and the
  frozen-at-commit doctrine enforced by the same `--diff` mechanic #7 defined. #10: the
  state lives in the private company repo, stated at the top of the format doc. §4:
  checkpoint approvals are recorded as `confirmed_by` / `confirmed_at`, and the
  evidence-based read-what-exists move is where `observed` facts with a `source:` come
  from — both surfaced in the demo's layers.
- **Design calls surfaced, not buried.** Five, each with its rejected alternative: the
  Phase 3 re-ordering (the one I most want reviewed); frontmatter instead of a second
  Markdown table, with **no status column** because a declared status is the
  agent-honored label #9 rejected; content-based discovery so the engine's own
  `interview/` is silent; the demo retaining its interview state, which answers a fog
  question in one direction; and `main()`'s dedupe becoming an accumulator.
- **The 2.2a lesson is applied, not re-learned.** This is a format groundwork's own
  generator writes, so it gets a **restricted grammar**: `layers` must be a list, layer
  filenames must be `NN-slug.md` with `NN` from `01`, `00` is reserved, and anything else
  ERRORs with a message naming the required shape. No second table parser is created —
  the one canonical table grammar in this repo still governs `_executive-view.md` and
  nothing else.
- **The 1.4b lesson is applied.** The diff pass is driven by the **base file list**, and
  a directory counts as interview state when it carried a manifest **at base** — so
  deleting the manifest in the same diff cannot un-freeze the layers beneath it.
- **Anti-hollow probes, in both directions.** Four: an unlisted layer must ERROR (proving
  the stateless check reaches `demo/interview/`); a committed layer edit must ERROR
  (proving the diff guard is live); a `_working.md` edit must **not** error; and
  `_interview_dirs` must find the demo's state and **not** the engine's spec directory.
  The two absence-assertions are only meaningful next to the presence-assertions on the
  same code path, and the plan says so where they are written.
- **The dormant-check window is named.** After Task 2 the check has no corpus and passes
  vacuously; the plan says so at Task 2 Step 4 and closes it at Task 3, with Task 5's
  probe as the proof. That window is the single most likely way this slice ships hollow.
- **The cut line is named rather than left to discretion.** Task 4 is the half that makes
  #9's decision true; if it cannot land in this session it becomes a named Slice 3.1b in
  the spec, never a silent drop.
- **Placeholder scan:** no TBD/TODO. All ten new files are given in full; both check
  implementations are given in full; every modification quotes its replacement text.
- **Pre-empts the recurring findings.** (a) *Non-scalar frontmatter* — every manifest and
  layer field is checked with `_blank` **and** `isinstance`, and a bare `key:` (which the
  #11 reader returns as `[]`) is covered by an explicit test. (b) *Alias laundering* —
  symlinked manifests, layers, and working files all ERROR in the stateless check, and
  the diff pass uses `_committed_path_status` for the same reason `memory_diff_findings`
  does; layer names are matched with `fullmatch` against a fixed pattern, and never
  joined from user-supplied path fragments, so there is no path to climb out of the
  directory. (c) *Fail-open on malformed input* — an unreadable manifest, an unlistable
  state directory, an unreadable base blob, and an undecodable working file all resolve
  to ERROR, never to "unchanged" or "silent". (d) *Entropy and identifiers* — no external
  URLs, no phone-shaped runs, no 40-character tokens; every new filename is short. (e)
  *Corpus void* — the check is content-discovered, so the plan's dormant window is stated
  explicitly and closed with a planted violation rather than assumed away.
- **Type consistency:** `check_interview_state(root, ignore=())` matches every other
  structural check's signature and is wired at the end of `validate()`;
  `interview_diff_findings(root, base)` matches `memory_diff_findings`'s signature and
  reuses `_git_diff_context`, `_git_show`, `_committed_path_status`,
  `_diff_in_workbench_skips`, and `_read_utf8` unchanged.
