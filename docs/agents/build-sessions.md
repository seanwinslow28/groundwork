# Build-session rules (groundwork build phase)

> Replaces the wayfinder charting rules now that the map is complete. These are workbench rules for build sessions; they are NOT product content and never ship to adopters.

## Session shape
1. **One increment per session.** Build it, `validate` green, Codex-review, record what it revealed, stop. The pull to keep going is the signal to stop.
2. **One increment ends green:** `python3 scripts/validate.py` passes (zero ERRORs) before a session is done.
3. **Review gate:** Fable 5 builds; the Codex plugin reviews at session end (`/codex` review or `codex:codex-rescue`); the maintainer (Sean) lands the merge — the commit bit is the governance teeth (#18). Rule 9 governs the record those rounds must leave.
4. **Claim before work:** branch before touching the tree (never build on `main`).

## Standing rules (carried from charting)
5. **Explain before Sean decides.** Before each decision he owns, explain in plain terms: what it is, the options, the recommendation, and the honest counter-argument. Never accept "go with your recommendation" as a substitute for understanding.
6. **Honesty rules:** claims match what is verified/built; no capability claim precedes the capability; overclaiming is trust debt.
7. **Source of truth:** the approved design brief and CONTEXT.md (the resolved-decision glossary). Locked decisions are not reopened without new evidence.
8. **Pre-made text is not pre-verified.** A plan's pre-made replacement text carries a
   source citation for every factual claim, and the executor verifies those claims against
   that source *before* transcribing. Transcription fidelity protects the wording a review
   approved; it does not make the claims true, and "the plan said so" is not a basis. Where
   the source is another record, check that record against *its* sources too — one of the
   2026-08-01 slice's four factual defects was inherited from a run record that was itself
   wrong. Codex review caught three on the branch, before `main`'s product files carried
   them; the fourth surfaced only after the slice had merged, and it did reach `main`'s
   roadmap. Assume the ones you have not found yet are already shipped.

## Standing rules (added during build)
9. **Durable review verdicts.** A slice may not merge unless the verdicts of every Codex
   review round run against it are committed in the repository. **This is the operative
   text.** Decision 7 of the 2026-08-28 roles-as-the-accountable-unit design, under
   `docs/superpowers/specs/`, records the decision, its evidence and its counter-argument.

   **Where.** One directory per branch, one file per entry: `docs/superpowers/reviews/<slug>/`,
   or `docs/superpowers/plans/<slice>-reviews/` when the branch carries exactly one plan,
   where `<slice>` is that plan's filename with the leading `YYYY-MM-DD-` and the `.md`
   removed. `<slug>` is the branch name's last path component, lowercased, with every
   character outside `[a-z0-9._-]` replaced by `-`; if a directory of that name already
   exists in the merge target, append `-2`, `-3`. That mapping is deliberately not
   injective — the directory's `README.md` records the full branch name, which is what
   disambiguates. A collision found only at merge time is resolved by renaming the
   directory, which is not an edit to any entry.

   **Entries.** `round-NN.md`, numbered consecutively from 01. Every Codex invocation gets
   one, a crashed or abandoned one included — that entry records the task id and that no
   verdict was returned. A directory may also carry a numbered entry that is not a review
   round, such as a record of maintainer decisions; it says so on its first line. Nothing
   outside the repository enforces that no invocation was omitted, so the numbering is a
   record, not a guarantee.

   **An entry is immutable once committed.** A correction to an earlier entry is made by a
   later one, never by editing it.

   **What a round entry carries.** The reviewed revision as a commit SHA — a review runs
   against a clean worktree — the verdict, and every finding with the reviewer's own
   severity word kept verbatim, plus its disposition. A finding may be summarised rather
   than quoted in full. A disposition is **fixed** or **rejected with grounds**, and nothing
   else. Grounds say the finding is factually wrong, naming the source; out of scope, naming
   the scope and the follow-up work it becomes; or superseded, naming what supersedes it.
   A finding that is neither fixed nor rejected is unresolved, and a branch carrying an
   unresolved finding does not merge. The builder may reject a finding; every rejected one
   is also listed in the directory's `README.md`, so the single move that closes a finding
   by disagreeing with it cannot be buried inside an entry.

   **`README.md` carries what keeps changing** — the full branch name, a row per entry, the
   commit that carried each round's fixes, the rejected findings, and any open items. An
   entry cannot name the commit that fixes it, since that commit does not exist when the
   entry is written; the README's map is where that SHA lives. The README records; it never
   changes a disposition.

   **The terminal round.** The last verdict is committed after the state it reviewed, so
   that commit is not itself reviewed. That is accepted, and said here rather than exempted.
   The final verdict must be approving. A maintainer may merge over a non-approving one, and
   doing so **is** a rejection with grounds of whatever findings remain: the grounds go in
   the merge commit, as `5fc61c6` did for slice 2.1, and those findings are listed in the
   README like any other rejection.

   *Evidence:* the session that landed rule 8 ran twenty-five review rounds and kept no round
   output; three of its sixteen groundwork rounds left no numbered fix commit, and two of
   those left nothing anywhere. Decision 7 carries the full account.
   *Worked example:* `docs/superpowers/reviews/spec-roles-accountable-unit.md` — 25 rounds,
   102 findings, every disposition, one approving verdict, with its fix-commit map
   backfilled. It predates the per-entry layout above, which binds work started after this
   rule lands.

## Where the plan lives
- Design: `docs/superpowers/specs/2026-07-22-groundwork-v1-build-sequence-design.md`
- Plans: `docs/superpowers/plans/` (this file's siblings), one per phase-slice.
- **Loading:** these rules are no longer auto-loaded — `CLAUDE.md` is now the one-line `@AGENTS.md` import (D2 Move 2). Build sessions load this file by being pointed at it in the session kickoff; `AGENTS.md` links it under "Working on groundwork itself".
