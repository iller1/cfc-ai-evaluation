# CFC Demonstrator — CASE_10_INCOMPLETE_REQUIRED_CHECKS

Status: **PASS / executable / replayed**

## Teaching point

One current, trusted synthetic record supports the proposition, while the explicit requirement is `required_independent_supports = 2`.

The frozen controller returns:

- claim status: `SUPPORTED`
- reason: `direct referent-consistent support E1; support policy pending`
- policy violation: `INSUFFICIENT_SUPPORT_COUNT` (`observed = 1`, `required = 2`)
- control closure: `false`

Presentation mapping: **STOP**.

The distinction is deliberate: evidence may support a proposition without satisfying the full requirements for closure.

## Reproducibility

`run_case.py` uses only the public `cfc_anchor` surface. The preserved result was reproduced in three fresh processes with byte-identical JSON.
