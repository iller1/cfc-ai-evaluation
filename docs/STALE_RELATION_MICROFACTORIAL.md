# Stale relation microfactorial

## Goal

Refine the 16-state stale dependency factorial after three independent minimal
blocking relation families were found:

- origin/lineage;
- common-mode group;
- generic dependencies.

The common-mode-group field is already atomic at this abstraction level.

This experiment decomposes the other two families.

## Origin/lineage factorial

Initial design proposed four binary factors, but the frozen API exposed a structural dependency: the provenance lineage must run uniquely from `root_origin_id` to `origin_id`. Therefore lineage-chain endpoint identity is not an independent bit.

The valid origin microfactorial uses three independent binary factors:

1. root origin ID shared;
2. origin ID shared;
3. extractor ID shared.

The lineage path is derived from root origin -> origin in every state.

Total: **8 admissible states**.

This reduction is itself a combinatorial finding: a syntactically imaginable state dimension was not structurally independent.

Source semantics, common-mode group and generic dependencies remain distinct.

## Dependency singleton sweep

Ten generic dependency dimensions are tested one at a time:

- data_source
- sensor_input
- transform
- model
- extractor
- cache
- upstream_db
- operator
- preprocessing
- runtime

Controls:

- NONE shared;
- ALL shared.

Total: **12 states**.

## Equivalence controls

The all-shared three-factor origin state must reproduce the prior grouped `0100` result.

The all-shared dependency state must reproduce the prior grouped `0001` result.

No semantic conclusion is accepted if those controls fail.

Frozen CFC remains unchanged.
