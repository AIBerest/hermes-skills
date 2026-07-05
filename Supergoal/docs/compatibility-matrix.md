# Compatibility matrix — chip-supergoal v3 workstream

| Skill version | Contract/protocol | Hermetic probe | Live GoalManager probe | Notes |
|---|---|---|---|---|
| in-progress v3 | 3.0 / 3.0 | green: `python3 -m unittest tests.e2e.test_goalmanager_simulator tests.e2e.test_full_run` | unavailable unless `SUPERGOAL_HERMES_INTEGRATION=1` | Standard `/goal` remains production executor; simulator is test-only. |

## Observable contract covered

- `SUPERGOAL_PHASE_DONE` alone means continue.
- `AUDIT_COMPLETE` alone means continue.
- `SUPERGOAL_RUN_COMPLETE` alone means continue.
- `AUDIT_COMPLETE` + `SUPERGOAL_RUN_COMPLETE` + `Goal complete: yes` means done.
- `BLOCKED_BY_APPROVAL` means blocked/paused.
- Forced yield preserves exact next step.

## Live probe status

No safe live Hermes GoalManager integration harness was exposed in this runtime. The live test is present and opt-in:

```bash
SUPERGOAL_HERMES_INTEGRATION=1 python3 -m unittest tests.integration.test_live_goalmanager
```
