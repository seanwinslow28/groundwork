# Round 9 — Codex

**Reviewed revision:** `2bc94ce` (branch `feat/roster-schema-v2`, twenty-six commits against
`main` at `ddcb7a1`).
**Verdict:** **does not approve.** 6 findings — 1 BLOCKER, 1 HIGH, 2 MEDIUM, 2 LOW.

Codex confirms the README's 49-finding total and per-round severity arithmetic, that
`git diff --check` is clean, and that both validator invocations reproduce the disclosed
outputs. On the `_roster_key` question it reports finding **no remaining raw comparison
path** — role keys, holder keys, type-conflict detection, collision detection and owner
resolution all normalize — and that NFC rather than NFKC is the right form, since NFKC
would fold fullwidth and ligature spellings that are different names. The builder ran the
full suite on the reviewed revision: OK, 817 tests, skipped=1.

## Findings

| # | Severity | Finding | Confidence | Disposition |
|---|---|---|---|---|
| 1 | BLOCKER | Unicode general categories are **not** a complete test for invisible text. U+034F and U+FE0F are `Mn`, the Hangul fillers are `Lo`, U+2800 is `So`. Parsed as the sole Holder, each produced no finding and resolved `CISO` to a human holder readers cannot see | CONFIRMED | **Fixed, and the claim behind it withdrawn** — see below |
| 2 | HIGH | `_load_roster` uses `os.path.isfile` and `_read_utf8`, both of which follow a symlink, and the stateless check never rejects a symlinked roster. The proposal check compounds it: `resolved.startswith("governance/roles.md")` accepts a target resolving to `governance/roles.md.backup`. So ordinary `validate` could resolve active-rule ownership from unaudited content outside the artifact. `--diff` has its own symlink defence, so this is not a complete consent-gate bypass | CONFIRMED | **Both fixed.** A symlinked roster is now a **broken** roster with its own ERROR, not an absent one — absent is a different finding with a different severity. The proposal bucket test compares for equality when the target is the roster, since that bucket is one file rather than a directory prefix |
| 3 | MEDIUM | Refusing every `Cf` character also refuses U+200C and U+200D, which Unicode documents as required in some Persian names — so the roster could not represent some valid person-named owners. A contextual rule is needed | CONFIRMED | **Fixed.** Zero-width non-joiner and joiner are allowed **between two letters** and refused anywhere else. Two tests: a Persian name containing ZWNJ parses and resolves; a bare ZWNJ as the whole holder is still refused |
| 4 | MEDIUM | The authoritative roster example in `governance/README.md` places the table immediately after the frontmatter closer, which round 8's unconditional blank-line rule refuses. The plan repeats the invalid example. An adopter copying the documented schema gets a roster the validator rejects | CONFIRMED | **Fixed, and guarded.** The example gains a heading and a blank line, and a new test **extracts the fenced example from `governance/README.md` and parses it**, asserting it is clean and that its two rows resolve. A schema whose own example fails is not a schema, and that is now checked rather than remembered |
| 5 | LOW | `round-08.md` says the category check is "complete by construction" and that there is "no further omission to find". Finding 1 disproves both | CONFIRMED | **Corrected here**, since `round-08.md` is immutable. The claim was wrong when written. See below |
| 6 | LOW | `governance/README.md:49`, `MIGRATIONS.md:91` and `governance/roles.md:14` all promise resolution "by exact string", while `_roster_key` compares after NFC normalization | CONFIRMED | **Fixed.** All three now say "by exact string after NFC normalization", and `governance/README.md` records why NFC and not NFKC: NFKC would fold fullwidth and ligature forms, which are different names that happen to look related |

## The completeness claim, withdrawn

Round 8 replaced an enumerated list of invisible characters with a Unicode category test and
called it "complete by construction". Round 9 disproved that with four characters whose
categories are `Mn`, `Lo` and `So`. The claim was wrong, and this entry retracts it.

The check is now **three overlapping nets**: the invisible general categories; a named set
of characters that render as nothing while carrying a visible category; and a requirement
that a Role or Holder cell carry at least one letter or digit, which refuses a cell built
from marks or symbols without needing to know which of them render.

More importantly, `docs/known-limitations.md` now states plainly that this is **high-signal
and not exhaustive** — the same posture, and the same words, the secrets floor already uses.
Visibility is a property of fonts and renderers, not of the Unicode character database, so
no local check can decide it, and Unicode gains characters faster than any list is
maintained. The zero-width-joiner exemption added this round is itself a hole a determined
author could stand in, and the limitation says so.

Nine rounds have now each found a case the previous round's rule missed. The lesson this
entry records is not that the tenth rule will be right: it is that claiming completeness was
the error, and the honest artifact is a documented limitation plus overlapping partial
defences.

## Notes for the next round

- The active-rule ERROR suppression, offered for challenge in rounds 1–8, went unchallenged
  again.
- Findings by round: 11, 7, 6, 4, 5, 4, 6, 6, 6.
- Every count above was recomputed from the entries or the source.
