# Migrations

groundwork's content schema is versioned by a single integer, **`SCHEMA_VERSION`**,
bumped **only on a breaking change** — a change to the shape a running agent actually
needs. Additive commits do not bump it.

Each generated company repo records the schema version it was built against in a
`groundwork.pin` file at its root. When you pull a newer engine and `validate` reports
a **migration gate** — *"content is schema vN, engine is vM; see MIGRATIONS.md for
vN→vM"* — find the note below.

## The pull promise

- **Same schema version** (engine merely has more commits): pull is always safe. You
  can pull indefinitely; mere age never makes pull dangerous.
- **A breaking bump landed**: one clean migration-boundary error, never a scatter of
  field errors. Max skew is **one** breaking version.
- **Engine older than the pin** (you forgot to pull, or newer content arrived from
  elsewhere): a warning to pull the engine — validity is not asserted against a schema
  the engine doesn't yet know.

## The migration contract

Every breaking bump ships, here, a note: **what changed, what to change, why.** The
validator points precisely at each offending file and field. Where a change is
mechanical, a transform script *may* ship — a bonus, never the thing the promise rests
on. Full re-interview is a V3 capability, not a migration step.

## The pin file (`groundwork.pin`)

```
---
schema_version: <int>          # what skew compares (integer to integer)
generated_by_commit: <sha>     # provenance only — never used for skew math
---
```

It lives at the company-repo root, independent of `interview/`.

## Per-check `since:` demotion

Each check declares the `SCHEMA_VERSION` it was introduced at. A finding from a check
introduced at v*N* **demotes from ERROR to WARN** for content pinned below *N*: a v1 repo
has no roster, so a v2 resolution check cannot bind content pinned before rosters existed.

This is not leniency. Such a repo is already red at the **one** migration-boundary ERROR
above, and the demoted WARNs are the precise finger-pointing that error promises — which
files, which fields — rather than a scatter of ERRORs a reader has to triage. Content under
no pin, the engine's own tree included, is never demoted.

Wired at the v1→v2 bump (`apply_since_demotion` in `scripts/validate.py`), as this document
scheduled it.

## Current schema version: 2

Schema **v1** was the first released schema.

### v1 → v2 — roles are the accountable unit

**What changed.** An owner is a role or a named holder, and a role must be **held** to
activate. Every instance now carries a roster at `governance/roles.md` naming each role, its
holder(s), and each holder's type (`human` or `agent`). A rule that carries a rung (active)
must have all four owner fields — `owner`, `value_owner`, `runtime_check_owner`,
`human_appeal_owner` — resolve against it, and `human_appeal_owner` must resolve to at least
one **human**: an appeal path that terminates in a model is not an appeal path. A draft rule
may still carry unheld or absent owners; its gaps are named WARNs. **A `high-risk` draft is
the exception** — the safety spine runs draft-time, so an appeal owner that is missing,
resolves to nobody, or resolves only to agent holders ERRORs on a draft too. The roster also joins the
consent gate as a third governed artifact family — changing it in a governed root is an
escalating change wanting a proposal.

**What to change.**

1. Write `governance/roles.md`. Frontmatter: `valid_at` (when this mapping was last
   confirmed — a snapshot, not when a fact became true), `review_by`, and `source` (where the
   org map came from). Then one table, `| Role | Holder | Type |`, plain-text cells.
2. Make every **active** rule's four owner values resolve. Two ways, by exact string: a value
   matching a **Role** cell resolves to that row's holders; a value matching a **Holder** cell
   resolves to that holder. A person-named owner therefore resolves through a **holder-only
   row** — the Role cell left empty, which asserts a holder without asserting a role. A role
   with no row, or a row with no holder, is unheld.
3. Check that every `human_appeal_owner` reaches a holder typed `human`.
4. Set `schema_version: 2` in `groundwork.pin`.

A rule you cannot complete does not have to be forced: drop its `rung` and it is a draft
again, with its gaps named as WARNs rather than guessed at — **except a `high-risk` rule**,
whose appeal path must reach a named human whether it is a draft or not. There is no rung
six, and dropping the rung does not buy an exemption from that.

**Why.** A rule the machine enforces with an owner nobody claims is *enforced, but nobody
owns it* — the failure a persona-company run actually produced, where an owner field read
"the function, no person named" and the gate stayed green. Resolution against a roster is
what tells an accountable office apart from a disclaimer, and the check could not be added
without rejecting content a v1 reader accepted.

**What it does not do.** Nothing verifies a roster row against the world; a stale roster is a
confident error one level up ([docs/known-limitations.md](docs/known-limitations.md)). Owner
fields outside the constitution — deep records, Owner's Cards, memory records — are not
resolved in v2.

### Why the executive-view grammar tightened without a bump

The executive-view table moved to a restricted canonical grammar (one legal shape;
anything else ERRORs) while still on v1. Content that a permissive reader once accepted
— reordered columns, `| :--- |` alignment, two-column tables, rows without boundary
pipes — now fails the gate. Read strictly, that is a breaking change to a content shape,
and the pull promise above says a same-version pull is always safe.

It was landed at v1 anyway, deliberately, and this is the record of why: **at the time,
no `groundwork.pin` existed anywhere.** The pin file travels with pinned company
content; until any existed there was no pinned content in the world for a migration
boundary to protect, and the `since:` demotion mechanism that would soften such a change
is itself documented-but-unwired for exactly the same reason. Bumping to v2 then would
have spent the first migration on a change with zero affected repos and armed the skew
gate against nothing.

**That window is closed.** The first `groundwork.pin` landed on 2026-07-29, on the
`demo/` company instance, and the promise binds from it. A tightening of this kind —
content a permissive reader once accepted that a stricter one now ERRORs — is from here
on a **v2 change with a migration note**, no matter how small the syntax involved. The
"no adopters yet" argument was used exactly once, on the record, and is now spent.
