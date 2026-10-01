# CFC–RIDI v0.2 — CFC F3 Representation-Only Adversarial Result R1

Status: **CFC F3 NO-GO / PENDING INDEPENDENT RIDI RERUN-REVIEW**  
Authority: signed F0 feasibility workplan  
F3 criteria: bilaterally frozen R1  
F2 baseline: immutable `CFC-RIDI-F2-ADAPTER-v0.1`

## 1. Frozen criteria

F3 criteria SHA-256:

`f9640dbaec55a2b381a159825fe27a9e87502b75b20bbfbcf4382ca44cd887a2`

RIDI bilateral-freeze commit:

`ff86170104d44e09e1efb503aabe754c2341187b`

No criterion was changed after observing the F3 result.

## 2. Exact F2 baseline under test

Accepted F2 adapter commit:

`4167783eb48e1a1677107cb1359ad9b2f890017f`

Primary adapter SHA-256:

`4b975fda6242c9a7e33d0d692705ef6fe82683dbf2bddefc0345c2e5504b480a`

The F2 adapter bytes were not modified during F3.

## 3. Exact F3 suite identity

Final CFC suite commit:

`1d0f3fb5daa89da86700688e2e96a927d0dae20c`

Immutable CFC freeze reference:

`freeze/cfc-ridi-v0.2-f3-suite-r1-no-go`

Suite component Git blobs:

- `collaboration/cfc-ridi/v0.2/f3_suite/fixtures.py`
  - Git blob: `de90a4bf572cbf73e9c27abf037afa1a4fc709d0`
- `collaboration/cfc-ridi/v0.2/f3_suite/run_f3.py`
  - Git blob: `26f628651388350093ecccb29c06a31a73df9a51`
- `collaboration/cfc-ridi/v0.2/f3_suite/probe_f3.py`
  - Git blob: `1b1e4bd26b9a6444ec676b7d788bc0431f9fc4e4`
- `.github/workflows/cfc-ridi-f3-suite-r1.yml`
  - Git blob: `143d815d073914e1532eeea578d39cc9f7fe091d`

The suite runs each top-level F3 test in a fresh process. For controller-level mutation tests, control and mutation probes also execute in separate fresh processes with matching fixture identities, so mutation attribution is not inferred from global-registry contamination.

## 4. Exact CFC execution

GitHub Actions run:

`36879268412`

Job:

`110426566251`

Run commit:

`1d0f3fb5daa89da86700688e2e96a927d0dae20c`

The workflow independently rechecked the exact frozen F2 artifacts and exact Anchor wheel before F3 execution.

F2 representation baseline reproduced:

`PASS 8/8`

## 5. Exact result artifact

Actions artifact ID:

`11169934794`

Artifact name:

`cfc-ridi-f3-r1-result`

Artifact ZIP SHA-256:

`85984427f359c5ae75cc8f79103e06b1d6727a4216d71bdb3f18c9ea4df4360c`

Contained file:

`F3_RESULTS.json`

- bytes: `76129`
- SHA-256: `0c5dbdb3071e69988f76dd6573c1e5a8c43edfaf85716a21355d87a6e1febf14`

## 6. Result

`F3_NO_GO_REPRESENTATION_INVALID`

Summary:

- tests total: `15`
- PASS: `14`
- FAIL: `1`

Passing tests:

`F3-T01, T02, T03, T04, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15`

Failing test:

`F3-T05 — Cross-case / cross-arm resolved-state substitution`

## 7. T05 finding

T05 constructs two valid neutral arms with the same passage-level neutral bindings but different:

- `case_id`; and
- `arm`.

A resolved-state package is constructed for one case/arm.

The final attribution harness executes:

1. a control using that resolved state with its matching case/arm; and
2. the mutation using the same resolved state with the foreign case/arm.

Both executions use separate fresh processes and matching fixture identities.

Observed result:

`mutation diagnostic result == control diagnostic result`

F3 classification:

`mutation was silently ignored; diagnostic result identical to control`

Therefore the frozen adapter v0.1 does not, under this tested representation, distinguish the foreign case/arm substitution before or during the observable controller path.

This is sufficient to fail frozen criterion F3-T05.

This finding is bounded to the exact tested F2 adapter and F3 fixture/state construction. It is not a claim about all possible CFC integrations.

## 8. Required action under frozen F0/F3 rules

The exact accepted F2 adapter v0.1 is retained unchanged.

It must not be repaired under the same F2 identity.

F3 does not proceed to F4.

A mechanical repair may be proposed only as a **new versioned F2 candidate**, under the same:

- F1 controller/interface;
- neutral schema R1;
- frozen F3 criteria R1.

Any adapter-code repair requires:

1. new F2 adapter identity/version/hash;
2. full CFC-side F2 publication;
3. independent RIDI F2 review and bilateral exact-hash acceptance;
4. complete F3 T01–T15 rerun under the unchanged frozen criteria.

No criterion is weakened.

No F4/F5 conclusion is implied.

## 9. CFC decision

Current CFC status:

`F3_NO_GO_REPRESENTATION_INVALID`

pending independent RIDI reproduction/review of the exact suite and result above.

**Failure is evidence. Do not normalize it away.**
