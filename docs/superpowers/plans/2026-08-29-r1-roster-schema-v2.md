# R1 — the roles roster and the v1→v2 schema bump

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land `governance/roles.md` as a validated artifact, make an active constitution
rule's owners resolve against it, and spend groundwork's first `SCHEMA_VERSION` bump wiring
the per-check `since:` demotion mechanism that makes the migration boundary one clean error
instead of a scatter.

**Architecture:** One roster file per validated instance, parsed with the repository's
existing canonical table grammar (`_canonical_row`). Resolution is by exact string, two
ways — a Role cell resolves to that row's holders, a Holder cell resolves to that holder.
The roster's *schema* is checked by a new `check_roles`; *resolution of owner values against
it* lives inside `_check_constitution_instance`, where the rule frontmatter already is.
Every new check carries `since: 2` and demotes ERROR→WARN behind a v1 pin's single
migration-boundary ERROR. The roster becomes the third governed artifact family under #17,
with one exemption: a roster **added** in the same diff that moves its root's pin from v1 to
v2 is the sanctioned migration crossing.

**Tech Stack:** Python 3 standard library only (zero dependencies, enforced by
`TestZeroDep`). `unittest` — there is no pytest in this environment. Markdown content.

---

## Source of truth, and what is locked

`docs/superpowers/specs/2026-08-28-roles-accountable-unit-design.md` — eight locked
maintainer decisions and the **Landing order** section, which is this slice's content
list. Locked means locked: do not reopen a decision, and do not write policy the design
does not carry. If a question arises that the design does not answer, **stop and escalate**
with options, a recommendation, its reason, and the honest counter-argument
(`docs/agents/build-sessions.md` rule 5). Removing unapproved text preserves a locked
decision's silence; adding text legislates. They are not symmetric.

### Maintainer inputs, taken at plan time (2026-08-29)

Both were reserved by the design and are now answered. They are not open.

1. **The engine-root roster's holders.** `Head of IT` and `CISO` are both held by
   **`Sean Winslow`, typed `human`**, and the roster's `source` line states that groundwork
   is solo-maintained and the maintainer answers for every role its example rule names.
   The alternative offered was a descriptive holder string (`groundwork maintainer`); the
   maintainer chose the named person, so that the first roster an adopter reads teaches that
   a Holder cell holds a person.
2. **Intent-blind resolution.** Accepted as a documented blind spot, recorded in
   `docs/known-limitations.md`, with typed owner references (`role:` / `person:`) kept as
   the recorded alternative if it ever bites. Typed references now, and optional typed
   prefixes, were both offered and declined.

### Baseline verified at planning time (2026-08-29)

- `main` is `ddcb7a1`. Branch: `feat/roster-schema-v2`, worktree
  `~/Code-Brain/groundwork-wt-r1-roster`.
- `python3 scripts/validate.py .` → `0 error(s), 7 warning(s)`, exit 0.
- `python3 scripts/validate.py . --diff main` → exit 0.
- `python3 scripts/validate.py demo` → `0 error(s), 2 warning(s)`, exit 0.
- `python3 -m unittest discover -s tests -q` → OK, 709 tests, skipped=1.
- `AGENTS.md` is 162 lines (the cap is 200).

### The invariants every task must hold

- **The engine root stays `0 error(s), 7 warning(s)`.** If the count moves, a check is
  firing where it should not — the 2.3a scoping-bug class. Tasks 3 and 5 are the only
  places new engine-root content lands, and neither may add a WARN.
- **`demo` stays `0 error(s), 2 warning(s)`.** The demo's roster carries a `review_by` in
  the future precisely so it adds no staleness WARN.
- **`--diff main` stays exit 0**, at every task.
- **The test count never drops.** Record it after each task.
- **Zero dependencies.** `TestZeroDep` enforces it; nothing new imports anything.

### Rule 9 — the review record, from round 1

This branch adds exactly one plan, so the review directory is
`docs/superpowers/plans/r1-roster-schema-v2-reviews/` (this plan's filename with the leading
`2026-08-29-` and the `.md` removed). That path is free in `main`, verified at planning
time. Task 9 creates its `README.md`. One file per entry, `round-NN.md` from 01, immutable
once committed; corrections go in a later entry, never by editing an earlier one.

---

## File structure

**Created:**

| Path | Responsibility |
|---|---|
| `governance/roles.md` | The engine root's own roster. Two role rows, one holder. |
| `demo/governance/roles.md` | Umbercress's roster. Three holder-only rows. |
| `docs/superpowers/plans/r1-roster-schema-v2-reviews/README.md` | Rule 9's per-branch record. |

**Modified:**

| Path | What changes |
|---|---|
| `scripts/validate.py` | `Finding.since`; the demotion pass; roster parsing + `check_roles`; resolution inside `_check_constitution_instance`; `SCHEMA_VERSION = 2`; the roster as a governed family in `_governed_class`, `classify_governed_change`, `_check_proposals_instance`, and `blast_radius_diff_findings`. |
| `tests/test_validate.py` | `ROSTER_OK` fixture; `TestConstitution._rule` writes it; six new test classes (`TestSinceDemotion`, `TestRoster`, `TestRosterResolution`, `TestAppealReachesAHuman`, `TestRosterProposalTarget`, `TestRosterIsGoverned`). |
| `demo/groundwork.pin` | `schema_version: 1` → `2`. |
| `MIGRATIONS.md` | The v1→v2 note; the `since:` section flips from deferred to wired; current version 2. |
| `docs/rule-map.md` | A `check_roles` row; updated severities for `check_constitution` and `blast_radius_diff_findings`. |
| `docs/known-limitations.md` | Four entries: a stale roster, intent-blind resolution, owner fields outside the constitution, roster deletion. |
| `governance/README.md` | The roster's file grammar. |
| `demo/governance/README.md`, `demo/README.md` | The demo's own narration of its roster. `demo/canon.md` was checked and carries no inventory of demo contents, so it is not touched. |
| `CONTEXT.md`, `AGENTS.md`, `proposals/README.md` | The #17 routing enumeration: two artifact families → three. |
| `interview/generate.md` | The minimal R1-window workflow edits: pin `2`, roster generation, the declared-draft permission with its report obligation. |

### One decision this plan makes, and flags

`CONTEXT.md:57` currently reads "the **only two artifact kinds** the three buckets route."
Under locked decision 8 that sentence is **false**, not merely incomplete — so Task 6 amends
it. `CONTEXT.md` is the locked-decision glossary and the previous slice's review rejected
touching it *for scope*; this touch is different in kind — it transcribes a locked decision
into the glossary that exists to record locked decisions, and leaving `main` carrying a
false sentence would violate build-sessions rule 6. The amendment is minimal: two → three,
naming the roster. **Flag it in the round-1 review record so the reviewer sees it named
rather than discovering it.**

`CONTEXT.md:61`'s auto-apply test is *incomplete* rather than false — its "exactly when"
clause is on the auto-apply side and stays true — but its escalating enumeration is a list a
reader will take as closed. Task 6 adds the roster to it for the same reason.

---

## Task 1: The `since:` demotion mechanism

The mechanism first, with nothing yet declaring `since`. This task changes no severity
anywhere: it is provably inert until Task 3 tags a finding.

**Files:**
- Modify: `scripts/validate.py:21` (the `Finding` namedtuple), and add `_pin_versions` /
  `apply_since_demotion` beside `check_version_pin`; wire into `validate()` and `main()`.
- Test: `tests/test_validate.py` (new class `TestSinceDemotion`, placed immediately after
  `TestVersionPin`).

- [ ] **Step 1: Write the failing tests**

Add after the `TestVersionPin` class:

```python
class TestSinceDemotion(unittest.TestCase):
    """#21's per-check `since:` mechanism, wired at the v1->v2 bump. A finding
    introduced at schema vN demotes ERROR -> WARN for content pinned below N.
    The gate is NOT softened: a pin below the engine is already red at
    check_version_pin's single migration-boundary ERROR, and these demoted WARNs
    are the precise finger-pointing MIGRATIONS.md promises behind it."""

    def test_finding_defaults_to_no_since(self):
        f = validate.Finding("ERROR", "x.md", None, "m")
        self.assertIsNone(f.since)

    def test_pin_versions_maps_dirs_to_ints(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "co/groundwork.pin", "---\nschema_version: 1\n---\n")
            self.assertEqual(validate._pin_versions(d), {"co": 1})

    def test_root_pin_maps_to_the_empty_key(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", "---\nschema_version: 1\n---\n")
            self.assertEqual(validate._pin_versions(d), {"": 1})

    def test_malformed_pin_is_absent_not_lenient(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "co/groundwork.pin", "---\nschema_version: someday\n---\n")
            self.assertEqual(validate._pin_versions(d), {})

    def test_error_demotes_behind_an_older_pin(self):
        f = validate.Finding("ERROR", "co/governance/roles.md", None, "m", 2)
        out = validate.apply_since_demotion([f], {"co": 1})
        self.assertEqual(out[0].level, "WARN")
        self.assertIn("new since schema v2", out[0].message)
        self.assertIn("pinned at v1", out[0].message)

    def test_error_stands_at_the_pinned_version(self):
        f = validate.Finding("ERROR", "co/governance/roles.md", None, "m", 2)
        self.assertEqual(validate.apply_since_demotion([f], {"co": 2})[0].level, "ERROR")

    def test_unpinned_content_is_never_demoted(self):
        """The engine root carries no pin, so its own content is current by
        definition — demoting there would silently disarm the engine's own gate."""
        f = validate.Finding("ERROR", "governance/roles.md", None, "m", 2)
        self.assertEqual(validate.apply_since_demotion([f], {"co": 1})[0].level, "ERROR")

    def test_nearest_enclosing_pin_wins(self):
        f = validate.Finding("ERROR", "co/inner/governance/roles.md", None, "m", 2)
        out = validate.apply_since_demotion([f], {"co": 1, "co/inner": 2})
        self.assertEqual(out[0].level, "ERROR")

    def test_warns_and_untagged_findings_pass_through_unchanged(self):
        warn = validate.Finding("WARN", "co/x.md", None, "m", 2)
        plain = validate.Finding("ERROR", "co/x.md", None, "m")
        out = validate.apply_since_demotion([warn, plain], {"co": 1})
        self.assertEqual(out, [warn, plain])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_validate.TestSinceDemotion -v`
Expected: FAIL — `AttributeError: module 'validate' has no attribute '_pin_versions'`, and
`TypeError` on the five-argument `Finding`.

- [ ] **Step 3: Add the `since` field**

Replace `scripts/validate.py:21`:

```python
Finding = namedtuple("Finding", ["level", "path", "line", "message"])
```

with:

```python
# `since` is the SCHEMA_VERSION a check was introduced at (#21's per-check
# demotion), and defaults to None: a check that predates versioning binds every
# pin. See apply_since_demotion.
Finding = namedtuple("Finding", ["level", "path", "line", "message", "since"],
                     defaults=(None,))
```

- [ ] **Step 4: Add the demotion pass**

Insert immediately after `check_version_pin` ends (before `def check_company_root`):

```python
def _pin_versions(root, ignore=()):
    """{root-relative directory -> pinned schema version} for every readable
    groundwork.pin under root, where "" is root itself.

    A pin that is missing, unparseable, or non-integer is simply ABSENT here:
    check_version_pin already ERRORs on it, and letting a malformed pin grant
    leniency would make the broken state the quiet one. .gitignore is honored
    (as check_version_pin does), so a pin hidden behind an ignore rule buys no
    demotion — the safe direction."""
    out = {}
    for abspath in iter_files(root, ignore):
        if os.path.basename(abspath) != "groundwork.pin":
            continue
        rel = os.path.relpath(abspath, root)
        data, _f = _load_frontmatter(abspath, rel)
        if data is None:
            continue
        sv = data.get("schema_version")
        if not isinstance(sv, str):
            continue
        try:
            pinned = int(sv.strip())
        except ValueError:
            continue
        out[os.path.dirname(rel).replace(os.sep, "/")] = pinned
    return out


def apply_since_demotion(findings, pins):
    """#21's per-check `since:` mechanism, wired at the v1->v2 bump (MIGRATIONS.md).

    A finding carrying `since=N` demotes ERROR -> WARN when the nearest enclosing
    pinned root pins BELOW N: a v1 repo has no roster, so a v2 resolution check
    cannot bind content pinned before rosters existed. This never means a green
    gate — that root is already red at check_version_pin's single
    migration-boundary ERROR, and these WARNs are the finger-pointing behind it.

    Content under no pin (the engine's own tree) is never demoted: it is current
    by definition, which is what keeps groundwork's own gate armed.

    Applied at the COMPOSITION points — validate() and main()'s diff passes. A
    check called directly returns undemoted findings; only the caller that knows
    the tree knows the pins."""
    if not pins:
        return findings
    out = []
    for f in findings:
        if f.since is None or f.level != "ERROR":
            out.append(f)
            continue
        parts = f.path.replace(os.sep, "/").split("/")
        pinned = None
        for n in range(len(parts) - 1, -1, -1):
            d = "/".join(parts[:n])
            if d in pins:
                pinned = pins[d]
                break
        if pinned is not None and pinned < f.since:
            out.append(f._replace(level="WARN", message=(
                "%s [new since schema v%d; this content is pinned at v%d — "
                "see MIGRATIONS.md]" % (f.message, f.since, pinned))))
        else:
            out.append(f)
    return out
```

- [ ] **Step 5: Wire it into `validate()`**

In `validate()`, replace the final `return findings` with:

```python
    return apply_since_demotion(findings, _pin_versions(root, ignore))
```

- [ ] **Step 6: Wire it into `main()`'s diff passes**

In `main()`, replace the diff block:

```python
    if diff_base is not None:
        seen = set()
        for diff_pass in (memory_diff_findings,
                          blast_radius_diff_findings,
                          interview_diff_findings):
            fresh = [f for f in diff_pass(root, diff_base) if f not in seen]
            seen.update(fresh)
            findings += fresh
```

with:

```python
    if diff_base is not None:
        # Dedupe on the RAW findings, then demote: demotion rewrites the message,
        # so deduping after it would compare rewritten tuples against raw ones.
        pins = _pin_versions(root, load_gitignore(root))
        seen = set()
        for diff_pass in (memory_diff_findings,
                          blast_radius_diff_findings,
                          interview_diff_findings):
            fresh = [f for f in diff_pass(root, diff_base) if f not in seen]
            seen.update(fresh)
            findings += apply_since_demotion(fresh, pins)
```

Leave the comment above `seen` in place (it explains why each pass dedupes only against the
passes before it).

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate.TestSinceDemotion -v`
Expected: PASS, 9 tests.

- [ ] **Step 8: Full gate — the mechanism must be inert**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
```
Expected: OK, 718 tests, skipped=1.

```bash
python3 scripts/validate.py . ; echo "exit: $?"
```
Expected: exactly `0 error(s), 7 warning(s)`, exit 0. **Nothing carries `since` yet, so a
single moved count means the demotion pass is rewriting a finding it should not touch.**

```bash
python3 scripts/validate.py demo 2>&1 | tail -2 ; python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: `0 error(s), 2 warning(s)`; diff exit 0.

- [ ] **Step 9: Commit**

```bash
git add scripts/validate.py tests/test_validate.py && git commit -m "feat(validator): wire #21's per-check since: demotion, inert until v2"
```

---

## Task 2: Parse the roster — `check_roles`

Schema and integrity only. No roster file exists yet anywhere, so this task is also inert.

**Files:**
- Modify: `scripts/validate.py` (new block after `_check_constitution_instance`, before
  `INTERVIEW_MANIFEST`), `validate()`'s check list, `docs/rule-map.md`.
- Test: `tests/test_validate.py` (new class `TestRoster`, after `TestConstitutionProvenance`).

- [ ] **Step 1: Write the failing tests**

```python
ROSTER_OK = """---
valid_at: 2026-08-01
review_by: 2099-01-01
source: The maintainer's own statement
---
# Roles — who holds what

| Role | Holder | Type |
|---|---|---|
| Head of IT | Sean Winslow | human |
| CISO | Sean Winslow | human |
"""


class TestRoster(unittest.TestCase):
    """governance/roles.md: the file that decides who holds every owner an active
    rule names. Its own schema and integrity live here; resolving owner VALUES
    against it lives with the rules, in check_constitution."""

    def _roster(self, d, text=ROSTER_OK):
        _write(d, "governance/roles.md", text)

    def test_valid_roster_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d)
            self.assertEqual(validate.check_roles(d), [])

    def test_no_roster_is_silent_here(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/changelog.md", "# changelog\n")
            self.assertEqual(validate.check_roles(d), [])

    def test_roles_and_holders_parse(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d)
            roster, findings = validate._load_roster(d, d)
            self.assertEqual(findings, [])
            self.assertEqual(roster.roles["Head of IT"], ["Sean Winslow"])
            self.assertEqual(roster.holders["Sean Winslow"], "human")

    def test_missing_frontmatter_field_errors(self):
        for field in ("valid_at", "review_by", "source"):
            with tempfile.TemporaryDirectory() as d:
                self._roster(d, re.sub(r"(?m)^%s:.*\n" % field, "", ROSTER_OK))
                errs = [f for f in validate.check_roles(d) if f.level == "ERROR"]
                self.assertTrue(any(field in f.message for f in errs), field)

    def test_every_roster_finding_carries_since_two(self):
        """The roster does not exist below v2, so every finding about it must
        demote behind a v1 pin. One untagged finding would ERROR a v1 repo on a
        requirement that repo could not have met."""
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| Sean Winslow | Ada Byron | human |")
                         .replace("review_by: 2099-01-01\n", ""))
            findings = validate.check_roles(d)
            self.assertGreater(len(findings), 1)
            self.assertTrue(all(f.since == 2 for f in findings),
                            [f for f in findings if f.since != 2])

    def test_non_iso_valid_at_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("valid_at: 2026-08-01", "valid_at: someday"))
            self.assertTrue(any(f.level == "ERROR" and "valid_at" in f.message
                                for f in validate.check_roles(d)))

    def test_future_valid_at_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("valid_at: 2026-08-01", "valid_at: 2099-01-01"))
            self.assertTrue(any(f.level == "ERROR" and "future" in f.message
                                for f in validate.check_roles(d)))

    def test_passed_review_by_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("review_by: 2099-01-01", "review_by: 2020-01-01"))
            findings = validate.check_roles(d)
            self.assertTrue(any(f.level == "WARN" and "review_by" in f.message
                                for f in findings))
            self.assertFalse(any(f.level == "ERROR" for f in findings))

    def test_namespace_collision_errors(self):
        """A string that is both a Role and a Holder makes every owner reference
        to it ambiguous, and no precedence rule is defined because none should
        be needed."""
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| Sean Winslow | Ada Byron | human |"))
            self.assertTrue(any(f.level == "ERROR" and "both a Role and a Holder" in f.message
                                for f in validate.check_roles(d)))

    def test_conflicting_holder_types_error(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| CISO | Sean Winslow | agent |"))
            self.assertTrue(any(f.level == "ERROR" and "typed both" in f.message
                                for f in validate.check_roles(d)))

    def test_invalid_holder_type_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| CISO | Sean Winslow | person |"))
            self.assertTrue(any(f.level == "ERROR" and "type" in f.message
                                for f in validate.check_roles(d)))

    def test_holder_only_row_is_legal(self):
        """R1's generation writes person-confirmed owners as holder-only rows:
        a name, no role asserted."""
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "|  | Ada Byron | human |"))
            self.assertEqual([f for f in validate.check_roles(d) if f.level == "ERROR"], [])
            roster, _f = validate._load_roster(d, d)
            self.assertEqual(roster.holders["Ada Byron"], "human")

    def test_role_row_with_no_holder_is_legal_and_unheld(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| CISO |  |  |"))
            self.assertEqual([f for f in validate.check_roles(d) if f.level == "ERROR"], [])
            roster, _f = validate._load_roster(d, d)
            self.assertEqual(roster.roles["CISO"], [])
            self.assertEqual(validate._resolve_owner(roster, "CISO"), [])

    def test_empty_row_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |", "|  |  |  |"))
            self.assertTrue(any(f.level == "ERROR" and "neither a role nor a holder" in f.message
                                for f in validate.check_roles(d)))

    def test_type_without_a_holder_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| CISO |  | human |"))
            self.assertTrue(any(f.level == "ERROR" and "types a holder it does not name"
                                in f.message for f in validate.check_roles(d)))

    def test_markup_in_a_cell_errors(self):
        """Resolution is by exact string, so a bolded name is a DIFFERENT string
        from the one the rule carries — silently unresolvable."""
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                              "| CISO | **Sean Winslow** | human |"))
            self.assertTrue(any(f.level == "ERROR" and "plain text" in f.message
                                for f in validate.check_roles(d)))

    def test_missing_header_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK.replace("| Role | Holder | Type |\n", ""))
            self.assertTrue(any(f.level == "ERROR" and "header" in f.message
                                for f in validate.check_roles(d)))

    def test_one_role_two_holders(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d, ROSTER_OK + "| Head of IT | Ada Byron | human |\n")
            self.assertEqual([f for f in validate.check_roles(d) if f.level == "ERROR"], [])
            roster, _f = validate._load_roster(d, d)
            self.assertEqual(roster.roles["Head of IT"], ["Sean Winslow", "Ada Byron"])

    def test_nested_instance_roster_is_checked(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "co/governance/roles.md",
                   ROSTER_OK.replace("| CISO | Sean Winslow | human |", "|  |  |  |"))
            self.assertTrue(any(f.level == "ERROR" and f.path.startswith("co/")
                                for f in validate.check_roles(d)))

    def test_resolution_is_two_way_and_exact(self):
        with tempfile.TemporaryDirectory() as d:
            self._roster(d)
            roster, _f = validate._load_roster(d, d)
            self.assertEqual(validate._resolve_owner(roster, "Head of IT"),
                             [("Sean Winslow", "human")])
            self.assertEqual(validate._resolve_owner(roster, "Sean Winslow"),
                             [("Sean Winslow", "human")])
            self.assertEqual(validate._resolve_owner(roster, "head of it"), [])
            self.assertEqual(validate._resolve_owner(roster, "Ada Byron"), [])
            self.assertEqual(validate._resolve_owner(None, "Head of IT"), [])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_validate.TestRoster -v`
Expected: FAIL — `module 'validate' has no attribute 'check_roles'`.

- [ ] **Step 3: Implement the roster**

Insert into `scripts/validate.py` immediately after `_check_constitution_instance` ends and
before the `INTERVIEW_MANIFEST = "00-manifest.md"` line:

```python
# --- The roles roster (#R1 / decision 4) ----------------------------------
# One file per validated instance. It is the ONLY place resolution happens, so
# it is one place to go stale — and a dated one. Written inline in every rule's
# frontmatter instead, it would build the parallel-site drift class into every
# adopter repo.
ROSTER_REL = ("governance", "roles.md")
ROSTER_FIELDS = ("valid_at", "review_by", "source")
HOLDER_TYPES = {"human", "agent"}
ROSTER_HEADER = ["role", "holder", "type"]

# roles: {role -> [holder, ...]}, where [] is a declared-but-unheld role.
# holders: {holder -> "human" | "agent"}.
Roster = namedtuple("Roster", ["roles", "holders"])


def _parse_roster(text, rel):
    """Parse one governance/roles.md into (Roster, findings).

    The table grammar is _canonical_row — the SAME one the executive view uses.
    A second table grammar in this repo is a decision nobody should make twice.
    Rows are read from the FULL text, not the body: a frontmatter line can never
    start with '|', so the line numbers stay the file's own.

    Every finding here carries since=2. The roster does not exist below v2, so a
    v1-pinned repo could not have met any of these requirements."""
    findings = []
    data, _body, fm = _frontmatter_and_body(text, rel)
    findings += fm
    today = datetime.date.today()

    for field in ROSTER_FIELDS:
        v = data.get(field)
        if not (isinstance(v, str) and _answered(v)):
            findings.append(Finding("ERROR", rel, None,
                                    "roster missing '%s' — the roster is dated content "
                                    "(valid_at, review_by, source), org-memory style" % field, 2))
            continue
        if field == "source":
            continue
        d = _parse_date(v)
        if d is None:
            findings.append(Finding("ERROR", rel, None,
                                    "roster '%s' is not an ISO date (YYYY-MM-DD)" % field, 2))
        elif field == "valid_at" and d > today:
            findings.append(Finding("ERROR", rel, None,
                                    "roster 'valid_at' is in the future — it records when "
                                    "the mapping was last confirmed, never a plan", 2))
        elif field == "review_by" and d < today:
            findings.append(Finding("WARN", rel, None,
                                    "roster 'review_by' has passed — who holds what may "
                                    "have drifted", 2))

    roles, holders, header_seen = {}, {}, False
    for lineno, line in enumerate(text.split("\n"), 1):
        cells = _canonical_row(line)
        if cells is None:
            continue
        if [c.casefold() for c in cells] == ROSTER_HEADER:
            header_seen = True
            continue
        if all(c and set(c) <= set("-: ") for c in cells):
            continue  # delimiter
        role, holder, htype = cells
        bad_cell = False
        for label, cell in (("Role", role), ("Holder", holder), ("Type", htype)):
            if cell and not _is_plain_text(cell):
                findings.append(Finding("ERROR", rel, lineno,
                                        "roster %s cell carries markup — cells are plain "
                                        "text, and resolution is by exact string" % label, 2))
                bad_cell = True
        if bad_cell:
            continue
        if not role and not holder:
            findings.append(Finding("ERROR", rel, lineno,
                                    "roster row names neither a role nor a holder", 2))
            continue
        if holder:
            if htype not in HOLDER_TYPES:
                findings.append(Finding("ERROR", rel, lineno,
                                        "roster holder %r has type %r (one of %s) — the "
                                        "human-appeal path depends on it"
                                        % (holder, htype, sorted(HOLDER_TYPES)), 2))
            elif holders.get(holder, htype) != htype:
                findings.append(Finding("ERROR", rel, lineno,
                                        "roster holder %r is typed both %r and %r"
                                        % (holder, holders[holder], htype), 2))
            else:
                holders[holder] = htype
        elif htype:
            findings.append(Finding("ERROR", rel, lineno,
                                    "roster row types a holder it does not name", 2))
        if role:
            roles.setdefault(role, [])
            if holder:
                roles[role].append(holder)

    if not header_seen:
        findings.append(Finding("ERROR", rel, None,
                                "roster has no '| Role | Holder | Type |' header row", 2))
    for name in sorted(set(roles) & set(holders)):
        findings.append(Finding("ERROR", rel, None,
                                "%r is both a Role and a Holder — every owner reference to "
                                "it would be ambiguous, and no precedence rule is defined "
                                "because none should be needed" % name, 2))
    return Roster(roles, holders), findings


def _load_roster(inst, root):
    """(Roster, findings) for one instance, or (None, findings) when it has no
    roster. The findings belong to check_roles; every other caller discards them,
    so one malformed roster is reported once."""
    abspath = os.path.join(inst, *ROSTER_REL)
    rel = os.path.relpath(abspath, root)
    if not os.path.isfile(abspath):
        return None, []
    text, rd = _read_utf8(abspath, rel)
    if text is None:
        return None, rd
    roster, findings = _parse_roster(text, rel)
    return roster, rd + findings


def _resolve_owner(roster, value):
    """The holders an owner value resolves to, as [(holder, type)]. Empty means
    UNHELD: no roster match, or a Role row carrying no holder.

    Resolution is by EXACT string, two ways (decision 1 + decision 4): a value
    matching a Role cell resolves to that row's holders; a value matching a
    Holder cell resolves to that holder directly — which is what keeps a
    person-named owner valid.

    It is INTENT-BLIND: nothing marks a value as meant-as-role or meant-as-person,
    so a forgotten role row whose title equals an existing holder name resolves as
    that holder. Accepted and documented (docs/known-limitations.md); typed owner
    references are the recorded alternative."""
    if roster is None or not isinstance(value, str):
        return []
    v = value.strip()
    if v in roster.roles:
        return [(h, roster.holders.get(h)) for h in roster.roles[v]]
    if v in roster.holders:
        return [(v, roster.holders[v])]
    return []


def check_roles(root, ignore=()):
    """The roles roster's own schema and integrity, per instance (see
    _instance_roots). Whether a rule's owners RESOLVE against it is
    check_constitution's, where the rule frontmatter already is."""
    findings = []
    if _ignored("governance", ignore):
        return findings
    for inst in _instance_roots(root, ignore):
        _roster, f = _load_roster(inst, root)
        findings += f
    return findings
```

- [ ] **Step 4: Wire it into `validate()`**

In `validate()`, immediately after the `findings += check_constitution(root, ignore)` line,
add:

```python
    findings += check_roles(root, ignore)
```

- [ ] **Step 5: Add the `docs/rule-map.md` row**

`TestRuleMap` fails on any shipped `check_*` with no row. Insert immediately **after** the
`check_constitution` row:

```markdown
| The roles roster's schema and integrity: dated frontmatter, typed holders, no Role/Holder collision, per instance (R1) | check_roles | ERROR on the schema and on an ambiguous or mistyped holder, WARN on staleness |
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate.TestRoster tests.test_validate.TestRuleMap -v`
Expected: PASS.

- [ ] **Step 7: Full gate — still inert**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: OK, 738 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; diff exit 0. **No roster file exists yet, so any moved count means
`check_roles` is finding something that is not a roster.**

- [ ] **Step 8: Commit**

```bash
git add scripts/validate.py tests/test_validate.py docs/rule-map.md && git commit -m "feat(validator): governance/roles.md — the roster schema and its integrity"
```

---

## Task 3: The rosters, the missing-roster check, and activation resolution

This is the task that turns the gate red and green again in the same commit: the engine
root's own active rule names two roles, so the engine needs its own roster or R1 would break
groundwork's gate.

**Files:**
- Create: `governance/roles.md`, `demo/governance/roles.md`
- Modify: `scripts/validate.py` (`_check_constitution_instance`)
- Test: `tests/test_validate.py` (`TestConstitution._rule`, new class
  `TestRosterResolution`)

- [ ] **Step 1: Write the engine-root roster**

Create `governance/roles.md`. **`valid_at` is today's date at execution** — run
`date +%F` and use it; `review_by` is 90 days later — `python3 -c "import
datetime;print(datetime.date.fromisoformat('<valid_at>')+datetime.timedelta(days=90))"`. At
planning time those are `2026-08-29` and `2026-11-27`; **re-derive them, do not transcribe
them.**

```markdown
---
valid_at: 2026-08-29
review_by: 2026-11-27
source: The maintainer's own statement. groundwork is solo-maintained, so the maintainer answers for every role its own constitution rule names.
---
# Roles — who holds what

This is groundwork's own roster: the engine repository is a validated instance like any
other, and it carries one active constitution rule
([access-grants-need-human-signoff.md](constitution/access-grants-need-human-signoff.md))
whose four owner fields name two roles. A role must be held to activate, so those roles are
recorded here.

An owner value resolves against this table by exact string, two ways: a value matching a
**Role** cell resolves to that row's holders, and a value matching a **Holder** cell
resolves to that holder. `valid_at` is a snapshot — when this mapping was last confirmed,
not when a fact became true.

| Role | Holder | Type |
|---|---|---|
| Head of IT | Sean Winslow | human |
| CISO | Sean Winslow | human |
```

**These holders are maintainer-authored content, given at plan review 2026-08-29.** Nothing
else in the repository says who holds these roles, and an implementing agent must not invent
the answer.

- [ ] **Step 2: Write the demo roster**

Create `demo/governance/roles.md`. Umbercress's three active rules name three people —
`Priya Raman`, `Marcus Bell`, `Ruth Okafor` — and no roles, so every row is **holder-only**
(the Role cell empty): a name, with no role asserted. `valid_at` is the earliest
`confirmed_at` among the interview layers these entries transcribe (`2026-05-11`, layer
`01-role-and-scope.md`) — the conservative aggregate, so no entry's staleness is masked.
`review_by` matches the demo's own recorded review cadence rather than the 90-day interim
default; **it must be in the future or the demo gains a third WARN.**

```markdown
---
valid_at: 2026-05-11
review_by: 2026-11-30
source: The founder's own account, confirmed across interview layers 01–05.
---
# Roles — who holds what

Umbercress is twenty people and holds no formal offices, so this roster asserts no roles:
each row names a **holder** and leaves the Role cell empty. That is what makes a
person-named owner on a constitution rule resolve — `owner: Ruth Okafor` resolves because
Ruth Okafor is a holder here.

`valid_at` is a snapshot: the earliest date among the interview layers these entries came
from, so no entry's staleness is hidden behind a newer one.

| Role | Holder | Type |
|---|---|---|
|  | Priya Raman | human |
|  | Marcus Bell | human |
|  | Ruth Okafor | human |
```

Verify before writing: `grep -h "^owner:\|^value_owner:\|^runtime_check_owner:\|^human_appeal_owner:" demo/governance/constitution/*.md | sort -u`
— the holder set must cover exactly the names that appear.

- [ ] **Step 3: Write the failing tests**

First, give `TestConstitution._rule` a roster, so its fixtures keep meaning what they were
written to mean. Replace:

```python
    def _rule(self, d, text=RULE_OK, name="access.md"):
        _write(d, "governance/constitution/%s" % name, text)
```

with:

```python
    def _rule(self, d, text=RULE_OK, name="access.md", roster=ROSTER_OK):
        """RULE_OK's owners are the two roles ROSTER_OK holds, so the fixture
        writes both: from v2 on, a valid ACTIVE rule is one whose owners resolve.
        Pass roster=None for the no-roster case."""
        _write(d, "governance/constitution/%s" % name, text)
        if roster is not None:
            _write(d, "governance/roles.md", roster)
```

Then add a new class after `TestRoster`:

```python
class TestRosterResolution(unittest.TestCase):
    """Decision 2, held-to-activate: a rule with a rung must have every owner
    field resolve against the roster. A draft may not. The safety-spine checks
    that already run on drafts are untouched."""

    def _inst(self, d, rule=RULE_OK, roster=ROSTER_OK):
        _write(d, "governance/constitution/access.md", rule)
        if roster is not None:
            _write(d, "governance/roles.md", roster)

    def test_active_rule_with_resolving_owners_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d)
            self.assertEqual([f for f in validate.check_constitution(d)
                              if f.level == "ERROR"], [])

    def test_active_rule_with_an_unheld_owner_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, roster=ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                                   "| CISO |  |  |"))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("does not resolve" in f.message and "value_owner" in f.message
                                for f in errs), errs)

    def test_active_rule_with_an_absent_owner_row_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, roster=ROSTER_OK.replace("| Head of IT | Sean Winslow | human |\n", ""))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("does not resolve" in f.message and "'owner'" in f.message
                                for f in errs), errs)

    def test_person_named_owner_resolves_through_a_holder_only_row(self):
        """Decision 1 is ADDITIVE: a person's name stays a valid owner."""
        with tempfile.TemporaryDirectory() as d:
            self._inst(d,
                       rule=RULE_OK.replace("Head of IT", "Ruth Okafor").replace("CISO", "Ruth Okafor"),
                       roster=ROSTER_OK.replace("| Head of IT | Sean Winslow | human |\n"
                                                "| CISO | Sean Winslow | human |\n",
                                                "|  | Ruth Okafor | human |\n"))
            self.assertEqual([f for f in validate.check_constitution(d)
                              if f.level == "ERROR"], [])

    def test_active_rule_and_no_roster_is_one_error_not_a_scatter(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, roster=None)
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertEqual(len(errs), 1, errs)
            self.assertIn("governance/roles.md", errs[0].path)
            self.assertEqual(errs[0].since, 2)

    def test_drafts_only_and_no_roster_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", ""), roster=None)
            findings = validate.check_constitution(d)
            self.assertFalse(any(f.level == "ERROR" and "roles.md" in f.path for f in findings))
            self.assertTrue(any(f.level == "WARN" and "roles.md" in f.path for f in findings))

    def test_no_rules_at_all_needs_no_roster(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/constitution/README.md", "# rules\n")
            self.assertEqual(validate.check_constitution(d), [])

    def test_resolution_errors_carry_since_two(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, roster=ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                                   "| CISO |  |  |"))
            errs = [f for f in validate.check_constitution(d)
                    if f.level == "ERROR" and "does not resolve" in f.message]
            self.assertTrue(errs)
            self.assertTrue(all(f.since == 2 for f in errs))

    def test_v1_pinned_content_demotes_to_a_warn_behind_the_boundary(self):
        """The whole point of the since: mechanism: a v1 repo has no roster, so
        the resolution ERROR must not scatter — the pin's boundary ERROR is the
        one red line, and this is the finger-pointing behind it."""
        with tempfile.TemporaryDirectory() as d:
            _write(d, "co/groundwork.pin", "---\nschema_version: 1\n---\n")
            _write(d, "co/governance/constitution/access.md", RULE_OK)
            findings = validate.validate(d)
            roster_errs = [f for f in findings
                           if f.level == "ERROR" and "roles.md" in f.path]
            self.assertEqual(roster_errs, [])
            demoted = [f for f in findings
                       if f.level == "WARN" and "roles.md" in f.path]
            self.assertTrue(demoted)
            self.assertIn("new since schema v2", demoted[0].message)

    def test_the_engine_root_resolves_its_own_active_rule(self):
        """R1 without an engine-root roster would turn groundwork's own gate red."""
        errs = [f for f in validate.check_constitution(str(REPO)) if f.level == "ERROR"]
        self.assertEqual(errs, [])
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_validate.TestRosterResolution -v`
Expected: FAIL on the unheld/absent/no-roster cases — no resolution check exists yet, so
they report zero ERRORs where one is asserted.

- [ ] **Step 5: Implement resolution in the constitution check**

In `scripts/validate.py`, add beside `_RULE_OBJECT_FIELDS`:

```python
# The four owner fields decision 2 requires to resolve once a rule is active.
# `owner` is checked with its own message and is not in _RULE_OBJECT_FIELDS.
_RULE_OWNER_FIELDS = ["owner", "value_owner", "runtime_check_owner", "human_appeal_owner"]
```

In `_check_constitution_instance`, after `today = datetime.date.today()`, add:

```python
    # The roster resolves owner values. Its OWN findings belong to check_roles,
    # so they are discarded here — one malformed roster is reported once.
    roster, _rf = _load_roster(inst, root)
    rules_seen = active_seen = False
```

Inside the per-rule loop, immediately after `active = not _blank(rung)`, add:

```python
        rules_seen = True
        active_seen = active_seen or active
```

Inside the `else:` (active) branch, after the `for field in _RULE_OBJECT_FIELDS:` loop and
before the rule-statement check, add:

```python
            # Decision 2: held-to-activate. Only when a roster exists — with none,
            # the single missing-roster ERROR below is the whole message, never a
            # scatter of four.
            if roster is not None:
                for field in _RULE_OWNER_FIELDS:
                    v = data.get(field)
                    if not (isinstance(v, str) and _answered(v)):
                        continue  # already ERRORed as missing or a placeholder
                    if not _resolve_owner(roster, v):
                        findings.append(Finding("ERROR", rel, None,
                                                "active rule's '%s' (%s) does not resolve in "
                                                "the roster — a role must be held to activate"
                                                % (field, v.strip()), 2))
```

At the very end of the function, replace `return findings` with:

```python
    if rules_seen and roster is None:
        rel_roster = os.path.relpath(os.path.join(inst, *ROSTER_REL), root)
        if active_seen:
            findings.append(Finding("ERROR", rel_roster, None,
                                    "an active constitution rule needs a roster — "
                                    "governance/roles.md must say who holds every owner "
                                    "it names (a role must be held to activate)", 2))
        else:
            findings.append(Finding("WARN", rel_roster, None,
                                    "no governance/roles.md — a draft rule's owners resolve "
                                    "against nothing until the roster exists", 2))
    return findings
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate.TestRosterResolution tests.test_validate.TestConstitution tests.test_validate.TestConstitutionProvenance -v`
Expected: PASS.

- [ ] **Step 7: Full gate**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: OK, 748 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; diff exit 0.

**If the engine root shows a `governance/roles.md` ERROR**, the roster's holder strings do
not match the rule's owner strings character for character — compare them, do not retype
them. **If `demo` shows a third WARN**, its `review_by` is in the past.

- [ ] **Step 8: Commit**

```bash
git add governance/roles.md demo/governance/roles.md scripts/validate.py tests/test_validate.py && git commit -m "feat(governance): held-to-activate — rosters for the engine root and demo/"
```

---

## Task 4: The appeal-human constraint and draft visibility

**Files:**
- Modify: `scripts/validate.py` (`_check_constitution_instance`)
- Test: `tests/test_validate.py` (new class `TestAppealReachesAHuman`, after
  `TestRosterResolution`)

- [ ] **Step 1: Write the failing tests**

```python
class TestAppealReachesAHuman(unittest.TestCase):
    """Decision 3: the human_appeal_owner must resolve to at least one HUMAN
    holder — an appeal path that terminates in a model is not an appeal path.
    Decision 5: a draft's gaps are named WARNs, not silence."""

    AGENT_ROSTER = ROSTER_OK.replace("| CISO | Sean Winslow | human |",
                                     "| CISO | triage agent | agent |")

    def _inst(self, d, rule=RULE_OK, roster=ROSTER_OK):
        _write(d, "governance/constitution/access.md", rule)
        if roster is not None:
            _write(d, "governance/roles.md", roster)

    def test_active_rule_with_an_agent_only_appeal_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, roster=self.AGENT_ROSTER)
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("terminates in a model" in f.message for f in errs), errs)

    def test_high_risk_draft_with_an_agent_only_appeal_errors(self):
        """The safety spine runs draft-time: an appeal owner that resolves to a
        model is affirmatively wrong, not merely incomplete."""
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", ""),
                       roster=self.AGENT_ROSTER)
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("terminates in a model" in f.message for f in errs), errs)

    def test_high_risk_draft_with_an_appeal_resolving_to_nobody_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", ""),
                       roster=ROSTER_OK.replace("| CISO | Sean Winslow | human |", "| CISO |  |  |"))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("reaches no human" in f.message for f in errs), errs)

    def test_non_high_risk_draft_with_an_agent_only_appeal_warns(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", "")
                       .replace("action_class: high-risk", "action_class: reversible-write"),
                       roster=self.AGENT_ROSTER)
            findings = validate.check_constitution(d)
            self.assertFalse(any(f.level == "ERROR" for f in findings), findings)
            self.assertTrue(any(f.level == "WARN" and "terminates in a model" in f.message
                                for f in findings))

    def test_non_high_risk_draft_with_an_unresolved_appeal_warns_once(self):
        """Decision 5's three classes do not overlap: 'does not resolve' is one
        class, 'resolvable but wrongly typed' is another. An unresolved appeal
        owner on a plain draft is the FIRST, and must not also raise the second."""
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", "")
                       .replace("action_class: high-risk", "action_class: reversible-write"),
                       roster=ROSTER_OK.replace("| CISO | Sean Winslow | human |", "| CISO |  |  |"))
            appeal = [f for f in validate.check_constitution(d)
                      if "human_appeal_owner" in f.message]
            self.assertEqual(len(appeal), 1, appeal)
            self.assertEqual(appeal[0].level, "WARN")

    def test_draft_missing_owner_fields_warn_by_name(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", "")
                       .replace("owner: Head of IT\n", "", 1)
                       .replace("value_owner: CISO\n", ""))
            warns = [f.message for f in validate.check_constitution(d) if f.level == "WARN"]
            self.assertTrue(any("'owner'" in m for m in warns), warns)
            self.assertTrue(any("'value_owner'" in m for m in warns), warns)

    def test_draft_unresolved_owner_warns_by_name(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", ""),
                       roster=ROSTER_OK.replace("| Head of IT | Sean Winslow | human |\n", ""))
            warns = [f.message for f in validate.check_constitution(d) if f.level == "WARN"]
            self.assertTrue(any("does not resolve" in m and "'owner'" in m for m in warns), warns)

    def test_the_existing_draft_spine_error_is_untouched(self):
        """decision 2's verbatim guarantee: a high-risk draft with no appeal path
        must not leave the gate green — the ANSWERED-fields check, unchanged."""
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, rule=RULE_OK.replace("rung: human-decision\n", "")
                       .replace("human_appeal: A denied or delayed grant escalates to the "
                                "CISO, who decides within one business day\n", "")
                       .replace("human_appeal_owner: CISO\n", ""))
            errs = [f for f in validate.check_constitution(d) if f.level == "ERROR"]
            self.assertTrue(any("rung six" in f.message for f in errs))
            self.assertIsNone([f for f in errs if "rung six" in f.message][0].since,
                              "the pre-existing v1 spine ERROR must NOT carry since=2 — it "
                              "keeps firing under any pin")

    def test_appeal_findings_carry_since_two(self):
        with tempfile.TemporaryDirectory() as d:
            self._inst(d, roster=self.AGENT_ROSTER)
            new = [f for f in validate.check_constitution(d)
                   if "terminates in a model" in f.message]
            self.assertTrue(new)
            self.assertTrue(all(f.since == 2 for f in new))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_validate.TestAppealReachesAHuman -v`
Expected: FAIL — no appeal-human or draft-visibility check exists.

- [ ] **Step 3: Implement draft visibility**

In `_check_constitution_instance`, in the `if not active:` branch, after the existing
`"rule not yet placed on a rung (draft)"` WARN, add:

```python
            # Decision 5, hole (a): a draft's gaps are named, not silent. Two
            # classes here — a missing owner field, and one that does not resolve.
            # The third (a resolvable but agent-only appeal owner) is below, with
            # the rest of the appeal tiering.
            for field in _RULE_OWNER_FIELDS:
                v = data.get(field)
                if not (isinstance(v, str) and _answered(v)):
                    findings.append(Finding("WARN", rel, None,
                                            "draft rule has no answered '%s' — an owner field "
                                            "with no answer" % field, 2))
                elif roster is not None and not _resolve_owner(roster, v):
                    findings.append(Finding("WARN", rel, None,
                                            "draft rule's '%s' (%s) does not resolve in the "
                                            "roster (unheld)" % (field, v.strip()), 2))
```

- [ ] **Step 4: Implement the appeal-human constraint**

In `_check_constitution_instance`, immediately after the existing high-risk spine block (the
one whose message contains `"there is no rung six"`), add:

```python
        # Decision 3: the human appeal must reach a HUMAN. Tiering, by the tiers
        # that already exist: ERROR on any active rule, ERROR on a high-risk
        # draft (the safety spine runs draft-time), WARN on a plain draft
        # (decision 5's third class). The 'resolves to nothing' case is NOT
        # repeated here for an active rule (the activation ERROR names it) or for
        # a plain draft (decision 5's second class names it) — only a high-risk
        # draft needs it, where neither of those fires as an ERROR.
        high_risk = isinstance(ac, str) and ac == "high-risk"
        hao = data.get("human_appeal_owner")
        if roster is not None and isinstance(hao, str) and _answered(hao):
            held = _resolve_owner(roster, hao)
            if not held:
                if high_risk and not active:
                    findings.append(Finding("ERROR", rel, None,
                                            "high-risk rule's 'human_appeal_owner' (%s) reaches "
                                            "no human — it resolves to nobody, and an appeal "
                                            "that reaches nobody is not an appeal path"
                                            % hao.strip(), 2))
            elif not any(t == "human" for _h, t in held):
                findings.append(Finding("ERROR" if (active or high_risk) else "WARN", rel, None,
                                        "'human_appeal_owner' (%s) resolves only to agent "
                                        "holders — an appeal path that terminates in a model "
                                        "is not an appeal path" % hao.strip(), 2))
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate.TestAppealReachesAHuman tests.test_validate.TestConstitution tests.test_validate.TestRosterResolution -v`
Expected: PASS.

- [ ] **Step 6: Full gate**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: OK, 758 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; diff exit 0. Neither the engine nor the demo holds a draft rule, so the new
WARN classes must be silent in both.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate.py tests/test_validate.py && git commit -m "feat(governance): the human appeal must reach a human; a draft's gaps are named"
```

---

## Task 5: `SCHEMA_VERSION = 2` and the migration note

**Files:**
- Modify: `scripts/validate.py:30`, `demo/groundwork.pin`, `MIGRATIONS.md`
- Test: `tests/test_validate.py` (`TestVersionPin` additions)

- [ ] **Step 1: Write the failing tests**

Add to `TestVersionPin`:

```python
    def test_schema_version_is_two(self):
        self.assertEqual(validate.SCHEMA_VERSION, 2)

    def test_v1_pin_hits_one_migration_boundary_error(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", "---\nschema_version: 1\n---\n")
            errs = [f for f in validate.check_version_pin(d) if f.level == "ERROR"]
            self.assertEqual(len(errs), 1, errs)
            self.assertIn("v1->v2", errs[0].message)

    def test_the_boundary_error_never_demotes(self):
        """It carries no since:, so it binds under every pin — it IS the boundary."""
        with tempfile.TemporaryDirectory() as d:
            _write(d, "groundwork.pin", "---\nschema_version: 1\n---\n")
            errs = [f for f in validate.validate(d) if f.level == "ERROR"]
            self.assertTrue(any("v1->v2" in f.message for f in errs), errs)

    def test_the_demo_pin_is_migrated(self):
        text = (REPO / "demo" / "groundwork.pin").read_text(encoding="utf-8")
        self.assertIn("schema_version: 2", text)
```

Add to `TestSinceDemotion`:

```python
    def test_migrations_documents_the_mechanism_as_wired(self):
        """MIGRATIONS.md scheduled this for 'when the first breaking bump to v2 is
        authored'. This is that bump; the deferral text must not survive it."""
        text = (REPO / "MIGRATIONS.md").read_text(encoding="utf-8")
        self.assertNotIn("Deferred: per-check", text)
        self.assertIn("Current schema version: 2", text)
        self.assertIn("v1 → v2", text)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_validate.TestVersionPin tests.test_validate.TestSinceDemotion -v`
Expected: FAIL — `SCHEMA_VERSION` is 1.

- [ ] **Step 3: Bump the engine and the demo pin together**

`scripts/validate.py:30`:

```python
SCHEMA_VERSION = 2  # bumped ONLY on a breaking schema change (#21). Never on additive commits.
```

`demo/groundwork.pin` — change `schema_version: 1` to `schema_version: 2`. Leave
`generated_by_commit` alone: it is provenance, never skew math, and rewriting it would
assert a regeneration that did not happen.

**These two edits must land in the same commit.** The engine at v2 with the demo pinned at
v1 is a skew of one, which is exactly the migration-boundary ERROR — a red gate between
commits.

- [ ] **Step 4: Rewrite `MIGRATIONS.md`'s two sections**

Replace the whole `## Deferred: per-check `since:` demotion` section with:

```markdown
## Per-check `since:` demotion

Each check declares the `SCHEMA_VERSION` it was introduced at. A finding from a check
introduced at v*N* **demotes from ERROR to WARN** for content pinned below *N*: a v1 repo
has no roster, so a v2 resolution check cannot bind content pinned before rosters existed.

This is not leniency. Such a repo is already red at the **one** migration-boundary ERROR
above, and the demoted WARNs are the precise finger-pointing that error promises — "which
files, which fields", rather than a scatter of ERRORs a reader has to triage. Content under
no pin — the engine's own tree — is never demoted.

Wired at the v1→v2 bump (`apply_since_demotion` in `scripts/validate.py`), as this document
scheduled it.
```

Replace the `## Current schema version: 1` heading with `## Current schema version: 2`,
keep the two existing paragraphs beneath it (the v1 record and the executive-view-grammar
note — that history does not change), and insert a new section immediately **before**
`### Why the executive-view grammar tightened without a bump`:

```markdown
### v1 → v2 — roles are the accountable unit

**What changed.** An owner is a role or a named holder, and a role must be **held** to
activate. Every instance now carries a roster at `governance/roles.md` naming each role, its
holder(s), and each holder's type (`human` or `agent`). A rule that carries a rung (active)
must have all four owner fields — `owner`, `value_owner`, `runtime_check_owner`,
`human_appeal_owner` — resolve against it, and `human_appeal_owner` must resolve to at least
one **human**: an appeal path that terminates in a model is not an appeal path. A draft rule
may still carry unheld or absent owners; its gaps are named WARNs. The roster also joins the
consent gate as a third governed artifact family — changing it in a governed root is an
escalating change wanting a proposal.

**What to change.**

1. Write `governance/roles.md`. Frontmatter: `valid_at` (when this mapping was last
   confirmed — a snapshot, not when a fact became true), `review_by`, and `source` (where
   the org map came from). Then one table, `| Role | Holder | Type |`, plain-text cells.
2. Make every **active** rule's four owner values resolve. Two ways, by exact string: a
   value matching a **Role** cell resolves to that row's holders; a value matching a
   **Holder** cell resolves to that holder. A person-named owner therefore resolves through
   a **holder-only row** — the Role cell left empty, which asserts a holder without
   asserting a role. A role with no row, or a row with no holder, is unheld.
3. Check that every `human_appeal_owner` reaches a holder typed `human`.
4. Set `schema_version: 2` in `groundwork.pin`.

A rule you cannot complete does not have to be forced: drop its `rung` and it is a draft
again, with its gaps named as WARNs rather than guessed at.

**Why.** A rule the machine enforces with an owner nobody claims is *enforced, but nobody
owns it* — the failure a persona-company run actually produced, where an owner field read
"the function, no person named" and the gate stayed green. Resolution against a roster is
what tells an accountable office apart from a disclaimer, and the check could not be added
without rejecting content a v1 reader accepted.

**What it does not do.** Nothing verifies a roster row against the world; a stale roster is
a confident error one level up (`docs/known-limitations.md`). Owner fields outside the
constitution — deep records, Owner's Cards, memory records — are not resolved in v2.
```

- [ ] **Step 5: Migrate the `PIN_OK` fixture and its call sites**

`tests/test_validate.py` defines `PIN_OK` **twice** — at `:2574` (used by `TestVersionPin`)
and again at `:3131`, which shadows it for everything below (`TestBlastRadiusDiff`,
`TestCompanyRoot`). Both read `schema_version: 1` today.

Change **only the first** to `schema_version: 2`, so `test_current_pin_is_exactly_silent`
keeps meaning "a current pin is silent" rather than quietly becoming a skew assertion. Then
fix its four call sites, each of which does a `.replace("schema_version: 1", ...)` that would
otherwise become a silent no-op:

- `test_skew_forward_is_exactly_one_migration_error` — replace `"schema_version: 2"` with
  `"schema_version: 0"` (skew of two is still one boundary ERROR; keep the assertion).
- `test_reverse_skew_warns_not_errors` — replace `"schema_version: 2"` with
  `"schema_version: 3"`.
- `test_non_integer_schema_version_errors` — replace `"schema_version: 2"` with
  `"schema_version: v1"`.
- `test_validate_wires_pin` — replace `"schema_version: 2"` with `"schema_version: 0"`.

**Leave `:3131`'s `PIN_OK` at v1.** Its consumers never assert pin silence: the tripwire
does not read the version, and `TestCompanyRoot` asserts a WARN's presence, not the absence
of other findings. A v1 fixture there also keeps a genuine older-pin case in the suite.
Verify by running both classes, not by reasoning about them.

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate.TestVersionPin tests.test_validate.TestSinceDemotion tests.test_validate.TestCompanyRoot tests.test_validate.TestBlastRadiusDiff -v`
Expected: PASS.

- [ ] **Step 7: Full gate**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: OK, 763 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; diff exit 0. **A `demo/groundwork.pin` ERROR means the two edits did not land
together.**

- [ ] **Step 8: Commit**

```bash
git add scripts/validate.py demo/groundwork.pin MIGRATIONS.md tests/test_validate.py && git commit -m "feat(schema): SCHEMA_VERSION 2 — the first breaking bump, with its migration note"
```

---

## Task 6: The roster as the third governed artifact family

Decision 8. Every surface built for two families gains a third.

**Files:**
- Modify: `scripts/validate.py` (`_governed_class`, `classify_governed_change`,
  `_check_proposals_instance`, `blast_radius_diff_findings`)
- Modify: `CONTEXT.md`, `AGENTS.md`, `proposals/README.md`, `demo/README.md`
- Test: `tests/test_validate.py` (`TestGovernedClassify`, `TestProposals`, new class
  `TestRosterIsGoverned`)

- [ ] **Step 1: Write the failing tests**

Add to `TestGovernedClassify`:

```python
    def test_roster_is_its_own_governed_class(self):
        self.assertEqual(validate._governed_class("governance/roles.md"), "roster")
        self.assertEqual(validate._governed_class("Governance/Roles.md"), "roster")
        self.assertIsNone(validate._governed_class("governance/sub/roles.md"))
        self.assertIsNone(validate._governed_class("governance/changelog.md"))

    def test_a_roster_change_always_escalates(self):
        for kind in ("added", "modified"):
            radius, detail = validate.classify_governed_change(kind, "roster", "a\n", "b\n")
            self.assertEqual(radius, "escalating")
            self.assertIn("roster", detail)

    def test_an_untouched_roster_is_not_a_change(self):
        self.assertEqual(validate.classify_governed_change("modified", "roster", "a\n", "a\n"),
                         (None, None))
```

Add a new class after `TestBlastRadiusDiff`:

```python
class TestRosterIsGoverned(unittest.TestCase):
    """Decision 8: the roster decides who holds every active rule's owners and
    where its human appeal terminates, so editing it is governance, not
    bookkeeping. One exemption: an ADDITION in the same diff that moves the
    root's pin v1 -> v2 is the sanctioned migration crossing."""

    def _repo(self, d, pin="1"):
        """A committed governed root with a rule and no roster."""
        _git(d, "init", "-q")
        _git(d, "config", "user.email", "t@t.t")
        _git(d, "config", "user.name", "t")
        _write(d, "groundwork.pin", "---\nschema_version: %s\n---\n" % pin)
        _write(d, "governance/constitution/access.md", RULE_OK)
        _git(d, "add", "-A")
        _git(d, "commit", "-qm", "base")

    def test_a_roster_added_without_the_pin_moving_is_escalating(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/roles.md", ROSTER_OK)
            errs = [f for f in validate.blast_radius_diff_findings(d, "HEAD")
                    if f.level == "ERROR" and "roles.md" in f.path]
            self.assertTrue(any("no pending proposal" in f.message for f in errs), errs)

    def test_the_migration_bootstrap_exempts_the_addition(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/roles.md", ROSTER_OK)
            _write(d, "groundwork.pin", "---\nschema_version: 2\n---\n")
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if "roles.md" in f.path], [])

    def test_a_modification_is_never_exempt_even_across_the_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/roles.md", ROSTER_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "roster")
            _write(d, "governance/roles.md", ROSTER_OK + "|  | Ada Byron | human |\n")
            _write(d, "groundwork.pin", "---\nschema_version: 2\n---\n")
            errs = [f for f in validate.blast_radius_diff_findings(d, "HEAD")
                    if f.level == "ERROR" and "roles.md" in f.path]
            self.assertTrue(errs, "a roster modification is escalating, boundary or not")

    def test_a_re_add_at_v2_is_gated(self):
        """The delete-then-re-add route: a root already at v2 gets no bootstrap."""
        with tempfile.TemporaryDirectory() as d:
            self._repo(d, pin="2")
            _write(d, "governance/roles.md", ROSTER_OK)
            errs = [f for f in validate.blast_radius_diff_findings(d, "HEAD")
                    if f.level == "ERROR" and "roles.md" in f.path]
            self.assertTrue(errs)

    def test_a_matching_proposal_clears_a_roster_change(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/roles.md", ROSTER_OK)
            _write(d, "proposals/p1.md", _proposal("governance/roles.md"))
            self.assertEqual([f for f in validate.blast_radius_diff_findings(d, "HEAD")
                              if f.level == "ERROR" and "roles.md" in f.path], [])

    def test_the_roster_gate_carries_since_two(self):
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/roles.md", ROSTER_OK)
            gov = [f for f in validate.blast_radius_diff_findings(d, "HEAD")
                   if "roles.md" in f.path]
            self.assertTrue(gov)
            self.assertTrue(all(f.since == 2 for f in gov))

    def test_a_deleted_roster_stays_a_warn(self):
        """Deletions keep the documented WARN-only limitation all three governed
        families share. Gating them was weighed and declined as a larger redesign."""
        with tempfile.TemporaryDirectory() as d:
            self._repo(d)
            _write(d, "governance/roles.md", ROSTER_OK)
            _git(d, "add", "-A")
            _git(d, "commit", "-qm", "roster")
            os.remove(os.path.join(d, "governance", "roles.md"))
            findings = [f for f in validate.blast_radius_diff_findings(d, "HEAD")
                        if "roles.md" in f.path]
            self.assertTrue(findings)
            self.assertTrue(all(f.level == "WARN" for f in findings), findings)
```

**Before writing these, read the existing `TestBlastRadiusDiff` helpers** — `_git`,
`_proposal`, and how it builds a committed repo — and use them rather than the sketch above
if their signatures differ. Verified at planning time: `_git(d, *args)` at
`tests/test_validate.py:1597` (it does not set identity, so each fixture runs
`_git(d, "config", "user.email", ...)` and `"user.name"` itself), and
`_proposal(target, radius="escalating")` at `:3137` — the second parameter is named
`radius`, so pass it positionally.

Add to `TestProposals`:

```python
    def test_roster_is_a_valid_proposal_target(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/roles.md", ROSTER_OK)
            _write(d, "proposals/p1.md", _proposal("governance/roles.md"))
            self.assertFalse(any(f.level == "ERROR" and "must be a skill" in f.message
                                 for f in validate.check_proposals(d)))

    def test_a_roster_proposal_can_never_be_track1_body(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "governance/roles.md", ROSTER_OK)
            _write(d, "proposals/p1.md", _proposal("governance/roles.md", "track1-body"))
            self.assertTrue(any(f.level == "ERROR" and "roster" in f.message
                                for f in validate.check_proposals(d)))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_validate.TestGovernedClassify tests.test_validate.TestRosterIsGoverned tests.test_validate.TestProposals -v`
Expected: FAIL — `_governed_class` returns None for the roster.

- [ ] **Step 3: Classify the roster**

In `_governed_class`, after the `"rule"` branch and before the `skills/` branch:

```python
    if len(parts) == 2 and low[0] == "governance" and low[1] == "roles.md":
        return "roster"
```

Extend the docstring's first sentence to name the fourth value: `'roster'` (the instance's
`governance/roles.md`).

In `classify_governed_change`, immediately after the `cls == "rule"` branch:

```python
    if cls == "roster":
        return "escalating", ("the roles roster — it decides who holds every active rule's "
                              "owners and where its human appeal terminates (#17)")
```

- [ ] **Step 4: Accept the roster as a proposal target**

In `_check_proposals_instance`, replace the target-classification block. `target_is_skill`
and `target_is_rule` are initialized to `False` above; add `target_is_roster = False` beside
them, then:

```python
            t = os.path.normpath(target.strip().replace("\\", "/")).replace("\\", "/")
            target_is_skill = t.startswith("skills/")
            target_is_rule = t.startswith("governance/constitution/")
            target_is_roster = t == "governance/roles.md"
            if not (target_is_skill or target_is_rule or target_is_roster):
                findings.append(Finding("ERROR", rel, None,
                                        "proposal 'target' must be a skill (skills/), a constitution "
                                        "rule (governance/constitution/), or the roles roster "
                                        "(governance/roles.md); other artifacts keep their own "
                                        "governance (#17)"))
            elif not os.path.isfile(os.path.join(inst, t)):
                findings.append(Finding("ERROR", rel, None, "proposal 'target' not found: %s" % t))
            else:
                resolved = os.path.relpath(
                    os.path.realpath(os.path.join(inst, t)),
                    os.path.realpath(inst)).replace("\\", "/")
                bucket = ("skills/" if target_is_skill
                          else "governance/constitution/" if target_is_rule
                          else "governance/roles.md")
                if not resolved.startswith(bucket):
                    findings.append(Finding("ERROR", rel, None,
                                            "proposal 'target' resolves outside %s (symlink or filesystem "
                                            "alias: %s) — fail closed (#17)" % (bucket, resolved)))
                    target_is_rule = target_is_rule or resolved.startswith("governance/constitution/")
```

And in the `blast_radius` block, after the existing `br == "track1-body" and target_is_rule`
branch, add:

```python
        elif br == "track1-body" and target_is_roster:
            findings.append(Finding("ERROR", rel, None,
                                    "the roles roster can never be 'track1-body' — who holds an "
                                    "owner is governance, and it never auto-applies (#17)", 2))
```

- [ ] **Step 5: The migration-scoped bootstrap**

Add beside `_pin_dirs` in `scripts/validate.py`:

```python
def _pin_version_text(text):
    """The integer schema_version in a pin file's text, or None. Parsing only —
    check_version_pin owns the findings."""
    data, _f = parse_frontmatter(text or "", "<pin>")
    sv = (data or {}).get("schema_version")
    if not isinstance(sv, str):
        return None
    try:
        return int(sv.strip())
    except ValueError:
        return None
```

In `blast_radius_diff_findings`, immediately after `gov_roots = _pin_dirs(...)` and its
dormancy return, add:

```python
    def _bootstrap_roots():
        """Decision 8's migration-scoped bootstrap: governed roots whose pin moves
        v1 -> v2 in THIS diff. A roster ADDITION there is not escalating, because
        every v1->v2 migration necessarily adds its roster — the exemption is
        exactly the migration boundary, the sanctioned crossing mechanism.

        Narrow on purpose. Only v1 -> v2 (the only bump for which 'necessarily
        adds its roster' is true), only when a base pin exists, and only for
        additions — the caller enforces that last one. A root already at v2 gets
        nothing, which is what closes the delete-then-re-add route."""
        out = set()
        for g in gov_roots:
            pin_rel = (g + "/" if g else "") + "groundwork.pin"
            bf = base_rels.get(pin_rel)
            if bf is None:
                continue
            if _pin_version_text(_git_show(toplevel, base, bf)) != 1:
                continue
            abspath = os.path.join(root, *pin_rel.split("/"))
            if not os.path.isfile(abspath):
                continue
            new, _rd = _read_utf8(abspath, pin_rel)
            if _pin_version_text(new) == 2:
                out.add(g)
        return out

    bootstrap = _bootstrap_roots()
```

Then in the `for g, cls in pairs:` loop, replace:

```python
            radius, detail = classify_governed_change(kind, cls, old, new)
            if radius is None:
                continue
```

with:

```python
            if cls == "roster" and kind == "added" and g in bootstrap:
                continue  # decision 8's migration-scoped bootstrap
            radius, detail = classify_governed_change(kind, cls, old, new)
            if radius is None:
                continue
            # The roster is a v2 artifact: behind a v1 pin these demote to the
            # finger-pointing WARN, in front of the one boundary ERROR.
            since = 2 if cls == "roster" else None
```

and add `since` as the fifth argument to the three `Finding(...)` constructions in the rest
of that loop body (the two escalating ERRORs and the track-1 changelog WARN).

- [ ] **Step 6: Update the four prose sites**

Enumerate before editing — `grep -rn "skills and rules\|skill or a rule\|skill or a
constitution rule\|skill/rule\|two artifact kinds\|skill and rule" --include="*.md" . | grep
-v "^./docs/superpowers"` — and account for every hit. At planning time that is exactly
`CONTEXT.md:57,61`, `AGENTS.md:47`, `demo/README.md:36`, and `proposals/README.md:3,9,45,47,57`.
**Re-run the grep; do not trust this list.**

`CONTEXT.md` — "Improvement proposal":

> An agent-authored proposed change to a skill, a constitution rule, or the roles roster —
> the three artifact kinds the three buckets route. Memory records, Owner's Cards, and
> ontology worksheets keep their own governance; a memory enters this routing only at the
> moment it graduates into a proposed rule/skill change.

`CONTEXT.md` — "Blast-radius boundary", final sentence:

> Anything touching the description, governance frontmatter, or Owner's Card, any change to
> a track-2 skill or a rule, and any change to the roles roster, escalates.

`AGENTS.md:47` — "changes to its skills and rules run the #18 consent gate" becomes "changes
to its skills, rules, and roster run the #18 consent gate".

`demo/README.md:36` — the same substitution, in that sentence's own wording.

`proposals/README.md` — line 3 ("a skill or a constitution rule" → "a skill, a constitution
rule, or the roles roster"), line 17's comment (add `# or governance/roles.md`), line 40 (add
the roster to the escalating list), line 45 ("Proposals route **skills, rules, and the
roster.**"), and line 57 ("every changed skill, rule, and roster"). Add one sentence after
line 45's paragraph:

> The roster joined at schema v2: it decides who holds every active rule's owners and where
> its human appeal terminates, so editing it is governance. The one exemption is the
> migration itself — a roster **added** in the same diff that moves the root's pin from v1
> to v2 is the sanctioned crossing, because every v1→v2 migration adds one.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python3 -m unittest tests.test_validate.TestGovernedClassify tests.test_validate.TestRosterIsGoverned tests.test_validate.TestProposals tests.test_validate.TestBlastRadiusDiff -v`
Expected: PASS.

- [ ] **Step 8: Full gate — the bootstrap proves itself here**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: OK, 774 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; **diff exit 0**.

That last one is this task's real acceptance test: this branch adds `demo/governance/roles.md`
and moves `demo/groundwork.pin` from v1 to v2 in the same diff, which is decision 8's
bootstrap exercised end to end against `main`. **If it ERRORs on
`demo/governance/roles.md`, the bootstrap is not matching** — check that the base pin reads
1 (`git show main:demo/groundwork.pin`) and the working tree reads 2.

- [ ] **Step 9: Commit**

```bash
git add scripts/validate.py tests/test_validate.py CONTEXT.md AGENTS.md proposals/README.md demo/README.md && git commit -m "feat(governance): the roster is the third governed artifact family (#17)"
```

---

## Task 7: The documentation the design names

**Files:**
- Modify: `docs/known-limitations.md`, `docs/rule-map.md`, `governance/README.md`,
  `demo/governance/README.md`, `demo/canon.md`, `AGENTS.md`
- Test: `tests/test_validate.py` (`TestRoster` addition)

- [ ] **Step 1: Write the failing test**

Add to `TestRoster`:

```python
    def test_the_named_holes_are_documented(self):
        """The design names four things R1 must record rather than solve. A
        limitation nobody wrote down is a claim by omission."""
        text = (REPO / "docs" / "known-limitations.md").read_text(encoding="utf-8")
        for phrase in ("intent-blind", "stale roster",
                       "outside the constitution", "deleted roster"):
            self.assertIn(phrase, text.lower(), phrase)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m unittest tests.test_validate.TestRoster.test_the_named_holes_are_documented -v`
Expected: FAIL.

- [ ] **Step 3: Add the four limitations**

Append to `docs/known-limitations.md`, as a new section placed immediately after
`## Governance — the consent gate and its tripwire`:

```markdown
## Governance — the roles roster (schema v2)

- **A roster does not make "held" true.** It records what the repository says, dated — not
  the world. A person can leave, a role can move, and the file will keep resolving until
  someone edits it. A **stale roster** produces exactly the confident-error class the
  evidence floor documents, one level up: the gate goes green on an accountability structure
  nobody has confirmed. `valid_at` and `review_by` date the claim; nothing verifies it.
- **Resolution is intent-blind.** Nothing marks an owner value as meant-as-a-role or
  meant-as-a-person: a value is whatever it matches. So a role title whose roster row was
  *forgotten*, and which happens to equal an existing Holder string, silently resolves as
  that holder instead of surfacing as unheld — the integrity check catches a Role/Holder
  collision inside the file, but it cannot see a row that is absent. The structural fix is
  typed owner references in the rule itself (`role:` / `person:`), which discriminates at the
  source and changes the rule frontmatter schema for every adopter; it was weighed at R1 plan
  review and declined, because the failure needs a role title spelled identically to a holder
  name *and* a forgotten row, both the repo author's own text. Recorded here as the known
  alternative if it ever bites.
- **Owner fields outside the constitution are not resolved.** Deep records
  (`accountable_owner`, `gate_owner`), Owner's Cards, and memory records still carry owner
  strings that resolve against nothing. v2 resolves constitution-rule owners only —
  an ontology owner is descriptive where a rule owner is enforcement — and the remainder is a
  named remaining hole, open until a later slice decides it.
- **A deleted roster is a WARN, not an ERROR**, exactly as a deleted rule or skill is, and
  for the same reason: a proposal's `target` must be an existing file, so a deletion can
  never trace to one. Deletion is an attacker's cheapest move against a roster and it stays
  loud-after-the-fact rather than gated; gating deletions across all three governed families
  was weighed and declined as a larger redesign than this slice should carry. It is not
  silent — a root with active rules and no roster is red at the missing-roster ERROR, and
  re-adding one to a root already at v2 needs a proposal.
```

- [ ] **Step 4: Update the two changed rule-map rows**

`check_constitution`:

```markdown
| Typed rules, the no-rung-six safety invariant, held-to-activate resolution, orphan-prohibition, sunset (8, R1) | check_constitution | ERROR on the safety spine, on an active rule whose owner does not resolve, and on an appeal path that reaches no human; WARN on a draft's named gaps and missing provenance |
```

`blast_radius_diff_findings`:

```markdown
| The blast-radius tripwire: declared against actual across three governed families, plus the append-only changelog (18 and 17) | blast_radius_diff_findings | ERROR on a missing or mismatched proposal and on a changelog rewrite or deletion, WARN on a governed deletion or a missing changelog line |
```

- [ ] **Step 5: Document the roster's grammar where the other grammars live**

`governance/README.md` cites the rule objects; `interview/generate.md` sends a generator
there. Add a section after `## A rule is four owned objects, on a rung, with a sunset`:

```markdown
## The roster: who holds what

An owner is a **role** or a **named holder**, and `governance/roles.md` is where that
resolves. One roster per instance.

```
---
valid_at: <ISO date — when this mapping was last confirmed>
review_by: <ISO date — when to re-confirm it>
source: <where this org map came from: an interview layer, an HR system, the founder's word>
---
| Role | Holder | Type |
|---|---|---|
| Head of IT | Priya Vale | human |
|  | Ruth Okafor | human |
```

- **Two-way resolution, by exact string.** A value matching a **Role** cell resolves to that
  row's holders; a value matching a **Holder** cell resolves to that holder. The second form
  is what keeps `owner: Ruth Okafor` valid.
- **A holder-only row** (Role cell empty) names a holder without asserting a role.
- **A role with no row, or a row with no holder, is unheld** — and a rule with a rung cannot
  have an unheld owner. Drop the rung and it is a draft again, gaps named as WARNs.
- **Type is `human` or `agent`.** The `human_appeal_owner` must reach at least one `human`:
  an appeal path that terminates in a model is not an appeal path.
- **No string may be both a Role and a Holder** — every reference to it would be ambiguous.
- `valid_at` is a **snapshot**, deliberately narrower than org-memory's
  when-the-fact-became-true `valid_at`.

Changing the roster in a governed root is an escalating change (#17): it decides who holds
every active rule's owners.
```

Verify the fenced block renders — `_strip_code` and `check_links` both read this file, and
the inner table must sit inside the fence.

- [ ] **Step 6: Narrate the demo's roster**

`demo/governance/README.md` — add one line to whatever inventory it carries, naming
`roles.md` as who holds the owners its three rules name. `AGENTS.md`'s demo bullet
(`AGENTS.md:44-53`) enumerates the demo's contents; add the roster there, in that list's
own voice. Check `demo/canon.md` too — at planning time it carried no such inventory, so it
needs nothing; confirm that rather than assuming it. **Read each file first and match its wording**; do not paste a
sentence written for another file. Keep `AGENTS.md` under 200 lines
(`wc -l AGENTS.md`).

- [ ] **Step 7: Full gate**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
wc -l AGENTS.md
```
Expected: OK, 775 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; diff exit 0; AGENTS.md under 200.

**`TestDemoIsLiftable` is a tripwire here**: a link in a demo file that climbs out of `demo/`
fails it. The demo roster and the demo README edits must link only inside `demo/`.

- [ ] **Step 8: Commit**

```bash
git add docs/known-limitations.md docs/rule-map.md governance/README.md demo/governance/README.md demo/canon.md AGENTS.md tests/test_validate.py && git commit -m "docs: the roster's grammar, and the four holes R1 records rather than solves"
```

---

## Task 8: `interview/generate.md` — the minimal R1-window edits

Without these the documented generation workflow is broken for exactly the window between R1
and R2: `generate.md` instructs `schema_version: 1`, which the R1 engine ERRORs at the
migration boundary, and writing `2` with no roster fails the missing-roster check on any
active rule.

**Scope discipline.** These are the *minimal* edits the landing order assigns to R1. The
`provisioned: no` reconciliation, the wider report wording, the prose rewrite, and the full
roster elicitation are **R2** — do not write them here.

**Files:**
- Modify: `interview/generate.md`
- Test: `tests/test_validate.py` (`TestGeneratedCompanyRepo` addition)

- [ ] **Step 1: Write the failing test**

Add to `TestGeneratedCompanyRepo`:

```python
    def test_the_manifest_specifies_the_roster_and_the_v2_pin(self):
        """generate.md is the manifest a generator follows. If it still says
        schema_version: 1, or never mentions the roster, a run against the R1
        engine produces a repo that fails the gate on its first command."""
        text = (REPO / "interview" / "generate.md").read_text(encoding="utf-8")
        self.assertIn("schema_version: 2", text)
        self.assertNotIn("schema_version: 1", text)
        self.assertIn("governance/roles.md", text)
```

The repo-shape assertions the class already makes cover the rest: `_materialize` copies
`demo/`, which now carries both the roster and the v2 pin, so the generated-repo fixture
proves a v2 company repo passes as its own root.

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 -m unittest tests.test_validate.TestGeneratedCompanyRepo.test_the_manifest_specifies_the_roster_and_the_v2_pin -v`
Expected: FAIL.

- [ ] **Step 3: The pin**

In `generate.md`'s numbered item 1, change `schema_version: 1` to `schema_version: 2`. Change
nothing else in that paragraph — the write-order and base reasoning is the previous slice's
approved text.

- [ ] **Step 4: Add the roster to the repo shape**

In the `## What you write` tree, add under `governance/`, immediately after the
`constitution/<rule>.md` line:

```
    roles.md                      who holds each owner the rules name, typed
```

In the paragraph naming where each grammar lives, extend the governance citation: "the rule
objects **and the roster** in [../governance/README.md](../governance/README.md)".

- [ ] **Step 5: Write the roster generation step**

Insert into numbered item 5 (`governance/constitution/`), after the paragraph ending "…before
the repeal ships." and before the `Then changelog.md` paragraph:

```markdown
**Then `roles.md` — and invent nothing in it.** The roster is what makes an owner resolve, so
a rule cannot carry a rung until its four owner values do. Write it from the confirmed
answers you already have, by this rule and no wider:

- **Enter a holder, typed `human`, only where the binding protocol guarantees a person:** the
  acted-on activity's owner and the skill's owner — the answers under the row
  [questions.md](questions.md) marks "A role is not an owner", and the person guarantee in
  [protocol.md](protocol.md). Write each as a **holder-only row**: the Role cell empty. Those
  questions yield a person's name, not a role, and a Role row would assert a role the record
  never confirmed.
- **The backup owner is not among them.** Its `(human-only)` marker denotes where the answer
  came from, not the holder's humanity, and nothing forbids a role-shaped backup.
- **Every other owner value is not entered at all.** A constitution rule's owners may be
  roles, and a run has recorded one that disclaims an owner outright ("the function, no
  person named"). Writing such a value as a Role row would assert a role the record never
  confirmed — a disclaimer least of all. Left out, the roster asserts nothing about it and it
  simply fails to resolve, which is the true answer.
- **`valid_at` is the earliest `confirmed_at` among the interview layers these entries
  transcribe.** A conservative aggregate: layers freeze independently and a newer one
  reconfirms nothing about older entries, so the earliest date masks no entry's staleness.
  Never the generation date, which may fall later and confirms nothing.
- **Precondition.** Every source layer's `confirmed_at` must parse as a real, non-future ISO
  date. A malformed or future one **stops roster generation**, naming the offending layer.
  The legal recovery is a **new confirming turn**, never an edit — frozen layers are
  immutable, so the operator runs a correction layer re-confirming the affected entries with
  a parseable date, and the aggregate reads each entry's most recent confirming layer. Never
  invent a date.
- **`review_by` is an interim policy default**: 90 days after `valid_at`, because no question
  elicits a review cadence yet. Record it in the file as default-not-answered, so a reader
  can tell a policy default from an answer.
- **`source`** names where the org map came from — the interview layers, by name.

Role rows and agent-typed holders arrive when the interview elicits them directly. A repo
generated before then keeps its holder-only roster: that is valid content, and enriching it
is the company's own edit.
```

- [ ] **Step 6: Write the declared-draft permission with its paired obligation**

Insert immediately after the block above:

```markdown
**A rule with a gap ships as a declared draft, or not at all.** A constitution rule carrying
a gap in any of three classes — a required field that is **missing**, a field populated but
**unresolvable** against the roster, or a field populated but recorded as **disputed** — may
ship only as a **draft** (no rung) that declares those gaps in its own body. An undeclared
incomplete rule does not ship.

**One exception, and it outranks this permission:** a rule carrying a gate ERROR that fires
regardless of rung does not ship at all, declared or not. That is a `high-risk` rule whose
appeal path is missing, unresolvable, or resolves to no human holder, and a repealing rule
whose surviving job is not reassigned. Where a recorded action-class dispute includes
`high-risk` among the accounts, this exception applies as if the rule were high-risk, even
when the scalar field carries the lower class — otherwise a dispute the validator cannot read
would ship a rule the spine would reject.

**And the obligation that pays for the permission:** the generation report must name every
constitution rule that shipped incomplete, and why. The permission without the obligation
would make declaring cheaper than completing.
```

- [ ] **Step 7: Full gate**

```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
python3 scripts/validate.py . ; echo "exit: $?"
python3 scripts/validate.py demo 2>&1 | tail -2
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
Expected: OK, 776 tests, skipped=1; `0 error(s), 7 warning(s)` exit 0; `0 error(s),
2 warning(s)`; diff exit 0.

Every relative link added must resolve — `check_links` ERRORs otherwise. `questions.md` and
`protocol.md` are siblings of `generate.md`; `../governance/README.md` is the engine path
already cited there.

- [ ] **Step 8: Commit**

```bash
git add interview/generate.md tests/test_validate.py && git commit -m "docs(interview): generation writes a v2 pin and a roster, inventing neither"
```

---

## Task 9: The review record, and the terminal gate

**Files:**
- Create: `docs/superpowers/plans/r1-roster-schema-v2-reviews/README.md`

- [ ] **Step 1: Confirm the directory name is free in the merge target**

```bash
git ls-tree main -- docs/superpowers/plans/r1-roster-schema-v2-reviews docs/superpowers/plans/r1-roster-schema-v2-reviews.md
```
Expected: empty output. If either exists, append `-2` and record why in the README.

- [ ] **Step 2: Write the README**

```markdown
# Codex review record — branch `feat/roster-schema-v2`

Rule 9's durable record. This branch adds exactly one plan
(`docs/superpowers/plans/2026-08-29-r1-roster-schema-v2.md`), so the directory takes the
plan-adjacent form. Each `round-NN.md` beside this file is fixed once committed; this file
carries the parts that keep changing.

**Branch:** `feat/roster-schema-v2`.

## Rounds

| Round | Reviewed | Verdict | Findings | Fix commit |
|---|---|---|---|---|

## Open findings

None recorded yet.

## Rejected findings

None recorded yet.

## Maintainer items

1. **Two decisions taken at plan review, 2026-08-29**, both reserved by the design and both
   answered before any code was written: the engine-root roster's holders (`Head of IT` and
   `CISO` are held by Sean Winslow, typed `human`), and intent-blind resolution (accepted as
   a documented blind spot rather than moving to typed owner references).
2. **`CONTEXT.md` is edited by this branch.** Locked decision 8 makes `CONTEXT.md:57`'s "the
   only two artifact kinds" false, so the glossary entry is amended to three. Flagged here
   because the previous slice rejected a `CONTEXT.md` edit for scope, and this one is a
   different kind: transcribing a locked decision into the glossary that records locked
   decisions.
3. **Carried, none blocking this slice** — the four items the previous session left the
   maintainer: what counts as adequate grounds for rejecting a finding
   (`docs/superpowers/reviews/review-record-rule/round-11.md`); whether `CONTEXT.md:105`'s
   consent invariant should carry the bootstrap qualification; whether a later `--diff` base
   must be proven to contain the generated root; and ratification of the rule-1 departure
   recorded in both merged logs.
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-08-29-r1-roster-schema-v2.md docs/superpowers/plans/r1-roster-schema-v2-reviews/README.md && git commit -m "docs(plan): R1 — the roster and the v1->v2 bump, with its review record"
```

(The plan file itself is committed here if it was not committed at planning time.)

- [ ] **Step 4: The terminal gate, all four commands**

```bash
python3 scripts/validate.py . ; echo "exit: $?"
```
```bash
python3 scripts/validate.py demo ; echo "exit: $?"
```
```bash
python3 scripts/validate.py . --diff main ; echo "exit: $?"
```
```bash
python3 -m unittest discover -s tests -q 2>&1 | tail -3
```
Expected: `0 error(s), 7 warning(s)` exit 0; `0 error(s), 2 warning(s)` exit 0; diff exit 0;
OK with 776 tests and skipped=1.

- [ ] **Step 5: Codex review, round 1**

Launch via the `codex:codex-rescue` agent with `--background`, from the worktree, and poll
the job's JSON directly — the companion runtime keys job state by the **launch** cwd
(`~/.claude/plugins/data/codex-inline/state/<dir-hash>/jobs/`), so a job launched from the
worktree is invisible to status polls from the main repo. Run every watcher `Bash` call with
`run_in_background`: a foreground wrapper is killed at the harness timeout while the job
still reports "running".

Tell the reviewer explicitly:

- A clean round is a real outcome. **Do not manufacture findings.**
- Do not re-raise anything this README already discloses as open.
- Its sandbox usually cannot create a temp directory, so its `unittest` run will report
  hundreds of `TemporaryDirectory` errors. **That is environmental, not a regression** — the
  suite is verified by the builder, and the round entry says so.

Review threads are **not** resumable. After committing fixes, launch a **fresh** review.

- [ ] **Step 6: Write `round-01.md` and iterate**

Every Codex invocation gets an entry, a crashed one included. Each entry carries the reviewed
revision as a **commit SHA**, the verdict, and every finding with the reviewer's own severity
word verbatim plus its disposition — fixed, rejected with grounds, or open. An entry is
immutable once committed; corrections go in a later entry. The README's table carries the
fix commit, since an entry cannot name the commit that fixes it.

Before committing any fix: enumerate every site that could carry the claim and diff them
against each other; verify quoted text, numbers, and line references against the source file
rather than against the review's citation; and if a fix touches a maintainer decision, stop
and ask.

---

## Self-review

**Spec coverage.** Every item in the design's R1 paragraph maps to a task: roster schema
(2, 7), the five validator checks all carrying `since: 2` (1–4, 6), rosters for the engine
root **and** `demo/` (3), the demo pin migrated (5), the first `SCHEMA_VERSION` bump with the
`since:` mechanism wired (1, 5), tests (every task), `docs/rule-map.md` (2, 7),
`docs/known-limitations.md` (7), `MIGRATIONS.md` (5), the roster as a third governed family
with the migration-scoped bootstrap (6), and the minimal `generate.md` edits (8). The
intent-blind blind spot and the engine-root holders — the two the design flagged for the
maintainer — are answered above and used in Tasks 3 and 7.

**Deliberately not here**, and each with its reason: the prose rewrite of the person-versus-role
sites (`questions.md:93`, `protocol.md:247`, `interview/README.md:149`) and the full roster
elicitation are **R2** by the landing order. No new question enters `questions.md`, so
`TestQuestionSkeletonCoverage` needs no change — R1 derives the roster from answers the
interview already collects, and the coverage test builds its required set from validator
constants, none of which R1 adds.

**Type consistency.** `Roster(roles, holders)` is built by `_parse_roster`, returned by
`_load_roster`, and read by `_resolve_owner` and `_check_constitution_instance`;
`_RULE_OWNER_FIELDS` is the one list of the four owner fields, used by both the activation
loop and the draft-visibility loop; `since=2` is the single tag on every new check.
`_pin_versions` returns `{dir -> int}` and `apply_since_demotion` consumes exactly that;
`_pin_version_text` (text → int) is a separate, differently-named helper for the diff path,
which reads blobs rather than the walked tree.
