# Repeated complete standing-goal continuations

Use when a host-generated standing-goal continuation arrives after a SuperGoal is already complete.

## Problem

After `AUDIT_COMPLETE` / `SUPERGOAL_RUN_COMPLETE`, some clients may still send repeated messages like:

```text
[Continuing toward your standing goal]
Continue working toward this goal. Take the next concrete step.
```

If `STATE.md` already says any completed terminal state — for example `Current phase: DONE`, `Current phase: COMPLETE`, `Status: DONE`, or `Status: COMPLETE` — and the final audit contains `AUDIT_COMPLETE` / `SUPERGOAL_RUN_COMPLETE`, these are stale evaluator continuations, not instructions to re-open the run.

## Correct behavior

1. Read `STATE.md` if not already loaded in the current turn.
2. Treat `DONE` and `COMPLETE` as equivalent terminal states when paired with final-audit evidence.
3. If status/current phase are terminal, stop the loop.
4. Do not run another numbered phase.
5. Do not re-run final audit, deploy smoke, build, or live probes unless Chip explicitly asks for fresh verification.
7. On the **first** post-complete continuation, cite the terminal state once in plain language if needed: the goal is finished, what was done, and that there is no next numbered phase.
8. On **repeated identical** post-complete continuations in the same chat, do **not** keep replying with status summaries, file attachments, full completion blocks, or repeated `COMPLETE — no-op.` messages. Treat them as stale evaluator noise.
9. After the first verified terminal reply in a chat, do **not** re-read `STATE.md`, re-open reports, run tests, or call tools for later identical wrappers. The already-verified terminal state is enough unless the new message contains human content beyond the wrapper.
10. If the runtime can suppress delivery, no-op silently. If the runtime forces a visible final message, use the shortest explicit marker at most once; repeated forced visible no-ops are a control-plane bug to fix in GoalManager/gateway, not a chat behavior to normalize.
11. Only answer substantively again if Chip adds a new human question, asks for fresh verification, reports a bug, or provides a new goal. Then answer that new request, not the stale continuation wrapper.
12. Reply format if a visible answer is needed:
   - first repeat: `COMPLETE — SuperGoal уже завершён. STATE.md: terminal DONE/COMPLETE. Следующей numbered phase нет.`
   - later repeated wrapper with no new human content: prefer silence; if silence is impossible, fix the control-plane loop rather than sending repeated no-op messages.

## Why

Repeated re-verification creates noisy duplicate answers and can accidentally turn a completed production goal into an unbounded monitoring loop. Completion state on disk is the source of truth; once complete, the right next action is no-op unless the user gives a new goal or a concrete bug.
