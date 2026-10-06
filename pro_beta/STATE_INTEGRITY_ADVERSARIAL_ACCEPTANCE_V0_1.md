# State Integrity adversarial acceptance v0.1

Date: 2026-10-06

Status: **ACCEPTANCE HARNESS CANDIDATE — READ-ONLY**

## Purpose

This harness closes the remaining State Integrity v0.1 promotion evidence for failure modes that should not be created by corrupting production persistence.

It operates on one authenticated, owner-scoped conversation whose current HAWM snapshot already has a valid server-side identity receipt.

The harness derives the baseline exclusively from persisted server-side state and then creates adversarial copies **in memory only**.

It does not alter the persisted HAWM snapshot, identity receipt, CFC run or audit history.

## Endpoint

`GET /api/conversations/{conversation_id}/state-integrity-acceptance`

The request carries no case ID, arm ID, snapshot ID, lineage ID, predecessor ID or fingerprint.

## Preconditions

The current persisted state must first resolve through the ordinary State Integrity adapter as:

`STATE_VALID / EXACT_STATE_BINDING_ESTABLISHED`

Otherwise the harness returns:

`ACCEPTANCE_UNRESOLVED / BASELINE_STATE_NOT_VALID`

A legacy snapshot without an identity receipt remains:

`ACCEPTANCE_UNRESOLVED / SNAPSHOT_IDENTITY_NOT_REGISTERED`

## In-memory adversarial matrix

The harness tests:

- cross-case substitution → `STATE_INVALID / CASE_ID_MISMATCH`;
- cross-arm substitution → `STATE_INVALID / ARM_ID_MISMATCH`;
- lineage substitution → `STATE_INVALID / LINEAGE_ID_MISMATCH`;
- stale snapshot → `STATE_UNRESOLVED / CURRENT_SNAPSHOT_MISMATCH`;
- same snapshot identity with changed payload → `STATE_INVALID / SNAPSHOT_FINGERPRINT_MISMATCH`;
- predecessor mismatch → `STATE_UNRESOLVED / PREDECESSOR_MISMATCH`.

Every case must preserve:

`authorization_effect = DOES_NOT_AUTHORIZE_CLOSURE`

## Safety boundary

The harness is not an alternate State Integrity decision path.

It is an authenticated production acceptance tool.

It:

- does not persist adversarial variants;
- does not accept client-supplied identity claims;
- does not execute CFC;
- does not create or modify identity receipts;
- does not upgrade any state;
- does not authorize closure.

Boundary:

`SERVER_DERIVED_IN_MEMORY_VARIANTS_ONLY_NO_PERSISTENCE_NO_CFC_EXECUTION`

## Acceptance result

A successful run returns:

`ACCEPTANCE_PASS / ALL_ADVERSARIAL_VARIANTS_FAILED_CLOSED_AS_EXPECTED`

Only when all matrix cases return the exact expected fail-closed state and reason.
