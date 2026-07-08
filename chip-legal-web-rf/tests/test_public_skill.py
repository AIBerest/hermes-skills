import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicSkillTests(unittest.TestCase):
    def test_public_validator_passes(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_public_skill.py"), str(ROOT)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("validation_errors=0", proc.stdout)

    def test_consent_matrix_keeps_ads_optional(self):
        matrix = json.loads((ROOT / "templates" / "ui" / "consent-matrix.json").read_text(encoding="utf-8"))
        all_items = matrix["registration"] + matrix["payment"]
        for item in all_items:
            self.assertFalse(item["defaultChecked"], item)
            if item["type"] == "ads":
                self.assertFalse(item["required"], item)

    def test_required_template_set_exists(self):
        required = [
            "01-public-offer.md",
            "02-privacy-policy.md",
            "03-personal-data-consent.md",
            "04-advertising-consent.md",
            "05-cookies-consent.md",
            "06-service-rules.md",
            "07-paid-subscription-autopay-consent.md",
            "08-product-addendum.md",
            "09-expert-content-release.md",
        ]
        for name in required:
            self.assertTrue((ROOT / "templates" / "legal" / name).is_file(), name)

    def test_skill_has_required_sections(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for heading in ["## Trigger", "## Output Contract", "## Quick Test Checklist", "## Done Criteria"]:
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
