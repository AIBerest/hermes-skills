import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class ArchiveSymlinkSecurity(unittest.TestCase):
    def test_package_final_artifacts_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            sg = base / ".supergoal"
            sg.mkdir()
            outside = base / "outside-secret.txt"
            outside.write_text("outside-content\n", encoding="utf-8")
            (sg / "safe.txt").write_text("safe\n", encoding="utf-8")
            (sg / "escape.txt").symlink_to(outside)
            result = subprocess.run(
                ["bash", str(ROOT / "templates/delivery/package-final-artifacts.sh")],
                cwd=base,
                env={"SUPERGOAL_ROOT": str(sg)},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            archive = sg / "out/final-artifacts.zip"
            if archive.exists():
                with zipfile.ZipFile(archive) as zf:
                    names = zf.namelist()
                    self.assertNotIn("escape.txt", names)
                    for name in names:
                        self.assertNotIn("outside-content", zf.read(name).decode("utf-8", errors="ignore"))

if __name__ == "__main__":
    unittest.main()
