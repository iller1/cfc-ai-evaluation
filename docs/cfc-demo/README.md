# CFC public walkthrough

This directory contains a six-step bilingual presentation. It is not a live NOAA-to-controller integration.

Lane A: 18/18 synthetic developer tests of the frozen public API; role installation missing, no closure.

Lane B: separate offline helper comparison of seven NOAA image pairs; two byte-identical and five different.

Native internal test (separate from NOAA): under unchanged two-support policy, the synthetic aligned input safe/safe/safe produced VERIFIED + global_consistency_valid=true + CONTROL_CLOSURE=true, while safe/safe/unsafe produced VERIFIED + global_consistency_valid=false + CONTROL_CLOSURE=false. Only global_consistency_valid failed in the conflicting scenario, and the engine named conflicts E1-E3 and E2-E3. Exactly one authored evidence value changed; derived content-bound fixture metadata was regenerated. A local Windows reproduction on 15 October 2026 reported 16/16 test cases OK. This is an operator-run development fixture, not an external independent audit or proof of production authorization. The exact frozen wheel SHA-256 was b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303. The full reproducer package CFC_NATIVE_ISOLATED_CONSISTENCY_GATE_DEV_v0_1 is held separately and is not included in this public page.

NOAA-to-Anchor bridge: NOT_ESTABLISHED. No authorization. F01 HOLD and R273 NO_GO.

Images shown in this web page are schematic illustrations, not archived original JPEGs. Full unmodified archives are preserved separately. The independent methods, meaning and trust reviews remain open.

Main project: https://github.com/iller1/cfc-ai-evaluation
