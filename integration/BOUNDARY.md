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

## Evidence classes

Local RC validation is internal engineering evidence only.

External usability evidence begins only when a developer who has not previously integrated CFC performs the frozen timed test without live assistance from the author.
