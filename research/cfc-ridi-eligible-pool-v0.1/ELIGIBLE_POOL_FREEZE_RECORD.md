# CFC ↔ RIDI Eligible Pool v0.1 — RIDI-side freeze record

**Record date:** 2026-09-29  
**RIDI repository:** `adeebnoor/ridi`  
**Branch:** `freeze/cfc-ridi-eligible-pool-v0.1`  
**Parent candidate-registry branch head:** `ccd08e7ff8467a58006e8d27012a90e35d223fb6`  
**Status:** RIDI-SIDE POOL IDENTITY FROZEN / BILATERAL EXACT-BYTE MIRROR PENDING / NO SEED / NO CASE SELECTION

## Authority and chronology

This record follows, and does not modify, the previously frozen CFC ↔ RIDI Shared Case Protocol v0.1 and its frozen eligibility gate.

- Shared Case Protocol v0.1 SHA-256: `d6bc94e90be4ac01bd8ee60f32aa3045dd827f4f3e9e64a68b82191615138571`
- Frozen eligibility checker SHA-256: `96ca16e12e3f2fecb5a06998eb28476e250b2a0965f2b26713da298391958904`
- Candidate registry SHA-256: `09824e8fa0837cc852b34c984b3ad7156a7433a57d672f4124356f4806e2fccf`
- Eligibility audit SHA-256: `23e027e7228c3a09d13b238619ca87389f304f3fb281c37b386cca6a6defe826`
- Frozen eligible-pool identity SHA-256: `ebb7e660199687650a5c03888839401cc6f88f5b3fe6a55a77649bb855a43ade`

The candidate registry contains 800 registrations. The frozen checker result is 800 ACCEPT and 0 REJECT.

No selection seed existed before this record, and none is created here.

## Independent CFC-side verification

Krzysztof Śliwka completed an independent CFC-side review dated 2026-09-29.

The review independently reproduced:

- 800 registrations;
- 800 ACCEPT;
- 0 REJECT;
- audit SHA-256 `23e027e7228c3a09d13b238619ca87389f304f3fb281c37b386cca6a6defe826`;
- eligible-pool SHA-256 `ebb7e660199687650a5c03888839401cc6f88f5b3fe6a55a77649bb855a43ade`.

The review also reports pre-selection structural checks over case identities, A/B arm pairing, dataset counts, specimen and endpoint bindings, grade vectors, pair fingerprints, and registry-row commitments, without using substantive CFC/RIDI outcomes, correctness, desired asymmetry, or scientific attractiveness for eligibility.

Reviewer report file as received by RIDI:
- `CFC_RIDI_Independent_Review_2026-09-29.pdf`
- bytes: `59073`
- SHA-256: `3a2bc84a0f3f4471b4140429200f76201e3fad47ea0d8e226044afe7902bfcf2`

The CFC reviewer explicitly approved the exact eligible-pool draft hash for a separate bilateral pool freeze and explicitly recorded that no seed or case selection had occurred.

## Frozen pool identity

The only pool identity approved by this RIDI-side record is:

```text
ebb7e660199687650a5c03888839401cc6f88f5b3fe6a55a77649bb855a43ade  eligible_pool.tsv
```

This digest is the exact deterministic pool output independently reproduced by the CFC reviewer under the unchanged frozen checker on the exact candidate registry.

Any pool bytes with a different SHA-256 are not the CFC ↔ RIDI Eligible Pool v0.1 and require a new version plus renewed bilateral approval.

## Source-provenance boundary retained

The bilateral freeze must retain the CFC review's stated upstream provenance limitation.

The 2026-09-29 CFC review did not independently inspect the original upstream:
- `contexts_800.jsonl`;
- `registered_generations_primary_800.jsonl`;
- original preregistration artifact.

Accordingly, this freeze records the complete delivered derived frame and its internal structural/hash bindings, but does not convert those upstream provenance claims into an independently reverified claim. No additional eligibility filtering is introduced by this record.

## Freeze boundary

This record freezes the RIDI-side pool identity only.

It does **not**:
- generate a seed;
- commit a seed;
- reveal a seed;
- score or rank candidate cases;
- select a case;
- instantiate the selected specimen;
- run CFC;
- run RIDI;
- exchange substantive raw outputs;
- interpret the comparison.

The bilateral pool freeze is complete only after an exact-byte CFC-side mirror of the approved pool identity is publicly recorded and verified.

Only after that mirror is recorded may the protocol advance to the joint seed commit–reveal step.

**Evidence before selection.**
