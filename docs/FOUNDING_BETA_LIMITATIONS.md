# CFC + HAWM Founding Beta — Limitations

These limitations are part of the product boundary, not fine print.

## 1. Experimental status

Founding Beta is experimental.

It is not a certification, safety guarantee, external validation, or proof of general AI reliability.

## 2. Human control

A human must retain final control over decisions made from beta outputs.

CFC + HAWM should not be the sole basis for high-risk decisions during Founding Beta.

## 3. Narrow initial scope

The first beta should support a small number of clearly defined workflows.

A workflow that cannot be represented clearly enough to replay should not be treated as beta-ready.

## 4. False stops and missed stops are expected findings

The beta is explicitly intended to surface:
- false stops,
- missed stops,
- unresolved states that are presented unclearly,
- missing evidence/provenance handling,
- workflow assumptions that fail in practice.

A reported failure is evidence for iteration, not automatically evidence that the entire approach succeeds or fails.

## 5. Model output is not controller authority

Model replies may be stored as MODEL_REPLY_UNCHECKED / NOT_CONNECTED_C2 unless and until a controller result explicitly authorizes a stronger status.

Natural-language confidence must not be treated as a substitute for controller authority.

## 6. Benchmark limits

Repeatability results apply only to the tested cases, model versions, prompts, providers and observed runs.

They do not establish future error rates or general reliability.

## 7. Provider/API failures

Provider/API failure is separate from semantic model failure.

A missing response is not CONSISTENT, AMBIGUOUS or PREMATURE_CLOSURE.

## 8. Data and privacy

External beta use must not begin with sensitive customer data until the data-handling policy, retention policy, deletion process and access boundaries are explicitly defined.

Use synthetic, public, or appropriately authorized low-risk data for early trials.

## 9. Frozen baseline

Frozen controller artifacts remain frozen.

No bug discovered in beta may be silently repaired inside a frozen artifact. Any future controller change requires a separately versioned line and regression evidence.
