# CFC–RIDI v0.2 — F2 Adapter v0.2 Candidate Publication

Status: CFC-SIDE REPAIR CANDIDATE PUBLISHED / PENDING INDEPENDENT RIDI REVIEW  
Authority: signed F0 feasibility workplan  
Prior F3 status: `F3_NO_GO_REPRESENTATION_INVALID` on F2 adapter v0.1  
Repair target: `F3-T05 — Cross-case / cross-arm resolved-state substitution`

## Candidate branch and exact commit

Branch:

`review/cfc-ridi-v0.2-f2-adapter-v0.2`

Exact candidate commit:

`930d7b0119159eaedbaf947691d9510b4c61d81c`

The frozen F2 v0.1 candidate remains unchanged at:

`4167783eb48e1a1677107cb1359ad9b2f890017f`

## Repair

v0.2 introduces a deterministic root-level:

`neutral_arm_binding`

The resolved-state package must reproduce the exact binding derived from the validated neutral arm.

The binding covers:

- neutral-schema SHA-256;
- `case_id`;
- `arm`;
- dataset;
- task;
- draw;
- question SHA-256;
- registered-context-line SHA-256;
- endpoint-record SHA-256;
- candidate-conclusion SHA-256;
- canonical SHA-256 of the ordered passage-binding set.

A mismatch raises `BindingError` before Controller construction or evaluation.

This directly addresses the reproduced T05 substitution path without changing controller semantics or the accepted F1 public interface.

## Exact component identities

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

## CFC-side representation verification

CFC independently reran the exact published v0.2 adapter/test source bytes.

Result:

`PASS 10/10`

The retained v0.1 representation tests all remain present.

New regression coverage includes:

- exact valid root binding accepted;
- altered root `case_id` rejected;
- foreign `case_id + arm` binding rejected even when passage-level bindings remain compatible.

The locally executed `adapter.py` and `test_adapter.py` SHA-256 values matched the GitHub candidate identities above exactly.

## Public-interface verification boundary

CFC did not rerun the public-interface probe locally because the current local runtime did not contain the frozen Anchor wheel.

The candidate includes `probe_public_api.py` for independent RIDI execution against the exact frozen wheel.

The F1 public import/method surface, wheel-verification function and private-access boundary are unchanged from the bilaterally accepted v0.1 adapter.

This record does not claim a new local public-interface probe result.

## Unchanged boundaries

v0.2 does not:

- modify CFC Anchor 0.2.90rc1;
- expand the bilaterally accepted F1 interface;
- modify Neutral Schema R1;
- modify F3 Criteria R1;
- create or upgrade authority;
- infer semantic state from neutral metadata;
- add case-specific outcome logic;
- access private Anchor internals;
- use monkeypatching or private-state injection.

## Current state

This is a candidate publication only.

F2 v0.2 is not bilaterally accepted yet.

No F3 rerun and no F4 progression are authorized until RIDI independently reviews and accepts this exact F2 candidate identity.

If F2 v0.2 is bilaterally accepted, the next required step is a complete T01–T15 rerun under the unchanged frozen F3 criteria.
