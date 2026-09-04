# CFC Project Status

## Current stage

CFC is currently in the external validation, demonstrator closure, and controlled-study preparation stage.

## Frozen / closed baselines

- Operator Wrapper v1.23 — promoted and byte-for-byte frozen.
- CFC Anchor 0.2.90rc1 — frozen deterministic executable controller checkpoint used through its public API.
- Formal State & Closure Specification v1.0 — formally frozen descriptive specification.
- External Replication Package v1.1 — closed replication package.
- Four-Track benchmark — frozen descriptive evidence.
- Restricted Phase-1 10K engineering campaign — completed.

The frozen baselines are not being modified during the current review phase.

## Demonstrator

CFC Demonstrator v1.0-rc1 is a separate external presentation and replay layer over the frozen CFC Anchor checkpoint.

Current demonstrator work is limited to repository/release reconciliation, documentation hygiene, verification, and final promotion. It does not modify controller logic.

## Current priority

The current priority is not further controller development.

The focus is now on:

1. closing the Demonstrator v1.0 release audit and repository reconciliation;
2. independent human methods review;
3. independent replication as a separate evidence class;
4. preregistration of the controlled A/B/C/D study only after activation blockers are closed;
5. comparison with adjacent LLM and agent-evaluation approaches without unsupported novelty claims.

## Validation philosophy

CFC is evaluated using frozen baselines so that controller behavior is not changed after observing evaluation results.

Internal engineering evidence, controlled causal evidence, and independent external replication are treated as separate evidence classes and must not be conflated.

## Current claims

CFC has produced internal engineering evidence within the restricted domains tested so far. Those results are not independent external validation and do not establish production readiness, universal correctness, or general AI-safety improvement.

Independent review, controlled confirmatory evaluation, and external replication remain open scientific milestones.

## Project scope

CFC is focused on one narrow reliability question:

> Does the available evidence and current system state actually justify a definitive conclusion?

It is not intended to replace general-purpose model evaluation, hallucination detection, safety testing, or factuality benchmarks.

Its purpose is to add a specific control layer around unsupported closure.

**Frozen Operator Wrapper baseline:** v1.23  
**Frozen executable controller checkpoint:** CFC Anchor 0.2.90rc1  
**Project stage:** External validation / demonstrator closure / controlled-study preparation  
**Author:** Krzysztof Śliwka
