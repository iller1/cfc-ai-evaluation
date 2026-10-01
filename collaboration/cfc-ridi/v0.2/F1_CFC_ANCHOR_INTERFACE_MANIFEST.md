# CFC–RIDI v0.2 — F1 CFC Anchor Interface Manifest

Status: PROPOSED F1 INTERFACE CONTRACT / CFC-SIDE  
Baseline: `CFC Anchor 0.2.90rc1`  
Wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`  
Public API contract SHA-256: `fee18165ea5d4a29e72137028ec3cf5c637b85c83672437b2352fc316f53b66a`

No F2 adapter development is authorized until bilateral F1 acceptance.

## 1. Package boundary

Allowed package root:

`cfc_anchor`

Primary controller:

`cfc_anchor.Controller`

The external adapter must not import or call:

`cfc_anchor._engine`

or any other private/internal module or symbol not listed in this manifest.

## 2. Allowed public package-level classes

The proposed interface permits the public classes already exercised by the frozen Demonstrator path as required by a Phase F representation:

- `Controller`
- `HostTrustPolicy`
- `HostTrustRegistration`
- `IdentityAuthorityAttestation`
- `IdentityAuthorityVerdict`
- `SourceSemanticsAuthorityAttestation`
- `SourceSemanticsAuthorityVerdict`
- `ProvenanceAuthorityAttestation`
- `ProvenanceAuthorityVerdict`
- `EvidenceAuthorityAttestation`
- `EvidenceAuthorityVerdict`
- `EpistemicRoleAuthorityAttestation`
- `EpistemicRoleAuthorityVerdict`
- `RetrievalAuthorityAttestation`
- `RetrievalAuthorityVerdict`
- `FailureDomainTopologyAttestation`
- `FailureDomainTopologyVerdict`
- `SupportSetIndependenceAuthorityAttestation`
- `SupportSetIndependenceAuthorityVerdict`

Use of any additional public class would require explicit F1 interface amendment and bilateral acceptance before use by F2.

## 3. Allowed public Controller methods

The proposed adapter may use only the following Controller methods where required by the accepted neutral schema and authority-state representation:

- `draft_identity(...)`
- `install_verified_identity(...)`
- `draft_failure_domain_topology(...)`
- `install_verified_failure_domain_topology(...)`
- `draft_source_semantics(...)`
- `install_verified_source_semantics(...)`
- `draft_evidence_record(...)`
- `verify_evidence_provenance(...)`
- `verify_evidence_authority(...)`
- `draft_epistemic_role(...)`
- `install_verified_epistemic_role(...)`
- `evidence_with_epistemic_role(...)`
- `evidence_record_mapping(...)`
- `draft_snapshot(...)`
- `install_verified_snapshot(...)`
- `draft_support_set_independence(...)`
- `install_verified_support_set_independence(...)`
- `identity_commitment(...)`
- `failure_domain_topology_commitment(...)`
- `source_semantics_commitment(...)`
- `provenance_commitment(...)`
- `evidence_authority_commitment(...)`
- `snapshot_commitment(...)`
- `support_set_independence_commitment(...)`
- `evaluate_snapshot(...)`

No method outside this list is authorized for the F2 adapter unless the F1 interface contract is explicitly amended and bilaterally re-accepted.

### Commitment-helper completeness amendment

The listed public commitment helpers are included because the frozen public Demonstrator lifecycle uses them to bind public draft objects to the corresponding attestation commitments before verified installation. Their inclusion does not broaden the package boundary beyond the frozen public API and does not authorize any private/internal access.

## 4. Adapter boundary

The adapter may transform accepted neutral-schema fields into calls to the listed public API only.

The adapter must not:

- modify controller code;
- monkeypatch controller behavior;
- import `cfc_anchor._engine`;
- inject unapproved private runtime state;
- write directly to controller-private registries;
- call private/internal authorization functions;
- manufacture evidence or authority;
- infer authority from retrieval relevance, model output, source identity or expected experimental result;
- introduce case-specific exceptions.

If faithful representation requires any prohibited action, Phase F must record the applicable F2 NO-GO rather than crossing this boundary.

## 5. Host-trust boundary

Public trust/attestation installation APIs do not by themselves establish that qualifying real authority exists.

Any verifier/authority used later must satisfy the independently accepted F4/F5 authority-universe rules.

Demonstrator synthetic verifiers are fixtures only and are not authorized as substantive v0.2 authority.

## 6. Representation limitation

The public interface consumes explicit structured state.

It does not automatically determine correct domain semantics from arbitrary documents or natural-language material.

Upstream semantic mapping must remain explicit, reviewable and bounded by the later accepted neutral schema.

## 7. Acceptance meaning

If bilaterally accepted, this manifest defines the maximum controller-facing surface available to the F2 candidate adapter.

It does not approve an adapter implementation.

It does not authorize substantive execution.

It does not establish real authority availability.

It does not alter the frozen controller.

F1 before F2.
