# Frozen Baselines Manifest

Version: 0.1  
Date: 2026-10-06  
Status: **NORMATIVE REGISTRY FOR CONTROL STACK DEVELOPMENT**

## Purpose

This manifest separates artifacts that are frozen from artifacts that remain mutable during Control Stack development.

A version label alone is not treated as a cryptographic identity. Where an exact digest is known, it is recorded. Where a digest is not recorded here, the manifest does not invent one.

## Registry classes

- `FROZEN_BYTE_IDENTITY` — bytes must not change in this development line.
- `FROZEN_SEMANTICS` — historical semantics/results must not be reinterpreted or rescored.
- `RELEASED_PRESENTATION` — released presentation/replay artifact; historical release remains immutable.
- `RELEASE_CANDIDATE` — may still change before promotion under its own gates.
- `HOST_MUTABLE` — application/integration layer may evolve without changing frozen CFC semantics.
- `EXTERNAL_EVIDENCE_ONLY` — result/evidence class; not a code baseline.
- `EXPERIMENTAL` — exploratory lane with no authority to rewrite frozen artifacts.

## Frozen baselines

| Artifact | Version / identity | Registry class | Mutation rule |
| --- | --- | --- | --- |
| Operator Wrapper | v1.23 | `FROZEN_BYTE_IDENTITY` | No byte changes. New behavior requires a separately versioned artifact. |
| Operator Wrapper SHA-256 | `95277663c445509af0820c3abdddaa295dfaaf93dd077ce32897b185b80957d8` | `FROZEN_BYTE_IDENTITY` | Any mismatch is a hard identity failure. |
| CFC Anchor | `0.2.90rc1` | `FROZEN_BYTE_IDENTITY` + `FROZEN_SEMANTICS` | No controller edits in the Control Stack line. Host layers may only adapt explicit inputs/outputs. |
| Formal State & Closure Specification | v1.0 | `FROZEN_SEMANTICS` | Historical specification remains the descriptive baseline. New contracts must be separately versioned. |
| External Replication Package | v1.1 | `FROZEN_BYTE_IDENTITY` | Closed package. Do not replace historical bytes. |
| External Replication Package SHA-256 | `ccd95f257e43612620ed74c1a4b2a81ff19a1efe3eed0192e30bb05118134cae` | `FROZEN_BYTE_IDENTITY` | Any mismatch is a hard identity failure. |
| Four-Track benchmark | frozen historical benchmark | `FROZEN_SEMANTICS` | No historical rescoring after reveal. New scoring requires a new study/version. |
| Restricted Phase-1 10K engineering campaign | completed historical campaign | `FROZEN_SEMANTICS` | Results remain historical evidence and are not rewritten after later discoveries. |

## Released presentation baseline

| Artifact | Version / identity | Registry class | Mutation rule |
| --- | --- | --- | --- |
| CFC Demonstrator | v1.0 | `RELEASED_PRESENTATION` | Historical release is immutable. New UX must use a new version/branch. |
| Demonstrator v1.0 release asset SHA-256 | `d4c46d435994a291cf09cc9ca880be06bd4271c83e2875f9fbf3f887bd08ae28` | `FROZEN_BYTE_IDENTITY` | Used as release identity anchor. |

## Current mutable host/application artifacts

| Artifact | Current state | Registry class | Allowed changes |
| --- | --- | --- | --- |
| Pro Beta host application | active | `HOST_MUTABLE` | UI/API/persistence controls may evolve if frozen controller semantics remain unchanged. |
| Durable HAWM snapshot → CFC run binding | production verified | `HOST_MUTABLE` | May receive fixes/extensions under new tests; historical verification receipts remain immutable. |
| Evidence Drift v0.1 | production verified | `HOST_MUTABLE` | New versions must preserve v0.1 receipts and boundaries. |
| State Monitor v0.1 | production verified | `HOST_MUTABLE` | New invariants require a new version or explicit extension contract. |
| Audit V2 | active host-side audit path | `HOST_MUTABLE` | May add fields/versioned contracts; must never substitute latest state for historical execution input. |
| CFC Integration Layer | v0.4 RC | `RELEASE_CANDIDATE` | May change only under its RC gates. External usability remains an open evidence class. |
| Information Passport | pre-v1 integration track | `EXPERIMENTAL` / `HOST_MUTABLE` | May evolve until a versioned portable contract is frozen. |

## External-evidence artifacts

The following are not controller baselines and must not be used to rewrite frozen behavior:

- external developer usability results;
- independent replication results;
- controlled-study results;
- methods review decisions;
- domain pilot outcomes;
- commercial pilot outcomes.

Registry class:

`EXTERNAL_EVIDENCE_ONLY`

Each evidence class keeps its own receipt and claim ceiling.

## Forbidden mutations

Control Stack development must not:

1. edit frozen CFC Anchor `0.2.90rc1`;
2. edit Operator Wrapper v1.23 bytes;
3. overwrite historical release/package bytes;
4. rescore frozen historical benchmark results after reveal;
5. convert a historical FAIL/HOLD/STOP into PASS/CONTINUE by changing criteria after observation;
6. backfill a missing historical binding as though it had existed at execution time;
7. treat a hash as evidence of truth rather than byte identity;
8. let an adapter manufacture evidence, authority, independence, applicability or scope that upstream did not establish;
9. let a newer host module reinterpret a historical frozen receipt.

## Versioning rule

Any required behavior change must create a new explicit artifact identity, for example:

- `state-integrity 0.1 -> 0.2`;
- `evidence-layer 0.1 -> 0.2`;
- `control-stack-schema 0.1 -> 0.2`;
- `cfc-core-adapter 0.1 -> 0.2`.

Historical versions and receipts remain available.

## Development gate

Before a new Control Stack component is merged, its tests must demonstrate that no frozen artifact was modified or semantically reinterpreted.

If frozen identity cannot be established, the correct state is:

`HOLD / IDENTITY_NOT_ESTABLISHED`

not an inferred PASS.
