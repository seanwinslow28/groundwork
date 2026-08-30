# Round 02 — Codex review

**Reviewed:** `c3af4d2`
**Verdict:** **does not approve** — Standards 0 findings; Spec 4 findings, worst severity
**Major** (the reviewer's own words).

## Findings

### 1. Major — "editable header can launder committed entries" — FIXED

The reviewer's construction: open an HTML comment in the editable header, leave every base
entry verbatim and contiguous below it, close the comment after them, then append a
replacement entry. Every rule the narrowing enforced was satisfied and the guard returned
`True`, while the rendered file showed a reader only the replacement entry.

**Measured before acting**, on `c3af4d2`:

```
guard verdict on the laundering diff: True
appended entries: ['- 2026-07-28 | skills/a/SKILL.md | the only one a reader sees | ...']
```

It is real, and this branch created it: the pre-#32 whole-file guard refused any inserted
header line outright, so the comment could never be opened. It is the one way the editable
header can reach content it does not own — every entry survives in the bytes and none of them
survives to a reader — and the one-glance property #17 rests on is a property of reading the
file.

**Fixed.** `_changelog_header_leaves_a_comment_open` refuses a header whose last `<!--` has no
`-->` after it inside the header. `_changelog_appended_span` now returns a reason rather than a
bare boolean, so the two violations carry distinct ERRORs instead of one message that would
have been wrong about which rule broke. Six pure tests and one integration test; the
integration test asserts the ERROR class and the message's distinguishing phrase, not the whole
string.

Deliberately not claimed: that this closes every way a header can change how the ledger
renders. It closes the one that **hides** it. The check is textual and conservative — a `<!--`
inside a fenced code block counts, which can only over-report — and it does not model arbitrary
raw HTML. That residue is now written into `docs/known-limitations.md` rather than left for a
later round to find.

### 2. Low — "rotation prose overclaims" — FIXED

`docs/known-limitations.md` said archiving or rotating the changelog "reads as a rewrite",
unqualified, while an entry-less base now accepts a header-only replacement. Correct, and the
reviewer correctly noted it does not challenge decision 3. Qualified with "Once a changelog
holds an entry", plus the reason the case below it is empty: there is nothing to archive.

`docs/roadmap.md` carries the sibling sentence and was **left alone deliberately** — it is
scoped to "a long-lived changelog", which already carries the qualifier. Recorded here so the
sweep's asymmetry is a decision and not an omission.

### 3. Low — "demo roster claim includes unsupported deletions" — REJECTED

The finding: `demo/governance/changelog.md` says roster changes escalate to a proposal, while
deleting `demo/governance/roles.md` produces only a WARN and a proposal cannot target a deleted
file; it asks that the claim be qualified to additions and edits.

**Rejected — factually wrong.** Its premise is that the sentence states a validator severity.
It does not: it is a statement of Umbercress's governance routing, saying what escalates and
what appears in the changelog. Deletion **is** escalating, and the source says so directly —
[`proposals/README.md`](../../../../proposals/README.md), the "A governed file **deleted**"
bullet: *"Retiring a rule, skill, or roster is escalating, but a proposal's `target` must be an
existing file, so a deletion can never be traced to one and the honest record is the
maintainer's consent commit. This is a documented limitation, not an oversight."* The WARN is
the gate conceding it cannot trace a correct routing claim, not the routing claim being false.

**The reading under which the finding is fair**, recorded rather than argued away: a reader
who takes the preamble as a description of what the gate enforces would be misled. Two things
answer that. The sentence's subject is the company's governance, and the same imprecision would
apply identically to every other family it names — rules, Owner's Cards, track-2 skills — so
qualifying only the clause this branch touched would leave the sentence less consistent than it
found it. The deletion limitation is carried for all three families in
[`docs/known-limitations.md`](../../../known-limitations.md).

### 4. Low — "caller docstring retains the falsified whole-file claim" — FIXED

`blast_radius_diff_findings`'s docstring still said "the changelog itself is append-only
(ERROR)". A correct catch and a real miss: the sweep for claims this change falsified was run
across `*.md` and not across the source's own docstrings. Corrected, and the sweep re-run over
`scripts/validate.py` — the other four `append-only` sites are the memory-source message, the
stateless check's docstring, the deletion message, and the pass-1 comment, none of which the
narrowing touches.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`.

| Mutation | Result |
|---|---|
| Neuter the open-comment check | 5 failures |
| `rfind("<!--")` to `find("<!--")` — first comment instead of last | 1 failure |
| None (restored) | OK, 867 |

## The reviewer's own verification, and a correction to it

The reviewer reported the three validator commands green and "860 tests discovered, 680 failed
during `TemporaryDirectory` setup because the read-only sandbox exposes no writable temporary
directory", calling that environmental. **That is correct**, and it was verified outside the
sandbox rather than taken on trust: `python3 -m unittest discover -s tests -q` on `c3af4d2`
returned `OK, 860 tests, skipped=1`. The count is 867 after this round's tests.

Its closing note — that rule 9's `round-02.md` and README update "could not be written: the
sandbox rejected the patch as read-only" — is not a finding and is not treated as one. Writing
the record is the builder's job, not the reviewer's.

## Worktree drift during the round, disclosed

A one-phrase precision edit to `docs/rule-map.md` was made after the review launched — the
severity cell said "at or below the changelog's first entry line", which does not say *which
file's* first entry line, and the guard anchors on the base's. It was stashed within the round
so the worktree stayed byte-identical to `c3af4d2`, and it is applied in this round's fix
commit. Recorded because a reviewed revision that drifted mid-round is worth stating, not
because the edit was consequential.
