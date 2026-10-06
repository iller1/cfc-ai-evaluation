# HAWM Snapshot Identity Registry v0.1

Date: 2026-10-06  
Status: **IMPLEMENTATION CANDIDATE — NOT YET PRODUCTION PROMOTED**

## Purpose

Persist an independent host-side identity anchor for every new HAWM snapshot so
State Integrity v0.1 can compare the observed current payload with the identity
registered when the snapshot was created.

This registry does not modify the frozen CFC Anchor `0.2.90rc1`.

## Adapter contract

Version:

`HAWM_STATE_IDENTITY_ADAPTER_V0_1`

For newly saved Pro Beta HAWM snapshots:

- `case_id = HAWM_PRO_BETA_STATE`
- `arm_id = HAWM_WORKING_STATE`
- `state_id = snapshot_id`
- `lineage_id = conversation_id`
- `previous_state_id = exact previously persisted snapshot_id, or null for the first snapshot`
- `registered_snapshot_fingerprint = SHA-256(canonical JSON state payload)`

These are host identity mappings only. They do not establish evidence truth,
evidence applicability, source independence, CFC closure or execution
permission.

## No historical backfill

Existing snapshots created before this registry are not assigned synthetic
identity receipts.

If an exact persisted identity receipt is absent, the downstream State
Integrity integration must fail closed as unresolved. A later process must not
reconstruct a receipt and present it as if it existed at snapshot creation
time.

## Persistence boundary

The identity receipt is stored separately from the snapshot payload.

This allows a same-`snapshot_id` / changed-payload condition to be detected by
comparing the current canonical payload fingerprint against the fingerprint
registered at creation time.

The receipt is scoped to the same owned conversation as the snapshot.

## Partial-write rule

Snapshot creation and identity receipt creation are separate host persistence
operations in v0.1.

If snapshot persistence succeeds but receipt persistence fails, the save
operation surfaces the failure. The resulting snapshot has no valid identity
anchor and therefore must not later be treated as `STATE_VALID`.

This is fail-closed. Atomic persistence may be added in a later version without
rewriting historical receipts.

## Promotion gate

Before production promotion:

1. in-memory registry acceptance passes;
2. PostgreSQL round-trip and ownership checks pass;
3. legacy snapshot without receipt remains unresolved/not registered;
4. same snapshot ID with changed payload produces
   `STATE_INVALID / SNAPSHOT_FINGERPRINT_MISMATCH`;
5. exact predecessor is persisted for sequential snapshots;
6. no frozen CFC artifact changes;
7. production State Integrity assessment derives expectations from this
   persisted server-side receipt, not request-provided identity claims;
8. production read-only acceptance is recorded separately.

Until these gates are satisfied:

`IMPLEMENTATION_CANDIDATE_ONLY`
