# Round 12 — Codex review

**Reviewed:** `074f752`
**Verdict:** **does not approve** — Standards 1 **Moderate**; Spec 1 **Low** and 1 **Minor**
(the reviewer's own severity words). All three fixed.

**No accepting-direction gap was found.** That is the first time on this branch, and it is the
result worth recording: the reviewer re-ran round 11's coverage matrix against the current rules
and reports every CommonMark block type and the GFM table either terminated by the required
blank line or conservatively refused. Nine rounds found a way to reach the ledger; this one did
not. Every finding below is about the record and the diagnostic being accurate, not about the
guard being wrong.

## Findings

### Standards 1. Moderate — "round 11's prose repair did not reach every mutable site" — FIXED

Two sites, and round 11 claimed to have swept them all. The claim was false.

- **The `"hidden"` ERROR text itself.** It named a code fence, an angle bracket and the blank
  line, so for the header `1. item` the validator refused the file while listing three
  conditions that header already satisfied — a message that tells the author nothing about why.
  It now names all five.
- **The README's account**, which still said "three ways" and "everything else", eight lines
  before recording indented code and lists as the counterexamples that disproved it.

The finding is exactly the failure shape the record names — a claim corrected in some sites and
not all — and it landed on the entry that had just claimed the sweep was complete. **"Every
mutable site is rewritten" was itself the ninth consecutive round's overclaim.** `round-11.md`
is immutable; this entry is its correction.

### Spec 1. Low — "one round-11 mutation measurement is wrong or mislabeled" — FIXED

The reviewer applied the mutation `round-11.md` labels "Rule 4 moved back after the comment
exception" and measured **one** failure where the table records four. **Re-measured here both
ways at `074f752`:**

| Edit | Failures |
|---|---|
| Rule 4 **deleted** — what round 11 actually ran | 4 |
| Rule 4 **moved** after the comment exception — what the label described | 1 |

The count was true of the edit performed and false of the edit described. **This is the second
mislabelled mutation row on this branch** — round 05 had one, round 06 corrected it, and round 11
made the same mistake six entries later. The lesson had been written down as "each row names the
edit literally" and was then not applied. `round-11.md` is immutable; read its row as *"Rule 4
deleted | 4 failures"*, and the moved-after-the-exception mutation is in this round's table with
its own measured count.

### Spec 2. Minor — `_opens_a_container` was not the classifier its docstring claimed — FIXED

Three separate inaccuracies, all in the refusing direction and so none of them a safety gap:

- **Unicode digits.** `rest[i].isdigit()` is true for `١` and `²`, so `١. release notes` was
  refused as a list. CommonMark's ordered markers are one to nine **ASCII** digits. Now
  `rest[i] in "0123456789"`. Both the non-ASCII case and the nine-versus-ten-digit boundary were
  unpinned by any test; they are pinned now, and two mutations confirm it.
- **`* * *`** is a thematic break, not a list item, and is refused as though it were a bullet.
  Left as it is, and documented.
- **The block-quote justification was simply wrong.** The source and
  `docs/known-limitations.md` said a block quote holds blocks across a blank line. It does not —
  CommonMark separates two block quotes with one, so rule 3 already covers it. The refusal is
  kept because one container test is worth more than a second rule about when quoting is safe,
  but it is now recorded as **conservative rather than necessary**. Inventing a hazard to
  justify a refusal is the same defect as overclaiming a protection, in the other direction, and
  it is worth naming as its own shape.

## What the reviewer cleared

The whole safety matrix: thematic break, ATX and setext headings, fenced code, HTML types 1 to
7, link reference definitions, paragraphs, indented code, lists, block quotes and GFM tables all
either terminate at the required blank line or are conservatively refused, with **no false
acceptance**. `_md_indent`'s tab stops in every position tested, and column four as the correct
root-level threshold. Rule 4 running before the comment exception. Both shipped headers opening
no container. The base-anchored protected suffix, the contiguous comparison, the appended-span
boundary, `CHANGELOG_REASONS` failing closed, and `appended_targets` ordering — a fourth
consecutive round clearing those. And all 38 `FOUND_BY_REVIEW` cases reaching the rule their
label implies, with no wrong-reason pass.

It also endorsed the deliberate non-fix: tightening `_changelog_first_entry` would turn a base
holding only an indented or `- - -` "entry" into an entry-less, wholly editable file, and the
limitation is accurately documented.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`. Each row names the edit
literally, and this round both re-ran a row from an earlier entry and recorded what it actually
measures.

| Mutation | Result |
|---|---|
| Ordered-marker digits back to Unicode `isdigit()` | 2 failures |
| Ordered-marker digit limit raised past nine | 1 failure |
| Rule 4 **moved** after the comment exception — the edit round 11's row described | 1 failure |
| Rule 4 **deleted** — the edit round 11's row measured | 4 failures |
| None (restored) | OK, 871 |

## Environment

The reviewer reported the three validator commands matching at `074f752` and
`TestChangelogAppendOnly` passing, but could not reproduce the full suite: 871 tests discovered
with 682 `TemporaryDirectory` errors, its sandbox having no writable temporary directory. It
said so rather than reporting it as a defect. Verified outside the sandbox on `074f752`:
`OK, 871 tests, skipped=1`, unchanged after this round's tests.
