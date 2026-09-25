# CFC-next 0.3.0a2 peer-controller isolation review

## Question

CFC-next 0.3.0a2 intentionally shares the frozen engine registries inside one
Python interpreter. The previous state-isolation review showed that candidate
accounting authorization does not authorize an ordinary frozen Controller.

This review asks the next multi-user question:

> Can accounting authorized by candidate Controller A accidentally authorize a
> distinct candidate Controller B with different identity, evidence, retrieval
> scope and accounting context in the same interpreter?

## Representative phase

The first phase covers:

- root-origin shared relation;
- extractor shared relation;
- generic dependency / data source.

Each relation is executed in a fresh subprocess.

For each case:

1. build independent A and B contexts;
2. verify both start blocked;
3. install and finalize valid accounting only for A;
4. verify A closes;
5. evaluate pre-existing B;
6. evaluate a fresh B Controller over B's context;
7. deliberately attempt to reuse A's accounting ID for B and require fail-closed rejection;
8. verify B remains blocked after the collision attempt.

## Claim boundary

This is not a claim of arbitrary thread safety or concurrent writes. It tests
same-interpreter peer-controller authorization isolation under distinct
contexts and a deliberate accounting-ID collision.

If the representative phase is clean, expand the identical test to all 14
known blocker families before drawing a general result.
