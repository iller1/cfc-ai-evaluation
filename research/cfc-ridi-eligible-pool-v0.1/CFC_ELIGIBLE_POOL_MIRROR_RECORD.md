# CFC ↔ RIDI Eligible Pool v0.1 — CFC-side exact-byte mirror record

**Record date:** 2026-09-29  
**CFC repository:** `iller1/cfc-ai-evaluation`  
**Branch:** `freeze/cfc-ridi-eligible-pool-v0.1`  
**Status:** CFC PUBLIC EXACT-BYTE POOL MIRROR COMMITTED / RIDI INDEPENDENT PUBLIC VERIFICATION PENDING / NO SEED / NO CASE SELECTION / NO SUBSTANTIVE EXECUTION

## Authority and sequence

This record follows the frozen Shared Case Protocol v0.1, frozen bilateral eligibility gate, construction of the complete 800-pair candidate registry, independent CFC-side reproduction, and RIDI-side pool freeze. It does not alter any earlier frozen artifact.

- Shared Case Protocol v0.1 SHA-256: `d6bc94e90be4ac01bd8ee60f32aa3045dd827f4f3e9e64a68b82191615138571`
- Frozen eligibility checker SHA-256: `96ca16e12e3f2fecb5a06998eb28476e250b2a0965f2b26713da298391958904`
- Candidate registry SHA-256: `09824e8fa0837cc852b34c984b3ad7156a7433a57d672f4124356f4806e2fccf`
- Reproduced eligibility audit SHA-256: `23e027e7228c3a09d13b238619ca87389f304f3fb281c37b386cca6a6defe826`
- Frozen eligible pool SHA-256: `ebb7e660199687650a5c03888839401cc6f88f5b3fe6a55a77649bb855a43ade`
- Checker result: 800 registrations / 800 ACCEPT / 0 REJECT.

## RIDI-side source freeze and receipt

The RIDI-side authoritative freeze record and SHA-256 manifest were copied without changes into this CFC mirror:

| CFC mirror path | Same RIDI original Git blob |
| --- | --- |
| `research/cfc-ridi-eligible-pool-v0.1/ELIGIBLE_POOL_FREEZE_RECORD.md` | `276155f4c7a03b25067b2d0bc3bd386f37402cfd` |
| `research/cfc-ridi-eligible-pool-v0.1/POOL_SHA256_FROZEN.txt` | `5c8b3643732638b3ad0d9ecb4baa973bfa936f04` |

RIDI freeze branch: `adeebnoor/ridi@freeze/cfc-ridi-eligible-pool-v0.1`.

RIDI subsequently recorded its independent pre-publication receipt check in `collaboration/cfc-ridi/eligible-pool-v0.1/CFC_PREPUBLICATION_POOL_RECEIPT_CHECK.md`, observing CFC's prior metadata-only branch at commit `a31e86cab8ee2c34f4e392fae370c3e2d8651313`. That earlier receipt is an independent *pre-publication* check, not a claim of post-publication bilateral verification.

## CFC exact-byte pool publication

The CFC-side independently reproduced and RIDI pre-publication-received `eligible_pool.tsv` was committed unchanged at:

`research/cfc-ridi-eligible-pool-v0.1/eligible_pool.tsv`

**Pool-only publication commit:** `1421782eb40319a643e82e570713754a939d80bd`  
**Public Git blob:** `e9f256466b3651e21893ec66fbc78828717875f4`  
**Bytes:** 654915  
**Encoding and line endings:** UTF-8 / LF, terminated by LF.  
**Line count:** 801, comprising one header and 800 data rows.  
**Unique case IDs / pair fingerprints:** 800 / 800.  
**Frozen content SHA-256:**

```text
ebb7e660199687650a5c03888839401cc6f88f5b3fe6a55a77649bb855a43ade  eligible_pool.tsv
```

CFC independently verified the original received file's SHA-256 and Git blob identity, then read the public file back at the pool-only publication commit and compared it byte-for-byte with the received file: **identical**. The public file's Git blob also equals the locally computed Git blob.

The original frozen manifest and RIDI freeze record remain unaltered. This separate CFC record is additive; its own final branch-head commit is necessarily later than the pool-only publication commit it identifies.

## Scope and upstream provenance boundary

The CFC independent review reconstructed the eligibility audit and pool under the unchanged checker and checked delivered derived specimen and endpoint bindings without outcome-based candidate filtering. It did **not** independently inspect the original upstream `contexts_800.jsonl`, `registered_generations_primary_800.jsonl`, or original preregistration artifact. Those provenance claims remain attributable to RIDI, not newly certified by the mirror.

This is an exact-byte pool identity freeze, **not** empirical validation, case selection or an evaluation outcome.

## Remaining bilateral step and stop condition

The CFC public pool is committed. The bilateral mirror remains **AWAITING RIDI POST-PUBLICATION VERIFICATION** until Adeeb independently retrieves and confirms the public TSV identity and this final CFC mirror record/commit.

Only after RIDI confirms that verification may the parties proceed to the frozen protocol's seed commit–reveal procedure. No seed was generated, committed or revealed here; no case was selected and neither controller underwent substantive execution.

**Evidence before selection.**
