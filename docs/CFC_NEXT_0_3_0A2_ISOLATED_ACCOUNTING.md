# CFC-next 0.3.0a2 isolated accounting candidate

## Purpose

0.3.0a2 is a separately versioned successor to the accepted experimental
0.3.0a1 candidate.

It exists for one reason: remove the process-isolation blocker found in
0.3.0a1 without weakening Repair A, Repair B, the 14-positive acceptance
matrix, the 12-negative fail-closed controls, or frozen-reference regression.

0.3.0a1 remains pinned and unchanged.

## Isolation repair

0.3.0a1 replaced
`cfc_anchor._engine.register_decision_generic_dependency_accounting` at module
import time.

0.3.0a2 does not replace that engine symbol.

Instead, the candidate subclass overrides only
`install_verified_decision_generic_dependency_accounting`. The override
preserves the frozen host-trust, attestation, verifier, idempotency, runtime
verification and metadata checks, but invokes the candidate Repair-A registry
function directly when a new exact accounting row must be created.

The frozen Controller continues to resolve the original frozen engine
registration function inside the same interpreter.

## Unchanged decision-accounting semantics

Repair A remains:

- exact three-field identity;
- nonblank node type and identifier;
- canonical blank dimension permitted for LINEAGE / COMMON_MODE;
- source-semantic exclusion;
- dependency ontology constraints;
- exact node hashing.

Repair B remains:

- non-selected endpoint admitted only for the exact fresh
  decision_level_required obligation;
- exact evaluated-snapshot membership;
- exact engine-selected support map;
- exact node and endpoint set;
- same decision context.

## Readiness matrix

0.3.0a2 must pass all of the following:

- unchanged 14/14 positive acceptance fixtures;
- unchanged 12/12 negative fail-closed controls;
- zero unexpected BOUND negative paths;
- no import-time frozen-engine mutation;
- no engine mutation after a successful candidate accounting lifecycle;
- no import-time patch-installer surface;
- two full acceptance runs produce identical JSON;
- four representative positive cases pass concurrently in separate fresh
  processes;
- frozen wheel hash remains pinned;
- full existing repository CI remains green.

Same-interpreter concurrent mutation of the frozen engine is no longer required
or used. This review does not claim that the underlying frozen global registries
are designed for arbitrary multi-threaded stateful writes; the concurrency
claim is intentionally limited to independent fresh processes.

## Promotion rule

0.3.0a2 may be called promotion-ready only if the machine-readable readiness
harness reports all gates true.

Passing this gate still does not silently rewrite 0.3.0a1 or the frozen
0.2.90rc1 history. Any freeze/promotion must be a later explicit step.
