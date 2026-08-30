# Entry 01 — maintainer decisions, not a review round

This entry is **not a Codex review round**. It records the three decisions the maintainer
made under [rule 5](../../../agents/build-sessions.md) before any code was written, and the
measurements those decisions rested on. Codex rounds begin at `round-02.md`.

**Decided:** 2026-08-30, by the maintainer, on all three questions issue #32 leaves open.

## What was measured first, on `b2cb1d0`

Every fact the issue asserts was re-confirmed rather than trusted:

- `_changelog_append_only` was whole-file — "every line committed at base must survive, in
  order, as the head of the new file" — preamble included.
- Its only caller was `blast_radius_diff_findings`, which raises the ERROR under `--diff`.
- The entry-line test is `s.strip().startswith("- ")`, in the stateless check
  (`_check_changelog_instance`) and in `_changelog_appended_targets`.
- `governance/changelog.md` holds 17 lines and **zero** entry lines;
  `demo/governance/changelog.md` holds 11 lines and **zero** entry lines.

**The defect was reproduced.** The correcting edit to the demo preamble — adding the roster
to the enumeration — was applied and the gate run:

```
ERROR demo/governance/changelog.md  the governance changelog is append-only — an existing entry was edited, reordered, or removed (#17)
1 error(s), 7 warning(s)
```

Two things that probe settled, both of which move against the kickoff's expectation:

1. **It cost no pending proposal.** The run produced that one ERROR and no "escalating
   change with no pending proposal". `governance/changelog.md` is not one of the governed
   artifact families, so correcting the demo preamble alone carries neither a proposal nor a
   post-merge removal obligation. The cost the issue's comment names arrives only if a slice
   touches a governed demo file alongside, and this one does not. Testing against `demo/` is
   therefore both the faithful surface and the free one.
2. **The message itself was false on today's files.** It said an existing entry was edited
   where no entry exists.

## Decision 1 — narrow the guard

**Chosen: narrow it.** Against declining and documenting the limitation, and against a third
option raised at escalation and not taken: moving the mutable prose out of the guarded file
entirely, leaving the changelog a pure ledger with a minimal frozen header pointing at a
sibling doc. That option loosens nothing and was genuinely attractive; it was refused because
it pays a permanent structural cost in every generated repo and does not repair a repo already
generated, whose header is stale today.

**The counter-argument, recorded because it is the serious one.** Loosening an append-only
guard is how a laundering route gets created. It has a sharper form than the issue states:
`demo/governance/changelog.md` is not a governed family, so it carries no #18 consent gate —
**the append-only guard was the only automated protection on that file at all.** Narrowing to
entries leaves its header with none. The answer is that the commit bit is the real enforcement
(rule 3, #18) and a header is reviewable prose in a PR like any other. That is an argument,
not a proof, and the maintainer decided it knowing so. It is written into
[`docs/known-limitations.md`](../../../known-limitations.md) rather than left implicit.

## Decision 2 — the boundary is anchored in the BASE

The issue's phrasing, "the contiguous block before the first entry line", does not say *which
file's* first entry line, and that ambiguity is the whole security question.

**Chosen: anchored in the base.** Let `k` be the index of the first entry line in the base
text. `base_lines[k:]` must survive verbatim and contiguous in the new file, positioned at the
new file's first entry line. Anything above it is free.

Rejected: anchoring in the new file. Under that reading an attacker edits the base's first
entry into non-entry prose and it silently joins the editable header — the laundering route
the counter-argument names, left open.

**An entry, byte for byte:** a line whose `str.strip()` — Unicode whitespace, both ends —
begins with U+002D HYPHEN-MINUS followed by U+0020 SPACE. Identical to the two pre-existing
sites, deliberately, so the three cannot drift.

**Can an existing entry be converted into non-entry text?** No. The new file's first entry
must equal the base's first entry, so converting it means either a different entry now leads
(mismatch) or no entry line survives (refused outright). Editing a later entry, reordering,
removing one, interleaving prose between entries, and prepending an entry are all refused for
the same reason. The one residual freedom is prose above every entry, which is already
achievable today by appending prose below them.

## Decision 3 — an entry-less base protects nothing

**Chosen: the whole file is editable when the base holds no entry line.** That is the state of
both changelogs shipped here and of every freshly generated company repo, so the narrowing
ships in the state that grants the most freedom. The grounds: there is no entry to launder
until a first one exists, and the guard engages the moment one does. A floor — requiring, say,
the first line to survive — was rejected as arbitrary: it defends nothing nameable.

**Counter-argument, recorded:** the guard's teeth are therefore not exercised by any shipped
tree, only by the tests. That is why the mutation table in `round-02.md` onward matters more
here than usual.

**A related exposure, named and not new:** an attacker choosing an old `--diff` base gets a
more permissive protected block. That is the same shape as open issue #40 and this change
neither creates nor worsens it.

## MIGRATIONS.md — checked, not assumed

`MIGRATIONS.md` bumps `SCHEMA_VERSION` only on a breaking change, "a change to the shape a
running agent actually needs", and the pull promise is about content a stricter engine would
newly reject. This slice runs the other way: the gate now **accepts** content it previously
rejected, so no existing repo becomes invalid and no adopter must change anything. **No bump,
no migration note.** Verified against [`MIGRATIONS.md`](../../../../MIGRATIONS.md) directly.
