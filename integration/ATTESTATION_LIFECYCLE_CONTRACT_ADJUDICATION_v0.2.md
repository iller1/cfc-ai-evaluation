# CFC Attestation Lifecycle — Contract Adjudication v0.2

**Date:** 2026-09-13  
**Status:** `ADJUDICATED_WITH_NORMATIVE_GAP`  
**Frozen baseline modified:** `NO`  
**Original adversarial oracle changed:** `NO`  
**Original results rescored:** `NO`

## Executive adjudication

The preserved adversarial finding remains reproducible: under a predeclared **current-use** policy, frozen CFC Anchor 0.2.90rc1 can reach `control_closure=true` after an independence attestation has expired relative to the decision context, and after a negative re-verification when the caller continues evaluation on the preserved runtime state.

After inspection of the frozen Operator Wrapper v1.23, the frozen Formal State & Closure Specification v1.0, the R267 public-interface freeze candidate, the R267 accepted limitations and trust-boundary traceability matrix, and the R268 final freeze decision, the contractual classification is:

> **NO ESTABLISHED FROZEN-ANCHOR CONTRACT VIOLATION.**  
> **A NORMATIVE ATTESTATION-LIFECYCLE GAP EXISTS AT THE HOST–ANCHOR BOUNDARY.**

This is not a conversion of the adversarial FAILs into PASS. It separates two questions:

1. **Behavioral oracle:** current-use validity was required by the test, and the preserved bypass cases fail that oracle.
2. **Frozen Anchor contract:** the inspected R267/R268 freeze defines the stable public interface and trust-boundary surface, but does not state that external SI/SSI attestation validity must be re-evaluated at every later `evaluate(...)`, nor that a rejected re-verification revokes an already-installed runtime pin.

Therefore the current evidence establishes a reproducible lifecycle behavior and an integration-policy requirement, but not a breach of an explicit frozen Anchor guarantee.

---

## 1. Protected identities inspected

| Artifact | Identity / role |
|---|---|
| `CFC_OPERATOR_WRAPPER_v1.23_PROMOTED.txt` | SHA-256 `95277663c445509af0820c3abdddaa295dfaaf93dd077ce32897b185b80957d8`; frozen natural-language decision-control layer |
| `CFC_FORMAL_STATE_AND_CLOSURE_SPECIFICATION_v1.0.md` | SHA-256 `2f287292d52abf72e2461569cdab2a7d0920f3aa1a48197e0f0a0de1de4c32e1`; frozen external descriptive specification of v1.23 |
| CFC Anchor 0.2.90rc1 wheel | SHA-256 `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303` |
| Frozen Anchor engine | SHA-256 `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0` |
| R267 logical public API contract | logical SHA-256 `fee18165ea5d4a29e72137028ec3cf5c637b85c83672437b2352fc316f53b66a` |

No protected artifact above is changed by this adjudication.

---

## 2. Layer-by-layer result

### 2.1 Operator Wrapper v1.23 — current-use semantics are explicitly represented

The promoted wrapper expressly says that, when relevant to the current proposition and records:

- explicit expiry is a demonstrated non-fulfilment;
- wrong scope is a demonstrated non-fulfilment;
- lack of required authority is a demonstrated non-fulfilment;
- common origin/material/basis cannot be converted into independence by format, signature, separate file, issuer, or stage;
- a supplied current assessment must distinguish historical approval from current approval.

G04 is a concrete frozen witness: a certificate valid only through 2026-03-31 cannot establish `CURRENTLY_APPROVED` at an assessment on 2026-08-24, and historical approval is not current approval.

**Classification:** `ALREADY_COVERED` for the wrapper's textual decision semantics when the expiry/scope fact is part of the supplied record state.

**Boundary:** this wrapper is explicitly a textual classifier of fictional records. It does not define CFC Anchor's SI/SSI runtime-pin lifecycle.

### 2.2 Formal State & Closure Specification v1.0 — confirms the wrapper rule, does not transfer it to Anchor API

The specification is explicitly descriptive of `CFC_OPERATOR_WRAPPER_v1.23_PROMOTED.txt` and forbids strengthening or importing missing semantics.

It records:

- expiry, inactivity, wrong scope and lack of required authority as source-backed validity predicates when explicitly demonstrated and relevant;
- `TMP-G04-001`: an expired certificate cannot establish current approval at the later assessment;
- `TMP-G04-002`: historical approval is not current approval;
- no universal authority-state machine;
- no default general temporal semantics beyond what frozen sources express.

**Classification:** `CONFIRMED_FOR_WRAPPER / NOT_A_NORMATIVE_ANCHOR_LIFECYCLE_MAPPING`.

### 2.3 R267/R268 Anchor freeze — interface freeze, not evaluate-time attestation-lifecycle guarantee

R267 freezes the candidate public surface:

- exact exports;
- 90 supported Controller methods and signatures;
- three public properties;
- 17 trust-boundary identifiers;
- host verifier-pinning semantics;
- fail-closed integration mapping.

R268 approves that public-interface freeze. Its freeze rule covers changes to exports, signatures, properties, trust-boundary identifiers and stable-surface exclusions.

R268 also expressly preserves non-claims: the decision is **not** a production-readiness, external-validation, correctness or safety guarantee. Provider-specific verifier implementation and support policy remain outside the freeze.

R267 accepted limitations further state that provider-specific verifier cryptography/IAM/signature formats remain host-owned and that final support policy is not frozen.

**Classification:** `CURRENT_USE_LIFECYCLE_GUARANTEE_NOT_EXPRESSED_IN_FROZEN_INTERFACE_CONTRACT`.

### 2.4 R254 dependency / independence documentation — fail-closed for runtime trust/certificate invalidity, but not for elapsed external-attestation validity

The dependency/independence trust-boundary documentation states that public evaluation fails closed if a relevant relation row:

- is unattested;
- has lost its runtime pin; or
- has a now-invalid engine independence certificate.

It also states that a later modeled `COMMON_MODE` relation can invalidate a previously issued support-set independence certificate.

The preserved lifecycle reproducer is different: the previously established runtime pin remains present, and the engine certificate remains structurally valid. What changed is the external attestation's current-use status or the verifier's later verdict. The inspected freeze documents do not say that either event automatically deletes the prior runtime pin.

**Classification:** `PARTIALLY_COVERED_TRUST_LIFECYCLE / EXTERNAL_CURRENT_USE_REVOCATION_NOT_SPECIFIED`.

---

## 3. Adjudication of preserved findings

| Finding | Preserved behavior | Current-use oracle | Frozen Anchor contract adjudication | Attribution |
|---|---|---|---|---|
| A01 / T08–T10 — expiry after valid admission | reproducible closure | **FAIL** | **NO ESTABLISHED CONTRACT VIOLATION; lifecycle guarantee not expressed** | host–Anchor lifecycle boundary |
| A02 / T11–T12 — negative reverify then continued evaluate | reproducible closure on preserved pin | **FAIL** | **NO ESTABLISHED CONTRACT VIOLATION; revocation effect on prior pin not expressed** | Anchor pin retention + host error handling |
| A03 / T14 — one-time reuse | reproducible under added one-time policy | **FAIL under added policy** | **OUTSIDE FROZEN CONTRACT / NOT ESTABLISHED** | upstream consumption policy |
| A04 / T18 — shared issuer root absent from modeled input | closure if root correlation is not represented | **FAIL under stronger deployment oracle** | **NOT AN ANCHOR ROOT-BYPASS CONTRACT VIOLATION** | unmodeled upstream trust dependency |

This table does not alter any original PASS/FAIL result. It changes only the normative attribution after additional source inspection.

---

## 4. Exact claim boundary after adjudication

### Supported publication claim

> A preserved adversarial harness reproducibly obtains closure from frozen CFC Anchor 0.2.90rc1 after independence-attestation expiry relative to a current-use decision policy, and after rejected re-verification when evaluation continues on a preserved runtime pin. The R267/R268 frozen interface contract does not explicitly define evaluate-time external-attestation freshness or automatic invalidation of an earlier pin after failed re-verification. A separate host-side lifecycle guard can enforce the stricter current-use policy without modifying the frozen Anchor.

### Claims not supported by current evidence

Do **not** state:

- `CFC Anchor 0.2.90rc1 is proven to violate its frozen contract`;
- `the reviewer found seven Anchor vulnerabilities`;
- `revocation is completely ignored`;
- `the root of trust was bypassed`;
- `the host alone is at fault`;
- `the new integration guard changes or repairs the raw Anchor result`.

---

## 5. Resulting architecture decision for pilots

For pilots that require the proposition **"current authority must justify current closure"**, the integration contract must explicitly adopt **current-use** semantics:

1. evaluate attestation temporal validity at decision time;
2. bind exact case/scope/purpose/resource/audience;
3. require sufficiently fresh revocation state;
4. treat failed revalidation as invalidating host-side eligibility and stop the normal workflow;
5. use decision/session replay binding with atomic consumption;
6. model common root/failure-domain relationships rather than counting attestations;
7. pass only `ELIGIBLE_FOR_ANCHOR` into the frozen controller; never reinterpret that as `ALLOW`;
8. preserve direct frozen Anchor output separately for adversarial bypass/reproduction work.

These are **integration requirements**, not retroactive claims about what Anchor already guaranteed.

---

## 6. Final status

- Frozen behavior finding: **CONFIRMED / REPRODUCIBLE**.
- Current-use adversarial oracle failures: **UNCHANGED**.
- Host-side mitigation: **23/23 unit PASS; 23/23 normal-chain E2E PASS; 0 normal-chain false ALLOW**.
- Frozen Anchor contract violation: **NOT ESTABLISHED BY THE INSPECTED FROZEN CONTRACT**.
- Normative lifecycle gap: **CONFIRMED AT HOST–ANCHOR INTEGRATION BOUNDARY**.
- External-review value: **YES** — suitable as a bounded lifecycle/contract-boundary finding and integration-profile review.
