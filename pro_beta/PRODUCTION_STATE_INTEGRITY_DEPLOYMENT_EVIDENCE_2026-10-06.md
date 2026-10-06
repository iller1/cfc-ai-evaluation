# Production State Integrity deployment evidence — 2026-10-06

Status: **DEPLOYED / SCHEMA-GATED / AUTHENTICATED FUNCTIONAL ACCEPTANCE PENDING**

This receipt records what was actually established for State Integrity v0.1 in the Pro Beta production API on 2026-10-06.

It does **not** claim full production verification.

## Production release

Production branch:

`pro-beta-v0.1`

State Integrity production port PR:

`#92 — Production API: State Integrity v0.1 identity-bound read-only assessment`

Merge commit:

`276a4497d472cb82a7deea0a295d678ea6af9072`

Railway deployment:

`36f6ee45-fa94-4eca-8cf8-b94d11b22acd`

Deployment result:

`SUCCESS`

The deployed source metadata reported:

- repository: `iller1/cfc-ai-evaluation`
- branch: `pro-beta-v0.1`
- commit: `276a4497d472cb82a7deea0a295d678ea6af9072`

## Bootstrap gate correction

The first deployment exposed a verification gap in the database bootstrap contract: the new `hawm_snapshot_identities` table was created by `schema.sql`, but was not yet included in `EXPECTED_TABLES`.

That meant application startup did not independently fail closed if this table were absent.

The gap was corrected separately rather than being ignored.

Bootstrap correction PR:

`#93 — Production API: require HAWM identity registry in bootstrap`

Production branch head after the correction:

`cbfd107859b75c5c6451dcec4b962aa48dc190f6`

Relevant correction commit:

`29a569c593cbe82811c7af9dca6673fd5a3ca820 — fix: require HAWM identity registry at database bootstrap`

Railway deployment:

`c71c6c98-0734-4b7b-9283-532bb7200fe7`

Deployment result:

`SUCCESS`

## Database bootstrap evidence

The production startup log for deployment
`c71c6c98-0734-4b7b-9283-532bb7200fe7`
reported:

`PRO_BETA_DATABASE_READY tables=audit_reports,benchmark_manual_labels,benchmark_runs,cfc_runs,conversations,founding_beta_measurements,founding_beta_retention_reports,hawm_snapshot_identities,hawm_snapshots,messages,usage_events,users,workspaces`

Therefore `hawm_snapshot_identities` was present and included in the startup fail-closed table verification.

## CI evidence

Before production merge, PR #92 completed successfully with the production Pro Beta contract suite.

The suite preserved existing production gates, including:

- Evidence Drift;
- State Monitor;
- PostgreSQL integration;
- API/service/auth contracts;

and added:

- `control_stack.test_state_integrity`;
- `pro_beta.test_snapshot_identity_registry`;
- `pro_beta.test_state_integrity_adapter`.

The release also added `COPY control_stack /app/control_stack` to the production Dockerfile so the deployed API image contains the State Integrity primitive it imports.

## Production interface now deployed

Read-only route:

`GET /api/conversations/{conversation_id}/state-integrity`

Design boundary:

- observed current identity is derived from persisted HAWM state/history;
- expected identity is derived from the separately persisted server-side `HAWMSnapshotIdentity` receipt;
- the request cannot supply fingerprint, predecessor, lineage, case ID, arm ID or snapshot ID as authority;
- historical snapshots without an identity receipt remain unresolved;
- `STATE_VALID` does not authorize CFC closure or execution.

## Claim ceiling

The following are established:

- State Integrity v0.1 code is deployed in the production API;
- the production image contains the State Integrity module;
- the identity registry schema is present;
- startup now verifies the identity registry table fail-closed;
- the production release passed the preserved Pro Beta CI gates;
- the production deployment is healthy according to Railway.

The following is **not yet established** in this receipt:

- an authenticated end-to-end request to the live `/state-integrity` route using a real owned conversation and a newly registered HAWM snapshot;
- live confirmation of the returned `STATE_VALID`, `STATE_INVALID` or `STATE_UNRESOLVED` semantics through that authenticated production route.

The execution environment used to prepare this receipt could not resolve the public Railway hostname for a direct HTTP acceptance request, and no user bearer credential was available for authenticated endpoint testing.

Therefore the status remains:

`PRODUCTION_DEPLOYED_SCHEMA_GATED_FUNCTIONAL_ACCEPTANCE_HOLD`

and **not**:

`PRODUCTION_VERIFIED`

## Reopen / closure condition

This HOLD can be closed only after an authenticated production acceptance demonstrates, at minimum:

1. a newly saved HAWM snapshot receives a persisted identity receipt;
2. the live State Integrity route reads that persisted receipt;
3. exact current state returns the expected identity-only valid result;
4. no-receipt legacy state remains unresolved;
5. no result upgrades authority beyond `DOES_NOT_AUTHORIZE_CLOSURE`.

A later production verification receipt should be added rather than rewriting this document.
