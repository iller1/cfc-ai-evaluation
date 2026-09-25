# CFC-next 0.3.0a1 process-isolation promotion review

## Purpose

Test whether the accepted experimental candidate can coexist safely with the
frozen CFC Anchor 0.2.90rc1 inside one Python interpreter.

This review does not modify the candidate or the frozen wheel.

## Promotion requirements

A promotable candidate must not make a frozen Controller instance observe
candidate admission semantics merely because the candidate module was imported.

The review therefore checks:

1. frozen engine registration function before candidate import;
2. engine registration function immediately after candidate import;
3. a FrozenController class loaded before candidate import;
4. candidate patch lifecycle after an explicit restore attempt;
5. fresh-process isolation control before and after the mutation probe.

## Interpretation

A process-local mutation is not the same as modifying the frozen wheel on disk.
However, promotion requires a stronger boundary than file immutability: frozen
and candidate semantics must not silently change each other inside a shared
runtime.

If import-time mutation contaminates the frozen Controller, the candidate
remains an accepted experimental candidate but is not ready to become a frozen
or release baseline until that isolation problem is repaired.

## Observed result

The CI probe reproduces three same-process blockers:

1. **IMPORT_TIME_GLOBAL_ENGINE_MUTATION**
   - importing `cfc_next_candidate` replaces
     `cfc_anchor._engine.register_decision_generic_dependency_accounting`;
   - the function object changes immediately at module import time.

2. **FROZEN_CONTROLLER_SAME_PROCESS_CONTAMINATION**
   - a `cfc_anchor.Controller` class loaded before the candidate import still
     resolves its install path through the shared `cfc_anchor._engine` module;
   - after candidate import that frozen Controller can therefore observe the
     candidate registration function.

3. **PATCH_LIFECYCLE_STATE_DIVERGENCE**
   - the candidate tracks patch installation with a module-level boolean;
   - after the engine function is explicitly restored, calling the candidate
     installer again does not re-install the candidate function because the
     flag still says the patch is installed.

The fresh-process control passes: a new Python subprocess starts with the same
frozen registration-function source hash before and after the candidate mutation
probe, and the pinned wheel SHA remains unchanged.

## Promotion classification

**NOT_PROMOTION_READY_PROCESS_ISOLATION_BLOCKER**

This is a runtime-isolation finding, not a failure of the 14-positive /
12-negative decision-accounting acceptance contract.

CFC-next 0.3.0a1 therefore remains:

**ACCEPTED_EXPERIMENTAL_CANDIDATE**

but must not be promoted to a frozen or release baseline in its current
import-time monkeypatch form.

The next candidate should remove global import-time mutation rather than weaken
the acceptance or frozen-regression gates.

