# CFC Integration Layer v0.4 — Release Candidate Record

Status: **RC VALIDATION PASS / EXTERNAL USABILITY NOT YET VERIFIED**

## Local RC artifacts

Integration package:

`CFC_INTEGRATION_LAYER_v0.4.zip`

SHA-256:

`984c45a153609ef5a7b294e2df0ccb293a5dc962ee846bd25de90bdc277cf9db`

Installable integration wheel:

`cfc_integration-0.4.0-py3-none-any.whl`

SHA-256:

`d46337f34b571ba282b4fe8d416e06360dadc742c247070016a16783db696e4a`

Frozen CFC Anchor wheel embedded by the integration package:

`cfc_anchor-0.2.90rc1-py3-none-any.whl`

SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

Frozen engine SHA-256:

`77a7547c02ce4aac3d3abc759bbd266f4251de9149da2308454527c7f2dea5c0`

RC audit wrapper:

`CFC_INTEGRATION_LAYER_v0.4_RC.zip`

SHA-256:

`7770a8e466045415b776c849bbd654da875f8f3d863ab94ff319bfef4dbf8ab4`

## RC validation

- internal manifest: PASS — 31 entries
- frozen Anchor identity: PASS
- fresh Python virtual environment: PASS
- offline wheel installation: PASS
- `cfc-doctor`: PASS
- `cfc-demo`: PASS
- mapping ALLOW example: PASS
- mapping STOP example: PASS
- integration regression: 11/11 PASS

## Freeze rule

The v0.4 RC is not to be silently modified during external usability testing.

If external testers identify a defect or material integration problem, the fix belongs in a successor candidate such as v0.5, with the v0.4 result preserved historically.

## Publication state

The text status and RC identity are recorded in the public repository.

The binary Integration Layer release asset has **not** yet been declared a final public GitHub release in this record. Do not describe `v0.4 RC` as externally validated or production-ready.
