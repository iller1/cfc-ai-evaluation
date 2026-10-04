# Production snapshot → CFC run binding verification — 2026-10-04

## Status

**DURABLE SNAPSHOT→RUN BINDING: PRODUCTION VERIFIED**

This checkpoint records one authenticated end-to-end production acceptance run for the Pro Beta HAWM → CFC persistence boundary.

It is evidence for the host/application binding only. It does **not** modify or extend the semantics of the frozen CFC controller and it is **not** a full real-world provenance receipt.

## Production identity

Production API source:

- branch: `pro-beta-v0.1`
- merge commit: `ac18a46e22a5598cff8362cbb799f27764e0ace9`
- Railway deployment: `e8f18758-ed0a-4c47-aad8-84a0437482f8`
- deployment status: `SUCCESS`

Observed production startup/release gates before the authenticated test:

- merge completed;
- CI completed successfully;
- production image deployed from the merge commit above;
- startup schema bootstrap completed and emitted `PRO_BETA_DATABASE_READY`;
- Railway `/healthz` check succeeded;
- retention worker started;
- all five Railway services were online with no fresh failed deployment, warning, or critical state.

## Invariant under test

The acceptance condition was:

> A CFC run must remain durably bound to the exact HAWM snapshot used for that execution, even after a newer HAWM working-state snapshot is persisted.

The audit layer must not silently substitute the newest HAWM state for the historical execution input.

Required Audit V2 outcome after:

`snapshot C → CFC run → snapshot D → Audit V2`

was:

- `binding.status = BOUND_TO_PERSISTED_SNAPSHOT`
- persisted execution snapshot ID = snapshot C
- latest HAWM snapshot ID = snapshot D
- the two IDs are different
- `latest_snapshot_is_run_input = false`
- the exported run-bound HAWM body is C, not D.

## Authenticated production sequence

Conversation:

- name: `HAWM binding production test`
- conversation ID: `conv_5373e1033804407caa05af55371f0394`

### 1. Snapshot C used for execution

Persisted execution snapshot:

- snapshot ID: `hawm_3eac92fff0964419854da4816dbfdb42`
- created: `2026-10-04 13:54:05.770333+00`
- goal: `BINDING TEST C`
- task: `Snapshot C`
- claim: `Claim C`
- evidence: `Evidence C`

Structured CFC state:

- conclusion: `POSITIVE`
- required supports: `1`
- scope: `EXPECTED`
- provenance: `DISTINCT`
- independence authority: `NONE`
- Evidence 1 polarity: `POSITIVE`
- Evidence 1 validity: `CURRENT`

### 2. CFC execution

Persisted CFC run:

- run ID: `cfc_b53e43dd89184d1a9b07af3046202bc0`
- case: `HAWM_STRUCTURED_CUSTOM`
- controller anchor: `0.2.90rc1`
- created: `2026-10-04 13:54:07.756403+00`
- claim state: `VERIFIED`
- decision: `ALLOW`
- reason: `policy-satisfied support set (1)`

The run persisted the HAWM snapshot ID:

`hawm_3eac92fff0964419854da4816dbfdb42`

### 3. Newer HAWM working state persisted without re-running CFC

A later HAWM snapshot was saved:

- snapshot ID: `hawm_4b1078d76a2b494b99568abf02dde516`
- created: `2026-10-04 13:57:28.05752+00`
- goal: `BINDING TEST D`

Production HTTP logs for this step showed a HAWM write/read only and no new `POST /cfc-from-hawm` before the final audit export.

## Audit V2 observed result

The final authenticated Audit V2 reported:

```text
Link status: BOUND_TO_PERSISTED_SNAPSHOT
CFC run ID: cfc_b53e43dd89184d1a9b07af3046202bc0
Persisted execution snapshot ID: hawm_3eac92fff0964419854da4816dbfdb42
Latest HAWM snapshot ID (separate state): hawm_4b1078d76a2b494b99568abf02dde516
Latest snapshot is the run input: False
```

The report exported the run-bound HAWM snapshot as snapshot C while separately exporting snapshot D as the latest working state.

Therefore the system did not relabel the historical CFC run with the newer HAWM state.

## Acceptance result

**PASS**

Observed chain:

`snapshot C → persisted CFC run bound to C → newer snapshot D → Audit V2 still resolves C as the execution input`

This satisfies the production acceptance criterion for durable HAWM snapshot → CFC run binding.

## Non-accepted earlier attempts

Earlier interactive attempts in the same conversation are not counted as acceptance evidence because an additional `POST /cfc-from-hawm` occurred after the newer HAWM snapshot was saved. In those attempts, Audit V2 correctly showed the newest snapshot as the run input.

The final accepted sequence was performed only after server logs confirmed that the newer snapshot write was not followed by another CFC execution.

## Claim boundary

This checkpoint supports the bounded claim:

> The deployed Pro Beta host/application layer durably persisted the exact HAWM snapshot identity used by a CFC run and Audit V2 later reconstructed that historical execution input correctly after the HAWM working state changed.

It does **not** establish:

- that free-text HAWM content is CFC-verified evidence;
- that ordinary model replies are CFC-verified;
- a complete provenance receipt for external or real-world source data;
- universal production readiness;
- general AI-safety correctness;
- any change to frozen CFC Anchor `0.2.90rc1` semantics.
