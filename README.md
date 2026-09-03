# CFC — AI Evaluation & Control Framework
## Quick links

- [Project Status](PROJECT_STATUS.md)
- [Independent Review Guide](REVIEW.md)
- [Representative Examples](#representative-examples)
- ## Quick links
## Quick links

- [Project Status](PROJECT_STATUS.md)
- [Technical Overview](docs/TECHNICAL_OVERVIEW.md)
- [Technical Brief (PDF)](docs/CFC_Technical_Brief_September_2026.pdf)
- [Independent Review Guide](REVIEW.md)
- [Representative Examples](#representative-examples)

**CFC** is an independent AI evaluation and control project focused on a specific LLM reliability failure mode:

## Feedback and review

Independent technical feedback is welcome.

If you identify a counterexample, unsupported closure, false block, ambiguity in the state model, or a methodological weakness, please open a GitHub Issue with enough detail to reproduce the case.

The most useful feedback is specific, technical and reproducible.
> An AI system reaches a definite conclusion even though the available evidence or current system state does not justify closing the question yet.
> 
## Representative examples

Three simplified examples illustrate the core control logic:

- [Example 01 — Unresolved Evidence → Definite Conclusion](examples/01_unresolved_to_definite_conclusion.md)
- [Example 02 — Valid Evidence → Definite Conclusion](examples/02_valid_closure.md)
- [Example 03 — Conflicting Evidence Without Valid Resolution](examples/03_conflicting_evidence.md)

These examples are intended to explain the logic of CFC and are not presented as empirical benchmark results.
## The problem

A model can produce a fluent and confident answer while the underlying evidence is still:

- unresolved,
- conflicting,
- stale,
- out of scope,
- incomplete,
- or dependent on an invalid resolution.

In these situations, response quality alone does not tell us whether the conclusion was legitimately supported.

Typical failure patterns include:

- `UNRESOLVED → TRUE / FALSE`
- conflicting evidence resolved without a valid rule
- stale or wrong-scope evidence influencing a decision
- unsupported state transitions
- definitive conclusions while required checks remain incomplete

## What CFC does
## Representative examples

Two simplified examples illustrate the core control logic:

- [Example 01 — Unresolved Evidence → Definite Conclusion](examples/01_unresolved_to_definite_conclusion.md)
- [Example 02 — Valid Evidence → Definite Conclusion](examples/02_valid_closure.md)
- 
- [Example 03 — Conflicting Evidence Without Valid Resolution](examples/03_conflicting_evidence.md)
These examples are intended to explain the logic of CFC and are not presented as empirical benchmark results.

CFC separates two questions:

1. **Can the model generate a conclusion?**
2. **Does the available evidence and system state actually justify that conclusion?**

The framework applies explicit state, evidence, validity, scope and closure rules before allowing a decision to be treated as resolved.

Conceptually:

```text
INPUT / EVIDENCE STATE
        ↓
MODEL CONCLUSION
        ↓
CFC CHECK
        ↓
ALLOW / STOP / UNRESOLVED
        ↓
REASON
