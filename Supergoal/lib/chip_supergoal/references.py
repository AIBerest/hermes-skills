from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_reference_catalog(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_reference_catalog(skill_root: str | Path, catalog: dict[str, Any]) -> list[str]:
    root = Path(skill_root)
    errors: list[str] = []
    refs = catalog.get("references", [])
    ids: set[str] = set()
    paths: set[str] = set()
    invariant_owner: dict[str, str] = {}
    for ref in refs:
        rid = ref.get("id")
        path = ref.get("path")
        if not rid or rid in ids:
            errors.append(f"duplicate or missing reference id: {rid}")
        ids.add(rid)
        if not path or path in paths:
            errors.append(f"duplicate or missing reference path: {path}")
        paths.add(path)
        if path and not (root / path).is_file():
            errors.append(f"missing reference file: {path}")
        for inv in ref.get("owns_invariants", []):
            if inv in invariant_owner:
                errors.append(f"invariant {inv} has multiple canonical owners: {invariant_owner[inv]} and {path}")
            invariant_owner[inv] = path
    actual = {p.relative_to(root).as_posix() for p in (root / "references").glob("*.md") if not p.name.endswith('.generated.md')}
    missing = sorted(actual - paths)
    if missing:
        errors.extend(f"uncataloged reference: {p}" for p in missing)
    return errors


def generate_index(catalog: dict[str, Any]) -> str:
    lines = ["# Generated reference index", "", "Generated from `spec/reference-catalog.json`.", ""]
    for ref in catalog.get("references", []):
        lines.append(f"- `{ref['path']}` — {ref['status']} — {', '.join(ref.get('owns_invariants', [])) or 'no invariant owner'}")
    return "\n".join(lines) + "\n"


def generate_dispatch(catalog: dict[str, Any]) -> str:
    lines = ["# Generated reference dispatch", "", "Generated from `spec/reference-catalog.json`.", ""]
    for ref in catalog.get("references", []):
        if ref.get("load_default") or ref.get("owns_invariants"):
            lines.append(f"- Trigger `{', '.join(ref.get('triggers', []))}` → load `{ref['path']}`")
    return "\n".join(lines) + "\n"
