# CFC–RIDI v0.2 — Bilateral F2 Exact-Hash Closure

Status: F2 BILATERALLY ACCEPTED / F3 NEXT  
Authority: signed F0 feasibility workplan  
F1: bilaterally exact-hash accepted  
Neutral schema R1: bilaterally exact-hash closed  
F2 reporting convention: bilateral and operative

## Accepted candidate

Candidate:

`CFC-RIDI-F2-ADAPTER-v0.1`

Exact candidate commit:

`4167783eb48e1a1677107cb1359ad9b2f890017f`

Pre-F2 base:

`c8eb82fbae4f78ac11cab2ef49db3d21af78e722`

The candidate branch is exactly four commits ahead of the pre-F2 base and contains only four added files under:

`collaboration/cfc-ridi/v0.2/f2_adapter/`

## Accepted artifact identities

### adapter.py

- bytes: `28972`
- SHA-256: `4b975fda6242c9a7e33d0d692705ef6fe82683dbf2bddefc0345c2e5504b480a`
- Git blob: `85bd07b602d3555a306a5200457704fcfa0bffe3`

### test_adapter.py

- bytes: `6586`
- SHA-256: `4f70526185dbb69e4073c0baf89a6f924e8e1e220ba0317c339708bf5b152f34`
- Git blob: `04af56414b7aa370d67f31a12e2e0fa3a1be9845`

### README.md

- bytes: `3479`
- SHA-256: `3bf666564b2c1a7f85526a3e223e7385e30a61c73e8d5f67ca0b17d954d7638a`
- Git blob: `2d3e763ebf83b9be5edc21bf9a4cb4a9d2efa606`

### ADAPTER_MANIFEST.json

- bytes: `1348`
- SHA-256: `32b8c36ebb434fa620cdae970ed12bbb389a1ae62d20be6005e78b7c0db89591`
- Git blob: `b34b948c15c453b7d35ecfaf8429af0616150987`

CFC independently re-fetched the exact candidate commit and reproduced every byte length, SHA-256 and Git blob above before countersigning.

## RIDI independent acceptance

RIDI independently reviewed the same exact candidate and recorded:

`F2_CANDIDATE_ADAPTER_V0_1_RIDI_REVIEW_PASS`

and:

`F2_CANDIDATE_ADAPTER_V0_1_RIDI_EXACT_HASH_ACCEPTED`

RIDI review commit:

`09ea8a3131bcfeb42531d49fc2a9a15772964a8c`

RIDI independently reproduced:

- exact candidate repository delta;
- all four artifact identities;
- published representation suite `PASS 8/8`;
- static F1 public-boundary audit;
- positive public-interface probe against the exact frozen Anchor wheel.

## CFC countersign

CFC explicitly accepts the exact same F2 candidate identity and artifact hashes above.

No adapter byte is changed by this countersign.

## Effect

F2 exact-hash bilateral acceptance is complete.

This does not imply:

- F3 adversarial-suite acceptance;
- F4 authority-universe acceptance;
- F5 calibration acceptance;
- substantive CFC/RIDI execution approval.

The exact accepted F2 adapter is now the immutable baseline for F3.

Any adapter change requires a new versioned F2 candidate and renewed bilateral F2 review/acceptance.

Next gate:

`F3 — REPRESENTATION-ONLY ADVERSARIAL SUITE`

F0 signed → F1 closed → neutral schema closed → F2 closed → F3.
