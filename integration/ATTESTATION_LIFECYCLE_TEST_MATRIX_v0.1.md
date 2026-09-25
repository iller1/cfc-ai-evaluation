# CFC Attestation Lifecycle Integration Test Matrix v0.1

Status: **PREDECLARED EXTERNAL / HOST-SIDE TEST PLAN**

This matrix tests `ATTESTATION_LIFECYCLE_PROFILE_v0.1`. It does not alter the frozen controller and does not redefine frozen Anchor guarantees.

## Breaker criterion

Breaker success requires actual closure/`ALLOW` where the predeclared condition requires `STOP` or `UNRESOLVED`.

Reason-string differences alone do not count.

## Core matrix

| Test ID | Input state | Threat assumption | Expected host result | Layer under test |
|---|---|---|---|---|
| ATL-001 | valid at install, expired at decision | attacker reuses once-valid attestation | STOP | integration lifecycle |
| ATL-002 | `valid_from` is after decision time | attacker preplays future attestation | STOP | integration lifecycle |
| ATL-003 | scope mismatch | attacker reuses attestation for another scope | STOP | mapping/integration |
| ATL-004 | purpose mismatch | attacker repurposes valid credential | STOP | mapping/integration |
| ATL-005 | resource mismatch | attacker moves credential to another resource | STOP | mapping/integration |
| ATL-006 | audience mismatch | attacker uses credential at another consumer | STOP | mapping/integration |
| ATL-007 | revoked before expiry | attacker continues using revoked credential | STOP | upstream revocation + integration |
| ATL-008 | revocation status too stale | current revocation state cannot be established | UNRESOLVED | upstream revocation |
| ATL-009 | replayed consumed nonce | attacker replays in same/another decision | STOP | integration anti-replay |
| ATL-010 | no decision binding and no usable nonce | replay resistance cannot be established | UNRESOLVED | integration anti-replay |
| ATL-011 | two attestations, same root | apparent multiplicity hides common trust root | STOP for independence claim | provenance/common-mode mapping |
| ATL-012 | two attestations, same failure domain | one compromise may affect both | STOP for independence claim | source failure domain |
| ATL-013 | root/failure-domain relation missing | independence cannot be established | UNRESOLVED | upstream provenance |
| ATL-014 | known compromised root | attacker controls configured trust root | STOP | upstream trust boundary |
| ATL-015 | authenticity unknown | forged credential may be present | UNRESOLVED | upstream authenticity |
| ATL-016 | authenticity invalid | forgery is established | STOP | upstream authenticity |
| ATL-017 | issuer outside configured trust set | valid signature from untrusted issuer | STOP | trust configuration |
| ATL-018 | current, right-scope, non-revoked, replay-safe, trusted | no lifecycle fault | ELIGIBLE_FOR_ANCHOR only | integration gate |
| ATL-019 | two current attestations, distinct roots and failure domains | no known common-mode relation | ELIGIBLE_FOR_ANCHOR only | independence gate |
| ATL-020 | failed revalidation after earlier success | host attempts to continue using cached permission | STOP and cached permission invalidated | host orchestration |
| ATL-021 | decision-bound attestation reused after decision ID was finalized | attacker replays a previously accepted decision-bound credential | STOP | integration anti-replay |
| ATL-022 | same `attestation_id` supplied twice with apparent distinct lineage | attacker duplicates one logical credential to satisfy a count threshold | STOP for independence claim | identity / independence mapping |
| ATL-023 | case mismatch | attacker moves a valid attestation into another case | STOP | mapping/integration |

## Required result record

Each executed case must record:

- test ID
- input state
- threat assumption
- expected result fixed before execution
- actual integration-guard result
- actual frozen-controller result, if the guard allows the controller to be called
- PASS / FAIL
- exact reason
- component attribution: controller / wrapper / demonstrator / mapping / integration / upstream trust
- immutable reproducer reference for any false closure

## Interpretation rule

`ELIGIBLE_FOR_ANCHOR` means the lifecycle/trust precondition passed. It is not a final authorization and must not be reported as `ALLOW`.

A controller call SHOULD NOT occur when the integration guard returns `STOP` or `UNRESOLVED` under this profile. If an experiment intentionally bypasses that rule to probe the frozen Anchor, the bypass must be labeled as an adversarial harness action, not normal integration behavior.
