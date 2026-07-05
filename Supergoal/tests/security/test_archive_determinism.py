import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class ArchiveDeterminismTest(unittest.TestCase):
    def package(self, sg: Path):
        result = subprocess.run(
            ["bash", str(ROOT / "templates/delivery/package-final-artifacts.sh")],
            cwd=sg.parent,
            env={"SUPERGOAL_ROOT": str(sg)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return sg / "out/final-artifacts.zip", sg / "out/final-artifacts-manifest.json"

    def test_deterministic_archive_and_embedded_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            sg = Path(td) / ".supergoal"
            sg.mkdir()
            (sg / "a.txt").write_text("alpha\n", encoding="utf-8")
            (sg / "b.txt").write_text("beta\n", encoding="utf-8")
            archive1, manifest1 = self.package(sg)
            digest1 = hashlib.sha256(archive1.read_bytes()).hexdigest()
            archive1_bytes = archive1.read_bytes()
            archive2, manifest2 = self.package(sg)
            digest2 = hashlib.sha256(archive2.read_bytes()).hexdigest()
            self.assertEqual(digest1, digest2)
            self.assertEqual(archive1_bytes, archive2.read_bytes())
            manifest = json.loads(manifest2.read_text())
            self.assertEqual(manifest["hash"], digest2)
            with zipfile.ZipFile(archive2) as zf:
                self.assertIn("MANIFEST.json", zf.namelist())
                embedded = json.loads(zf.read("MANIFEST.json"))
                self.assertEqual(embedded["secret_scan"], "passed")
                self.assertEqual([item["path"] for item in embedded["files"]], ["a.txt", "b.txt"])

    def test_secret_scan_rejects_private_key_block(self):
        with tempfile.TemporaryDirectory() as td:
            sg = Path(td) / ".supergoal"
            sg.mkdir()
            marker = "-----BEGIN " + "PRIVATE KEY-----"
            (sg / "leak.txt").write_text(marker + "\nabc\n", encoding="utf-8")
            result = subprocess.run(["bash", str(ROOT / "templates/delivery/package-final-artifacts.sh")], cwd=sg.parent, env={"SUPERGOAL_ROOT": str(sg)}, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SGV-PACKAGE-SECRET", result.stderr)

if __name__ == "__main__":
    unittest.main()
