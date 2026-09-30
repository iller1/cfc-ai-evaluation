# CFC–RIDI v0.2 — F1 Single-Baseline Nomination

Status: CFC-SIDE NOMINATION FOR INDEPENDENT RIDI REVIEW  
Authority: signed F0 feasibility workplan  
No F2 adapter development is authorized by this nomination.

## 1. Nominated baseline

CFC nominates exactly one signed-workplan candidate:

`CFC Anchor 0.2.90rc1`

Role:

`deterministic executable controller`

Frozen wheel:

`demonstrator/cfc_anchor-0.2.90rc1-py3-none-any.whl`

Wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

Engine SHA-256:

`77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`

Public API contract SHA-256:

`fee18165ea5d4a29e72137028ec3cf5c637b85c83672437b2352fc316f53b66a`

Protected identity status:

`FROZEN PUBLIC API V1`

Public release reference:

`cfc-demonstrator-v1.0`

Tag commit:

`ba3efb6592b4b8602799fd6ec136c0ab1edefbbe`

## 2. Exact proposed adapter-facing interface

The proposed Phase F adapter-facing interface is the frozen public Python package interface rooted at:

`cfc_anchor.Controller`

together with the public package-level data/attestation/verdict classes required by the declared host-trust and evidence-installation lifecycle.

The exact interface contract for F1 is recorded separately in:

`F1_CFC_ANCHOR_INTERFACE_MANIFEST.md`

The adapter may use only the listed public imports and public Controller methods in that manifest.

No `cfc_anchor._engine` access is included in the proposed interface.

## 3. Factual reasons for nomination under the F1 acceptance rule

This nomination is based on the signed-F0 acceptance rule, not on comparative ranking.

The nominated baseline has an already-frozen public package/API identity.

Existing public CFC demonstration/integration paths show that an external layer can invoke the frozen Anchor without:

- modifying the frozen controller;
- adapter-side monkeypatching;
- injecting unapproved private runtime state;
- calling `cfc_anchor._engine`;
- using an unapproved private/internal authorization bypass.

The controller remains read-only.

The proposed interface therefore provides a bounded path for F2 feasibility work if and only if RIDI independently verifies and bilaterally accepts this F1 package.

## 4. Known limitations retained

This nomination does not claim that the Anchor can automatically derive correct semantics from arbitrary source material.

The adapter must receive or construct only explicitly represented structured inputs permitted by the later accepted neutral schema and authority-state rules.

The adapter may not:

- create evidence, authority or semantic support;
- infer hidden authority;
- synthesize authority merely to reach execution;
- broaden scope to rescue a case;
- use case-specific exceptions;
- depend on expected CFC/RIDI outcomes;
- use private/internal controller state.

The simplified Integration Layer RC does not expose every Anchor mechanism and is not itself nominated as the F2 adapter.

No substantive real-authority availability claim is made at F1.

## 5. Non-nominated candidate

`CFC-next 0.3.0a2` remains an accurately inventoried signed-workplan candidate but is not nominated for this Phase F path.

This is not a negative ranking or rejection of that baseline.

Its frozen candidate implementation has an internal dependency on private Anchor internals including `cfc_anchor._engine`. That fact is distinct from adapter-side access, as already recorded and independently verified.

The present nomination chooses the Anchor public-interface path because it directly instantiates the F1 adapter-boundary rule with a pre-existing frozen public API.

## 6. F1 state after publication

This artifact is a CFC-side nomination only.

It does not constitute bilateral F1 acceptance.

RIDI independent verification remains required.

No F2 adapter source may be developed or treated as a Phase F experiment artifact before bilateral acceptance of:

1. this exact baseline identity; and
2. the exact adapter-facing interface contract.

F0 remains signed and unchanged.

v0.1 remains closed and immutable.

F1 before F2.
