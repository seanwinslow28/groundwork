## Round 2 — 2026-08-29, task-mteadhof-nhr8en, verdict: does not approve (6 findings)

Reviewed: `5a71138` (the round-1 fixes). All 6 accepted; five fixed in the following
commit, one extended. **Three of round 1's five "fixed" dispositions were wrong or
incomplete**, and one of them changed a maintainer decision without asking — the failure
this session's kickoff named explicitly. Round-1 rows 1, 2, 4 and 5 are **amended** by
rows 1, 2, 4 and 6 below, and round 1's own prose summary is corrected by row 5.

| # | Sev | Finding (compressed) | Verdict | Disposition |
|---|---|---|---|---|
| 1 | major | Renaming the base from the approved "the generation commit" to "the commit that creates the governed root — the one adding `groundwork.pin`" is a substantive narrowing, not an operational definition, and the multi-commit fallback it carried is an unapproved governance policy: with the pin first, every later generated rule and skill escalates, which contradicts this section's own rationale and requires a pending-proposal state the roles design records as impossible | CONFIRMED | Fixed by reverting to the approved words. The base is "the generation commit — the one you wrote the OS in", and the multi-commit policy is gone. Round 1's finding — that the term is undefined and `generate.md` has no commit step — therefore stands **unfixed and escalated**, not resolved. It is open item 4 below. Amends round-1 row 1, whose "fixed" was an unapproved change |
| 2 | major | "A change touching neither exercises neither" is still false: the same invocation runs `interview_diff_findings`, so editing or deleting a confirmed layer exercises the frozen-layer guard while touching neither a new rule/skill nor a memory record; modifications to existing rules and skills and changelog rewrites are further counterexamples | CONFIRMED | Fixed: the false universal is gone. The sentence now names three cases without closing the set — new rule or skill (#18), editing or deleting a confirmed layer (frozen layers), and memory immutability needing a record present at the base. Amends round-1 row 2, whose "verified independently" did not cover the third pass |
| 3 | major | The pin bullet's pointer, "what the root-creating commit is itself measured against", inverts the model — that commit is passed **as the base**, so its tree is excluded from the comparison rather than measured; the two descriptions conflict on the core S2 requirement | CONFIRMED | Fixed: the pointer now reads "which commit the gate measures *from*, and why the write order inside it does not change what the gate sees" |
| 4 | minor | "With nothing in the tree the base does not already hold" rules out additions by pathname only; a base file deleted from the tree, or retained with changed contents, still gives the passes something to find | CONFIRMED | Fixed: the condition is now the working tree matching the base for every file either side holds. Amends round-1 row 5 |
| 5 | major | This log overclaims: rows 1, 2 and 5 were called fixed when their replacements were wrong; the prose said "four fixed … two not changed" while the table marks five rows fixed and one not; and "the error text quoted verbatim" is false — neither the log nor `generate.md` quotes the validator's wording, and the S2 source's shortened form is not the current text | CONFIRMED | Corrected here by supersession, round 1's table left as written. The count: round 1 was **five rows fixed, one row not changed** — row 4 alone, and it carries two maintainer items, which is what the prose miscounted. The verbatim claim is withdrawn: the reviewer checked the error text against the validator's output; `generate.md` paraphrases it and quotes nothing |
| 6 | minor | Open item 2 named only `README.md:123`, omitting `delivery/README.md:238`, which gives the same company-repo `--diff main` command and promises exit 0 — and the removed "Later runs" paragraph had cited both, so it was not a discovery failure | CONFIRMED | Fixed: open item 2 now names both sites. Amends round-1 row 4's inventory |

Verified clean by the round, and reported as such: the measurement reproduces exactly —
`--diff 8af5680` gives 2 errors / 5 warnings / exit 1, one error per rule, and
`--diff ab9e9bd` gives 0 / exit 0, with exactly two committed files under
`governance/constitution/`. `_pin_dirs` does exactly *discover* pin pathnames from both
sides, so row 6 of round 1 was right. Preconditions 2–3 plus `protocol.md:11` establish
the same-repo committed history. Removing the "Later runs" paragraph was correct — it
asserted an ancestry guarantee the validator does not enforce — and the resulting silence
about later bases is fairly recorded as open item 3. The header's landing-order claim is
accurate. All four gates matched: `validate.py .` 0 errors / 7 warnings, `--diff main`
exit 0, `demo` 0 errors / 2 warnings, 709 tests OK (skipped=1).

One observation the round recorded without raising it as a finding: `proposals/` in the
generated OS contains a `README.md`, so it holds no pending proposal but is not literally
empty — the pre-existing C8 distinction. `generate.md`'s "empty at generation" is its own
existing wording, unchanged by this branch.

### Open maintainer items after this round

Items 1–3 stand as recorded in round 1, with item 2 extended:

1. **`CONTEXT.md`'s consent-gate entry and the root-creating commit.** Unchanged. The
   glossary says every escalating change reaches the main line through a proposal; this
   branch exempts the root-creating commit. Decision 8 supports reading generation as the
   baseline rather than an exception, but the glossary does not express that reading.
2. **`README.md:127` *and* `delivery/README.md:244`.** Both give a company repo
   `--diff main`, and `delivery/` promises exit 0. Both are correct once the generation
   commit is on `main` and both reproduce S2 while generation sits on an unmerged branch.
3. **The base contract for later runs.** The validator requires only that the ref
   resolves; nothing enforces that a base contains the generated root.
4. **What "the generation commit" means when generation is not one commit** (new, row 1).
   `generate.md` contains no commit step at all, so the approved words name a commit the
   document never tells anyone to make. The options are: say generation lands as a single
   commit; define the base as the commit that creates the governed root and accept the
   multi-commit governance consequences; or leave it, since the ordinary case is
   unambiguous. This was decided unilaterally in `5a71138` and is now reverted to the
   approved wording pending the maintainer's call.
