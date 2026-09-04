# CFC — AI Evaluation & Control Framework

## CFC Demonstrator

A reconciled and locally validated CFC Demonstrator v1.0 source/package candidate is now present on `main` over the frozen CFC execution track.

`INPUT / EVIDENCE STATE → MODEL CONCLUSION → CFC CHECK → ALLOW / STOP + CLAIM STATE + REASON`

The earlier RC1 repository/release provenance mismatch has been resolved. Exact CASE_09 and CASE_10 bytes were recovered from the preserved RC1 release asset, verified against preserved SHA-256 anchors, and restored to the reconciled source tree. The final v1.0 candidate contains CASE_01–CASE_10 and a freshly generated SHA-256 manifest.

Final candidate validation passed:

* manifest: 108/108 files
* preset replay: 10/10
* custom regression: PASS
* reviewer A/B: PASS
* frozen CFC Anchor wheel identity: PASS

The demonstrator also includes:

* live replay against the frozen controller
* Reviewer Mode live A/B experiment
* bounded Custom Case Builder
* SHA-256 verification
* no pip requirement
* no network requirement

### Links

* [Open the demonstrator source](https://github.com/iller1/cfc-ai-evaluation/tree/main/demonstrator)
* [Historical CFC Demonstrator v1.0-rc1 release](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0-rc1)
* [Read reconciliation status](demonstrator/RECONCILIATION_STATUS.md)

The final `cfc-demonstrator-v1.0` tag/release publication is still pending. Until that publication step is completed, the validated `main` source and locally frozen v1.0 package candidate are the current finalization artifacts.

The demonstrator is an external layer over the frozen CFC Anchor `0.2.90rc1` public API.

Operator Wrapper v1.23 remains byte-for-byte frozen and separate.
