# CFC Attestation Lifecycle E2E Plan v0.1

Status: **PRE-EXECUTION / EXPECTATIONS FROZEN BEFORE E2E RUN**
Date: 2026-09-13

## Boundary

This plan tests the external chain:

`host attestation lifecycle guard -> exact frozen CFC Anchor 0.2.90rc1`

It does not modify or reinterpret Operator Wrapper v1.23, CFC Anchor 0.2.90rc1, or CFC Demonstrator v1.0.

The Demonstrator's `server.run_custom` path is used only as a verified invocation adapter for the exact frozen wheel. Final controller outcome is read from the raw frozen-controller field `control_closure`; presentation wording is not used to repair or reinterpret it.

## Frozen artifact identity required before execution

- Demonstrator release ZIP SHA-256: `d4c46d435994a291cf09cc9ca880be06bd4271c83e2875f9fbf3f887bd08ae28`
- Anchor wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- Anchor engine SHA-256: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- Mandatory gates: `49`
- Persistence schema: `DECISION_PERSISTENCE_HISTORY_V6`

Execution must abort on identity mismatch.

## Invocation rule

If guard result is `STOP` or `UNRESOLVED`, normal E2E orchestration MUST NOT call Anchor. The recorded Anchor result is `SKIPPED_BY_GUARD`.

If guard result is `ELIGIBLE_FOR_ANCHOR`, Anchor is called with a separately bounded synthetic fixture. `ELIGIBLE_FOR_ANCHOR` is never translated to `ALLOW` by the guard.

## Predeclared expectations

ATL-001..ATL-023 retain the exact guard expectations in `ATTESTATION_LIFECYCLE_TEST_MATRIX_v0.1.md`.

Only two normal-chain cases are expected to reach Anchor:

- `ATL-018`: lifecycle-valid single attestation. Downstream fixture has one current positive evidence record, `required_independent_supports=1`, expected frozen Anchor outcome: `ALLOW`.
- `ATL-019`: lifecycle-valid two-attestation set with distinct roots and failure domains. Downstream fixture has two current positive evidence records, distinct modeled provenance, explicit frozen-API independence authority, `required_independent_supports=2`, expected frozen Anchor outcome: `ALLOW`.

For every other ATL case, expected frozen Anchor outcome in normal orchestration is `SKIPPED_BY_GUARD`.

## E2E PASS rule

A case PASS requires:

1. exact expected guard state;
2. correct call/skip behavior;
3. for ATL-018/019, raw `control_closure=true` from the exact frozen Anchor and matching frozen engine identity.

## Breaker rule

A lifecycle breaker is only present if normal orchestration reaches frozen-controller closure where the predeclared lifecycle state requires `STOP` or `UNRESOLVED`.

No reason-string difference counts as a breaker.

A deliberate guard bypass, if tested separately, must be labeled `ADVERSARIAL_BYPASS` and cannot be described as normal integration behavior.
