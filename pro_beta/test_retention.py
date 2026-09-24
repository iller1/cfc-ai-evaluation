from __future__ import annotations

import json
import os
import unittest
from uuid import uuid4

from pro_beta.retention import build_retention_summary, run_retention_once


class FoundingBetaRetentionTests(unittest.TestCase):
    def test_summary_keeps_only_aggregate_learning_fields(self):
        rows = [
            {
                "measurement_id": "fbm_secret_1",
                "workspace_id": "ws_company_a",
                "case_id": "CUSTOMER-CASE-777",
                "comment": "do not archive this",
                "reason_code": "verbose reason",
                "hawm_state": "internal state",
                "system_version": "founding-beta-rc1",
                "workflow_type": "decision_support",
                "cfc_result": "ALLOW",
                "human_assessment": "AGREE",
                "final_action": "ACTED",
                "problem_type": "NONE",
                "created_at": "2026-09-01T00:00:00+00:00",
            },
            {
                "measurement_id": "fbm_secret_2",
                "workspace_id": "ws_company_b",
                "case_id": "CUSTOMER-CASE-888",
                "comment": "also do not archive",
                "reason_code": "another reason",
                "hawm_state": "another state",
                "system_version": "founding-beta-rc1",
                "workflow_type": "decision_support",
                "cfc_result": "STOP",
                "human_assessment": "DISAGREE",
                "final_action": "DID_NOT_ACT",
                "problem_type": "FALSE_STOP",
                "created_at": "2026-09-02T00:00:00+00:00",
            },
        ]

        summary = build_retention_summary(rows)
        encoded = json.dumps(summary)

        self.assertEqual(summary["source_record_count"], 2)
        self.assertEqual(summary["cfc_result_counts"], {"ALLOW": 1, "STOP": 1})
        self.assertEqual(summary["problem_type_counts"], {"FALSE_STOP": 1, "NONE": 1})
        for forbidden in (
            "fbm_secret",
            "ws_company",
            "CUSTOMER-CASE",
            "do not archive",
            "reason",
            "internal state",
        ):
            self.assertNotIn(forbidden, encoded)

    def test_empty_summary_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "RETENTION_REPORT_REQUIRES_ROWS"):
            build_retention_summary([])


@unittest.skipUnless(
    os.environ.get("PRO_BETA_TEST_DATABASE_URL"),
    "PRO_BETA_TEST_DATABASE_URL not configured",
)
class FoundingBetaRetentionPostgresTests(unittest.TestCase):
    def test_archive_then_delete_respects_14_day_cutoff(self):
        import psycopg

        from pro_beta.db_bootstrap import ensure_schema

        database_url = os.environ["PRO_BETA_TEST_DATABASE_URL"]
        ensure_schema(database_url)

        suffix = uuid4().hex
        user_id = "usr_ret_" + suffix
        workspace_id = "ws_ret_" + suffix
        old_id = "fbm_old_" + suffix
        recent_id = "fbm_recent_" + suffix

        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into users (user_id, external_auth_subject, email)
                    values (%s, %s, %s)
                    """,
                    (user_id, "ret|" + suffix, None),
                )
                cur.execute(
                    """
                    insert into workspaces (workspace_id, user_id, name)
                    values (%s, %s, %s)
                    """,
                    (workspace_id, user_id, "Retention test"),
                )
                for measurement_id, age_days, result, problem in (
                    (old_id, 15, "STOP", "FALSE_STOP"),
                    (recent_id, 13, "ALLOW", "NONE"),
                ):
                    cur.execute(
                        """
                        insert into founding_beta_measurements (
                            measurement_id, workspace_id, system_version,
                            workflow_type, case_id, cfc_result, reason_code,
                            hawm_state, human_assessment, final_action,
                            problem_type, comment, created_at
                        )
                        values (
                            %s, %s, 'founding-beta-rc1', 'decision_support',
                            %s, %s, 'test reason', 'test state', 'AGREE',
                            'DID_NOT_ACT', %s, null,
                            now() - make_interval(days => %s)
                        )
                        """,
                        (
                            measurement_id,
                            workspace_id,
                            "CASE-" + measurement_id,
                            result,
                            problem,
                            age_days,
                        ),
                    )
            conn.commit()

        outcome = run_retention_once(database_url, retention_days=14)
        self.assertEqual(outcome["status"], "ARCHIVED_AND_DELETED")
        self.assertGreaterEqual(outcome["deleted_measurements"], 1)

        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select measurement_id
                    from founding_beta_measurements
                    where measurement_id = any(%s)
                    order by measurement_id
                    """,
                    ([old_id, recent_id],),
                )
                remaining = [row[0] for row in cur.fetchall()]
                self.assertEqual(remaining, [recent_id])

                cur.execute(
                    """
                    select summary
                    from founding_beta_retention_reports
                    where report_id = %s
                    """,
                    (outcome["report_id"],),
                )
                summary = cur.fetchone()[0]
                encoded = json.dumps(summary)
                self.assertEqual(summary["cfc_result_counts"]["STOP"], 1)
                self.assertNotIn(old_id, encoded)
                self.assertNotIn(workspace_id, encoded)

                cur.execute(
                    "delete from founding_beta_retention_reports where report_id = %s",
                    (outcome["report_id"],),
                )
                cur.execute(
                    "delete from founding_beta_measurements where measurement_id = %s",
                    (recent_id,),
                )
                cur.execute("delete from workspaces where workspace_id = %s", (workspace_id,))
                cur.execute("delete from users where user_id = %s", (user_id,))
            conn.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
