# CFC-next 0.3.0a2 accounting lifecycle review

## Scope

This review does not modify the frozen CFC-next 0.3.0a2 baseline.

It asks one narrow question: after a valid decision-generic-dependency
accounting row has been installed, finalized, and shown to permit closure in
its original decision context, can that authorization incorrectly survive a
material context mutation?

The representative phase covers three blocker families:

- `root_origin_shared`
- `extractor_shared`
- `dependency:data_source`

For each family the harness first proves an exact authorized baseline, then
tests:

1. exact replay control;
2. as-of date shift;
3. claim-id change;
4. retrieval-scope change;
5. support requirement change.

Each case runs in a fresh subprocess.

## Two lifecycle paths

The harness records two distinct behaviors:

- **direct evaluate after mutation** — useful for identifying whether a caller
  can continue evaluating on previously finalized accounting state without
  re-running the prepare/finalize lifecycle;
- **re-finalize then evaluate** — the stronger lifecycle check. A material
  context change must either fail closed during re-finalization or evaluate
  without stale authorization.

A direct-evaluate closure after mutation is reported as a boundary finding,
not automatically as a frozen-contract violation, because the public lifecycle
obligation to re-finalize every changed context must be established separately.

A closure that remains authorized after successful re-finalization of a
materially changed context is classified more strongly as stale accounting
authorization persistence.

## Expansion rule

If the representative phase does not reveal a harness/design error, expand
the same mutation matrix to all 14 blocker families before drawing a general
0.3.0a2 lifecycle conclusion.
