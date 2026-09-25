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


## Result

The corrected microfactorial completed successfully and both equivalence controls
matched the prior grouped factorial.

### Structural state-space correction

The original four-bit origin design was invalid because lineage endpoint identity
is structurally dependent on `root_origin_id` and `origin_id`.

The admissible independent origin dimensions are therefore:

- root origin ID;
- origin ID;
- extractor ID.

The lineage path is derived from the endpoints.

### Origin result

- admissible states: **8**
- ALLOW: **1**
- STOP: **7**

Only `000` — no shared origin factor — closes.

Each individual origin factor is independently sufficient to produce:

- claim state = VERIFIED
- control closure = false
- only false gate = `decision_support_closure_valid`

Minimal one-factor blockers:

- root origin shared only;
- origin shared only;
- extractor shared only.

### Generic dependency result

Twelve dependency states were checked:

- NONE shared;
- each of the 10 dependency dimensions shared individually;
- ALL shared.

Every one of the **10/10 singleton dependency dimensions** independently blocks
closure while leaving the claim VERIFIED:

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

There were no singleton dependency dimensions that allowed closure.

### Equivalence controls

Both passed:

- all three origin factors shared == prior grouped origin/lineage mask `0100`;
- all ten dependencies shared == prior grouped dependency mask `0001`.

Both reproduce:

- claim state = VERIFIED
- control closure = false
- false gates = [`decision_support_closure_valid`]

## Refined rule observed in the frozen controller

For this controlled stale-E2 configuration:

> Any single shared provenance/dependency identity between current E1 and stale
> E2 is sufficient to preserve a downstream authorization block, even though
> stale E2 is no longer needed for claim qualification.

At the tested abstraction level, this applies to:

- root origin;
- origin;
- extractor;
- common-mode group;
- every generic dependency identity tested.

Shared source-semantics metadata alone remains the exception observed so far:
it does not block closure when all provenance/dependency identities are distinct.

## Classification

**BOUNDARY FINDING — RELATION-LEVEL STALE AUTHORIZATION PERSISTENCE**

This remains intentionally unclassified as a false block. The experiment
establishes the mechanism much more narrowly, but the normative question remains:

> Once an evidence record becomes stale for claim qualification, should a shared
> provenance/dependency relation to that stale record continue to withhold
> downstream closure authorization?

That policy question belongs to CFC-next / contract review, not a modification of
the frozen controller.
