# Entry 03 — Codex review round

**Reviewed revision:** `cfb0c20`
**Verdict, in the reviewer's words:** "The round is not clean. I found 2 classifier
defects—1 Major and 1 Minor—and 3 Minor prose defects."
**Brief:** audit round 02's seven repairs first — asking of each not only whether it closed
the state it was for but whether it **opened a new one** — then the same classifier-correctness
and completeness questions on the changed code.

Still in the finding-class entry 01 named, so **rule 11 does not fire**.

## The repair audit, which is why this round was worth running

The reviewer confirmed five of the seven round-02 repairs closed their state and changed no
verdict they should not have: `-m`, `--root`, per-path `os.fsdecode`, the removal of
`strip()`, and the removal of the NFC fold. **Two of the repairs introduced new defects**, and
both are below. Asking "does this repair over-correct?" is what surfaced them; a round that
only re-asked the original question would have missed both.

## Findings

Severity words are the reviewer's own, verbatim.

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Major | **Pathname presence is not marker presence.** Both the walk and the `lexists` guard were type-blind, and it broke in both directions: a real marker deleted and replaced by a **directory** of the same name still "exists", so the deletion was hidden; and a **gitlink or symlink-to-directory** named like a marker counted as evidence a governed root had existed, so removing it drew a false ERROR. | **Fixed** — `--raw` carries the mode and only `100644`/`100755` is evidence; the presence proof is `isfile`, not `lexists` |
| 2 | Minor | **One unrelated unreadable directory suppressed every deletion.** Round 02's repair for its own finding 8 returned early whenever any directory was unreadable, blinding candidates whose absence was independently provable. | **Fixed** — suppression scoped to candidates under an unreadable prefix |
| P1 | Minor | The docstring's umbrella claim that every flag was measured such that dropping it would "lose a real marker or invent one" is **false for `--diff-filter=A`**. | **Fixed** |
| P2 | Minor | `docs/known-limitations.md` credited round 02 with finding "all four" limits; it found two, and the other two were already disclosed. | **Fixed** |
| P3 | Minor | Entry 01 says "The walk reads committed history" without qualification. | **Corrected here** — see below |

## Finding 1 reintroduced the escape this slice exists to close

Worth saying plainly rather than leaving in a table. The under-refusing half of finding 1 is
not a new edge: it is **issue #40's own escape**, reachable again through a repair made for
round 02. Delete the pin, `mkdir groundwork.pin`, and the check that was built to notice a
deleted pin went quiet. That is the second time on this branch that a fix for a narrow case
widened a hole somewhere else, and it is the argument for auditing repairs rather than only
re-asking the original question.

## P1: the third wrong statement about `--diff-filter=A`

The record must carry this because it is a pattern, not a slip. Three statements have now been
made about that one flag and the first two were wrong:

1. Entry 01: dropping it "changes no verdict." **Disproved by round 02.**
2. The sentence that replaced it swept the flag into the same "dropping it loses a real marker
   or invents one" clause as `-m`, `--root` and `--no-renames`. **Disproved by round 03** —
   dropping it still recovers a marker in the merge fixture's shape, and the mutation still
   survives the suite.
3. What the docstring says now: it is a **narrowing**, kept because `-m` and `--root` make the
   additions visible on their own, and **not** because anything measured shows it is needed.

Each correction was written to stop the previous overclaim and produced a new one. The third
version claims less than the code does rather than more, which is the only direction that
stops the sequence.

## P3 corrects entry 01

Entry 01's residual-limit paragraph says "The walk reads committed history." That is broader
than the truth: it reads what this repository's configured `git log` will show it, which
rounds 02 and 03 narrowed four separate ways (merge diffs, `log.showRoot`, replacement
objects, submodule gitlinks). Entry 01 is immutable, so the correction lives here.
`docs/known-limitations.md` carries the accurate statement.

## The two open findings from entry 02, now decided

**Both are documented rather than fixed**, decided by the maintainer 2026-08-30 under rule 5.
Neither is rejected — no closed-list category fits, and rule 9 keeps such a finding open
rather than dressing it as something else. Both are recorded in `docs/known-limitations.md`
and each now has an issue so the work is not lost:

- **Entry 02 finding 4** (a marker inside an initialized submodule) → issue #41.
- **Entry 02 finding 7** (`git replace` / grafts) → issue #42.

The maintainer's grounds, recorded: finding 4 needs a second mechanism — a `git log` per
initialized submodule, with its own states to get right — which is what rule 10 exists to
route to an issue rather than into a slice. Finding 7's one-flag fix would make this walk
follow a different history from `_git_diff_context`'s base-tree read **in the same run**, and
two histories behind one verdict is worse than a stated limit; the coherent version is a
repo-wide policy, which is issue #42.

## Verification

Outside the sandbox, on the state after these fixes: **884 tests, OK, skipped=1**;
`validate.py .` 0 errors and 8 warnings (the baseline entry 01 declared); `validate.py demo`
0 errors and 2 warnings; `--diff main` exit 0.

The reviewer stated it did not run the suite in its sandbox and relied on the supplied
external verification and direct inspection. That is the expected environmental limit, and it
is why the numbers above are measured here rather than quoted from the round.

## Mutations

Four, each reverting one round-03 fix literally, each run against the whole suite. All four
were caught: `--raw` back to `--name-only`, `isfile` back to `lexists`, the unreadable
suppression back to global, and accepting gitlink and symlink modes as marker evidence.
