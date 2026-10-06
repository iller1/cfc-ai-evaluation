# Production verification — State Integrity v0.1

Date: 2026-10-06

## Closure label

**STATE INTEGRITY v0.1: PRODUCTION VERIFIED**

This checkpoint records authenticated production verification of the bounded host/application-layer State Integrity path.

It does **not** modify or extend the semantics of frozen CFC Anchor `0.2.90rc1`.

## Positive control — exact current registered state

Conversation: `conv_66ae46586a034df7b5b5f2366ff37661`

Snapshot: `hawm_cc26c6d45ca747b987faff88e48263fc`

Previous state: `hawm_2f1c3e1d46c74b45aaa96f7b811554d6`

Observed result:

- status: `STATE_VALID`
- reason: `EXACT_STATE_BINDING_ESTABLISHED`
- expectation source: `PERSISTED_HAWM_SNAPSHOT_IDENTITY`
- case: `HAWM_PRO_BETA_STATE`
- arm: `HAWM_WORKING_STATE`
- binding status: `BOUND`
- lineage status: `ESTABLISHED`
- identity adapter: `HAWM_STATE_IDENTITY_ADAPTER_V0_1`
- state fingerprint: `fc5e9cdd8ffc88e17685f1e1c719322cc1e35ad60d9ad23f22ae100c35ea982b`
- requires review: `false`
- read only: `true`
- propagation effect: `NO_ADDITIONAL_BLOCK_FROM_STATE_INTEGRITY_ONLY`
- authorization effect: `DOES_NOT_AUTHORIZE_CLOSURE`
- boundary: `EXPLICIT_IDENTITY_LINEAGE_AND_SNAPSHOT_BINDING_ONLY`
- adapter boundary: `PERSISTED_HAWM_SNAPSHOT_AND_SERVER_IDENTITY_RECEIPT_ONLY`

Railway production telemetry confirmed one successful HAWM save and one successful State Integrity request for this conversation in the acceptance window.

## Negative control — legacy state without identity receipt

Conversation: `conv_5373e1033804407caa05af55371f0394`

Conversation label: `HAWM binding production test`

Legacy snapshot: `hawm_4b1078d76a2b494b99568abf02dde516`

Observed result:

- status: `STATE_UNRESOLVED`
- reason: `SNAPSHOT_IDENTITY_NOT_REGISTERED`
- expectation source: `NONE`
- case: `HAWM_PRO_BETA_STATE`
- arm: `HAWM_WORKING_STATE`
- state ID: `hawm_4b1078d76a2b494b99568abf02dde516`
- snapshot ID: `hawm_4b1078d76a2b494b99568abf02dde516`
- lineage: `NONE`
- previous state: `NONE`
- binding status: `UNKNOWN`
- lineage status: `UNKNOWN`
- identity adapter: `NONE`
- state fingerprint: `NONE`
- requires review: `true`
- read only: `true`
- propagation effect: `BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED`
- authorization effect: `DOES_NOT_AUTHORIZE_CLOSURE`
- boundary: `EXPLICIT_IDENTITY_LINEAGE_AND_SNAPSHOT_BINDING_ONLY`
- adapter boundary: `PERSISTED_HAWM_SNAPSHOT_AND_SERVER_IDENTITY_RECEIPT_ONLY`

Railway production telemetry independently confirmed for this legacy conversation in the same acceptance window:

- `GET /state-integrity -> 2xx` observed;
- `POST /hawm -> 0`;
- `POST /cfc-from-hawm -> 0`.

Therefore the negative control was read-only and did not create a replacement snapshot, backfill identity, or execute CFC.

## Verified production cycle

`legacy persisted snapshot without receipt`
→ `STATE_UNRESOLVED`
→ `SNAPSHOT_IDENTITY_NOT_REGISTERED`
→ `BLOCK_STATE_CARRY_FORWARD_STATE_INTEGRITY_REQUIRED`

and independently:

`new persisted HAWM snapshot`
→ `server-side identity receipt`
→ `exact current-state comparison`
→ `STATE_VALID`
→ `EXACT_STATE_BINDING_ESTABLISHED`
→ `BOUND / ESTABLISHED`

In both paths:

`DOES_NOT_AUTHORIZE_CLOSURE`

## Acceptance result

**PASS**

Final status:

`STATE_INTEGRITY_V0_1_PRODUCTION_VERIFIED`

## Claim boundary

This verification proves only the bounded State Integrity v0.1 host/application-layer identity and lineage behavior described above.

It does not establish factual truth of HAWM free text, evidence validity or applicability, source independence, automatic provenance discovery, closure authorization, universal production readiness, or general AI-safety correctness.

Frozen CFC Anchor `0.2.90rc1` remains untouched.
