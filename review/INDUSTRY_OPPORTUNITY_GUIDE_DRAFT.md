# CFC — Research Prototype & Industry Review Guide

**Draft for academic and industry introductions — not a product catalogue or offer of production deployment**  
**Date:** 2026-11-22

## The problem in one minute

AI systems can generate conclusions that sound final even when underlying evidence is absent, stale, conflicting or outside scope. CFC research explores a narrow control principle: **a conclusion or verified source is not, by itself, authorization to close a decision or perform an action**. Unsupported states should remain `UNRESOLVED`.

## Which problem would you like to evaluate?

| Your workflow | Relevant existing research demonstrator | What a limited review could test | Current boundary |
|---|---|---|---|
| AI-generated summaries or policy answers cite the wrong passage | **Evidence Copilot** — local Ollama document-analysis demonstrator | Exact quotation agreement, incomplete support, human escalation on a synthetic policy | Local prototype only; does not prove semantic accuracy or run frozen CFC; latest package distribution still in preparation |
| An AI recommendation is treated as approved without adequate evidence | **CFC Demonstrator v1.0** | Deterministic replay of predefined evidence/authority cases and STOP/UNRESOLVED reasoning | Synthetic cases and limited manual builder, not arbitrary natural-language understanding or execution enforcement |
| Evidence/approval state may go stale or be mis-mapped between stages | **CFC × HAWM / Integration RC** | Controlled synthetic adapter/mapping review and stale-state scenarios | Experimental, limited mapping; no production end-to-end protection |
| Agents may execute twice or act after approval goes stale | **M6 / Execution Controls research** | Technical review of authorization-to-execution boundary and durable attempt evidence | **DESIGN HOLD**; E2E 0/6; CP-15 NOT CONNECTED. Not deployable |

These are **different development tracks**, not one integrated turnkey product. Organizations select a **problem to investigate**, not an already-proven solution.

## One illustrative, non-operational demonstration

Synthetic internal policy: rule A requires manager approval before publication; rule B allows an exception for urgent documents. Evidence Copilot can answer a question and check whether an exact quotation appears in the extracted source. This **does not** prove the answer correctly interpreted exceptions. A separate CFC Demonstrator illustrates deterministic evidence-state decisions; no runtime connection between the two is implied.

## What can be offered today?

1. Academic/technical review of the frozen demonstrator, its specified claim boundaries and reproducibility.
2. Short **offline, synthetic, non-operational** demonstrations.
3. Scoping discussion: one candidate workflow, pre-registered success and failure criteria, relevant baseline comparator, acceptable false HOLD rate, independent reviewer, stop condition.

This is **not** an authorization to use confidential documents, to grant an AI tool execution permissions, or to place the system in a live decision path.

## Honest evidence snapshot

- Public CFC Demonstrator v1.0 and frozen baseline are documented in the [main repository](https://github.com/iller1/cfc-ai-evaluation) and [release](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0).
- [Evidence Copilot P74 external-review checkpoint](https://github.com/iller1/cfc-ai-evaluation/pull/115) is a reproducible candidate archive, but independent runtime replication is outstanding.
- [P77 onward findings and operator-reported tests](https://github.com/iller1/cfc-ai-evaluation/pull/116) document selected repairs and continuing limitations. Latest candidate archives are **not fully published**.
- P79 local exact quotation check passed for one real Qwen3 1.7B scenario; P80 synthetic semantic boundary tests passed; P81 author-created reference labels remain under external-review HOLD.
- No claim of general factual accuracy, prevention of downstream execution, validated industry ROI, independent model-context coverage or production readiness.

## What we ask from a professor, engineer or company

- Identify **one precise workflow** and its input/output format.
- Tell us the cost of both **false ALLOW** and **false STOP**, and what evidence an independent reviewer would need.
- Nominate a technical reviewer for source inspection and independent rerun, or an industry contact interested in an **offline research evaluation**.
- Highlight any known standard/baseline tool that should be used as comparison.

**Contact intent:** seeking critical research review, reproducibility partners and conversations about candidate use cases; no claim of a finished commercial product.

## Further technical information

- [Main CFC repository](https://github.com/iller1/cfc-ai-evaluation)
- [Demonstrator v1.0](https://github.com/iller1/cfc-ai-evaluation/releases/tag/cfc-demonstrator-v1.0)
- [Pre-review repair register](PRE_EXTERNAL_REVIEW_REPAIR_GATE_2026-11-22.md)

**Status:** DRAFT FOR REVIEW — NON-PRODUCTION.
