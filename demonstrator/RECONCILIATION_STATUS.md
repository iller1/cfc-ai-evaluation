# CFC Demonstrator reconciliation status

## Final status

`RECONCILIATION_COMPLETE_FINAL_VALIDATION_PASS`

The historical tag `cfc-demonstrator-v1.0-rc1` remains preserved unchanged.

## RC1 release identity

- asset: `CFC_DEMONSTRATOR_v1.0-rc1.zip`
- size: `424046` bytes
- SHA-256: `ba52b52fac78b7a1753fdd5a79d43f0d63b6604daac3701bbe44b96cd5fcb394`

The exact CASE_09 and CASE_10 bytes were recovered from that asset. Every recovered file matched the preserved per-file SHA-256 anchors before restoration to the repository.

## Restored source provenance

Exact CASE_09 and CASE_10 bytes were restored to `main` in commit:

`2fc0bf2758db0328ed0edf6a97bca72214704101`

The restoration changed repository provenance only; it did not modify the frozen CFC Anchor or Operator Wrapper.

## Frozen identities

- CFC Anchor version: `0.2.90rc1`
- CFC Anchor wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- CFC Anchor engine SHA-256: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- Operator Wrapper version: `v1.23`
- Operator Wrapper SHA-256: `95277663c445509af0820c3abdddaa295dfaaf93dd077ce32897b185b80957d8`

## Final validation gate

Final v1.0 promotion is permitted only when the exact packaged candidate passes:

1. fresh SHA-256 manifest verification;
2. frozen wheel identity verification;
3. 10/10 preset replay;
4. custom regression PASS;
5. reviewer A/B PASS;
6. claim-boundary and public-link audit.

This file is part of the final candidate manifest; therefore any modification requires manifest regeneration and complete revalidation.
