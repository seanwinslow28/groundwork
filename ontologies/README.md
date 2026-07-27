# Ontologies — the map of what each function does

One directory per function. Each carries an `_executive-view.md` (the top tier) and,
for activities the company has chosen to act on, one deep record per activity.

## The two tiers (#5)

**Executive view** — *every* activity the function does, carrying only its **name** and
its **Direction**. That is the whole requirement. It is meant to be legible to
leadership and finishable in one sitting; it never demands deep fields.

- **up** — deserves *more* human time. Judgment, relationships, or consequences that
  should not be handed to a machine.
- **down** — should stop being hand-run. Repetitive, describable, or mechanical.

Direction is a claim about *where the work should go*, not about how it is done today.

**Deep record** — one file per **acted-on** activity: the Motion verdict with its five
scores, Work type, and the accountability owner, plus — when Motion is `automate` or
`build` — Substrate, Shape, and all eight parts of the Describability Gate.

Depth is earned by acting, not by planning to act. An activity with no deep record is
not a gap; it is an activity nobody has chosen to work on yet, and the validator stays
silent about it.

## The executive-view table has exactly one legal shape

The validator does not parse markdown tables generously — it accepts one canonical
form and ERRORs on everything else, the same way the frontmatter reader accepts one
restricted grammar (#11). This is a format groundwork writes, so defining it beats
guessing at it.

```
| Activity | Direction | Deep record |
|---|---|---|
| Escalation management | up | — |
| Renewal preparation | down | [deep record](customer-success/renewal-prep.md) |
```

A deep-record path is relative to the **function directory**, so inside
`customer-success/_executive-view.md` that last cell links to plain `renewal-prep.md`
with no directory part. It carries the `customer-success/` prefix above only because
this example sits one level up, in `ontologies/` — the validator checks every relative
link in this repository, fenced examples and inline code included, so an example link
has to resolve from the file it is written in.

- The header row is exactly those three columns, in that order.
- The delimiter row comes immediately after it: three cells of three-or-more dashes,
  no alignment colons.
- Every row starts and ends with `|` and has exactly three cells, unindented.
- Cells are plain text — no code spans, HTML, escaped pipes, or images.
- The Deep record cell is `—` or exactly one link.
- The file contains **one** such table and no other line carrying a `|`.

The cost of this is real and deliberate: benign formatting variance — reordering the
columns, `| :--- |` alignment, indenting the table, a row without its trailing pipe —
fails the gate rather than being tolerated. That is the same trade #11 already took
for frontmatter, and it is why a header typo can no longer silently disable every
Direction check in a file.

## These files are templates

The ontologies in this repository are **engine exemplars** — a plausible starting map
for a B2B SaaS company, not claims about yours. The activity lists and Directions are
meant to be edited, cut, and argued with. A generated company's real ontology lives in
its own private repository (see `AGENTS.md`, "Two repos").

`people-hr/` is worked one level deeper than the rest: it carries the
`onboarding-orchestration` deep record that the skill, Owner's Card, memory baseline,
and constitution rule are all built on. Read it as the reference shape.
