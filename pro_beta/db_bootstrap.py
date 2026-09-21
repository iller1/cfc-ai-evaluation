from __future__ import annotations

import os
from pathlib import Path


SCHEMA_PATH = Path(__file__).with_name("schema.sql")
EXPECTED_TABLES = (
    "users",
    "workspaces",
    "conversations",
    "messages",
    "hawm_snapshots",
    "cfc_runs",
    "audit_reports",
    "benchmark_runs",
    "usage_events",
)


class DatabaseBootstrapError(RuntimeError):
    pass


def ensure_schema(database_url: str) -> tuple[str, ...]:
    if not database_url:
        raise DatabaseBootstrapError("DATABASE_URL_REQUIRED")

    try:
        import psycopg
    except ImportError as exc:
        raise DatabaseBootstrapError("PSYCOPG_NOT_INSTALLED") from exc

    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(schema)
                cur.execute(
                    """
                    select tablename
                    from pg_catalog.pg_tables
                    where schemaname = 'public'
                      and tablename = any(%s)
                    order by tablename
                    """,
                    (list(EXPECTED_TABLES),),
                )
                present = tuple(row[0] for row in cur.fetchall())
            conn.commit()
    except Exception as exc:
        raise DatabaseBootstrapError("DATABASE_SCHEMA_BOOTSTRAP_FAILED") from exc

    missing = tuple(sorted(set(EXPECTED_TABLES) - set(present)))
    if missing:
        raise DatabaseBootstrapError(
            "DATABASE_SCHEMA_INCOMPLETE:" + ",".join(missing)
        )
    return present


def bootstrap_from_environment() -> tuple[str, ...]:
    return ensure_schema(os.environ.get("DATABASE_URL", ""))
