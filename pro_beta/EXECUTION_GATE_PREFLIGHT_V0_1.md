# Pro Beta Execution Gate Registry + Read-only Preflight v0.1

Date: 2026-10-07

Status: **INTEGRATION CANDIDATE — NOT PRODUCTION PROMOTED**

## Purpose

This integration provides the host-side persistence and read-only preflight required by Control Stack Execution Gate v0.1.

It does not create execution authority and does not execute external actions.

Execution Gate primitive:

`control_stack/execution_gate.py`

Primitive boundary:

`EXACT_CONTROLLER_STATE_AUTHORITY_IDEMPOTENCY_HUMAN_AND_SINGLE_ATTEMPT_ONLY`

Host preflight boundary:

`PERSISTED_INTENT_STATE_INTEGRITY_EXECUTION_RECEIPTS_AND_EXPLICIT_NO_AUTHORITY_ONLY`

Authority effect:

`DOES_NOT_CREATE_AUTHORITY`

## Existing real-authority constraint

The repository already records:

`F4/F5_NO_GO_REAL_AUTHORITY_UNAVAILABLE`

for the inspected real-authority universe.

Relevant records include:

- `collaboration/cfc-ridi/v0.2/F4_CFC_AUTHORITY_UNIVERSE_CANDIDATE_R1_PUBLICATION.md`;
- `collaboration/cfc-ridi/v0.2/F4_F5_CFC_REAL_AUTHORITY_NO_GO_COUNTERSIGN.md`.

This integration does not weaken or reinterpret that result.

No existing Pro Beta:

- model output;
- CFC demonstrator result;
- source ID;
- review manifest;
- benchmark label;
- HAWM field;
- user presence

is promoted into real execution authority.

## Execution Intent Registration

`ExecutionIntentRegistration` is a non-authorizing record.

It identifies one exact proposed action by:

- `intent_id`;
- conversation;
- `action_id`;
- exact persisted `controller_run_id`;
- exact HAWM `state_id`;
- exact state fingerprint as `state_version`;
- `idempotency_key`;
- exact planned `receipt_id`;
- canonical action-payload fingerprint;
- explicit human-review requirement;
- explicit transaction requirement;
- registry adapter version.

The service derives state/version from persisted server records.

The caller cannot supply an arbitrary state version.

An intent requires:

- an owned CFC run;
- that run to be bound to a HAWM snapshot;
- an existing HAWM identity anchor;
- the intent state to be the same state as the run-bound snapshot;
- the intent state version to equal the registered snapshot fingerprint.

An intent is not permission to act.

## Idempotency and receipt identity

Within one conversation:

- an idempotency key may be registered only once;
- a planned receipt ID may be registered only once.

This is conservative by design.

A retry after an uncertain attempt requires a newly governed intent with a new idempotency identity.

## Execution Receipt Registry

`ExecutionReceiptRecord` is append-only application state for an execution attempt that actually reached an executor.

Preflight-only `BLOCKED` and `NOT_ATTEMPTED` states are not persisted as execution receipts.

A persisted receipt must exactly match its intent on:

- receipt ID;
- action ID;
- controller run ID;
- state ID;
- state version;
- idempotency key.

The database enforces this exact tuple with a composite foreign key.

The registry accepts only attempted outcomes:

- `ATTEMPTED_NOT_EXECUTED`;
- `EXECUTED`;
- `OUTCOME_UNKNOWN`;
- `FAILED` (reserved by the primitive contract).

Coherence rules are enforced in both the service/persistence path and PostgreSQL constraints.

## Database binding

New tables:

- `execution_intents`;
- `execution_receipts`.

Execution intent has exact foreign-key binding to:

- the controller run;
- the run-bound HAWM snapshot;
- the HAWM identity anchor.

The database uses a composite run/state foreign key so a run from snapshot A cannot be paired with state B even inside the same conversation.

The receipt table uses a composite exact-intent foreign key so a receipt cannot reuse an intent ID while changing action/run/state/version/idempotency metadata.

Database bootstrap treats both tables as required once promoted to production.

## Read-only endpoint

Candidate endpoint:

`GET /api/conversations/{conversation_id}/execution-preflight`

It is authenticated and owner-scoped.

There is intentionally no public POST route for:

- execution intent creation;
- execution authority;
- execution receipt creation;
- action execution.

## Preflight evaluation order

The endpoint evaluates:

`current HAWM snapshot -> State Integrity -> latest persisted Execution Intent -> prior Execution Receipts -> Execution Gate`

If there is no current HAWM snapshot:

`PREFLIGHT_UNRESOLVED / NO_HAWM_SNAPSHOTS`

If State Integrity is not valid:

`PREFLIGHT_UNRESOLVED / STATE_INTEGRITY_NOT_VALID`

If no execution intent exists:

`PREFLIGHT_UNRESOLVED / EXECUTION_INTENT_NOT_REGISTERED`

## Explicit real-authority HOLD

v0.1 has no real execution-authority receipt source.

Therefore, even for an exact current intent, the preflight calls the primitive with:

- controller decision: `NOT_RUN`;
- controller blocker: `HOLD_REAL_EXECUTION_AUTHORITY_UNAVAILABLE`;
- CFC authority: `NOT_ESTABLISHED`;
- current authority: `NOT_ESTABLISHED`.

The result must remain:

`EXECUTION_BLOCKED`

with:

- attempted = false;
- executed = false;
- no executor call;
- no persistence action.

The host must not map the existing Pro Beta `ALLOW` presentation into Control Stack `CONTINUE`.

## Stale-state behavior

If a newer HAWM snapshot exists after the intent was registered, preflight preserves:

- `PRE_EXECUTION_STATE_ID_MISMATCH`;
- `PRE_EXECUTION_STATE_VERSION_MISMATCH`.

A prior controller/action state cannot be carried forward to a new state.

## Replay behavior

Persisted execution receipts are supplied to the primitive as prior receipt state.

The primitive can therefore preserve:

- `IDEMPOTENCY_REPLAY_BLOCKED`;
- `IDEMPOTENCY_KEY_REUSED_FOR_DIFFERENT_ACTION`;
- `EXECUTION_RECEIPT_ID_REUSED`.

Replay protection no longer depends on caller-supplied history.

## Read-only guarantee

The preflight endpoint:

- creates no HAWM snapshot;
- creates no identity record;
- creates no execution intent;
- creates no execution receipt;
- executes no CFC run;
- calls no executor;
- creates no external effect.

The response exposes:

- `read_only = true`;
- `persistence_actions = []`;
- `cfc_executed = false`;
- `authority_effect = DOES_NOT_CREATE_AUTHORITY`.

## Promotion ceiling

This candidate establishes:

- persisted exact action/state intent binding;
- persisted replay/receipt history;
- database-level exact tuple constraints;
- authenticated read-only negative-authority preflight;
- stale-state and replay propagation into Execution Gate.

It does not establish:

- real-world execution authority;
- positive `CONTINUE` production execution;
- a production executor adapter;
- transaction safety;
- human approval policy correctness;
- exactly-once third-party effects.

Before production promotion of the negative/preflight path:

1. full Pro Beta/PostgreSQL CI must pass;
2. no public write/execute route may exist;
3. narrow production port must preserve all existing production gates;
4. database bootstrap must show both execution tables;
5. authenticated live no-intent negative control must be observed;
6. telemetry must show GET-only preflight and zero execution mutation paths;
7. append-only production acceptance evidence must be recorded.

Positive execution remains separately blocked until a governed real-authority source and verifier contract exist.

Frozen CFC Anchor `0.2.90rc1` remains unchanged.
