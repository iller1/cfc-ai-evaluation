# Production checkpoint — State Integrity v0.1

Date: 2026-10-06

## Closure label

**STATE INTEGRITY v0.1: DEPLOYED + SCHEMA VERIFIED — FUNCTIONAL ACCEPTANCE HOLD**

This checkpoint records what has been demonstrated in the production deployment and what has not yet been demonstrated.

It must not be cited as `PRODUCTION VERIFIED`.

It does **not** modify or extend the semantics of frozen CFC Anchor `0.2.90rc1`.

## Production artifacts

Production branch:

`pro-beta-v0.1`

State Integrity production API merge:

`276a4497d472cb82a7deea0a295d678ea6af9072`

Railway deployment:

`36f6ee45-fa94-4eca-8cf8-b94d11b22acd`

Deployment status:

`SUCCESS`

Bootstrap-gate strengthening merge:

`cbfd107859b75c5c6451dcec4b962aa48dc190f6`

Railway deployment:

`c71c6c98-0734-4b7b-9283-532bb7200fe7`

Deployment status:

`SUCCESS`

Main bootstrap parity merge:

`7016f60bd3a18f7e077efeab076a4f7cb3303a90`

## What is deployed

The production API now contains:

- `STATE_INTEGRITY_V0_1`;
- the persisted `HAWMSnapshotIdentity` receipt;
- canonical SHA-256 fingerprint registration for newly saved HAWM snapshots;
- explicit state ID, conversation lineage and exact predecessor binding;
- no historical identity backfill;
- read-only authenticated route:
  `GET /api/conversations/{conversation_id}/state-integrity`;
- fail-closed adapter semantics;
- Docker packaging of the required `control_stack/state_integrity.py` module.

The expected side of the State Integrity comparison is derived from the persisted server-side identity receipt, not from request-provided identity fields.

## CI evidence

Before production release, the Pro Beta contract suite passed with:

- existing Evidence Drift coverage preserved;
- existing State Monitor coverage preserved;
- State Integrity primitive tests;
- snapshot identity registry tests;
- read-only State Integrity adapter tests;
- PostgreSQL persistence and ownership tests;
- database bootstrap tests.

The release PR and the bootstrap-strengthening PR both passed the Pro Beta contract gate before merge.

## Production schema verification

The final production deployment emitted:

`PRO_BETA_DATABASE_READY`

with the required table set including:

`hawm_snapshot_identities`

This verifies that the production database bootstrap executed successfully and that the identity registry table was present at startup.

The bootstrap gate now treats absence of that table as:

`DATABASE_SCHEMA_INCOMPLETE`

rather than allowing startup to report database readiness.

## Functional acceptance status

**HOLD**

An authenticated production request to the new State Integrity endpoint has not yet been recorded in this checkpoint.

The current session did not have an end-user bearer credential suitable for executing an authenticated production HAWM workflow.

Therefore this checkpoint does not claim that the complete authenticated endpoint path has been production-verified.

## Required closure sequence

To promote this checkpoint to:

`STATE INTEGRITY v0.1: PRODUCTION VERIFIED`

record one controlled authenticated production sequence demonstrating:

1. save a new HAWM snapshot after identity-registry deployment;
2. call `GET /state-integrity` for the exact current snapshot;
3. receive:
   - `STATE_VALID`;
   - `EXACT_STATE_BINDING_ESTABLISHED`;
   - `expectation_source = PERSISTED_HAWM_SNAPSHOT_IDENTITY`;
   - `read_only = true`;
   - `authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`;
4. demonstrate a controlled negative path without laundering identity authority;
5. confirm the endpoint itself performs no HAWM write and no CFC execution;
6. commit a separate immutable production verification receipt.

A legacy snapshot created before identity registration may also be used as a fail-closed check and should return:

`STATE_UNRESOLVED / SNAPSHOT_IDENTITY_NOT_REGISTERED`

## Claim ceiling

Even after functional acceptance, `STATE_VALID` means only that the represented host state matches its registered state identity and lineage contract.

It does not establish:

- evidence truth;
- evidence applicability;
- source independence;
- semantic correctness of free text;
- CFC closure;
- execution permission;
- general production readiness;
- general AI safety.

The authorization boundary remains:

`DOES_NOT_AUTHORIZE_CLOSURE`
