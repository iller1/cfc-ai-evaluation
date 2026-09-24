# CFC + HAWM Founding Beta v2 — Security, Incident & Support Basics

**Status:** operational draft for review before paid beta.

## Security boundary

Founding Beta is a controlled experimental service, not an SLA-backed production safety system.

Core controls currently intended:
- external authentication;
- workspace ownership checks;
- provider API keys remain browser-session/BYOK on the legacy Pro Beta path and are not persisted by the Pro Beta data model;
- dedicated Founding Beta v2 path contains no customer-content input;
- CFC frozen baseline is not silently modified;
- controller result and human decision remain distinct;
- measurement deletion is authenticated and workspace-scoped.

## Allowed data

Use only data permitted by the Round-1 Data Policy.

Do not submit:
- passwords,
- API keys/tokens,
- sensitive personal data,
- unnecessary personal data,
- customer secrets through feedback or measurement comments.

## Incident categories

Report as an incident if any of the following occurs:
- unauthorized workspace access;
- measurement data exposed to another customer;
- credential/API-key persistence where it should not occur;
- customer content unexpectedly persisted by the dedicated Founding Beta path;
- deletion request fails;
- frozen controller identity unexpectedly changes;
- production integrity/availability problem materially prevents agreed beta testing.

## Response process

1. Record incident ID and time discovered.
2. Contain the affected workflow/service where practical.
3. Preserve technical evidence without collecting unnecessary customer content.
4. Determine affected workspaces/data categories.
5. Notify affected participant according to agreed incident terms.
6. Correct the issue in an allowed version/layer.
7. Add regression evidence.
8. Record closure and any required follow-up.

## Contacts

- Beta support contact: `krzysztofsliwka@yahoo.co.uk`
- Security/privacy incident contact: `krzysztofsliwka@yahoo.co.uk`
- Emergency escalation contact: TO CONFIRM

Operational severity/containment procedure: `FOUNDING_BETA_OPERATOR_EMERGENCY_PROCEDURE.md`.

These must be real monitored addresses before paid onboarding.

## Support model — proposed

For Founding Beta:
- one primary support channel;
- no 24/7 SLA;
- reasonable-efforts support during the beta;
- product feedback and incident reports are distinct;
- roadmap influence does not create unlimited custom-development obligations.

Exact response-time commitments remain TO DECIDE and require alignment with the Beta Agreement.

## Availability

The beta may change, be interrupted or be temporarily unavailable.

No production availability guarantee should be offered unless separately agreed in writing.

## Release/change handling

Every material beta fix should have:
- version/commit identity;
- reproducible case;
- regression test where applicable;
- release note.

Frozen CFC baselines remain unchanged unless a separately versioned future controller line is explicitly opened.
