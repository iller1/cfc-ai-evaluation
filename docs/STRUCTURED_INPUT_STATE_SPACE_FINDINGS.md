# Structured HAWM State-Space — First Frozen-CFC Findings

**Status:** external research finding over frozen CFC Anchor 0.2.90rc1.

This records observed transitions only. Counter-intuitive transitions are not classified as controller bugs; they become candidates for semantic review.

## Execution

- GitHub Actions run #5 / 36137202352: SUCCESS
- GitHub Actions run #9 / 36137450216: SUCCESS and same summary
- admissible states executed: **480**
- semantic mutation edges checked: **2288**
- ALLOW / VERIFIED: **24**
- STOP / QUARANTINED: **192**
- STOP / SUPPORTED: **80**
- STOP / UNRESOLVED: **144**
- STOP / VERIFIED: **40**

## Invariance results

### Global polarity inversion

Flip conclusion POSITIVE <-> NEGATIVE and invert every included evidence polarity while preserving all other fields.

- pairs checked: **240**
- mismatches: **0**

### Evidence-order swap

For two-evidence cases, swap E1 and E2 while preserving their polarity and validity.

- pairs checked: **240**
- mismatches: **0**

## Clean directional observations

### EXPECTED -> WRONG scope

- total: 240
- closure decreases: **24**
- closure increases: **0**
- all 24 decreases: ALLOW / VERIFIED -> STOP / VERIFIED

This demonstrates that VERIFIED claim state and closure authorization are separate.

### DISTINCT -> SHARED_LINEAGE

- total: 160
- closure decreases: **8**
- closure increases: **0**
- observed decrease: ALLOW / VERIFIED -> STOP / VERIFIED

### NONE -> VERIFIED independence authority

- total: 160
- closure increases: **2**
- closure decreases: **0**
- increases: STOP / SUPPORTED -> ALLOW / VERIFIED

### Evidence polarity: opposing -> supporting

E1: 240 edges; closure increases 16; decreases 0.
E2: 192 edges; closure increases 10; decreases 0.

## Non-monotonic findings requiring semantic review

### Finding A — support-threshold reversal

Changing only required_independent_supports 1 -> 2 normally makes closure harder, but there are **2 closure increases**.

Both are polarity-symmetric versions of the same state:
- scope EXPECTED
- provenance DISTINCT
- independence authority VERIFIED
- E1 and E2 both CURRENT
- both evidence records support the conclusion

Observed:
- required=1 -> STOP / SUPPORTED
- required=2 -> ALLOW / VERIFIED

For required=1 the false gates include support policy, support-universe common-mode coverage, relation discovery/resolution coverage and support-selection justification. For required=2 the reason is policy-satisfied support set (2).

Candidate class: **SUPPORT THRESHOLD / SUPPORT-SET COUPLING**.

Question: does a two-record verified independence certificate intentionally make the two-support policy closable while leaving the one-support selection unresolved, or is this an unexpected policy interaction?

### Finding B — making evidence stale can increase closure

E1 CURRENT -> STALE:
- closure decreases: 16
- closure increases: **8**

E2 CURRENT -> STALE:
- closure decreases: 10
- closure increases: **8**

The increasing E1 cases share: required supports=1, EXPECTED scope, DISTINCT provenance, and another CURRENT evidence record that supports the conclusion.

Observed increases include STOP / SUPPORTED -> ALLOW / VERIFIED and STOP / QUARANTINED -> ALLOW / VERIFIED.

Candidate class: **EVIDENCE WITHDRAWAL / ACTIVE-UNIVERSE CONTRACTION**.

Interpretation hypothesis: making one record stale removes it from the active decision-relevant support/conflict universe, leaving one current support sufficient for the one-support policy.

### Finding C — adding evidence can reduce closure

E2 OMIT -> INCLUDE across 384 edges:
- closure increases: 10
- closure decreases: **16**
- unchanged: 358

All 16 decreases start from ALLOW / VERIFIED and can end in STOP / SUPPORTED, STOP / QUARANTINED or STOP / VERIFIED.

Candidate class: **EVIDENCE ADDITION / SUPPORT-UNIVERSE EXPANSION**.

Important observation: more evidence is not equivalent to more authorization.

### Finding D — stale extra evidence can still change authorization

In SHARED_LINEAGE cases, adding a stale second record can produce ALLOW / VERIFIED -> STOP / VERIFIED.

Candidate class: **STALE RECORD / DEPENDENCY-UNIVERSE INTERACTION**.

## What the combinatorial method added

The state-space approach exposed test families that are easy to miss when cases are designed only by intuition:

1. support-threshold / support-set coupling;
2. active-universe contraction after evidence becomes stale;
3. support-universe expansion after adding evidence;
4. stale-record interaction with provenance/dependency state;
5. global polarity inversion symmetry;
6. evidence-order invariance.

## Next step

Do not change the frozen controller.

For each non-monotonic finding: reduce to the smallest before/after pair; inspect exact false-gate differences; state the expected semantic rule before judging the behavior; classify as intended behavior, boundary finding, or candidate false-closure/false-block issue; only then create a permanent external regression fixture.


## Refinement — logical mutation vs runtime mutation

The combinatorial sweep exposed an important fixture-level coupling in the custom builder.

An E2 OMIT -> INCLUDE mutation is not always a pure evidence-addition operation:

- **DISTINCT + NONE**: pure E2 addition; E1 provenance is unchanged and no independence certificate is installed.
- **DISTINCT + VERIFIED**: adding E2 also activates installation of the explicit E1/E2 support-set independence certificate, because the custom fixture only installs that certificate when two evidence records exist.
- **SHARED_LINEAGE + NONE**: adding E2 also causes the fixture to rebuild E1 with shared lineage/dependency identifiers, because shared lineage is only materialized when more than one evidence record exists.

Therefore the 384 SUPPORT_COMPLETENESS edges must be split into three 128-edge runtime classes before interpreting them as metamorphic tests.

This is a test-harness finding, not a frozen-controller defect.

It also explains why some apparent 'stale extra evidence' or 'adding evidence' effects can be confounded by provenance/authority changes that are derived by the fixture rather than represented as a second explicit UI-field mutation.

### Consequence

Future semantic classification must distinguish:

1. **logical input delta** — what the HAWM form field changed;
2. **derived runtime delta** — what the adapter/fixture changed in the actual frozen-CFC API objects;
3. **controller output delta** — what the frozen controller returned.

Only edges with a controlled derived runtime delta should be used as clean one-factor metamorphic tests.
