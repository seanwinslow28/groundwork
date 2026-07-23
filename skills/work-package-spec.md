# Skills as work packages

A groundwork skill is never a bare `SKILL.md`. Copying a SKILL.md alone fails across harnesses — loading rules differ, hooks become prose, sub-agents don't exist, MCP configs vanish (§6). So every generated skill ships as a **work package**: a directory `skills/<name>/` (engine exemplars) — or `.agents/skills/<name>/` with a `.claude/skills/<name>` symlink when delivered to a company (#19) — containing:

- **`SKILL.md`** — the skill core, with frontmatter:
  - `name` — the skill's directory name.
  - `description` — the **selection surface**, reviewed like landing-page copy: outcome-oriented and **non-overlapping** with other skills (agents mis-select at 30+ overlapping tools). One outcome, stated plainly.
  - `action_class` — one of `read-only` / `reversible-write` / `external-side-effect` / `high-risk` (§5.3). Declared everywhere; enforced by hooks where the harness supports them, by review gates where it doesn't.
  - `provisioned` — `yes` once the skill is live for a company; `no` while drafting. The validator's card strictness follows this flag.
  - `ontology` — the path to the ontology deep record this skill was generated for (referential-integrity- and drift-checked).
- **Harness requirements** — the tools, permissions, scripts, and connectors the skill needs to run.
- **Compatibility notes** — "tested in X; here is what breaks in Y." Honesty as a feature. Seeds the card's `known_failure_modes`.
- **A Memory row** — what the skill may **read** from org memory, **write** back, or keep **run-only** (required now that harnesses write memory by default; the constitution must say what agents may persist).
- **`owner-card.md`** — the Owner's Card (below). The owner lives here, not in the skill body.

The one-question test ships with every package: *"if I had to move this skill tomorrow, what would break?"*

## The Owner's Card

Human-owned accountability. Required-ness of a field is a property of the skill's **action class**, atop a spine no card may lack (#6). The generator **refuses** to invent the owner, the forbidden actions, and the death conditions — those come only from a human's interview answers.

**Always required (the spine), every card:**
`owner`, `backup_owner`, `job` (one sentence), `allowed_actions`, `proposed_only_actions`, `forbidden_actions`, `pause_condition`, `retirement_condition`, `source_of_truth`, `review_cadence`, `known_failure_modes` (a truthful "none observed yet" passes; blank does not), `last_reviewed`, `next_review`, `success_standard`.

**Required at `external-side-effect` / `high-risk` (review track 2); a WARN below:**
`evidence_required`, `sources_must_not_use`, `review_sample` — exactly what a track-2 reviewer physically needs.

**Optional, silent:** `users`, `other_allowed_sources`.

**Generator drafts (human confirms at PR review):** `job`, `source_of_truth`, `review_cadence`, `success_standard` (from the captured baseline), `last_reviewed`/`next_review`, `allowed_actions` + `proposed_only_actions` (observable from the skill just written), `owner` (surfaced from the ontology's accountability owner — drift-checked), and seeded `known_failure_modes` (from the compatibility notes).

**Interview must ask a human (per provisioned skill):** `backup_owner`, `forbidden_actions`, `pause_condition`, `retirement_condition`. These never appear in generator template output.

Doctrine: *shared use is fine; shared responsibility is often no responsibility* — and *some agents should die* (the death conditions are only meaningful because a human named the trigger).
