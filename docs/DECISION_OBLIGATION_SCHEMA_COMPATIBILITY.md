# Decision obligation schema compatibility

## Goal

Test whether exact decision-level generic dependency obligation nodes emitted by
the frozen engine are representable by the frozen accounting schemas that are
supposed to account for them.

The prior reviews established two different symptoms:

- `GENERIC_DEPENDENCY/data_source` has a schema-valid three-field node, but the
  public draft rejects the exact mixed selected/stale endpoint set;
- `COMMON_MODE` and `ROOT_ORIGIN` produce nodes with an empty middle field and
  the public generic-accounting draft rejects them as invalid nodes.

This review asks whether the latter mismatch exists only in the public wrapper
or already between two frozen core contracts:

1. engine obligation emission;
2. internal generic-accounting registry schema.

Each relation is executed in a fresh subprocess.

## Decision rule

If the frozen engine emits a required obligation node that the frozen internal
generic-accounting registry itself rejects on node-schema grounds, classify it
as an **engine-emitted / accounting-schema incompatibility**.

Do not conflate that with the separate selected/excluded endpoint reachability
inconsistency already established for `data_source`.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

## Result

All three isolated cases reproduced `VERIFIED/STOP` with only
`decision_support_closure_valid=false`, and all three frozen assessments marked
the relation `decision_level_required=true` with classification
`DECISION_GENERIC_MODELED_SNAPSHOT_MIXED_UNCOVERED`.

### COMMON_MODE

Frozen engine-emitted obligation node:

`("COMMON_MODE", "", "group:shared")`

The node has arity 3, but its middle component is blank.

- frozen internal `register_decision_generic_dependency_accounting`:
  **REJECTED** — `ValueError: invalid generic dependency node`;
- public `draft_decision_generic_dependency_accounting`:
  **REJECTED** — `ValueError: invalid generic dependency node`.

### ROOT_ORIGIN

Frozen engine-emitted obligation node:

`("LINEAGE", "", "general-record:root:shared")`

Again the node has arity 3 with a blank middle component.

- frozen internal registry:
  **REJECTED** — `ValueError: invalid generic dependency node`;
- public draft:
  **REJECTED** — `ValueError: invalid generic dependency node`.

### GENERIC_DEPENDENCY / data_source

Frozen engine-emitted obligation node:

`("DEPENDENCY", "data_source", "shared")`

All three components are nonblank.

- frozen internal registry:
  **ACCEPTED**, binding state `PENDING`;
- public draft with the exact engine-selected support map:
  **REJECTED** — `ValueError: generic dependency endpoints must be selected supports`.

This confirms two separate contract failures.

## Classification

### A. COMMON_MODE and ROOT_ORIGIN

**ENGINE-EMITTED / ACCOUNTING-SCHEMA INCOMPATIBILITY**

The frozen decision engine emits required generic-accounting obligation nodes
that the frozen generic-accounting registry itself declares structurally
invalid. The mismatch therefore exists below the public Controller wrapper.

### B. GENERIC_DEPENDENCY / data_source

**PUBLIC SELECTED/EXCLUDED ENDPOINT REACHABILITY INCONSISTENCY**

The frozen internal accounting schema accepts the exact node and exact mixed
endpoint obligation, and prior core-bindability testing showed the core can close
it. The supported public constructor alone makes the exact obligation
unrepresentable by requiring every accounting endpoint to be selected support.

These mechanisms must remain separate in subsequent analysis.

Neither result changes frozen CFC Anchor 0.2.90rc1.

