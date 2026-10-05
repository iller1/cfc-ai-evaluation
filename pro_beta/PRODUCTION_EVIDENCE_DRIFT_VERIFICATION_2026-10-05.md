# Production verification — Evidence Drift v0.1

Date: 2026-10-05

## Closure label

**EVIDENCE DRIFT v0.1: PRODUCTION VERIFIED**

This checkpoint records an authenticated production verification of the bounded host/application-layer Evidence Drift path.

It does **not** change or extend the semantics of frozen CFC Anchor `0.2.90rc1`.

## Production artifacts

API production branch:

`pro-beta-v0.1`

Evidence Drift production API merge commit:

`1381184b41a536fa1431e0082b6e3fe749ec9a9b`

Railway API deployment:

`6854a7f2-5c84-457e-92c1-6fe08607cbcc`

Deployment status:

`SUCCESS`

Frontend main merge commit:

`27f084ac7d9b3a3018ac2c1012ddad0df08b2f73`

Railway frontend deployment:

`da603d5e-69af-4152-a19a-2d6bfb37acad`

Frontend deployment status:

`SUCCESS`

## Verified production invariant

Evidence Drift resolves its comparison baseline only through:

`latest persisted CFC run -> persisted hawm_snapshot_id -> exact historical HAWM snapshot`

It then compares that exact baseline with the latest persisted HAWM snapshot.

It does not use the latest HAWM snapshot as the historical baseline, and it does not silently carry forward an older closure when the latest CFC run is unbound.

## Authenticated production sequence

Conversation:

`conv_66ae46586a034df7b5b5f2366ff37661`

### 1. Legacy/unbound guard

Initial production check returned:

- status: `UNRESOLVED`
- reason: `LATEST_CFC_RUN_UNBOUND`
- baseline source: `NONE`
- CFC run: `cfc_41a482d6f5454675bfe330361530f874`
- baseline snapshot: `NONE`
- current snapshot: `hawm_4f454e0994e445f18717adc9bf45e278`
- requires re-evaluation: `true`
- propagation effect: `BLOCK_CARRY_FORWARD_REEVALUATION_REQUIRED`
- authorization effect: `DOES_NOT_AUTHORIZE_CLOSURE`

This verifies fail-closed behavior for a legacy/latest run without a durable HAWM binding.

The drift request itself was read-only.

### 2. Fresh run-bound baseline

A new structured HAWM snapshot was saved and executed through the frozen CFC path.

Production HTTP sequence:

- `POST /hawm -> 200`
- `POST /cfc-from-hawm -> 200`
- `GET /hawm -> 200`

Resulting run-bound state:

- CFC run: `cfc_2576c0a96c4c49069dd021b4f9f27d8c`
- baseline snapshot: `hawm_a38601eb51eb4bcf9a1b958686b467fa`

### 3. Negative control — no drift

Without changing the structured state, Evidence Drift returned:

- status: `NO_DRIFT`
- reason: `SAME_SNAPSHOT`
- baseline source: `PERSISTED_CFC_RUN_BINDING`
- CFC run: `cfc_2576c0a96c4c49069dd021b4f9f27d8c`
- baseline snapshot: `hawm_a38601eb51eb4bcf9a1b958686b467fa`
- current snapshot: `hawm_a38601eb51eb4bcf9a1b958686b467fa`
- changed paths: none
- requires re-evaluation: `false`
- propagation effect: `NO_ADDITIONAL_BLOCK_FROM_DRIFT_ONLY`
- authorization effect: `DOES_NOT_AUTHORIZE_CLOSURE`

This verifies that `NO_DRIFT` does not itself authorize closure.

### 4. Material evidence drift

Only the explicit structured evidence validity was changed:

`Evidence 1 validity: CURRENT -> STALE`

The operator then used the HAWM-only save path.

Production HTTP sequence:

- `POST /hawm -> 200`
- `GET /hawm -> 200`

No `POST /cfc-from-hawm` occurred before the drift assessment.

The new working snapshot was:

`hawm_74b09b3cf14745bda9642a04b85c7180`

Evidence Drift then returned:

- status: `MATERIAL_DRIFT`
- reason: `STRUCTURED_EVIDENCE_STATE_CHANGED`
- baseline source: `PERSISTED_CFC_RUN_BINDING`
- baseline snapshot: `hawm_a38601eb51eb4bcf9a1b958686b467fa`
- current snapshot: `hawm_74b09b3cf14745bda9642a04b85c7180`
- changed paths: `cfc_structured.evidence`
- requires re-evaluation: `true`
- propagation effect: `BLOCK_CARRY_FORWARD_REEVALUATION_REQUIRED`
- authorization effect: `DOES_NOT_AUTHORIZE_CLOSURE`

This verifies the intended carry-forward block after a material structured evidence change.

### 5. Re-evaluation creates a new baseline

With the changed `STALE` evidence still present, the operator ran the structured HAWM -> CFC path again.

Production HTTP sequence:

- `POST /hawm -> 200`
- `POST /cfc-from-hawm -> 200`
- `GET /hawm -> 200`

New run-bound state:

- CFC run: `cfc_5a569f0359e244bf94e16d63b375d697`
- baseline snapshot: `hawm_32e441c930634a5285e96fe094dd577a`

### 6. Post-re-evaluation negative control

Evidence Drift then returned:

- status: `NO_DRIFT`
- reason: `SAME_SNAPSHOT`
- baseline source: `PERSISTED_CFC_RUN_BINDING`
- CFC run: `cfc_5a569f0359e244bf94e16d63b375d697`
- baseline snapshot: `hawm_32e441c930634a5285e96fe094dd577a`
- current snapshot: `hawm_32e441c930634a5285e96fe094dd577a`
- changed paths: none
- requires re-evaluation: `false`
- propagation effect: `NO_ADDITIONAL_BLOCK_FROM_DRIFT_ONLY`
- authorization effect: `DOES_NOT_AUTHORIZE_CLOSURE`

The final drift request was read-only:

- `GET /evidence-drift -> 200`

No new HAWM write or CFC execution was performed by the drift check.

## Verified cycle

The authenticated production sequence therefore demonstrated:

`CURRENT baseline`
→ `NO_DRIFT`
→ `CURRENT -> STALE HAWM-only change`
→ `MATERIAL_DRIFT`
→ `BLOCK_CARRY_FORWARD_REEVALUATION_REQUIRED`
→ `CFC re-evaluation`
→ `new persisted run-bound baseline`
→ `NO_DRIFT`

## What this proves

This checkpoint supports the bounded claim that the deployed host/application layer can:

1. bind a CFC run to an exact persisted HAWM snapshot;
2. compare that exact historical structured state with the latest HAWM state;
3. detect a material explicit structured evidence change;
4. block silent carry-forward of an earlier closure state until re-evaluation;
5. establish a new comparison baseline after re-evaluation;
6. fail closed when the latest CFC run has no durable HAWM binding.

## What this does not prove

This checkpoint does **not** establish that:

- free-text HAWM content is verified evidence;
- ordinary model replies are CFC-verified;
- Evidence Drift determines real-world truth;
- evidence semantics are discovered automatically from natural language;
- a `NO_DRIFT` result authorizes closure or action;
- the system provides a complete external provenance receipt;
- the system is universally production-ready;
- the system is a general AI safety solution.

The comparison boundary remains:

`STRUCTURED_HAWM_CFC_STATE_ONLY_NO_FREE_TEXT_EVIDENCE_INFERENCE`

and the authorization boundary remains:

`DOES_NOT_AUTHORIZE_CLOSURE`
