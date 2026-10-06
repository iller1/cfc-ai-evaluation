# Production State Integrity deployment evidence — 2026-10-06

Status: **DEPLOYED / SCHEMA-GATED / AUTHENTICATED FUNCTIONAL ACCEPTANCE PENDING**

This receipt records what was actually established for State Integrity v0.1 in the Pro Beta production system on 2026-10-06.

It does **not** claim full production verification.

## Production API release

Production branch:

`pro-beta-v0.1`

State Integrity production port PR:

`#92 — Production API: State Integrity v0.1 identity-bound read-only assessment`

Merge commit:

`276a4497d472cb82a7deea0a295d678ea6af9072`

Railway API deployment:

`36f6ee45-fa94-4eca-8cf8-b94d11b22acd`

Deployment result:

`SUCCESS`

## Bootstrap gate correction

The first deployment exposed a verification gap in the database bootstrap contract: `schema.sql` created `hawm_snapshot_identities`, but startup did not yet require that table in `EXPECTED_TABLES`.

The gap was corrected separately instead of being ignored.

Bootstrap correction PR:

`#93 — Production API: require HAWM identity registry in bootstrap`

Production branch head after correction:

`cbfd107859b75c5c6451dcec4b962aa48dc190f6`

Relevant correction commit:

`29a569c593cbe82811c7af9dca6673fd5a3ca820`

Railway API deployment:

`c71c6c98-0734-4b7b-9283-532bb7200fe7`

Deployment result:

`SUCCESS`

Production startup reported:

`PRO_BETA_DATABASE_READY tables=audit_reports,benchmark_manual_labels,benchmark_runs,cfc_runs,conversations,founding_beta_measurements,founding_beta_retention_reports,hawm_snapshot_identities,hawm_snapshots,messages,usage_events,users,workspaces`

Therefore the identity registry table is part of the production startup fail-closed schema check.

## Production frontend control

State Integrity UI PR:

`#97 — Pro Beta UI: add State Integrity production control`

Merge commit:

`9766f01dfd18d2037dc17d5bc269b07681c8c6f5`

Railway frontend deployment:

`5d6d9804-7eb9-49cf-a9d2-c6d6fa7e8672`

Deployment result:

`SUCCESS`

The deployed UI exposes the authenticated read-only control:

`Sprawdź integralność stanu`

which calls:

`GET /api/conversations/{conversation_id}/state-integrity`

The control does not save HAWM state and does not execute CFC.

## CI evidence

The State Integrity release and UI changes passed the relevant Pro Beta contract suites before merge.

The release preserved existing production gates including Evidence Drift, State Monitor, PostgreSQL integration, API/service/auth contracts and frontend regression tests.

Added acceptance coverage includes:

- `control_stack.test_state_integrity`;
- `pro_beta.test_snapshot_identity_registry`;
- `pro_beta.test_state_integrity_adapter`;
- State Integrity frontend route/rendering checks.

## Deployed semantic boundary

Observed state identity is derived from persisted HAWM state/history.

Expected state identity is derived only from the separately persisted server-side `HAWMSnapshotIdentity` receipt created when a new HAWM snapshot is saved after registry deployment.

The request does not supply fingerprint, predecessor, lineage, case ID, arm ID or snapshot ID as authority.

Historical snapshots without a receipt are not backfilled.

`STATE_VALID` means only that represented host state matches its registered identity/lineage contract.

It does not establish evidence truth, evidence applicability, source independence, CFC closure or execution permission.

Authorization boundary:

`DOES_NOT_AUTHORIZE_CLOSURE`

## Claim ceiling

Established:

- State Integrity v0.1 code is deployed in the production API;
- the production image contains the State Integrity primitive;
- the identity registry schema is present;
- startup verifies the identity registry table fail-closed;
- the authenticated frontend control is deployed;
- release and frontend CI passed.

Not yet established in this receipt:

- authenticated end-to-end live response semantics from a real owned conversation through the deployed State Integrity route.

Therefore the status remains:

`PRODUCTION_DEPLOYED_SCHEMA_GATED_FUNCTIONAL_ACCEPTANCE_HOLD`

and not:

`PRODUCTION_VERIFIED`

## Closure sequence

The HOLD should be closed only through the normal authenticated user path.

Preferred production sequence:

1. On an untouched pre-registry HAWM conversation, run State Integrity before saving a new snapshot.
   Expected: `STATE_UNRESOLVED / SNAPSHOT_IDENTITY_NOT_REGISTERED`.
2. Save the current HAWM state normally, creating a new snapshot and server-side identity receipt.
3. Run State Integrity again.
   Expected: `STATE_VALID / EXACT_STATE_BINDING_ESTABLISHED`.
4. Confirm:
   - `expectation_source = PERSISTED_HAWM_SNAPSHOT_IDENTITY`;
   - `binding_status = BOUND`;
   - `lineage_status = ESTABLISHED`;
   - `read_only = true`;
   - `authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`.
5. Add a separate production verification receipt. Do not rewrite this HOLD receipt.
