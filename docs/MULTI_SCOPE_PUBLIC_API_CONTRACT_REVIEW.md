# Multi-scope public API contract review

## Goal

Resolve the separate multi-retrieval-scope boundary observed during stale relation
snapshot-locality testing.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.

## Public contract findings

Read-only introspection of the frozen public/runtime API established that:

- `evaluate(..., retrieval_scope=...)` and `evaluate_snapshot(...)` evaluate one
  explicit retrieval scope;
- decision-relevant candidate scopes are collected before authorization;
- if there is more than one candidate, the engine resolves a winner through the
  snapshot supersession graph;
- a unique winner is required for snapshot competition/applicability;
- a valid supersession edge requires:
  - successor `supersedes` resolves to the predecessor scope;
  - predecessor and successor use the same retrieval authority;
  - successor attestation explicitly sets
    `supersession_authority_id == retrieval_authority_id`;
  - successor `snapshot_version` is greater than predecessor version;
  - predecessor projection is either carried unchanged or explicitly retracted.

The public `RetrievalAuthorityAttestation` exposes
`supersession_authority_id`, so this path is available to an external host
without modifying the frozen controller.

## Controlled result

Five fresh-process modes were tested with the same single POSITIVE/CURRENT E1 and
DISTINCT provenance.

### SINGLE_SCOPE

- resolved winner = evaluated scope
- claim state = VERIFIED
- control closure = true
- false gates = []
- supersession certificates = 0

### PARALLEL_NO_SUPERSESSION

- two decision-relevant candidate scopes
- resolved winner = none
- claim state = UNRESOLVED
- control closure = false
- gates/false gates = empty
- stop_type = NONE
- supersession certificates = 0

### VALID_SUCCESSOR_EVALUATED

Successor uses version 2, references predecessor via `supersedes`, and carries
explicit same-authority supersession permission.

- resolved winner = successor
- supersession certificates = 1
- claim state = VERIFIED
- control closure = true
- false gates = []

### VALID_PREDECESSOR_EVALUATED

The same valid supersession graph exists, but the predecessor is passed as the
evaluated retrieval scope.

- resolved winner = successor
- supersession certificates = 1
- claim state = UNRESOLVED
- control closure = false
- gates/false gates = empty
- stop_type = NONE

### SUPERSEDES_WITHOUT_VERSION_INCREASE

A successor reference exists but the version does not increase.

- resolved winner = none
- supersession certificates = 0
- claim state = UNRESOLVED
- control closure = false
- gates/false gates = empty
- stop_type = NONE

## Classification

**INTENDED MULTI-SCOPE SNAPSHOT COMPETITION REQUIRES A UNIQUE VALID SUPERSESSION WINNER**

The earlier multi-retrieval-scope result is explained by the frozen competition
contract:

`multiple decision-relevant snapshots + no valid unique supersession winner -> fail closed`

and:

`valid authorized successor + successor evaluated -> VERIFIED / ALLOW`

Therefore the previously open multi-retrieval-scope boundary is not evidence of
stale-relation authorization persistence and is not classified as a false block.

The stale-relation finding remains separately localized to stale E2 participating
inside the evaluated snapshot with a shared provenance/dependency relation.
