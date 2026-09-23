# CFC + HAWM Founding Beta v2 — Paid Launch Blocker Matrix

Status date: 2026-09-23

## Purpose

This matrix separates engineering readiness from owner decisions and external dependencies.

The Founding Beta can continue as an experimental, controlled pre-paid/private beta while paid activation remains blocked by the external/legal items below.

## A. Engineering / product — internally controllable

| Item | Status | Evidence / next action |
|---|---|---|
| Dedicated no-customer-content Founding Beta page | READY | `/founding-beta` branch implementation |
| Content-free measurement contract | READY | system/workflow/CFC/reason/HAWM/human/problem metadata only |
| Ephemeral structured CFC check | READY | no message or free-text HAWM persistence |
| Workspace ownership | READY | persistence/API tests |
| Measurement deletion endpoint | READY | authenticated workspace purge |
| Postgres 18 compatibility | READY | CI PASS |
| Current production baseline health | READY | Railway latest deployments SUCCESS |
| Frozen controller unchanged | READY | Anchor 0.2.90rc1 / Wrapper v1.23 remain frozen |
| Automatic 30-day retention enforcement | BLOCKER | implement scheduled/credible cleanup before claiming automatic 30-day deletion |
| Live Founding Beta deployment | BLOCKER / NOT AUTHORIZED YET | requires explicit deployment decision |
| Live onboarding dry run | BLOCKER ON DEPLOYMENT | run after a safe beta route is deployed |

## B. Owner decisions — must be explicit

| Item | Status | Decision needed |
|---|---|---|
| Support contact | OPEN | real monitored address/channel |
| Security/privacy incident contact | OPEN | real monitored non-public channel |
| Emergency escalation | OPEN | person/channel |
| Named production operators | OPEN | who may access Railway/database |
| Billing mechanism | OPEN | Stripe/manual invoice/other |
| Refund policy | OPEN | commercial decision + legal review |
| Minimum beta activity | OPEN | e.g. N real workflows/tests per month |
| Paid vs no-charge first wave | OPEN | decide whether legal review precedes all external use or only payment |

## C. External factual verification

| Item | Status | Needed |
|---|---|---|
| Railway customer-facing data geography | OPEN | verify current Railway documentation for region code `sfo` |
| Backup retention/expiry | OPEN | verify Railway/provider behavior |
| Encryption/security disclosures | OPEN | verify current provider documentation |
| Subprocessor list | OPEN | Railway, Clerk, model providers; confirm roles |

## D. UK legal review — hard blocker to paid start

Counsel must finalize or approve:

- Founding Beta Agreement;
- Privacy Notice / data-flow;
- controller/processor roles;
- retention/deletion wording;
- subprocessors and international transfers;
- governing law / contracting entity;
- B2B/consumer scope;
- payment, VAT/invoicing;
- cancellation/refunds;
- warranty/disclaimer language;
- limitation of liability / indemnity;
- IP/confidentiality;
- acceptable use;
- incident obligations.

**Status: NOT COMPLETED.**

Do not present working drafts as final legal terms.

## E. First-user evidence — cannot be simulated

| Item | Status |
|---|---|
| 3–5 genuinely engaged companies identified | OPEN |
| Bounded workflow for each company | OPEN |
| Named human reviewer for each company | OPEN |
| Company acceptance of beta limitations | OPEN |
| Real usage / feedback cycle | OPEN |
| Repeated problem signals across independent workflows | OPEN |

## Launch states

### State 1 — Engineering candidate
Achieved when code/tests/docs are ready.

**Current status: substantially achieved.**

### State 2 — Ready to recruit controlled participants
Requires:
- safe beta deployment or controlled access path;
- onboarding dry run;
- support contact;
- explicit workflow/data boundaries.

**Current status: close, not yet complete.**

### State 3 — Unpaid / controlled real-workflow beta
May be possible before full paid launch if legal/privacy risk is appropriately bounded and the operator chooses that route.

Do not assume this is legally cleared merely because no money is charged.

### State 4 — Paid Founding Beta
Requires all legal/commercial/data blockers above to be closed.

**Current status: NOT YET AUTHORIZED / NOT LEGALLY COMPLETE.**

## Scope guard

Beta exists to measure CFC + HAWM behavior in real workflows, not to maximize feature count.

If a proposed feature does not improve measurement quality, test safety, or enable a real bounded workflow, it is not a Founding Beta priority.
