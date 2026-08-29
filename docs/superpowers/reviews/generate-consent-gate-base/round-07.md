## Round 7 — 2026-08-29, maintainer decision (not a review round)

No Codex invocation. This entry records the decision that unblocked the branch. Round 6
answered the question it was asked directly — *"This branch cannot receive approval until
item 4 is decided and the prose is made consistent with that choice"* — and the maintainer
decided item 4 on 2026-08-29, with the six options, a recommendation and a
counter-argument put individually.

**Fix commit for round 6: `13d8bef`.** Round 1 → `5a71138`, 2 → `f562d69`, 3 → `7421d58`,
4 → `10e1ec1`, 5 → `d2ce4fc`, 6 → `13d8bef`.

| Item | Decision | Chosen | Where it landed |
|---|---|---|---|
| 4 | What "the generation commit" means when generation is not one commit | **Option (e): `groundwork.pin` lands only in the final generation commit** (the recommendation) | The `groundwork.pin` bullet and the base sentence in "Then prove it" |

**What changed, and why it resolves the blocker.** `generate.md` still has no commit step,
so "the generation commit" named a commit nothing told anyone to make. The ordering rule
supplies one without requiring atomic generation: the pin is committed only in the last
generation commit, so **the commit that creates the governed root and the final commit of
generation are the same commit**. S2's approved sentence — "the commit which creates the
governed root is not subject to the consent gate" — is then literally true whether
generation took one commit or several, and the base sentence can name that commit without
presupposing atomicity. The document already told the generator to write the pin last, so
this turns existing advice into the definition rather than adding a rule.

**The counter-argument, recorded.** It makes a write-order instruction load-bearing for
governance: a generator that commits the pin early produces a repo whose base this rule
cannot name. The maintainer accepted that against the alternative of requiring generation
to be a single commit, which is simpler but forbids a multi-commit generation outright.

**What the base-relative statement from round 6 keeps doing.** The clause added there —
escalation turns on whether the base you diff against already holds the file, not on write
order within a commit — is true under this decision as under every other option, and is
unchanged. It is what keeps the pin bullet's rationale correct rather than merely
consistent with the chosen topology.
