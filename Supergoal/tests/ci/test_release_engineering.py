import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class ReleaseEngineeringTest(unittest.TestCase):
    def test_version_changelog_and_release_checklist_agree(self):
        version = (ROOT / "VERSION").read_text().strip()
        changelog = (ROOT / "CHANGELOG.md").read_text()
        checklist = (ROOT / "docs/release-checklist.md").read_text()
        self.assertIn(version, changelog)
        self.assertIn("GitHub actions are pinned", checklist)
        self.assertIn("contents: read", checklist)

    def test_ci_is_split_and_actions_are_pinned(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        for job in ["unit", "schema", "semantic", "rendering", "e2e", "security", "migration", "reference", "aggregate"]:
            self.assertRegex(ci, rf"\n  {job}:\n")
        self.assertIn("permissions:\n  contents: read", ci)
        uses = re.findall(r"uses:\s*([^\s]+)", ci)
        self.assertTrue(uses)
        for item in uses:
            self.assertRegex(item, r"@[a-f0-9]{40}$", item)
        self.assertIn("shellcheck", ci)
        self.assertIn("shfmt", ci)

    def test_compile_reproducibility_command_shape(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a"; b = Path(td) / "b"
            for out in [a, b]:
                result = subprocess.run([sys.executable, "scripts/sgctl.py", "compile", "examples/brownfield-feature/CONTRACT.json", "--out", str(out)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for rel in ["CONTRACT.json", "THINKING.md", "RESEARCH.md", "reports/research.json", "LOOP_DESIGN.md", "ROADMAP.md", "STATE.md", "PROTOCOL.md", "LAUNCH_GOAL.md", "MANIFEST.json", "phases/phase-01.md"]:
                self.assertEqual((a / rel).read_bytes(), (b / rel).read_bytes(), rel)

    def test_no_tracked_test_dirtiness_gate_is_documented(self):
        test_sh = (ROOT / "scripts/test.sh").read_text()
        self.assertIn("git diff --check", test_sh)
        checklist = (ROOT / "docs/release-checklist.md").read_text()
        self.assertIn("compare deterministic immutable outputs", checklist)

if __name__ == "__main__":
    unittest.main()
