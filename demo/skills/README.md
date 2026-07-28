# Umbercress — skills

The four activities Umbercress has acted on, each shipped as a work package: a
`SKILL.md` that says what the agent does, and an `owner-card.md` that says who
answers for it. The convention itself is documented in the engine
([work-package spec](../../skills/work-package-spec.md)); this directory is what it
looks like filled in for one company.

| Package | Action class | Owner | Ontology record |
|---|---|---|---|
| [renewal-prep](renewal-prep/SKILL.md) | reversible-write | Marcus Bell | [Renewal preparation](../ontologies/customer-success/renewal-preparation.md) |
| [feature-request-triage](feature-request-triage/SKILL.md) | reversible-write | Dana Whitfield | [Feature-request triage](../ontologies/product/feature-request-triage.md) |
| [onboarding-orchestration](onboarding-orchestration/SKILL.md) | external-side-effect | Ruth Okafor | [Onboarding orchestration](../ontologies/people-hr/onboarding-orchestration.md) |
| [performance-review-prep](performance-review-prep/SKILL.md) | reversible-write | Ruth Okafor | [Performance-review prep](../ontologies/people-hr/performance-review-prep.md) |

Three of the four are track 1 — everything they write is a document a person reads and
can rewrite. Onboarding is track 2 because it creates accounts, orders equipment, and
sends messages: side effects that leave the workspace. That difference is not a label,
it is what the Owner's Cards and the constitution are shaped around.
