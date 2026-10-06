# State Integrity v0.1

Date: 2026-10-06  
Status: **IMPLEMENTATION CANDIDATE — NOT YET PRODUCTION PROMOTED**

## Purpose

State Integrity v0.1 establishes whether an observed state is bound to the expected case, arm, snapshot and lineage before downstream layers consume it.

It is a host-side Control Stack module.

It does **not** modify or reinterpret frozen CFC Anchor `0.2.90rc1`.

## Boundary

`EXPLICIT_IDENTITY_LINEAGE_AND_SNAPSHOT_BINDING_ONLY`

The module does not determine:

- evidence truth;
- evidence applicability;
- continuity authority;
- CFC closure;
- execution permission.

Every result preserves:

`authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`

## Inputs

Observed record:

- `case_id`;
- `arm_id`;
- `state_id`;
- `snapshot_id`;
- `lineage_id`;
- `previous_state_id`;
- explicit `state_payload`.

Independent expectation:

- expected `case_id`;
- expected `arm_id`;
- expected current `snapshot_id`;
- expected `lineage_id`;
- expected predecessor state;
- registered snapshot fingerprint.

The registered fingerprint is treated as an independently supplied identity anchor.

If no fingerprint is registered, the module does not infer identity.

## Outputs

### `STATE_VALID`

Returned only when:

- case matches;
- arm matches;
- lineage matches;
- observed snapshot is the expected current snapshot;
- predecessor matches;
- canonical state fingerprint matches the registered fingerprint.

Effect:

`NO_ADDITIONAL_BLOCK_FROM_STATE_INTEGRITY_ONLY`

This is not closure authorization.

### `STATE_UNRESOLVED`

Used when state identity cannot be fully established without proving substitution.

Examples:

- observed snapshot is not the expected current snapshot;
- predecessor mismatch;
- registered fingerprint missing;
- malformed/incomplete expectation.

Effect:

`BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED`

### `STATE_INVALID`

Used for direct integrity contradiction.

Examples:

- cross-case substitution;
- cross-arm substitution;
- lineage ID substitution;
- registered snapshot ID with changed payload/fingerprint.

Effect:

`BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED`

## Canonical fingerprint

The explicit state payload is serialized with deterministic JSON key ordering and hashed with SHA-256.

Equivalent object key order therefore produces the same fingerprint.

The fingerprint proves identity of the represented payload bytes after canonicalization.

It does not prove truth of the payload.

## v0.1 adversarial matrix

| Case | Expected |
| --- | --- |
| exact case/arm/snapshot/lineage/fingerprint | `STATE_VALID` |
| correct-looking state from another case | `STATE_INVALID / CASE_ID_MISMATCH` |
| correct-looking state from another arm | `STATE_INVALID / ARM_ID_MISMATCH` |
| wrong lineage ID | `STATE_INVALID / LINEAGE_ID_MISMATCH` |
| stale/non-current snapshot | `STATE_UNRESOLVED / CURRENT_SNAPSHOT_MISMATCH` |
| same snapshot ID, changed payload | `STATE_INVALID / SNAPSHOT_FINGERPRINT_MISMATCH` |
| predecessor mismatch | `STATE_UNRESOLVED / PREDECESSOR_MISMATCH` |
| no registered fingerprint | `STATE_UNRESOLVED / SNAPSHOT_FINGERPRINT_NOT_REGISTERED` |
| payload key reorder only | same fingerprint |
| multiple simultaneous substitutions | preserve all detected violations |
| incomplete expectation | fail closed as `STATE_UNRESOLVED` |

## Relationship to existing production controls

Durable HAWM snapshot → CFC run binding already proves one important host-side invariant:

a persisted CFC run can remain bound to the exact HAWM snapshot used for execution.

State Integrity v0.1 generalizes the identity problem into an explicit module contract.

Evidence Drift remains separate:

- State Integrity asks whether this is the intended state/snapshot/lineage.
- Evidence Drift asks whether explicit CFC-relevant evidence state changed relative to a run-bound baseline.

State Monitor remains separate:

- State Monitor asks whether a working-state transition silently cleared an unresolved marker without exact-current evaluation.

## Promotion gate

Before production promotion:

1. all primitive tests pass;
2. existing Control Stack schema tests remain green;
3. full repository regression remains green;
4. production integration derives expectations from persisted server-side state, not user-provided claims;
5. cross-case and cross-arm substitution are demonstrated fail-closed;
6. same-snapshot/different-content mismatch is demonstrated fail-closed;
7. stale snapshot is not silently treated as current;
8. no frozen CFC artifact changes;
9. production integration remains read-only unless a separate explicit persistence action is invoked.

Until those gates are satisfied, status remains:

`IMPLEMENTATION CANDIDATE`
