# CFC Integration Layer v0.4 RC

Experimental developer integration layer over frozen `CFC Anchor 0.2.90rc1`.

## What this RC adds

- installable Python integration package;
- simplified Python API;
- JSON / CLI execution;
- `cfc-doctor` integrity smoke check;
- `cfc-demo` first-decision path;
- explicit declarative business-data mapping;
- bounded mapping rules for boolean, enum, expiry-date, and exact-scope fields;
- human-readable decision/state/reason output;
- raw frozen-controller result retained for audit.

## Example

```python
from cfc_integration import CFC
result = CFC.check("APPROVED", ["verified", "missing"], required=2)
print(result)
```

Expected semantic class:

```text
STOP | ... | required evidence unresolved or missing
```

## RC validation

- manifest: PASS — 31 entries
- frozen Anchor identity: PASS
- clean virtual environment: PASS
- offline wheel install: PASS
- `cfc-doctor`: PASS
- `cfc-demo`: PASS
- mapping ALLOW/STOP examples: PASS
- integration regression: 11/11 PASS

## Artifact identities

`CFC_INTEGRATION_LAYER_v0.4.zip`

SHA-256:

`984c45a153609ef5a7b294e2df0ccb293a5dc962ee846bd25de90bdc277cf9db`

`cfc_integration-0.4.0-py3-none-any.whl`

SHA-256:

`d46337f34b571ba282b4fe8d416e06360dadc742c247070016a16783db696e4a`

Frozen Anchor wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

## Important

This is a release candidate, not a production release.

External usability has not yet been verified.

Open gates:

- `TIME_TO_FIRST_CFC_DECISION <= 15 minutes`
- `TIME_TO_FIRST_DOMAIN_MAPPING <= 30 minutes`

The RC does not claim automatic contract understanding, legal accuracy, regulatory compliance, commercial ROI, or production readiness.
