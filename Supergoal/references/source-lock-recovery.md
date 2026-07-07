# Source-lock recovery for SuperGoal execution

Use when a SuperGoal package is blocked on missing exact URLs, dates, runtime mapping, or CRM/application destination.

## Pattern

Before asking Chip to resend everything, actively recover what is recoverable:

1. Re-read the package state (`STATE.md`, `RESEARCH.md`, `ROADMAP.md`) and preserve explicit blockers.
2. Search prior session context for exact final funnel/copy, user corrections, and named artifacts.
3. Inspect the target runtime read-only to map repo, service/container, bot identity, start handler, and existing DB surfaces.
4. For public URLs, derive likely candidates from current app snapshots/content indexes when available, then verify with HTTP status before reducing the blocker list.
5. Update `RESEARCH.md` with recovered evidence and `STATE.md` with a smaller blocker list.
6. If the blocker is CRM/application routing for a Human20 bot funnel, inspect the existing sales/waitlist bot before asking Chip: look for `record_lead_application`, `lead_application`, `v2_waitlist_events`, `v2_waitlist_leads`, manager/question chat env, and recent sanitized event rows. A recovered canonical destination can close the generic “where store applications” blocker, while still leaving product approval or bot-runtime choice blocked.
7. Only stop as blocked on inputs that cannot be safely recovered: exact live date/time, live webinar URL, final approval that a candidate URL is intended, or application/CRM routing if no canonical destination can be proven or multiple destinations remain equally plausible.

## Guardrails

- Do not code live behavior with placeholder links for buttons like `Перейти на эфир` or `Смотреть бонусный урок`.
- Do not invent CRM destinations. If several plausible stores exist, keep the destination as a blocker.
- If user-facing Russian copy is involved for Человек 2.0, avoid `Human20/human20` in public text. Internal repo/service names may remain as evidence.
- When a goal manager/session says “continue” but no `/goal` state exists, continue the next concrete planning/recovery step manually and write evidence back into the package instead of looping on the launcher error.
