from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ResearchGateTest(unittest.TestCase):
    def load_contract(self) -> dict:
        return json.loads((ROOT / "examples/brownfield-feature/CONTRACT.json").read_text(encoding="utf-8"))

    def run_sgctl(self, *args: str):
        return subprocess.run([sys.executable, "scripts/sgctl.py", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_required_research_gate_blocks_without_satisfied_perplex_evidence(self):
        data = self.load_contract()
        data["compatibility"]["research_gate"] = {"required": True, "status": "blocked", "provider": "perplex", "sources": []}
        with tempfile.TemporaryDirectory() as td:
            contract = Path(td) / "CONTRACT.json"
            contract.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_sgctl("validate-contract", str(contract), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            codes = {d["code"] for d in json.loads(result.stdout)}
            self.assertIn("SGV-RESEARCH-REQUIRED", codes)
            self.assertIn("SGV-RESEARCH-SOURCES", codes)

    def test_non_perplex_provider_needs_unavailable_reason(self):
        data = self.load_contract()
        data["compatibility"]["research_gate"] = {
            "required": True,
            "status": "satisfied",
            "provider": "web",
            "query": "fixture",
            "summary": "This summary is long enough to describe web fallback research evidence for the plan.",
            "sources": [{"title": "Fixture", "url": "https://example.com", "provider": "web"}],
        }
        with tempfile.TemporaryDirectory() as td:
            contract = Path(td) / "CONTRACT.json"
            contract.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_sgctl("validate-contract", str(contract), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SGV-RESEARCH-PERPLEX-FIRST", {d["code"] for d in json.loads(result.stdout)})

    def test_compile_emits_research_markdown_and_machine_report(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "sg"
            result = self.run_sgctl("compile", "examples/brownfield-feature/CONTRACT.json", "--out", str(package))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((package / "RESEARCH.md").is_file())
            self.assertTrue((package / "reports" / "research.json").is_file())
            report = json.loads((package / "reports" / "research.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "satisfied")
            self.assertEqual(report["provider"], "perplex")
            valid = self.run_sgctl("validate-package", str(package), "--strict")
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

    def test_validate_package_catches_research_report_drift(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "sg"
            result = self.run_sgctl("compile", "examples/brownfield-feature/CONTRACT.json", "--out", str(package))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (package / "reports" / "research.json").write_text("{}\n", encoding="utf-8")
            drift = self.run_sgctl("validate-package", str(package), "--format", "json")
            self.assertNotEqual(drift.returncode, 0)
            self.assertIn("SGV-PACKAGE-GENERATED-DRIFT", {d["code"] for d in json.loads(drift.stdout)})


    def test_required_research_gate_blocks_compile(self):
        data = self.load_contract()
        data["compatibility"]["research_gate"] = {"required": True, "status": "blocked", "provider": "perplex", "sources": []}
        with tempfile.TemporaryDirectory() as td:
            contract = Path(td) / "CONTRACT.json"
            out = Path(td) / "sg"
            contract.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_sgctl("compile", str(contract), "--out", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())
            self.assertIn("research gate", result.stderr + result.stdout)

    def test_inferred_risky_research_cannot_be_disabled_by_required_false(self):
        data = self.load_contract()
        data["compatibility"]["research_gate"] = {"required": False, "status": "not_required", "provider": "manual", "sources": [], "summary": "not needed"}
        with tempfile.TemporaryDirectory() as td:
            contract = Path(td) / "CONTRACT.json"
            contract.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_sgctl("validate-contract", str(contract), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SGV-RESEARCH-REQUIRED", {d["code"] for d in json.loads(result.stdout)})

    def test_perplex_gate_requires_perplex_source(self):
        data = self.load_contract()
        data["compatibility"]["research_gate"] = {
            "required": True,
            "status": "satisfied",
            "provider": "perplex",
            "query": "fixture",
            "summary": "This summary is long enough to describe the research evidence for the plan.",
            "sources": [{"title": "Fixture", "url": "https://example.com", "provider": "web"}],
        }
        with tempfile.TemporaryDirectory() as td:
            contract = Path(td) / "CONTRACT.json"
            contract.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_sgctl("validate-contract", str(contract), "--format", "json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SGV-RESEARCH-PERPLEX-SOURCE", {d["code"] for d in json.loads(result.stdout)})

    def test_validate_package_catches_blocked_embedded_research_gate(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td) / "sg"
            result = self.run_sgctl("compile", "examples/brownfield-feature/CONTRACT.json", "--out", str(package))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads((package / "CONTRACT.json").read_text(encoding="utf-8"))
            data["compatibility"]["research_gate"]["status"] = "blocked"
            (package / "CONTRACT.json").write_text(json.dumps(data), encoding="utf-8")
            drift = self.run_sgctl("validate-package", str(package), "--format", "json")
            self.assertNotEqual(drift.returncode, 0)
            self.assertIn("SGV-RESEARCH-REQUIRED", {d["code"] for d in json.loads(drift.stdout)})

    def test_non_perplex_fallback_reason_is_rendered(self):
        data = self.load_contract()
        data["compatibility"]["research_gate"] = {
            "required": True,
            "status": "satisfied",
            "provider": "web",
            "provider_unavailable_reason": "Perplex unavailable in this offline fixture; web source used as fallback.",
            "query": "fixture",
            "summary": "This summary is long enough to describe web fallback research evidence for the plan.",
            "sources": [{"title": "Fixture", "url": "https://example.com", "provider": "web"}],
        }
        with tempfile.TemporaryDirectory() as td:
            contract = Path(td) / "CONTRACT.json"
            package = Path(td) / "sg"
            contract.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_sgctl("compile", str(contract), "--out", str(package))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Perplex unavailable", (package / "RESEARCH.md").read_text(encoding="utf-8"))
            self.assertIn("provider_unavailable_reason", (package / "reports" / "research.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
