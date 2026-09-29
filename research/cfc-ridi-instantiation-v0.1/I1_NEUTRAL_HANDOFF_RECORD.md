# CFC ↔ RIDI selected-case v0.1 — I1-safe neutral exact-line handoff

**Record date:** 2026-09-29  
**Selected case:** `RAG-nq-test1035`  
**Status:** FOUR NEUTRAL RECORD HASHES PASS / CFC PUBLIC NEUTRAL HANDOFF COMMITTED / RIDI INDEPENDENT RECEIPT PENDING / NO SUBSTANTIVE CFC OR RIDI EXECUTION

## Frozen selection and transport boundaries

- RIDI selected-case record: `adeebnoor/ridi@4592e0b5de1cd34a6db8f7219512dd1d535f11a7`.
- The 800-case deterministic selection was independently reproduced on the CFC side. This handoff does not select again.
- Frozen eligible-pool SHA-256: `ebb7e660199687650a5c03888839401cc6f88f5b3fe6a55a77649bb855a43ade`.
- Original reviewed source transport: `CFC_RIDI_CANDIDATE_REGISTRY_INPUT_v0.1.zip`, 435772 bytes, SHA-256 `2b96ee5319cb93bce9b752fb4c6c3353c0e0463d8cd11e79f0dd682423093b00`.
- Original transport member `source_specimens_1600.jsonl` SHA-256: `a612fd38f0a502fd082f1955e4c1679f3c2a6bc91a9df44ca12c120dbf56f1f1`.
- Original transport member `offline_endpoints_1600.jsonl` SHA-256: `49441ff1e495f645cc0ae7d2117a4c9ff7c6be4ce622e9c83b9bc7bd78f5319e`.

## Frozen extractor identity

The extractor is copied byte-for-byte from RIDI commit `338ac387459d64a466c1df84256f476d92ca4a09`:

`collaboration/cfc-ridi/instantiation-v0.1/tools/extract_selected_specimen.py`

Original Git blob, reproduced from the locally executed exact bytes: `8b506b2d540923e036b6a2c222948e4b8cc3bd6d` (3035 bytes). It read the original JSONL input lines as bytes, and accepted only uniquely present selected A/B rows matching their frozen full-line SHA-256, including terminal LF.

## Exact selected neutral lines

| Exact archive member | Original source line | Byte count, including LF | Verified SHA-256 |
| --- | ---: | ---: | --- |
| `source_A.jsonl` | 855 | 994 | `60e19ea94ff13ded74e6ca19d6063909d374951f86218a9e3e68833b46126734` |
| `source_B.jsonl` | 856 | 993 | `018f1de8876594e57a383b69a1fcd605e811cf062695cc2ab947c737a697e308` |
| `endpoint_A.jsonl` | 855 | 382 | `e03c1c6433cd197f780537a90d1541744b314cf8eb196ca426f7dc4a41779c67` |
| `endpoint_B.jsonl` | 856 | 379 | `e66408834f040464bb8146e4ed814a26f15bb871519db4194c7a764b4e8580c5` |

Manifest `EXTRACTION_MANIFEST.json` SHA-256: `dd570c50f2746512f90fcb407fbc403cdc17f2afae677c2e1ab740e9f65cf3a7`.

Local extraction status: **PASS (4/4)**; no reserialization, normalization, line-ending conversion, content repair, case substitution or outcome-based reselection. The original upstream preregistration and source archives beyond this previously reviewed transport have not been independently verified on the CFC side; the earlier provenance limitation remains.

## Published I1-safe handoff

Exact archive path:

`research/cfc-ridi-instantiation-v0.1/CFC_RIDI_RAG-nq-test1035_I1_NEUTRAL_HANDOFF_v0.1.zip`

Publication commit: `6930975339820dc8344a55ae1cb46f6121791804`  
ZIP Git blob: `ed40be0fb1fb237ae16320bf23842565f248de0f`  
ZIP size: **5271 bytes**  
ZIP SHA-256: `f6845736496c51d5407ddfe46481a07a8d7ee43eb4735e3c23aee934607b3b56`

Archive members are exactly the four named neutral JSONL lines, `EXTRACTION_MANIFEST.json`, `EXTRACTION_LOG.txt`, the exact RIDI extractor `extract_selected_specimen.py`, and `TOOL_IDENTITY.txt`. ZIP integrity and extracted member equality were separately checked after packaging.

## I1 boundary / next gate

This public handoff contains **no CFC mapped per-arm input, CFC authority manifest, CFC gates/reasons, CFC results or classifications**. Those must not be disclosed to RIDI before the frozen raw-bundle commitment stage. This record does not assert private CFC M1/A1/I1 instantiation is complete.

RIDI must independently download and verify the exact four selected-line SHA-256 hashes, extraction manifest, ZIP identity and provenance before freezing its RIDI-permitted input. CFC must separately create/freeze private mapped per-arm inputs and validate M1/A1/I1 without exposing prohibited contents. Freeze both sides' hashes/versions and validation status before **any** substantive execution.

**Evidence before execution.**
