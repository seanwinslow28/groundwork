# groundwork V1 — Slice 2.3b: the demo canon + the #16 synthetic-identifier check — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `demo/` and make it verifiable before it holds anything. Ship the **demo canon** (#16) — one file that is simultaneously the human description of the fictional world and the validator's positive allowlist — plus `check_synthetic_identifiers`, the `demo/`-scoped ERROR that every email, domain, phone, and IP in demo content resolves to the canon or an RFC-reserved fiction namespace. Also close the one open boundary decision Slice 2.3a left, because this is the slice that makes it observable.

**Architecture:** `demo/canon.md` carries the machine-readable allowlist in #11 frontmatter (`domains`, `external_domains`, `phone_range`) and the fictional world in prose (company, product, people). `check_synthetic_identifiers(root, ignore=())` walks everything under a `demo` directory, extracts structured identifiers with high-signal patterns, and ERRORs on any that does not trace to the canon or a reserved-for-fiction namespace. Missing or unreadable canon with demo content present is itself an ERROR — unverifiable demo content fails closed. No content beyond the canon and a README lands here; ontologies, skills, governance, and the script follow in 2.3c–2.3e.

**Tech Stack:** Python 3.9+ standard library only (no new imports); stdlib `unittest`; Markdown.

## Global Constraints

- **`scripts/validate.py` imports stdlib only.** No new imports. Keep `TestZeroDep` green.
- **Findings:** `ERROR` fails the gate (exit 1); `WARN` prints, does not fail.
- **Scope matrix from #16 is exact and must not drift:** the synthetic-identifier check is **`demo/` only** and **ERROR**; it must **never** apply to `your-company/`, whose real identifiers are legitimate by design. The secret scan stays global and is untouched by this slice.
- **The check is high-signal, not exhaustive** — the same posture as the secrets floor. It verifies the *structured* surface only; the prose layer is the documented ceiling.
- **The engine repo's output moves by exactly one line.** Before this slice: `0 error(s), 7 warning(s)`. After: still `0 error(s)`, and the WARN count must not change — `demo/` introduces no warnings.
- **Codebase conventions:** reuse `Finding`, `_read_utf8`, `_load_frontmatter`, `_blank`, `_ignored`, `iter_files`, `_memory_record_files`, `_live_record_realpaths`.
- **Per-session gate:** `python3 -m unittest discover -s tests` green AND `python3 scripts/validate.py .` exit 0 AND `python3 scripts/validate.py . --diff main` exit 0 → Codex review → maintainer merges.
- **Commit trailer:** `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`

## Prerequisite

Slice 2.3a merged and pushed (`1cd13f1`; 572 tests, 1 designed skip, gate exit 0, 7 WARNs). Branch:

```bash
git checkout main && git pull && git checkout -b build/slice-2.3b-demo-canon
```

---

## Design calls flagged for the maintainer

**1. Close the outer-subsumes-inner memory asymmetry — now, not later.**
Slice 2.3a left this open and Fable's own note said "ideally before 2.3b makes it observable." This is that slice, so here is the call.

*The asymmetry:* a **root** skill can cite `baseline: demo/memory/x.md` and pass, because `_memory_record_files(root)` walks every `memory/` directory beneath root — including nested instances'. The reverse is blocked: a demo skill citing a root record fails. So containment holds inward and leaks outward.

*Recommendation: close it, symmetrically.* Fable recommended leaving it on the grounds that nothing exercises it yet — but that is precisely the argument that expires this week. Once `demo/` holds memory records (2.3c), an engine exemplar could quietly take its baseline from demo content, and the walking skeleton's provisioning gate would be satisfied by a fictional company's numbers. The rule that makes it coherent is one sentence: **a memory record belongs to exactly one instance — the parent of the last `memory` component in its path — and only that instance may cite it.**

*Why it is cheap:* 2.3a already computes exactly that ("the parent of the LAST 'memory' component"), inline in `check_memory`, after two Codex rounds got it right. Task 1 extracts it into `_memory_instance_base` and reuses it for the baseline allowlist. One rule, one home, two consumers — instead of the same rule living in one place and being contradicted by a walk in another.

*Honest counter-argument:* it forecloses a shared memory pool across instances. But #10's model is one company, one repo, one memory; there is no sanctioned cross-instance sharing, and if it is ever wanted it should be an explicit declaration rather than a side effect of how a walker recurses.

**2. `external_domains` exists, and ships empty.**
#16's canon declares the fictional world's domains. But demo documentation may one day need to link to something real — the groundwork repo itself, a vendor's docs. Without a declared escape hatch, the first such link creates pressure to loosen the check, which is how a positive allowlist dies. So the canon carries an `external_domains` list that is **empty in this slice**: the demo starts with zero real domains, and any future addition is a visible, deliberate, reviewable edit to the one file that documents the world. A declaration, not a bypass.

**3. The demo company is `Umbercress`, and the person names are the documented ceiling.**
Web-searched before adoption: no presence as a company, product, or term (the discarded candidates `Quillstone` and `Larkfield` are both real). Domain `umbercress.example` is doubly safe — an RFC 6761 reserved TLD *and* canon-declared. Phones use `555-01xx`; IPs use TEST-NET. **Person names cannot be made safe this way** — a real name looks exactly like a fictional one, which is #16's stated ceiling. The canon says so in its own text, so a reader meets the limit where the names are, not only in `docs/known-limitations.md`.

**4. Running the validator with a demo directory *as* the root skips this check.**
Scope is "any path under a directory named `demo`", so `python3 scripts/validate.py demo/` finds no `demo` component and the check is silent. This mirrors an already-accepted limitation (`validate.py <memory-dir>` skips record discovery, Slice 1.4). The repo gate runs from the repo root, which is the supported setting. Documented rather than solved.

---

## File Structure

- `scripts/validate.py` — **modify.** Extract `_memory_instance_base`; scope the baseline allowlist to the skill's own instance; add `RESERVED_TLDS`, `RESERVED_DOMAINS`, `TESTNET_PREFIXES`, `PUBLIC_TLDS`, the identifier patterns, and `check_synthetic_identifiers(root, ignore=())`; wire it into `validate()`.
- `tests/test_validate.py` — **modify.** `TestMemoryInstanceOwnership` and `TestSyntheticIdentifiers`.
- `demo/canon.md` — **create.** The world + the allowlist.
- `demo/README.md` — **create.** What the demo is, and honestly what it is not yet.
- `docs/known-limitations.md` — **modify.** #16's synthetic-ceiling paragraph.
- `AGENTS.md` — **modify.** Status list: `demo/` exists and what is in it.

---

## Task 1: One memory record, one instance

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
class TestMemoryInstanceOwnership(unittest.TestCase):
    def test_root_skill_cannot_borrow_a_nested_instance_baseline(self):
        # The asymmetry Slice 2.3a left open: containment held inward and
        # leaked outward, so an engine exemplar could take its baseline from
        # the demo company's numbers.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ontologies/people-hr/_executive-view.md", EXEC_OK)
            _write(d, "ontologies/people-hr/onboarding-orchestration.md", AUTOMATE_OK)
            _write(d, "skills/onboarding-orchestration/SKILL.md",
                   SKILL_BASELINED.replace("baseline: memory/onboarding-baseline.md",
                                           "baseline: demo/memory/onboarding-baseline.md"))
            _write(d, "skills/onboarding-orchestration/owner-card.md", CARD_OK)
            _write(d, "demo/memory/onboarding-baseline.md", MEM_OK)
            self.assertTrue(any(f.level == "ERROR" and "baseline" in f.message.lower()
                                for f in validate.check_owner_cards(d)))

    def test_own_instance_baseline_still_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d)
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_nested_instance_baseline_still_resolves(self):
        with tempfile.TemporaryDirectory() as d:
            _write_instance(d, "demo/")
            self.assertEqual([f for f in validate.check_owner_cards(d)
                              if f.level == "ERROR"], [])

    def test_memory_instance_base_picks_the_last_memory_component(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "memory", "company", "memory", "x.md")
            self.assertEqual(
                os.path.realpath(validate._memory_instance_base(d, p)),
                os.path.realpath(os.path.join(d, "memory", "company")))

    def test_memory_instance_base_at_root(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "memory", "x.md")
            self.assertEqual(os.path.realpath(validate._memory_instance_base(d, p)),
                             os.path.realpath(d))
```

- [ ] **Step 2: Run to verify failure**

Run: `cd "$(git rev-parse --show-toplevel)" && python3 -m unittest tests.test_validate.TestMemoryInstanceOwnership -v`
Expected: FAIL — no attribute `_memory_instance_base`, and the borrow test passes today (which is the bug).

- [ ] **Step 3: Extract the rule.** Add next to `_memory_record_files` in `scripts/validate.py`:

```python
def _memory_instance_base(base, abspath):
    """The instance a memory record belongs to: the parent of the LAST 'memory'
    component in its path. A record under demo/memory/ belongs to demo/; one
    under memory/company/memory/ belongs to memory/company/ — taking the FIRST
    component would select the outer root and reopen cross-instance resolution
    (Codex r2 of Slice 2.3a). `base` is the directory `abspath` is relative to.

    One rule, one home: check_memory resolves `superseded_by` with it, and
    check_owner_cards scopes the baseline allowlist with it. Both consumers
    agreeing is what makes 'a record belongs to exactly one instance' true
    rather than merely intended."""
    dparts = os.path.relpath(
        os.path.dirname(abspath), base).replace("\\", "/").split("/")
    mem_idx = len(dparts) - 1 - dparts[::-1].index("memory")
    return os.path.join(base, *dparts[:mem_idx])
```

Then in `check_memory`, replace the inline `dparts`/`mem_idx`/`inst_base` computation with:

```python
                inst_base = _memory_instance_base(root, abspath)
```

leaving the surrounding comment and every finding unchanged.

- [ ] **Step 4: Scope the baseline allowlist to the skill's own instance.** In the `check_owner_cards` worker, where the allowlist is built, replace it with:

```python
                if memory_record_realpaths is None:
                    inst_real = os.path.realpath(inst)
                    memory_record_realpaths = _live_record_realpaths(
                        [p for p in _memory_record_files(inst, ignore)
                         if os.path.realpath(_memory_instance_base(inst, p))
                         == inst_real])
```

> This is the whole fix: `_memory_record_files(inst, …)` walks *every* `memory/` directory beneath `inst`, including nested instances'. Filtering to records whose own instance **is** `inst` makes ownership symmetric.

- [ ] **Step 5: Verify**

Run: `python3 -m unittest tests.test_validate.TestMemoryInstanceOwnership tests.test_validate.TestMemory tests.test_validate.TestMemoryIndex tests.test_validate.TestProvisioningGate tests.test_validate.TestNestedInstanceMemory tests.test_validate.TestNestedInstanceCards -v`
Expected: PASS — the pre-existing classes prove nothing else moved.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: exactly `0 error(s), 7 warning(s)`, exit 0.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "fix(validate): a memory record belongs to exactly one instance

Closes the outer-subsumes-inner asymmetry Slice 2.3a left open: a root skill
could take its baseline from a nested instance's records while the reverse was
blocked. The 'parent of the last memory component' rule now has one home and
two consumers.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: The demo canon and README

**Files:** Create `demo/canon.md`, `demo/README.md`

- [ ] **Step 1: Create `demo/canon.md`:**

```markdown
---
company: Umbercress
product: Umbercress Relay
domains:
  - umbercress.example
external_domains:
phone_range: 555-01
---
# The Umbercress world — demo canon

This file declares the fictional company the demo is built on. It is two things at
once: the human description of that world, and the validator's **positive allowlist**
— every email, domain, phone number, and IP address anywhere under `demo/` must trace
back to what is declared here or to a namespace reserved for fiction (#16).

Everything under `demo/` is in scope by directory. There is no per-file "this is
synthetic" marker, because a marker re-asserts rather than verifies.

## The company

**Umbercress** is a ~20-person B2B SaaS company. Its product, **Umbercress Relay**, is
a shift-scheduling platform sold to mid-market logistics operators. It has one office,
no subsidiaries, and about 60 paying customers on annual contracts.

Its size is the point. A 20-person company has a fractional CFO and a bookkeeper
rather than a finance department, one person doing all of People operations, and three
people in customer success — which is why the demo's ontology goes deep on customer
success, product, and People/HR, and stays deliberately shallow elsewhere.

## Identifiers

| Kind | Value | Why it is safe |
|---|---|---|
| Email domain | `umbercress.example` | `.example` is reserved for documentation (RFC 6761) **and** declared here |
| Phone numbers | `555-01xx` | The North American range reserved for fiction |
| IP addresses | `192.0.2.x`, `198.51.100.x`, `203.0.113.x` | TEST-NET-1/2/3, reserved for documentation (RFC 5737) |
| External domains | none | The demo links to nothing real. Adding one is a deliberate edit to this table and to `external_domains` above |

## The people

Eight people are named in the demo; the other dozen or so are unnamed. Emails follow
`first.last@umbercress.example`.

| Name | Role |
|---|---|
| Priya Raman | CEO |
| Marcus Bell | VP Customer Success |
| Dana Whitfield | Director of Product |
| Tomás Iglesias | VP Engineering |
| Ruth Okafor | Head of People |
| Jae-won Park | Principal Product Manager |
| Nina Sokolova | Senior Customer Success Manager |
| Ellis Warner | Staff Engineer |

**These names are the honest limit of this file.** A structured identifier can be
proven fictional; a person's name cannot. Any name is somebody's real name somewhere,
so "no real person is referenced here" rests on the fact that these were invented for
this demo and on maintainer review — not on any check. The same is true of the company
name, which was searched for prior art before it was chosen but cannot be proven
unique. See [docs/known-limitations.md](../docs/known-limitations.md).

## Customers

Customer accounts named in the demo are fictional operators: **Cartwright Haulage**,
**Belport Freight**, **Norlander Logistics**, **Waypoint Distribution**. They carry no
identifiers of their own beyond `umbercress.example` contacts.
```

- [ ] **Step 2: Create `demo/README.md`:**

```markdown
# demo — the pre-installed example company

A complete, fictional company OS you can read without configuring anything. It exists
so the shape of a generated `your-company/` can be inspected before you generate one,
and so the validator has real content to run against.

Read [canon.md](canon.md) first: it declares the fictional world, and it is also the
allowlist the validator checks every identifier in this directory against.

## What is here now

- `canon.md` — the fictional world and the identifier allowlist.

## What is coming

This directory is being filled in slices, and the walkthrough is not usable yet:

- The company's ontologies and org memory.
- Its skills, Owner's Cards, and constitution — including the rule that stops an agent
  from writing a performance assessment.
- The 15-minute walkthrough script, and the version pin that puts this directory under
  the same governance the validator applies to a real company repo.

Nothing here describes a capability that works today. When the walkthrough lands, this
section will say so and the script will be linked from it.

## What this is not

Not a template to copy. A real company OS is generated by the interview into its own
private repository (see [AGENTS.md](../AGENTS.md), "Two repos"). This is a worked
example to read.
```

- [ ] **Step 3: Verify nothing existing breaks**

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0 — `demo/` carries no content directory yet, so no structural check treats it as an instance, and its two relative links resolve.

- [ ] **Step 4: Commit**

```bash
git add demo
git commit -m "feat(demo): the Umbercress canon + demo README (#16 allowlist)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: `check_synthetic_identifiers`

**Files:** Modify `scripts/validate.py`, `tests/test_validate.py`

- [ ] **Step 1: Add failing tests** to `tests/test_validate.py`:

```python
CANON_OK = ("---\ncompany: Umbercress\nproduct: Umbercress Relay\n"
            "domains:\n  - umbercress.example\nexternal_domains:\n"
            "phone_range: 555-01\n---\n# The Umbercress world\n")


class TestSyntheticIdentifiers(unittest.TestCase):
    def _demo(self, d, body, name="notes.md", canon=CANON_OK):
        if canon is not None:
            _write(d, "demo/canon.md", canon)
        _write(d, "demo/" + name, body)

    def test_no_demo_directory_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "README.md", "mail me at real.person@acme.com\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_canon_domain_email_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Ask ruth.okafor@umbercress.example about it.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_domain_email_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Ask ruth.okafor@acme-logistics.com about it.\n")
            self.assertTrue(any(f.level == "ERROR" and "acme-logistics.com" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_reserved_namespaces_pass(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "a@x.test b@y.invalid c@example.com d@sub.example.org\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_url_host_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "See https://status.acme-logistics.com/incidents for detail.\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_bare_public_domain_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Their site is acme-logistics.com and it is slow.\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_filenames_are_not_domains(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "See canon.md, SKILL.md, validate.py and config.json.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_fiction_phone_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 555-0142 or (555) 019-9 nonsense.\n")
            self.assertEqual([f for f in validate.check_synthetic_identifiers(d)
                              if "555-0142" in f.message], [])

    def test_real_phone_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Call 415-555-2671 for support.\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_testnet_ip_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "The relay runs at 192.0.2.14 and 203.0.113.7.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_real_ip_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "The relay runs at 8.8.8.8.\n")
            self.assertTrue(any(f.level == "ERROR" and "8.8.8.8" in f.message
                                for f in validate.check_synthetic_identifiers(d)))

    def test_external_domain_declared_in_canon_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "Source: https://github.com/x/y\n",
                       canon=CANON_OK.replace("external_domains:\n",
                                              "external_domains:\n  - github.com\n"))
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_missing_canon_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/notes.md", "nothing identifying here\n")
            self.assertTrue(any(f.level == "ERROR" and "canon" in f.message.lower()
                                for f in validate.check_synthetic_identifiers(d)))

    def test_unreadable_canon_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            _write_bytes(d, "demo/canon.md", b"---\ndomains:\n  - \xff\xfe\n---\n")
            _write(d, "demo/notes.md", "x\n")
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_your_company_is_never_scoped(self):
        # #16 is explicit: real identifiers are legitimate in your-company/.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/canon.md", CANON_OK)
            _write(d, "your-company/notes.md", "ceo@acme-logistics.com 8.8.8.8\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_subdomain_of_a_canon_domain_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "app.umbercress.example is the console.\n")
            self.assertEqual(validate.check_synthetic_identifiers(d), [])

    def test_lookalike_suffix_does_not_pass(self):
        # 'notumbercress.example' ends with the canon domain as a STRING but is
        # not a subdomain of it.
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "notumbercress.example is someone else.\n")
            findings = validate.check_synthetic_identifiers(d)
            self.assertEqual(findings, [])  # .example is reserved regardless

    def test_lookalike_suffix_on_a_public_tld_errors(self):
        with tempfile.TemporaryDirectory() as d:
            self._demo(d, "notumbercress.com is someone else.\n",
                       canon=CANON_OK.replace("umbercress.example", "umbercress.com"))
            self.assertTrue(any(f.level == "ERROR" for f in
                                validate.check_synthetic_identifiers(d)))

    def test_wired_into_validate(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "demo/canon.md", CANON_OK)
            _write(d, "demo/notes.md", "ceo@acme-logistics.com\n")
            self.assertTrue(any(f.level == "ERROR" for f in validate.validate(d)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest tests.test_validate.TestSyntheticIdentifiers -v`
Expected: FAIL — no attribute `check_synthetic_identifiers`.

- [ ] **Step 3: Implement.** Add to `scripts/validate.py`, immediately after `check_changelog`:

```python
# Namespaces reserved for documentation and fiction — safe anywhere.
RESERVED_TLDS = (".example", ".test", ".invalid", ".localhost")
RESERVED_DOMAINS = ("example.com", "example.net", "example.org")
# RFC 5737 TEST-NET-1/2/3.
TESTNET_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.")
# A curated set of real public suffixes. Bare hostnames are only recognized when
# they end in one of these, which is what keeps 'canon.md', 'validate.py', and
# 'config.json' from reading as domains. High-signal, not exhaustive — the same
# posture as the secrets floor (#16).
PUBLIC_TLDS = ("com", "net", "org", "io", "co", "ai", "dev", "app", "cloud",
               "xyz", "me", "us", "uk", "ca", "de", "fr", "jp", "in", "tech",
               "info", "biz", "sh", "gg", "so", "to")

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,})")
_URL_HOST = re.compile(r"https?://(?:[^/@\s]*@)?([A-Za-z0-9.-]+)")
_BARE_DOMAIN = re.compile(
    r"(?<![A-Za-z0-9@._-])((?:[A-Za-z0-9-]+\.)+(?:%s))(?![A-Za-z0-9-])"
    % "|".join(PUBLIC_TLDS))
_PHONE = re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?([2-9]\d{2})\)?[-. ]?(\d{3})[-. ]?(\d{4})(?!\d)")
_IPV4 = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?![\d.])")


def _domain_allowed(host, allowed):
    """A host passes when it is, or is a subdomain of, a declared or reserved
    domain. Suffix matching is component-wise on purpose: 'notumbercress.com'
    ends with 'umbercress.com' as a string but is a different domain."""
    host = host.strip().rstrip(".").lower()
    if not host:
        return True
    if host.endswith(RESERVED_TLDS):
        return True
    for d in tuple(allowed) + RESERVED_DOMAINS:
        d = d.strip().lower().rstrip(".")
        if d and (host == d or host.endswith("." + d)):
            return True
    return False


def check_synthetic_identifiers(root, ignore=()):
    """#16, scoped to demo/ and ERROR: every structured identifier in demo
    content must trace to the demo canon or to a namespace reserved for fiction.
    Deliberately NOT applied to your-company/, whose identifiers are real by
    design — a WARN there would be cry-wolf noise that teaches adopters to
    ignore the validator.

    This verifies the structured surface only. A real company or person named in
    free prose looks exactly like a fictional one, and no check can tell them
    apart; that layer rests on the canon plus maintainer review, and is recorded
    as a Known Limitation."""
    findings = []
    demo_files = [p for p in iter_files(root, ignore)
                  if "demo" in os.path.relpath(p, root).replace(os.sep, "/").split("/")[:-1]]
    if not demo_files:
        return findings

    canon_path = os.path.join(root, "demo", "canon.md")
    if not os.path.isfile(canon_path):
        return [Finding("ERROR", os.path.join("demo", "canon.md"), None,
                        "demo content is present but there is no canon to verify it "
                        "against — every identifier under demo/ must trace to the "
                        "declared fictional world (#16)")]
    data, fm = _load_frontmatter(canon_path, os.path.join("demo", "canon.md"))
    findings += fm
    if data is None:
        return findings
    allowed = []
    for key in ("domains", "external_domains"):
        v = data.get(key)
        if _blank(v):
            continue
        allowed += [x for x in (v if isinstance(v, list) else [v])
                    if isinstance(x, str) and x.strip()]
    prefix = data.get("phone_range")
    phone_prefix = prefix.strip() if isinstance(prefix, str) and prefix.strip() else "555-01"

    for abspath in sorted(demo_files):
        rel = os.path.relpath(abspath, root)
        text, rd = _read_utf8(abspath, rel)
        if text is None:
            findings += rd
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            hosts = set(_EMAIL.findall(line)) | set(_URL_HOST.findall(line)) \
                | {m.group(1) for m in _BARE_DOMAIN.finditer(line)}
            for host in sorted(hosts):
                if not _domain_allowed(host, allowed):
                    findings.append(Finding(
                        "ERROR", rel, lineno,
                        "identifier %r is not in the demo canon or a reserved-for-"
                        "fiction namespace (#16)" % host))
            for exch, mid, last in _PHONE.findall(line):
                number = "%s-%s-%s" % (exch, mid, last)
                if not ("%s-%s" % (mid, last)).startswith(phone_prefix):
                    findings.append(Finding(
                        "ERROR", rel, lineno,
                        "phone number %r is outside the %sxx range reserved for "
                        "fiction (#16)" % (number, phone_prefix)))
            for ip in _IPV4.findall(line):
                octets = ip.split(".")
                if any(not o.isdigit() or int(o) > 255 for o in octets):
                    continue  # not an address; a version string or similar
                if not ip.startswith(TESTNET_PREFIXES):
                    findings.append(Finding(
                        "ERROR", rel, lineno,
                        "IP address %r is not in a TEST-NET range reserved for "
                        "documentation (#16)" % ip))
    return findings
```

> **Note on the phone rule:** the canon's `phone_range` is `555-01`, and the check compares it against the *last seven digits* (`NNN-NNNN`), so `555-0142` passes and `415-555-2671` (whose last seven are `555-2671`) does not.

- [ ] **Step 4: Wire into `validate()`** — after `findings += check_changelog(root, ignore)`, add:

```python
    findings += check_synthetic_identifiers(root, ignore)
```

- [ ] **Step 5: Verify**

Run: `python3 -m unittest tests.test_validate.TestSyntheticIdentifiers -v`
Expected: PASS (18 tests).

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0 — the canon and README carry only `umbercress.example`, `555-01xx`, and TEST-NET addresses.

Run the probe that proves the check is not vacuous on the real `demo/`:

```bash
python3 - <<'PY'
import sys; sys.path.insert(0, 'scripts'); import validate
f = validate.check_synthetic_identifiers('.', validate.load_gitignore('.'))
print("findings on the real demo/:", f or "none")
open('demo/_probe.md', 'w').write("mail ceo@acme-logistics.com at 8.8.8.8, call 415-555-2671\n")
f = validate.check_synthetic_identifiers('.', validate.load_gitignore('.'))
print("planted violations caught:", len(f))
for x in f: print("   ", x.message)
import os; os.remove('demo/_probe.md')
PY
```

Expected: `none` for the committed content, then **3** planted violations caught (domain, IP, phone). Zero caught means the scope filter is not matching the real `demo/` — investigate before continuing.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate.py tests/test_validate.py
git commit -m "feat(validate): #16 synthetic-identifier check (demo-scoped ERROR)

Every email, URL host, bare public domain, phone, and IP under demo/ must trace
to the canon or a reserved-for-fiction namespace. Missing canon with demo content
present fails closed. Never applied to your-company/.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: The documented ceiling and the full gate

**Files:** Modify `docs/known-limitations.md`, `AGENTS.md`

- [ ] **Step 1: Append to `docs/known-limitations.md`:**

```markdown
## Demo content (#16)

- **The synthetic ceiling.** groundwork mechanically verifies that structured
  identifiers in demo content resolve to reserved-for-fiction namespaces or the
  declared demo canon, and scans all committed content for high-signal secret
  patterns. It does not — and cannot, mechanically — prove that no real-world entity is
  referenced in free prose. That the demo's narrative names no real company, person, or
  customer rests on the fixed fictional canon plus maintainer review, not an automated
  check. The company name was searched for prior art before it was chosen; the person
  names cannot be searched in any meaningful sense, because every name is somebody's.
- **Bare-domain detection is high-signal, not exhaustive.** A hostname written without a
  scheme is only recognized when it ends in one of a curated list of public suffixes.
  That is what stops `canon.md` and `validate.py` reading as domains, and it means a
  real domain on an unlisted suffix would pass. Emails and `http(s)://` URLs are matched
  regardless of suffix.
- **The check is scoped by directory name.** Anything under a directory named `demo` is
  in scope; `your-company/` never is, by design — its identifiers are real and
  legitimate (#16's scope matrix). Running the validator with a demo directory *as* the
  root finds no `demo` component and skips the check; the repo gate runs from the repo
  root, which is the supported setting. This mirrors the existing limitation for
  `validate.py <memory-dir>`.
- **A four-number dotted string is treated as an IP address.** A version string like
  `10.4.2.1` in demo prose would be flagged. Failing toward a false positive is the
  intended direction here.
```

- [ ] **Step 2: Update `AGENTS.md`.** In "Built and working", add after the `proposals/` bullet:

```markdown
- `demo/` — the pre-installed example company (**Umbercress**). Its canon declares the
  fictional world and doubles as the validator's identifier allowlist. The company's
  ontologies, skills, governance, and the 15-minute walkthrough are still being filled
  in — `demo/README.md` says what is there today.
```

And in the "Not built yet" list, replace the `demo/` bullet with:

```markdown
- `demo/` walkthrough — the synthetic company's content and the 15-minute 3-query
  script. The directory exists and its canon is in place; the walkthrough is not
  usable yet.
```

- [ ] **Step 3: Full gate**

Run: `python3 -m unittest discover -s tests 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `OK (skipped=1)`, roughly 595 tests.

Run: `python3 scripts/validate.py . ; echo "exit: $?"`
Expected: `0 error(s), 7 warning(s)`, exit 0. The WARN count must not move — `demo/` introduces none.

Run: `python3 scripts/validate.py . --diff main ; echo "exit: $?"`
Expected: exit 0. `demo/` has no `groundwork.pin`, so it is not yet a governed root and the #18 tripwire stays dormant (the pin lands in 2.3e, after the content settles).

- [ ] **Step 4: Commit**

```bash
git add docs/known-limitations.md AGENTS.md
git commit -m "docs: the #16 synthetic ceiling, stated where the names are

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Scope note — what this slice excludes

- **No demo ontologies, skills, governance, or memory.** `demo/` carries only its canon and README, so no structural check treats it as an instance yet. **2.3c** adds the ontologies and org memory, including the async-standups decision record with its supersession chain (demo query 1).
- **No `groundwork.pin`.** It lands in **2.3e**, after the content is stable, so the #18 tripwire activates on a settled instance instead of demanding a proposal per authored file.
- **No changes to the global secret scan.** #16's other half is already built and untouched here.
- **Still open for the maintainer:** three Slice 1.5d-ii deferrals (dot-directory classification, case-variant authorization, the path-style nit), the `SKIP_RELPATHS` gate-scoping sign-off, and the standing re-review rule. Task 1 closes the 2.3a memory-boundary question.

## Self-Review

- **Ticket coverage (#16):** canon as single source of truth and positive allowlist → `demo/canon.md`, both human doc and machine-read; in-scope by directory with no per-file marker → the scope rule and its stated reasoning; the scope/severity matrix (demo-only, ERROR; never `your-company/`) → `check_synthetic_identifiers` plus `test_your_company_is_never_scoped`; RFC-reserved namespaces (`.example`/`.test`/`.invalid`, `555-01xx`, TEST-NET) → the constants and their tests; the residual Known Limitation → `docs/known-limitations.md`, quoted close to the ticket's own wording.
- **Placeholder scan:** no TBD/TODO; every file's content and every code change is given in full, with verification commands and expected output.
- **Type consistency:** `check_synthetic_identifiers(root, ignore=())` → `list[Finding]`, matching every sibling check and its call site in `validate()`. `_memory_instance_base(base, abspath)` → `str`. `_domain_allowed(host, allowed)` → `bool`. No new imports.
- **Pre-empts the recurring Codex findings.** (a) *Fail-open on malformed input* — demo content with a missing or unreadable canon ERRORs rather than passing; a non-list `domains` value is filtered by `isinstance` rather than crashing. (b) *Alias laundering* — `_domain_allowed` matches components (`host == d or host.endswith("." + d)`), so `notumbercress.com` does not inherit `umbercress.com`'s allowance; there is a dedicated test for exactly that. (c) *Corpus void* — Task 3 Step 5 plants three violations in the real `demo/` and asserts they are caught, so "no findings" is distinguished from "the scope filter never matched". (d) *Non-scalar frontmatter* — `_blank` plus `isinstance` guards on `domains`, `external_domains`, and `phone_range`; a bare `external_domains:` parses to `[]` and is skipped, which is exactly how it ships.
- **The load-bearing decision is surfaced, not slipped in:** closing the memory-ownership asymmetry tightens an existing behavior. It is Design call 1, with the rule stated in one sentence, the reason it expires this week, and the counter-argument (no shared memory pool across instances) written down.
