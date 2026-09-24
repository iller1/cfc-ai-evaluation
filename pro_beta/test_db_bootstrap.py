from __future__ import annotations

import os
import unittest

from pro_beta.db_bootstrap import DatabaseBootstrapError, ensure_schema

try:
    import psycopg
except ImportError:
    psycopg = None


class DatabaseBootstrapUnitTests(unittest.TestCase):
    def test_missing_database_url_fails_closed(self):
        with self.assertRaisesRegex(
            DatabaseBootstrapError, "DATABASE_URL_REQUIRED"
        ):
            ensure_schema("")


@unittest.skipIf(psycopg is None, "psycopg is not installed")
class DatabaseBootstrapIntegrationTests(unittest.TestCase):
    def test_schema_bootstrap_is_idempotent(self):
        dsn = os.environ.get("PRO_BETA_TEST_DATABASE_URL")
        if not dsn:
            raise unittest.SkipTest("PRO_BETA_TEST_DATABASE_URL is not set")

        first = ensure_schema(dsn)
        second = ensure_schema(dsn)
        self.assertEqual(first, second)
        self.assertEqual(
            set(first),
            {
                "users",
                "workspaces",
                "conversations",
                "messages",
                "hawm_snapshots",
                "cfc_runs",
                "audit_reports",
                "benchmark_runs",
                "benchmark_manual_labels",
                "founding_beta_measurements",
                "founding_beta_retention_reports",
                "usage_events",
            },
        )

        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select to_regclass('public.users'),
                           to_regclass('public.workspaces'),
                           to_regclass('public.conversations'),
                           to_regclass('public.messages'),
                           to_regclass('public.hawm_snapshots'),
                           to_regclass('public.cfc_runs')
                    """
                )
                row = cur.fetchone()

        self.assertEqual(
            row,
            (
                "users",
                "workspaces",
                "conversations",
                "messages",
                "hawm_snapshots",
                "cfc_runs",
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
