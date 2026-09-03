# CFC Demonstrator — CASE_06_WRONG_AUDIT_SCOPE

Status: **PASS / executable / replayed**

## Teaching point

Even when the claim itself is verified by current evidence, an invalid audit scope blocks decision closure.

## Frozen controller result

- claim status: `VERIFIED`
- reason: `policy-satisfied support set (1)`
- stop type: `NONE`
- control closure: `false`
- false gates: `scope_adequacy_valid`

Presentation mapping: **STOP**.

`run_case.py` uses only the public `cfc_anchor` surface and was replayed in three fresh processes with byte-identical output. Synthetic case-scoped verifiers establish only the fictional demonstration trust state; they are not production IAM/crypto.
