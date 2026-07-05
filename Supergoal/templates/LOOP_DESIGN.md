# LOOP_DESIGN.md

## Goal
Describe the execution loop's falsifiable goal in one paragraph. Include what will be true when the loop is done.

## Context sources
List the source set the executor must trust, inspect, or verify. Separate canonical sources from assumptions.

- User objective:
- Repository / filesystem:
- Project docs / rules:
- Runtime / production sources:
- Prior sessions or memory:
- Assumptions still needing falsification:

## Host model
Name the executor/host model or agent surface that will drive the loop. State whether subagents are allowed and under what condition.

## Reviewer / judge model
Define the review seat.

- Reviewer/judge:
- Mode: notes / verdict / both
- Rubric:
- Required evidence tier:
- Mutation rule:

## Verification gates
List gates in execution order. Prefer commands/tests/API checks over prose judgment.

1. Gate:
   - check:
   - pass condition:
   - failure mutation:

## State checkpoints
Define where state is written and how continuation/recovery works.

- State file:
- Event ledger:
- Phase reports:
- Delivery receipts:
- Backup / rollback evidence:

## Stop conditions
State when the loop must stop instead of burning tokens.

- hard blocker:
- approval blocker:
- no-progress:
- max revisions:
- max iterations:
- budget exceeded:

## Budget
State the planned budget.

- phases:
- max iterations:
- revise limit per failed gate:
- token/time target:

## Boundaries
List what the loop must not touch without explicit approval.

- secrets / credentials:
- private Telegram / personal data:
- production / public channels:
- payments / legal / destructive data:
- unrelated files / other Hermes profiles:

## Failure recovery
For each likely failure class, name the next action.

- validation failure:
- test failure:
- missing source:
- delivery failure:
- rollback needed:

## Human approvals
List the only human gates that remain.

- planning review:
- dangerous action approvals:
- final launch / delivery approval if needed:

## ASCII preview

```text
INTAKE / RECON
  ↓
THINKING + RESEARCH
  ↓
LOOP_DESIGN.md
  ↓ gate: loop health rubric + RPD/Senior pressure
ROADMAP + PHASE SPECS
  ↓ gate: phase validation + launch contract
/goal EXECUTION
  ↓
PHASE N
  ↓ gate: tests + RPD_PHASE_REVIEW where risky
FINAL AUDIT
  ↓ gate: RPD_FINAL_REVIEW
DELIVER / DONE
```
