# CFC — AI Evaluation & Control Framework

CFC is an experimental framework focused on one narrow reliability question:

> Does the available evidence and current system state actually justify a definitive conclusion?

It is not presented as a general AI-safety system, a production-ready enterprise control layer, or a replacement for model evaluation, factuality testing, or domain review.

## CFC Demonstrator v1.0

The final public Demonstrator v1.0 release is published over the frozen CFC execution track.

`INPUT / EVIDENCE STATE → MODEL CONCLUSION → CFC CHECK → ALLOW / STOP + CLAIM STATE + REASON`

Final validation before publication included:

- manifest: 108/108 files PASS
- preset replay: 10/10 PASS
- custom regression: PASS
- reviewer A/B: PASS
- frozen CFC Anchor wheel identity: PASS

The final release asset is:

`CFC_DEMONSTRATOR_v1.0.zip`

SHA-256:

`d4c46d435994a291cf09cc9ca880be06bd4271c83e2875f9fbf3f887bd08ae28`

### Demonstrator links

- [Final CFC Demonstrator v1.0 release](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0)
- [Demonstrator source](demonstrator/)
- [Reconciliation status](demonstrator/RECONCILIATION_STATUS.md)
- [Historical RC1 release](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0-rc1)

The Demonstrator is an external layer over frozen CFC Anchor `0.2.90rc1`.

Operator Wrapper v1.23 remains byte-for-byte frozen and separate.

## Integration Layer — experimental productization track

A separate experimental integration layer is being developed over the frozen Anchor to reduce first-use friction without modifying controller behavior.

Current release candidate:

`CFC Integration Layer v0.4 RC`

The RC provides:

- installable Python integration package
- three-line Python API
- CLI / JSON input
- `cfc-doctor` integrity smoke check
- `cfc-demo` first-decision path
- bounded declarative mapping from explicit business fields to normalized evidence states
- access to the raw frozen-controller result for audit

This integration layer is **not part of the frozen CFC Anchor**. External usability remains unverified until unfamiliar developers complete the prepared timed tests.

See [integration/](integration/) for the RC status and claim boundary.

## Validation boundary

Internal engineering evidence, controlled causal evidence, independent review, external replication, and product usability are separate evidence classes and must not be conflated.
