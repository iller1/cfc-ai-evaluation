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

The analyzer also generates pairs of admissible states that differ in exactly one field. These pairs form the basis of metamorphic tests such as:

- CURRENT -> STALE
- EXPECTED -> WRONG
- DISTINCT -> SHARED_LINEAGE
- required supports 1 -> 2
- E2 OMIT -> INCLUDE
- POSITIVE -> NEGATIVE

The next phase should assign expected directional constraints to these mutations and then run the frozen controller externally.

## Important boundary

This experiment does not assume that every admissible input has a known correct ALLOW/STOP outcome.

Mathematical enumeration comes first. Semantic expectations are added only when they are justified by the frozen controller contract or a separately documented test hypothesis.
