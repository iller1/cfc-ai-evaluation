# CFC + HAWM Founding Beta v2 — Paid Launch Blocker Matrix

Status date: 2026-09-24

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
| Measurement deletion endpoint | READY | authenticated workspace purge; live dry run PASS on 2026-09-24: 1 synthetic record deleted, 0 customer-content records deleted, empty history after refresh |
| Postgres 18 compatibility | READY | CI PASS |
| Current production baseline health | READY | Railway latest deployments SUCCESS |
| Frozen controller unchanged | READY | Anchor 0.2.90rc1 / Wrapper v1.23 remain frozen |
| Automatic 14-day retention enforcement | READY / LIVE | CI runs `#258` and `#259`: SUCCESS; Railway API deployment `08ba2c70-12c9-4e0a-96f4-cac234124e80` on commit `06ccbef5d1027627af7a2f687e66d6bf28a9782a`: SUCCESS; worker started and first production pass returned `NO_EXPIRED_RECORDS` |
| Live Founding Beta deployment | READY | deployed live on Railway 2026-09-23 after explicit authorization |
| Live onboarding dry run | READY | synthetic end-to-end run completed live: STOP/SUPPORTED, ALLOW/VERIFIED, STOP/UNRESOLVED; measurements persisted without customer content |

## B. Owner decisions — must be explicit

| Item | Status | Decision needed |
|---|---|---|
| Support contact | DECIDED | `krzysztofsliwka@yahoo.co.uk` |
| Security/privacy incident contact | DECIDED | `krzysztofsliwka@yahoo.co.uk` |
| Emergency escalation | PROCEDURE READY / OWNER CONFIRMATION | severity, containment and escalation procedure documented; backup/escalation person still to confirm |
| Named production operators | PROCEDURE READY / OWNER CONFIRMATION | minimum-access operator responsibilities/revocation documented; operator name(s) still to confirm |
| Billing mechanism | RECOMMENDATION READY / OWNER DECISION | prefer Stripe Payment Link if legal/accounting setup is ready; otherwise manual invoice; do not build custom billing |
| Refund policy | OPEN | commercial decision + legal review |
| Minimum beta activity | RECOMMENDATION READY / OWNER DECISION | working first-wave expectation: about 5 bounded real cases + one structured feedback summary per company |
| Paid vs no-charge first wave | OPEN | decide whether legal review precedes all external use or only payment |

## C. External factual verification

| Item | Status | Needed |
|---|---|---|
| Railway workload region | PARTIALLY VERIFIED | production API, frontend and Postgres currently report Railway region code `sfo`; current Railway public region docs identify US West Metal as California, USA, but the project-specific legacy/internal `sfo` → public-region mapping is not yet independently confirmed |
| Backup retention/expiry | OPEN / PARTIAL FACTS | Railway public docs state scheduled volume backups can retain daily backups 6 days, weekly 27 days, monthly 89 days; current connected project tooling does not expose whether this Postgres volume has a backup schedule or PITR enabled, so project-specific backup configuration remains to verify |
| Encryption/security disclosures | VERIFIED AT PROVIDER LEVEL | Railway DPA states databases are encrypted at rest and secure transport controls are used; Railway support documentation additionally states data at rest, including volumes and backups, is AES-256 encrypted automatically |
| Subprocessor list | PARTIALLY VERIFIED | Railway DPA points to its Trust Center as the authoritative current list and requires notice before new subprocessors are enabled; exact current list should be retained from the Trust Center for the legal/customer pack |

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

**Current status: engineering/onboarding conditions met; recruitment still depends on remaining owner/external/privacy decisions.**

### State 3 — Unpaid / controlled real-workflow beta
May be possible before full paid launch if legal/privacy risk is appropriately bounded and the operator chooses that route.

Do not assume this is legally cleared merely because no money is charged.

### State 4 — Paid Founding Beta
Requires all legal/commercial/data blockers above to be closed.

**Current status: NOT YET AUTHORIZED / NOT LEGALLY COMPLETE.**

## Scope guard

Beta exists to measure CFC + HAWM behavior in real workflows, not to maximize feature count.

If a proposed feature does not improve measurement quality, test safety, or enable a real bounded workflow, it is not a Founding Beta priority.
