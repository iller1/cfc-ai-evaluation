# CFC — AI Evaluation & Control Framework

## CFC Demonstrator

A local executable demonstrator is available for the frozen CFC execution track:

**CFC Demonstrator v1.0-rc1**

`INPUT / EVIDENCE STATE → MODEL CONCLUSION → CFC CHECK → ALLOW / STOP + CLAIM STATE + REASON`

The demonstrator includes:

* 10 executable representative cases
* live replay against the frozen controller
* Reviewer Mode live A/B experiment
* bounded Custom Case Builder
* SHA-256 verification
* offline release self-check
* no pip requirement
* no network requirement

### Links

* [Open the demonstrator source](https://github.com/iller1/cfc-ai-evaluation/tree/main/demonstrator)
* [Download CFC Demonstrator v1.0-rc1](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0-rc1)

The demonstrator is an external layer over the frozen CFC Anchor `0.2.90rc1` public API.

Operator Wrapper v1.23 remains byte-for-byte frozen and separate.
