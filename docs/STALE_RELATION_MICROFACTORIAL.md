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

Four binary factors:

1. root origin ID shared;
2. origin ID shared;
3. extractor ID shared;
4. lineage chain shared.

Total: **16 states**.

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

The all-shared origin state must reproduce the prior grouped `0100` result.

The all-shared dependency state must reproduce the prior grouped `0001` result.

No semantic conclusion is accepted if those controls fail.

Frozen CFC remains unchanged.
