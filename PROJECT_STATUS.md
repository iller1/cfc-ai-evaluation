# CFC Project Status

## Current stage

CFC is currently in the external validation and controlled-study preparation stage. Demonstrator source reconciliation and final local package validation are complete; publication of the final GitHub `cfc-demonstrator-v1.0` tag/release remains pending.

## Frozen / closed baselines

- Operator Wrapper v1.23 — promoted and byte-for-byte frozen.
- CFC Anchor 0.2.90rc1 — frozen deterministic executable controller checkpoint used through its public API.
- Formal State & Closure Specification v1.0 — formally frozen descriptive specification.
- External Replication Package v1.1 — closed replication package.
- Four-Track benchmark — frozen descriptive evidence.
- Restricted Phase-1 10K engineering campaign — completed.

The frozen baselines are not being modified during the current review phase.

## Demonstrator

CFC Demonstrator v1.0 is a separate external presentation and replay layer over the frozen CFC Anchor checkpoint.

The RC1 repository/release provenance defect was resolved by recovering the exact CASE_09 and CASE_10 bytes from the preserved RC1 release asset, verifying all recovered files against preserved SHA-256 anchors, and restoring them to the reconciled source tree.

The final v1.0 candidate was validated locally with:

- fresh manifest: 108/108 PASS;
- frozen wheel identity: PASS;
- preset replay: 10/10 PASS;
- custom regression: PASS;
- reviewer A/B: PASS.

The validated source candidate is present on `main`. Final GitHub tag/release publication is still pending and must not be described as completed until the tag and release asset actually exist.

## Current priority

The current priority is not further controller development.

The focus is now on:

1. publishing the already-validated Demonstrator v1.0 final tag/release;
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
**Demonstrator status:** v1.0 source/package candidate validated; GitHub final release publication pending  
**Project stage:** External validation / controlled-study preparation  
**Author:** Krzysztof Śliwka
