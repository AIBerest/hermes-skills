from __future__ import annotations

import re
from .model import Contract
from .graph import phase_graph_errors
from .policy import risk_policy_errors

ID_PATTERNS = {
    "goal": re.compile(r"^sg-[0-9]{8}-[a-z0-9-]+$"),
    "phase": re.compile(r"^P[0-9]{2}$"),
    "criterion": re.compile(r"^P[0-9]{2}-C[0-9]{2}$"),
    "command": re.compile(r"^P[0-9]{2}-CMD[0-9]{2}$"),
}

def stable_id_errors(contract: Contract) -> list[str]:
    errors: list[str] = []
    if not ID_PATTERNS["goal"].match(contract.goal.id):
        errors.append(f"invalid goal id: {contract.goal.id}")
    seen: set[str] = set()
    for phase in contract.phases:
        if not ID_PATTERNS["phase"].match(phase.id):
            errors.append(f"invalid phase id: {phase.id}")
        for item_id in [phase.id, *(c.id for c in phase.criteria), *(c.id for c in phase.commands), *(d.id for d in phase.deliverables)]:
            if item_id in seen:
                errors.append(f"duplicate id: {item_id}")
            seen.add(item_id)
        command_ids = {c.id for c in phase.commands}
        for criterion in phase.criteria:
            if not ID_PATTERNS["criterion"].match(criterion.id):
                errors.append(f"invalid criterion id: {criterion.id}")
            if criterion.verifier.command_id and criterion.verifier.command_id not in command_ids:
                errors.append(f"{criterion.id} references missing command {criterion.verifier.command_id}")
        for command in phase.commands:
            if not ID_PATTERNS["command"].match(command.id):
                errors.append(f"invalid command id: {command.id}")
            if not command.command or command.command.upper() == "TBD":
                errors.append(f"{command.id} has placeholder command")
            if command.timeout_seconds <= 0:
                errors.append(f"{command.id} timeout must be positive")
    return errors

def semantic_errors(contract: Contract, risk_policy: dict | None = None) -> list[str]:
    errors = []
    errors.extend(stable_id_errors(contract))
    errors.extend(phase_graph_errors(contract))
    if risk_policy is not None:
        errors.extend(risk_policy_errors(contract, risk_policy))
    return errors
