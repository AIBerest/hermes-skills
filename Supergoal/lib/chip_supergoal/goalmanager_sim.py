from __future__ import annotations

from dataclasses import dataclass

@dataclass
class GoalManagerSimulator:
    max_turns: int = 30
    turns: int = 0
    state: str = "running"

    def classify(self, response: str) -> str:
        self.turns += 1
        has_audit = "AUDIT_COMPLETE" in response
        has_run = "SUPERGOAL_RUN_COMPLETE" in response
        goal_yes = "Goal complete: yes" in response
        if has_audit and has_run and goal_yes:
            self.state = "done"
            return "done"
        if "BLOCKED_BY_APPROVAL" in response or "AUDIT_HANDOFF" in response or "FAILURE_HANDOFF" in response:
            self.state = "blocked"
            return "blocked"
        if "SUPERGOAL_TURN_YIELD" in response or "SUPERGOAL_PHASE_DONE" in response or has_audit or has_run:
            self.state = "continue"
            return "continue"
        if self.turns >= self.max_turns:
            self.state = "blocked"
            return "blocked"
        self.state = "continue"
        return "continue"

    def forced_yield_footer(self, next_step: str) -> str:
        return f"SUPERGOAL_TURN_YIELD\nGoal complete: no\nNext: {next_step}\nCompletion requires: AUDIT_COMPLETE and SUPERGOAL_RUN_COMPLETE in the same final response."
