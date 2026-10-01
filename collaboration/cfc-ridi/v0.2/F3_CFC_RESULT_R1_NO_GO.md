# CFC–RIDI v0.2 — CFC F3 Representation-Only Adversarial Result R1

Status: **F3 NO-GO / REPRESENTATION INVALID / PENDING INDEPENDENT RIDI RERUN**  
Authority: signed F0 feasibility workplan  
F3 criteria: bilaterally frozen R1  
F2 baseline under test: immutable `CFC-RIDI-F2-ADAPTER-v0.1`

## 1. Frozen inputs

F2 adapter commit:

`4167783eb48e1a1677107cb1359ad9b2f890017f`

F2 adapter SHA-256:

`4b975fda6242c9a7e33d0d692705ef6fe82683dbf2bddefc0345c2e5504b480a`

F3 criteria SHA-256:

`f9640dbaec55a2b381a159825fe27a9e87502b75b20bbfbcf4382ca44cd887a2`

No F2 adapter byte was modified during F3.

## 2. Exact runnable suite

Frozen CFC suite commit:

`657fb9a0b2b8e1d384cfdee7119fc190c628d4c7`

CFC freeze ref:

`freeze/cfc-ridi-v0.2-f3-suite-r1-failed`

Exact suite components:

### fixtures.py
- bytes: `19906`
- SHA-256: `7dd0fbd28f9c96ab9263dd437d6a766ac9134b334d18ec899d9e002310a9b0ed`
- Git blob: `de90a4bf572cbf73e9c27abf037afa1a4fc709d0`

### probe_f3.py
- bytes: `4688`
- SHA-256: `777355fafd140d498c96d7abe86d7697f9c639640c7a7e22793c709b62b2bed7`
- Git blob: `1b1e4bd26b9a6444ec676b7d788bc0431f9fc4e4`

### run_f3.py
- bytes: `22512`
- SHA-256: `fa478d57a93f9c0477f740f7f86929f5bdcc05b3efd2b764f9a392d293c5853d`
- Git blob: `1a0c74aaffcc5edd1d9bc369a67a2c316941d2d5`

### workflow
`.github/workflows/cfc-ridi-f3-suite-r1.yml`
- bytes: `2730`
- SHA-256: `6fd5b3ed185ed4079f3c39b84df470d6e4ca7f2fd96c217ac663d12622234971`
- Git blob: `143d815d073914e1532eeea578d39cc9f7fe091d`

## 3. Exact final run

GitHub Actions workflow:

`CFC-RIDI F3 Suite R1`

Run ID:

`36879596864`

Job ID:

`110427668953`

The run independently rechecked the frozen F2 component hashes and reproduced the F2 representation baseline `PASS 8/8` before running F3.

Complete result artifact:

- artifact ID: `11171210778`
- artifact name: `cfc-ridi-f3-r1-result`
- ZIP bytes: `8870`
- ZIP SHA-256: `ddeade58f7902fa9a8a6c12105d0280831d2f2a4bac6f54b6934b330ffd2ee3a`

Contained result file:

`F3_RESULTS.json`

- bytes: `76129`
- SHA-256: `0c5dbdb3071e69988f76dd6573c1e5a8c43edfaf85716a21355d87a6e1febf14`

## 4. Final result

Tests:

- total: `15`
- PASS: `14`
- FAIL: `1`

Passing tests:

`T01, T02, T03, T04, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15`

Failing test:

`F3-T05 — Cross-case / cross-arm resolved-state substitution`

Exact finding:

`mutation was silently ignored; diagnostic result identical to control`

The control and mutation were executed separately in fresh processes. The mutation applied a resolved-state package prepared for one case/arm to a different case/arm while preserving superficially compatible passage-level bindings.

The frozen adapter did not reject the foreign case/arm package and did not produce a mutation-attributable diagnostic difference.

Under the bilaterally frozen T05 criterion, this is a FAIL.

## 5. CFC F3 decision

Result:

`F3_NO_GO_REPRESENTATION_INVALID`

This result applies only to the exact F2 adapter v0.1 identity above.

It does not alter or invalidate the frozen CFC Anchor.

It does not reopen F0, F1, or the neutral-schema exact-hash closure.

It does not establish any F4/F5 result.

## 6. Required next action under frozen criteria

The failing F2 adapter v0.1 is retained unchanged.

No F4 progression is authorized.

A correction may be attempted only as a **new versioned F2 adapter candidate**, with the frozen F1 interface, neutral schema and F3 criteria unchanged.

Any repaired adapter requires:

1. new exact F2 candidate identity/hash;
2. complete independent RIDI F2 review and bilateral F2 acceptance;
3. complete rerun of all F3 T01–T15 under the already frozen criteria.

Before repair, RIDI independently reruns/reviews this exact F3 suite/result.

Failure is retained; criteria are not weakened.
