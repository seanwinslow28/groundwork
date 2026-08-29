# Review record — `docs/rule9-categories-consent-clause`

Branch name as it stood when this directory was made: `docs/rule9-categories-consent-clause`.
Merge target: `main`, at `aa26e3a`.

**The slice.** The two governance-document amendments R1 decided and deliberately did not
carry, recorded as decisions 5a and 5b of entry 12 in
`docs/superpowers/plans/r1-roster-schema-v2-reviews/`:

1. build-sessions rule 9 gains the closed list of three rejection categories, with the
   open-plus-maintainer-override escape hatch left stated and unchanged.
2. `CONTEXT.md:105`'s consent-gate entry gains one qualifying clause, resting on the
   generation exemption alone — **not** on decision 8's migration bootstrap, which
   classifies a roster addition at the v1→v2 boundary as *not escalating*, a case the
   invariant survives.

Both are prose. No validator change, no test change.

This branch also records the closure of the two open maintainer items these decisions
answered, in the directories that raised them:
`docs/superpowers/reviews/generate-consent-gate-base/README.md` (item 1) and
`docs/superpowers/reviews/review-record-rule/README.md` (grounds for rejecting a finding).

## Entries

| Entry | Reviewed revision | Verdict | Fixes committed in |
|---|---|---|---|
| `round-01.md` | `85211b4` | 1 minor finding, 0 spec findings (no approval word given) | `74369a5` |
| `round-02.md` | `74369a5` | 2 minor findings (reported once per axis; no approval word given) | `4dc7bc6` |
| `round-03.md` | `4dc7bc6` | 1 minor finding (reported once per axis; no approval word given) | record-only correction, in `round-03.md` itself |

## Open findings

None. Every finding from rounds 1–3 is fixed or corrected.

**Two corrections to earlier entries, each carried by a later one** — the entries themselves
are immutable, as rule 9 requires:

- **`round-02.md` corrects `round-01.md`:** its scope note says seven disclosed items where
  the list holds six. Six is right.
- **`round-03.md` corrects `round-02.md`:** its claim that every complete entry-12 citation
  trips `check_entropy` is false — a relative markdown link to the directory scores 3.952797
  and resolves — and its two figures came from two different citation forms. The split
  citation in rule 9 is a style choice, not a necessity; `round-03.md` carries all four
  measurements.

## Rejected findings

None.

## Maintainer items

None. The two maintainer decisions this slice implements were taken before it started, as
decisions 5a and 5b of entry 12 in `docs/superpowers/plans/r1-roster-schema-v2-reviews/`.
