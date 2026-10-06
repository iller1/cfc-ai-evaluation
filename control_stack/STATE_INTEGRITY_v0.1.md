# State Integrity v0.1

Date: 2026-10-06

Status: IMPLEMENTATION CANDIDATE — NOT YET PRODUCTION PROMOTED

## Purpose

State Integrity v0.1 verifies that a represented state belongs to the expected case, arm, lineage and current snapshot before later Control Stack layers rely on it.

It is intentionally narrow.

It does not decide evidence applicability, continuity authority, CFC closure or action permission.

Boundary:

EXPLICIT_IDENTITY_LINEAGE_AND_SNAPSHOT_BINDING_ONLY

Authorization boundary:

DOES_NOT_AUTHORIZE_CLOSURE

## Inputs

Observed state record:

- case_id
- arm_id
- state_id
- snapshot_id
- lineage_id
- previous_state_id
- state_payload

Independent expectation:

- case_id
- arm_id
- current_snapshot_id
- lineage_id
- expected_previous_state_id
- registered_snapshot_fingerprint

The expectation is a binding target, not a field copied from the observed record.

## Outputs

### STATE_VALID

Exact state binding was established.

Expected properties:

- binding_status = BOUND
- lineage_status = ESTABLISHED
- no unresolved violations
- propagation effect = NO_ADDITIONAL_BLOCK_FROM_STATE_INTEGRITY_ONLY

STATE_VALID does not authorize closure.

### STATE_UNRESOLVED

The state cannot be trusted as current, but there is not enough evidence to classify it as an explicit identity substitution.

Examples:

- current snapshot mismatch / stale state;
- predecessor mismatch;
- registered snapshot fingerprint missing;
- malformed or incomplete input.

Effect:

BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED

### STATE_INVALID

An explicit identity or integrity contradiction was found.

Examples:

- cross-case substitution;
- cross-arm substitution;
- lineage ID substitution;
- same registered snapshot identity with changed payload fingerprint.

Effect:

BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED

## v0.1 acceptance matrix

| Case | Expected |
| --- | --- |
| exact case/arm/snapshot/lineage/fingerprint | STATE_VALID |
| correct-looking content from wrong case | STATE_INVALID / CASE_ID_MISMATCH |
| correct-looking content from wrong arm | STATE_INVALID / ARM_ID_MISMATCH |
| wrong lineage identity | STATE_INVALID / LINEAGE_ID_MISMATCH |
| stale/non-current snapshot | STATE_UNRESOLVED / CURRENT_SNAPSHOT_MISMATCH |
| same snapshot identity with changed payload | STATE_INVALID / SNAPSHOT_FINGERPRINT_MISMATCH |
| wrong predecessor | STATE_UNRESOLVED / PREDECESSOR_MISMATCH |
| missing registered fingerprint | STATE_UNRESOLVED |
| malformed input | STATE_UNRESOLVED |
| canonical key reorder only | same fingerprint |
| multiple violations | preserve all detected violations |
| valid state | still DOES_NOT_AUTHORIZE_CLOSURE |

## Fail-closed rule

Any result other than STATE_VALID requires review and blocks carry-forward at the State Integrity boundary.

A later layer must not reinterpret STATE_UNRESOLVED or STATE_INVALID as STATE_VALID.

## Relationship to existing production work

Durable HAWM snapshot → CFC run binding already proves a bounded host-side historical input link.

State Integrity v0.1 generalizes the identity problem into a reusable Control Stack primitive for:

- case binding;
- arm binding;
- lineage binding;
- current snapshot binding;
- immutable state fingerprint checks.

This does not make the full Control Stack production verified.

## Promotion gate

Before production promotion:

1. acceptance matrix passes;
2. dedicated CI passes;
3. shared Control Stack schema regression remains green;
4. no frozen CFC artifact changes;
5. API/persistence integration derives expectations independently from persisted records;
6. authenticated production testing demonstrates at least:
   - exact valid binding;
   - cross-case substitution fail-closed;
   - cross-arm substitution fail-closed;
   - stale snapshot fail-closed;
   - same snapshot identity with changed payload fail-closed;
7. production receipt states the exact boundary and nonclaims.
