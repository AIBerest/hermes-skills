import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from chip_supergoal.migrate import MigrationError, migrate_v2_package, read_v2_state_md
from chip_supergoal.model import load_contract

class V2MigrationTest(unittest.TestCase):
    def test_valid_v2_package_migrates_to_valid_v3_contract_with_backup(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "migrated"
            report = migrate_v2_package(ROOT / "tests/fixtures/v2-valid/package-minimal", out)
            self.assertTrue(report["ok"])
            self.assertTrue((out / "v2-backup/ROADMAP.md").is_file())
            contract = load_contract(out / "CONTRACT.json")
            self.assertEqual(contract.schema_version, "3.0")
            self.assertEqual(contract.phases[0].id, "P01")

    def test_invalid_v2_package_fails_with_unresolved_diagnostics(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "bad"
            (src / "phases").mkdir(parents=True)
            (src / "ROADMAP.md").write_text("# Bad\n", encoding="utf-8")
            (src / "phases/phase-01.md").write_text((ROOT / "tests/fixtures/v2-invalid/phase-99-of-1-rpd-mismatch.md").read_text(), encoding="utf-8")
            with self.assertRaises(MigrationError) as ctx:
                migrate_v2_package(src, Path(td) / "out")
            self.assertIn("migration_unresolved", str(ctx.exception))
            self.assertIn("SGV-PHASE-ORDINAL-OUT-OF-RANGE", str(ctx.exception))

    def test_v2_state_md_read_only_fallback(self):
        state = read_v2_state_md(ROOT / "tests/fixtures/v2-valid/package-minimal/STATE.md")
        self.assertEqual(state["compatibility_mode"], "v2-read-only")
        self.assertEqual(state["current_phase"], "1")

if __name__ == "__main__":
    unittest.main()
