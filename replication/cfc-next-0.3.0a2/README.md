# CFC-next 0.3.0a2 replication reference

This directory provides a compact reproduction entry point for the separately
frozen CFC-next 0.3.0a2 baseline.

The canonical frozen Git ref is:

`frozen/cfc-next-0.3.0a2`

Freeze merge commit:

`568282c1f66af9f1f2fad8cf2b04b08226b9aea6`

## What is frozen

The frozen baseline is the exact 0.3.0a2 candidate/evidence chain pinned by:

`research/cfc_next_0_3_0a2_freeze_manifest.json`

The candidate source SHA-256 is:

`dc8ae4f2d51296d68ecf5e75ac861faf1f50f062e1761e0814ce157f08a588a7`

The underlying historical frozen Anchor remains CFC Anchor 0.2.90rc1 with
wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

## Minimal reproduction

Check out the frozen ref and use Python 3.11:

```bash
git checkout frozen/cfc-next-0.3.0a2
python -m research.review_cfc_next_0_3_0a2_acceptance
python -m research.review_cfc_next_0_3_0a2_promotion_readiness
python -m research.review_cfc_next_0_3_0a2_state_isolation
python -m research.review_cfc_next_0_3_0a2_freeze_review
```

Expected high-level results:

- acceptance: 14/14 positive fixtures;
- negative controls: 12/12 fail-closed;
- unexpected BOUND negative paths: 0;
- promotion-readiness: all gates true;
- state isolation: 14/14 tested blocker families show no candidate
  authorization visible to ordinary frozen evaluation;
- pinned freeze manifest: verified.

## What 0.3.0a2 changes

Relative to the accepted experimental 0.3.0a1 candidate, 0.3.0a2 preserves
Repair A and Repair B while removing the import-time monkeypatch of
`cfc_anchor._engine`.

The candidate-specific install lifecycle invokes its Repair-A registration path
directly. The ordinary frozen Controller keeps the original frozen engine
registration function.

## Boundaries

This package does not claim that the underlying global frozen registries are
designed for arbitrary same-interpreter multi-threaded stateful writes.

The tested concurrency claim is limited to independent fresh processes.

Shared registry objects are observable, but the full 14-case state-isolation
review showed that candidate-installed BOUND accounting did not authorize an
ordinary frozen Controller evaluation in the tested same-process contexts.

No historical frozen result was rescored.
