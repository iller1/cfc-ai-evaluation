# CFC Demonstrator RC1 Reconciliation Status

## Current status

`RC_RECONCILED_PENDING_FINAL_PACKAGE_VALIDATION`

The original repository/source mismatch has been repaired on `main`. Final v1.0 promotion is still not authorized until a fresh final package manifest and full final-candidate verification pass.

## Confirmed facts

- Historical tag `cfc-demonstrator-v1.0-rc1` remains preserved unchanged.
- Published RC1 release asset: `CFC_DEMONSTRATOR_v1.0-rc1.zip`.
- RC1 asset size: `424046` bytes.
- RC1 asset SHA-256: `ba52b52fac78b7a1753fdd5a79d43f0d63b6604daac3701bbe44b96cd5fcb394`.
- Exact RC1 asset bytes were recovered and independently checked against the preserved release digest.
- CASE_09 and CASE_10 were extracted from that exact asset; every recovered file passed its preserved SHA-256 integrity anchor.
- The exact recovered bytes were restored to `main` in commit `2fc0bf2758db0328ed0edf6a97bca72214704101`.
- Post-write Git blob identities for all 18 restored CASE_09/CASE_10 files match the Git blob identities computed from the recovered RC1 bytes, confirming byte-for-byte repository restoration.
- `demo_config.json` references CASE_01 through CASE_10 and the corresponding CASE_09/CASE_10 `reference_execution.json` files now exist on `main`.
- Frozen execution engine remains CFC Anchor `0.2.90rc1`.
- Frozen wheel SHA-256 remains `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`.
- Operator Wrapper v1.23 remains byte-for-byte frozen and separate.

## Fresh recovery replay

The recovered RC1 asset was freshly extracted and `verify_release.py` was executed locally after recovery.

Result:

- status: `PASS`
- manifest files verified: `107`
- live preset replay: `10/10`
- custom regression: `PASS`
- reviewer A/B: `PASS`
- wheel SHA-256: exact expected frozen value
- engine SHA-256: exact expected frozen value
- Python used for the fresh replay: `3.13.5`
- pip required: `false`
- network required: `false`

This confirms the recovered historical RC1 bytes remain internally executable and reproducible. It does not by itself promote the current reconciled `main` tree to final v1.0 because current documentation differs from the historical release package and the final manifest must be regenerated from the exact final candidate bytes.

## Reconciliation defect disposition

The previously recorded discrepancy was a demonstrator packaging/source-provenance defect: CASE_09 and CASE_10 existed in the release asset but were absent from the repository source tree. It was not evidence of a frozen-controller logic failure.

That specific provenance defect is now **RESOLVED**.

## Remaining finalization gate

Before final v1.0 promotion:

1. Freeze the reconciled final candidate tree.
2. Build the final package from the exact reconciled source bytes.
3. Regenerate top-level `SHA256SUMS.txt` from the exact final candidate bytes; do not reuse the stale RC1/main manifest.
4. Verify the frozen wheel identity.
5. Run complete manifest verification on the final candidate package.
6. Run preset replay and require `10/10 PASS`.
7. Run custom regression and require `PASS`.
8. Run reviewer A/B verification and require `PASS`.
9. Audit public links and claim language against the bounded Proof-of-Concept / experimental-research status.
10. Only then create/promote CFC Demonstrator v1.0 and record the final tag, package SHA-256, and release URL.

Until these remaining items pass, the historical RC1 remains evidence and the final v1.0 release remains pending.
