# CFC Project Status

## Current stage

CFC is currently in the external validation, controlled-study preparation, and bounded productization stage.

The final CFC Demonstrator v1.0 GitHub release has been published. Independent review, confirmatory causal evaluation, external replication, and external usability testing remain open.

## Frozen / closed baselines

- Operator Wrapper v1.23 — promoted and byte-for-byte frozen.
- CFC Anchor 0.2.90rc1 — frozen deterministic executable controller checkpoint used through its public API.
- Formal State & Closure Specification v1.0 — formally frozen descriptive specification.
- External Replication Package v1.1 — closed replication package.
- Four-Track benchmark — frozen descriptive evidence.
- Restricted Phase-1 10K engineering campaign — completed.

The frozen baselines are not being modified during the current review and productization phase.

## Demonstrator

CFC Demonstrator v1.0 is a separate external presentation and replay layer over the frozen CFC Anchor checkpoint.

The earlier RC1 repository/release provenance defect was resolved by recovering the exact CASE_09 and CASE_10 bytes from the preserved RC1 release asset, verifying the recovered files against preserved SHA-256 anchors, and restoring them to the reconciled source tree.

The final v1.0 package was validated with:

- fresh manifest: 108/108 PASS;
- frozen wheel identity: PASS;
- preset replay: 10/10 PASS;
- custom regression: PASS;
- reviewer A/B: PASS.

Final public release:

`https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0`

Release asset SHA-256:

`d4c46d435994a291cf09cc9ca880be06bd4271c83e2875f9fbf3f887bd08ae28`

## Integration Layer / Company Pilot track

A separate productization track now exists over the frozen Anchor. It does not modify CFC Anchor or Operator Wrapper.

Current integration candidate:

`CFC Integration Layer v0.4 RC`

Local RC validation includes:

- internal manifest: PASS;
- frozen Anchor identity: PASS;
- fresh virtual environment: PASS;
- offline wheel install: PASS;
- `cfc-doctor`: PASS;
- `cfc-demo`: PASS;
- integration regression: 11/11 PASS.

The integration layer provides a bounded Python API, CLI/JSON path, integrity smoke check, first-decision demo, and explicit declarative mapping for simple business fields.

External usability gates remain open:

- `TIME_TO_FIRST_CFC_DECISION <= 15 minutes` — NOT YET VERIFIED;
- `TIME_TO_FIRST_DOMAIN_MAPPING <= 30 minutes` — NOT YET VERIFIED.

These gates require previously unfamiliar external developers and cannot be satisfied by internal testing.

## Current priority

The current priority is not further controller development.

The active workstreams are:

1. independent human methods review;
2. independent replication as a separate evidence class;
3. preregistration of the controlled A/B/C/D study only after activation blockers are closed;
4. external usability testing of the Integration Layer RC;
5. controlled offline Company Pilot outreach and historical-case pilots;
6. comparison with adjacent LLM and agent-evaluation approaches without unsupported novelty claims.

## Validation philosophy

CFC is evaluated using frozen baselines so that controller behavior is not changed after observing evaluation results.

Internal engineering evidence, controlled causal evidence, independent external replication, external usability evidence, and commercial pilot outcomes are treated as separate evidence classes and must not be conflated.

## Current claims

CFC has produced internal engineering evidence within the restricted domains tested so far. Those results are not independent external validation and do not establish production readiness, universal correctness, legal accuracy, commercial ROI, or general AI-safety improvement.

Independent review, controlled confirmatory evaluation, external replication, external usability testing, and real customer pilot evidence remain open milestones.

## Project scope

CFC is focused on one narrow reliability question:

> Does the available evidence and current system state actually justify a definitive conclusion?

Its purpose is to add a specific control layer around unsupported closure.

**Frozen Operator Wrapper baseline:** v1.23  
**Frozen executable controller checkpoint:** CFC Anchor 0.2.90rc1  
**Demonstrator status:** v1.0 RELEASED  
**Integration status:** v0.4 RC; external usability NOT YET VERIFIED  
**Project stage:** External validation / controlled-study preparation / bounded productization  
**Author:** Krzysztof Śliwka
