from __future__ import annotations

import json
from pathlib import Path
from .model import Contract


def load_risk_policy(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def risk_policy_errors(contract: Contract, policy: dict) -> list[str]:
    errors: list[str] = []
    tags = policy.get("risk_tags", {})
    known = set(tags)
    for phase in contract.phases:
        for tag in phase.risk_tags:
            if tag not in known:
                errors.append(f"{phase.id} uses unknown risk tag {tag}")
                continue
            required = set(tags[tag].get("required_rpd_focus", []))
            if required and not phase.rpd.required:
                errors.append(f"{phase.id} risk {tag} requires RPD")
            missing = sorted(required - set(phase.rpd.focus))
            if missing:
                errors.append(f"{phase.id} risk {tag} missing RPD focus: {', '.join(missing)}")
    return errors
