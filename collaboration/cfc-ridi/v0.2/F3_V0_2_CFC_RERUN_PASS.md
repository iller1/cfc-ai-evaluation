# CFC–RIDI v0.2 — CFC F3 Representation-Only Adversarial Rerun PASS on F2 v0.2

Status: **CFC F3 PASS / PENDING INDEPENDENT RIDI RERUN**  
Authority: signed F0 feasibility workplan  
F2 baseline: `CFC-RIDI-F2-ADAPTER-v0.2`, bilaterally exact-hash closed  
F3 criteria: bilaterally frozen R1, unchanged

## 1. Frozen F2 v0.2 baseline

Exact F2 candidate commit:

`930d7b0119159eaedbaf947691d9510b4c61d81c`

Primary adapter SHA-256:

`15b7d01787237b2e5f0d1ca106c4e84aaf1976a2512179c79c458fe3d80e634b`

F2 v0.2 bilateral closure commit:

`aa5dda08d32b57a62c1f014e97b3c415eda29ae6`

Freeze ref:

`freeze/cfc-ridi-v0.2-f2-adapter-v0.2`

## 2. Frozen F3 criteria

Criteria SHA-256:

`f9640dbaec55a2b381a159825fe27a9e87502b75b20bbfbcf4382ca44cd887a2`

No F3 criterion was changed or weakened after the prior T05 failure.

## 3. Runnable F3 rerun identity

Exact rerun commit:

`c14dc6030f80f036757214627b011385e31768f7`

Freeze ref:

`freeze/cfc-ridi-v0.2-f3-r1-pass-v02`

The previously failed F3 R1 state remains separately frozen at:

`freeze/cfc-ridi-v0.2-f3-suite-r1-failed`

The rerun uses the same T01–T15 criteria and test meanings. Mechanical harness changes were limited to binding the unchanged tests to the new frozen F2 v0.2 baseline and supplying the root `neutral_arm_binding` required by v0.2.

### fixtures.py
- bytes: `19991`
- SHA-256: `b0349b70ac6ef4ea35e19589e05da5e71a45e885a0dd980fa16b8226d1420d4f`
- Git blob: `f23ae05b6ce166d1f12104fe12d14c4a902fca14`

### probe_f3.py
- bytes: `4688`
- SHA-256: `777355fafd140d498c96d7abe86d7697f9c639640c7a7e22793c709b62b2bed7`
- Git blob: `1b1e4bd26b9a6444ec676b7d788bc0431f9fc4e4`

### run_f3.py
- bytes: `22606`
- SHA-256: `3ac4cf728fabe0f8c846321327c9ddd5794883efba741c4ff7f4138e7a2952fe`
- Git blob: `7f1fbac49f0572f3a58badddc9e7cb0ed0b9f880`

### workflow
`.github/workflows/cfc-ridi-f3-suite-r1.yml`
- bytes: `2775`
- SHA-256: `719f2bd3c59a85e0c14e7d7833e685d5ede69c4dbfda1427ed1c9bda896771b4`
- Git blob: `7f306d549a547c14c45f6a44664d22618230df15`

## 4. Final CFC run

GitHub Actions workflow:

`CFC-RIDI F3 Suite R1`

Run ID:

`36889271912`

Job ID:

`110460449077`

Run head:

`c14dc6030f80f036757214627b011385e31768f7`

Result:

`success`

The run first independently rechecked the exact frozen F2 v0.2 component identities, installed the exact frozen Anchor wheel, and reproduced the F2 v0.2 representation baseline:

`PASS 10/10`

It then executed the complete frozen F3 suite.

## 5. F3 result

Tests:

- total: `15`
- PASS: `15`
- FAIL: `0`

All tests passed:

`T01, T02, T03, T04, T05, T06, T07, T08, T09, T10, T11, T12, T13, T14, T15`

Overall result:

`F3_REPRESENTATION_ONLY_ADVERSARIAL_SUITE_PASS`

The previously failing T05 now passes under the unchanged criterion because the foreign case/arm resolved-state package is rejected by the v0.2 root neutral-arm binding before Controller evaluation.

## 6. Exact result artifact

GitHub Actions artifact ID:

`11176600720`

Artifact name:

`cfc-ridi-f3-r1-result`

Artifact ZIP:

- bytes: `8773`
- SHA-256: `fe9554c8dec791b50ebdab77fbb0bf555553ae3514e051081e3f6b320092506b`

Contained result:

`F3_RESULTS.json`

- bytes: `69494`
- SHA-256: `13dfe40f255e0398b971e90b3ea10cae164205ae5b345d7980c77b50a7b80e7b`

The contained JSON reports:

- `tests_total = 15`
- `tests_passed = 15`
- `tests_failed = 0`
- `overall_status = F3_REPRESENTATION_ONLY_ADVERSARIAL_SUITE_PASS`

## 7. CFC decision

CFC records:

`F3_REPRESENTATION_ONLY_ADVERSARIAL_SUITE_PASS`

for the exact F2 adapter v0.2 identity above.

This is CFC-side F3 acceptance only.

RIDI must independently rerun/review the exact frozen rerun identity and result before bilateral F3 closure.

No F4 progression is authorized until RIDI independently confirms the same F3 result.

The prior v0.1 F3 NO-GO remains retained as historical evidence and is not overwritten.
