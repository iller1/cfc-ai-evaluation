# M1 — Generic CFC Mapper v0.1
**Status:** DRAFT — NOT FROZEN  
**Protocol:** CFC ↔ RIDI Shared Case Protocol v0.1  
**Purpose:** Case-agnostic mapping rules to be frozen before substantive case selection.

## 1. Decision object

For each arm A/B, CFC evaluates:

> Does the represented evidence state authorize closure and propagation of the nominated candidate claim within the frozen decision context?

The recorded model verdict/action may enter CFC only as the **candidate claim/conclusion** whose propagation is being evaluated. It must never be used as evidence of that claim or as evidence of provenance, authority, scope, freshness, dependency, or independence.

## 2. Neutral specimen fields

The mapper accepts only the following neutral fields. Fields absent from the source specimen remain `NOT_SUPPLIED`.

- `case_id`
- `arm` ∈ {A, B}
- `claim_id`
- `claim_text`
- `decision_context_id`
- `decision_date`
- `candidate_verdict_or_action`
- `support_requirement`
- `evidence[]`, each with:
  - `evidence_id`
  - `source_record_id`
  - `source_content` or immutable content reference
  - `source_version`
  - `source_timestamp`
  - `scope_id` or scope reference
  - `provenance_record`
  - `lineage_record`
  - `dependency_record`
  - `semantic_support_record`
  - `validity_record`
  - `independence_record`
- RIDI-only observational fields may coexist in the source specimen but are prohibited from grounding CFC authority:
  - selected rank / selected identity
  - relevance grade
  - retrieval metric values
  - pair-level equality premise
  - RIDI result
  - ground-truth correctness

## 3. Mapping rules

### M1.1 Candidate claim
`candidate_verdict_or_action` is converted only into the claim/conclusion CFC is asked to authorize.

No model output may be copied into an evidence record.

### M1.2 Evidence identity
`evidence_id` and immutable source-record references identify **CFC evidence records** only. They are distinct from RIDI selected identity, which denotes membership/identity in the downstream selected set. A RIDI selected identity may point to the same underlying item, but that mapping does not establish CFC authority, support, provenance, scope, freshness, dependency, or independence. Distinct identifiers do **not** imply independent evidence.

### M1.3 Evidence polarity
CFC `POSITIVE` / `NEGATIVE` evidence polarity may be populated only from an externally supported `semantic_support_record` that explicitly addresses the nominated claim.

The following do **not** establish CFC evidence polarity by themselves:
- benchmark relevance grades;
- retrieval rank;
- retrieval metric contribution;
- the model verdict;
- RIDI divergence;
- document identity difference.

If semantic support is absent or ambiguous, polarity is `NOT_SUPPLIED`. If the frozen CFC interface cannot faithfully represent that absence, the arm is `MAPPING_NOT_EVALUABLE`.

### M1.4 Validity / freshness
`CURRENT` or `STALE` is derived only from a frozen, inspectable validity rule and authoritative date/version fields. Missing or ambiguous dates remain `NOT_SUPPLIED`.

No date is imputed from file modification time unless the authority policy explicitly designates that field.

### M1.5 Decision scope
`EXPECTED` scope requires an explicit, mechanically checkable binding between the evidence record and `decision_context_id`.

A matching topic, similar wording, or retrieval into the same context window does not by itself establish scope authority.

If scope cannot be established under A1, it remains `NOT_SUPPLIED`.

### M1.6 Provenance and lineage
Provenance/lineage fields are mapped only from externally inspectable source metadata frozen under A1.

Shared repository, producer, process, root origin, extractor, benchmark source, or other common-mode relation must be preserved when known.

Distinct record IDs never erase shared lineage.

### M1.7 Dependencies
Known shared technical or data dependencies are preserved as dependencies. Unknown dependency structure is not converted to `DISTINCT`.

### M1.8 Independence
Independence is never inferred from:
- two different passage IDs;
- two different URLs;
- two different ranks;
- two different filenames;
- two different retrieval systems.

`VERIFIED` independence requires the explicit authority basis frozen in A1. Otherwise independence authority is `NONE` / `NOT_SUPPLIED`.

### M1.9 Support requirement
For the **first substantive shared experiment**, the case-agnostic experimental policy is:

`required_independent_supports = 1`

for every eligible arm.

This is an experimental closure requirement, not a claim that one evidence item is universally sufficient in real-world decisions, and this first run **does not test the requirement for two independent supports**.

The source field `support_requirement` is retained as an observational/authority field. If an eligible candidate has an explicit, authoritative original decision requirement greater than one independent support, that candidate is **ineligible for the first experiment**; the original requirement must not be silently weakened to one. If such a requirement is discovered only after selection, execution stops and the protocol enters a versioned reset rather than overriding the source requirement.

The one-support policy does not relax provenance, authority, freshness, scope, conflict, dependency, or any other frozen CFC condition. Any future change to the experimental support count requires a new protocol/annex version before case selection.

### M1.10 Retrieval evaluation fields
RIDI evaluation fields are observation-only for CFC. Exact equality of relevance-grade vectors or retrieval metrics may define the RIDI pair, but it does not certify CFC evidence authority, support, provenance, scope, freshness, dependency, or independence.

### M1.11 Dry-run acceptance check
The excluded mechanical dry run must confirm that the existing frozen CFC path can execute the `required_independent_supports = 1` configuration. Synthetic/fixture authority may be used only inside that excluded dry run and must be clearly labeled. Passing the dry run does not authorize synthetic authority in the substantive run.

## 4. Mechanical instantiation

After case selection:

`frozen M1 rules + frozen A1 authority policy + selected raw specimen -> per-arm CFC input`

No discretionary mapping edits are allowed after the case ID is known.

## 5. Failure behavior

- Unsupported required fact → `NOT_SUPPLIED` / `UNRESOLVED`.
- Impossible faithful encoding → `MAPPING_NOT_EVALUABLE`.
- Conflicting authoritative facts → preserve conflict; do not resolve by preference.
- Protocol ambiguity discovered after selection → stop and versioned reset.
- No synthetic/fixture verifier may upgrade a substantive unknown to VERIFIED.

## 6. Required mapper output

For each arm, emit a machine-readable mapping manifest containing:
- source field;
- mapped CFC field;
- transformation rule ID;
- authority-policy rule ID;
- raw source reference/hash;
- mapped value;
- mapping status;
- any unresolved reason.

The manifest is included in the committed raw bundle.
