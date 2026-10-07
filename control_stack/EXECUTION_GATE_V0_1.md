# Execution Gate v0.1

Date: 2026-10-07

Status: **IMPLEMENTATION CANDIDATE — NOT PRODUCTION PROMOTED**

## Purpose

Execution Gate v0.1 is Control Stack Layer E.

It enforces an already-established controller/authority result at the exact action boundary.

It does not create authority.

Boundary:

`EXACT_CONTROLLER_STATE_AUTHORITY_IDEMPOTENCY_HUMAN_AND_SINGLE_ATTEMPT_ONLY`

Authority effect:

`DOES_NOT_CREATE_AUTHORITY`

## Core invariant

A technically available action is not executable merely because:

- a model proposed it;
- a previous controller run allowed it;
- the same action was allowed on an earlier state;
- the action was already attempted once;
- the executor can be called.

Execution requires the exact current state and current authority to still match the controller decision context.

## Pre-execution requirements

An execution attempt is allowed only when all are true:

- controller decision is exactly `CONTINUE`;
- controller blocker set is empty;
- CFC authority state is `ESTABLISHED`;
- current authority state is still `ESTABLISHED`;
- controller state ID equals current state ID;
- controller state version equals current state version;
- required human review is explicitly approved;
- a required transactional boundary is explicitly supported;
- idempotency key has not been used before;
- execution receipt ID has not been used before.

Any failed requirement blocks before the executor is called.

## Idempotency

The gate consumes an explicit prior execution-receipt set.

For v0.1:

- a reused receipt ID is blocked;
- the same idempotency key for the same action is treated as replay and blocked;
- the same idempotency key for another action is treated as a key collision and blocked;
- the gate does not silently retry.

A later retry must use a newly governed execution receipt and must not conceal an earlier uncertain outcome.

## Single-attempt rule

`execute_with_gate` calls the executor at most once.

The executor receives an exact immutable call context containing:

- action ID;
- controller run ID;
- state ID;
- state version;
- idempotency key;
- execution receipt ID;
- whether a transaction boundary is required;
- opaque action payload.

The gate performs no hidden retry.

## Execution result semantics

The shared execution envelope distinguishes:

### `NOT_ATTEMPTED`

No executor call occurred because execution has not been requested yet.

- attempted = false
- executed = false

### `BLOCKED`

The gate rejected execution before the executor was called.

- attempted = false
- executed = false

### `ATTEMPTED_NOT_EXECUTED`

The executor was called and explicitly confirmed no external effect.

- attempted = true
- executed = false

### `EXECUTED`

The executor was called and explicitly confirmed an external effect with a non-empty effect handle.

- attempted = true
- executed = true

### `OUTCOME_UNKNOWN`

The executor was called, but the gate cannot safely determine whether the external effect occurred.

- attempted = true
- executed = null

Examples include:

- executor exception after submission may have occurred;
- malformed executor response;
- explicit adapter result `UNKNOWN`;
- an `EXECUTED` claim without a valid effect handle.

The gate must not convert this state into `executed = false`.

### `FAILED`

Reserved for a future adapter contract that can explicitly prove the attempt failed with no effect.

- attempted = true
- executed = false

v0.1 does not infer this state from exceptions.

## Executor contract

The v0.1 executor returns one of:

`{"outcome": "EXECUTED", "effect_handle": "<non-empty>"}`

`{"outcome": "NOT_EXECUTED", "effect_handle": null}`

`{"outcome": "UNKNOWN", "effect_handle": "<string-or-null>"}`

An exception is fail-closed as `OUTCOME_UNKNOWN`.

## Transaction boundary

When `transaction_required = true`, execution is blocked unless the adapter explicitly declares `transaction_supported = true`.

v0.1 does not claim distributed transaction safety.

For adapters that declare transaction support, an `EXECUTED` result means the adapter contract only reports the effect after its supported commit boundary.

## Human review

When `human_review_required = true`, the exact call is blocked unless `human_review_approved = true`.

The gate does not infer approval from identity, role, prior approval or user presence.

## Shared schema change

The shared Control Stack execution object now permits:

`executed = null`

only when:

`execution_status = OUTCOME_UNKNOWN`

This prevents uncertain external outcomes from being laundered into a false no-effect claim.

The schema also binds status/flag coherence:

- `BLOCKED` cannot claim an attempt;
- `EXECUTED` requires attempted=true, executed=true and a non-empty effect handle;
- known-no-effect states require executed=false;
- `OUTCOME_UNKNOWN` requires attempted=true and executed=null.

## Acceptance matrix

The v0.1 tests cover at least:

- exact CONTINUE + exact state/version + authority -> allowed;
- HOLD -> blocked before executor;
- STOP -> blocked before executor;
- controller blocker under a CONTINUE label -> blocked;
- missing CFC authority -> blocked;
- revoked/current authority missing -> blocked;
- stale state ID -> blocked;
- stale state version -> blocked;
- required human approval absent -> blocked;
- required transaction boundary unavailable -> blocked;
- same-action replay -> blocked;
- idempotency key collision across actions -> blocked;
- receipt ID reuse -> blocked;
- malformed prior receipt collection -> blocked;
- successful executor -> called exactly once and EXECUTED;
- explicit no-effect -> ATTEMPTED_NOT_EXECUTED;
- executor exception -> OUTCOME_UNKNOWN;
- explicit unknown -> OUTCOME_UNKNOWN;
- malformed executor result -> OUTCOME_UNKNOWN;
- EXECUTED without effect handle -> OUTCOME_UNKNOWN;
- missing executor -> blocked before attempt;
- schema integration for EXECUTED / BLOCKED / OUTCOME_UNKNOWN.

## Claim ceiling

This candidate establishes deterministic, fail-closed execution-boundary semantics only.

It does not establish:

- production connector safety;
- arbitrary third-party transaction guarantees;
- distributed exactly-once delivery;
- real-world action authority;
- human-review policy correctness;
- side-effect reversibility.

Before production promotion it requires:

1. dedicated CI and shared-schema regression;
2. a persisted execution-receipt registry;
3. server-side ownership and exact-state binding;
4. a real read-only preflight path;
5. controlled synthetic executor acceptance;
6. live fail-closed stale-state and replay controls;
7. no bypass path around the gate;
8. append-only production verification evidence.

Frozen CFC Anchor `0.2.90rc1` remains unchanged.
