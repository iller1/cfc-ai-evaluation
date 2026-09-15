# CFC Attestation Lifecycle E2E Results v0.1

- Total: **23**
- PASS: **23**
- FAIL: **0**
- Normal-chain false ALLOW: **0**
- Anchor called for: **ATL-018, ATL-019**
- Frozen wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- Frozen engine SHA-256: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- Manifest verified: **108 files**

| Test | Expected guard | Actual guard | Anchor | Result |
|---|---|---|---|---|
| ATL-001 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-002 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-003 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-004 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-005 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-006 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-007 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-008 | UNRESOLVED | UNRESOLVED | SKIPPED_BY_GUARD | PASS |
| ATL-009 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-010 | UNRESOLVED | UNRESOLVED | SKIPPED_BY_GUARD | PASS |
| ATL-011 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-012 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-013 | UNRESOLVED | UNRESOLVED | SKIPPED_BY_GUARD | PASS |
| ATL-014 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-015 | UNRESOLVED | UNRESOLVED | SKIPPED_BY_GUARD | PASS |
| ATL-016 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-017 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-018 | ELIGIBLE_FOR_ANCHOR | ELIGIBLE_FOR_ANCHOR | ALLOW | PASS |
| ATL-019 | ELIGIBLE_FOR_ANCHOR | ELIGIBLE_FOR_ANCHOR | ALLOW | PASS |
| ATL-020 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-021 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-022 | STOP | STOP | SKIPPED_BY_GUARD | PASS |
| ATL-023 | STOP | STOP | SKIPPED_BY_GUARD | PASS |

## Interpretation

`ELIGIBLE_FOR_ANCHOR` was never treated as `ALLOW` by the host guard. Anchor was invoked only after lifecycle eligibility passed.

A zero false-ALLOW count in this E2E suite demonstrates the behavior of this external integration profile under the declared fixtures. It does not retroactively establish that frozen Anchor itself contains lifecycle enforcement for attestations.
