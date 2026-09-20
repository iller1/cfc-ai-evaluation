from __future__ import annotations

import unittest

from pro_beta.bridge_acceptance import (
    SCENARIOS,
    run_bridge_acceptance_pack,
)


class HAWMCFCBridgeAcceptanceTests(unittest.TestCase):
    def test_acceptance_pack_has_seven_named_scenarios(self):
        self.assertEqual(len(SCENARIOS), 7)
        self.assertEqual(
            [scenario.scenario_id for scenario in SCENARIOS],
            [
                "BRIDGE_01_SUFFICIENT_SUPPORT",
                "BRIDGE_02_INSUFFICIENT_SUPPORT",
                "BRIDGE_03_ACTIVE_CONTRADICTION",
                "BRIDGE_04_STALE_EVIDENCE",
                "BRIDGE_05_WRONG_SCOPE",
                "BRIDGE_06_INDEPENDENCE_AUTHORITY_AB_ALLOW",
                "BRIDGE_07_SHARED_LINEAGE",
            ],
        )

    def test_bridge_acceptance_pack_passes_against_frozen_anchor(self):
        report = run_bridge_acceptance_pack()
        self.assertEqual(report["pack"], "HAWM_CFC_BRIDGE_ACCEPTANCE_V1")
        self.assertEqual(report["controller_anchor"], "0.2.90rc1")
        self.assertEqual(report["scenario_count"], 7)
        self.assertEqual(
            report["boundary"],
            "BOUNDED_STRUCTURED_SYNTHETIC_INPUT_NOT_FREE_TEXT_ANALYSIS",
        )
        self.assertTrue(
            report["passed"],
            msg="bridge acceptance failures: "
            + repr(
                [
                    row
                    for row in report["results"]
                    if not row["passed"]
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
