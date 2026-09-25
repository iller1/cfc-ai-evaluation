# CFC-next negative decision-accounting baseline

## Purpose

Freeze the current fail-closed behavior for the 12 negative-control classes in
the CFC-next decision-accounting acceptance manifest.

This is a **frozen-reference baseline**, not a repair and not a rescore of
historical CFC Anchor 0.2.90rc1 results.

Each negative control runs in a fresh subprocess.

## Public attestation lifecycle

The public decision generic-accounting lifecycle has two distinct authorities:

- an **external host-trusted attestor** supplies
  `DecisionGenericDependencyAccountingAttestation`;
- after that attestation is verified, the wrapper registers the internal
  accounting row using the reserved engine-local
  `LOCAL_SUPPORT_UNIVERSE_AUTHORITY`.

The shared decision-attestation validator explicitly rejects an external
attestation that tries to impersonate the reserved engine-local authority. This
is intended trust-boundary behavior, not a contract conflict.

## Frozen baseline result

All 12 controls are fail-closed. There are **zero unexpected BOUND
authorization paths**.

Three controls are currently rejected first by the public
`evidence_ids ⊆ selected_supports` guard:

- `NEG_WRONG_NODE_CORRECT_ENDPOINTS`;
- `NEG_NONSEL_ENDPOINT_OUTSIDE_EVALUATED_SNAPSHOT`;
- `NEG_NONSEL_ENDPOINT_WITHOUT_REQUIRED_OBLIGATION`.

For each of those, an explicit expanded-selected-map localization control was
also run. In all three controls:

1. draft creation becomes possible;
2. the externally attested record installs;
3. the registry row remains `PENDING`;
4. finalize rejects it with
   `generic dependency accounting did not bind to exact decision context`.

So the current selected-support-only guard masks the future Repair-B admission
condition, but downstream exact binding independently remains fail-closed.

## Exact frozen signatures

| Negative class | Earliest / decisive frozen result |
| --- | --- |
| Wrong node, correct endpoints | exact map rejected early; expanded control installs PENDING, exact finalize rejects bind |
| Correct node, wrong endpoint set | installs PENDING; exact finalize rejects bind |
| Non-selected endpoint outside evaluated snapshot | exact map rejected early; expanded control installs PENDING, exact finalize rejects bind |
| Non-selected endpoint without required obligation | exact map rejected early; expanded control installs PENDING, exact finalize rejects bind |
| Wrong selected-support map | installs PENDING; exact finalize rejects bind |
| Wrong retrieval scope / snapshot | draft rejects: retrieval scope is not installed |
| Wrong claim requirements | install rejects: draft is not bound to this decision context |
| Stale decision-context commitment | install rejects: draft is not bound to this decision context |
| Source-semantic node in generic channel | installs PENDING; exact finalize rejects bind |
| Invalid node structure / blank identifier | draft rejects: invalid generic dependency node |
| Mismatched external attestation | install rejects: attestation does not bind exact decision projection |
| Accounting outside exact fresh universe | installs PENDING; exact finalize rejects bind |

The machine-readable expected signatures live in
`research/cfc_next_accounting_acceptance_manifest.json` and are asserted by
`review_cfc_next_negative_control_baseline.py`.

## CFC-next meaning

After Repair A and Repair B, the three currently masked controls must be
re-executed through the newly reachable exact selected/excluded admission path.
They must still reject or remain non-authorizing for their **actual semantic
reason**, not merely because of the old blanket selected-support restriction.

The existing exact decision-context, universe, node, endpoint, attestation and
binding checks should continue to provide the downstream fail-closed boundary.

Frozen CFC Anchor 0.2.90rc1 remains unchanged.
