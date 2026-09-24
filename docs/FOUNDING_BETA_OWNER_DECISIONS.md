# CFC + HAWM Founding Beta v2 — Owner Decisions Sheet

**Purpose:** reduce the remaining owner-controlled blockers to explicit yes/no decisions.

## Decision 1 — Primary production operator

Recommended default:

- Primary production operator: project owner/founder.
- Access only when needed for deployment, incident handling, deletion/retention verification or service recovery.
- Individual accounts only where supported.
- MFA/2FA enabled where supported.

Owner decision: **CONFIRM / CHANGE**

## Decision 2 — Backup / emergency operator

Recommended default for the first small beta:

- no standing backup operator unless a trusted second person actually needs production access;
- document the absence of a backup operator rather than granting unnecessary privileged access;
- emergency escalation remains via the monitored support/security email until a real backup person is appointed.

This follows least-privilege: do not create privileged access merely to make the role chart look complete.

Owner decision: **CONFIRM / APPOINT BACKUP**

## Decision 3 — Minimum participant activity

Recommended first-wave minimum:

- 1 agreed bounded workflow;
- 1 named human reviewer;
- approximately 5 real cases during the beta period;
- 1 short structured feedback summary;
- immediate reporting of false allow, false stop, unexpected persistence or access issues.

Reason: enough signal to learn whether the participant is genuinely using the beta without turning the £10 beta into a heavy service contract.

Owner decision: **CONFIRM / CHANGE**

## Decision 4 — Billing mechanism

Recommended default:

- do not build custom billing;
- use Stripe Payment Link if legal/accounting setup is ready;
- otherwise use manual invoice/bank transfer for the first few companies.

Paid activation remains blocked until legal/accounting questions are resolved.

Owner decision: **STRIPE / MANUAL INVOICE / DEFER**

## Decision 5 — Refund/cancellation

Do not finalize wording before legal review.

Recommended commercial direction only:

- simple cancellation;
- no long commitment;
- avoid promising refunds or non-refundable status until counsel/accounting confirms the wording.

Owner decision: **DEFER TO LEGAL REVIEW** (recommended)

## Decision 6 — First external wave

Recommended default:

- recruit 3–5 companies;
- one workflow per company to start;
- low-risk bounded use only;
- human final decision mandatory;
- NO CUSTOMER CONTENT BY DEFAULT;
- scale only after observing real feedback load.

Owner decision: **CONFIRM / CHANGE**

## Current status

Items already technically prepared:

- operator/emergency procedure;
- support/security contact;
- recruitment pack;
- exact new-company walkthrough;
- billing decision note;
- 14-day automatic source-measurement retention;
- self-service measurement deletion;
- no active Railway customer volume backups/PITR on the current plan.

Still external or user-dependent:

- fresh external-style onboarding timing run;
- named primary operator confirmation;
- backup-operator decision;
- billing selection;
- legal review;
- first 3–5 companies.
