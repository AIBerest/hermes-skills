# Telegram launch and delivery

Use when the SuperGoal package or final artifacts must be sent through Telegram, or when launch happens by replying `/goal` to a Markdown file/message.

## Launch surfaces

Canonical order:

1. `LAUNCH_GOAL.md` native document with `SUPERGOAL_GOAL_BODY:`.
2. Clean Telegram launch card with button/reply affordance.
3. Explicit `/goal start <objective>` fallback outside code fences if rich launch fails or the receiving bot expects a start subcommand.
4. Plain-text `/goal "..."` fallback only when that surface is known to accept it.

If a user replies with only `/goal` and the gateway says “No goal for this session”, treat it as a launch UX miss: re-emit the same objective in `/goal start ...` form instead of assuming the package is running.

Do not use `ROADMAP.md`, `THINKING.md`, or `PROTOCOL.md` as hidden launch surfaces.

## Review delivery gate

When Chip asks for SuperGoal/ТЗ files, send the canonical `review_pack_v2` native `.md` files by default:

- `THINKING.md`
- `LOOP_DESIGN.md`
- `ROADMAP.md`
- `LAUNCH_GOAL.md`
- `RESEARCH.md` only when it exists and is non-empty

`references/artifact-boundaries.md` is the source of truth for review-pack ownership, stage, receipt, and planning-vs-final delivery boundaries. The planner must script delivery when available and write `.supergoal/out/review-md-files-delivery-receipt.json` with `ok=true`, `sent=true`, and `pack_version="review_pack_v2"`. If sending fails, print `SUPERGOAL_REVIEW_FILES_BLOCKED` with the reason and do not pretend the files were delivered.

## Final artifact gate

If final files are requested, generated `/goal` must package and send final artifacts, verify receipt, then print `SUPERGOAL_FILES_SENT` before `SUPERGOAL_RUN_COMPLETE`.

## Idempotency

Use target + file/archive hash for idempotency. Do not resend automatically unless the user explicitly asks or `SUPERGOAL_FORCE_RESEND=1` is set for a deliberate retry.
