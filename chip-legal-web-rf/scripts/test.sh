#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
python3 -m py_compile scripts/*.py
python3 scripts/validate_public_skill.py .
python3 -m unittest discover -s tests -v
python3 - <<'PY'
from pathlib import Path
bad=[]
for p in Path('.').rglob('*'):
    if '.git' in p.parts or '__pycache__' in p.parts or not p.is_file():
        continue
    for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
        if line.startswith('<<<<<<< ') or line == '=======' or line.startswith('>>>>>>> '):
            bad.append(str(p)); break
print('conflict_marker_files=', len(bad))
for item in bad: print(item)
raise SystemExit(1 if bad else 0)
PY
