# CFC–RIDI v0.2 — CFC F4 Authority-Universe Candidate R1

Status: **CFC F4 CANDIDATE PUBLISHED / PENDING INDEPENDENT RIDI VERIFICATION**  
Authority: signed F0 feasibility workplan  
Prior gate: `F3_V0_2_BILATERAL_PASS_CLOSED`

## 1. Exact candidate identity

Artifact:

`collaboration/cfc-ridi/v0.2/F4_AUTHORITY_UNIVERSE_CANDIDATE_R1.json`

Review commit:

`f9b69e3627f8ecff5bfccdb5706c400eb1d08ff8`

Freeze ref:

`freeze/cfc-ridi-v0.2-f4-authority-universe-r1-candidate`

Exact identity:

- bytes: `8477`
- SHA-256: `65ecfac8b0a59c62d727291499b26519a8b8fdc800a983218ded3ce5fdadf2ec`
- Git blob: `21756730d6b7a8660c00486403066a61c7f9b660`

## 2. Cutoff

Authority-record cutoff:

`2026-10-01T20:31:34Z`

Cutoff basis:

RIDI bilateral F3 closure commit:

`e796224f7574df88a1a403834e6a369343f35698`

Only authority records demonstrably pre-existing at or before this cutoff are eligible for F4 membership.

No post-cutoff authority creation, relabeling, solicitation, semantic expansion, or applicability expansion is permitted.

## 3. Required authority boundaries

The exact F2 v0.2 adapter requires external state/authority for:

- IDENTITY;
- FAILURE_DOMAIN_TOPOLOGY;
- SOURCE_SEMANTICS;
- PROVENANCE;
- EVIDENCE_AUTHORITY;
- EPISTEMIC_ROLE;
- RETRIEVAL;
- SUPPORT_SET_INDEPENDENCE if required by the frozen support rule;
- host-pinned trust registrations/verifiers for the used authority boundaries.

Control metadata such as `decision_as_of`, decision scope, claim ID, neutral-arm binding and required support count are recorded separately and are not promoted into authority records.

## 4. Candidate universe result

CFC inspection located:

`0`

qualifying pre-existing substantive authority records under the F4 membership rule.

Therefore:

`f4_membership_count = 0`

and:

`complete_authority_case_available = NOT_DEMONSTRATED`

This is a bounded inspection conclusion, not a claim that no such record exists anywhere outside the inspected material.

If RIDI identifies a specific pre-cutoff record that satisfies the frozen membership rule, it must be nominated by immutable identity/hash and reviewed before bilateral F4 acceptance. It cannot be created or reinterpreted after the cutoff.

## 5. Explicit non-authority exclusions

The candidate does not treat the following as substantive authority:

- `contexts_800.jsonl`;
- `registered_generations_primary_800.jsonl`;
- RIDI preregistration by itself;
- source registration, doc IDs, passage hashes, grades, ranks or benchmark labels;
- recorded endpoint/model output/correctness;
- F3 synthetic fixture verifiers/attestations;
- `DeveloperFixtureSession`;
- `LOCAL_*` fixture authorities;
- built-in research fixture identities;
- example attestation code.

## 6. Inspection evidence

### SOURCE_PROVENANCE.md

- bytes: `2354`
- SHA-256: `c5c49b7c93c32bcfee23d20f6cb7456d9f6d14b9ab8d2846b6a320f91f4ac0ff`

The file states that `a1_preexisting_authority_available=TRUE` does not mean every CFC authority field is VERIFIED and records no original authoritative independent-support-count rule.

### Private pre-execution assessment

`CFC_RIDI_RAG-nq-test1035_PRIVATE_PREEXECUTION_ASSESSMENT_20260929.md`

- bytes: `5307`
- SHA-256: `9ccab3bedc11119d876eb396c42939224eb88401cd3dadc07146695eae3dc5d7`

That assessment records that the recovered source supplied passage content/identity but no external semantic-support, validity, independence, provenance or dependency record sufficient to establish the missing CFC authority state.

These inspection documents are evidence about availability and boundaries. They are not themselves members of the substantive authority universe.

## 7. Current decision boundary

CFC does **not** yet record:

`F4/F5_NO_GO_REAL_AUTHORITY_UNAVAILABLE`

because the exact F4 candidate must first undergo independent RIDI verification.

No F5 substantive execution is authorized.

If RIDI independently accepts the same zero-member universe and no qualifying pre-cutoff authority record is nominated under the frozen rule, the next required decision is whether the signed-F0 trigger:

`F4/F5_NO_GO_REAL_AUTHORITY_UNAVAILABLE`

has been met.

No authority may be synthesized to avoid that outcome.
