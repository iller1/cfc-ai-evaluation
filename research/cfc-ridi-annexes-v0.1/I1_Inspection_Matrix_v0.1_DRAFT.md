# I1 — Inspection Matrix v0.1
**Status:** DRAFT — NOT FROZEN  
**Protocol:** CFC ↔ RIDI Shared Case Protocol v0.1  
**Purpose:** Predeclare what each system/participant may inspect before raw-output commitment.

## 1. Principles

- CFC and RIDI inspect different surfaces, but the experiment is **not fully blinded**. Both sides may inspect the recorded A/B verdicts/actions because those values are needed by both frameworks; this overlap can make the RIDI primary equivalence result inferable before bundle exchange.
- The protection is therefore **independent execution with output sequestration and mandatory hash commitments**, not complete outcome blinding. Neither participant sees the other side's substantive raw output, computed result bundle, or interpretation before both raw-bundle hashes are committed.
- Ground-truth correctness is withheld from primary decision logic unless explicitly needed for an entry condition; for v0.1 it is secondary only.
- HAWM and Information Passport are excluded from the first active path.

## 2. Pre-execution inspection matrix

Legend: `YES` = permitted; `NO` = prohibited; `POST` = available only after both raw-output commitments.

| Field / artifact | Adeeb / RIDI side | Krzysztof / CFC side | Notes |
|---|---:|---:|---|
| Frozen protocol + M1/A1/I1 | YES | YES | Public/frozen |
| Eligible pool IDs + eligibility rationale after pool freeze | YES | YES | Before seed reveal |
| Pool source hashes | YES | YES | Before selection |
| Selected case ID after commit–reveal | YES | YES | Same record |
| Raw A/B selected identities | YES | YES | **RIDI selected identity** is downstream membership/identity. If referenced by CFC, it may identify the corresponding source item only; it is not itself CFC evidence authority or independence. |
| Raw A/B evidence content / immutable references | YES | YES | Required for mapping review |
| Retrieval rank positions | YES | NO | RIDI surface only |
| Relevance-grade vector | YES | NO | RIDI equality premise; not CFC authority |
| Retrieval metrics | YES | NO | RIDI equality premise |
| Recorded offline model verdict/action A/B | YES | YES | CFC: candidate claim only; RIDI: primary downstream endpoint |
| Ground-truth correctness label | POST | POST | Secondary analysis only |
| CFC semantic-support authority records | NO | YES | Not a RIDI input |
| CFC scope authority records | NO | YES | Not a RIDI input |
| CFC provenance/lineage authority records | NO | YES | Not a RIDI input |
| CFC dependency/common-mode authority records | NO | YES | Not a RIDI input |
| CFC independence authority records | NO | YES | Not a RIDI input |
| Mapped CFC per-arm input | POST | YES | Included in CFC raw bundle |
| CFC per-arm output | POST | YES | Hidden from RIDI until commitments |
| Derived CFC pair classification | POST | POST | Computed after raw per-arm outputs exist |
| RIDI pair-level PASS/FAIL | YES | POST | Hidden from CFC until commitments |
| RIDI selected-identity/secondary fields | YES | POST | Hidden from CFC until commitments |
| RIDI interpretation narrative | NO | NO | Not authored until unblind |
| CFC interpretation narrative | NO | NO | Not authored until unblind |

## 3. Participant restrictions

### I1.1 Adeeb / RIDI side
Before raw-bundle commitment, may not inspect:
- CFC mapped input;
- CFC gates/reasons;
- CFC claim state;
- CFC closure result;
- Krzysztof's interpretation.

### I1.2 Krzysztof / CFC side
Before raw-bundle commitment, may not inspect:
- computed RIDI PASS/FAIL;
- RIDI divergence summary;
- ground-truth correctness;
- Adeeb's interpretation.

The CFC side may see the recorded A/B verdict/action because it is the candidate claim under review. Because the RIDI primary endpoint is equivalence of those recorded values under the frozen comparison function, Krzysztof may be able to infer the RIDI result from permitted inputs. This is an acknowledged information overlap, not a protocol violation. The CFC side must nevertheless not receive Adeeb's computed RIDI output bundle, diagnostics, or interpretation before commitment.

### I1.3 Identity distinction
**RIDI selected identity** and **CFC evidence-record identity** are different protocol concepts. Mapping one to the other may establish which underlying item is being referenced, but cannot create evidence authority, provenance, semantic support, scope, freshness, dependency status, or independence.

### I1.4 Both sides
Before both commitments:
- no discussion of expected asymmetry;
- no replacement of the selected case;
- no mapper changes;
- no threshold changes;
- no new authority evidence created after selection.

## 4. Post-commit exchange

After both bundle hashes are committed and exact bundles are exchanged/verified, both parties may inspect:
- the other's mapped inputs;
- raw outputs;
- logs;
- versions/configuration;
- hash manifests;
- ground-truth correctness for secondary analysis;
- derived pair classification.

Interpretation begins only after verification.

## 5. Violations

Any pre-commit inspection outside this matrix is a protocol deviation and must be logged.

A material violation that could reveal the other side's substantive result triggers a versioned reset rather than silent continuation.
