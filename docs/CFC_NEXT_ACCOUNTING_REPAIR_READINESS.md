# CFC-next decision-accounting repair readiness

## Status

The decision-accounting research chain is now complete enough to hand to a
separately versioned CFC-next candidate implementation.

This document does **not** authorize modification of frozen CFC Anchor
0.2.90rc1 and does not rescore any historical result.

## Evidence chain

The repair proposal is grounded in the following linked results:

1. the stale mixed-endpoint closure path was localized to
   `decision_support_closure_valid`;
2. exact internal accounting proved the schema-valid mixed obligation is
   core-bindable;
3. frozen policy was shown to require selected/excluded relation preservation;
4. COMMON_MODE / LINEAGE were shown to be engine-emitted but rejected by the
   accounting schema;
5. all 14 minimal blockers were classified:
   - 3 engine-emitted/accounting-schema incompatibilities;
   - 11 public selected/excluded reachability inconsistencies that are
     core-bindable;
6. the repair surface was localized to two admission rules;
7. the positive acceptance manifest freezes all 14 target cases;
8. the negative frozen-reference baseline executes all 12 negative classes:
   - 12/12 fail closed;
   - 0 unexpected BOUND paths;
   - 3 are currently masked by the legacy selected-support-only guard, with
     separate expanded-map controls proving downstream bind remains fail-closed.

## Proposed repairs

### Repair A — SHARED_GENERIC_NODE_VALIDATOR

Make internal and public generic-accounting validation use the same structural
domain as the engine's generic dependency node model.

The repair must preserve:

- exact 3-tuple identity;
- nonblank node type and identifier;
- source-semantic exclusion;
- legal blank middle dimension for canonical LINEAGE / COMMON_MODE nodes;
- typed dependency ontology constraints;
- exact hashing.

### Repair B — EXACT_REQUIRED_OBLIGATION_ENDPOINT_ADMISSION

Replace the blanket public rule requiring every endpoint to be selected support
with admission of a non-selected endpoint **only** when the exact node and exact
endpoint set are freshly derived as a `decision_level_required` obligation for
the same exact decision context.

The engine-selected support map must not be expanded to make the draft pass.

## Security boundary that remains unchanged

The research does not support weakening:

- decision-level obligation derivation;
- exact selected-support-map binding;
- exact node and endpoint matching;
- retrieval scope / snapshot binding;
- claim / requirements binding;
- generic-universe hashes;
- provenance / ontology / equivalence commitments;
- external attestation verification;
- BOUND-state requirement;
- decision-support closure certificate validation;
- persistence commitments.

The 12 negative controls now provide regression coverage for these boundaries.

## Implementation gate

A future CFC-next candidate should be considered ready for review only when the
existing acceptance manifest is reused without weakening:

- **14/14 positive fixtures** must reach the target closure state through the
  supported public lifecycle;
- **12/12 negative controls** must reject or remain non-authorizing;
- the three currently masked negatives must be tested through the newly
  reachable selected/excluded path, not merely rejected by the old blanket
  guard;
- frozen CFC Anchor 0.2.90rc1 must remain unchanged;
- historical results must not be rescored.

The current status remains **DESIGN_SPEC_ONLY / NOT_IMPLEMENTED**.
