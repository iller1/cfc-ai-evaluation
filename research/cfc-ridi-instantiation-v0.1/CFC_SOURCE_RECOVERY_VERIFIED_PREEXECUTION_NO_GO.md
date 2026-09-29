# CFC ↔ RIDI RAG-nq-test1035 — source recovery verification and pre-execution decision

**Status:** SOURCE RECOVERY VERIFIED / CFC PRIVATE EXECUTABLE INPUT FREEZE NOT COMPLETE / PRE-EXECUTION NO-GO (MAPPING_NOT_EVALUABLE) / NO SUBSTANTIVE EXECUTION

## Original source recovered — independent CFC verification

RIDI recovery commit: `a198f07969b47cd25b812ba1a79f516f5e1c679a`.

Commit-pinned file: `collaboration/cfc-ridi/source-recovery-v0.1/contexts_800.jsonl`.

Public Git blob: `e7c031dc4697b08052a35d8b676bb8203c145714`.

The CFC side independently fetched the full Git blob through its connected GitHub access, reproduced the source's exact UTF-8 byte stream without JSON reserialization/normalization, and computed its SHA-256 using an independently validated hashing implementation:

- byte size: **25266491**;
- SHA-256: `1485c0ad114673d297c580080d11086d3ace8827f9b586b15ad3928c7d0b21a1`;
- exact SHA-256 and size match the original frozen source declaration: **PASS**;
- 1600 LF-terminated original context records, including both selected qid A/B records;
- selected A/B query identity, question, source registration, prompt digest and source passage identities match the already frozen neutral handoff without disclosing the I1-restricted fields.

Prior existence is additionally evidenced by the historical RIDI execution check (`8ff699b63d21096e0d585befdefcdb7a94b93329`, Actions job `107430864294`, 2026-09-23) and recovery action (`109621892044`). This verified recovery resolves the former exact-source-availability HOLD. It does not independently certify other upstream archives or create new authority records.

## Separate frozen CFC mapping/execution gate

Frozen M1/A1/I1 remain unchanged:

- M1 SHA-256: `7adc4229277280acf9f48528a74ace7df9ba28ac1295e30ced318a7c1a3ee858`;
- A1 SHA-256: `86f8b73bbb7e6f59aea95f2f388d15b78c3cda2d9ffc5190336b3e5a4ca64be9`;
- I1 SHA-256: `2f3a86e6e9e4b32633813bc2bd82dd2e04f55d7a643ca32780a78b997c01ae4b`.

CFC Anchor identity: `cfc-anchor 0.2.90rc1`; original wheel SHA-256 `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`; engine SHA-256 `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`. These identify the existing controller **only**, not a completed authorized experiment-specific runner/configuration freeze.

After the source-recovery PASS, the **separate** private M1/A1 mechanical executable-input assessment remains **MAPPING_NOT_EVALUABLE under the currently available frozen v0.1 execution path**. No positive executable freeze is claimed. The exact private mapping assessment remains CFC-side only under I1. This is not a CFC claim state, gate value or substantive output and does not establish that the general controller is incapable of a future faithfully specified adapter.

Therefore the requested mapped A/B input SHA-256/byte sizes, mapping and authority manifest SHA-256/byte sizes, and a valid substantive runner/configuration invocation identity are **NOT SUPPLIED AS COMPLETED FREEZE IDENTITIES**. Reporting an arbitrary hash of partial or synthetic placeholders would misleadingly imply a valid execution gate.

## Frozen stop boundary

- Selected case remains `RAG-nq-test1035`; no reselection, no mapper/policy/threshold amendment.
- No synthetic authority or post-selection authority assertion has been promoted into the substantive record.
- No substantive CFC execution; no RIDI raw computed result or output inspected.
- No CFC mapped inputs, authority-manifest contents, gates/reasons, raw outputs or interpretations are disclosed.
- No CFC or RIDI substantive execution is authorized by this record.
- This pre-execution no-go is **not** a derived CFC_PAIR_NOT_EVALUABLE substantive result from a run that never occurred.

The next allowable decision is bilateral discussion of a **versioned protocol/annex reset**, including review/freeze of a faithful nonfixture substantive mapping/runner path before any new substantive selection, unless an already-frozen approved compliant implementation can be independently identified and verified. Do not quietly patch v0.1 or continue executing after a failed gate.

**Evidence before execution.**
