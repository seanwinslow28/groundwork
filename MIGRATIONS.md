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

## Deferred: per-check `since:` demotion

At `SCHEMA_VERSION = 1` there is no older schema to be lenient toward, so the
per-check `since:` mechanism (demoting a genuinely-new requirement to a "new since
your pin" warning) is **not yet wired**. When the first breaking bump to v2 is authored,
each new check declares the `since:` version it was introduced at, and a new-requirement
check demotes to WARN for content pinned before it. Until then this is documented intent,
not code.

## Current schema version: 1

Schema **v1** is the first released schema. There are no migrations yet.

### Why the executive-view grammar tightened without a bump

The executive-view table moved to a restricted canonical grammar (one legal shape;
anything else ERRORs) while still on v1. Content that a permissive reader once accepted
— reordered columns, `| :--- |` alignment, two-column tables, rows without boundary
pipes — now fails the gate. Read strictly, that is a breaking change to a content shape,
and the pull promise above says a same-version pull is always safe.

It was landed at v1 anyway, deliberately, and this is the record of why: **at the time,
no `groundwork.pin` existed anywhere.** The pin file ships with a generated company
repo; until one existed there was no pinned content in the world for a migration
boundary to protect, and the `since:` demotion mechanism that would soften such a change
is itself documented-but-unwired for exactly the same reason. Bumping to v2 then would
have spent the first migration on a change with zero affected repos and armed the skew
gate against nothing.

**That window is closed.** The first `groundwork.pin` landed on 2026-07-29, on the
`demo/` company instance, and the promise binds from it. A tightening of this kind —
content a permissive reader once accepted that a stricter one now ERRORs — is from here
on a **v2 change with a migration note**, no matter how small the syntax involved. The
"no adopters yet" argument was used exactly once, on the record, and is now spent.
