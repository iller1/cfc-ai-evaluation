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

## Frozen source localization

The inspection shows that the failure is localized to two duplicated admission
rules rather than the downstream closure machinery.

### Generic node domain

`dependency_nodes(f)` emits generic provenance nodes in these families:

- `("LINEAGE", "", id)`;
- `("COMMON_MODE", "", id)`;
- typed dependency nodes;
- `("EXTRACTOR", "extractor", id)`;
- source-semantic nodes, which are later removed from
  `raw_generic_dependency_nodes`.

`canonical_generic_dependency_node()` requires a 3-tuple and a nonblank
identifier, excludes source-semantic node types, and otherwise preserves a raw
generic node when no unique equivalence mapping applies. It does **not** require
the middle field to be nonblank.

The accounting validators are stricter than that canonical domain:

- frozen internal
  `register_decision_generic_dependency_accounting()` rejects any node with a
  blank component;
- public
  `draft_decision_generic_dependency_accounting()` applies the same
  all-three-components-nonblank rule.

That duplicated validator is the direct cause of the LINEAGE / COMMON_MODE
schema incompatibility.

### Mixed endpoint admission

The frozen internal registry accepts an exact accounting record whose
`selected_support_map` contains E1 only while its exact endpoint set contains
E1 + stale E2.

The public draft adds a stronger rule:

`set(evidence_ids) ⊆ selected_supports`

and rejects the exact mixed selected/excluded obligation before it can enter the
verified public lifecycle.

Downstream binding and closure are already exact-context fail-closed:

- selected-support-map hash must match the decision graph;
- node and endpoint set must exactly match the obligation;
- decision generic universe and obligation hashes must match;
- policy, ontology, provenance and equivalence commitments must match;
- the accounting row must be BOUND before it can satisfy closure.

The 11 core-bindability controls show that this downstream machinery can safely
resolve the exact mixed obligation once the accounting record exists.

## Minimal CFC-next repair specification

### Repair A — one shared generic-node validator

Replace the duplicated "all three fields must be nonblank" checks with one
shared predicate whose accepted structural domain is aligned with
`dependency_nodes` + `canonical_generic_dependency_node`.

Required properties:

1. node must remain an exact 3-tuple of strings;
2. node type and identifier must be nonblank;
3. source-semantic node types remain ineligible for generic accounting;
4. an empty middle field must be legal where it is part of the canonical node
   shape, including LINEAGE and COMMON_MODE;
5. typed DEPENDENCY dimensions remain constrained by the dependency ontology;
6. validation must not rewrite the node or alter its hash;
7. both the frozen-core-equivalent registry path and public Controller draft
   must use the same predicate in CFC-next.

Do not repair this by changing LINEAGE or COMMON_MODE identities merely to make
all three fields nonblank. Their current canonical identity is already consumed
by discovery, universe hashing and exact closure matching.

### Repair B — exact-obligation admission for non-selected endpoints

Replace the public draft rule

`evidence_ids ⊆ selected_supports`

with a stronger decision-context rule:

> A non-selected endpoint may appear in a generic accounting draft only when
> the exact node + exact endpoint set is a freshly derived
> `decision_level_required` obligation for the same exact decision context.

The admission check must require all of the following:

- all endpoints are present in the exact evaluated evidence/snapshot;
- the supplied selected-support map exactly matches the current decision graph;
- the supplied generic node exactly matches the freshly derived obligation;
- the endpoint set exactly matches that obligation;
- the obligation is `decision_level_required=true`;
- the obligation belongs to the same retrieval scope, snapshot, claim set,
  requirements and decision-context commitment.

This preserves the ability to account for selected/excluded relations required
by policy without permitting arbitrary excluded evidence to be attached to a
decision.

### Components that should remain unchanged

The current evidence indicates no need to weaken or redesign:

- `_decision_level_generic_dependency_assessments`;
- decision generic universe construction;
- `_find_bound_decision_generic_dependency_accounting`;
- exact context/hash binding;
- attestation verification;
- `make_decision_support_closure_certificate`;
- persistence commitments.

Those layers are what made the internal exact-bind controls fail closed and
allowed closure only for the exact required obligation.

## Mandatory CFC-next acceptance matrix

Positive regression cases:

1. `root_origin_shared` exact LINEAGE obligation becomes representable.
2. `origin_shared` exact LINEAGE obligation becomes representable.
3. `common_mode_group_shared` exact COMMON_MODE obligation becomes
   representable.
4. All 11 schema-valid dependency/extractor blockers can enter the supported
   public draft -> verify/install -> finalize lifecycle without changing the
   engine-selected support map.
5. After valid exact accounting, each of the 14 cases reaches the same core
   result demonstrated by the internal controls where applicable:
   `VERIFIED`, `decision_support_closure_valid=true`, closure certificate
   present, no false gate caused by the formerly unreachable obligation.

Negative controls:

1. wrong node with correct endpoints -> reject;
2. correct node with extra/missing endpoint -> reject;
3. non-selected endpoint absent from the evaluated snapshot -> reject;
4. stale/non-selected endpoint with no freshly derived required obligation ->
   reject;
5. wrong selected-support map -> reject;
6. wrong retrieval scope or snapshot -> reject;
7. wrong claim set or requirements -> reject;
8. stale decision-context commitment -> reject;
9. source-semantic node presented as generic accounting -> reject;
10. invalid arity/type/blank identifier -> reject;
11. unverified or mismatched external attestation -> reject;
12. accounting that does not bind to the exact fresh universe -> must remain
    non-authorizing.

Historical frozen results must not be rescored. CFC Anchor 0.2.90rc1 remains the
frozen reference; this specification is for a separately versioned CFC-next
candidate only.

## Design conclusion

The evidence supports a two-change repair, not a controller rewrite:

1. **schema alignment** — make generic-accounting node validation match the
   generic node domain the engine already emits;
2. **exact-obligation reachability** — allow selected/excluded accounting only
   when it is an exact, fresh, engine-required obligation.

The existing exact binding and closure checks should remain the security
boundary.

