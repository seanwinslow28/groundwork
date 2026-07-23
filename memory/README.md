# Org memory

What this organization remembers, with what provenance, owned by whom, and how an
observation becomes policy. Files + validator checks — no engine (session recall and
retrieval belong to the harness). One record per file under a `memory/` folder; the
index lists live records only.

## Record schema (six field groups, no more)

| Field | Meaning | Required |
|---|---|---|
| `provenance` | `observed` / `inferred` / `confirmed` / `superseded` | always |
| `owner` | who is accountable for this record | always |
| `valid_at` | ISO date the fact became true (frozen) | always |
| `invalid_at` | ISO date the fact stopped being true | iff superseded |
| `review_by` | ISO date the record should be re-checked | soft (WARN) |
| `superseded_by` | repo-relative path to the record that replaces this one | iff superseded |
| `source` | the evidence behind the record | always (ERROR only for `confirmed`) |

## Rules

- **Never edited — superseded.** A fact that stops being true is not deleted or
  rewritten; a new record supersedes it, and the old one gets `invalid_at` +
  `superseded_by`. Doubt without a replacement fact = supersession by a record whose
  body states the retraction. (Bi-temporal, Zep's pattern.)
- **Frozen at commit:** the body and `valid_at`. **Mutable as governance acts:** `owner`
  (reassignable), `review_by` (bumpable), `source` (append-only), the provenance label
  (**forward only**: `observed`/`inferred` → `confirmed`; → `superseded` only via the
  supersession rules; no downgrades).
- **Supersession fields are forbidden on live records** — `invalid_at`/`superseded_by`
  appear only on a superseded record.
- **The index lists live records only.** Superseded records live in history, reachable
  via `superseded_by` chains (and that is how the index stays inside the load budget).
- **Promotion path** (observation → working note → decision) is carried by folder
  placement, not a frontmatter field.

## Checking immutability at PR time

The default `validate` run is stateless (it checks each record's shape). At PR/CI
time, run the diff mode to enforce that records are never edited:

```
python3 scripts/validate.py --diff <base>   # e.g. --diff main
```

It ERRORs on any change to a frozen field (body, `valid_at`), a provenance downgrade
or removal, a non-append `source` change, an altered supersession field, or a
**deleted** record (records are superseded, never deleted). Whitespace-only changes
at the edges of the body (e.g. a trailing newline) are tolerated — they are not
treated as edits. The four-verb reconciliation
(add / update / supersede / discard) stays a human review practice; the diff mode is
its mechanical backstop.
