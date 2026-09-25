# Structured Input State-Space Experiment

## Purpose

Generate the complete discrete state space exposed by the current Founding Beta structured HAWM -> CFC adapter before applying semantic expectations.

This deliberately separates:

1. mathematics: enumerate the state space;
2. structural validity: collapse UI duplicates and reject contradictory states;
3. logic: classify expected controller behaviour;
4. execution: compare expected transitions with the frozen controller.

The frozen CFC controller is not modified.

## Current counts

- raw UI configurations: **1024**
- canonical logical states: **640**
- structurally admissible states: **480**
- contradictory SHARED_LINEAGE + VERIFIED states rejected: **160**

The 1024 -> 640 reduction occurs because when Evidence 2 is omitted, its polarity and validity selections have no semantic effect and collapse to one canonical state.

## Mutation analysis

The analyzer generates two related mutation sets:

- **1904 one-field mutation pairs**: states differing in exactly one stored field.
- **2288 semantic mutation edges**: the one-field pairs plus 384 logical E2 add/remove operations.

The distinction matters because E2 OMIT -> INCLUDE is one logical operation even though the serialized state also materializes E2 polarity and validity.

These edges form the basis of metamorphic tests such as:

- CURRENT -> STALE
- EXPECTED -> WRONG
- DISTINCT -> SHARED_LINEAGE
- required supports 1 -> 2
- E2 OMIT -> INCLUDE
- POSITIVE -> NEGATIVE

The current mutation-family counts are:

- CLAIM_EVIDENCE_ALIGNMENT: 240
- SUPPORT_THRESHOLD: 240
- SCOPE: 240
- PROVENANCE_DEPENDENCY: 160
- INDEPENDENCE_AUTHORITY: 160
- EVIDENCE_POLARITY: 240
- FRESHNESS: 240
- SUPPORT_COMPLETENESS: 384
- SECOND_EVIDENCE_POLARITY: 192
- SECOND_EVIDENCE_FRESHNESS: 192

The next phase should assign expected directional constraints to these mutations and then run the frozen controller externally.

## Important boundary

This experiment does not assume that every admissible input has a known correct ALLOW/STOP outcome.

Mathematical enumeration comes first. Semantic expectations are added only when they are justified by the frozen controller contract or a separately documented test hypothesis.
