# CFC-next 0.3.0a2 peer-context isolation review

## Scope

This review does not modify the frozen CFC-next 0.3.0a2 baseline and does not
rescore any historical benchmark.

It investigates same-interpreter cross-context behavior before any decision
accounting authorization is installed.

## Initial observation

The first peer-controller harness attempted to build candidate contexts A and B
with the same blocker family. It failed before accounting installation: after A
existed, B no longer exposed the single required decision-level obligation
expected by the harness.

The first failure is preserved as evidence. It was not an accounting
authorization leak because no accounting row had yet been installed.

## Diagnostic 1: relation identity

The harness separates:

### GLOBAL_SHARED_RELATION_ID

A and B use different evidence IDs, source IDs, identity registry entries,
retrieval scopes and snapshots, but the blocker relation itself has the exact
same identifier in both contexts.

### TENANT_NAMESPACED_RELATION_ID

The relation remains shared between E1 and E2 inside each context, but its
identifier is different across A and B.

For every one of the 14 blocker families and both namespace modes, fresh
subprocesses run:

1. A only;
2. B only;
3. A then B;
4. B then A.

Result: **112 scenarios**.

Observed in all 14 blocker families under both relation-ID modes:

- a standalone context is VERIFIED;
- it exposes one required decision-level accounting obligation;
- it remains fail-closed because decision-support closure is not yet satisfied;
- when a second independently registered context for the same canonical
  identity already exists in the interpreter, the later evaluated context is
  UNRESOLVED;
- its selected support map is empty;
- its required decision-level obligation count is zero;
- control closure remains false.

Changing only the relation identifier therefore does not remove the
interference.

## Diagnostic 2: canonical identity

The second diagnostic keeps relation identifiers tenant-namespaced and varies
the identity target.

### SHARED_CANONICAL_IDENTITY

A and B use different identity registry entry IDs, evidence IDs, scopes and
snapshots, but both identity records refer to the same surface
subject/entity/event/version.

### TENANT_NAMESPACED_CANONICAL_IDENTITY

A and B use distinct surface subjects, entity IDs and event IDs in addition to
distinct identity registry entries and relation identifiers.

Again all 14 blocker families are executed in A-only, B-only, A-then-B and
B-then-A fresh-process controls: **112 scenarios**.

Result:

- shared canonical identity: interference reproduced in **14/14** blocker
  families;
- tenant-namespaced canonical identity: interference reproduced in **0/14**
  blocker families;
- no scenario produced unauthorized control closure;
- no accounting authorization was installed in either diagnostic.

## Adjudication

Machine-readable classification:

`FAIL_CLOSED_SHARED_CANONICAL_IDENTITY_CROSS_CONTEXT_INTERFERENCE`

This is a same-process global-registry boundary, not evidence of a
decision-accounting authorization leak.

The observed transition is fail-closed:

`VERIFIED -> UNRESOLVED`

rather than an unauthorized transition to closure.

The evidence supports the narrower statement that independently registering
the same canonical entity/event/version in multiple same-interpreter contexts
can affect identity resolution across those contexts. When canonical identity
is distinct across A and B, the tested interference disappears in all 14
blocker families.

## Deployment implication

A service that wants independent request/session semantics must not assume that
separate Controller objects imply separate frozen runtime registries.

Until registry-level canonical identity coordination or explicit context
isolation is designed and validated, safe integration should use one of these
boundaries:

1. process isolation for independent CFC runs; or
2. an explicitly coordinated canonical identity registry that prevents
   independent duplicate registrations from competing in the global runtime.

The current Pro Beta prepared-CFC execution path already invokes the frozen
custom case runner through a subprocess, so this finding does not establish a
cross-session defect in the currently deployed Beta path.

Do not replace that process boundary with a long-lived shared in-process
Controller pool without a separately validated isolation design.

## Claim boundary

This review does not claim:

- arbitrary multithreaded safety or unsafety;
- an authorization bypass;
- production readiness;
- cross-process interference;
- that every possible identity-registry pattern has been tested.

It establishes the bounded 224-scenario result above across the complete
14-family decision-accounting blocker taxonomy.
