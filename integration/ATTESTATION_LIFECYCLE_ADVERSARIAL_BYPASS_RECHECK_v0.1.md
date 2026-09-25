# CFC Attestation Lifecycle — Adversarial Bypass Recheck v0.1

**Date:** 2026-09-13  
**Status:** REPRODUCED / bounded current-use lifecycle finding  
**Baseline:** exact frozen CFC Anchor 0.2.90rc1 from CFC Demonstrator v1.0  
**Mode:** ADVERSARIAL_BYPASS — intentionally bypasses the new host-side lifecycle guard

## Boundary

This recheck is separate from the normal integration chain.

Normal chain:

`attestation -> lifecycle guard -> ELIGIBLE_FOR_ANCHOR -> frozen Anchor`

This recheck intentionally executes the preserved pre-existing minimal reproducer directly against the exact frozen Anchor so that the host-side guard cannot hide or repair frozen behavior.

It does **not** modify the frozen controller, wrapper, or demonstrator. It does not redefine the frozen Anchor contract.

## Frozen artifact identity

The exact Demonstrator v1.0 package was revalidated before execution.

- Demonstrator ZIP SHA-256: `d4c46d435994a291cf09cc9ca880be06bd4271c83e2875f9fbf3f887bd08ae28`
- Anchor wheel SHA-256: `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`
- Anchor engine SHA-256: `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`
- mandatory gates: `49`
- persistence schema: `DECISION_PERSISTENCE_HISTORY_V6`

Release verification before the E2E/recheck passed manifest 108/108, preset replay 10/10, custom regression, and reviewer A/B checks.

## Preserved reproducer identity

The reproducer and expected historical outputs were taken from the preserved `CFC_Attestation_Adversarial_Audit_2026-09-13.zip` package, not rewritten for this recheck.

| Artifact | SHA-256 | Preserved manifest match |
|---|---|---|
| `minimal/repro.py` | `1a8161fc253f7912831802058d1c4a279760f96bbb3899c53028c40faf36b92d` | YES |
| `minimal/si-expiry.json` | `446f02742914eec2c7e56048886d1d8d39ba50bac198e551a292eef7e48ac417` | YES |
| `minimal/ssi-expiry.json` | `dc91c8ca7ae54a4775990a9ddf60def6cf59d16fb59ceca781d78e798496d6d8` | YES |
| `minimal/ssi-revocation.json` | `5ae43807e1adec06f2a7b4dfdfb8f4f3473de706cf4c4351869f1d4bb1b89f22` | YES |

## Fresh re-execution

Each preserved mode was executed twice in a fresh Python process against the exact frozen runtime.

| Mode | Predeclared current-use expected closure | Frozen `control_closure` | Frozen `stop_type` | Run 1 SHA | Run 2 SHA | Historical-byte match |
|---|---:|---:|---|---|---|---|
| `si-expiry` | false | **true** | `EPISTEMIC_STOP` | `446f02742914eec2c7e56048886d1d8d39ba50bac198e551a292eef7e48ac417` | same | YES |
| `ssi-expiry` | false | **true** | `EPISTEMIC_STOP` | `dc91c8ca7ae54a4775990a9ddf60def6cf59d16fb59ceca781d78e798496d6d8` | same | YES |
| `ssi-revocation` | false | **true** | `EPISTEMIC_STOP` | `5ae43807e1adec06f2a7b4dfdfb8f4f3473de706cf4c4351869f1d4bb1b89f22` | same | YES |

For `ssi-revocation`, the registered verifier first rejects explicit reverification with:

`support-set independence verifier did not re-approve exact attestation`

The caller then continues to `evaluate`; the previously installed state remains usable and the raw result has `control_closure=true`, with claim state `VERIFIED` and reason `policy-satisfied support set (2)`.

## Result

**Reproduction status: CONFIRMED.**

The three bounded minimal current-use lifecycle reproductions are deterministic across two new processes and byte-for-byte identical to the preserved outputs from the earlier audit.

This strengthens the evidence that the observed behavior is a stable property of the frozen executable path under these exact sequences, rather than a one-off harness artifact.

## What this establishes

It establishes a reproducible mismatch between:

- the predeclared **current-use lifecycle policy** used by the adversarial audit; and
- the behavior obtained when the preserved sequence is executed directly against frozen Anchor 0.2.90rc1.

Under that policy, expired authority or an explicitly rejected current reverification must prevent closure. The preserved direct executions still produce closure.

## What this does NOT establish

This recheck does **not** by itself prove that frozen Anchor violates its own published contract.

The unresolved contract question remains:

> Does a successful independence-attestation verification authorize a durable installed certificate/pin, or must that external attestation remain current at every later closure decision?

Likewise, after a failed revalidation, the host may be contractually expected to abort rather than continue. Until the frozen contract resolves those semantics, the technically accurate description remains:

**reproducible attestation-lifecycle current-use finding at the host–Anchor boundary**

rather than an unconditional claim of an Anchor vulnerability.

## Relationship to the new lifecycle guard

The separately developed host-side Attestation Lifecycle Integration Profile v0.1 blocks these classes before an Anchor call under the normal integration chain. Its normal E2E suite currently returns 23/23 PASS with zero false ALLOW and invokes the frozen Anchor only for lifecycle-eligible controls.

That host-side mitigation must not be used to reinterpret or erase the direct frozen behavior recorded here. The normal-chain E2E and the adversarial-bypass recheck are separate evidence classes.
