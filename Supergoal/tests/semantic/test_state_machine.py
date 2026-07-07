import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from chip_supergoal.events import read_events, verify_event_chain
from chip_supergoal.state import State, StateStore, read_state, recover_from_events, validate_goal_identity

DIGEST = "a" * 64

class StateMachineTest(unittest.TestCase):
    def test_atomic_transition_and_event_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(td)
            initial = State(goal_id="sg-20260625-state-test", contract_sha256=DIGEST, state_revision=0, lifecycle="DRAFT", current_phase_id="P01", phase_status="PENDING")
            store.initialize(initial)
            new = store.transition("COMPILED", expected_revision=0, phase_status="READY")
            self.assertEqual(new.state_revision, 1)
            self.assertEqual(read_state(store.state_json).lifecycle, "COMPILED")
            events = read_events(store.events)
            self.assertEqual(verify_event_chain(events), [])
            self.assertEqual(events[-1]["state_revision"], 1)
            self.assertIn("COMPILED", store.state_md.read_text())

    def test_illegal_transition_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(td)
            store.initialize(State(goal_id="sg-20260625-state-test", contract_sha256=DIGEST, state_revision=0, lifecycle="COMPILED", current_phase_id="P01", phase_status="READY"))
            with self.assertRaisesRegex(ValueError, "SGV-STATE-ILLEGAL-TRANSITION"):
                store.transition("DONE", expected_revision=0)

    def test_stale_writer_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(td)
            store.initialize(State(goal_id="sg-20260625-state-test", contract_sha256=DIGEST, state_revision=0, lifecycle="DRAFT", current_phase_id="P01", phase_status="PENDING"))
            store.transition("COMPILED", expected_revision=0)
            with self.assertRaisesRegex(ValueError, "SGV-STATE-STALE-WRITER"):
                store.transition("PLAN_REVIEWED", expected_revision=0)

    def test_goal_digest_mismatch_rejected(self):
        state = State(goal_id="sg-20260625-state-test", contract_sha256=DIGEST, state_revision=0, lifecycle="DRAFT", current_phase_id="P01", phase_status="PENDING")
        with self.assertRaisesRegex(ValueError, "SGV-STATE-CONTRACT-MISMATCH"):
            validate_goal_identity(state, goal_id="sg-20260625-other", contract_sha256=DIGEST)
        with self.assertRaisesRegex(ValueError, "SGV-STATE-CONTRACT-MISMATCH"):
            validate_goal_identity(state, goal_id="sg-20260625-state-test", contract_sha256="b" * 64)

    def test_recovery_from_corrupt_state_uses_valid_event_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            store = StateStore(td)
            store.initialize(State(goal_id="sg-20260625-state-test", contract_sha256=DIGEST, state_revision=0, lifecycle="DRAFT", current_phase_id="P01", phase_status="PENDING"))
            store.state_json.write_text("{broken", encoding="utf-8")
            recovered = recover_from_events(td)
            self.assertIsNotNone(recovered)
            self.assertEqual(recovered.lifecycle, "RECOVERING")
            store.events.write_text(store.events.read_text().replace('"event_id"', '"event_id_tampered"', 1), encoding="utf-8")
            self.assertIsNone(recover_from_events(td))

if __name__ == "__main__":
    unittest.main()
