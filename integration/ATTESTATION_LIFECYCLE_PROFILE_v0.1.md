# CFC Attestation Lifecycle Integration Profile v0.1

Status: **EXPERIMENTAL / NON-FROZEN INTEGRATION POLICY**

Date: 2026-09-13

This profile is **not part of frozen CFC Anchor 0.2.90rc1**, **not part of Operator Wrapper v1.23**, and does not modify or reinterpret either frozen baseline.

It defines a host-side integration policy for independence attestations after adversarial review identified lifecycle cases that are only partially covered by the current public contract.

## 1. Purpose

The profile prevents a host workflow from treating an independence attestation as currently usable merely because it was accepted at an earlier time.

Passing this profile means only:

`ELIGIBLE_FOR_ANCHOR`

It does **not** mean:

`ALLOW`

The frozen controller must still evaluate the applicable closure conditions, and all other required evidence/state conditions must still be satisfied.

## 2. Boundary

The host is responsible for enforcing this profile before each decision that relies on an independence attestation.

The frozen Anchor remains unchanged. Raw Anchor output must remain available for audit and must not be rewritten by the host, wrapper, or demonstrator.

This profile does not claim that the frozen Anchor itself guarantees decision-time attestation freshness, revocation handling, replay resistance, or trust-root authenticity.

## 3. Required decision-time checks

An attestation may be treated as `ELIGIBLE_FOR_ANCHOR` only when all required checks below succeed at the current decision time.

### 3.1 Temporal validity

The host MUST evaluate the attestation at `decision_time`, not only at installation or issuance time.

Required fields:

- `issued_at`
- `valid_from`
- `valid_to`

Required condition:

`valid_from <= decision_time <= valid_to`

If `ttl_seconds` is present, the host MUST also require:

`decision_time <= issued_at + ttl_seconds`

Expired or not-yet-valid attestations produce `STOP`.

### 3.2 Exact scope binding

The host MUST compare the attestation against the current decision context using exact bindings for the fields declared by the profile:

- `scope_id`
- `purpose_id`
- `resource_id`
- `audience_id`

Any explicit mismatch produces `STOP`.

A missing binding needed by the current profile produces `UNRESOLVED`.

### 3.3 Revocation

The host MUST obtain a revocation status for the attestation before relying on it.

- known revoked -> `STOP`
- known good and sufficiently fresh -> continue
- missing, unknown, or stale revocation status -> `UNRESOLVED`

The maximum acceptable age of the revocation check is a host policy parameter and MUST be recorded with the decision.

A negative revalidation MUST invalidate any cached host authorization derived from the earlier attestation. The host MUST NOT continue a workflow using the earlier cached permission after revalidation fails.

### 3.4 Replay resistance

An attestation MUST be bound to the current decision by at least one accepted anti-replay mechanism:

1. exact `decision_id` binding; or
2. exact `session_id` binding plus a nonce that has not previously been consumed.

If neither mechanism is available, replay resistance is `UNRESOLVED`.

A reused nonce produces `STOP`.

Nonce consumption MUST be committed atomically with the decision that uses it.

### 3.5 Authenticity and issuer trust

Cryptographic signature verification or equivalent authenticity verification is an upstream dependency.

The host MUST require an explicit authenticity result:

- `verified` -> continue
- `invalid` -> `STOP`
- missing / unknown -> `UNRESOLVED`

The host MUST also evaluate whether the issuer is within the configured trust set for the current purpose.

This profile does not recursively prove the trustworthiness of every trust root. The configured trust-root set is the explicit trust boundary.

### 3.6 Failure domains and common-mode trust

Two attestations MUST NOT be counted as independent merely because there are two records or two signatures.

For a set of attestations to satisfy an independence requirement, the host MUST resolve both:

- `failure_domain_id`
- `root_id`

Known equality of either failure domain or root across attestations means the set MUST NOT be treated as independent and produces `STOP` for an independence requirement.

Missing or unresolved failure-domain/root information produces `UNRESOLVED`.

A known compromised root produces `STOP` for every attestation that depends on that root.

### 3.7 Decision-time snapshot

Every decision relying on an attestation SHOULD record at minimum:

- `decision_time`
- `decision_id`
- `session_id`
- `case_id`
- attestation IDs
- issuer IDs
- validity interval
- revocation status and `revocation_checked_at`
- scope/purpose/resource/audience bindings
- failure-domain IDs
- root IDs
- nonce(s) consumed, if applicable
- host profile version
- raw frozen-controller result

## 4. Threat model

The adversary may:

- submit an old but once-valid attestation;
- submit an attestation for the wrong scope, purpose, resource, or audience;
- replay a previously accepted attestation in another session or decision;
- continue presenting an attestation after revocation;
- control or compromise one attestation source;
- present multiple attestations that share one failure domain or root of trust;
- present a forged attestation whose authenticity has not actually been verified;
- exploit host caching after a failed revalidation.

The adversary is **not assumed** to be unable to compromise a configured root of trust. If root compromise is known, the profile fails closed for that root. If root status is unknown, the profile cannot prove root integrity and treats the configured root set as an explicit trust boundary.

## 5. Breaker success criterion

A real breaker success is:

`host + frozen controller returns ALLOW / closure`

when the predeclared test conditions require:

`STOP / UNRESOLVED`

A different reason string, message wording, or internal path is not sufficient.

Expected results MUST NOT be changed after observing the actual result.

## 6. Layer attribution

Failures are attributed using the following rule:

- **Anchor/controller**: the frozen controller itself returns closure contrary to a guarantee actually present in its frozen contract.
- **Operator Wrapper**: the wrapper violates a guarantee actually present in the frozen wrapper contract.
- **Demonstrator**: presentation/replay changes or repairs the underlying controller decision.
- **Mapping/integration**: host mapping or orchestration incorrectly treats an attestation as eligible.
- **Upstream trust mechanism**: signature verification, issuer trust, revocation source, root compromise status, or another fact required by this profile is unavailable or invalid.

No issue should be called a controller vulnerability unless there is a reproducible false `ALLOW` against an established frozen-controller guarantee.

## 7. Minimal acceptance properties

The profile is acceptable for pilot use only if all of the following hold:

1. expired attestation -> `STOP`
2. not-yet-valid attestation -> `STOP`
3. wrong-scope/purpose/resource/audience attestation -> `STOP`
4. revoked-before-expiry attestation -> `STOP`
5. replayed nonce -> `STOP`
6. no usable anti-replay binding -> `UNRESOLVED`
7. two attestations sharing one failure domain -> not independent
8. two attestations sharing one root -> not independent
9. unknown root/failure-domain relation -> `UNRESOLVED`
10. known compromised root -> `STOP`
11. failed revalidation invalidates cached host authorization
12. valid/current/right-scope attestation -> only `ELIGIBLE_FOR_ANCHOR`; final closure still depends on the frozen controller and all remaining closure conditions

## 8. Publication language

A bounded external finding may state that adversarial testing exposed an **attestation lifecycle integration risk** under a predeclared decision-time freshness policy.

Until the frozen contract itself is shown to require decision-time attestation validity, publication MUST NOT claim that the finding proves a defect in CFC Anchor 0.2.90rc1.
