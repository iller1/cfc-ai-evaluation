# Frozen Baselines Manifest — CFC Control Stack

Version: FROZEN_BASELINES_MANIFEST_v0.1

Date: 2026-10-06

Status: NORMATIVE DEVELOPMENT BOUNDARY

## Purpose

This manifest defines which historical CFC artifacts are frozen, which host/application artifacts may evolve, and which evidence artifacts are append-only.

## Classification

- FROZEN — byte identity or historical semantics are not changed in this development line.
- RELEASED — historical release remains immutable; later versions require a new identity.
- HOST-MUTABLE — application and integration code may evolve under explicit versioning and regression gates.
- EVIDENCE-APPEND-ONLY — new receipts may be added; existing receipts are not rewritten.
- EXTERNAL-EVIDENCE-ONLY — status can change only from new external evidence, not internal reinterpretation.

## Registry

| Artifact | Identity / reference | Class | Rule |
| --- | --- | --- | --- |
| Operator Wrapper | v1.23 | FROZEN | Byte-for-byte unchanged. |
| Operator Wrapper SHA-256 | 95277663c445509af0820c3abdddaa295dfaaf93dd077ce32897b185b80957d8 | FROZEN | Immutable hash anchor. |
| CFC Anchor | 0.2.90rc1 | FROZEN | Executable controller semantics are unchanged in this line. |
| Formal State & Closure Specification | v1.0 | FROZEN | Historical descriptive baseline remains fixed. |
| External Replication Package | v1.1 | RELEASED | Replacement requires a new version and identity. |
| Four-Track benchmark | historical frozen benchmark | FROZEN | No post-hoc rescoring or criteria repair. |
| Restricted Phase-1 10K campaign | completed historical campaign | FROZEN | Results remain historical evidence. |
| CFC Demonstrator | v1.0 | RELEASED | Presentation/replay baseline only. |
| Demonstrator v1.0 release asset SHA-256 | d4c46d435994a291cf09cc9ca880be06bd4271c83e2875f9fbf3f887bd08ae28 | FROZEN | Immutable release identity. |
| CFC Integration Layer | v0.4 RC | HOST-MUTABLE | May be superseded only by an explicit new version. |
| Integration Layer v0.4 RC SHA-256 | 7770a8e466045415b776c849bbd654da875f8f3d863ab94ff319bfef4dbf8ab4 | EVIDENCE-APPEND-ONLY | Existing RC package identity retained. |
| Durable snapshot→run production receipt | PRODUCTION_SNAPSHOT_RUN_BINDING_VERIFICATION_2026-10-04.md | EVIDENCE-APPEND-ONLY | Do not rewrite. |
| Evidence Drift production receipt | PRODUCTION_EVIDENCE_DRIFT_VERIFICATION_2026-10-05.md | EVIDENCE-APPEND-ONLY | Do not rewrite. |
| State Monitor production receipt | PRODUCTION_STATE_MONITOR_VERIFICATION_2026-10-06.md | EVIDENCE-APPEND-ONLY | Do not rewrite. |
| Integration Layer unfamiliar-user usability gates | first decision <=15 min; mapping <=30 min | EXTERNAL-EVIDENCE-ONLY | Only unfamiliar external-user evidence can close them. |
| Controlled study activation | R271-R273 readiness line | EXTERNAL-EVIDENCE-ONLY | Methods review and preregistration gates before confirmatory collection. |

## Frozen semantic invariants

1. VERIFIED or factual validity does not imply authority to propagate.
2. Technical possibility does not imply permission.
3. Hash identity does not imply truth.
4. Historical PASS / FAIL / HOLD / STOP semantics are not retroactively repaired.
5. Frozen benchmark results are not rescored after reveal to preserve preferred conclusions.
6. Missing upstream information is not silently manufactured downstream.
7. Internal engineering evidence is not relabeled as independent external validation.
8. A new module does not become part of frozen CFC merely because it integrates with it.

## Allowed development surface

The following may evolve under explicit versions and tests:

- host application;
- HAWM persistence and presentation;
- State Integrity;
- Evidence & Provenance;
- Continuity & Transition;
- CFC adapter;
- Execution Gate;
- Audit / Information Passport;
- domain adapters;
- UI controls;
- integration packages;
- synthetic pilot workflows.

Every change must use a new commit or version identity, preserve historical receipts, pass regression gates and state its claim ceiling.

## Forbidden mutations

- modifying frozen Anchor behavior to make a new module pass;
- changing Operator Wrapper bytes;
- rewriting a historical receipt after observing a new result;
- rescoring a frozen benchmark after reveal;
- replacing an old artifact under the same frozen identity;
- inferring missing authority from free text;
- allowing an adapter to generate evidence or authority absent upstream;
- treating latest state as historical execution input when exact persisted binding exists;
- removing historical FAIL / HOLD outcomes from evidence history.

## Reopen triggers

A frozen line is reopened only if a concrete requirement comes from one of:

- external reproducer demonstrates a specific defect;
- independent pilot exposes a bounded integration failure;
- material contract/specification contradiction;
- real customer workflow requires a change that cannot be implemented host-side;
- frozen benchmark failure under pre-existing criteria reveals a core defect.

Reopening requires a new version line and does not overwrite the previous frozen baseline.

## Current gate

This manifest plus CONTROL_STACK_ARCHITECTURE_v0.1.md complete the freeze-registry / architecture checkpoint only after repository CI is green and both files are merged to main.

Next checkpoint:

CONTROL_STACK_SCHEMA_v0.1.json
