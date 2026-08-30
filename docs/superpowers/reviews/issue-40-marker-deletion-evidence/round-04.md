# Entry 04 — Codex review round

**Reviewed revision:** `512126f`
**Verdict, in the reviewer's words:** "The round is not clean. I found four Major and one
Minor classifier defects, plus two Minor prose/record defects."
**Brief:** audit round 03's three repairs for over-correction first, then the standing
classifier-correctness and completeness questions.

Still in the finding-class entry 01 named, so **rule 11 does not fire**.

## Findings

Severity words are the reviewer's own, verbatim.

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Major | History simplification prunes a side branch whose marker was added and removed before a net-zero merge. | **Rejected — factually wrong** |
| 2 | Major | Bare `-m` takes the format `log.diffMerges` configures; a COMBINED record carries one source mode per parent, so `parts[1]` is not the destination and the parser misread it. | **Fixed** — `--diff-merges=separate`, plus a guard |
| 3 | Major | `--diff-filter=A` removes the `T` record for a path that arrived as a symlink and later became a real file, so the only proof it ever existed as a marker was discarded. | **Fixed** — the flag is gone |
| 4 | Major | Base presence was pathname-only: a base holding a SYMLINK named `groundwork.pin` suppressed the finding for a real marker added and deleted after it. | **Fixed** — `_base_markers` reads modes |
| 5 | Minor | Working-tree membership by NAME was checked before the type proof, so a broken symlink left where the marker had been counted as the marker still present. | **Fixed** — the name check is gone; `isfile` is the only proof |
| S1 | Minor | Prose overclaims the type proof, and a caller comment still credits `lexists`. | **Fixed** |
| S2 | Minor | The record says two test docstrings crediting `lexists` were corrected; a third was not. | **Fixed** |

## The rejection, and the evidence for it

**Finding 1 is rejected as factually wrong**, which is rule 9's first category, and the source
that shows it wrong is the reviewer's own reproduction:

1. The finding reports `Wrong output: []` for a fixture where a side branch adds the marker,
   removes it, and is merged net-zero.
2. That harness was reconstructed **verbatim** — same `fresh()`, `pin()` and `probe()`
   functions, same commands, `probe` invoked with `"."` from inside the repo as written — and
   run against `512126f`, the revision the finding was filed against. It returned the ERROR,
   not `[]`.
3. Independently: a `git merge -s ours` case, which is the canonical shape for
   `--full-history` mattering, gives **byte-identical** `git log` output with and without the
   flag.

The mechanism is visible once measured: `--diff-merges=separate` forces every merge to be
diffed against each parent, and that is what defeats the TREESAME pruning the finding
describes. The pruning is real in general; it is not reachable through this flag set.

**`--full-history` was added for this finding and has been removed.** Keeping a flag on the
strength of a defect that does not reproduce is the exact pattern that has cost this branch
four wrong statements already, and the mutation dropping it survived the suite — which is what
prompted the measurement rather than a plausible explanation.

`test_a_marker_on_a_net_zero_merged_side_branch_is_seen` is kept, with a docstring saying
plainly that it pins nothing that was broken and that it is the evidence for this rejection.

## `--diff-filter=A`: the sequence ends here

Four statements have now been made about one flag. **Three were wrong.**

1. Entry 01: dropping it "changes no verdict." Disproved by round 02.
2. Its replacement: dropping it would lose a real marker, like the other flags. Disproved by
   round 03.
3. Its replacement: a harmless narrowing, kept but not claimed to be needed. Disproved by
   round 04 finding 3 — and by the builder independently, probing the same question before the
   round returned: git reports a symlink becoming a regular file as `T`, which the filter
   discarded before the mode was ever read.
4. What stands: **the flag is gone.** The question it was standing in for is answered without
   it — any record whose DESTINATION mode is a regular file proves the path existed as one
   somewhere in the range, and deletions carry a destination of `000000` and drop out on the
   same test.

Each correction was written to stop the previous overclaim and produced a new one. What broke
the sequence was deleting the thing being described rather than describing it better.

## A guard no mutation reaches, said plainly

The parser skips a combined record (`::...`) rather than reading `parts[1]` as a destination
mode. **`--diff-merges=separate` makes that branch unreachable, so no mutation of it fails the
suite**, and the record says so rather than implying coverage. It is kept because a combined
record whose first source mode happens to be a regular file would otherwise be accepted for
the wrong reason — a silent misread, not an error. Removing it was considered; the NFC fold
was removed on similar grounds in round 02, but that fold was actively wrong on some
filesystems where this guard is merely idle.

## Verification

Outside the sandbox, after these fixes: **889 tests, OK, skipped=1**; `validate.py .` 0 errors
and 8 warnings (the baseline entry 01 declared); `validate.py demo` 0 errors and 2 warnings;
`--diff main` exit 0.

All five of the reviewer's reproductions were built and run against the fixed code. Four now
report the marker where they previously did not; the fifth is finding 1, which reported the
marker before the round as well.

The reviewer confirmed it did not modify the tree and that `git diff --check` was clean, and
relied on the supplied external test result because temporary-directory execution is blocked
in its sandbox.

## Mutations

Six, each reverting one round-04 change literally. Four caught: bare `-m` for
`--diff-merges=separate`, re-adding `--diff-filter=A`, the untyped base check, and accepting
any destination mode as evidence. Two survived, and neither is a coverage gap left standing:
dropping `--full-history` survived **because the flag did nothing**, which is why it is no
longer in the tree; and the combined-record guard, which is unreachable under the explicit
merge-format flag, as recorded above.
