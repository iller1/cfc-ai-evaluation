from __future__ import annotations

import os
from pathlib import Path


SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class DatabaseBootstrapError(RuntimeError):
    pass


def ensure_schema(database_url: str) -> None:
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
            conn.commit()
    except Exception as exc:
        raise DatabaseBootstrapError("DATABASE_SCHEMA_BOOTSTRAP_FAILED") from exc


def bootstrap_from_environment() -> None:
    ensure_schema(os.environ.get("DATABASE_URL", ""))
