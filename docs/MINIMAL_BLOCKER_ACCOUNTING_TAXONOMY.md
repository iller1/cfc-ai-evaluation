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
