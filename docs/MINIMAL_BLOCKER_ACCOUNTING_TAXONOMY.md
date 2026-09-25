# Minimal blocker accounting taxonomy

## Goal

Classify all 14 previously isolated minimal stale-relation blockers by the
decision-accounting contract failure mechanism they trigger.

The 14 blockers are:

- origin family: `root_origin_shared`, `origin_shared`,
  `extractor_shared`;
- `common_mode_group_shared`;
- dependency singletons: `data_source`, `sensor_input`, `transform`,
  `model`, `extractor`, `cache`, `upstream_db`, `operator`,
  `preprocessing`, `runtime`.

Each blocker is run in a fresh subprocess with:

- E1 = CURRENT;
- E2 = STALE;
- both evidence records positive and otherwise matching;
- required independent supports = 1;
- exactly one minimal relation factor shared.

For each frozen engine-emitted `decision_level_required` generic obligation,
the review tests:

1. exact registration in the frozen internal generic-accounting registry;
2. exact bind to the frozen decision context;
3. direct frozen-core closure after exact bind, when binding is possible;
4. exact construction through the supported public Controller draft surface.

## Classification

Primary expected mechanisms:

- `ENGINE_EMITTED_ACCOUNTING_SCHEMA_INCOMPATIBILITY`
- `PUBLIC_SELECTED_EXCLUDED_ENDPOINT_REACHABILITY_INCONSISTENCY_CORE_BINDABLE`

Any other mechanism is recorded separately rather than forced into one of these
classes.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

## Result

All 14 previously isolated minimal blockers reproduced the same baseline
authorization signature:

- claim state = `VERIFIED`;
- `control_closure = false`;
- `decision_support_closure_valid = false`;
- the only relevant decision-accounting obstruction is the required generic
  obligation involving selected CURRENT E1 and stale/non-selected E2.

The 14 blockers split cleanly into two mechanisms.

### A. Engine-emitted / accounting-schema incompatibility — 3 blockers

1. `root_origin_shared`
   - engine node:
     `("LINEAGE", "", "general-record:root:shared")`
   - frozen internal registry: **REJECTED**
   - public draft: **REJECTED**
   - error: `ValueError: invalid generic dependency node`

2. `origin_shared`
   - engine node:
     `("LINEAGE", "", "general-record:origin:shared")`
   - frozen internal registry: **REJECTED**
   - public draft: **REJECTED**
   - error: `ValueError: invalid generic dependency node`

3. `common_mode_group_shared`
   - engine node:
     `("COMMON_MODE", "", "group:shared")`
   - frozen internal registry: **REJECTED**
   - public draft: **REJECTED**
   - error: `ValueError: invalid generic dependency node`

These required obligations cannot enter generic accounting even at the frozen
internal registry layer because the engine-emitted node shape contains a blank
middle component.

### B. Public selected/excluded endpoint reachability inconsistency, core-bindable — 11 blockers

The following 11 blockers all produce schema-valid `DEPENDENCY` nodes:

- `extractor_shared` -> `("DEPENDENCY", "extractor", "shared")`
- `dependency:data_source`
- `dependency:sensor_input`
- `dependency:transform`
- `dependency:model`
- `dependency:extractor`
- `dependency:cache`
- `dependency:upstream_db`
- `dependency:operator`
- `dependency:preprocessing`
- `dependency:runtime`

For every one of these 11 cases:

- exact frozen internal registration: **ACCEPTED**;
- exact bind: `BOUND`;
- direct frozen core after exact bind:
  - claim = `VERIFIED`;
  - `control_closure = true`;
  - `decision_support_closure_valid = true`;
  - decision-support closure certificate present;
  - false gates = none;
- exact public draft:
  **REJECTED** with
  `ValueError: generic dependency endpoints must be selected supports`.

This shows that the public selected/excluded endpoint reachability inconsistency
is not limited to `data_source`; it spans every tested dependency category and
the provenance extractor relation after semantic normalization.

## Taxonomy summary

- total minimal blockers: **14**
- engine-emitted/accounting-schema incompatibility: **3**
- schema-valid but public endpoint-unreachable and core-bindable: **11**
- unclassified mechanisms: **0**

The two mechanisms are therefore broad structural classes rather than isolated
special cases.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

