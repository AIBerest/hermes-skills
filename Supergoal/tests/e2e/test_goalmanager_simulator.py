import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from chip_supergoal.goalmanager_sim import GoalManagerSimulator

class GoalManagerSimulatorTest(unittest.TestCase):
    def test_phase_done_alone_continues(self):
        sim = GoalManagerSimulator()
        self.assertEqual(sim.classify("SUPERGOAL_PHASE_DONE\nGoal complete: no"), "continue")

    def test_audit_or_run_marker_alone_continues(self):
        sim = GoalManagerSimulator()
        self.assertEqual(sim.classify("AUDIT_COMPLETE\nGoal complete: no"), "continue")
        self.assertEqual(sim.classify("SUPERGOAL_RUN_COMPLETE\nGoal complete: no"), "continue")

    def test_final_marker_pair_marks_done(self):
        sim = GoalManagerSimulator()
        self.assertEqual(sim.classify("AUDIT_COMPLETE\nSUPERGOAL_RUN_COMPLETE\nGoal complete: yes"), "done")

    def test_forced_yield_resumes_exact_next_step(self):
        sim = GoalManagerSimulator()
        footer = sim.forced_yield_footer("P03")
        self.assertEqual(sim.classify(footer), "continue")
        self.assertIn("Next: P03", footer)

    def test_approval_blocker_pauses(self):
        sim = GoalManagerSimulator()
        self.assertEqual(sim.classify("BLOCKED_BY_APPROVAL\nNeed bounded approval manifest"), "blocked")

if __name__ == "__main__":
    unittest.main()
