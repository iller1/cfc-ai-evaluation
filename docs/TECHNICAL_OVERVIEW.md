# CFC — Technical Overview

## 1. Purpose

CFC is an AI evaluation and control framework focused on a narrow reliability problem:

> A model reaches a definite conclusion even though the available evidence or current system state does not justify closure.

The framework is designed to separate answer generation from authorization to close a decision.

---

## 2. Core control principle

A model may be able to generate a plausible conclusion without having sufficient evidence to justify that conclusion.

CFC therefore evaluates the state surrounding the conclusion before closure is permitted.

Conceptually:

INPUT / EVIDENCE STATE  
↓  
MODEL CONCLUSION  
↓  
CFC CONTROL CHECKS  
↓  
ALLOW / STOP / UNRESOLVED  
↓  
AUDITABLE REASON

---

## 3. State model

At a simplified level, required checks can occupy states such as:

- FORMALLY_POSITIVE
- FORMALLY_NEGATIVE
- UNRESOLVED

These states are not interchangeable.

In particular:

UNRESOLVED ≠ FORMALLY_POSITIVE  
UNRESOLVED ≠ FORMALLY_NEGATIVE

An unresolved state must remain unresolved until valid evidence or an applicable resolution mechanism changes that state.

---

## 4. Closure logic

A definitive conclusion is permitted only when the required conditions for closure are satisfied.

Examples:

### Legitimate positive closure

All required checks are validly FORMALLY_POSITIVE.

Result:

ALLOW

### Negative resolution

At least one required check is validly FORMALLY_NEGATIVE.

The result must reflect that negative resolution according to the applicable decision rules.

### Unresolved state

At least one required check remains UNRESOLVED and no valid rule resolves it.

Result:

NO CLOSURE / UNRESOLVED

CFC is designed to prevent uncertainty from being silently converted into certainty.

---

## 5. Evidence controls

The framework evaluates more than the apparent meaning of an evidence record.

Relevant control dimensions include:

- record validity
- active/inactive state
- scope applicability
- temporal validity
- evidence identity
- provenance relationships
- conflict membership
- resolution applicability
- state binding
- dependency relationships

A record may exist and still be ineligible to influence the current closure decision.

---

## 6. Conflict handling

When applicable active records conflict, CFC does not select a preferred record merely because one outcome appears more plausible.

Closure depends on whether the conflict has been resolved by a valid and applicable resolution mechanism.

If no valid resolution exists, the conflicting state remains unresolved.

---

## 7. Failure modes targeted

Representative failure modes include:

- unresolved evidence converted into TRUE or FALSE
- conflicting evidence resolved without authority
- stale evidence influencing the current decision
- wrong-scope evidence being treated as applicable
- inactive records affecting closure
- invalid resolution records being accepted
- unsupported state transitions
- incomplete evidence being treated as complete
- dependency or provenance relationships being ignored
- definite conclusions produced while required checks remain unresolved

---

## 8. Evaluation philosophy

CFC is evaluated as a deterministic reliability control rather than as a prompt-engineering technique.

The goal is not to make a model sound more cautious.

The goal is to determine whether the formal state permits closure.

Testing therefore focuses on:

- unsupported closure
- legitimate closure preservation
- unresolved-state preservation
- conflict handling
- evidence validity
- scope handling
- state transitions
- adversarial edge cases

---

## 9. Frozen baseline

The current frozen controller baseline is:

**CFC v1.23**

The baseline remains byte-for-byte frozen during the current external validation stage.

External documentation, demonstrations and review materials may be added around the baseline without changing its controller logic.

---

## 10. Current validation stage

Current priorities are:

- independent technical review
- external replication
- representative demonstrations
- validation against additional failure cases
- comparison with LLM and agent evaluation approaches
- preparation for possible shadow-mode pilot testing

Internal results are encouraging, but they are not treated as independent validation.

---

## 11. Intended role

CFC is not intended to replace:

- factuality evaluation
- hallucination benchmarks
- safety classifiers
- general model evaluation
- red-team testing
- human review

It is intended to provide an additional control layer focused specifically on whether the evidence and state justify a definitive conclusion.

---

## 12. Relevance to agentic systems

In an agentic system, an unsupported conclusion may not remain only a textual error.

It can become an input to:

- a tool call
- a workflow transition
- a database update
- an automated recommendation
- another agent
- a downstream decision

For this reason, preserving unresolved states can be important before an agent is allowed to continue acting.

---

**Current frozen baseline:** CFC v1.23  
**Project:** Independent AI Evaluation & Reliability Project  
**Author:** Krzysztof Śliwka
