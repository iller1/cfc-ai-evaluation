# CFC-next 0.3.0a2 state-isolation review

## Purpose

0.3.0a2 removes the import-time function monkeypatch found in 0.3.0a1.

Before any freeze decision, this review tests a deeper boundary:

> after 0.3.0a2 installs and binds an accounting authorization, can an ordinary
> frozen CFC Anchor 0.2.90rc1 Controller in the same Python interpreter observe
> that authorization through the shared runtime registries?

This is distinct from source-code isolation. A candidate can leave the frozen
engine function unchanged while still writing authorization state into data
structures consumed by frozen evaluation.

## Matrix

All 14 previously isolated minimal decision-accounting blockers are tested in
fresh subprocesses:

- root_origin_shared;
- origin_shared;
- extractor_shared;
- common_mode_group_shared;
- dependency:data_source;
- dependency:sensor_input;
- dependency:transform;
- dependency:model;
- dependency:extractor;
- dependency:cache;
- dependency:upstream_db;
- dependency:operator;
- dependency:preprocessing;
- dependency:runtime.

For each blocker:

1. candidate and frozen Controllers evaluate before candidate accounting;
2. candidate creates, verifies, installs and finalizes the exact required
   accounting;
3. candidate re-evaluates;
4. the same frozen Controller instance re-evaluates;
5. a newly created frozen Controller instance re-evaluates;
6. the shared SUPPORT_SELECTION_REGISTRY row is recorded.

No frozen wheel file is modified and no historical result is rescored.

## Freeze rule

If a candidate-installed authorization changes a frozen Controller evaluation
from STOP to closure in the same interpreter, code isolation alone is
insufficient for a frozen-baseline promotion.

That outcome should be classified as a shared-state authorization boundary and
should trigger a state-isolation repair, not a weakening of the acceptance
tests.

## Observed result

The full 14-case state-isolation matrix passes.

For every minimal blocker:

- candidate baseline remains STOP / VERIFIED before exact accounting;
- candidate reaches closure after its exact verified accounting is finalized;
- the candidate accounting row is present in the shared registry and BOUND;
- a frozen Controller instance created before candidate accounting remains
  closure false after candidate accounting;
- a newly created frozen Controller instance also remains closure false;
- candidate authorization visible to frozen evaluation is **false**.

The aggregate machine-readable result is:

- relations tested: **14**;
- candidate authorization visible to frozen relations: **[]**;
- shared registry state detected: **true**;
- promotion status: **STATE_ISOLATION_GATE_PASS**.

This demonstrates authorization isolation across the complete minimal blocker
taxonomy even though the underlying runtime registry object is shared.

## Freeze-readiness meaning

Together with the 0.3.0a2 promotion-readiness gate, the full matrix now shows:

- no import-time frozen-engine mutation;
- no operation-time frozen-engine mutation;
- no candidate authorization leakage into ordinary frozen evaluation across
  all 14 minimal Repair-A / Repair-B blocker families;
- unchanged frozen wheel and no historical rescore.

A separate explicit freeze/closure step is still required before 0.3.0a2 can be
treated as a frozen CFC-next baseline.

