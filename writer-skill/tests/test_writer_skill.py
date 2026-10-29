"""Static checks for writer-skill packaging and source-update contract."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
STATE = ROOT / "references" / "source-state.json"


class WriterSkillTests(unittest.TestCase):
    def test_frontmatter_and_sections(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("\n---\n", text[4:])
        self.assertIn("name: writer-skill", text)
        for section in ("When to use", "Procedure", "Pitfalls", "Verification"):
            self.assertIn("## " + section, text)

    def test_safety_and_voice_guardrails(self):
        text = SKILL.read_text(encoding="utf-8")
        for clause in ("not** an AI detector", "Do not add fake typos", "Preserve evidence", "user-specific", "do not blindly"):
            # The last semantic requirement is expressed as "Do not copy ... blindly".
            if clause == "do not blindly":
                self.assertIn("blindly import", text)
            else:
                self.assertIn(clause, text)

    def test_source_baseline(self):
        state = json.loads(STATE.read_text(encoding="utf-8"))
        self.assertEqual(state["url"], "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing")
        self.assertIsInstance(state["revision_id"], int)
        self.assertIn("Historical indicators", state["baseline_sections"])


if __name__ == "__main__":
    unittest.main()
