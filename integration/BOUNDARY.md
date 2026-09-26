# Integration Layer Claim Boundary

The Integration Layer is **not** part of frozen CFC Anchor.

It is an external developer-facing adapter and mapping layer intended to reduce integration friction.

## What the current RC demonstrates

- a bounded Python API can invoke the exact frozen Anchor;
- the frozen wheel identity is checked;
- a clean offline installation path works locally;
- `ALLOW` and `STOP` can be obtained through a simplified API and CLI;
- raw frozen-controller output remains available for audit;
- simple explicit business fields can be mapped declaratively to normalized evidence states;
- positive and negative conclusions are exercised in regression tests.

## What the current RC does not demonstrate

- automatic contract or document understanding;
- automatic legal interpretation;
- automatic evidence classification from arbitrary enterprise data;
- production readiness;
- enterprise scalability;
- legal accuracy;
- regulatory compliance;
- commercial ROI;
- universal ease of integration;
- external developer usability;
- support for every possible CFC Anchor mechanism or domain mapping.

## Mapping boundary

The current declarative mapping layer intentionally supports only bounded, inspectable rules.

Examples include:

- boolean field → normalized evidence state;
- enum value → normalized evidence state;
- expiry date relative to an explicit decision date → `verified` or `stale`;
- exact field equality → expected or wrong scope.

The mapper does not use an LLM to infer undocumented semantics.

## Aggregation boundary

The current integration example may use an orchestration policy such as:

`all_checks_must_allow`

That is integration-layer orchestration logic. It must not be described as a frozen Anchor invariant unless separately established.

## Same-process runtime isolation boundary

Research against frozen CFC-next `0.3.0a2` found a bounded same-interpreter
cross-context interaction when independently created contexts register the same
canonical entity/event/version identity.

The observed transition was fail-closed:

`VERIFIED -> UNRESOLVED`

No unauthorized control closure was observed, and the diagnostic did not install
decision-accounting authorization.

Separating Controller objects is therefore **not** sufficient evidence that their
runtime registry state is independent.

For independent request/session semantics, integration code should use one of
these boundaries unless a different design is separately validated:

1. process isolation between independent CFC runs; or
2. explicit registry-level canonical identity coordination that prevents
   competing independent registrations of the same canonical identity.

Tenant-namespaced canonical identity removed the tested interference across all
14 blocker families in the bounded diagnostic.

This finding does not modify or rescore frozen CFC Anchor `0.2.90rc1`,
CFC-next `0.3.0a2`, or Integration Layer `v0.4 RC`. It is a deployment
constraint derived from separate research evidence.

See:
[peer-context isolation review](../docs/CFC_NEXT_0_3_0A2_PEER_CONTROLLER_ISOLATION.md).

## Evidence classes

Local RC validation is internal engineering evidence only.

External usability evidence begins only when a developer who has not previously integrated CFC performs the frozen timed test without live assistance from the author.
