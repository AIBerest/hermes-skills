#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PRIVATE_MARKER_PARTS = [
    "human" + "20",
    "человек" + r"\s*2\.0",
    "среда" + r"\s+внедрения",
    "yur" + "chenko",
    "юр" + "ченко",
    "ev" + "gyur",
    "chip" + "da",
    "@" + "chip",
    "/home/" + "hermes",
    r"\." + "supergoal",
    "telegram" + " session",
    r"api[_-]?key\s*=",
    r"secret\s*=",
    r"token\s*=",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]
PRIVATE_MARKERS = re.compile("|".join(PRIVATE_MARKER_PARTS), re.IGNORECASE)
REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "AGENT_HANDOFF.md",
    "references/checkbox-consent-principles.md",
    "references/document-pack-map.md",
    "templates/legal/01-public-offer.md",
    "templates/legal/02-privacy-policy.md",
    "templates/legal/03-personal-data-consent.md",
    "templates/legal/04-advertising-consent.md",
    "templates/legal/05-cookies-consent.md",
    "templates/legal/07-paid-subscription-autopay-consent.md",
    "templates/ui/consent-matrix.json",
]

SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}:
            continue
        yield path


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")

    for path in iter_text_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        # repo/skill name is intentional, but private names are not allowed elsewhere.
        scan_text = text.replace("chip-legal-web-rf", "")
        for i, line in enumerate(scan_text.splitlines(), 1):
            if PRIVATE_MARKERS.search(line):
                errors.append(f"private marker: {path.relative_to(root)}:{i}: {line[:160]}")

    matrix_path = root / "templates/ui/consent-matrix.json"
    if matrix_path.is_file():
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        for group in ("registration", "payment"):
            for item in matrix.get(group, []):
                if item.get("defaultChecked") is not False:
                    errors.append(f"{group}.{item.get('type')}: defaultChecked must be false")
                if item.get("type") == "ads" and item.get("required") is not False:
                    errors.append(f"{group}.ads: advertising consent must be optional")
                if not item.get("href") or not item.get("label"):
                    errors.append(f"{group}.{item.get('type')}: missing href/label")

    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    print(f"validation_errors={len(errors)}")
    for err in errors:
        print(err)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
