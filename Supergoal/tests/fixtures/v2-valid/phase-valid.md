SUPERGOAL_PHASE_START
Phase: 1 of 1 — Valid baseline
Task: Preserve current validator positive behavior
Mandatory commands: bash scripts/test.sh
Acceptance criteria: 3
Evidence required: command output
Depends on phases: none
RPD required: yes
RPD focus: integration

## Work
- Create a baseline fixture that remains accepted by the v2 validator.

## Acceptance criteria
- Fixture has exact required sections.
- Fixture has three concrete acceptance bullets.
- Fixture has RPD metadata.

## Mandatory commands
- bash scripts/test.sh

## Evidence required
- Command output with exit code 0.
