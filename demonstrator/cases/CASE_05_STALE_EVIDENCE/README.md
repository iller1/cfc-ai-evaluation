# CFC Demonstrator — CASE_05_STALE_EVIDENCE

Status: **PASS / executable / replayed**

## Teaching point

A record can be structurally trusted yet stale at the audit date; stale evidence must not justify closure.

## Frozen controller result

- claim status: `UNRESOLVED`
- reason: `no referent-consistent epistemically available support`
- stop type: `NONE`
- control closure: `false`
- false gates: `claim_specific_support_policy_valid, claim_support_universe_common_mode_coverage_valid, decision_relevant_relation_discovery_complete_valid, decision_support_closure_valid, no_critical_unresolved, source_independence_semantics_valid, support_relation_instance_resolution_coverage_valid, support_selection_justification_valid, support_set_common_mode_coverage_valid`

Presentation mapping: **STOP**.

`run_case.py` uses only the public `cfc_anchor` surface and was replayed in three fresh processes with byte-identical output. Synthetic case-scoped verifiers establish only the fictional demonstration trust state; they are not production IAM/crypto.
