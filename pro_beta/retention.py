from __future__ import annotations

import json
import os
import threading
import time
from collections import Counter
from typing import Any
from uuid import uuid4


DEFAULT_RETENTION_DAYS = 14
DEFAULT_CHECK_INTERVAL_SECONDS = 3600
_ADVISORY_LOCK_ID = 684214091427


def _count(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def build_retention_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a content-minimized aggregate before source measurements are deleted.

    Intentionally excluded: user/workspace identity, measurement_id, case_id,
    reason_code, hawm_state, comments and any customer content.
    """
    if not rows:
        raise ValueError("RETENTION_REPORT_REQUIRES_ROWS")

    created = sorted(str(row["created_at"]) for row in rows)
    return {
        "retention_report_schema": 1,
        "source_record_count": len(rows),
        "source_created_at_first": created[0],
        "source_created_at_last": created[-1],
        "system_version_counts": _count(rows, "system_version"),
        "workflow_type_counts": _count(rows, "workflow_type"),
        "cfc_result_counts": _count(rows, "cfc_result"),
        "human_assessment_counts": _count(rows, "human_assessment"),
        "final_action_counts": _count(rows, "final_action"),
        "problem_type_counts": _count(rows, "problem_type"),
    }


def run_retention_once(database_url: str, retention_days: int = DEFAULT_RETENTION_DAYS) -> dict[str, Any]:
    """Archive aggregate statistics, then delete the exact expired source rows.

    Report insertion and source deletion happen in one PostgreSQL transaction.
    A transaction-scoped advisory lock prevents concurrent workers from creating
    duplicate reports for the same source rows.
    """
    if not database_url:
        raise ValueError("DATABASE_URL_REQUIRED")
    if retention_days < 1:
        raise ValueError("RETENTION_DAYS_INVALID")

    import psycopg

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("select pg_try_advisory_xact_lock(%s)", (_ADVISORY_LOCK_ID,))
            if not bool(cur.fetchone()[0]):
                return {
                    "status": "SKIPPED_LOCK_HELD",
                    "retention_days": retention_days,
                    "source_record_count": 0,
                    "deleted_measurements": 0,
                    "report_id": None,
                }

            cur.execute(
                "select now() - make_interval(days => %s)",
                (retention_days,),
            )
            cutoff_at = cur.fetchone()[0]

            cur.execute(
                """
                select measurement_id, system_version, workflow_type,
                       cfc_result, human_assessment, final_action,
                       problem_type, created_at
                from founding_beta_measurements
                where created_at < %s
                order by created_at, measurement_id
                for update
                """,
                (cutoff_at,),
            )
            raw_rows = cur.fetchall()
            if not raw_rows:
                return {
                    "status": "NO_EXPIRED_RECORDS",
                    "retention_days": retention_days,
                    "cutoff_at": cutoff_at.isoformat(),
                    "source_record_count": 0,
                    "deleted_measurements": 0,
                    "report_id": None,
                }

            rows = [
                {
                    "measurement_id": row[0],
                    "system_version": row[1],
                    "workflow_type": row[2],
                    "cfc_result": row[3],
                    "human_assessment": row[4],
                    "final_action": row[5],
                    "problem_type": row[6],
                    "created_at": row[7].isoformat(),
                }
                for row in raw_rows
            ]
            summary = build_retention_summary(rows)
            report_id = "fbr_" + uuid4().hex

            cur.execute(
                """
                insert into founding_beta_retention_reports (
                    report_id, retention_days, cutoff_at,
                    source_record_count, summary
                )
                values (%s, %s, %s, %s, %s::jsonb)
                """,
                (
                    report_id,
                    retention_days,
                    cutoff_at,
                    len(rows),
                    json.dumps(summary, separators=(",", ":"), sort_keys=True),
                ),
            )

            ids = [row["measurement_id"] for row in rows]
            cur.execute(
                """
                delete from founding_beta_measurements
                where measurement_id = any(%s)
                """,
                (ids,),
            )
            deleted = int(cur.rowcount)
            if deleted != len(rows):
                raise RuntimeError("RETENTION_DELETE_COUNT_MISMATCH")

        conn.commit()

    return {
        "status": "ARCHIVED_AND_DELETED",
        "retention_days": retention_days,
        "cutoff_at": cutoff_at.isoformat(),
        "source_record_count": len(rows),
        "deleted_measurements": deleted,
        "report_id": report_id,
    }


def _worker_loop(database_url: str, retention_days: int, interval_seconds: int) -> None:
    while True:
        try:
            result = run_retention_once(database_url, retention_days)
            print(
                "FOUNDING_BETA_RETENTION " + json.dumps(result, separators=(",", ":"), sort_keys=True),
                flush=True,
            )
        except Exception as exc:
            print(
                "FOUNDING_BETA_RETENTION_ERROR "
                + json.dumps({"type": type(exc).__name__, "message": str(exc)}, separators=(",", ":")),
                flush=True,
            )
        time.sleep(interval_seconds)


def start_retention_worker_from_environment() -> threading.Thread | None:
    enabled = os.environ.get("FOUNDING_BETA_RETENTION_ENABLED", "true").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        return None

    database_url = os.environ.get("DATABASE_URL", "")
    retention_days = int(
        os.environ.get("FOUNDING_BETA_RETENTION_DAYS", str(DEFAULT_RETENTION_DAYS))
    )
    interval_seconds = int(
        os.environ.get(
            "FOUNDING_BETA_RETENTION_CHECK_SECONDS",
            str(DEFAULT_CHECK_INTERVAL_SECONDS),
        )
    )
    if interval_seconds < 60:
        raise ValueError("RETENTION_CHECK_INTERVAL_TOO_SHORT")

    worker = threading.Thread(
        target=_worker_loop,
        args=(database_url, retention_days, interval_seconds),
        name="founding-beta-retention",
        daemon=True,
    )
    worker.start()
    return worker
