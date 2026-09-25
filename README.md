# CFC — AI Evaluation & Control Framework

CFC is an experimental framework focused on one narrow reliability question:

> Does the available evidence and current system state actually justify a definitive conclusion?

It is not presented as a general AI-safety system, a production-ready enterprise control layer, or a replacement for model evaluation, factuality testing, or domain review.

## CFC Minimal Commit Invariant — Technical Note v1.0

A short technical note formalising the minimal CFC state-transition rule is now published on Zenodo.

Core comparison:

`Δ_t := Diff(C_t, V_{t-1})`

Core commit invariant:

`¬A_t ⇒ ¬Commit(C_t)`

Minimal verified-state update:

`V_t = C_t` when `A_t = 1`; otherwise `V_t = V_{t-1}`.

Operationally, a generated candidate does not by itself authorize a change to verified state. If the required authorization condition is not established, the previous verified state is preserved.

- DOI: [10.5281/zenodo.22819553](https://doi.org/10.5281/zenodo.22819553)
- Zenodo record: [CFC Minimal Commit Invariant: A Technical Note on State Transition and Unsupported Closure](https://zenodo.org/records/22819553)

The logical implication itself is elementary and is not presented as a claim of mathematical novelty. The contribution of the note is its explicit role as a compact architectural state-control invariant within CFC.

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

## CFC-next 0.3.0a2 — frozen decision-accounting baseline

A separately versioned CFC-next decision-accounting track has now been frozen
after the 0.3.0a1 process-isolation finding was repaired and re-tested.

Frozen ref:

`frozen/cfc-next-0.3.0a2`

Freeze merge commit:

`568282c1f66af9f1f2fad8cf2b04b08226b9aea6`

Validation at freeze:

- 14/14 positive decision-accounting fixtures PASS
- 12/12 negative controls fail-closed
- zero unexpected BOUND negative paths
- promotion-readiness all gates PASS
- 14/14 same-process state-isolation cases PASS
- deterministic full acceptance rerun PASS
- concurrent representative fresh-process positives PASS
- full repository CI: 32/32 workflows PASS
- frozen CFC Anchor 0.2.90rc1 unchanged
- no historical rescore

Candidate source SHA-256:

`dc8ae4f2d51296d68ecf5e75ac861faf1f50f062e1761e0814ce157f08a588a7`

See the [0.3.0a2 replication reference](replication/cfc-next-0.3.0a2/)
for the pinned manifest, validation commands, and claim boundaries.

This CFC-next baseline is separate from the historical frozen Anchor and from
the Demonstrator v1.0 release.

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

## HAWM + CFC Chat Prototype v0.4.2 — external reviewer package

A separate experimental HAWM + CFC chat prototype is available for a bounded independent replay. It is a state-aware conversation shell around an unchanged frozen CFC Anchor checkpoint.

The reviewer package includes the hardened prototype, setup/verification instructions, scope and non-claims, identity manifest, checksums, and a review result form.

- [Reviewer package page](HAWM_CFC_v0.4.2_EXTERNAL_REVIEWER_PACKAGE.zip)
- [Direct ZIP download](https://raw.githubusercontent.com/iller1/cfc-ai-evaluation/main/HAWM_CFC_v0.4.2_EXTERNAL_REVIEWER_PACKAGE.zip)

External reviewer package SHA-256:

`b6c5777cc95ed483ee2cd5e79476a550faeeca51be759fc91b94673150efb374`

Contained hardened prototype SHA-256:

`2ceb687004485c8aeef93150f80a0a6675185e403767a3163c1de51177d95a09`

The package is intended for a short independent replay of a bounded wrapper/integration checkpoint. It does **not** claim production readiness, arbitrary natural-language semantic mapping, real-world source independence, universal correctness, or independent validation until an outside reviewer actually performs and reports the replay.

## Validation boundary

Internal engineering evidence, controlled causal evidence, independent review, external replication, and product usability are separate evidence classes and must not be conflated.
