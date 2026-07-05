from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_INVARIANT_FIELDS = {
    "id", "title", "owner", "severity_if_broken", "description",
    "canonical_reference", "tests", "introduced_by", "status",
}


def load_catalog(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    invariants = catalog.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        return ["catalog must contain a non-empty invariants array"]
    seen: set[str] = set()
    for index, item in enumerate(invariants):
        if not isinstance(item, dict):
            errors.append(f"invariants[{index}] must be an object")
            continue
        missing = sorted(REQUIRED_INVARIANT_FIELDS - item.keys())
        if missing:
            errors.append(f"{item.get('id', f'invariants[{index}]')} missing fields: {', '.join(missing)}")
        invariant_id = item.get("id")
        if not isinstance(invariant_id, str) or not invariant_id.startswith("INV-"):
            errors.append(f"invariants[{index}] has invalid id: {invariant_id!r}")
        elif invariant_id in seen:
            errors.append(f"duplicate invariant id: {invariant_id}")
        else:
            seen.add(invariant_id)
        tests = item.get("tests", [])
        if item.get("severity_if_broken") == "P1" and not tests:
            errors.append(f"{invariant_id} is P1 but has no behavioral test ids")
        if item.get("status") not in {"hard", "draft", "deprecated"}:
            errors.append(f"{invariant_id} has unsupported status: {item.get('status')!r}")
    return errors


def invariant_ids(catalog: dict[str, Any]) -> set[str]:
    return {item["id"] for item in catalog.get("invariants", []) if isinstance(item, dict) and "id" in item}
