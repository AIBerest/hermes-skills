import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from chip_supergoal.model import canonical_json, contract_from_dict, load_contract
from chip_supergoal.normalize import semantic_errors
from chip_supergoal.policy import load_risk_policy

class ContractModelTest(unittest.TestCase):
    def fixture(self):
        return json.loads((ROOT / "examples/brownfield-feature/CONTRACT.json").read_text())

    def test_contract_loads_and_serializes_canonically(self):
        contract = load_contract(ROOT / "examples/brownfield-feature/CONTRACT.json")
        encoded = canonical_json(contract)
        self.assertTrue(encoded.endswith("\n"))
        self.assertEqual(encoded, canonical_json(contract))
        self.assertEqual(contract.goal.id, "sg-20260625-brownfield-feature")

    def test_unknown_fields_are_rejected_in_strict_mode(self):
        data = self.fixture()
        data["unexpected"] = True
        with self.assertRaises(ValueError):
            contract_from_dict(data, strict=True)

    def test_duplicate_phase_id_is_rejected(self):
        data = self.fixture()
        data["phases"].append(deepcopy(data["phases"][0]))
        data["phases"][1]["ordinal"] = 2
        contract = contract_from_dict(data)
        self.assertTrue(any("duplicate phase id" in e or "duplicate id" in e for e in semantic_errors(contract, load_risk_policy(ROOT / "spec/risk-policy.json"))))

    def test_missing_dependency_is_rejected(self):
        data = self.fixture()
        data["phases"][0]["depends_on"] = ["P99"]
        contract = contract_from_dict(data)
        self.assertIn("P01 depends on missing phase P99", semantic_errors(contract, load_risk_policy(ROOT / "spec/risk-policy.json")))

    def test_dependency_cycle_is_rejected(self):
        data = self.fixture()
        second = deepcopy(data["phases"][0])
        second["id"] = "P02"; second["ordinal"] = 2; second["depends_on"] = ["P01"]
        second["criteria"][0]["id"] = "P02-C01"; second["criteria"][0]["verifier"]["command_id"] = "P02-CMD01"
        second["commands"][0]["id"] = "P02-CMD01"; second["deliverables"][0]["id"] = "P02-D01"
        data["phases"][0]["depends_on"] = ["P02"]
        data["phases"].append(second)
        contract = contract_from_dict(data)
        self.assertTrue(any("dependency cycle" in e for e in semantic_errors(contract, load_risk_policy(ROOT / "spec/risk-policy.json"))))

    def test_risky_phase_without_required_rpd_focus_is_rejected(self):
        data = self.fixture()
        data["phases"][0]["rpd"] = {"required": False, "focus": []}
        contract = contract_from_dict(data)
        errors = semantic_errors(contract, load_risk_policy(ROOT / "spec/risk-policy.json"))
        self.assertTrue(any("requires RPD" in e for e in errors))
        self.assertTrue(any("missing RPD focus" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
