# Roadmap

**Last reviewed 2026-08-01.** Nothing below V1 is described in the present tense, and
nothing moves onto the shipped list until it is. That rule is the same one the README has
run on since the first commit: no capability claim precedes the capability.

## V1 — shipped

The adoptable core: the two-tier ontology schema, work packages with Owner's Cards, the
compiled constitution on a five-rung enforcement ladder, organizational memory with
provenance and supersession, the consent gate and its blast-radius tripwire, the version
pin and the pull promise, the interview and generation protocols, the `demo/` company with
its fifteen-minute walkthrough, the provisioning guide, and the zero-dependency validator
that gates all of it.

One thing on this list has never been done by anyone: **no adopter has run the interview
and generation on a real company.** The protocols have been executed twice by the team
that wrote them — a generation-only dry run against the demo's own layers, and one full
end-to-end run, the interview protocol's first, against a simulated company staffed by
adversarial agent personas, scored blind against planted gaps and with the interviewing
session's transcript audited.
[known-limitations.md](known-limitations.md) records both runs and what a simulated
company cannot prove.

## V1.5 — hardening, no schema change

Small, and none of it is promised by a date.

- **Gate on git-tracked content** rather than on a walker plus a minimal `.gitignore`
  reader. Cleaner scope than the current model and it retires two known limitations.
- **`SPDX-License-Identifier` headers** on the three shipped scripts. Deferred from V1
  deliberately: worth adding once, on purpose, rather than as a side effect of a
  documentation slice.
- **Changelog rotation.** The append-only check compares against the full base file, so a
  long-lived changelog has no supported way to be archived.
- **The generation protocol's one unresolved composition**, found by its first dry run:
  a skill missing a human-only answer ships `provisioned: no`, but when its deep record
  also did not ship, the skill's `ontology:` reference has nothing to resolve to and the
  gate ERRORs. Which instruction wins is a maintainer decision, recorded in
  [known-limitations.md](known-limitations.md) until it is made.
- **Severity mismatches from the rule map's hand audit** — the Slice 4.3 audit found
  none, so nothing is queued; this line is the standing home for any a later audit finds.
- **Keep the comparison current.** [How groundwork compares](../README.md#how-groundwork-compares)
  is a claim about a landscape that moves, and a comparison written once and left alone
  becomes wrong without anyone editing it. It gets re-verified against the named projects
  rather than left to rot, on the same principle as this document's review date.

## V2 — documented, not built

Each of these is designed far enough to be described and deliberately absent from V1. The
first one is the only one with a schema cost.

- **The first `SCHEMA_VERSION` bump has landed, and neither candidate rode it.** v2 is
  *roles as the accountable unit* — a roster at `governance/roles.md`, and an active rule's
  owners must resolve against it ([MIGRATIONS.md](../MIGRATIONS.md)). The two passengers
  this bullet named are recorded below, with what became of each. First, a
  health-metrics field: the interview already asks what must not degrade while a
  standard is met — the Goodhart guard — and there is nowhere typed to put the answer,
  so it lands in prose. The first end-to-end run was designed to measure whether that
  gap matters and could not: its must-not-degrade plant failed at elicitation, so the
  fact never reached prose and the typed-field question stays open. Second, and the only
  candidate with a measured instance behind it: **a representable form for *enforced,
  but nobody owns it***. That run's confirmed interview record carried a rule at
  `hard-block` whose ownership nobody claimed. Three outcomes were considered — omit the
  rule, ship it and let the gate fail, or ship it as a declared draft — and the generation
  contract permits only the first, since an artifact missing a required field does not
  ship. The run shipped the draft and the validator accepted it with warnings, so a
  structural consumer reads two drafts and zero active rules where the confirmed record
  says a hard gate. That the gate allowed it at all is a second finding, not a licence.

  The health-metrics field is **still unbuilt** and still a candidate for a later bump. The
  second candidate was **superseded rather than delivered**: v2 chose held-to-activate over a
  representable third state, so an unowned practice still reads as a draft in the machine
  layer — by design now, with named WARNs, rather than by accident. The roles design records
  that choice and its cost in full. Any further addition is another bump with its own
  migration note; the pull promise has been binding since 2026-07-29.
- **Per-check `since:` tags** and scatter-suppression, the other half of the version-skew
  policy. **Wired at the v1→v2 bump**, as planned: a check declares the version it was
  introduced at, and its ERROR demotes to a finger-pointing WARN behind an older pin's single
  migration-boundary error.
- **The Classify, Consent, Enforce compliance pack:** a consent registry with approved and
  forbidden uses and expiry, CODEOWNERS on sensitive generated folders, a Gitleaks
  profile, an erasure runbook, and a data-protection impact template.
- **Cowork plugin packaging and the GitHub-synced marketplace as a walkthrough** rather
  than as documented steps a maintainer runs by hand.
- **Runnable learning-loop skills** — session-to-skill extraction and an
  improvement-proposal skill — plus generated rung-3 reminders rather than one hand-written
  exemplar.
- **The morning-briefing pattern** and a truth-layer schema.
- **Governed autonomous application:** today an agent proposes and a human lands. The
  question V2 asks is which changes an agent may apply under a rule that a human wrote,
  with the consent record still intact.
- **Cross-harness runtime-enforcement parity.** Hooks are Claude-Code-only; everywhere
  else the action-class rule degrades to an instruction. Closing that means building on
  each harness's own enforcement surface, where one exists.

## V3 — further out

- **Re-interview and drift.** Merging a new interview pass against retained state, which
  is what the frozen-layer format was built to make possible.
- **Per-function deepening** past the first three-to-five acted-on activities.
- **An adoption scoreboard** measured as coordination tax removed rather than as usage.
- **An evaluations and traces recipe** for skills that actually run.

## Never

Not "not yet" — these are commitments, and they are what keeps everything above cheap.

- **No hosted anything.** No server, no dashboard, no per-seat features, no account.
- **No agent runtime.** The harness is the runtime.
- **No memory or retrieval engine.** groundwork owns what an organization should remember,
  with what provenance, owned by whom — not how it is indexed or recalled.
- **No third-party dependencies** in shipped scripts. There is no `requirements.txt` and
  there will not be.

## How this document stays honest

Two mechanisms, both cheap. It carries the date it was last reviewed, so a reader can see
how stale it is rather than guessing. And an item may only move to the shipped list in the
same change that ships it — the same rule that kept the word "open source" out of the
README until the `LICENSE` file existed.
