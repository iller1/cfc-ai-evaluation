# CFC-next decision-accounting repair surface

## Purpose

Prepare a minimal repair specification for a future CFC-next implementation
without modifying frozen CFC Anchor 0.2.90rc1.

The preceding research established two broad structural failure classes:

1. engine-emitted generic obligation nodes that the accounting schema itself
   rejects (`LINEAGE` and `COMMON_MODE`);
2. schema-valid mixed selected/excluded obligations that the frozen core can
   bind and close, but the supported public draft constructor rejects because
   every accounting endpoint is required to be selected support.

This review is read-only and inspects the exact frozen source surfaces that
create, validate, register, bind, and publicly construct those obligations.

## Constraint

No frozen source, policy, registry semantics, or historical result may be
modified in this branch.

Any repair described here is a CFC-next design proposal only.
