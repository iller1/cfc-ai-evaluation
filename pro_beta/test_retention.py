from __future__ import annotations

import json
import unittest

from pro_beta.retention import build_retention_summary


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
