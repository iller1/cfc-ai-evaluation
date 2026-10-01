# CFC–RIDI v0.2 — CFC F2 Candidate Adapter Publication Record

Status: CFC-SIDE CANDIDATE PUBLISHED / PENDING INDEPENDENT RIDI REVIEW  
Authority: signed F0 feasibility workplan  
F1: bilaterally exact-hash accepted  
Neutral schema R1: bilaterally exact-hash closed

## Candidate branch

`review/cfc-ridi-v0.2-f2-adapter-v0.1`

Candidate head commit:

`4167783eb48e1a1677107cb1359ad9b2f890017f`

The branch is exactly 4 commits ahead of the pre-F2 base:

`c8eb82fbae4f78ac11cab2ef49db3d21af78e722`

and contains only four added files under:

`collaboration/cfc-ridi/v0.2/f2_adapter/`

## Primary adapter source

`adapter.py`

- bytes: `28972`
- SHA-256: `4b975fda6242c9a7e33d0d692705ef6fe82683dbf2bddefc0345c2e5504b480a`
- Git blob: `85bd07b602d3555a306a5200457704fcfa0bffe3`

## Representation tests

`test_adapter.py`

- bytes: `6586`
- SHA-256: `4f70526185dbb69e4073c0baf89a6f924e8e1e220ba0317c339708bf5b152f34`
- Git blob: `04af56414b7aa370d67f31a12e2e0fa3a1be9845`

CFC-side prepublication representation run:

`PASS 8/8`

These tests are not F3.

## Boundary README

`README.md`

- bytes: `3479`
- SHA-256: `3bf666564b2c1a7f85526a3e223e7385e30a61c73e8d5f67ca0b17d954d7638a`
- Git blob: `2d3e763ebf83b9be5edc21bf9a4cb4a9d2efa606`

## Candidate manifest

`ADAPTER_MANIFEST.json`

- bytes: `1348`
- SHA-256: `32b8c36ebb434fa620cdae970ed12bbb389a1ae62d20be6005e78b7c0db89591`
- Git blob: `b34b948c15c453b7d35ecfaf8429af0616150987`

## Preserved boundaries

The candidate:

- accepts one neutral arm at a time;
- uses `recorded_endpoint.canonical` only as candidate conclusion;
- does not infer identity, polarity, provenance, independence, scope, freshness, epistemic role, decision `as_of`, or support count from neutral fields;
- contains no verifier implementation;
- creates no authority;
- contains no private Anchor import/access;
- contains no monkeypatch path;
- contains no private-state injection path;
- contains no alternate controller path;
- contains no case-ID-specific branch;
- pins the accepted Anchor wheel SHA-256 and checks the supplied wheel artifact before controller use;
- restricts controller-facing calls to the bilaterally accepted F1 public surface;
- requires later semantic/authority state to be supplied externally under later frozen Phase F gates.

## Reporting convention

CFC countersigned the RIDI-accepted F2 NO-GO reporting convention at:

`c8eb82fbae4f78ac11cab2ef49db3d21af78e722`

The convention is operative before the first F2 classification.

## Current decision state

This publication is not F2 bilateral acceptance.

RIDI remains the independent verifier.

No F3/F4/F5 conclusion is implied.

Any failure must be retained under the frozen F0 criteria and operative reporting convention.
