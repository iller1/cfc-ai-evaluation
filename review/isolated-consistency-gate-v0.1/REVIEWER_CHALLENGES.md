# CFC · Reviewer challenges and falsification targets

**Status:** OPEN FOR TECHNICAL CRITIQUE — NOT INDEPENDENTLY VALIDATED.

This document is an adversarial self-review of the [original reproduction package](./CFC_NATIVE_ISOLATED_CONSISTENCY_GATE_DEV_v0_1.zip), not a third-party endorsement. The frozen Anchor wheel is unchanged.

## Reproduced evidence

- Operator on Windows (2026-10-15): 16/16 local harness tests passed.
- Follow-up Linux replay of the **same** package and byte-matched frozen wheel: 16/16 harness tests passed. These are two environments, **not two independent implementations**.
- Authored counterfactual: only E3.value changes from `safe` to `unsafe` (content-bound role ID and derived artifacts are regenerated).
- Both cases retain claim state `VERIFIED`.
- Aligned case: all gates true; native internal `control_closure=true`.
- Conflicting case: exactly `global_consistency_valid=false`; native internal `control_closure=false`; conflicts identified for E1–E3 and E2–E3.
- Public F01 NOAA ingestion / independent custody: **not tested**. Production authorization: **false**.

## Priority objections — please try to falsify these claims

1. **Test fixture dependence.** The runner verifies the wheel hash, extracts original `self_tests` helpers using an AST, *modifies a copy of the fixture function* to parameterize E3.value, and executes that copy in the engine module. The engine bytes are not edited, but this **is not a direct public API experiment**. Investigate whether the result holds without the fixture-only role/scope setup.
2. **Independence and source authority.** `r23_case` registers three synthetic provenance sources, issues synthetic support-set independence certificates, and selects the first two supports while classifying the third `EXCLUDED_NOT_NEEDED`. Those records do not prove independence or trusted authority for real data.
3. **Challenge the selection policy.** Swap which evidence is selected versus excluded; introduce shared failure domains, duplicate sources, alias identities, unresolved relationships and contradictory source semantics. In particular, can a conflicting *excluded* record ever be omitted from the global consistency check, leading to false closure?
4. **Check the oracle.** Many harness assertions derive from the same native result being tested. Confirm gate completeness and the meaning of `VERIFIED` against the actual source code; avoid mistaking 16 passing assertions for 16 independent demonstrations. The report's `production_authorization=false` is a declared scope flag, **not a proof of external authorization checks**.
5. **Boundary to real-world evidence.** Specify how a real provider's temporal scope, source identity, failure domain, issuer ancestry and trust are established without synthetic certificates. This question remains OPEN; `NOAA → Controller.evaluate` is NOT_ESTABLISHED.

## One additional exploratory probe (not part of 16/16)

On a *temporary copy of the external runner only*, I expanded the E3-value test to include `calm` (unmodelled relation). The original wheel remained byte-identical. One exploratory execution observed:

| E3 value | Claim | Global consistency | Failed gates | Internal closure |
| --- | --- | --- | --- | --- |
| `safe` | VERIFIED | true | none | true |
| `unsafe` | VERIFIED | false | `global_consistency_valid` | false |
| `calm` | VERIFIED | true | `constraint_relation_coverage_sufficient` | false |

The `calm` result indicates a **separate fail-closed route for unmodelled relationships**, not proof of general semantic understanding. It has **not** been integrated into the original 16-case verified package or independently validated.

A reviewer can reproduce this optional exploratory variation by copying `reproduce_isolated.py` to another filename and changing only the external wrapper's scenario iterable, from

```python
[('aligned','safe'),('conflicting','unsafe')]
```

to

```python
[('aligned','safe'),('conflicting','unsafe'),('unmodelled','calm')]
```

Then inspect `cases.unmodelled.failed_gates` in the generated output JSON. This is **not** a change to the frozen wheel and is **not** a certified new test.

## Explicit limits

The publication supports a narrow observation: a specific, known native synthetic fixture distinguishes an explicit contradiction from an aligned state and blocks closure despite `VERIFIED`. It does **not** establish the performance of a generalized AI system, independent assurance, NOAA ingestion, production safety or permission to deploy.

Frozen boundaries: Anchor FROZEN · F01 HOLD · G10/G13/G14 BLOCK · R273 NO_GO.

## Polish summary / Podsumowanie

Wynik 16/16 został odtworzony na Windows i Linuxie, ale oba uruchomienia używają tego samego kodu reproduktora i syntetycznych certyfikatów. Krytyczna ocena musi zakwestionować poprawność selekcji dowodów, niezależność źródeł, założenia pochodzenia oraz działanie poza wewnętrznym trybem testowym. Eksploracyjna wartość `calm` dała blokadę `constraint_relation_coverage_sufficient` przy zachowanym `VERIFIED`, ale ten wariant nie należy do oryginalnych 16 testów.
