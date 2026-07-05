import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from chip_supergoal.diagnostics import Diagnostic, has_blocking
from chip_supergoal.invariants import load_catalog, validate_catalog, invariant_ids

class DiagnosticsAndInvariantsTest(unittest.TestCase):
    def test_diagnostic_renders_human_and_json(self):
        d = Diagnostic(
            code="SGV-PHASE-COUNT-MISMATCH",
            severity="error",
            blocking_stage="preflight",
            invariant_id="INV-VALIDATOR-001",
            artifact="CONTRACT.json",
            pointer="/phases/0",
            message="Declared phase count does not match phases[] length",
            remediation="Regenerate counts from phases[]",
        )
        encoded = json.loads(d.to_json())
        self.assertEqual(encoded["code"], "SGV-PHASE-COUNT-MISMATCH")
        self.assertIn("INV-VALIDATOR-001", d.render_human())
        self.assertTrue(has_blocking([d]))

    def test_invalid_diagnostic_is_rejected(self):
        with self.assertRaises(ValueError):
            Diagnostic(
                code="BAD",
                severity="error",
                blocking_stage="preflight",
                invariant_id="INV-VALIDATOR-001",
                artifact="CONTRACT.json",
                pointer="/",
                message="bad",
                remediation="fix",
            )

    def test_invariant_catalog_is_complete_for_p1_hard_invariants(self):
        catalog = load_catalog(ROOT / "spec/invariant-catalog.json")
        errors = validate_catalog(catalog)
        self.assertEqual(errors, [])
        ids = invariant_ids(catalog)
        required = {
            "INV-BOUNDARY-001", "INV-GOAL-001", "INV-LAUNCH-001", "INV-CONTINUE-001",
            "INV-AUDIT-001", "INV-RPD-001", "INV-DELIVERY-001", "INV-RECOVERY-001",
            "INV-BLOCKER-001", "INV-REFERENCE-001", "INV-VALIDATOR-001", "INV-ARCHIVE-001",
        }
        self.assertTrue(required <= ids)
        for item in catalog["invariants"]:
            if item["severity_if_broken"] == "P1":
                self.assertTrue(item["tests"], item["id"])

if __name__ == "__main__":
    unittest.main()
