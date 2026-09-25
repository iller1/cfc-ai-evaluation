# Decision support closure path inspection

## Goal

Locate, read-only, the exact frozen-engine path that produces
`decision_support_closure_valid` in the stale-relation boundary.

This step follows the empirical narrowing already established:

- relation-level persistence is polarity-insensitive;
- claim-subject-insensitive;
- stale-age-insensitive over 3-92 days;
- bound to stale E2 participating in the evaluated snapshot;
- shared source semantics alone does not trigger it;
- shared root/origin/extractor/common-mode or any tested generic dependency does.

The inspection searches frozen runtime symbols and source references involving
decision support closure, claim/support relations, support universe construction,
selected support, and dependency relations.

## Constraint

Read-only introspection only. CFC Anchor 0.2.90rc1 is not modified.

## Decision rule

After CI, identify the smallest frozen function chain that explains why a stale
record can be excluded from active claim support while its shared relation still
affects downstream authorization.

Only then choose the next metamorphic test.
