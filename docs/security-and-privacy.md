# Security and privacy

Who this is for: the person deciding whether to put their company's operating rules in a
git repository, and whoever has to sign off on that. It describes what groundwork exposes,
what it cannot protect, and the three things a maintainer has to get right.

For the mechanics of what each individual check does and does not catch, read
[known-limitations.md](known-limitations.md). This page is the shape of the risk, not the
list of gaps.

## The shape of the thing

groundwork is markdown files in a private git repository, read by coding agents, maintained
by one person who has the commit bit. There is no server, no database, no hosted component,
and no account. That removes whole categories of risk — there is no service to breach, no
tenancy to escape, no session to hijack — and concentrates what is *stored* in two places:
**your git host** and **the machines your agents run on**.

What is *processed* goes further, and a privacy reviewer should count both surfaces:

- **The model provider, on every cloud-backed harness.** Claude Code, Codex, Cursor, and
  Gemini CLI send what the agent reads to their model APIs — and an agent working in a
  company OS reads the ontology, the memory records, and (if retained) the interview
  transcript. Whatever retention, training-use, and access terms you have with that
  provider apply to this material; groundwork adds no layer on top of them.
- **The plugin path, if you choose organization distribution.** A manually uploaded
  plugin ships only what you packaged — skill bodies and Owner's Cards. A GitHub-synced
  marketplace is broader: the vendor's GitHub App is authorized on the **connected
  repository**, not on the plugin subdirectory, so if the marketplace repository is your
  company repo, the integration can reach the interview transcript and organizational
  memory too. If those must stay off the vendor surface, use a dedicated marketplace
  repository holding only the plugin folders — and treat it as a **derived artifact**:
  update it only by copying from an approved company-repo commit, never by editing it in
  place, because a plugin-only repository carries no `groundwork.pin` and the consent
  gate does not run there.
  [`delivery/README.md`](../delivery/README.md) documents both paths with dates.

Everything groundwork ships that executes is three Python files: the validator, the
action-class hook, and the demo's rung-3 reminder. All three are Python 3 standard library
only, take input and print output, and **make no network calls** — the stdlib allowlist in
`TestZeroDep` does not contain `urllib`, `socket`, `http`, or any client library, so a
shipped script that imported its way onto the network would fail this repository's own
test suite, and the one external program any of them runs is `git`, locally. There is no
telemetry, no update check, and nothing that phones home.

## The one failure that is silent, and it is a privacy failure

If you distribute your skills as an organization plugin, **the plugin source must be a
subdirectory, never the repository root.** A manifest entry pointing at the root packages
the whole company repo — including your interview transcript, your organizational memory,
and your constitution — and ships it to every employee who installs it.

It is silent: nothing breaks, no error appears, the plugin works. And pointing the
marketplace at the repository you already have is the obvious first move, which makes this
the single most likely serious mistake available. [`delivery/README.md`](../delivery/README.md)
states it as a hard rule with the reason attached. **No check can enforce it** — the
manifest lives in a dot-directory the validator never scans, and that limit is recorded
rather than papered over.

## What is in the repository, most sensitive first

1. **`interview/` — the interview transcript.** The most sensitive thing in a company OS,
   and the easiest to underestimate. It records how the company actually works, including
   what people said about what is broken and who owns what. Treat it the way you would
   treat leadership meeting notes, because that is roughly what it is.
2. **`memory/` — organizational memory.** Named people, dates, decisions, contract values,
   and captured baselines. Records are append-and-supersede, so nothing is ever edited
   away — see the erasure tension below.
3. **`governance/constitution/` — the rules.** Each rule names an owner and an appeal
   path, so it is a map of who decides what.
4. **`ontologies/` and `skills/` — the work map.** Process and role detail, plus each
   agent's owner, forbidden actions, and death conditions.

All four are why the two-repo model exists: the public groundwork clone is an engine and
nothing organizational is ever written into it.

## Who can reach it

**One git-capable maintainer holds the commit bit.** That is the write model: everyone
else proposes changes in conversation, and the maintainer commits.

**Read access depends on how you distribute skills, and only one path keeps the
repository off employees' machines.** Under organization plugin distribution, employees
receive the packaged skills and never the repository. Under repo-local provisioning — the
only path that exists for Codex, Cursor, and Gemini CLI, which have no organization push
surface — provisioning means the person **has the repository checked out**, interview
transcript, organizational memory, and constitution included. If those must stay
maintainer-only, plugin distribution is the only current answer, and it is
Claude-Code-only; [known-limitations.md](known-limitations.md) records this squarely.

The consequence is that **your repository's access control is your git host's** — branch
protection, org membership, SSO, and audit log are the git host's features, not
groundwork's. Organization plugin distribution adds a second surface with its own
requirements (Team or Enterprise plan, Cowork and Skills enabled, Owners only), documented
with its verification date in [`delivery/README.md`](../delivery/README.md) — and it is a
**hosted** surface: what you package ships through the vendor's service and lands on every
installing employee's machine, which is exactly why the subdirectory rule above is the one
failure this page leads with.

## Secrets

A company OS should contain no credentials, and the validator enforces a floor rather than
a guarantee: a curated set of high-signal secret patterns at **ERROR** level, plus an
entropy heuristic that only **WARNs** — a WARN prints and does not fail the gate — running
over the walked, non-gitignored, **UTF-8-readable** content. A file the walker cannot read
or decode is skipped silently, so a credential in a binary or non-UTF-8 file is outside
this floor entirely. It is **not** exhaustive.

**Use [Gitleaks](https://github.com/gitleaks/gitleaks) as the real backstop**, in CI or as
a pre-commit hook. That is not a hedge — it is the documented design, because a
zero-dependency stdlib scanner cannot compete with a maintained rule set, and pretending
otherwise would be the more dangerous claim. Two scope facts worth knowing: `.gitignore`
matching is minimal (exact names and simple globs), and this repository's own gate skips
`tests/` and `docs/superpowers/` because the validator's fixtures necessarily quote
example secret patterns.

## What the validator cannot prove

Three limits matter more than the rest, and none of them is a bug:

- **It cannot prove a human reviewed anything.** The consent gate is a tripwire: it can
  demand that an escalating change carry a matching proposal, and it cannot tell whether
  anyone read it. The real enforcement is the commit bit — only the maintainer can land a
  change. That is a permissions convention, not a cryptographic proof.
- **It cannot read prose for truth.** Every required field can be answered, correctly
  shaped, and wrong. The validator checks that the answer exists; a person checks that it
  is true.
- **It cannot prove your demo or your records are free of real names.** Structured
  identifiers — emails, domains, phone numbers, IP addresses — are mechanically checked
  against a declared allowlist in demo content. A real person named in free prose looks
  exactly like a fictional one, and a postal address is prose to this check.

## Personal data, and an honest tension

Organizational memory names people. Records carry an owner, a provenance label, and a
date, and a superseded record stays readable rather than being deleted — that is the whole
point of the schema, and it is what makes "why do we do it this way" answerable.

**It is also in tension with an erasure request**, and V1 does not resolve it. Git history
means that even deleting a file leaves the content reachable; a real erasure is a
history-rewriting operation on the repository. groundwork ships no runbook for that in V1.
The compliance pack — a consent registry, CODEOWNERS on sensitive generated folders, a
Gitleaks profile, an erasure runbook, and a data-protection impact template — is
documented on the [roadmap](roadmap.md) and **not built**. If personal-data handling is a
gating requirement for you, that is the honest answer today.

Two things you can do now, neither of which groundwork implements for you: keep
performance and assessment content out of organizational memory (the demo's
performance-review rule models exactly this boundary), and decide deliberately whether
your interview transcript is retained — **before the repository's first commit.** The
generator's default is to keep `interview/`, and the `--diff` gate treats deleting a
confirmed layer as an ERROR (frozen layers are the consent record) wherever the base being
compared against holds both that layer and its `00-manifest.md` —
[`interview/README.md`](../interview/README.md) states the condition. So retention is an
upfront choice, not one you can quietly reverse later. Nothing in the
validator requires an `interview/` directory to exist, and the demo retains its own as a
disposition rather than a rule.

## Reporting something

groundwork is files, so the realistic vulnerability surface is small: the three scripts,
and any instruction in a shipped document that would lead an agent to do something unsafe.
If you find either, open an issue on the repository. There is no embargo process and no
security mailing list, and saying so is more useful than implying one exists.
