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

## Result

CI reproduced the stale-relation boundary with all three minimal relation families:
common-mode, root-origin, and generic dependency `data_source`.

In every case:

- claim state = `VERIFIED`;
- `control_closure = false`;
- the only false gate is `decision_support_closure_valid`;
- the engine-selected support map contains current E1 only;
- stale E2 is not claim-owned and is not classified as selected justificatory support;
- nevertheless the decision-level generic-dependency assessment creates an
  obligation whose endpoint set contains both E1 and stale E2;
- `make_decision_support_closure_certificate()` cannot find bound accounting
  for that obligation and returns `None`.

### Public accounting reachability

The public accounting surface cannot represent the exact engine obligation
without changing the decision state.

For `GENERIC_DEPENDENCY/data_source`:

- exact selected-support map `{c1: [E1]}` is rejected with
  `generic dependency endpoints must be selected supports`;
- expanding the map to `{c1: [E1, E2]}` permits draft creation, but that map
  no longer matches the engine-selected support state because E2 is stale and
  excluded from selected support.

For `COMMON_MODE` and `ROOT_ORIGIN`:

- the engine emits generic-dependency obligation nodes
  `("COMMON_MODE", "", "group:shared")` and
  `("LINEAGE", "", "general-record:root:shared")`;
- the public generic-accounting draft rejects both as
  `invalid generic dependency node` because its public draft contract requires
  all three node fields to be nonblank;
- the separate public source-dependency accounting API cannot satisfy this
  specific closure path: the frozen closure function looks for bound generic
  accounting for these obligations, and source-dependency drafts also require
  both endpoints to be selected supports.

## Classification

**DECISION-ACCOUNTING PUBLIC REACHABILITY BOUNDARY**

The frozen engine creates decision-level authorization obligations involving a
stale, non-selected endpoint, while the public accounting surface requires
accounting endpoints to be selected supports. Two engine-emitted node shapes
also cannot be represented by the public generic-accounting draft schema.

This is stronger than the earlier phenomenological stale-relation finding, but
it is still recorded as a contract/reachability boundary rather than a
`false block`. No normative external contract has yet been established that
requires this state to be closable.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

