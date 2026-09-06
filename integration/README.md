# CFC Integration Layer

Status: **EXPERIMENTAL RELEASE CANDIDATE**

Current candidate: `v0.4 RC`

The Integration Layer is a separate productization layer over frozen `CFC Anchor 0.2.90rc1`.

It does **not** modify the frozen controller.

## Purpose

Reduce first-use integration friction while preserving explicit evidence-state mapping and access to the frozen controller audit result.

Target developer path:

```text
company workflow
→ explicit mapping
→ CFC Integration Layer
→ frozen CFC Anchor 0.2.90rc1
→ ALLOW / STOP + state + reason + raw audit result
```

## Developer-facing interface

Three-line Python example:

```python
from cfc_integration import CFC
result = CFC.check("APPROVED", ["verified", "missing"], required=2)
print(result)
```

The RC also provides:

```bash
cfc-doctor
cfc-demo
cfc-check case.json
cfc-map policy.json record.json
```

## Normalized evidence vocabulary in the bounded RC

- `verified`
- `negative`
- `missing`
- `stale`
- expected / wrong scope
- explicit independence and lineage controls

The declarative mapper currently supports bounded explicit rule types such as boolean fields, enums, expiry dates, and exact scope equality.

## Important boundary

The Integration Layer does not automatically understand contracts, law, business policy, or raw enterprise data.

A host workflow still needs an explicit mapping from its own evidence semantics to normalized CFC inputs.

No production-readiness, legal-accuracy, regulatory-compliance, commercial-ROI, or universal plug-and-play claim is made.

## External usability gates

These remain open:

- `TIME_TO_FIRST_CFC_DECISION <= 15 minutes` — **NOT YET VERIFIED**
- `TIME_TO_FIRST_DOMAIN_MAPPING <= 30 minutes` — **NOT YET VERIFIED**

Both require previously unfamiliar external developers.

See:

- [Release candidate record](RELEASE_CANDIDATE.md)
- [Claim boundary](BOUNDARY.md)
- [External usability tests](USABILITY_TESTS.md)
