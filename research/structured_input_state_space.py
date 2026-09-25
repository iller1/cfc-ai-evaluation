from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import product
from typing import Iterable

CONCLUSIONS = ("POSITIVE", "NEGATIVE")
REQUIRED_SUPPORTS = (1, 2)
SCOPES = ("EXPECTED", "WRONG")
PROVENANCE_SHAPES = ("DISTINCT", "SHARED_LINEAGE")
INDEPENDENCE_AUTHORITIES = ("NONE", "VERIFIED")
POLARITIES = ("POSITIVE", "NEGATIVE")
VALIDITIES = ("CURRENT", "STALE")
E2_MODES = ("OMIT", "INCLUDE")


@dataclass(frozen=True)
class StructuredState:
    conclusion: str
    required_independent_supports: int
    scope: str
    provenance_shape: str
    independence_authority: str
    e1_polarity: str
    e1_validity: str
    e2_mode: str
    e2_polarity: str | None = None
    e2_validity: str | None = None

    @property
    def admissible(self) -> bool:
        return not (
            self.provenance_shape == "SHARED_LINEAGE"
            and self.independence_authority == "VERIFIED"
        )

    def as_cfc_structured(self) -> dict:
        evidence = [
            {"polarity": self.e1_polarity, "validity": self.e1_validity}
        ]
        if self.e2_mode == "INCLUDE":
            evidence.append(
                {"polarity": self.e2_polarity, "validity": self.e2_validity}
            )
        return {
            "conclusion": self.conclusion,
            "required_independent_supports": self.required_independent_supports,
            "scope": self.scope,
            "provenance_shape": self.provenance_shape,
            "independence_authority": self.independence_authority,
            "evidence": evidence,
        }


def raw_ui_configurations() -> Iterable[tuple]:
    return product(
        CONCLUSIONS,
        REQUIRED_SUPPORTS,
        SCOPES,
        PROVENANCE_SHAPES,
        INDEPENDENCE_AUTHORITIES,
        POLARITIES,
        VALIDITIES,
        E2_MODES,
        POLARITIES,
        VALIDITIES,
    )


def canonical_states() -> list[StructuredState]:
    states: set[StructuredState] = set()
    for values in raw_ui_configurations():
        (
            conclusion,
            required,
            scope,
            provenance,
            independence,
            e1_pol,
            e1_valid,
            e2_mode,
            e2_pol,
            e2_valid,
        ) = values
        if e2_mode == "OMIT":
            e2_pol = None
            e2_valid = None
        states.add(
            StructuredState(
                conclusion,
                required,
                scope,
                provenance,
                independence,
                e1_pol,
                e1_valid,
                e2_mode,
                e2_pol,
                e2_valid,
            )
        )
    return sorted(
        states,
        key=lambda s: tuple(str(v) for v in asdict(s).values()),
    )


def admissible_states() -> list[StructuredState]:
    return [state for state in canonical_states() if state.admissible]


MUTATION_FIELDS = (
    "conclusion",
    "required_independent_supports",
    "scope",
    "provenance_shape",
    "independence_authority",
    "e1_polarity",
    "e1_validity",
    "e2_mode",
    "e2_polarity",
    "e2_validity",
)


def differing_fields(a: StructuredState, b: StructuredState) -> list[str]:
    aa = asdict(a)
    bb = asdict(b)
    return [field for field in MUTATION_FIELDS if aa[field] != bb[field]]


def one_field_mutation_pairs(states: list[StructuredState] | None = None):
    rows = states or admissible_states()
    for i, a in enumerate(rows):
        for b in rows[i + 1 :]:
            diff = differing_fields(a, b)
            if len(diff) == 1:
                yield a, b, diff[0]


def mutation_family(field: str) -> str:
    return {
        "conclusion": "CLAIM_EVIDENCE_ALIGNMENT",
        "required_independent_supports": "SUPPORT_THRESHOLD",
        "scope": "SCOPE",
        "provenance_shape": "PROVENANCE_DEPENDENCY",
        "independence_authority": "INDEPENDENCE_AUTHORITY",
        "e1_polarity": "EVIDENCE_POLARITY",
        "e1_validity": "FRESHNESS",
        "e2_mode": "SUPPORT_COMPLETENESS",
        "e2_polarity": "SECOND_EVIDENCE_POLARITY",
        "e2_validity": "SECOND_EVIDENCE_FRESHNESS",
    }[field]


def summary() -> dict:
    canonical = canonical_states()
    admissible = [s for s in canonical if s.admissible]
    pairs = list(one_field_mutation_pairs(admissible))
    families: dict[str, int] = {}
    for _, _, field in pairs:
        family = mutation_family(field)
        families[family] = families.get(family, 0) + 1
    return {
        "raw_ui_configurations": 1024,
        "canonical_logical_states": len(canonical),
        "admissible_states": len(admissible),
        "rejected_contradictory_states": len(canonical) - len(admissible),
        "one_field_mutation_pairs": len(pairs),
        "mutation_families": dict(sorted(families.items())),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summary(), indent=2, sort_keys=True))
