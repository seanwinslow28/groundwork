# groundwork

The ubiquitous language of the Company OS being charted here — terms are added as wayfinder tickets resolve them, so this glossary grows with the map.

## Language

### Ontology (schema tiers — ticket #5)

**Executive view**:
The top tier of a function's ontology: every activity, carrying only its name and Direction. Legible and presentable to leadership; never demands deep fields.
_Avoid_: overview, summary tier

**Acted-on activity**:
An activity the adopter has selected to act on, which is what triggers deep-field requirements. Required-ness is a property of this status (plus Motion), never of a field alone.
_Avoid_: selected, prioritized, active

**Common core**:
The fields every acted-on activity must carry regardless of Motion: the Motion verdict with its five scores, Work type, and the accountability owner-half.

**Automation path**:
An acted-on activity whose Motion is automate or build — the only path that additionally requires Substrate, Shape, and the Describability Gate.

**Describability Gate**:
The eight-part precondition (inputs, output, standard, source of truth, exception path, error cost, owner, review gate) an automation-path activity must pass before a skill is generated for it. All eight must be *answered* — a truthful "none" is an answer; "N/A" is not — and there is no waiver mechanism.
_Avoid_: checklist, waiverable gate

**Provisioning gate**:
A requirement enforced when a skill ships rather than at interview time. The captured baseline is the canonical example: no skill provisions for an activity without one.

**Machinery-follows enforcement**:
The validator doctrine from ticket #5: ERROR exactly when a field is about to back (or already backs) a running agent, WARN on incomplete thinking about acted-on activities, silence on untouched worksheets.
_Avoid_: strict mode, completeness check

**Depth doctrine**:
"Depth is earned by acting, not by planning to act" — the interview steers the first run to 3–5 acted-on activities; the cap is doctrine, not a validator rule.

### Owner's Card (field tiers — ticket #6)

**Card spine**:
The human-owned accountability fields every Owner's Card requires regardless of action class: owner, backup owner, job-in-one-sentence, the three action-class lines (allowed / proposed-only / forbidden), and the death conditions.
_Avoid_: core fields, minimal card

**Track-2 trio**:
Evidence required, sources-it-must-not-use, and review sample — required exactly when the skill's action class is external-side-effect or high-risk (review track 2); a visible warning below that.

**Death conditions**:
An Owner's Card's pause condition and retirement condition. Always human-answered — "some agents should die" only means something if a human named the trigger.
_Avoid_: shutdown criteria, sunset (sunset dates belong to rules)

**Generator refusal**:
The doctrine that the generator never invents an owner, a forbidden action, or a death condition — it drafts only what it can observe from the ontology and the skill it wrote; the refused fields come solely from a human's interview answers.
_Avoid_: manual fields, human override

### Improvement proposals (three-bucket routing — ticket #17)

**Improvement proposal**:
An agent-authored proposed change to a skill or a constitution rule — the only two artifact kinds the three buckets route. Memory records, Owner's Cards, and ontology worksheets keep their own governance; a memory enters this routing only at the moment it graduates into a proposed rule/skill change.
_Avoid_: suggestion, self-improvement (the ungated kind is banned)

**Blast-radius boundary**:
The auto-apply test: a proposal auto-applies exactly when a bad version's worst case is bounded — a body-only edit to a track-1 (read-only / reversible-write) skill. Anything touching the description, governance frontmatter, or Owner's Card, or any change to a track-2 skill or a rule, escalates.
_Avoid_: low-risk (undefined on its own), trivial change

**Proposal schema**:
The completeness checklist a proposal must carry — diff, reason, evidence links, blast-radius declaration. Mechanically splits needs-sign-off (complete → draft PR; the PR is the review file) from needs-more-context (incomplete).
_Avoid_: confidence threshold

**Proposal demotion**:
Routing an incomplete proposal back down the promotion path to an org-memory working note with its gaps named; it re-enters as a proposal when the gaps fill, inheriting the memory schema's `review_by` anti-rot.
_Avoid_: rejection (a verdict), pending queue

**Governance changelog**:
The central append-only index of auto-applied changes — one line per entry pointing at its commit (index, not store) — scanned in the maintainer's reconciliation pass. The accountability half of "auto-apply with changelog."
_Avoid_: audit log (implies an engine), "git history is the changelog"

### Version skew (engine-vs-content pin — ticket #21)

**Schema version**:
The single coarse integer the engine carries, bumped **only** on a breaking schema change. The unit skew is measured in — never commits or days. The content's pin records the `schema_version` it was generated against; skew = engine's minus content's.
_Avoid_: version number (ambiguous with the groundwork commit/release), semver

**Pull promise**:
The guarantee that `git pull` on the engine never ERRORs content for merely being old. A new requirement WARNs ("new since your pin"); a sharper-eyes check keeps its severity; a breaking change becomes one migration gate. Keeps pulling upstream safe, which the two-repo model depends on.
_Avoid_: backward compatibility, forward compatibility

**Sharper-eyes check**:
A check whose schema is unchanged but which now catches a problem that was *always* invalid (e.g. a looping supersession chain). Keeps its declared severity, including ERROR, on old content — the content was genuinely broken all along, so surfacing it is honest, not a new requirement.
_Avoid_: stricter check, new rule (conflates with new-requirement)

**New-requirement demotion**:
The rule that a check asserting a field/shape introduced *after* the pin cannot ERROR pre-pin content — it WARNs, labeled "new since your pin." The mechanism is each check carrying a `since:` schema-version compared against the pin.
_Avoid_: grandfathering, soft-fail

**Migration gate**:
What the validator emits at skew ≥ 1 — a single migration-boundary ERROR ("content is v3, engine is v4; see MIGRATIONS for v3→v4") instead of scattered field errors. **Max skew is one breaking version.** The V1 contract is a guaranteed `MIGRATIONS.md` note plus precise validator finger-pointing; a transform script is a bonus, and full re-interview is V3.
_Avoid_: upgrade wall, hard block

**Version pin**:
The dedicated company-repo-root file (independent of `interview/`) recording `schema_version` (what skew compares) and `generated_by_commit` (provenance only — never used for skew math). The one piece of data the whole skew policy reads.
_Avoid_: lockfile, manifest (that is #9's interview manifest)

### Consent gate (per-harness proposal mechanics — ticket #18)

**Consent gate**:
The harness-independent invariant behind governed self-improvement: an *escalating* change reaches the main line only via a reviewable proposal artifact plus a distinct human affirmative act, leaving a git record. The "rung-5, human-owned decision" made mechanical. A GitHub draft PR is one *rendering* of it, never the gate itself.
_Avoid_: draft PR (a rendering, not the gate), approval workflow (implies an engine)

**Consent ladder**:
The graceful degradation of *how* the proposal file is reviewed-and-applied, richest to floor: GitHub **draft PR** → `proposal/*` **branch-merge** (Cursor / GitLab / Bitbucket / local git) → self-attested **`approved_by` field** on the committed file (the branchless floor, weakest rung). The proposal *file* is canonical; every rung is a way of looking at it.
_Avoid_: PR fallback, review options

**Proposal file**:
The canonical gate artifact — a file in `proposals/` carrying #17's proposal schema (diff, reason, evidence links, blast-radius declaration). It *is* the review file. Anchoring on the file (not the PR) follows from "groundwork is files": PR metadata evaporates if you leave GitHub; the file and its consent commit do not. `proposals/` is **pending-only** (mirrors #7's live-records-only doctrine); on apply the file evaporates into the git consent-commit.
_Avoid_: pull request, review file (that framing was #17's GitHub-specific shorthand)

**Commit-bit teeth**:
The real enforcement layer: only the git-capable maintainer can *land* a change on the main line; agents only *propose* (§4). This — not the validator — is what makes rule changes rung-5 "by construction." The gate's guarantee is a permissions convention, not a cryptographic proof; the honest limit is a documented Known Limitation.
_Avoid_: validator enforcement (the validator is a tripwire, not the teeth), branch protection

**Blast-radius match check**:
The validator `--diff` tripwire #18 adds: an escalating change (rule / track-2 skill / description / governance frontmatter / Owner's Card, per #17's boundary) must trace to an approved proposal whose *declared* blast-radius matches what the diff *actually* touches — mismatch or missing-proposal is an ERROR. Stops an agent smuggling a rule edit inside a proposal labelled "track-1 body-only." Cannot verify a human *truthfully* reviewed — that is the commit bit's job.
_Avoid_: consent check (overstates what a stateless validator can prove)
