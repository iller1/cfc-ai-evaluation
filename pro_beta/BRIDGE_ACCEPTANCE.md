# HAWM → CFC Bridge Acceptance Pack v1

This pack is a regression gate for the bounded structured HAWM → frozen CFC bridge.

It does **not** interpret free-text HAWM fields and does **not** establish production-grade provenance or external trust. It exercises explicit structured synthetic inputs through frozen CFC Anchor `0.2.90rc1`.

Acceptance scenarios:

1. sufficient current support → `VERIFIED / ALLOW`
2. insufficient support count → `SUPPORTED / STOP`
3. active contradiction → `QUARANTINED / STOP`
4. stale support → `UNRESOLVED / STOP`
5. wrong scope → `VERIFIED / STOP`
6. two distinct current supports with explicit independence authority → `VERIFIED / ALLOW`
7. two current supports with shared lineage → `SUPPORTED / STOP`

Run locally with:

`python -m unittest -v pro_beta.test_bridge_acceptance`

The acceptance pack passes only when all seven scenarios match their expected frozen-controller behavior and the structured-input boundary remains explicit.
