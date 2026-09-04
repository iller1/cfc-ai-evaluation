# CFC Demonstrator RC1 Reconciliation Status

## Current status

`RC_BLOCKED_FOR_REPOSITORY_RECONCILIATION`

Final v1.0 promotion is not authorized yet.

## Confirmed facts

- Historical tag `cfc-demonstrator-v1.0-rc1` is preserved unchanged.
- The published RC1 release asset is `CFC_DEMONSTRATOR_v1.0-rc1.zip`.
- Release asset digest: `sha256:ba52b52fac78b7a1753fdd5a79d43f0d63b6604daac3701bbe44b96cd5fcb394`.
- The RC1 release record states:
  - 10 executable representative cases;
  - 107 manifest files verified;
  - preset replay 10/10;
  - custom regression PASS;
  - reviewer A/B PASS.
- Frozen execution engine: CFC Anchor `0.2.90rc1`.
- Frozen wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`.
- Operator Wrapper v1.23 remains byte-for-byte frozen and separate.
- `demo_config.json` on `main` references CASE_01 through CASE_10.
- The checked-in `demonstrator/cases/` tree on `main` currently contains CASE_01 through CASE_08 only.
- The historical RC1 tag also contains CASE_01 through CASE_08 only in its repository tree.

## CASE_09 / CASE_10 integrity anchors

The existing demonstrator manifest preserves exact expected SHA-256 values for the missing release files.

### CASE_09_INACTIVE_UNBOUND_RESOLUTION

- `README.md` — `f57523a658f0e3c5baa61216a4aea2ed439570ce67776a7c92e2f88965f059b5`
- `SHA256SUMS.txt` — `70d0713f8983654662ba3637268d0dc3aaea6369ab397ed5bc2e89f614ed175f`
- `VALIDATION.json` — `f0d72c8334f12d4415b4e4377ec5915d6d3c69b0b7ee91e8dc77a9ff3a761e4a`
- `case.json` — `c9dfe98fbc84e298f6f7f7e894a8601b737a425f2c81027d386ff8378544ea78`
- `execution_1.json` / `execution_2.json` / `execution_3.json` / `reference_execution.json` — `543f831aa6214f35a1e08f6e6af111c82ac52bbfcfa59d7e0d37b3c0978984c1`
- `run_case.py` — `3c1262814eae0738f31771328d87ec2aac1e9c792de80456208c1c57ad576748`

### CASE_10_INCOMPLETE_REQUIRED_CHECKS

- `README.md` — `25d109d3ea6143572bca74c18611c72710aad603baa9aa2236db1563b40ae71a`
- `SHA256SUMS.txt` — `d999031b425e80fa94735267a5020f02206e207d73c491aeba1b7220be57a7cf`
- `VALIDATION.json` — `2f676b6322450536d022b8a2da09af055b518fdc3fcc70bfb9f491fe1c321779`
- `case.json` — `7be5714a4ad253b7b3c65ee6b066e26b4b515ce7b8c53c0e9c2dfddd28335bfc`
- `execution_1.json` / `execution_2.json` / `execution_3.json` / `reference_execution.json` — `8c83275544091d39d45ae44216db4bd4d4646f495f42a74dca1ffbadeebd1800`
- `run_case.py` — `9aad2b0a3f44178d8b04d29ad2acdfdaac1d76f97f720f4cd6fc6eaa1a75bf48`

These values are verification anchors only. They are not substitutes for the missing file bytes.

## Interpretation

The discrepancy is between the repository source tree and the published release asset. It is a provenance/reconciliation defect in the demonstrator packaging workflow, not a demonstrated failure of the frozen controller logic.

CASE_09 and CASE_10 must not be recreated from memory, summaries, or inferred behavior. Their exact release bytes must be recovered from the preserved RC1 release asset or another byte-identical preserved source before insertion into the final candidate tree.

## Already corrected on main

- `PROJECT_STATUS.md` updated to the current external-validation / demonstrator-closure / controlled-study-preparation stage.
- `demonstrator/CLAIM_BOUNDARY.md` corrected and made explicitly conditional on a reconciled 10-case source/release state.
- `examples/` normalized so examples 01, 02, and 03 live at one level.
- accidental nested `examples/examples/...` duplicates removed.
- repository README files now disclose the source/release mismatch explicitly.

## Remaining finalization gate

Before final v1.0 promotion:

1. Recover exact CASE_09 and CASE_10 release bytes.
2. Verify every recovered file against the integrity anchors above.
3. Restore them into one reconciled source tree.
4. Confirm every `demo_config.json` `reference_file` exists.
5. Regenerate `SHA256SUMS.txt` from the exact final candidate bytes.
6. Verify the frozen wheel identity.
7. Run complete manifest verification.
8. Run preset replay and require 10/10 PASS.
9. Run custom regression and require PASS.
10. Run reviewer A/B verification and require PASS.
11. Audit public links and claim language.
12. Only then create/promote CFC Demonstrator v1.0.

Until all items pass, the historical RC1 remains evidence and the final release remains blocked.
