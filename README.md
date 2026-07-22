# groundwork

> The groundwork your company runs on.

An open-source, harness-agnostic Company OS. Point your coding agent at this repo and it interviews your company about the work each function actually does — what should get **more** human time, what should get **automated away**, and under **what rules** — then generates your operating system from that map: folder-per-function ontologies, skills with named owners, a compiled constitution, and organizational memory that learns under governance instead of rewriting itself.

## Status: building V1

The design is fully charted — all 19 [wayfinder decisions](https://github.com/seanwinslow28/groundwork/issues/1) are resolved and recorded (see [CONTEXT.md](CONTEXT.md)). Build is underway; capabilities are described here only as they become real.

## How groundwork compares

Two active projects work the same territory — a company brain as a git repo of markdown that agents read and improve. Both shipped parts of this shape before groundwork did. The compact version:

| Project | What it is | The contrast (nuance lives in the prose below) |
|---|---|---|
| [Sylph](https://github.com/getnao/sylph) | Harness-agnostic markdown skills in git, self-improving | The rule change itself: automatic there, human-reviewed here |
| [clawcompany](https://github.com/Claw-Company/clawcompany) | A runtime app (`npx clawcompany`) with compressed memory | A runtime you adopt vs. files any agent already reads |

### On the two active projects

**[Sylph](https://github.com/getnao/sylph)** shipped the self-improving-company-brain-as-a-git-repo shape first, in May 2026 — groundwork did not invent that loop. Sylph is harness-agnostic markdown in git, and after you approve a skill's output it rewrites its own rules to match your edits. The contrast groundwork owns is what happens to that rewrite: in Sylph the rule change itself fires automatically, unreviewed (its README says so plainly); in groundwork's design the *change itself* is a typed proposal a human approves before it lands. Governance — typed rules, named owners, appeals, and a validator — is the lane groundwork is building that neither active project ships.

**[clawcompany](https://github.com/Claw-Company/clawcompany)** ships 4-layer compressed memory (~400 tokens per mission) — real context-budget engineering, and prior art groundwork learned from. The difference is a category, not a feature count: clawcompany is a fat runtime you adopt — its own app, UI, and server, multi-*provider* by design — while groundwork is files any agent already reads. groundwork's memory bet also differs in kind: governed memory (provenance, review, supersession) the company owns as files, rather than compression. One status fact, stated only because they report it themselves: clawcompany's own README notes the open-source repo is maintenance-slowed in favor of a paid closed-source sibling — relevant if you are choosing a foundation.

The wider landscape (dswh/company-os, Workflowsio, gbrain, beevibe, the commodity skill libraries) is earlier or thinner takes on parts of the same idea; the sources groundwork genuinely builds on are credited at the bottom in [Prior art & inspiration](#prior-art--inspiration).

## License

Apache-2.0 — chosen for its patent grant (enterprise-counsel comfort). Content generated into `your-company/` is the adopter's own and is **not** covered by this license (an explicit README/NOTICE carve-out ships with the generator). The `LICENSE` file lands with the first release artifacts.

## Prior art & inspiration

groundwork did not invent the company-OS-as-git-repo idea; this section is the honest map of where its pieces came from. Where a source is paid, the idea is theirs and this open implementation is ours — the links go to the originals.

- **Jiaona Zhang (JZ) / Laurel** — the ontology → skills → delivery shape, the captain model, two-track review, and maturity levels trace to [JZ's Company OS essay](https://www.news.aakashg.com/p/company-os-jz). Free editorial with no shipped product; groundwork reimplements the ideas, it does not fork the system described there.

- **Aakash Gupta + Hannah Stulberg** — the Team OS pattern: a shared git repo as a team's knowledge base, with consent-gated file classification (share only on positive evidence; nothing leaks by default). **Hannah Stulberg built the original at DoorDash**; Aakash's [Team OS guide](https://www.news.aakashg.com/p/team-os-cc) (paid, with a public starter repo) and [PM OS](https://www.news.aakashg.com/p/pm-os) package and teach it. groundwork's design generalizes the pattern beyond one team and routes the classification through a compiled constitution.

- **Nate B. Jones** — work-package framing, SOUL.md-style elicitation, "every agent needs an owner," the agent-shaped-work test, and the row-by-row control map for deciding whether an agent ships, from [Nate's newsletter](https://natesnewsletter.substack.com). Stated straight: **Open Skills is a paid product**; the open, forkable artifact is **[Open Brain (OB1)](https://github.com/NateBJones-Projects/OB1)**.

- **[dswh/company-os](https://github.com/dswh/company-os)** — the closest prior art to groundwork's interview-install mechanic; its author coined "self-installing AI-native company operating system." It is a source-available seed; a governed, compiled system with a validator is the delta groundwork is building.
