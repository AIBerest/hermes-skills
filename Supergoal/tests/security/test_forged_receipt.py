import hashlib
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class ForgedReceiptSecurity(unittest.TestCase):
    def test_review_md_files_rejects_minimal_forged_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            sg = Path(td) / ".supergoal"
            out = sg / "out"
            out.mkdir(parents=True)
            for name in ["THINKING.md", "LOOP_DESIGN.md", "ROADMAP.md", "LAUNCH_GOAL.md"]:
                (sg / name).write_text(f"# {name}\n", encoding="utf-8")
            hashes = {name: sha256(sg / name) for name in ["THINKING.md", "LOOP_DESIGN.md", "ROADMAP.md", "LAUNCH_GOAL.md"]}
            (out / "review-md-files-delivery-receipt.json").write_text(json.dumps({
                "ok": True,
                "sent": True,
                "target": "telegram:test",
                "hashes": hashes,
            }), encoding="utf-8")
            result = subprocess.run(
                ["bash", str(ROOT / "templates/delivery/send-review-md-files.sh")],
                cwd=Path(td),
                env={"SUPERGOAL_ROOT": str(sg), "SUPERGOAL_DELIVERY_TARGET": "telegram:test"},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_final_artifacts_rejects_minimal_forged_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            sg = Path(td) / ".supergoal"
            out = sg / "out"
            out.mkdir(parents=True)
            archive = out / "final-artifacts.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("safe.txt", "safe\n")
            digest = sha256(archive)
            (out / "final-artifacts-delivery-receipt.json").write_text(json.dumps({
                "ok": True,
                "sent": True,
                "target": "telegram:test",
                "hash": digest,
            }), encoding="utf-8")
            result = subprocess.run(
                ["bash", str(ROOT / "templates/delivery/send-final-artifacts.sh"), str(archive)],
                cwd=Path(td),
                env={"SUPERGOAL_ROOT": str(sg), "SUPERGOAL_DELIVERY_TARGET": "telegram:test"},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
