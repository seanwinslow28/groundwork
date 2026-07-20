# Resume trace — reopening in Cursor, mid-turn 3

> The test the ticket asks for: "what a resume-from-Cursor-after-starting-in-Claude-
> Code actually feels like against each." Fresh agent, zero memory. It must recover:
> **(1) where are we, (2) what's locked, (3) what's a guess, (4) what to ask next.**

---

## Shape A — one resumable state file

**What the agent reads:** `interview-state.md` (the whole thing, every turn).

**Resume feels like:** open one file, top-to-bottom. The `## Resume header` +
`phase:` + `open_question_id:` front-load the "where are we." Confirmed vs provisional
are two labelled sections. It reconstructs in one read, no traversal.

- ✅ Single read, single pointer. Nothing to stitch.
- ✅ Confirmed/provisional/open-question all visible at once.
- ⚠️ "What's locked" is a **claim inside the file**, not enforced. A resuming agent
  (or a fumbled edit) can silently rewrite a confirmed fact — the format trusts prose.
- ⚠️ The file **reloads in full every turn** and grows unbounded → the exact
  context-budget pressure #13 warns about; by layer 8 the boot cost is the transcript.
- ⚠️ Harness switch survives, but the **audit trail is only the transcript digest** —
  self-reported. "Sasha approved scope in Claude Code" is a line the agent wrote, not
  a fact you can verify.

## Shape B — per-phase checkpoint artifacts

**What the agent reads:** `00-manifest.md` (small, fixed size) → then only the files
it needs. Confirmed context = frozen layer files. In-flight = `_working.md`.

**Resume feels like:** read the manifest (pointer + table), see phase `cs-renewal` /
status `awaiting-answer`, open `_working.md` for the one open question. Confirmed
layers are there if needed but don't have to be re-read to continue.

- ✅ **"What's locked" is enforced by git, not by trust.** `git log` = the approval
  trail (each confirmed layer is its own commit); `git status` = the dirty `_working.md`
  is exactly what's provisional. This is #10's "checkpoint = commit" falling out for free.
  Real output from the throwaway repo:
  ```
  6a4c620  interview(cs-renewal): confirmed — renewal-prep steps, Motion=assist
  acae6a8  interview(scope): confirmed — functions + top pain
   A interview/_working.md          # in flight, not yet a checkpoint
  ```
- ✅ **Bounded resume cost.** Manifest is fixed-size; the agent pulls only relevant
  layers. Boot cost doesn't grow with interview length. Friendly to #13's budget check.
- ✅ **Confirmed = frozen file = immutable**, matching #7's "frozen at commit" instinct
  and the never-edit/only-supersede doctrine. Rewriting a confirmed layer shows up as a
  diff on a committed file — catchable by a `--diff` guard, same mechanic as #7.
- ⚠️ More files + a promote step (`_working.md` → `03-*.md` + commit) = more ceremony
  and more for the validator to check (manifest/file drift, orphan working files).
- ⚠️ The pointer (manifest) and the reality (files + git) can disagree if a turn
  half-commits — a new drift surface Shape A doesn't have.

---

## The crux

Both survive the harness switch. The real split is **what carries the "confirmed"
guarantee**:

- **Shape A** encodes confirmed-vs-provisional as *labels the agent promises to
  respect*. Simple, one read — but the guarantee is only as good as the next agent's
  discipline, and it fights #13 on boot cost.
- **Shape B** encodes it as *git structure*: confirmed = committed & frozen,
  provisional = the dirty working file. The guarantee is mechanical and auditable, it's
  already what #10 said the substrate is, and it stays inside #13's budget — at the
  cost of more files and a promote/commit step each layer.

Confirmed-vs-provisional (both shapes, same vocabulary as #7): **confirmed** = approved
at a checkpoint; **inferred/observed** = agent's, unconfirmed. #7's provenance enum is
reused rather than a parallel one invented.
