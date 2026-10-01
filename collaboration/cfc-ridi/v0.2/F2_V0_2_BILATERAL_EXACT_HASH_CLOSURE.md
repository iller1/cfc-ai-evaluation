# CFC–RIDI v0.2 — Bilateral F2 Adapter v0.2 Exact-Hash Closure

Status: F2 v0.2 BILATERALLY ACCEPTED / F3 COMPLETE RERUN NEXT  
Authority: signed F0 feasibility workplan

## Accepted candidate

Candidate:

`CFC-RIDI-F2-ADAPTER-v0.2`

Exact candidate commit:

`930d7b0119159eaedbaf947691d9510b4c61d81c`

Prior failed v0.1 remains frozen at:

`4167783eb48e1a1677107cb1359ad9b2f890017f`

## Exact accepted identities

### adapter.py
- bytes: `30630`
- SHA-256: `15b7d01787237b2e5f0d1ca106c4e84aaf1976a2512179c79c458fe3d80e634b`
- Git blob: `373598e8774622cc91d43b811eb636a231bd906c`

### test_adapter.py
- bytes: `8853`
- SHA-256: `3798cfb0b9c79311cb74b4bd5be71c2805ff225d316a57f2fb55c2d8462fd732`
- Git blob: `81d948ef8cc19ad471eeb05121fa64f7a885e6aa`

### README.md
- bytes: `3891`
- SHA-256: `0c441a05b75c62b827c69c0d40a83d7ede02b66d40b757156e3ddcec4d070ba7`
- Git blob: `55df7702ed90f6134762136171e5557cdde692a2`

### probe_public_api.py
- bytes: `730`
- SHA-256: `cf330aabe63cb5b1722bdbffc0ec92980e4d312cbcdf771c69c7fff6b4a2622a`
- Git blob: `4125a52565edc69a026ddd646cdd32880e68a137`

### ADAPTER_MANIFEST.json
- bytes: `2125`
- SHA-256: `6e56866ac5d6ee7eddc82a06d8c172cb886d38d98f2e7fa1fa76d3afa03aa264`
- Git blob: `2bb1efff7b5da612c77a86afae8f0f90c5dac402`

CFC re-fetched the exact candidate commit and confirmed the same Git blob identities before countersign.

## RIDI independent acceptance

RIDI independently reproduced:

- `PASS 10/10`
- `PUBLIC_INTERFACE_PROBE_PASS`
- rejection of every tested `neutral_arm_binding` mismatch
- unchanged accepted F1 public-interface boundary

RIDI decision:

`F2_ADAPTER_V0_2_RIDI_REVIEW_PASS`

`F2_ADAPTER_V0_2_RIDI_EXACT_HASH_ACCEPTED`

RIDI review commit:

`cfe06427b7cac6e86d11a877e09792101302f5fc`

## CFC countersign

CFC explicitly accepts the exact same v0.2 identity above.

Result:

`F2_ADAPTER_V0_2_BILATERAL_EXACT_HASH_CLOSED`

No v0.2 adapter byte is changed by this countersign.

## Effect

The exact v0.2 candidate becomes the immutable F2 baseline for the renewed F3 run.

Frozen F3 Criteria R1 remain unchanged.

No F4 progression is authorized before a complete T01–T15 rerun passes.

Next required step:

`F3 — COMPLETE T01–T15 RERUN AGAINST F2 v0.2`
