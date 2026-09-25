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
