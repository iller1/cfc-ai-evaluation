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

Two representative mechanisms are tested in fresh subprocesses:

- root_origin_shared — the Repair-A LINEAGE family;
- dependency:data_source — a schema-valid Repair-B family.

For each relation:

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
