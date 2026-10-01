# CFC–RIDI v0.2 — F2 Candidate Nonfixture Adapter v0.2

Status: **CFC-SIDE F2 REPAIR CANDIDATE FOR INDEPENDENT RIDI REVIEW**  
Controller baseline: `CFC Anchor 0.2.90rc1`  
Neutral schema: `CFC-RIDI Phase F Neutral Arm Schema v0.2 R1`  
Frozen F3 criteria: R1, unchanged

This is a new versioned F2 candidate created after the bilaterally reproduced F3 R1 NO-GO on adapter v0.1.

The frozen v0.1 adapter remains unchanged.

## Repair scope

The v0.1 F3 failure was:

`F3-T05 — Cross-case / cross-arm resolved-state substitution`

Exact finding:

`mutation was silently ignored; diagnostic result identical to control`

v0.2 adds one mechanical representation boundary:

`neutral_arm_binding`

Every resolved-state package must now carry an exact deterministic binding to the neutral arm being executed.

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

The adapter compares the supplied binding with the binding deterministically derived from the validated neutral arm.

Any mismatch raises `BindingError` before Controller construction or evaluation.

This prevents a resolved-state package prepared for one case/arm from being reused for another case/arm merely because passage-level bindings happen to be compatible.

## What did not change

v0.2 does not:

- modify the frozen Anchor;
- expand the accepted F1 public interface;
- change the neutral schema;
- change the frozen F3 criteria;
- create authority;
- infer identity, polarity, provenance, lineage, independence, scope, freshness, epistemic role, decision `as_of`, or support count;
- add case-specific exceptions;
- add private Anchor access;
- add monkeypatching or private-state injection.

The repair is representation-only and mechanical.

## Two-stage path

`prepare_artifacts(...)` validates one neutral arm and emits deterministic mapping and authority/state requirement manifests.

`authority_requirements(...)` now exposes the exact `neutral_arm_binding` that any later resolved-state package must reproduce.

`execute_with_resolved_state(...)` validates the root binding before constructing the public Controller path.

The adapter still contains no substantive verifier implementation and creates no authority.

## Regression tests

The v0.2 representation suite retains all v0.1 tests and adds:

1. valid exact root binding is accepted by resolved-state validation;
2. altered root `case_id` is rejected;
3. foreign `case_id + arm` binding with otherwise compatible passage bindings is rejected.

The candidate must be tested against the exact frozen Anchor wheel before publication.

These are F2 representation tests only. They are not the F3 rerun.

## Frozen identities retained

- Anchor wheel SHA-256:
  `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- Anchor engine SHA-256:
  `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- F1 interface SHA-256:
  `b23719df7efd75dc4d53b33808377e1002a044a88acc5354defd06dc59829184`
- Neutral schema R1 SHA-256:
  `d609a6d6af94d1108048360a349edb612b65b95336d5f90e6874c4da022b60a0`
- F3 criteria R1 SHA-256:
  `f9640dbaec55a2b381a159825fe27a9e87502b75b20bbfbcf4382ca44cd887a2`
- Failed frozen F2 v0.1 commit:
  `4167783eb48e1a1677107cb1359ad9b2f890017f`

No F3/F4/F5 conclusion is implied by publication of v0.2.
