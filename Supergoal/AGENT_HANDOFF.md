# chip-supergoal — maintainer handoff

Public source bundle for the `chip-supergoal` Hermes skill.

## What this is
- Skill root: `chip-supergoal/`
- Purpose: Principal+/Architect+ SuperGoal planner/compiler skill for disk-backed `.supergoal/` packages and standard Hermes `/goal` execution handoff.

## First files to read
1. `README.md`
2. `docs/README.ru.md`
3. `SKILL.md`
4. `references/execution-state-machine.md`
5. `references/upstream-goal-compatibility.md`
6. `scripts/sgctl.py`

## Verify after cloning
```bash
python3 -m unittest discover -s tests
bash scripts/test.sh
```

## Privacy boundary
Runtime/cache state is intentionally excluded: `.git`, `.supergoal`, `__pycache__`, `.pytest_cache`, local DBs, credentials, receipts, and generated delivery artifacts.
