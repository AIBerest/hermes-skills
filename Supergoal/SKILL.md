---
name: chip-supergoal
description: Principal+ plan-only SuperGoal planner for non-trivial software work. Builds a verified .supergoal package with THINKING, LOOP_DESIGN, ROADMAP, STATE, phase specs, PROTOCOL, RPD/Senior gates, Telegram delivery receipts when required, and one explicit /goal handoff. Use for /chip-supergoal, plan and ship X, autonomous build planning, risky refactors, production-adjacent tasks, and standing SuperGoal continuation repair.
argument-hint: <describe what must be built, fixed, shipped, or planned>
---

# chip-supergoal

`chip-supergoal` is a **planner/compiler**, not the executor. It turns a non-trivial task into a disk-backed `.supergoal/` package and one launchable standard Hermes `/goal` handoff. The later upstream GoalManager session executes from the generated files, verifies every phase, runs final audit, and prints `SUPERGOAL_RUN_COMPLETE` only after `AUDIT_COMPLETE`.

## Principal+ contract

Use this root as the controller. Heavy detail lives in references and templates.

1. **Simple core, modular depth** — root owns triggers, invariants, stage order, artifact list, and reference dispatch. Incident lessons live in references.
2. **Plan-only boundary** — this skill may inspect, research, and write planning artifacts. It must not execute numbered implementation phases.
3. **One launch surface** — create exactly one human-facing launch body in `LAUNCH_GOAL.md`. Do not hide alternate launch bodies in `ROADMAP.md` or `THINKING.md`.
4. **One standard `/goal`, not a chain** — the executor reads `STATE.md` and continues until all phases plus audit complete.
5. **No false done** — every phase needs real evidence; final completion requires re-reading the original `ROADMAP.md`, re-running aggregate checks, checking deliverables, `RPD_FINAL_REVIEW`, `AUDIT_COMPLETE`, then `SUPERGOAL_RUN_COMPLETE`.
6. **Risky work gets Senior Gate** — auth, payments, secrets, production, migrations, gateways, cron/model routing, private data, destructive actions, public launches, and recurring bugs require evidence-tiered RPD/Senior review.
7. **Telegram delivery is blocking when requested** — if Chip asks for files or final artifacts in Telegram, scripted send + receipt is part of done, not a promise.
8. **Chip review files are always delivered** — for Chip-facing SuperGoal planning, send the review `.md` files into the current Telegram thread by default (`THINKING.md`, `LOOP_DESIGN.md`, `ROADMAP.md`, `LAUNCH_GOAL.md`, plus `RESEARCH.md` when non-empty). A text-only summary is incomplete.

## Use when

Use for:

- `/chip-supergoal <task>` or “make SuperGoal / SG / ТЗ package”
- “plan and ship X”, autonomous feature/refactor/redesign planning
- brownfield work where codebase reality, tests, deployment, or recovery matter
- greenfield products/systems where stack, research, architecture, and phase boundaries matter
- standing SuperGoal continuation/repair where `STATE.md` exists
- skill/library hardening work that needs phases, review, and final audit

Do **not** use for tiny edits, one factual answer, pure copywriting, or a task whose safest path is direct execution in the current session. For those, say it is too small for SuperGoal and use the direct workflow.

## Human gates

Only two gates are allowed by default:

1. **Stage 1 clarifying questions** — only for true material gaps that tools cannot answer.
2. **Stage 6 plan review** — show the reviewed package summary and wait for explicit go/no-go before launch.

Everything else should be autonomous and evidence-backed.

## Generated artifacts

Write under `$SUPERGOAL_ROOT` (normally `<repo>/.supergoal/`):

- `THINKING.md` — goals, constraints, risks, dependencies, assumptions, memory hits, tools/skills used.
- `RESEARCH.md` — only when research gates run.
- `LOOP_DESIGN.md` — pre-launch loop harness: goal, context, host/reviewer/judge roles, verification gates, state, stop conditions, budget, boundaries, egress/redaction, recovery, and ASCII preview.
- `ROADMAP.md` — decision package, phase map, measurable acceptance criteria, mandatory commands, evidence requirements.
- `STATE.md` — current phase, baseline ref, status snapshot, events, delivery state.
- `PROTOCOL.md` — self-contained executor loop copied from `templates/PROTOCOL.md`.
- `LAUNCH_GOAL.md` — the only artifact containing a launch line beginning exactly `SUPERGOAL_GOAL_BODY:`.
- `phases/phase-N.md` — one strict phase spec per phase, validated by `scripts/validate-phase.sh`.
- `scripts/repo-state.sh` — deliverable/diff/cleanliness helper copied from this skill.
- delivery scripts/receipts when Telegram/file delivery is requested.

See `references/artifact-schemas.md` for exact schemas and `templates/LAUNCH_GOAL.md` for the launch contract.

## Procedure

| Stage | Action | Evidence |
|---|---|---|
| 0 | Resolve live skill dir, preload memory, detect tools/skills, detect resume state. | skill path + context notes |
| 1 | Intake. Brownfield asks 0–2 questions; greenfield batches up to 4 until material gaps close. | assumptions/gaps list |
| 2 | Recon. Run stack/env/repo scripts and read outputs. | 5-line stack/commands/risk summary |
| 3 | Research + architecture gates. Use skill-first research when current facts matter. | `THINKING.md`; optional `RESEARCH.md` |
| 3.5 | **Loop Design Gate.** Design the execution harness before roadmap compilation: host/reviewer/judge, verification gates, state, stop, budget, boundaries, egress/redaction, failure recovery, and ASCII preview. Mutate weak loop specs before launch. | `LOOP_DESIGN.md`; loop health rubric |
| 4 | Decompose into as many phases as the task requires. | phase map with dependencies |
| 5 | Write roadmap, state, protocol, launch goal, and phase specs. | files on disk + phase validation |
| 6 | Run embedded `RPD_PLAN_REVIEW`; mutate weak artifacts or mark `checked-holds`. Show review summary and wait. | revision ledger + go/no-go |
| 6.5 | Preflight smoke: baseline commands, repo state, required files, blockers. | `PREFLIGHT_GREEN` or `PREFLIGHT_RED` |
| 7 | Emit one ready launch card/file. User starts `/goal`; planner stops. | `READY_TO_DISPATCH` or blocked state |

Detailed planning rules: `references/core-planning-contract.md`, `references/research-and-architecture-gates.md`, `references/phase-design.md`, `references/planning-depth.md`.

## Executor invariants for generated `/goal`

The generated `PROTOCOL.md` must preserve these exact marker families:

- phase loop: `SUPERGOAL_PHASE_START`, `SUPERGOAL_STATUS`, `SUPERGOAL_PHASE_VERIFY`, `MEMORY_SAVED`, `SUPERGOAL_PHASE_DONE`, `SUPERGOAL_TURN_YIELD`
- preflight: `PREFLIGHT_GREEN`, `PREFLIGHT_RED`, `READY_TO_DISPATCH`
- RPD: `RPD_PLAN_REVIEW`, `RPD_PHASE_REVIEW`, `RPD_FINAL_REVIEW`
- failure recovery: `FAILURE_PROBE`, `FAILURE_ESCALATE`, `FAILURE_HANDOFF`
- audit: `AUDIT_START`, `AUDIT_VERIFY`, `AUDIT_GAPS`, `AUDIT_COMPLETE`, `AUDIT_HANDOFF`
- delivery/approval: `SUPERGOAL_REVIEW_FILES_BLOCKED`, `SUPERGOAL_FILES_SENT`, `BLOCKED_BY_APPROVAL`, `READY_FOR_DELETE_APPROVAL`
- completion: `SUPERGOAL_RUN_COMPLETE`

Official GoalManager execution continues across numbered phases in the same run until final audit, a real safety/approval gate, or a real blocker. It must not stop merely because `SUPERGOAL_PHASE_DONE` was printed. `SUPERGOAL_TURN_YIELD` is a forced-yield/blocker marker, not a courtesy phase boundary. See `references/execution-state-machine.md`.

## Phase spec contract

When generating phase files programmatically, build acceptance criteria and evidence lists as explicit arrays/lists, not strings. A common failure mode is iterating over a string and producing one bullet per character; validation may pass structurally while the phase is unusable. After generation, re-read at least one phase file and verify the bullets are semantic before declaring the package ready.

Every phase file must contain:

```text
SUPERGOAL_PHASE_START
Phase: N of TOTAL — <name>
Task: <one-line task>
Mandatory commands: <csv>
Acceptance criteria: <count>
Evidence required: <csv>
Depends on phases: <ids|none>
RPD required: yes|no
RPD focus: security|integration|ux|migration|data-loss|gateway|payments|none
```

And exact headings:

- `## Work`
- `## Acceptance criteria`
- `## Mandatory commands`
- `## Evidence required`

Run `bash "$SUPERGOAL_DIR/scripts/validate-phase.sh" <phase-file>` for every phase.

## RPD / Senior Gate

`chip-supergoal` embeds RPD. Do not invoke external `/rpd` to run this workflow.

- `RPD_PLAN_REVIEW` always runs before Stage 6 user review.
- `RPD_PHASE_REVIEW` runs in generated `/goal` for risky phases or `RPD required: yes`.
- `RPD_FINAL_REVIEW` always runs after `AUDIT_VERIFY` and before `AUDIT_COMPLETE`.
- Findings must mutate `ROADMAP.md`, `THINKING.md`, phase specs, protocol, code/work, or audit-fix specs. Otherwise mark `checked-holds` with evidence tier.

Load `references/rpd-review-gates.md` for the full evidence-tier, severity, overengineering-budget, and principal-review contract.

## Reference dispatch

Load only the matching canonical reference. Start with `references/dispatch-map.md` when the correct reference is not obvious.

Core active references:

- Planning/controller: `references/core-planning-contract.md`
- Artifact boundaries / review pack v2: `references/artifact-boundaries.md`
- Generated schemas: `references/artifact-schemas.md`
- Execution state machine / final audit: `references/execution-state-machine.md`
- Standard `/goal` compatibility: `references/upstream-goal-compatibility.md`
- Loop Design Gate: `references/loop-design-gate.md`
- RPD/Senior review: `references/rpd-review-gates.md`
- Telegram launch/delivery: `references/telegram-launch-and-delivery.md`
- Production safety: `references/production-safety.md`
- Skill maintenance: `references/skill-maintenance.md`

Specialist refs and superseded incident clusters live in `references/dispatch-map.md` and `references/INDEX.md`. Incident refs are for forensics unless the dispatch map names them for the current trigger.

For self-upgrades of `chip-supergoal` toward Architect+ / contract-compiler behavior, load `references/architect-plus-v3-upgrade-execution-lessons.md` before executing or repairing the mission package. It captures path-drift handling, non-git proof shape, temporary xfail cleanup, bytecode/privacy-scan pitfall, and local-alpha final audit rules.

If a new incident only adds another example of an existing invariant, update the relevant reference. Add to root only when it introduces a new invariant or public marker.

## Launch and delivery rules

- `LAUNCH_GOAL.md` is the replyable launch file. It contains the exact upstream-compatible `SUPERGOAL_GOAL_BODY:` line.
- `ROADMAP.md`, `THINKING.md`, and `PROTOCOL.md` must not contain their own actual launch body line.
- When creating a SuperGoal **about the `chip-supergoal` skill itself**, do not leave the generated package under the skill root if the package contains a real `LAUNCH_GOAL.md`: the skill self-test scans the skill tree and expects only the template launch body. Put the mission package in an external workspace path (for example `<workspace-dir>/.supergoal/<name>`) or ensure it is outside the self-test scan before running `scripts/test.sh`.
- Planning-stage review pack uses `review_pack_v2`: `THINKING.md`, `LOOP_DESIGN.md`, `ROADMAP.md`, `LAUNCH_GOAL.md`, plus `RESEARCH.md` when non-empty.
- **Chip default: always send the planning-stage `.md` files back into the current Telegram thread for Chip to review, even if he did not explicitly ask for files.** This is a standing preference for `chip-supergoal`, not an optional delivery mode. Include native `MEDIA:` attachments or use the Telegram delivery script, then verify delivery/receipt before saying the package is ready. A text summary without the `.md` files is incomplete.
- For Chip-facing SuperGoal packages with useful supporting context, also send `RESEARCH.md` when it exists and is not empty; keep `PROTOCOL.md`, `STATE.md`, and phase specs on disk unless Chip asks for the full bundle.
- If Telegram/native file delivery is required or triggered by the Chip default above, the run must create/send receipts and verify `ok=true` and `sent=true` before declaring the corresponding gate closed. If a multi-file send partially succeeds or one attachment times out, resend only the missing file(s), store all successful message IDs in the receipt, and record the partial-send note instead of treating the whole review pack as failed or silently complete.
- Final artifacts require `SUPERGOAL_FILES_SENT` before `SUPERGOAL_RUN_COMPLETE` when final-file delivery was requested.

## Verification checklist

After editing this skill or generating a package:

```bash
cd <installed-skill-dir>
bash scripts/test.sh
python3 <skills-dir>/create-skill/scripts/skill_workflow_guard.py <installed-skill-dir> || true
```

Then verify live loadability with `skill_view("chip-supergoal")` and, for critical refs, `skill_view("chip-supergoal", file_path="references/rpd-review-gates.md")`.

## Output Contract

For Chip, final planning output is compact and evidence-first:

1. what package was written
2. key risks/assumptions
3. which files were sent or where they are
4. exact launch instruction/card
5. what remains blocked, if anything

Do not claim execution success from this planner. Only the `/goal` executor can earn `AUDIT_COMPLETE` and `SUPERGOAL_RUN_COMPLETE`.
## Quick Test Checklist

- [ ] `skill_view("chip-supergoal")` loads this concise Principal+ root.
- [ ] `bash scripts/test.sh` exits 0 from the skill directory.
- [ ] `templates/LAUNCH_GOAL.md` is the only file with an actual line starting `SUPERGOAL_GOAL_BODY:`.
- [ ] `templates/ROADMAP.md` has no launch-body line.
- [ ] A filled `templates/phase-goal.txt` passes `scripts/validate-phase.sh`.
- [ ] `templates/PROTOCOL.md` preserves continuous execution through phase boundaries, forced-yield semantics, weak-blocker guard, and final-audit markers.
- [ ] New incident lessons update canonical references/tests instead of bloating root.
- [ ] If `.supergoal/` is ignored by git, stale package cleanup and direct package verification are reported separately from tracked implementation git status.

## Done Criteria

- [ ] Frontmatter has `name: chip-supergoal`, trigger-rich description, and `argument-hint`.
- [ ] Root `SKILL.md` stays under the local architecture budget enforced by `scripts/test.sh`.
- [ ] Planner writes `THINKING.md`, optional `RESEARCH.md`, `LOOP_DESIGN.md`, `ROADMAP.md`, `STATE.md`, `PROTOCOL.md`, `LAUNCH_GOAL.md`, and strict phase specs.
- [ ] Embedded RPD/Senior Gate remains self-contained; no external `/rpd` dependency.
- [ ] Risky phases require RPD metadata and measurable evidence.
- [ ] Final executor completion requires `AUDIT_COMPLETE` before `SUPERGOAL_RUN_COMPLETE`.
- [ ] File/Telegram delivery, when requested, is backed by receipts before completion.
- [ ] For Chip-facing planning packages, the review `.md` files were sent to the current Telegram thread by default: `THINKING.md`, `LOOP_DESIGN.md`, `ROADMAP.md`, `LAUNCH_GOAL.md`, and non-empty `RESEARCH.md`. If delivery could not be verified, the package is `SUPERGOAL_REVIEW_FILES_BLOCKED`, not ready.
