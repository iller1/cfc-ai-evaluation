# CFC–RIDI v0.2 — F1 CFC-Side Candidate Inventory

Status: DESCRIPTIVE INVENTORY ONLY  
Authority: signed F0 feasibility workplan  
Purpose: record immutable identity, adapter-facing interface, and known representability/reachability boundaries for the two controller baseline candidates already named in F0.

This document does not nominate, rank, prefer, or select a baseline.

No F2 adapter development is authorized by this inventory.

---

## Candidate A — CFC Anchor 0.2.90rc1

### Exact identity

Name:

`CFC Anchor 0.2.90rc1`

Status:

Frozen deterministic executable controller checkpoint.

Frozen wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

Frozen engine SHA-256:

`77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`

Public frozen execution reference:

`cfc-demonstrator-v1.0`

Tag commit:

`ba3efb6592b4b8602799fd6ec136c0ab1edefbbe`

The final Demonstrator v1.0 release is an external presentation/replay layer over the unchanged frozen Anchor and contains the pinned frozen wheel identity.

### Adapter-facing interface

The frozen wheel exposes a Python package API through `cfc_anchor`.

Primary controller entry point:

`cfc_anchor.Controller`

The demonstrated public API path includes structured host-trust registration, identity, source-semantics, provenance, evidence-authority, epistemic-role, retrieval-snapshot, failure-domain-topology and support-set-independence operations, with terminal evaluation through the frozen Controller API.

The existing Demonstrator invokes the frozen controller without replacing or modifying its logic.

A separate Integration Layer RC also demonstrates an external bounded adapter over the same frozen Anchor while retaining the raw controller result for audit.

### Representability / reachability boundaries

The Anchor does not automatically infer correct domain semantics from arbitrary documents, contracts, enterprise records, or natural-language inputs.

A host or adapter must explicitly map upstream information into the structured evidence, authority, scope, provenance, dependency, retrieval, and claim representations required by the controller.

The current Integration Layer intentionally supports bounded, inspectable mappings and does not demonstrate general automatic semantic mapping.

Synthetic verifier implementations used in demonstration fixtures are fixture trust components and must not be treated as independent real-world authority.

Not every Anchor mechanism is exposed by the simplified Integration Layer RC.

### Controller modification / bypass status

Controller modification required:

`NO`

Adapter-side monkeypatching required:

`NO`

Private-state injection required for the demonstrated public API path:

`NO`

Private/internal bypass required for ordinary frozen evaluation:

`NO`

The candidate can therefore be evaluated through its frozen package interface without modifying the frozen controller.

---

## Candidate B — CFC-next 0.3.0a2

### Exact identity

Name:

`CFC-next 0.3.0a2`

Status:

Frozen decision-accounting candidate.

Canonical frozen Git ref:

`frozen/cfc-next-0.3.0a2`

Freeze merge commit:

`568282c1f66af9f1f2fad8cf2b04b08226b9aea6`

Candidate source SHA-256:

`dc8ae4f2d51296d68ecf5e75ac861faf1f50f062e1761e0814ce157f08a588a7`

Underlying frozen Anchor reference:

`CFC Anchor 0.2.90rc1`

Underlying Anchor wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

No separately pinned candidate wheel is identified in the 0.3.0a2 replication manifest; the frozen candidate source SHA-256 is the canonical candidate source commitment.

### Adapter-facing interface

The candidate package exports:

- `Controller`
- `CANDIDATE_VERSION`
- `FROZEN_REFERENCE`
- `generic_accounting_node_valid`

Its `Controller` subclasses the frozen Anchor `Controller`.

The candidate additionally exposes decision-accounting lifecycle methods including:

- `draft_decision_generic_dependency_accounting(...)`
- `install_verified_decision_generic_dependency_accounting(...)`

The candidate preserves inherited frozen-controller evaluation behavior while adding the separately versioned decision-accounting path.

### Representability / reachability boundaries

The candidate-specific decision-accounting path requires structured evidence and an already represented decision context.

It does not solve arbitrary upstream semantic mapping.

Installation requires the relevant retrieval scope and host-trust / attestation / verifier conditions to be satisfied.

The frozen replication reference does not claim that the underlying global frozen registries support arbitrary same-interpreter multi-threaded stateful writes.

The tested concurrency claim is limited to independent fresh processes.

Shared registry objects are observable.

In the tested 14-case state-isolation review, candidate-installed BOUND accounting did not authorize an ordinary frozen `Controller` evaluation in the tested same-process contexts.

No historical frozen result was rescored.

### Controller modification / bypass status

Frozen Anchor modification required:

`NO`

Adapter-side monkeypatching required:

`NO`

Import-time monkeypatching:

`NO`

The 0.3.0a2 baseline specifically removed the import-time mutation present in the earlier 0.3.0a1 experimental candidate.

However, the frozen 0.3.0a2 implementation itself imports and uses private/internal Anchor implementation symbols, including `cfc_anchor._engine` and private controller-module constants/helpers.

Therefore:

Private Anchor implementation dependency inside the candidate baseline:

`YES`

Private-state injection required by an external adapter merely to call the exported candidate API:

`NO`

Private/internal bypass required by an external adapter:

`NO`, provided the adapter uses the exported candidate interface and does not reach around it.

This private/internal dependency is a property of the frozen candidate baseline itself and is recorded separately from adapter-side access requirements.

---

## Neutral F1 conclusion

Both candidates are recorded without preference.

Candidate A provides a frozen Anchor API with an externally demonstrated adapter path and no adapter-side requirement for controller modification or private-state access.

Candidate B provides a separately frozen decision-accounting extension with an exported controller interface and no import-time monkeypatch, while retaining implementation-level dependency on private Anchor internals.

This inventory does not determine whether either interface is sufficient for the RIDI v0.2 feasibility contract.

That determination belongs to bilateral F1 review.

No baseline is nominated here.

No F2 adapter development is authorized here.

F0 remains signed and unchanged.

v0.1 remains closed and immutable.
