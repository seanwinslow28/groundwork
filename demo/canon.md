---
company: Umbercress
product: Umbercress Relay
domains:
  - umbercress.example
external_domains:
phone_range: 555-01
---
# The Umbercress world — demo canon

This file declares the fictional company the demo is built on. It is two things at
once: the human description of that world, and the validator's **positive allowlist**
— every email, domain, phone number, and IP address anywhere under `demo/` must trace
back to what is declared here or to a namespace reserved for fiction (#16).

Everything under `demo/` is in scope by directory. There is no per-file "this is
synthetic" marker, because a marker re-asserts rather than verifies.

## The company

**Umbercress** is a ~20-person B2B SaaS company. Its product, **Umbercress Relay**, is
a shift-scheduling platform sold to mid-market logistics operators. It has one office,
no subsidiaries, and about 60 paying customers on annual contracts.

Its size is the point. A 20-person company has a fractional CFO and a bookkeeper
rather than a finance department, one person doing all of People operations, and three
people in customer success — which is why the demo's ontology goes deep on customer
success, product, and People/HR, and stays deliberately shallow elsewhere.

## Identifiers

| Kind | Value | Why it is safe |
|---|---|---|
| Email domain | `umbercress.example` | `.example` is reserved for documentation (RFC 6761) **and** declared here |
| Phone numbers | `555-01xx` | The North American range reserved for fiction |
| IP addresses | `192.0.2.x`, `198.51.100.x`, `203.0.113.x` | TEST-NET-1/2/3, reserved for documentation (RFC 5737) |
| External domains | none | The demo links to nothing real. Adding one is a deliberate edit to this table and to `external_domains` above |

## The people

Eight people are named in the demo; the other dozen or so are unnamed. Emails follow
`first.last@umbercress.example`.

| Name | Role |
|---|---|
| Priya Raman | CEO |
| Marcus Bell | VP Customer Success |
| Dana Whitfield | Director of Product |
| Tomás Iglesias | VP Engineering |
| Ruth Okafor | Head of People |
| Jae-won Park | Principal Product Manager |
| Nina Sokolova | Senior Customer Success Manager |
| Ellis Warner | Staff Engineer |

**These names are the honest limit of this file.** A structured identifier can be
proven fictional; a person's name cannot. Any name is somebody's real name somewhere,
so "no real person is referenced here" rests on the fact that these were invented for
this demo and on maintainer review — not on any check. The same is true of the company
name, which was searched for prior art before it was chosen but cannot be proven
unique. See [docs/known-limitations.md](../docs/known-limitations.md).

## Customers

Customer accounts named in the demo are fictional operators: **Cartwright Haulage**,
**Belport Freight**, **Norlander Logistics**, **Waypoint Distribution**. They carry no
identifiers of their own beyond `umbercress.example` contacts.
