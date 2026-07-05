# LOOP_DESIGN.md

## Goal
Ship a falsifiable chip-supergoal change with no courtesy stop at phase boundaries.

## Context sources
- Skill root: <installed-skill-dir>.
- Package state: .supergoal/STATE.md.
- Canonical request: provided architecture plan.

## Host model
- Host: standard Hermes /goal executor.

## Reviewer / judge model
- Reviewer: embedded RPD/Senior gate with pass/fail mutation requests.

## Verification gates
- Programmatic gate: bash scripts/test.sh returns exit 0.
- Targeted gate: python3 -m unittest discover -s tests returns exit 0.

## State checkpoints
- STATE.md phase pointer before and after every phase.
- Event ledger line for every phase completion.

## Stop conditions
- Retry at most 3 times per failed gate.
- Stop after 2 no-progress attempts or a real approval blocker.

## Budget
- 13 phases.
- 30 turn budget recommendation.
- 3 audit rounds maximum.

## Boundaries
- Secrets/tokens/private Telegram content never leave local context.
- Production/public/payment/DNS/grant actions require approval.

## Failure recovery
- On failed validation, patch and retry.
- On missing repo baseline, record non-git baseline or block with exact path.

## Human approvals
- Required only for secrets, money, DNS, grants, destructive production, public/mass sends.

## ASCII preview
```text
LOOP_DESIGN.md -> /goal -> PHASES -> FINAL AUDIT -> DONE
```
