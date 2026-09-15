# CFC Attestation Lifecycle — External Reviewer Decision Form v0.2

**Review target:** attestation lifecycle / host–Anchor trust boundary  
**Baseline:** frozen Operator Wrapper v1.23 + frozen CFC Anchor 0.2.90rc1  
**Review rule:** do not modify, repair, rescore, or reinterpret frozen artifacts.

## 1. Integrity check

Record the identities you actually reviewed.

| Item | Expected identity | Reviewer result |
|---|---|---|
| Operator Wrapper v1.23 | SHA-256 `95277663c445509af0820c3abdddaa295dfaaf93dd077ce32897b185b80957d8` | |
| Formal State & Closure Specification v1.0 | SHA-256 `2f287292d52abf72e2461569cdab2a7d0920f3aa1a48197e0f0a0de1de4c32e1` | |
| CFC Anchor 0.2.90rc1 wheel | SHA-256 `b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303` | |
| Frozen Anchor engine | SHA-256 `77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0` | |
| R267 logical public API contract | SHA-256 `fee18165ea5d4a29e72137028ec3cf5c637b85c83672437b2352fc316f53b66a` | |

If any identity differs, stop and classify the review as `BASELINE_IDENTITY_MISMATCH`.

## 2. Reproduction decision

Run or independently inspect the preserved minimal reproducers before interpreting the contract.

| Reproducer | Predeclared current-use expectation | Expected preserved frozen behavior | Reproduced? |
|---|---|---|---|
| SI expires after valid admission | no closure | `control_closure=true` | |
| SSI expires relative to decision context | no closure | `control_closure=true` | |
| rejected SSI reverify, then continued evaluate | no closure | rejected reverify, then `control_closure=true` | |

If a reproducer does not match, provide the exact command, raw output, artifact hashes, and smallest explanation that accounts for the difference.

## 3. Normative contract questions

Answer each question independently. Do not infer a rule merely because it would be desirable or safer.

### Q1 — evaluate-time freshness

Does any **frozen Anchor normative source** explicitly require `SourceIndependenceAuthorityAttestation` or `SupportSetIndependenceAuthorityAttestation` to remain temporally valid at every later `evaluate(...)` / `evaluate_snapshot(...)` call?

- [ ] YES
- [ ] NO
- [ ] UNRESOLVED

If YES, provide the exact frozen artifact and exact locator. A general wrapper rule about expired fictional records is not sufficient unless the source explicitly maps it to Anchor SI/SSI runtime lifecycle.

**Source / locator:**

**Reason:**

### Q2 — failed re-verification effect

Does any frozen Anchor normative source explicitly require a failed or negative SI/SSI re-verification to revoke or invalidate the previously installed runtime pin/certificate before later evaluation?

- [ ] YES
- [ ] NO
- [ ] UNRESOLVED

**Source / locator:**

**Reason:**

### Q3 — interface freeze versus behavior guarantee

Do R267/R268 freeze only the public API/trust-boundary surface, or do they additionally guarantee the lifecycle semantics in Q1/Q2?

- [ ] INTERFACE / TRUST SURFACE ONLY
- [ ] THEY EXPLICITLY GUARANTEE Q1/Q2
- [ ] UNRESOLVED

If selecting the second option, cite the exact normative clause.

**Source / locator:**

**Reason:**

### Q4 — wrapper-to-Anchor transfer

Is there an explicit frozen rule permitting the Operator Wrapper v1.23 temporal rule (“historical approval is not current approval” / relevant expiry blocks current approval) to be transferred as a normative SI/SSI runtime rule of CFC Anchor 0.2.90rc1?

- [ ] YES
- [ ] NO
- [ ] UNRESOLVED

**Source / locator:**

**Reason:**

## 4. Integration-profile review

Review the non-frozen lifecycle guard separately from the frozen Anchor finding.

Confirm or reject each property:

- [ ] guard success means only `ELIGIBLE_FOR_ANCHOR`, never `ALLOW`;
- [ ] decision-time temporal validity and TTL are checked;
- [ ] case/scope/purpose/resource/audience are exactly bound;
- [ ] revocation freshness is checked;
- [ ] replay is blocked by single-use decision binding or session+nonce;
- [ ] duplicate attestation IDs cannot satisfy an independence count twice;
- [ ] shared root or shared failure domain cannot automatically establish independence;
- [ ] failed/unresolved revalidation removes host-side cached eligibility;
- [ ] STOP/UNRESOLVED cases are not silently passed to Anchor in normal-chain E2E.

If any property fails, provide a minimal input producing the contrary result.

## 5. Required final verdict

Select exactly one primary verdict.

- [ ] `CONFIRM_BOUNDARY_FINDING` — reproduced current-use mismatch; no explicit frozen Anchor contract clause establishing Q1/Q2 was found; lifecycle requirement belongs in an explicit integration policy.
- [ ] `ESTABLISH_FROZEN_CONTRACT_VIOLATION` — reproduced behavior violates an explicit frozen Anchor normative clause. **Exact frozen source + locator is mandatory.**
- [ ] `REJECT_FINDING_AS_REPRODUCTION_ERROR` — preserved behavior does not reproduce on the identified frozen artifact. Raw contradictory evidence is mandatory.
- [ ] `INSUFFICIENT_EVIDENCE` — evidence is insufficient to decide; list the missing artifact or unresolved fact.

## 6. Claim-discipline check

Mark each statement as acceptable or unacceptable on the reviewed evidence.

| Statement | Acceptable? | Reason |
|---|---|---|
| “A current-use lifecycle mismatch is reproducible.” | | |
| “The host-side current-use guard mitigates the tested normal-chain cases without changing Anchor.” | | |
| “Frozen Anchor 0.2.90rc1 is proven to violate its frozen contract.” | | |
| “Seven independent Anchor vulnerabilities were found.” | | |
| “The root of trust was bypassed.” | | |
| “The lifecycle responsibility is entirely the host’s.” | | |

## 7. Reviewer notes

**Reviewer / affiliation (optional):**

**Date:**

**Environment:**

**Additional frozen sources inspected:**

**Material disagreement with the supplied adjudication:**

**Recommended publication wording:**
