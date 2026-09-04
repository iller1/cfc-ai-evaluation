# CFC Demonstrator RC1 Reconciliation Status

## Current status

`RC_BLOCKED_FOR_REPOSITORY_RECONCILIATION`

Final v1.0 promotion is not authorized yet.

## Confirmed facts

- Historical tag `cfc-demonstrator-v1.0-rc1` is preserved unchanged.
- The published RC1 release asset is `CFC_DEMONSTRATOR_v1.0-rc1.zip`.
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

## Interpretation

The discrepancy is between the repository source tree and the published release asset. It is a provenance/reconciliation defect in the demonstrator packaging workflow, not a demonstrated failure of the frozen controller logic.

CASE_09 and CASE_10 must not be recreated from memory, summaries, or inferred behavior. Their exact release bytes must be recovered from the preserved RC1 release asset or another byte-identical preserved source before insertion into the final candidate tree.

## Already corrected on main

- `PROJECT_STATUS.md` updated to the current external-validation / demonstrator-closure / controlled-study-preparation stage.
- `demonstrator/CLAIM_BOUNDARY.md` corrected from eight to ten configured synthetic cases and expanded to cover CASE_09/10 teaching boundaries.
- `examples/` normalized so examples 01, 02, and 03 live at one level.
- accidental nested `examples/examples/...` duplicates removed.
- repository README files now disclose the source/release mismatch explicitly.

## Remaining finalization gate

Before final v1.0 promotion:

1. Recover exact CASE_09 and CASE_10 release bytes.
2. Restore them into one reconciled source tree.
3. Confirm every `demo_config.json` `reference_file` exists.
4. Regenerate `SHA256SUMS.txt` from the exact final candidate bytes.
5. Verify the frozen wheel identity.
6. Run complete manifest verification.
7. Run preset replay and require 10/10 PASS.
8. Run custom regression and require PASS.
9. Run reviewer A/B verification and require PASS.
10. Audit public links and claim language.
11. Only then create/promote CFC Demonstrator v1.0.

Until all items pass, the historical RC1 remains evidence and the final release remains blocked.
