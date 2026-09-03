# CFC Demonstrator — CASE_04_REDUNDANCY_VALID_RESOLUTION

Status: **PASS / executable / replayed**

## Teaching point

Three current, trusted synthetic records support the same proposition. E1 and E2 are explicitly verified as the required independent support set. E3 is in the matching universe but has a modeled `REDUNDANCY_ONLY` relation with E2. The host supplies an exact, externally attested `REDUNDANT_RELATION_ACCOUNTED` resolution and a certified excluded-support disposition for E3.

The frozen controller then returns:

- claim status: `VERIFIED`
- reason: `policy-satisfied support set (2)`
- stop type: `EPISTEMIC_STOP`
- control closure: `true`
- false gates: `0`

Presentation mapping: **ALLOW**.

## Important boundary

This is a **relation-resolution case**, not an override of a direct factual contradiction. Direct polarity/state contradictions remain a separate hard-quarantine behavior in the frozen engine and must not be presented as if a relation-resolution certificate can simply vote them away.

## Reproducibility

`run_case.py` uses only the public `cfc_anchor` surface. It does not import `cfc_anchor._engine`, `cfc_anchor.testing`, or `developer_fixture_session`. The reference result was reproduced in three fresh processes with byte-identical JSON.
