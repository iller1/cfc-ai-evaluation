# CFC-next 0.3.0a2 freeze review

## Purpose

This is the explicit freeze-review stage for CFC-next 0.3.0a2.

It does not modify or rescore frozen CFC Anchor 0.2.90rc1 and it does not
rewrite the pinned 0.3.0a1 accepted experimental candidate.

## Required evidence

The freeze review re-executes and requires:

- 14/14 positive decision-accounting fixtures;
- 12/12 negative controls fail-closed;
- zero unexpected BOUND negative paths;
- deterministic full acceptance rerun;
- concurrent representative fresh-process positives;
- no import-time or operation-time frozen-engine mutation;
- 14/14 same-process state-isolation cases with no candidate authorization
  visible to frozen evaluation;
- pinned frozen wheel SHA-256;
- no historical rescore.

It also emits SHA-256 commitments for the 0.3.0a2 source and the complete
acceptance / readiness / state-isolation evidence chain.

## Freeze rule

The first run may only classify the candidate as
READY_FOR_PINNED_FREEZE_MANIFEST.

A later commit must pin the emitted commitments into a machine-readable freeze
manifest and make the freeze-review script verify those exact values. Only that
pinned, re-verified state can become the frozen CFC-next baseline.

## Pinned freeze manifest

The authoritative manifest is:

`research/cfc_next_0_3_0a2_freeze_manifest.json`

It pins:

- candidate source:
  `dc8ae4f2d51296d68ecf5e75ac861faf1f50f062e1761e0814ce157f08a588a7`
- acceptance harness:
  `683913e46bd9fe90100766c75f4cddbbcd0bf466b8068a5f1b0933eeaa9d42df`
- promotion-readiness harness:
  `7238dedcc3b53a9b1a2ae996796b0b85242cad503a9d4f561378e87a5db762cf`
- state-isolation harness:
  `3b4e39663736e7dfb74189d0d84c2bc05a4f6a4167ad5ccf34bb942be1b37c72`
- acceptance manifest:
  `31191438ea7ceffd8acdceb352c79f38f58900b5a4b3c991119e6d4c8e0ede60`
- Repair A/B specification:
  `275e261279e1861dd5b2233829b60d535a9f95b6fc57a763dd30d4d2f0f38f56`
- pinned 0.3.0a1 closure manifest:
  `83ea43a569924c1c880181c57bb235e8132d1db2ad7f51b1977f7a0f6395ec26`
- frozen 0.2.90rc1 wheel:
  `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

The final freeze-review gate recomputes every commitment and must match this
manifest exactly.

## Freeze semantics

The manifest uses `FROZEN_ON_MERGE`.

Therefore the branch is not the frozen baseline merely because the manifest
exists. Freeze becomes effective only after:

1. the pinned-manifest freeze-review gate passes;
2. all repository regression workflows pass on the exact final PR head;
3. the PR is merged without changing the pinned candidate/evidence chain.

After that merge, CFC-next 0.3.0a2 is the separately frozen CFC-next baseline.

CFC Anchor 0.2.90rc1 remains a distinct historical frozen reference and
CFC-next 0.3.0a1 remains a distinct pinned accepted experimental candidate.

