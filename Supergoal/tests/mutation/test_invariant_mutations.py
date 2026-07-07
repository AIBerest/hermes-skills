import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from chip_supergoal.model import contract_from_dict
from chip_supergoal.normalize import semantic_errors
from chip_supergoal.policy import load_risk_policy

class InvariantMutationTest(unittest.TestCase):
    def fixture(self):
        return json.loads((ROOT / "examples/brownfield-feature/CONTRACT.json").read_text())

    def test_mutation_second_launch_body_is_killed(self):
        with tempfile.TemporaryDirectory() as td:
            pkg = Path(td) / "pkg"; pkg.mkdir()
            for name in ["THINKING.md", "LOOP_DESIGN.md", "ROADMAP.md", "STATE.md", "PROTOCOL.md", "LAUNCH_GOAL.md"]:
                (pkg / name).write_text("# x\n", encoding="utf-8")
            (pkg / "LAUNCH_GOAL.md").write_text("SUPERGOAL_GOAL_BODY: ok\n", encoding="utf-8")
            (pkg / "ROADMAP.md").write_text("SUPERGOAL_GOAL_BODY: mutated\n", encoding="utf-8")
            result = subprocess.run([sys.executable, "scripts/sgctl.py", "validate-package", str(pkg), "--format", "json"], cwd=ROOT, text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SGV-PACKAGE-LAUNCH-MARKER", {d["code"] for d in json.loads(result.stdout)})

    def test_mutation_risky_rpd_requirement_removed_is_killed(self):
        data = self.fixture()
        data["phases"][0]["rpd"] = {"required": False, "focus": []}
        errors = semantic_errors(contract_from_dict(data), load_risk_policy(ROOT / "spec/risk-policy.json"))
        self.assertTrue(any("requires RPD" in e for e in errors))

    def test_mutation_placeholder_command_is_killed(self):
        data = self.fixture()
        data["phases"][0]["commands"][0]["command"] = "TBD"
        errors = semantic_errors(contract_from_dict(data), load_risk_policy(ROOT / "spec/risk-policy.json"))
        self.assertTrue(any("placeholder command" in e for e in errors))

    def test_mutation_missing_evidence_blocks_audit(self):
        from chip_supergoal.audit import audit_contract
        report = audit_contract(contract_from_dict(self.fixture()), [])
        self.assertFalse(report.can_complete)
        self.assertIn("AUDIT_GAP", {i.issue_type for i in report.issues})

if __name__ == "__main__":
    unittest.main()
