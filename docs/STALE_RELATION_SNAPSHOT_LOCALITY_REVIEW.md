# Stale relation snapshot locality review

## Goal

Determine where the observed relation-level stale authorization persistence lives
relative to the evaluated retrieval snapshot.

The frozen controller remains unchanged.

## Primary matrix

Hold constant:

- conclusion = POSITIVE;
- E1 = POSITIVE / CURRENT;
- E1 alone satisfies required supports = 1;
- E2 = POSITIVE / STALE;
- scope of each installed snapshot is explicit;
- no explicit support-set independence certificate;
- every state runs in a fresh subprocess.

Vary relation shape:

1. DISTINCT control;
2. common-mode group;
3. root-origin identity;
4. one generic dependency identity (`data_source`).

Vary E2 placement:

1. `EVALUATED_SNAPSHOT` — E2 is part of the snapshot being evaluated;
2. `OTHER_SNAPSHOT` — E2 is installed in a separate verified retrieval scope before E1 is evaluated;
3. `VERIFIED_ONLY` — E2 is fully verified but is not installed in any retrieval snapshot.

Total: **12 isolated states**.

## Primary result

### EVALUATED_SNAPSHOT

- DISTINCT: VERIFIED / ALLOW
- common-mode: VERIFIED / STOP
- root-origin: VERIFIED / STOP
- generic dependency: VERIFIED / STOP

For the three shared-relation cases the only false gate is:

`decision_support_closure_valid`

This reproduces the relation-level stale authorization persistence.

### VERIFIED_ONLY

All four relation shapes produce:

- claim state = VERIFIED
- control closure = true
- false gates = []
- no global-consistency violation

Therefore, merely verifying stale E2 in controller state is not sufficient to
preserve the authorization residue. In the tested path, E2 must participate in
the evaluated retrieval snapshot.

### OTHER_SNAPSHOT

All four relation shapes, including DISTINCT, produce:

- claim state = UNRESOLVED
- control closure = false
- gates = {}
- false gates = []
- stop_type = NONE
- no claim-support-policy violation
- no critical unresolved item
- no global-consistency, evidence, identity, or integration error

Because the DISTINCT control behaves identically, this result is **not**
classified as a stale-relation effect.

## Multi-snapshot reducer

A separate DISTINCT-provenance reducer varied only retrieval context:

- `VERIFIED_ONLY`
- different scope, auxiliary snapshot installed first
- different scope, evaluated snapshot installed first
- same scope, auxiliary snapshot installed first
- same scope, evaluated snapshot installed first

Result:

### VERIFIED_ONLY

- VERIFIED / ALLOW

### Different retrieval scopes

Both installation orders produce the same result:

- UNRESOLVED / STOP
- gates = {}
- stop_type = NONE

Therefore the effect is order-insensitive in the tested pair.

### Same retrieval scope

The second snapshot installation is rejected in both orders with:

`ValueError: retrieval scope_id already exists with different content or authority`

This shows that one `scope_id` cannot be reused for different snapshot
content/authority in this path.

## Classification

### Stale relation finding

**EVALUATED-SNAPSHOT-BOUND RELATION-LEVEL STALE AUTHORIZATION PERSISTENCE**

Within the tested single-snapshot path:

`stale E2 verified but outside evaluated snapshot -> no relation-level authorization residue`

`stale E2 inside evaluated snapshot + shared relation -> STOP/VERIFIED`

This narrows the previously observed persistence from controller-global evidence
state to the evaluated snapshot path.

### Separate retrieval-context boundary

**MULTI-RETRIEVAL-SCOPE CONTEXT BOUNDARY**

Installing a second verified retrieval scope causes the tested simple
`evaluate_snapshot` path to return UNRESOLVED with no populated gate set,
independent of relation shape and installation order.

This is recorded separately. It is not classified as a false block, and the
current experiment does not claim whether this fail-closed behavior is required
by the intended multi-scope contract.

## Non-claim

Nothing in this review changes CFC Anchor 0.2.90rc1 or establishes that the
multi-scope behavior is erroneous.
