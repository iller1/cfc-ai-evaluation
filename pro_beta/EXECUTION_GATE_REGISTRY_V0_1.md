# Pro Beta Execution Gate registry and preflight v0.1

Date: 2026-10-07

Status: **INTEGRATION CANDIDATE — NOT PRODUCTION PROMOTED**

## Purpose

This integration binds Control Stack Execution Gate v0.1 to persisted Pro Beta state without introducing a real action-execution path.

It adds:

- an append-only Execution Receipt registry;
- exact CFC-run/state/fingerprint binding;
- read-only server-derived execution preflight;
- no public execution endpoint;
- no executor;
- no synthetic-to-real authority upgrade.

## Critical Pro Beta boundary

Current Pro Beta CFC execution is a demonstrator / synthetic analogy.

The frozen controller may return:

`control_closure = true`

and the presentation may render:

`decision = ALLOW`

for a synthetic DemoSubject.

That result is **not** real-action authority.

Therefore this adapter applies the non-negotiable mapping:

`synthetic control_closure=true / ALLOW -> HOLD`

with blocker:

`SYNTHETIC_CFC_CLOSURE_NOT_REAL_ACTION_AUTHORITY`

and:

`cfc_authority_state = NOT_ESTABLISHED`

`current_authority_state = NOT_ESTABLISHED`

A synthetic STOP remains STOP.

No current Pro Beta path maps a synthetic result to Execution Gate `CONTINUE`.

## Read-only preflight

The adapter accepts only persisted server-side inputs:

- current HAWM snapshot;
- current HAWM identity anchor;
- ordinary State Integrity result for that exact current snapshot;
- latest selected CFC run;
- identity anchor for the exact snapshot evaluated by that CFC run;
- prior persisted Execution Receipt records.

The adapter accepts no client-supplied:

- controller decision;
- authority state;
- state fingerprint;
- CFC run binding;
- idempotency history;
- execution result.

It invokes:

`assess_execution_gate`

only.

It never invokes:

`execute_with_gate`

and exposes:

- `read_only = true`;
- `executor_called = false`;
- `persistence_actions = []`.

Adapter boundary:

`PERSISTED_CURRENT_STATE_AND_BOUND_SYNTHETIC_CFC_RUN_PREFLIGHT_ONLY_NO_REAL_ACTION_EXECUTION`

## State Integrity prerequisite

The current state must first have:

`STATE_VALID`

for the exact current snapshot and preserve:

`DOES_NOT_AUTHORIZE_CLOSURE`

A mismatched or invalid State Integrity result blocks preflight before CFC interpretation.

## Supported CFC run

v0.1 accepts only the state-bound:

`HAWM_STRUCTURED_CUSTOM`

Pro Beta run.

Prepared fixture cases are not eligible for execution preflight.

The controller anchor must remain:

`0.2.90rc1`

The raw `control_closure` boolean and presentation decision must agree exactly:

- true ↔ ALLOW;
- false ↔ STOP.

Any mismatch fails closed.

## Exact-state binding

Every persisted Execution Receipt binds:

- conversation;
- exact CFC run;
- exact controller-evaluated state;
- controller-state fingerprint;
- exact pre-execution state;
- pre-execution fingerprint;
- action ID;
- idempotency key;
- receipt ID.

The database enforces that:

- the CFC run and controller-state snapshot belong to the same conversation;
- the CFC run was actually bound to that exact controller state;
- controller-state version matches the persisted State Integrity fingerprint;
- pre-execution-state version matches its persisted fingerprint;
- receipt ID is unique;
- idempotency key is unique within the conversation.

## Receipt semantics

The registry persists the exact Execution Gate distinction between:

- NOT_ATTEMPTED;
- BLOCKED;
- ATTEMPTED_NOT_EXECUTED;
- EXECUTED;
- FAILED;
- OUTCOME_UNKNOWN.

For `OUTCOME_UNKNOWN`:

`executed = null`

The registry must never convert an uncertain external effect into `executed=false`.

SQL CHECK constraints duplicate the shared execution-record invariants so direct database writes cannot silently change status/flag semantics.

## No public write or execution path

This candidate adds no public API/HTTP endpoint for:

- creating an execution receipt;
- submitting an action;
- declaring action authority;
- invoking an executor;
- retrying an effect.

The receipt service is an internal authenticated server boundary for future governed integration.

## Acceptance matrix

The integration tests cover:

- exact blocked receipt round-trip;
- unbound CFC run rejected;
- run bound to a different state rejected;
- wrong controller-state fingerprint rejected;
- wrong pre-execution fingerprint rejected;
- duplicate receipt ID rejected;
- duplicate idempotency key rejected;
- malformed execution object rejected before persistence;
- cross-owner read rejected;
- PostgreSQL round-trip;
- direct SQL wrong fingerprint rejected by FK;
- direct SQL execution-flag laundering rejected by CHECK;
- synthetic STOP remains blocked;
- synthetic ALLOW becomes HOLD, never CONTINUE;
- invalid State Integrity blocks before CFC interpretation;
- prepared fixture is not supported;
- stale controller state is explicitly blocked;
- raw/presentation mismatch fails closed;
- frozen-anchor mismatch fails closed;
- prior idempotency replay is visible to the gate.

## Promotion ceiling

This candidate does not establish a real-action execution path.

Before any production execution can exist, separate work must establish:

1. a real action proposal identity/registry;
2. a real scope-bound action authority contract;
3. an authority issuer/verifier boundary;
4. a governed executor adapter;
5. transactional semantics for the target system where required;
6. durable idempotency and effect reconciliation;
7. live stale-state/replay/unknown-outcome controls;
8. evidence that no alternate action path bypasses Execution Gate.

Until then:

`PRO_BETA_REAL_ACTION_EXECUTION = HOLD`

and:

`SYNTHETIC_CFC_ALLOW != REAL_ACTION_CONTINUE`

Frozen CFC Anchor `0.2.90rc1` remains unchanged.
