from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from .evidence import EvidenceRecord
from .model import Contract
from .state import State

BLOCKING_ISSUES = {"AUDIT_GAP", "AUDIT_BLOCKER", "AUDIT_CORRUPTION"}

@dataclass(frozen=True)
class AuditIssue:
    issue_type: str
    message: str
    phase_id: str | None = None
    criterion_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass(frozen=True)
class AuditReport:
    goal_id: str
    contract_revision: int
    coverage: dict[str, int]
    issues: list[AuditIssue] = field(default_factory=list)
    delivery_status: str = "not_required"
    rpd_decision: str = "checked-holds"
    terminal_state_revision: int | None = None

    @property
    def blocking_count(self) -> int:
        return sum(1 for issue in self.issues if issue.issue_type in BLOCKING_ISSUES)

    @property
    def can_complete(self) -> bool:
        return self.blocking_count == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "contract_revision": self.contract_revision,
            "coverage": self.coverage,
            "issues": [i.to_dict() for i in self.issues],
            "delivery_status": self.delivery_status,
            "rpd_decision": self.rpd_decision,
            "terminal_state_revision": self.terminal_state_revision,
            "can_complete": self.can_complete,
        }


def audit_contract(contract: Contract, evidence: list[EvidenceRecord], *, final_delivery_required: bool = False, delivery_verified: bool = False, planner_review_missing_after_launch: bool = False, state: State | None = None) -> AuditReport:
    issues: list[AuditIssue] = []
    by_criterion = {(e.phase_id, e.criterion_id): e for e in evidence if e.result == "pass"}
    total_blocking = 0
    deterministic = 0
    for phase in contract.phases:
        for criterion in phase.criteria:
            if criterion.blocking:
                total_blocking += 1
                key = (phase.id, criterion.id)
                if key not in by_criterion:
                    issues.append(AuditIssue("AUDIT_GAP", "blocking criterion has no passing evidence", phase.id, criterion.id))
                else:
                    if by_criterion[key].type == "command_result" and by_criterion[key].replayable:
                        deterministic += 1
    if planner_review_missing_after_launch:
        issues.append(AuditIssue("AUDIT_WARNING", "planner review receipt missing after explicit launch; non-blocking warning"))
    if final_delivery_required and not delivery_verified:
        issues.append(AuditIssue("AUDIT_GAP", "requested final delivery receipt missing or unverified"))
    terminal_revision = state.state_revision if state else None
    if state and state.lifecycle != "DONE":
        issues.append(AuditIssue("AUDIT_GAP", f"terminal state is {state.lifecycle}, not DONE"))
    coverage = {
        "blocking_criteria_total": total_blocking,
        "blocking_criteria_with_passing_evidence": len([1 for phase in contract.phases for c in phase.criteria if c.blocking and (phase.id, c.id) in by_criterion]),
        "deterministic_coverage": deterministic,
        "unverified": sum(1 for i in issues if i.issue_type in BLOCKING_ISSUES),
    }
    delivery_status = "verified" if delivery_verified else ("missing" if final_delivery_required else "not_required")
    return AuditReport(goal_id=contract.goal.id, contract_revision=contract.contract_revision, coverage=coverage, issues=issues, delivery_status=delivery_status, terminal_state_revision=terminal_revision)


def terminal_markers_allowed(state: State, report: AuditReport) -> bool:
    return state.lifecycle == "DONE" and report.can_complete and report.terminal_state_revision == state.state_revision


def write_final_audit(report: AuditReport, out_dir: str | Path) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "final-audit.json"
    md_path = out / "final-audit.md"
    json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Final audit", "", f"Goal: `{report.goal_id}`", f"Contract revision: `{report.contract_revision}`", f"Can complete: {'yes' if report.can_complete else 'no'}", "", "## Coverage"]
    lines += [f"- {k}: {v}" for k, v in report.coverage.items()]
    lines += ["", "## Issues"]
    lines += [f"- {i.issue_type}: {i.message}" + (f" ({i.phase_id}/{i.criterion_id})" if i.phase_id else "") for i in report.issues] or ["- none"]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path
