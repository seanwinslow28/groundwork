# Entry 02 — Codex review round

**Reviewed revision:** `ae654cf`
**Verdict, in the reviewer's words:** "Question 1 is not clean. I found 2 Major and 7 Minor
classifier defects." Question 2's 16-cell grid was reported correct; the defects are in the
inputs to that grid, not the grid.
**Brief:** classifier correctness in both directions, plus a completeness audit enumerating
every repository state the new loop can encounter. Framed as classifier correctness rather
than adversarially, per the #32 session's measured finding that adversarial wording killed
two rounds at a provider content filter.

This round is squarely in the finding-class entry 01 named, so **rule 11 does not fire** and
the loop continues.

## Findings

Severity words are the reviewer's own, verbatim.

| # | Severity | What | Disposition |
|---|---|---|---|
| 1 | Major | A marker added by a **merge RESULT** is invisible: `git log --name-only` emits no diff for a merge commit by default. | **Fixed** — `-m` |
| 2 | Major | The whole NUL stream was decoded as strict UTF-8, so **one undecodable pathname erased every marker** in the same output. | **Fixed** — per-path `os.fsdecode` |
| 3 | Minor | `strip("\n")` on `-z`-framed names, wrong in **both** directions: it promoted a file named `"\ngroundwork.pin"` to a marker, and moved a real marker under `"\ndocs/..."` into the skipped `docs/superpowers` path. | **Fixed** — stripping removed |
| 4 | Minor | A marker whose history lives inside an **initialized submodule** is invisible: the superproject records a gitlink. | **Open** |
| 5 | Minor | A **gitlink or symlink-to-directory** named like a marker draws a false deletion — `os.walk` lists it under `dirnames`. | **Fixed** — `os.path.lexists` |
| 6 | Minor | `log.showRoot=false` suppresses an **orphan root commit's** addition. | **Fixed** — `--root` |
| 7 | Minor | **`git replace` / grafts** can make HEAD appear to parent the base and hide the addition. | **Open** |
| 8 | Minor | A marker under an **unreadable directory** is reported deleted while the file is still there. | **Fixed** — no deletion is reported at all when the walk could not read the tree |
| 9 | Minor | **NFC/case aliases**: a still-present marker could be called deleted. | **Fixed** — by `lexists`; see the correction below |
| P1 | Major | Prose in five places claimed committed marker additions are reported, without the limits findings 1, 2 and 6 expose. | **Fixed** |
| P2 | Major | The docstring's claim that dropping `--diff-filter=A` "changes no verdict" is **false** — the merge fixture disproves it. | **Fixed** |

## P2 corrects entry 01, and the correction matters

Entry 01 recorded mutation M8 as surviving "by construction", on the argument that any path
the walk returns which the caller does not filter can only have been created inside the
range. **That argument was wrong**, and the reviewer disproved it with a state rather than an
opinion: on the merge fixture, `--diff-filter=A` is exactly what hides the path, and dropping
the filter would have surfaced the later deletion and changed the verdict. Entry 01 is
immutable, so this entry carries the correction. The docstring sentence that made the claim
has been **removed**, not merely rebutted.

The reviewer was explicitly told M8's survival was disclosed and not to re-raise it, and that
a challenge to the *reasoning* would be a finding. It took that distinction exactly.

## Finding 9's disposition, stated honestly

The first fix for finding 9 folded the comparison to NFC. **No mutation of that fold could be
made to fail**, because `lexists` answers first on this platform. The fold was then removed
rather than kept with a test that did not test it — and on a normalization-SENSITIVE
filesystem it would have been worse than redundant: NFC and NFD are genuinely different files
there, so folding would have suppressed a true deletion. `lexists` is the whole fix.
`test_a_still_present_marker_is_not_called_deleted_by_spelling` pins `lexists` and its
docstring says so.

## Open findings, and why they are open rather than rejected

**Finding 4 (submodule) and finding 7 (`git replace` / grafts) are OPEN.** Neither is
rejected: no closed-list category fits cleanly, and rule 9 says a finding no category fits
stays open rather than being dressed as something else. Both are recorded in
`docs/known-limitations.md` as things the walk does not see. Whether either should be built
is a maintainer decision, put under rule 5 with the recommendation to document rather than
fix — finding 4 needs a second mechanism (a `git log` per initialized submodule), and
finding 7's one-flag fix (`--no-replace-objects`) would make this read follow a different
history from `_git_diff_context`'s base-tree read in the same run.

## Verification the reviewer could not do

The brief warned that the sandbox often cannot create temporary directories. Run outside it,
on the state after these fixes: **881 tests, OK, skipped=1**. `validate.py .` 0 errors and 8
warnings (the baseline entry 01 declared), `validate.py demo` 0 errors and 2 warnings,
`--diff main` exit 0.

Two of the reviewer's reproductions could not be built as written on this machine, and were
rebuilt rather than skipped:

- The **non-UTF-8 pathname**: APFS and HFS+ reject a filename that is not valid UTF-8. The
  test puts the same bytes into git's **index** with `update-index --cacheinfo`, so the bytes
  reach `git log`'s output — which is what the helper actually reads — without ever existing
  on disk.
- The **`chmod 000`** case is skipped when running as root, which ignores directory
  permissions.

## Mutations

Seven, one per fix, each reverting that fix literally and running the whole suite. Six were
caught. The seventh is the NFC fold described above, which is why it is no longer in the
tree. The mutation rows for the pre-round-02 code are in entry 01; the M8 row there stands as
written, with its **reasoning** corrected by P2 above.
