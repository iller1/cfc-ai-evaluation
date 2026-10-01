# CFC–RIDI v0.2 — CFC Independent Review and Exact-Hash Acceptance of Phase F Neutral Schema R1

Status: CFC REVIEW PASS / CFC EXACT-HASH ACCEPTANCE / PENDING BILATERAL NEUTRAL-SCHEMA CLOSURE  
Authority: signed F0 feasibility workplan  
F1 status: bilaterally accepted

No F2 adapter development is authorized by this record alone.

## 1. Reviewed artifact

RIDI artifact:

`collaboration/cfc-ridi/v0.2/PHASE_F_NEUTRAL_ARM_SCHEMA_DRAFT_R1.json`

RIDI review branch:

`review/cfc-ridi-v0.2-neutral-schema-r1`

CFC independently fetched the exact artifact through connected GitHub access and reproduced:

- bytes: `10353`
- SHA-256: `d609a6d6af94d1108048360a349edb612b65b95336d5f90e6874c4da022b60a0`
- Git blob: `c2d85835897350d9a10260e9febfbfa01d10eea6`

Result: exact identity MATCH.

## 2. F0/F1 review basis

Accepted F1 baseline:

`CFC Anchor 0.2.90rc1`

Accepted wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

Accepted F1 interface SHA-256:

`b23719df7efd75dc4d53b33808377e1002a044a88acc5354defd06dc59829184`

The F0 neutral-schema acceptance condition requires CFC to determine whether the required neutral fields can be consumed without hidden case-specific assumptions while preserving the accepted controller/interface boundary.

## 3. Neutrality review

CFC independently confirmed that R1:

- provides exactly one arm per mapping unit;
- contains no counterpart-arm payload;
- contains no RIDI PASS/FAIL;
- contains no endpoint equality/difference;
- contains no gold/correctness field;
- contains no passage retrieval-grade field;
- contains no expected-asymmetry field;
- permits `recorded_endpoint.canonical` only as the candidate claim/conclusion value;
- explicitly states that the endpoint is not evidence, authority or correctness;
- explicitly states that the schema asserts no positive authority and no semantic support;
- explicitly prohibits deriving independence from distinct-looking identifiers;
- explicitly leaves authoritative identity, provenance lineage, failure-domain topology, support-set independence, scope/applicability, freshness, evidence polarity, epistemic role and decision `as_of` semantics unspecified.

The schema therefore does not silently convert source availability, retrieval output, document identity, model output or bookkeeping metadata into CFC authority state.

## 4. Consumption under the accepted F1 interface

The schema can be consumed by a future F2 adapter without requiring a case-specific semantic assumption at the neutral-input boundary.

The permitted interpretation is bounded as follows:

- `recorded_endpoint.canonical` may be carried as the candidate conclusion string only;
- `query.question` and `passages[].text` are source content only;
- IDs, hashes, dataset/task labels, arm, draw, model/revision and source-binding metadata are bookkeeping/audit bindings only and do not establish CFC semantic or authority state;
- `recorded_endpoint.raw` is audit material only and is not promoted to evidence or authority;
- missing CFC semantic/authority state remains missing.

R1 does not require any controller-facing class or method outside the already accepted F1 interface.

R1 also does not require the adapter to invent subject/predicate/value semantics, claim identity, evidence polarity, provenance, independence, scope or temporal applicability. If later Phase F work cannot supply required state through the accepted public interface plus the separately frozen F4 authority universe without invention, the signed NO-GO semantics apply.

This is the critical distinction from the v0.1 pre-execution failure: schema acceptance does not imply executable authority-state completion.

## 5. Source-corpus verification boundary

R1 binds the registered source corpus SHA-256:

`1485c0ad114673d297c580080d11086d3ace8827f9b586b15ad3928c7d0b21a1`

That is the same `contexts_800.jsonl` identity previously independently verified by CFC during v0.1 source recovery:

- bytes: `25266491`
- rows: `1600`
- exact source SHA-256: MATCH

Historical CFC verification commit:

`f52053ba28b1001fd594d8f091ca8c68b3f93674`

This review does not claim that CFC reran RIDI's current 1,600-row R1 field-presence audit. RIDI records that audit in its pre-send review. CFC independently verifies the schema contract, exact schema identity, F0/F1 compatibility, and continuity to the already independently verified source-corpus identity.

## 6. Non-blocking F2 validation requirements

The following are implementation-validation points for F2/F3, not reasons to change R1:

- passage ordinal/order handling must be deterministic and must not create semantic identity or independence;
- binding hashes/IDs must remain audit/binding metadata and must not be promoted to authority;
- `source_registration` must remain non-authoritative binding metadata;
- any need for a neutral-schema field absent from R1 requires a versioned schema amendment and renewed bilateral acceptance;
- any need for a controller-facing surface outside the accepted F1 interface requires a versioned F1 amendment and renewed bilateral acceptance.

## 7. CFC decision

Result:

`PHASE_F_NEUTRAL_SCHEMA_R1_CFC_REVIEW_PASS`

CFC explicitly accepts the exact R1 artifact:

- bytes: `10353`
- SHA-256: `d609a6d6af94d1108048360a349edb612b65b95336d5f90e6874c4da022b60a0`
- Git blob: `c2d85835897350d9a10260e9febfbfa01d10eea6`

This is CFC-side exact-hash acceptance of the neutral schema only.

Bilateral neutral-schema closure still requires RIDI to record/confirm acceptance of the same exact artifact identity.

No F2 implementation begins before that closure.

F1 signed → neutral-schema exact-hash acceptance → F2.
