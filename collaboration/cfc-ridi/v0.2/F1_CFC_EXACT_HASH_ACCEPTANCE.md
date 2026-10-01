# CFC–RIDI v0.2 — CFC-Side F1 Exact-Hash Acceptance

Status: CFC-SIDE COUNTERSIGN / F1 EXACT-HASH ACCEPTANCE  
Authority: signed F0 feasibility workplan

CFC explicitly accepts the same exact F1 baseline identity and interface-manifest identity independently verified by RIDI.

## Accepted baseline

`CFC Anchor 0.2.90rc1`

Frozen wheel SHA-256:

`b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303`

## Accepted F1 interface manifest

File:

`collaboration/cfc-ridi/v0.2/F1_CFC_ANCHOR_INTERFACE_MANIFEST.md`

Bytes:

`4945`

SHA-256:

`b23719df7efd75dc4d53b33808377e1002a044a88acc5354defd06dc59829184`

Git blob:

`5e1bbd1823214955e962b88b3bb04af755e41586`

CFC independently rechecked the current repository artifact and reproduced the byte length and SHA-256 above before countersigning.

## Scope clarification

This F1 acceptance applies to the bounded public custom-Demonstrator lifecycle represented by the accepted interface manifest.

It does not claim that the accepted interface exposes every public surface used by every Demonstrator case.

If a later accepted neutral schema requires any additional public class or method, the F1 interface contract must be explicitly amended and bilaterally re-accepted before that surface can be used.

## Effect

With matching RIDI verification and this CFC countersign, F1 exact-hash baseline/interface acceptance is complete.

The next signed-F0 gate is the Neutral schema class for Phase F.

No F2 adapter development is authorized until that neutral schema artifact is also independently reviewed and bilaterally accepted.

F0 remains signed and unchanged.

v0.1 remains closed and immutable.

F1 exact-hash acceptance → neutral-schema exact-hash acceptance → F2.
