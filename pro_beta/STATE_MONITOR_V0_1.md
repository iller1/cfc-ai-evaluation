# State Monitor v0.1 — bounded HAWM transition contract

## Status

**IMPLEMENTATION CANDIDATE — NOT YET PRODUCTION PROMOTED**

State Monitor is a host/application-layer control over persisted HAWM snapshots.

It does **not** modify or reinterpret:

- frozen CFC Anchor `0.2.90rc1`;
- Operator Wrapper v1.23;
- Evidence Drift semantics;
- ordinary model replies;
- free-text HAWM text as verified evidence.

## Purpose

State Monitor v0.1 answers one narrow workflow question:

> Did an explicit HAWM unresolved condition disappear before the current snapshot itself received a persisted CFC evaluation?

The monitored transition is:

`previous HAWM snapshot -> current HAWM snapshot`

with one additional orchestration fact:

`current_snapshot_evaluated`

Production integration must derive that fact only from exact persisted snapshot-to-run binding.

## Why this exists

Evidence Drift detects whether CFC-relevant structured state changed relative to a run-bound baseline.

State Monitor watches a different failure mode: a working-state marker can disappear between snapshots even when no new evaluation has established the current snapshot as the evaluated state.

The first invariant is deliberately narrow:

`unresolved present -> unresolved absent`

must not silently inherit prior authority unless the current snapshot has itself been evaluated through the exact durable CFC binding path.

## Input boundary

v0.1 reads only explicit persisted HAWM fields and snapshot identity.

The `unresolved` field is treated only as an operator-managed workflow marker:

- non-empty string = unresolved marker present;
- empty or missing string = unresolved marker absent.

The module does **not** infer what the text means.

Boundary label:

`EXPLICIT_HAWM_WORKING_STATE_TRANSITIONS_ONLY_NO_FREE_TEXT_SEMANTIC_INFERENCE`

## Output states

### `NO_MONITOR_ALERT`

No monitored violation was found.

Possible reasons include:

- `UNRESOLVED_STILL_PRESENT`;
- `UNRESOLVED_ADDED`;
- `NO_UNRESOLVED_CLEARANCE`;
- `UNRESOLVED_CLEARED_AFTER_CURRENT_SNAPSHOT_EVALUATION`.

Effect:

`NO_ADDITIONAL_BLOCK_FROM_STATE_MONITOR_ONLY`

This is not closure or action authorization.

### `STATE_TRANSITION_ALERT`

The monitored transition occurred without the required evaluation condition.

Current v0.1 alert:

`UNRESOLVED_CLEARED_WITHOUT_CURRENT_SNAPSHOT_EVALUATION`

Effect:

`BLOCK_STATE_CARRY_FORWARD_REVIEW_REQUIRED`

### `UNRESOLVED`

The monitor cannot trust the comparison.

Examples:

- cross-conversation transition;
- malformed HAWM state;
- non-string `unresolved` field;
- invalid evaluation flag;
- same immutable snapshot ID with different canonical state.

Effect:

`BLOCK_STATE_CARRY_FORWARD_REVIEW_REQUIRED`

## Evaluation provenance requirement

The primitive accepts a boolean:

`current_snapshot_evaluated`

That value is **not** trusted as user input in the intended production design.

The API/service integration must derive it as:

`latest relevant persisted CFC run.hawm_snapshot_id == current snapshot.snapshot_id`

A merely existing CFC run is not enough.

An older bound run is not enough.

A run bound to another snapshot is not enough.

## Snapshot identity

Snapshots are treated as immutable.

If the same `snapshot_id` is supplied with a different canonical HAWM state, the result is:

`UNRESOLVED / SNAPSHOT_ID_CONTENT_MISMATCH`

The explicit structured evidence collection is order-normalized so equivalent evidence reordering alone does not create a false identity mismatch.

## Acceptance matrix

| Case | Expected |
| --- | --- |
| unresolved remains present | `NO_MONITOR_ALERT` |
| unresolved is added | `NO_MONITOR_ALERT` |
| unresolved clears, current snapshot not evaluated | `STATE_TRANSITION_ALERT` |
| unresolved clears, current snapshot exactly evaluated | `NO_MONITOR_ALERT` |
| same snapshot ID, changed state | `UNRESOLVED` |
| evidence reorder only under same semantic state | no identity mismatch |
| cross-conversation transition | `UNRESOLVED` |
| non-string unresolved field | `UNRESOLVED` |
| invalid evaluation flag | `UNRESOLVED` |
| no unresolved clearance | `NO_MONITOR_ALERT` |

## Relationship to Evidence Drift

Evidence Drift asks:

> Did the explicit CFC-relevant structured state change relative to the run-bound baseline?

State Monitor asks:

> Did the HAWM workflow state transition in a way that would silently remove an explicit unresolved marker without evaluating the current snapshot?

They are complementary.

Neither module returns `ALLOW`.

Both preserve:

`authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`

## API integration candidate

The integration candidate adds the authenticated read-only endpoint:

`GET /api/conversations/{conversation_id}/state-monitor`

The API derives its inputs from persisted history only:

1. load the owned HAWM snapshot history;
2. require at least two snapshots;
3. define `previous` as the immediately preceding persisted snapshot;
4. define `current` as the latest persisted snapshot;
5. inspect persisted CFC runs for an exact binding to `current.snapshot_id`;
6. set `current_snapshot_evaluated = true` only when such an exact binding exists.

The response adds:

- `evaluation_source`;
- `evaluation_cfc_run_id`.

A verified current-snapshot evaluation reports:

`evaluation_source = PERSISTED_CFC_RUN_BINDING`

An older run bound to the previous snapshot does not satisfy the current-snapshot requirement.

A later unrelated unbound prepared run does not erase historical proof that the exact current snapshot was evaluated; State Monitor is checking the transition-evaluation fact, not selecting the latest closure authority.

If fewer than two HAWM snapshots exist, the API returns:

`UNRESOLVED / INSUFFICIENT_HAWM_HISTORY`

The endpoint is read-only and never executes CFC, rewrites HAWM, or authorizes closure.

## Promotion gate

Before production promotion:

1. the primitive acceptance matrix must pass;
2. the existing Pro Beta regression must remain green;
3. API integration must derive current-snapshot evaluation from exact persisted CFC binding;
4. no user-provided boolean may decide evaluation status;
5. an older or unrelated CFC run must not satisfy the current-snapshot evaluation requirement;
6. authenticated production testing must demonstrate:
   - unresolved present;
   - unresolved removed with HAWM-only save;
   - State Monitor alert;
   - exact current snapshot CFC evaluation;
   - alert clears to `NO_MONITOR_ALERT`;
7. no frozen CFC artifact may change.
