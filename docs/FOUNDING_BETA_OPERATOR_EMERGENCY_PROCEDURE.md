# CFC + HAWM Founding Beta v2 — Production Operator & Emergency Procedure

**Status:** decision-ready operational procedure. Final named operator(s) still require owner confirmation.

## Principle

Production access is restricted to the minimum necessary for operation, incident handling and release verification.

Normal Founding Beta use must not require an operator to inspect customer documents, prompts, model replies or raw evidence.

## Production operator responsibilities

A production operator may:
- inspect Railway service health, deployment status and logs;
- verify database/schema health;
- investigate authentication, ownership, persistence and deletion failures;
- deploy already-reviewed Founding Beta application changes;
- disable or contain an affected service when needed to reduce risk;
- verify that the frozen CFC identities remain unchanged.

A production operator must not:
- retrieve customer business content merely for convenience;
- ask a participant to resend sensitive material when technical metadata is sufficient;
- bypass workspace ownership controls;
- alter frozen CFC / Wrapper / Demonstrator artifacts as an incident workaround;
- copy production records into personal/local stores without a documented diagnostic need.

## Current access decision still required

Before paid onboarding, the owner must confirm:
- primary production operator name;
- whether any backup operator exists;
- which individual accounts are authorized for GitHub, Railway and authentication-provider administration;
- that MFA/2FA is enabled where supported.

Until confirmed, do not describe production access as formally assigned.

## Emergency severity

### SEV-1 — contain immediately

Examples:
- unauthorized cross-workspace access;
- customer content unexpectedly persisted by the dedicated Founding Beta path;
- credential/token persistence;
- confirmed exposure of measurement data to the wrong participant;
- frozen controller identity unexpectedly changed in production.

Default response:

1. stop or isolate the affected path where practical;
2. preserve minimal technical evidence;
3. do not collect additional customer content;
4. identify affected workspace/data categories;
5. record incident ID, UTC discovery time and operator;
6. notify the project owner/security contact;
7. assess whether participant notification is required;
8. only restore after the failure mode is understood and a regression check exists.

### SEV-2 — urgent but bounded

Examples:
- deletion endpoint fails;
- 14-day retention worker fails repeatedly;
- authentication or workspace ownership path unavailable;
- production deployment breaks Founding Beta onboarding.

Response:

1. prevent new affected operations if continuing would increase risk;
2. diagnose from logs/metadata;
3. fix in an allowed application layer;
4. run regression tests;
5. record deploy/commit identity;
6. verify recovery.

### SEV-3 — normal beta defect

Examples:
- unclear UI;
- false stop / false allow finding with no security exposure;
- non-blocking presentation issue.

Handle through normal beta feedback and release process.

## Emergency contact path

Current support/security contact:

`krzysztofsliwka@yahoo.co.uk`

This address is the operational contact already selected for the Founding Beta.

A separate backup/escalation person is **TO CONFIRM** before paid onboarding.

## Access revocation

Revoke privileged access immediately when:
- an operator no longer needs production access;
- credentials are suspected compromised;
- a role changes;
- an account is shared or cannot be individually attributed.

After revocation:
- rotate affected secrets where appropriate;
- review recent privileged activity;
- record completion.

## Evidence discipline

Incident evidence should prefer:
- timestamps;
- service/deployment IDs;
- commit hashes;
- system version;
- workspace-scoped technical identifiers;
- error/reason codes;
- counts and aggregate state.

Avoid customer content unless it is strictly necessary and separately approved.

## Review triggers

Review this procedure:
- before first paid participant;
- after adding/removing an operator;
- after a security/privacy incident;
- after infrastructure/authentication changes.
