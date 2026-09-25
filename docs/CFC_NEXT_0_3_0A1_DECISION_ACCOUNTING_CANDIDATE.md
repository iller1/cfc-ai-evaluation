# CFC-next 0.3.0a1 decision-accounting candidate

## Scope

This is a separately versioned candidate layered over the frozen CFC Anchor
0.2.90rc1 runtime.

The frozen wheel is not edited or replaced.

The candidate implements only the two repairs already approved by the readiness
chain:

1. Repair A — SHARED_GENERIC_NODE_VALIDATOR
2. Repair B — EXACT_REQUIRED_OBLIGATION_ENDPOINT_ADMISSION

All downstream exact binding, attestation, universe, closure, and persistence
logic remains frozen.

## Repair A

Internal generic-accounting registration and the public candidate draft share
one validator.

It preserves the exact three-field node identity, requires nonblank node type
and identifier, rejects source-semantic node families, preserves typed
dependency constraints, and permits the canonical blank middle field only for
LINEAGE and COMMON_MODE.

## Repair B

The candidate no longer requires every accounting endpoint to be selected
support.

A mixed selected/non-selected endpoint set is admitted only when all of the
following hold in the fresh exact decision context:

- every endpoint is present in the evaluated snapshot;
- the supplied selected-support map equals the engine-selected map exactly;
- the supplied node equals a freshly derived decision_level_required obligation;
- the supplied endpoint set equals that exact obligation;
- the decision context remains bound to the same retrieval scope, evidence,
  claims, requirements, and text.

No selected-support map expansion is used.

## Acceptance gate

The existing frozen-reference manifest is not weakened.

Candidate acceptance requires:

- 14/14 positive minimal blockers close through the public
  draft -> verify/install -> finalize lifecycle;
- 12/12 negative controls reject or remain non-authorizing;
- zero unexpected BOUND negative paths;
- frozen CFC Anchor 0.2.90rc1 remains unchanged;
- historical frozen results are not rescored.

Status is experimental until the acceptance workflow passes.
