#!/usr/bin/env python3
"""Outcome-independent eligibility checker for CFC-RIDI v0.1.

This checker uses pre-selection registry facts only. It must not execute CFC,
execute RIDI, compare A/B verdicts for equivalence, inspect hidden correctness,
or rank candidates by scientific interest.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

HEX64 = set("0123456789abcdef")

REGISTRY_COLUMNS = [
    "case_id",
    "source_a_sha256",
    "offline_endpoint_a_sha256",
    "source_ref_a",
    "source_b_sha256",
    "offline_endpoint_b_sha256",
    "source_ref_b",
    "evaluation_definition_id",
    "evaluation_definition_sha256",
    "original_support_requirement_status",
    "offline_endpoint_present",
    "m1_representable",
    "a1_preexisting_authority_available",
    "i1_compatible",
    "no_consequential_execution",
    "prior_public_exposure",
    "outcome_independent_eligibility_attestation",
    "eligibility_rationale",
]

POOL_COLUMNS = [
    "case_id",
    "pair_fingerprint",
    "source_a_sha256",
    "offline_endpoint_a_sha256",
    "source_ref_a",
    "source_b_sha256",
    "offline_endpoint_b_sha256",
    "source_ref_b",
    "evaluation_definition_id",
    "evaluation_definition_sha256",
    "original_support_requirement_status",
    "prior_public_exposure",
    "eligibility_rationale",
]

AUDIT_COLUMNS = [
    "case_id",
    "pair_fingerprint",
    "eligibility_status",
    "reason_codes",
    "registry_row_sha256",
    "checker_sha256",
]

ELIGIBLE_SUPPORT_STATUS = {
    "AUTHORITATIVE_1",
    "NO_AUTHORITATIVE_REQUIREMENT_SPECIFIED",
}
ALL_SUPPORT_STATUS = ELIGIBLE_SUPPORT_STATUS | {"AUTHORITATIVE_GT1", "UNKNOWN"}
BOOL_FIELDS = [
    "offline_endpoint_present",
    "m1_representable",
    "a1_preexisting_authority_available",
    "i1_compatible",
    "no_consequential_execution",
    "outcome_independent_eligibility_attestation",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_hex64(value: str) -> bool:
    return len(value) == 64 and all(ch in HEX64 for ch in value)


def read_lf_utf8(path: Path) -> bytes:
    data = path.read_bytes()
    if b"\r" in data:
        raise ValueError("registry must use LF only")
    if not data.endswith(b"\n"):
        raise ValueError("registry must be LF-terminated")
    data.decode("utf-8")
    return data


def arm_binding(source_sha: str, endpoint_sha: str) -> str:
    msg = f"CFC-RIDI-ARM-v0.1|{source_sha}|{endpoint_sha}".encode("utf-8")
    return sha256(msg)


def pair_fingerprint(row: dict[str, str]) -> str:
    a = arm_binding(row["source_a_sha256"], row["offline_endpoint_a_sha256"])
    b = arm_binding(row["source_b_sha256"], row["offline_endpoint_b_sha256"])
    lo, hi = sorted((a, b))
    return sha256(f"CFC-RIDI-PAIR-v0.1|{lo}|{hi}".encode("utf-8"))


def registry_row_sha(row: dict[str, str]) -> str:
    # Parsed registry rows carry the SHA-256 of their exact source-line bytes.
    # Direct in-memory unit-test rows fall back to the canonical declared-column form.
    exact_source_sha = row.get("__registry_row_sha256")
    if exact_source_sha:
        return exact_source_sha
    exact = "\t".join(row[c] for c in REGISTRY_COLUMNS) + "\n"
    return sha256(exact.encode("utf-8"))


def canonical_metadata(row: dict[str, str]) -> tuple:
    arms = [
        (
            row["source_a_sha256"],
            row["offline_endpoint_a_sha256"],
            row["source_ref_a"],
        ),
        (
            row["source_b_sha256"],
            row["offline_endpoint_b_sha256"],
            row["source_ref_b"],
        ),
    ]
    arms.sort()
    return (
        tuple(arms),
        row["evaluation_definition_id"],
        row["evaluation_definition_sha256"],
        row["original_support_requirement_status"],
        row["offline_endpoint_present"],
        row["m1_representable"],
        row["a1_preexisting_authority_available"],
        row["i1_compatible"],
        row["no_consequential_execution"],
        row["prior_public_exposure"],
        row["outcome_independent_eligibility_attestation"],
    )


def base_reasons(row: dict[str, str]) -> list[str]:
    reasons: list[str] = []

    if not row["case_id"] or any(ord(ch) < 33 or ord(ch) > 126 for ch in row["case_id"]):
        reasons.append("INVALID_CASE_ID")

    for field in (
        "source_a_sha256",
        "offline_endpoint_a_sha256",
        "source_b_sha256",
        "offline_endpoint_b_sha256",
        "evaluation_definition_sha256",
    ):
        if not is_hex64(row[field]):
            reasons.append(f"INVALID_{field.upper()}")

    for field in ("source_ref_a", "source_ref_b", "evaluation_definition_id", "eligibility_rationale"):
        if not row[field].strip():
            reasons.append(f"MISSING_{field.upper()}")

    support = row["original_support_requirement_status"]
    if support not in ALL_SUPPORT_STATUS:
        reasons.append("INVALID_SUPPORT_REQUIREMENT_STATUS")
    elif support == "AUTHORITATIVE_GT1":
        reasons.append("AUTHORITATIVE_SUPPORT_REQUIREMENT_GT1")
    elif support == "UNKNOWN":
        reasons.append("ORIGINAL_SUPPORT_REQUIREMENT_UNKNOWN")

    for field in BOOL_FIELDS:
        if row[field] not in {"TRUE", "FALSE"}:
            reasons.append(f"INVALID_{field.upper()}")
        elif row[field] != "TRUE":
            reasons.append(f"{field.upper()}_FALSE")

    if row["prior_public_exposure"] not in {"TRUE", "FALSE", "UNKNOWN"}:
        reasons.append("INVALID_PRIOR_PUBLIC_EXPOSURE")

    return reasons


def parse_registry(path: Path) -> tuple[list[dict[str, str]], str]:
    data = read_lf_utf8(path)
    text = data.decode("utf-8")

    # Parse the TSV as a canonical byte-oriented format, not as permissive CSV.
    # This deliberately rejects quoted/embedded delimiters, extra fields, missing
    # fields, blank rows and multiline fields so the audited row bytes are exact.
    lines = text[:-1].split("\n")  # final LF already required by read_lf_utf8()
    expected_header = "\t".join(REGISTRY_COLUMNS)
    if not lines or lines[0] != expected_header:
        raise ValueError("candidate registry header/schema mismatch")

    rows: list[dict[str, str]] = []
    expected_fields = len(REGISTRY_COLUMNS)
    for line_no, raw_line in enumerate(lines[1:], start=2):
        if raw_line == "":
            raise ValueError(f"line {line_no}: blank registry row is noncanonical")

        fields = raw_line.split("\t")
        if len(fields) != expected_fields:
            raise ValueError(
                f"line {line_no}: noncanonical TSV shape; expected "
                f"{expected_fields} fields, got {len(fields)}"
            )

        row = dict(zip(REGISTRY_COLUMNS, fields, strict=True))
        row["__registry_row_sha256"] = sha256((raw_line + "\n").encode("utf-8"))
        rows.append(row)

    if not rows:
        raise ValueError("candidate registry contains no registrations")

    ids = [r["case_id"] for r in rows]
    if ids != sorted(ids):
        raise ValueError("candidate registry must be sorted lexicographically by case_id")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate case_id in candidate registry")
    return rows, sha256(data)


def write_tsv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    lines = ["\t".join(columns)]
    for row in rows:
        lines.append("\t".join(row[c] for c in columns))
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def evaluate(rows: list[dict[str, str]], checker_sha: str):
    preliminary = []
    by_pair: dict[str, list[dict]] = {}

    for row in rows:
        reasons = base_reasons(row)
        fp = pair_fingerprint(row) if all(
            is_hex64(row[f]) for f in (
                "source_a_sha256",
                "offline_endpoint_a_sha256",
                "source_b_sha256",
                "offline_endpoint_b_sha256",
            )
        ) else ""
        item = {
            "row": row,
            "pair_fingerprint": fp,
            "reasons": reasons,
            "registry_row_sha256": registry_row_sha(row),
        }
        preliminary.append(item)
        if fp:
            by_pair.setdefault(fp, []).append(item)

    for fp, items in by_pair.items():
        if len(items) <= 1:
            continue
        signatures = {canonical_metadata(x["row"]) for x in items}
        if len(signatures) > 1:
            for x in items:
                x["reasons"].append("DUPLICATE_PAIR_METADATA_CONFLICT")
        else:
            keep = min(items, key=lambda x: x["row"]["case_id"])
            for x in items:
                if x is not keep:
                    x["reasons"].append("DUPLICATE_PAIR_REGISTRATION")

    audit_rows = []
    pool_rows = []
    for item in preliminary:
        row = item["row"]
        reasons = sorted(set(item["reasons"]))
        status = "ACCEPT" if not reasons else "REJECT"
        audit_rows.append({
            "case_id": row["case_id"],
            "pair_fingerprint": item["pair_fingerprint"],
            "eligibility_status": status,
            "reason_codes": ",".join(reasons) if reasons else "NONE",
            "registry_row_sha256": item["registry_row_sha256"],
            "checker_sha256": checker_sha,
        })
        if status == "ACCEPT":
            pool_rows.append({
                "case_id": row["case_id"],
                "pair_fingerprint": item["pair_fingerprint"],
                "source_a_sha256": row["source_a_sha256"],
                "offline_endpoint_a_sha256": row["offline_endpoint_a_sha256"],
                "source_ref_a": row["source_ref_a"],
                "source_b_sha256": row["source_b_sha256"],
                "offline_endpoint_b_sha256": row["offline_endpoint_b_sha256"],
                "source_ref_b": row["source_ref_b"],
                "evaluation_definition_id": row["evaluation_definition_id"],
                "evaluation_definition_sha256": row["evaluation_definition_sha256"],
                "original_support_requirement_status": row["original_support_requirement_status"],
                "prior_public_exposure": row["prior_public_exposure"],
                "eligibility_rationale": row["eligibility_rationale"],
            })

    audit_rows.sort(key=lambda r: r["case_id"])
    pool_rows.sort(key=lambda r: r["case_id"])
    return audit_rows, pool_rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("candidate_registry")
    p.add_argument("--audit-out", required=True)
    p.add_argument("--pool-out", required=True)
    args = p.parse_args()

    checker_sha = sha256(Path(__file__).read_bytes())
    rows, registry_sha = parse_registry(Path(args.candidate_registry))
    audit, pool = evaluate(rows, checker_sha)

    write_tsv(Path(args.audit_out), AUDIT_COLUMNS, audit)
    write_tsv(Path(args.pool_out), POOL_COLUMNS, pool)

    print(f"checker_sha256={checker_sha}")
    print(f"candidate_registry_sha256={registry_sha}")
    print(f"registration_count={len(rows)}")
    print(f"accepted_count={sum(r['eligibility_status']=='ACCEPT' for r in audit)}")
    print(f"rejected_count={sum(r['eligibility_status']=='REJECT' for r in audit)}")
    print(f"eligibility_audit_sha256={sha256(Path(args.audit_out).read_bytes())}")
    print(f"eligible_pool_sha256={sha256(Path(args.pool_out).read_bytes())}")


if __name__ == "__main__":
    main()
