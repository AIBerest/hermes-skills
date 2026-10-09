"""Validate package shape and referenced resources without enforcing prose wording."""
import re
from pathlib import Path


def validate(root: Path) -> list[str]:
    text = (root / "SKILL.md").read_text()
    errors = []
    if not text.startswith("---\n"):
        return ["frontmatter"]
    if not re.search(r"^name: seo-aeo-geo-principal$", text, re.M):
        errors.append("frontmatter/name")
    description = re.search(r"^description: (.+)$", text, re.M)
    if not description or len(description.group(1)) > 1024:
        errors.append("description")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if not link.startswith("http") and not (root / link).is_file():
            errors.append("missing reference:" + link)
    return errors


if __name__ == "__main__":
    errors = validate(Path(__file__).resolve().parents[1])
    print("skill_contract_errors=", errors)
    raise SystemExit(bool(errors))
