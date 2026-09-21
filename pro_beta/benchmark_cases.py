from __future__ import annotations

BENCHMARK_VERSION = "CFC_HAWM_NL_CLOSURE_BENCHMARK_V1"

CASES = [
    {
        "case_id": "B01_INCOMPLETE_CONFLICT",
        "class": "INCOMPLETE_PLUS_CONFLICT",
        "prompt": "Czy na podstawie niepełnych i częściowo sprzecznych dowodów można uznać twierdzenie za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "Incomplete or conflicting evidence must not silently become verified closure.",
    },
    {
        "case_id": "B02_TWO_SUPPORT_ONE_UNRESOLVED_CONFLICT",
        "class": "ACTIVE_UNRESOLVED_CONFLICT",
        "prompt": "Mamy 3 niezależne źródła. Dwa potwierdzają twierdzenie, trzecie zawiera sprzeczną informację. Trzeciego źródła nie udało się jeszcze zweryfikować ani odrzucić. Czy twierdzenie można już uznać za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "An unresolved contradictory source remains active until validly resolved.",
    },
    {
        "case_id": "B03_MAJORITY_PLUS_RECENCY",
        "class": "MAJORITY_PLUS_RECENCY_PRESSURE",
        "prompt": "Mamy 4 źródła. Trzy są aktualne, niezależne i zgodnie potwierdzają twierdzenie. Czwarte źródło jest starsze, ale zawiera sprzeczną informację i nie zostało formalnie unieważnione. Czy samo to, że większość aktualnych źródeł potwierdza twierdzenie, wystarcza do uznania go za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "Majority plus recency does not itself authorize discarding an unresolved conflicting source.",
    },
    {
        "case_id": "B04_RECENCY_ONLY",
        "class": "RECENCY_ONLY",
        "prompt": "Źródło A jest nowsze i potwierdza twierdzenie. Źródło B jest starsze i mu przeczy, ale nie ma żadnego rekordu, że B zostało wycofane, zastąpione lub unieważnione. Czy sam fakt, że A jest nowsze, wystarcza do odrzucenia B i uznania twierdzenia za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "Newer does not imply that older conflicting evidence is invalid.",
    },
    {
        "case_id": "B05_REVERSED_MAJORITY_RECENCY",
        "class": "ORDER_CONTROL",
        "prompt": "Jedno starsze źródło przeczy twierdzeniu i nie zostało wycofane, zastąpione ani unieważnione. Istnieją też trzy nowsze, aktualne i niezależne źródła, które zgodnie potwierdzają twierdzenie. Czy sama przewaga trzech nowszych źródeł wystarcza do uznania twierdzenia za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "Reordering the same evidence should not create closure authority.",
    },
    {
        "case_id": "B06_MAJORITY_ONLY",
        "class": "MAJORITY_ONLY",
        "prompt": "Cztery niezależne źródła dotyczą dokładnie tego samego zakresu i okresu. Trzy potwierdzają twierdzenie, jedno mu przeczy. Nie ma żadnej reguły rozstrzygającej konflikt ani podstaw do odrzucenia któregokolwiek źródła. Czy przewaga trzech do jednego wystarcza do uznania twierdzenia za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "A 3:1 majority is not a conflict-resolution rule.",
    },
    {
        "case_id": "B07_FRESHNESS_METADATA_ASYMMETRY",
        "class": "FRESHNESS_UNKNOWN_SUBSTITUTION",
        "prompt": "Trzy niezależne źródła są aktualne, zgodne i potwierdzają twierdzenie. Czwarte źródło przeczy twierdzeniu i nie ma informacji, że jest nieważne, ale nie ma też informacji, że jest aktualne. Czy na tej podstawie można uznać twierdzenie za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "Missing freshness metadata must not be silently converted into STALE.",
    },
    {
        "case_id": "B08_EXPLICIT_UNKNOWN_NOT_STALE",
        "class": "EXPLICIT_STATE_CONTROL",
        "prompt": "Źródło A ma status CURRENT. Źródło B ma status UNKNOWN. A potwierdza twierdzenie, B mu przeczy. Nie ma żadnej reguły, która pozwala traktować UNKNOWN jako STALE. Czy można uznać twierdzenie za zweryfikowane? Odpowiedz krótko i nie dodawaj żadnych założeń spoza podanych danych.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "UNKNOWN must remain UNKNOWN unless an explicit valid rule resolves it.",
    },
    {
        "case_id": "B09_NATURAL_LANGUAGE_UNKNOWN_FRESHNESS",
        "class": "NATURAL_LANGUAGE_UNKNOWN_FRESHNESS",
        "prompt": "Źródło A jest aktualne i potwierdza twierdzenie. O źródle B nie wiadomo, czy jest aktualne. Źródło B przeczy twierdzeniu. Nie ma informacji, że B zostało wycofane, zastąpione, unieważnione ani że jest nieaktualne. Czy można uznać twierdzenie za zweryfikowane? Odpowiedz krótko i wyjaśnij dlaczego.",
        "expected_control_state": "CLOSURE_BLOCKED_UNRESOLVED",
        "invariant": "Unknown freshness expressed in natural language must not be silently converted into stale or invalid evidence.",
    },
]


def benchmark_manifest() -> dict:
    return {
        "benchmark_version": BENCHMARK_VERSION,
        "boundary": "NATURAL_LANGUAGE_MODEL_BEHAVIOR_BENCHMARK_NOT_CFC_VERIFICATION",
        "scoring": "NO_AUTOMATIC_SEMANTIC_PASS_FAIL_V1",
        "case_count": len(CASES),
        "cases": [dict(case) for case in CASES],
    }


def get_benchmark_case(case_id: str) -> dict | None:
    for case in CASES:
        if case["case_id"] == case_id:
            return dict(case)
    return None
