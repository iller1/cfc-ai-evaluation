# A1 — Authority Policy v0.1
**Status:** DRAFT — NOT FROZEN  
**Protocol:** CFC ↔ RIDI Shared Case Protocol v0.1  
**Purpose:** Define which external facts may authorize CFC mappings in the first substantive shared experiment.

## 1. General rule

A CFC field that requires authority may be VERIFIED only when the authority basis is:
1. predeclared before case selection;
2. externally inspectable;
3. applicable to the selected record/context;
4. preserved in the raw bundle;
5. not derived from the expected CFC or RIDI outcome.

Unknown facts remain unknown. A clean-looking run is not a reason to fabricate an attestation.

## 2. Authority classes

| Authority class | Acceptable basis | Explicitly insufficient alone |
|---|---|---|
| Record identity | Immutable public record ID + content/version hash or authoritative benchmark record | Filename, rank, local label |
| Content integrity | Source snapshot hash / public commit / archived dataset record | Re-rendered text without provenance |
| Semantic support | Frozen external annotation or explicit source statement that directly addresses the nominated claim | Retrieval relevance grade, model verdict, RIDI result |
| Validity/freshness | Authoritative timestamp/version + frozen date rule | File mtime, inferred recency |
| Scope | Explicit scope/context binding or exact rule over authoritative fields | Topic similarity, same retrieved window |
| Provenance/lineage | Public source metadata, immutable origin/version identifiers, frozen dependency records | Distinct IDs or URLs |
| Dependency/common mode | Explicit shared source/process/index/model/extractor metadata | Absence of known dependency |
| Independence | Explicit authority evidence that supports independence under the frozen rule | Distinct passages, retrievers, filenames, URLs |
| Retrieval snapshot | Frozen A/B specimen bytes + source hash + selection record | Recreated context without byte identity |
| Ground-truth correctness | Independently established benchmark/reference field, used only as RIDI secondary correctness | Model output or CFC closure result |

## 3. First-run authority restrictions

### A1.1 No fixture laundering
Synthetic authorities and demonstrator fixture verifiers are allowed only in the excluded mechanical dry run.

They are prohibited from upgrading substantive unknown facts.

### A1.2 Retrieval grades are not semantic-support authority
A benchmark relevance grade may be used to establish the RIDI equality premise when the protocol permits it.

It does **not**, by itself, establish that a passage is positive/negative evidence for the candidate claim in CFC.

### A1.3 Model verdict is never authority
The model verdict/action can define the candidate claim to be checked. It cannot establish support, truth, provenance, scope, freshness, dependency, or independence.

### A1.4 Frozen-rule application is permitted; new discretionary authority is prohibited
After case selection, a pre-frozen authority rule may be mechanically applied to an **already existing** source record or authority record that was permitted by A1/I1. This is ordinary instantiation, not a new authority assertion.

What is prohibited is creating, soliciting, editing, or introducing a new discretionary authority assertion after learning the selected case in order to make a mapping pass. If an authority rule was not frozen before selection, or the required supporting record did not already exist within the permitted evidence boundary, the missing fact remains unavailable for that protocol version.

### A1.5 Independence is conservative
If known lineage/dependency information conflicts with an independence claim, the dependency information governs and the independence claim is rejected.

### A1.6 One-support policy
Because M1 v0.1 fixes `required_independent_supports = 1`, the first substantive experiment does not require a multi-record independence certificate for closure and **does not test the requirement for two independent supports**.

A source case with an explicit authoritative requirement greater than one is ineligible for this first experiment; that requirement must not be weakened to fit the experimental policy.

The one-support policy does not relax provenance, authority, freshness, scope, conflict, dependency, or any other frozen CFC condition. Any additional evidence records and known shared dependencies remain visible and may still affect CFC state according to the frozen controller.

### A1.7 Dry-run authority boundary
The excluded mechanical dry run must demonstrate that the frozen CFC execution path accepts the one-support configuration. Synthetic authorities or fixture verifiers may be used only for that dry run, must be labeled as synthetic, and must not be copied, promoted, or reused as authority in the substantive run.

## 4. Missing authority handling

For every authority-requiring field:

- authoritative fact present and valid → map according to M1;
- fact absent → `NOT_SUPPLIED`;
- fact contradictory → preserve contradiction/conflict;
- fact not faithfully representable → `MAPPING_NOT_EVALUABLE`;
- source unavailable at execution → execution error / not evaluable; no substitution.

## 5. Authority evidence manifest

Each substantive raw bundle must include `authority_manifest.tsv` with:
- authority rule ID;
- mapped field;
- issuer/source;
- source URI or immutable reference;
- source version/date;
- content hash where available;
- validation method;
- validation result;
- value supplied to M1;
- unresolved/error note.

## 6. Non-claims

A1 does not assert that:
- public metadata is universally correct;
- one support is sufficient outside this bounded experiment;
- CFC validates raw-source semantics automatically;
- RIDI metrics validate CFC evidence;
- a CFC ALLOW implies real-world safety or permission to act.
