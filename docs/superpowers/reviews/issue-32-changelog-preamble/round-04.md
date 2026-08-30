# Round 04 — Codex review

**Reviewed:** `206a78a`
**Verdict:** **does not approve** — Standards 4 findings, worst **Moderate**; Spec 5 findings,
worst **Major** (the reviewer's own severity words).

The round did what round 03 was cut off before doing, and it found that round 02's repair was
the wrong shape: it special-cased one construct where the rule needed to be general.

## Findings

### Spec 1. Major — "an unclosed fence bypasses the repair" — FIXED
### Spec 2. Major — "concrete raw-HTML false negative" — FIXED

The same defect twice, and both **measured on `206a78a` before acting** — each returned
`reason=None` where the ERROR was owed:

| Construction | verdict before the fix |
|---|---|
| open a code fence in the header, close it after the ledger, append a replacement entry | accepted |
| the same with `<script>` … `</script>` | accepted |

Round 02's repair refused a header that left an **HTML comment** open. That was the construct
in front of it, and treating it as the category was the error: any construct that runs until a
closer does the same job. The fence re-renders the committed ledger as code while the
replacement entry renders as the live list; `<script>` makes the ledger script content and
shows the reader the replacement alone.

**Fixed by generalising, not by adding two more cases.** `_changelog_header_leaves_a_block_open`
replaces `_changelog_header_leaves_a_comment_open` and asks one question: does the header open
a block construct it does not close? The list is CommonMark's HTML block types 1 to 5 —
comment, CDATA, processing instruction, and the `script` / `style` / `pre` / `textarea` raw
blocks — plus fenced code, counted by line parity. It is a fixed list and
`docs/known-limitations.md` now says so in those words, because the list is the honest
boundary: a construct outside it is not modelled.

### Spec 3. Low — "harmless inline-code text is rejected" — FIXED

A header reading ``The token `<!--` denotes a comment.`` returned `"hidden"`. Verified. Beyond
being a false positive it was a usability defect with no way out: a changelog header could not
document the syntax it is written in. `_strip_inline_code` now drops matched backtick-delimited
spans before the scan. An **unmatched** run is deliberately left in place, because stripping it
would turn a bare fence line into prose — that asymmetry has its own test and its own mutation.

### Spec 4. Low — "`<!-->` is classified incorrectly" — FIXED

Verified: `<!-->` returned `True` (open) and `<!---->` returned `False`. CommonMark treats
`<!-->` and `<!--->` as complete comments; the closer overlaps the opener, and the search began
four characters in. It now begins two characters in for the comment pair only, with the reason
in a comment at the line. `<!----` remains correctly open.

### Spec 5 / Standards 3. Low — "the rule map omits the new header ERROR" — FIXED

Reported on both axes as the same documentation defect, and it was one. The
`blast_radius_diff_findings` severity cell now names the header case alongside the
protected-region edit and the deletion.

### Standards 1. Moderate — "the engine changelog claims enforcement that is dormant" — FIXED

`governance/changelog.md` said the `validate --diff` mode enforces entry immutability "at PR
time". The engine root carries no `groundwork.pin`, so that mode never reaches the engine's own
changelog — a fact this branch's README states about itself and then contradicted two files
away. This is the shape the previous slice measured nine times: **a replacement for an
overclaim reaching past what it can support.** The sentence now says the mode enforces it in a
governed root, that this repository carries no pin, and that review is what protects the file
here.

### Standards 2. Moderate — "replacement prose still makes the false 'only way' claim" — FIXED,
and it corrects an entry that cannot be edited

The reviewer is right, and this is the same failure shape again, one round later. Round 02's
repair claimed an unclosed comment was **the one way** the editable header could reach content
it does not own, and `round-02.md` says the repair "closes the one that hides it". Spec 1 and
Spec 2 disprove both.

The docstring carried the claim and no longer does. `round-02.md` is **immutable under rule 9**,
so this entry is the correction: **where round-02.md says an open HTML comment is the one way
the editable header can reach the ledger, and that the repair closes the one construct that
hides it, both are wrong.** An unclosed code fence and an unclosed raw-HTML block do it too,
and the fix in this round is a rule about block constructs rather than a rule about comments.

### Standards 4. Low — "the durable inventory contains two wrong counts" — FIXED

Both counts verified wrong: `docs/known-limitations.md` gained four entries and the README said
three; the branch adds four new helpers and the README said three. Neither was corrected to a
new number. **A count that has been wrong once is withdrawn, not re-counted** — that is what
worked in the previous slice, where three corrected counts were wrong three times. The rows now
name what was added, and the helper claim names a command the reader can run instead of a
figure they have to trust.

## The reviewer's non-findings, which are worth keeping

It checked and cleared, without raising: nested `<!--` handling; that a `-->` met while a
comment is open closes it and the apparent fence in between is not parsed as one; CRLF
normalization; that an opener sitting after the base's first entry is inside the protected
region and outside this predicate, a state the branch neither creates nor repairs; that every
production caller and test uses the `(reason, appended_lines)` contract, with known reasons
paired to an empty span and an unknown reason failing closed; that no pre-existing occurrence
of a base entry can enter the appended span; that the pre-#32 guard did refuse round 02's
construction, which `round-02.md` asserts; and that round 03's account of its own failure
matches. It found no revisionless source-line citation in the branch's additions.

## Mutations added this round

Applied alone, suite run, file restored, `PYTHONDONTWRITEBYTECODE=1`.

| Mutation | Result |
|---|---|
| Fence parity check removed | 1 failure |
| Raw-HTML pair list reduced to the comment | 1 failure |
| Comment closer searched from four characters in, not two | 1 failure |
| Inline-code stripping removed | 2 failures |
| Unmatched backtick run dropped rather than kept | 2 failures |
| None (restored) | OK, 876 |

## Environment

The reviewer reported 868 tests discovered with 682 `TemporaryDirectory` setup errors from a
sandbox with no writable temporary directory, and correctly called it environmental. Verified
outside the sandbox on `206a78a`: `OK, 868 tests, skipped=1`. After this round's tests the
suite is `OK, 876, skipped=1`.
