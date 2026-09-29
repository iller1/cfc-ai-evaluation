# Eligible candidate pool criteria v0.1

**Status: DRAFT — NOT FROZEN**

These criteria are intentionally outcome-independent. They must be jointly approved and frozen before any substantive selection seed is created.

## 1. Inclusion criteria

A candidate pair may enter the pool only if all of the following are true **using permitted pre-selection information only**:

1. **Stable pair identity.** The candidate has one unique printable-ASCII `case_id` and exactly two arms, A and B.
2. **Immutable arm binding.** Each arm has an immutable source/specimen reference and SHA-256. Its recorded offline verdict/action is either included inside those exact specimen bytes or, in v0.1, bound by a separate immutable `offline_endpoint_*_sha256`.
3. **Fixed RIDI evaluation premise.** The evaluation definition is fixed before pool freeze and has both a stable identifier/version and an immutable SHA-256. Eligibility cannot depend on the computed RIDI result.
4. **Recorded downstream endpoint.** A recorded or permitted offline verdict/action exists for both arms, is hash-bound before selection, and can be evaluated without causing a blocked real-world action.
5. **One-support compatibility with explicit status.** Original support-requirement status must be recorded as one of:
   - `AUTHORITATIVE_1` — an authoritative original policy explicitly requires one support;
   - `NO_AUTHORITATIVE_REQUIREMENT_SPECIFIED` — no authoritative original support-count requirement is specified for the source case;
   - `AUTHORITATIVE_GT1` — an authoritative original policy requires more than one support;
   - `UNKNOWN` — available pre-selection records do not establish the original requirement.

   Only `AUTHORITATIVE_1` and `NO_AUTHORITATIVE_REQUIREMENT_SPECIFIED` are eligible in this bounded first experiment. `AUTHORITATIVE_GT1` and `UNKNOWN` are ineligible. `UNKNOWN` must never be interpreted as evidence that the original policy required only one support.
6. **M1 representability.** The neutral source fields required by frozen M1 can be represented honestly, including explicit absent-field handling. Missing authority facts may remain NOT_SUPPLIED; they are not repaired.
7. **A1 authority boundary available.** Any authority evidence to be inspected already exists within the frozen A1/I1 boundary. No post-selection discretionary authority assertion is needed to make the case run.
8. **I1 inspection compatibility.** The case can be executed while respecting the frozen pre-commit inspection matrix.
9. **No consequential execution.** RIDI can use recorded/offline downstream outputs if CFC blocks; no live business, clinical, financial or other consequential action is required.
10. **No outcome-based eligibility.** Inclusion does not depend on a predicted, computed or known CFC ALLOW/BLOCK result, RIDI PASS/FAIL result, desired asymmetry, correctness label, or publication value.
11. **Prior exposure recorded.** Any prior public appearance of the case or its A/B outcome is recorded as metadata. Prior exposure is not silently ignored.
12. **No substantive case chosen in advance.** Eligibility rationale is documented before commit–reveal selection and must not identify a preferred case.
13. **Mechanical eligibility check passes.** The candidate passes the frozen pre-selection eligibility checker described in Section 4, and the exact acceptance record is preserved.

## 2. Immutable pair identity and duplicate handling

Each arm receives a mechanical arm binding:

`arm_binding = SHA256(UTF8("CFC-RIDI-ARM-v0.1|" + source_sha256 + "|" + offline_endpoint_sha256))`

The candidate receives an order-independent pair fingerprint:

`pair_fingerprint = SHA256(UTF8("CFC-RIDI-PAIR-v0.1|" + min(arm_binding_A, arm_binding_B) + "|" + max(arm_binding_A, arm_binding_B)))`

Rules:

- the same underlying A/B pair registered under another `case_id` is a duplicate;
- reversing A and B under another ID is still the same pair and is a duplicate;
- duplicate pair fingerprints produce only one eligible-pool entry;
- sharing **one** arm/source record with another otherwise distinct pair does **not** by itself make the two pairs duplicates;
- duplicate handling does not use CFC/RIDI outputs or correctness.

If two registrations have the same pair fingerprint but conflicting metadata, neither is silently preferred. The conflict is logged and must be resolved using pre-selection provenance only before pool freeze.

## 3. Exclusion criteria

Exclude a candidate if any of the following is established before pool freeze:

- original support-requirement status is `AUTHORITATIVE_GT1` or `UNKNOWN`;
- missing/unstable A or B source/specimen identity;
- missing immutable offline endpoint binding for either arm;
- no fixed evaluation definition identifier/version and SHA-256;
- no recorded/permitted offline downstream endpoint;
- M1 cannot faithfully encode the case even with NOT_SUPPLIED handling;
- required authority would have to be newly invented, solicited or edited after selection;
- execution would require violating I1;
- execution would require a prohibited real-world action;
- eligibility depends on known/expected/computed CFC or RIDI output;
- duplicate order-independent pair fingerprint under another registration;
- a metadata conflict affecting eligibility cannot be resolved mechanically from permitted pre-selection evidence.

## 4. Mechanical pre-selection eligibility procedure

Eligibility is determined **before pool freeze** by a deterministic checker that uses only fields permitted for pre-selection inspection.

For each registration the checker must:

1. validate the exact candidate-registry schema and byte conventions;
2. validate `case_id`, source/specimen hashes, offline-endpoint hashes and evaluation-definition hash;
3. compute both arm bindings and the order-independent pair fingerprint;
4. apply the support-requirement-status rule without imputing `UNKNOWN` to 1;
5. check recorded Boolean/status fields for M1 representability, A1 availability, I1 compatibility, offline endpoint availability and no consequential execution;
6. require an explicit attestation that computed CFC output, computed RIDI output, correctness and desired asymmetry were **not used** to decide eligibility;
7. detect duplicate pair fingerprints, including reversed A/B registrations;
8. write an immutable eligibility record containing:
   - `case_id`;
   - pair fingerprint;
   - `ACCEPT` or `REJECT`;
   - ordered reason codes;
   - source registry row hash;
   - checker version/hash;
9. produce the eligible-pool rows only from `ACCEPT` records;
10. preserve all rejected registrations and rejection reasons in a separate audit log.

The checker may calculate hashes and validate declared pre-selection facts. It may **not** execute CFC, execute RIDI, compare the A/B downstream verdicts for equivalence, inspect hidden correctness, or rank candidates by scientific interest.

A manual override is not permitted. Any checker defect requires a versioned reset and re-evaluation of all registrations before pool freeze.

## 5. Explicit non-exclusions

The following do **not** by themselves exclude a case:

- missing authority that frozen M1/A1 can honestly represent as NOT_SUPPLIED;
- expected possibility of CFC BLOCK;
- expected possibility of RIDI PASS or FAIL;
- unknown correctness;
- a null, negative or NOT EVALUABLE eventual substantive result, provided the case was eligible under the frozen pre-selection rules;
- one source/arm shared with another otherwise distinct A/B pair.

## 6. Candidate-registry and frozen-pool formats

### Candidate registry

Candidate registrations are stored as exact UTF-8, LF-terminated TSV and sorted lexicographically by `case_id`.

Required columns:

`case_id	source_a_sha256	offline_endpoint_a_sha256	source_ref_a	source_b_sha256	offline_endpoint_b_sha256	source_ref_b	evaluation_definition_id	evaluation_definition_sha256	original_support_requirement_status	offline_endpoint_present	m1_representable	a1_preexisting_authority_available	i1_compatible	no_consequential_execution	prior_public_exposure	outcome_independent_eligibility_attestation	eligibility_rationale`

This registry is an input to the frozen mechanical eligibility checker; it is **not** the eligible pool.

### Eligible pool

The checker emits an exact UTF-8, LF-terminated `eligible_pool.tsv`, sorted lexicographically by `case_id`.

Required columns:

`case_id	pair_fingerprint	source_a_sha256	offline_endpoint_a_sha256	source_ref_a	source_b_sha256	offline_endpoint_b_sha256	source_ref_b	evaluation_definition_id	evaluation_definition_sha256	original_support_requirement_status	prior_public_exposure	eligibility_rationale`

The exact file SHA-256 identifies the frozen pool.

## 7. Preserved eligibility audit

Before pool freeze, preserve:

- exact candidate registry bytes + SHA-256;
- exact checker bytes/version + SHA-256;
- full eligibility audit log with every ACCEPT/REJECT and reason code;
- exact eligible pool bytes + SHA-256;
- duplicate/conflict log, if non-empty.

No rejected registration may be deleted from the audit record merely because it was inconvenient or scientifically uninteresting.

This draft does not contain any candidate IDs, pool rows, selection seeds or substantive results.
