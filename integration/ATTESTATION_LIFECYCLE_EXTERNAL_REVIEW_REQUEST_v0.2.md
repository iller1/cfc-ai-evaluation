# CFC Attestation Lifecycle — External Review Request v0.2

**Review type:** independent adversarial / contract-boundary review  
**Target:** CFC Anchor 0.2.90rc1 attestation lifecycle at the host–Anchor boundary  
**Frozen baseline:** must not be modified, repaired, rescored, or reinterpreted

## What I am asking you to decide

Please independently review a reproducible attestation-lifecycle finding involving source-independence and support-set-independence attestations.

The narrow question is:

> Does the reproduced current-use mismatch violate an explicit frozen CFC Anchor contract, or does it expose a lifecycle policy that the frozen public-interface contract does not specify and therefore must be enforced by the host/integration layer?

I am **not** asking you to evaluate the whole CFC project, redesign the controller, or accept my current interpretation.

## Required review order

1. Verify the supplied artifact identities and checksums.
2. Reproduce or independently inspect the preserved minimal reproducers.
3. Confirm whether the frozen Anchor returns closure in the preserved expiry / rejected-reverification sequences.
4. Only then inspect the frozen contract sources.
5. If you conclude that the behavior violates the frozen Anchor contract, cite the exact frozen artifact and exact locator that requires:
   - evaluate-time freshness of SI/SSI attestations; and/or
   - revocation/invalidation of a previously installed runtime pin after failed re-verification.
6. Review the non-frozen lifecycle guard separately. Do not treat its STOP as a rewritten Anchor result.
7. Complete `ATTESTATION_LIFECYCLE_REVIEWER_DECISION_FORM_v0.2.md`.

## Current bounded finding

The preserved adversarial harness reproducibly obtains `control_closure=true` from frozen CFC Anchor 0.2.90rc1 after:

- an independence attestation has expired relative to the current-use decision context; and
- a negative re-verification, when the caller continues evaluation on the preserved runtime state.

Those cases fail the preregistered current-use oracle. The current contract adjudication does **not** treat that as proof of a frozen-contract violation because the inspected R267/R268 interface-freeze sources do not explicitly define those lifecycle semantics.

## What would change the conclusion

A reviewer can overturn the current adjudication by producing either:

- a contradictory reproduction on the exact frozen artifact; or
- an exact frozen normative clause establishing the missing lifecycle guarantee.

A general statement that expiry is unsafe, or that a safer design would re-check freshness, is not sufficient to establish a frozen-contract violation.

## Package

Review package:

`CFC_Attestation_Lifecycle_External_Review_Pack_v0.2.1.zip`

Expected SHA-256:

`c4e2fc99be3ab57bbdd43afa4dfdf7828e45aa085d5258fd262595d8c20230a7`

The package includes the preserved reproducer evidence, fresh rechecks, normal-chain guard results, contract adjudication, contract matrix, and reviewer decision form.

## Acceptable primary verdicts

Please choose exactly one in the supplied decision form:

- `CONFIRM_BOUNDARY_FINDING`
- `ESTABLISH_FROZEN_CONTRACT_VIOLATION`
- `REJECT_FINDING_AS_REPRODUCTION_ERROR`
- `INSUFFICIENT_EVIDENCE`

## Claim discipline

Please keep these layers separate:

1. raw frozen Anchor behavior;
2. the preregistered current-use oracle;
3. frozen-contract semantics;
4. non-frozen host mitigation.

The review should not silently convert one layer into another.
