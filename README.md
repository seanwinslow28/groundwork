
# groundwork

> The groundwork your company runs on.

An open-source, harness-agnostic **Company OS**. It is files, not an engine: markdown
conventions plus one zero-dependency validator, so any coding agent that reads a
repository can read this one. You point your agent here, it interviews your company about
the work each function actually does — what deserves **more** human time, what should be
**automated away**, and under **what rules** — and generates your operating system from
that map into a separate private repository: folder-per-function ontologies, skills with
named owners, a compiled constitution, and organizational memory that learns under
governance instead of rewriting itself.

## The governance, up front

groundwork's lane is governance. These are the mechanisms, not the claims:

- **The generator refuses to invent accountability.** It never supplies an interview
  answer the company did not give — that binds every answered field, the roster's holders
  and their types included — and five carry the refusal as an explicit mark: the owner, the
  backup owner, the forbidden actions, and the two death conditions. Those come only from a
  human's interview answers. An invented owner is an accountability
  structure the named person discovers when something goes wrong.
- **Every skill can die, and a human names the trigger.** Each skill's Owner's Card
  carries a pause condition and a retirement condition, both human-authored. "Some agents
  should die" only means something if a person named the trigger.
- **Eight preconditions before any skill exists.** The Describability Gate: inputs,
  output, standard, source of truth, exception path, error cost, owner, review gate. All
  eight must be answered. A truthful "none" counts as an answer. "N/A" does not. There is
  no waiver mechanism. (The full decision record lives in [`CONTEXT.md`](CONTEXT.md).)
- **Changes route by blast radius.** A change auto-applies only when a bad version's
  worst case is bounded. Anything touching governance, an owner, or a higher-risk skill
  escalates to human review, and auto-applied changes land in an append-only governance
  changelog.
- **One command checks all of it.** `python3 scripts/validate.py .`, Python standard
  library only. The validator errors exactly where a field backs a running agent, warns
  on incomplete thinking you have acted on, and stays silent on untouched work.
  Strictness follows consequence, not completeness.

And what this repo will not claim: no check reads prose for truth, the demo's refusal is
instruction-strength rather than a runtime block, and no real company has run the
interview yet. [`docs/known-limitations.md`](docs/known-limitations.md) is written to be
read before you rely on a check, not after.

## Not technical? Point your agent at this repo

One person who can use git and run a coding agent. That is the whole technical
requirement, and it is a real requirement — everyone else receives skills and proposes
changes in conversation.

1. **Clone this repository and open it in your coding agent** — Claude Code, Codex,
   Cursor, or Gemini CLI. Each loads [`AGENTS.md`](AGENTS.md) by its own convention:
   Claude Code through `CLAUDE.md`, Gemini CLI through `GEMINI.md`, Codex and Cursor
   natively. All three pointers are committed here, and `scripts/validate.py` checks that
   each still routes to the same canonical file.
2. **Say this:** *"Read AGENTS.md, then walk me through `demo/walkthrough.md`."* Fifteen
   minutes, three questions, no credentials.
3. **Then say this:** *"Interview me by following `interview/`, and generate our OS into a
   new private repository."* The agent asks one question at a time, and where an answer
   can only come from a person it stops instead of guessing.

No groundwork runtime to install, no server, no signup — the moving parts are git,
Python 3, and your coding agent. The one command this page asks anyone to run is
`python3 scripts/validate.py`.

## See it work first — fifteen minutes, no credentials

[`demo/walkthrough.md`](demo/walkthrough.md) is a pre-installed fictional twenty-person
company. Three questions, in order:

1. **A decision lookup.** Why engineering moved to asynchronous standups, who decided it,
   and what it replaced. The answer has a name and a date on it, the reasoning includes
   what was given up, and the superseded decision is still readable rather than deleted.
2. **A cross-function synthesis.** Which renewals are at risk because of unbuilt product
   work, and how much contract value is exposed. Nobody wrote that answer down — it lives
   across two functions' records, and the ontology is what makes them addressable
   together.
3. **A skill, and a refusal.** Ask for a performance-review evidence pack and you get a
   description of one. Then ask the agent to write the assessment itself, and it refuses —
   naming the rule, the owner, the appeal path, and what it *can* do instead — then points
   at the pending proposal somebody filed the last time this happened.

**What the walkthrough is honest about, and so is this page.** That refusal is
instruction-strength, not a runtime block: no hook enforces it, and the demo says so at
the exact moment overstating it would be most tempting. The company is fictional and
nothing is connected, so no skill there can actually run. Agents do not reliably
auto-select a skill from a description, so you may have to point at the file. And these
are three questions asked of a language model — the walkthrough tells you what a good
answer contains, not a transcript to match.

## The interview, and what it writes

**It is documents, not a program.** There is no `generate.py`. [`interview/`](interview/)
holds four things an agent follows: a resumable state format where "confirmed" is git
structure rather than a label an agent can edit, the consultant protocol (define the role
first, one question at a time, ground every acted-on activity in evidence, no
generation until understanding is complete), a
nine-section question skeleton in which every question names the field its answer fills,
and the generation protocol with the manifest of what a company repo contains.

The generator never supplies an interview answer the company did not give; five fields
carry that refusal as an explicit mark, and are the ones it will not draft even from
context: the owner, the backup owner, the forbidden actions, and the two death conditions.
An invented owner is an accountability structure the named person discovers when something
goes wrong.

Your OS lands in a **separate private repository**. This clone stays a pull-only engine;
nothing organizational is ever written into it, upstream improvements arrive by
`git pull` here, and your content is never re-copied — see [`AGENTS.md`](AGENTS.md) ("Two
repos") and [`MIGRATIONS.md`](MIGRATIONS.md) for the version-pin contract that makes
pulling safe.

The generator is a protocol rather than a script because its input is prose written by a
person and an agent in conversation, and a parser for that has an unbounded supply of
ways to be wrong. What makes it trustworthy is the gate at the end — and this repository's
own test suite builds a company repo from the manifest and proves the gate passes on it.

## Check what you have

```
python3 scripts/validate.py .
```

Python 3 standard library only. No dependencies, no `requirements.txt`, and a test that
fails if a shipped script ever imports one. Exit 0 means no ERRORs; WARNs print and do not
fail. To check the OS you generated, pass its path instead:

```
python3 scripts/validate.py ../acme-os
python3 scripts/validate.py ../acme-os --diff <generation commit>
```

**The base is the generation commit, not `main`.** The commit that created the governed
root is not subject to the consent gate — generation cannot be its own proposal — so a
base from before generation returns every generated rule as an escalating change with
nothing pending to match it. [`interview/generate.md`](interview/generate.md) names the
base and carries the measurement.

The first run checks structure and referential integrity, the two ontology tiers, every
Owner's Card against its ontology's owner and source of truth, every constitution rule
against the safety invariant that no rule may end in automation, every memory record's
provenance and supersession chain, a high-signal secrets floor, and the always-loaded
context budget. The second adds the stateful rules: organizational memory is
append-and-supersede rather than editable; a confirmed interview layer is frozen wherever
the base holds both the layer and its `00-manifest.md`; and the #18 consent gate
classifies every changed constitution rule, roles roster, and skill-package file, ERRORing
on an escalating change with no matching pending proposal. Deleting one of those governed
files **WARNs** rather than ERRORs, and #17's changelog rules run alongside.
[`proposals/README.md`](proposals/README.md) carries the full classification.

**What it does not prove.** The secrets floor is high-signal, not exhaustive. No check
reads prose for truth — the validator can confirm every required field is answered, and
cannot tell you the answer is true. [`docs/known-limitations.md`](docs/known-limitations.md) is the
full list, written to be read before you rely on a check rather than after.

## Getting it in front of people

[`delivery/`](delivery/) is the provisioning guide: the repo-local symlink layer that
gives your generated skills a harness-visible path, the organization plugin paths for
people who never touch git, and how to install the runnable action-class gate — with the
re-copy obligation that comes with it. Nothing in groundwork zips, uploads, or syncs
anything; these are steps a maintainer runs, and every external fact in the guide carries
the date it was verified, because all of these surfaces move.

## Status

**V1 is complete.** Everything this page describes is in the repository, and
`scripts/validate.py` gates all of it: the schema as files; eight function ontologies plus
worked deep records on both governance tracks, including one recording a deliberate
decision *not* to automate; work packages with Owner's Cards; a typed constitution on a
five-rung enforcement ladder, with one runnable exemplar and prose degradation everywhere
else; organizational memory with provenance and supersession; the consent gate and its
blast-radius tripwire; the interview and generation protocols; the `demo/` company and its
walkthrough; the provisioning guide; and the licence, security, and roadmap documents.

**And here is the thing nobody has done.** No interview has been run on a real company, so
no company OS has been generated from real answers. What is proven is the destination — a
test builds a company repo in the shape the manifest specifies and validates it as its own
root — plus one scoped dry run of the generation protocol against the demo's own layers,
and, as of 2026-08-01, one full end-to-end run of both protocols against a simulated
company staffed by adversarial agent personas: an interview nobody scripted, a generated
OS the validator passes, a scorecard graded blind against planted gaps, and a transcript
audit confirming the interviewer never read the answer key. What a simulated company can
and cannot prove is recorded in [`docs/known-limitations.md`](docs/known-limitations.md).
The path from a real conversation to a real repository has been designed, documented,
gated, and walked in simulation — not yet with a real company. If you walk it for real,
the thing we most want to hear about is where the protocol left you guessing.

[`docs/roadmap.md`](docs/roadmap.md) is what comes next and what never will.
[`docs/known-limitations.md`](docs/known-limitations.md) is what this does not do.
[`docs/security-and-privacy.md`](docs/security-and-privacy.md) is what it exposes.
[`docs/rule-map.md`](docs/rule-map.md) is every check and the severity it fires at.
[`CONTEXT.md`](CONTEXT.md) is the glossary of all nineteen resolved design decisions.

## How groundwork compares

Two active projects work the same territory — a company brain as a git repo of markdown that agents read and improve. Both shipped parts of this shape before groundwork did. The compact version:

| Project | What it is | The contrast (nuance lives in the prose below) |
|---|---|---|
| [Sylph](https://github.com/getnao/sylph) | Harness-agnostic markdown skills in git, self-improving | The rule change itself: automatic there, a human-approved proposal in groundwork's design |
| [clawcompany](https://github.com/Claw-Company/clawcompany) | A runtime app (`npx clawcompany`) with compressed memory | A runtime you adopt vs. files any agent already reads |

### On the two active projects

**[Sylph](https://github.com/getnao/sylph)** shipped the self-improving-company-brain-as-a-git-repo shape first, in May 2026 — groundwork did not invent that loop. Sylph is harness-agnostic markdown in git, and after you approve a skill's output it rewrites its own rules to match your edits. The contrast groundwork owns is what happens to that rewrite: in Sylph the rule change itself fires automatically, unreviewed (its README says so plainly); in groundwork's design the *change itself* is a typed proposal a human approves before it lands. Governance — typed rules, named owners, appeals, and a validator — is the lane groundwork is building that neither active project ships.

**[clawcompany](https://github.com/Claw-Company/clawcompany)** ships 4-layer compressed memory (~400 tokens per mission) — real context-budget engineering, and prior art groundwork learned from. The difference is a category, not a feature count: clawcompany is a fat runtime you adopt — its own app, UI, and server, multi-*provider* by design — while groundwork is files any agent already reads. groundwork's memory bet also differs in kind: governed memory (provenance, review, supersession) the company owns as files, rather than compression. One status fact, stated only because they report it themselves: clawcompany's own README notes the open-source repo is maintenance-slowed in favor of a paid closed-source sibling — relevant if you are choosing a foundation.

The wider landscape (dswh/company-os, Workflowsio, gbrain, beevibe, the commodity skill libraries) covers parts of the same idea; the sources groundwork genuinely builds on are credited at the bottom in [Prior art & inspiration](#prior-art--inspiration).

## License

[Apache-2.0](LICENSE) — chosen for its patent grant (enterprise-counsel comfort). The
`LICENSE` file is the canonical Apache text, unmodified, so you can diff it against
[apache.org](https://www.apache.org/licenses/LICENSE-2.0.txt) and see exactly what you are
agreeing to.

Copyright 2026 Sean Winslow.

**Your content is yours.** The operating system the interview generates is the adopter's
own work and is **not** covered by groundwork's license. That is not only a statement
here: [`interview/generate.md`](interview/generate.md) instructs the generator to write
the same carve-out into the company repository's own root instruction file, so the
repository holding your content is the one that says whose it is.

There is deliberately **no `NOTICE` file.** Under Apache-2.0 section 4(d), the attribution
notices in a NOTICE file must be carried forward by the derivative works they pertain to —
which makes NOTICE an attribution instrument, and the wrong home for a statement about the
adopter's own content in a different repository. The carve-out lives where the person it
protects will read it.

## Prior art & inspiration

groundwork did not invent the company-OS-as-git-repo idea; this section is the honest map of where its pieces came from. Where a source is paid, the idea is theirs and this open implementation is ours — the links go to the originals.

- **Jiaona Zhang (JZ) / Laurel** — the ontology → skills → delivery shape, the captain model, two-track review, and maturity levels trace to [JZ's Company OS essay](https://www.news.aakashg.com/p/company-os-jz). Free editorial with no shipped product; groundwork reimplements the ideas, it does not fork the system described there.

- **Aakash Gupta + Hannah Stulberg** — the Team OS pattern: a shared git repo as a team's knowledge base, with consent-gated file classification (share only on positive evidence; nothing leaks by default). **Hannah Stulberg built the original at DoorDash**; Aakash's [Team OS guide](https://www.news.aakashg.com/p/team-os-cc) (paid, with a public starter repo) and [PM OS](https://www.news.aakashg.com/p/pm-os) package and teach it. groundwork's design generalizes the pattern beyond one team and routes the classification through a compiled constitution.

- **Nate B. Jones** — work-package framing, SOUL.md-style elicitation, "every agent needs an owner," the agent-shaped-work test, and the row-by-row control map for deciding whether an agent ships, from [Nate's newsletter](https://natesnewsletter.substack.com). Stated straight: **Open Skills is a paid product**; the open, forkable artifact is **[Open Brain (OB1)](https://github.com/NateBJones-Projects/OB1)**.

- **[dswh/company-os](https://github.com/dswh/company-os)** — the closest prior art to groundwork's interview-install mechanic; its author coined "self-installing AI-native company operating system." It is a source-available seed; a governed, compiled system with a validator is the delta groundwork is building.
