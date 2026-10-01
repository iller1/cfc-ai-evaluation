# CFC–RIDI v0.2 — F2 Candidate Nonfixture Adapter v0.1

Status: **CFC-SIDE F2 CANDIDATE FOR INDEPENDENT RIDI REVIEW**  
Controller baseline: `CFC Anchor 0.2.90rc1`  
Neutral schema: `CFC-RIDI Phase F Neutral Arm Schema v0.2 R1`

This package is a separate adapter artifact. It does not modify the frozen controller.

## Boundary

The adapter accepts exactly one neutral arm at a time.

It may use `recorded_endpoint.canonical` only as the candidate conclusion string.

It does not treat query text, passage text, IDs, hashes, dataset/task labels, source registration, model output, or bookkeeping metadata as authority.

It does not infer:

- identity;
- polarity;
- provenance;
- lineage/dependencies;
- epistemic role;
- scope/applicability;
- freshness;
- support-set independence;
- decision `as_of`;
- required support count.

Missing semantic/authority state remains missing.

## Two-stage path

`prepare_artifacts(...)` validates the bilaterally frozen neutral schema and emits:

1. a deterministic mapping manifest;
2. a deterministic authority/state requirements manifest.

This stage performs no substantive CFC evaluation and creates no authority.

`execute_with_resolved_state(...)` is available only for a later externally supplied, pre-frozen resolved-state package. The adapter itself contains no verifier implementation and does not create authority records.

Before controller use, the adapter verifies the supplied Anchor wheel file against the accepted F1 wheel SHA-256. The execution harness must then expose that verified wheel as the `cfc_anchor` runtime package in a clean environment.

## Accepted public surface

The adapter imports only package-level names listed in the bilaterally accepted F1 interface manifest and calls only approved public `Controller` methods.

There is no import or access to `cfc_anchor._engine`.

There is no monkeypatch path, private-state injection path, alternate controller path, or case-ID-specific branch.

## F2 status semantics

This candidate is not F2 acceptance.

RIDI remains the independent verifier.

If the accepted public API cannot faithfully receive the required later state, use:

`F2_NO_GO_API_OR_IMPLEMENTATION_BOUNDARY`

with the applicable frozen reason code, including `API_INCOMPATIBLE` where appropriate.

## Local representation tests

`test_adapter.py` covers:

- deterministic one-arm preparation;
- exact neutrality constants;
- question and passage SHA bindings;
- fixed source-corpus binding;
- exact ten ordered passage records;
- rejection of hidden/extra fields;
- no authority inference;
- no private Anchor reference in adapter source;
- explicit external-state requirement;
- exact Anchor wheel hash enforcement.

The CFC-side prepublication run passed `8/8`.

These tests are representation-only. They are not F3 and do not establish substantive authority or controller feasibility.

## Frozen identities referenced by the adapter

- Anchor wheel SHA-256:
  `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- Anchor engine SHA-256:
  `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- F1 interface SHA-256:
  `b23719df7efd75dc4d53b33808377e1002a044a88acc5354defd06dc59829184`
- Neutral schema R1 SHA-256:
  `d609a6d6af94d1108048360a349edb612b65b95336d5f90e6874c4da022b60a0`
- Registered source corpus SHA-256:
  `1485c0ad114673d297c580080d11086d3ace8827f9b586b15ad3928c7d0b21a1`

No F3/F4/F5 conclusion is implied by publication of this candidate.
