# CFC-next 0.3.0a2 peer-context isolation review

## Why this review exists

CFC-next 0.3.0a2 intentionally uses registries provided by the frozen engine
inside one Python interpreter. The previous state-isolation review established
that candidate accounting authorization does not authorize an ordinary frozen
Controller.

The first peer-controller harness attempted to build candidate contexts A and B
with the same blocker family. It failed before any accounting authorization was
installed: after context A existed, context B no longer exposed the single
required decision-level obligation expected by the harness.

That first failure is preserved as evidence. It is not classified as an
accounting-authorization leak because no accounting row had yet been installed.

## Diagnostic split

The revised harness separates two cases.

### GLOBAL_SHARED_RELATION_ID

A and B use different evidence IDs, source IDs, identity registry entries,
retrieval scopes and snapshots, but the blocker relation itself uses the exact
same identifier in both contexts, for example:

- `general-record:root:shared`
- `extractor:shared`
- `data:shared:data_source`

This reproduces the original taxonomy fixture semantics and tests whether exact
relation-identity reuse creates observable cross-context interference.

### TENANT_NAMESPACED_RELATION_ID

The relation remains shared between E1 and E2 inside each context, but its
identity is distinct across A and B, for example:

- A: `general-record:root:shared:A`
- B: `general-record:root:shared:B`

This distinguishes global relation-ID collision from broader peer-controller
state interference.

## Execution order controls

For each representative relation and namespace mode, fresh subprocesses run:

1. A only;
2. B only;
3. A then B;
4. B then A.

The harness compares the second-built context with its standalone baseline and
records:

- claim state;
- control closure;
- false gates;
- decision-support-closure gate;
- required decision-level accounting obligations;
- selected support map.

No accounting authorization is installed in this diagnostic phase.

## Classification

Possible bounded classifications include:

- `SHARED_RELATION_ID_CROSS_CONTEXT_INTERFERENCE`
- `PEER_CONTROLLER_CONTEXT_ISOLATION_FINDING`
- `PEER_CONTEXT_CONSTRUCTION_ISOLATION_PASS`

A finding limited to exact shared relation IDs must not be generalized into an
arbitrary peer-controller or multi-user authorization leak without further
evidence.

The frozen CFC-next 0.3.0a2 source and frozen CFC Anchor reference remain
unchanged. Historical results are not rescored.


## Canonical identity axis

The relation-ID diagnostic showed interference even when A and B used distinct
relation identifiers. The next diagnostic therefore holds relation identifiers
tenant-namespaced and varies the canonical identity target:

- **SHARED_CANONICAL_IDENTITY** — A and B have different identity registry
  entry IDs but both refer to the same surface subject/entity/event/version;
- **TENANT_NAMESPACED_CANONICAL_IDENTITY** — A and B use distinct surface
  subjects, entity IDs and event IDs as well as distinct registry entries.

This determines whether the observed second-context transition to UNRESOLVED
is specifically caused by multiple registry entries for the same canonical
identity or persists even for fully separate identities.

This phase still installs no decision accounting authorization. It is a
construction/evaluation isolation diagnostic, not an authorization-leak test.
