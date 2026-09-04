# CFC Demonstrator — CASE_09_INACTIVE_UNBOUND_RESOLUTION

Status: **PASS / executable / replayed**

## Teaching point

The host installs an externally verified relation-resolution declaration, but deliberately does **not** finalize/bind it to the exact decision context. The frozen public API leaves the installation `bound = false`.

The frozen controller then fails closed before ordinary claim evaluation:

- integration error: `RELATION_RESOLUTION_NOT_BOUND`
- gate: `integration_decision_authority_runtime_verified = false`
- control closure: `false`

Presentation mapping: **STOP**.

## Important boundary

This case does not invent an `INACTIVE` status. It demonstrates the public API's real `PENDING/unbound` resolution state: verified existence is not sufficient authority for closure.

## Reproducibility

`run_case.py` uses only the public `cfc_anchor` surface. The preserved result was reproduced in three fresh processes with byte-identical JSON.
