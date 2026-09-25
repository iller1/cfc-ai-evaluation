# CFC-next 0.3.0a2 accounting lifecycle review

## Scope

This review does not modify the frozen CFC-next 0.3.0a2 baseline.

It asks one narrow question: after a valid decision-generic-dependency
accounting row has been installed, finalized, and shown to permit closure in
its original decision context, can that authorization incorrectly survive a
material context mutation?

The first representative phase covered three blocker families and passed 15/15
cases. The review is now expanded to all 14 blocker families from the frozen
decision-accounting taxonomy.

For every blocker family the harness first proves an exact authorized baseline,
then tests:

1. exact replay control;
2. as-of date shift;
3. claim-id change;
4. retrieval-scope change;
5. support requirement change.

That is a 14 x 5 = 70-case lifecycle matrix. Each case runs in a fresh
subprocess.

## Two lifecycle paths

The harness records two distinct behaviors:

- **direct evaluate after mutation** — checks whether previously finalized
  accounting state remains visible when a caller evaluates a changed context
  without re-running the prepare/finalize lifecycle;
- **re-finalize then evaluate** — the stronger lifecycle check. A material
  context change must either fail closed during re-finalization or evaluate
  without stale authorization.

A direct-evaluate closure after mutation is reported as a boundary finding,
not automatically as a frozen-contract violation, because the public lifecycle
obligation to re-finalize every changed context must be established separately.

A closure that remains authorized after successful re-finalization of a
materially changed context is classified more strongly as stale accounting
authorization persistence.

## Claim boundary

A clean 70-case result supports only the tested mutation classes over the 14
known blocker families. It is not a claim of arbitrary lifecycle correctness,
thread safety, production readiness, or immunity to untested state mutations.

The frozen CFC-next 0.3.0a2 source and frozen CFC Anchor reference are not
modified and historical benchmark results are not rescored.
