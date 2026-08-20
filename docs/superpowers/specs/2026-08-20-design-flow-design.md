# Design Flow Skill Design

## Goal

Create a personal Codex skill named `design-flow` that guides a web or product design task from an incoming brief through research, implementation, static visual approval, motion, and final hardening. The skill orchestrates existing specialist skills instead of duplicating their instructions.

## User Experience

The user can invoke the workflow with:

```text
$design-flow start <brief, file, URL, or repository target>
$design-flow continue
$design-flow status
$design-flow revise <stage>
$design-flow skip <stage and reason>
```

Natural-language requests such as “проведи этот лендинг по дизайн-флоу” should also trigger the skill.

The workflow is approval-driven. It must stop and wait for explicit user approval after:

1. the design brief;
2. selection of one visual direction;
3. static visual QA before motion.

Approval of one gate does not imply approval of later gates.

## Architecture

`design-flow` is a lightweight stateful orchestrator. Its `SKILL.md` contains routing, gate, state, and recovery rules. It references existing skills by name and requires Codex to load only the specialist skills needed for the current stage.

Per-project progress is stored in `docs/design-flow/state.md`. Supporting artifacts use stable paths when the project permits:

- `PRODUCT.md` for durable product truth;
- `docs/design-flow/brief.md` for the approved design brief;
- `DESIGN.md` for the reference lock and design decisions;
- `docs/design-flow/qa.md` for static visual QA.

The skill itself is developed in the `hermes-skills` repository as `Design-Flow/` and installed into `~/.codex/skills/design-flow/`. The repository copy is the source of truth.

## State Contract

`docs/design-flow/state.md` contains YAML frontmatter followed by a concise human-readable log. Required frontmatter fields are:

```yaml
project: project-name
task_type: greenfield-landing
current_stage: brief
status: waiting-for-approval
build_path: undecided
selected_direction: null
approved:
  product_brief: false
  visual_direction: false
  static_design: false
artifacts:
  product: PRODUCT.md
  brief: docs/design-flow/brief.md
  design: DESIGN.md
  qa: docs/design-flow/qa.md
next_action: approve-or-revise-brief
```

Allowed `task_type` values are `greenfield-landing`, `redesign`, `product-ui`, and `small-change`. Allowed `build_path` values are `undecided`, `direct-code`, and `image-first`.

Every completed stage appends its result, artifact path, decisions, approval state, and next action to the log. `continue` must read this file before taking action. If it is missing, the skill reconstructs state from existing artifacts and asks the user to confirm the recovered stage before proceeding.

## Workflow

### 1. Intake and classification

Inspect the brief, repository, existing product documentation, and available assets. Classify the task without changing code. Record the classification and explain the proposed route.

### 2. Product truth

Use `impeccable init` when durable product context is absent or stale. Preserve existing validated `PRODUCT.md` content. Do not put aesthetic decisions in `PRODUCT.md`.

### 3. Design brief

Use `impeccable shape` to produce `docs/design-flow/brief.md` with audience, job, desired outcome, proof, scope, content, states, constraints, and success criteria.

Stop at Gate 1. Present the brief and ask for explicit approval or revisions. Do not begin reference research before approval.

### 4. Existing design and reference intake

For a redesign, use `hallmark audit` on the existing surface. When the user supplies a reference, use `hallmark study` to extract transferable design DNA without cloning it. Skip this stage for projects with neither an existing surface nor supplied references and record why.

### 5. Refero research and direction selection

Use `refero-design` as the research authority. Also use `refero-web-design` for websites and landing pages. Research styles first, then relevant screens, and flows only when the product has a multi-step journey.

Produce three genuinely distinct directions. Each direction must state its visual idea, typography, palette, composition, media strategy, product fit, and risks.

Stop at Gate 2. The user must select one direction. Do not blend unselected directions.

### 6. Reference lock

Write the selected direction to `DESIGN.md`, including canvas, typography, accent roles, grid, layout, section order, media strategy, component language, density, responsive behavior, and elements that must not drift. Maintain a decision ledger for later changes.

### 7. Build-path selection

Choose `direct-code` when an approved target already exists, the task is small, or generated imagery would not materially improve the result. Use `design-taste-frontend` as an implementation guardrail for marketing pages, portfolios, and redesigns.

Choose `image-first` for a visually important greenfield landing page or major redesign without a sufficient visual target. Use `image-to-code` as the pipeline owner and `imagegen-frontend-web` for image art direction. Generate three representative hero directions only if Gate 2 still needs visual evidence; after selection, generate section images only for the selected direction.

For dense product interfaces, dashboards, tables, or multi-step tools, keep Refero and Impeccable as the primary authorities and do not force `design-taste-frontend` or image generation into the route.

Record the chosen path and rationale before implementation.

### 8. Static implementation

Implement against the approved brief and `DESIGN.md`. Specialist implementation skills may execute the work, but they may not silently redefine product scope, palette, typography, information architecture, or the selected visual direction.

Do not add decorative motion during this stage.

### 9. Static visual QA

Capture and inspect representative desktop and mobile states. Compare them with the approved visual target. Use `hallmark audit` for visual anti-slop review, `impeccable critique` for UX review, and `impeccable audit` for responsive, accessibility, state, and implementation quality.

Write findings to `docs/design-flow/qa.md` and classify them as P0 through P3. Resolve P0, P1, and P2 findings before Gate 3.

Stop at Gate 3. Present screenshots, the comparison summary, remaining P3 items, and ask the user to approve the static design. Do not start motion before approval.

### 10. Motion

Use `animate` only after Gate 3. Define the purpose and expected interaction frequency for each animation. Prefer the cheapest suitable mechanism, animate transform and opacity where possible, support reduced motion, and avoid animation when frequency or usability argues against it.

### 11. Finalization

Use the relevant Impeccable operations: `polish`, `adapt`, `harden`, and `optimize`. Re-run proportional visual and technical verification. Mark the workflow complete only when required artifacts exist, all three gates are approved, no P0-P2 findings remain, and the final implementation matches the reference lock.

## Gate and Revision Rules

- “Approved”, “утверждаю”, or an equally explicit statement approves only the currently presented gate.
- Ambiguous positive feedback does not count as approval; ask a concise confirmation.
- `revise <stage>` invalidates that stage and every dependent approval after it. Revising the visual direction, for example, clears visual-direction and static-design approval.
- `skip` requires a recorded reason. Product brief, direction selection, reference lock, and static approval cannot be skipped. Conditional research, image generation, motion, and individual finalization operations may be skipped when irrelevant.
- If the user changes scope materially, return to the earliest affected stage and update state before continuing.
- Never claim a stage is complete without checking its required artifact or observable result.

## Error and Recovery Behavior

- If a required specialist skill is unavailable, stop before its dependent stage, name the missing skill, and offer an installation or manual fallback.
- If Refero tooling or live references are unavailable, use its bundled references and clearly label the research limitation.
- If image generation fails, preserve the approved direction and offer direct-code implementation rather than silently substituting a different style.
- If the repository is dirty, preserve unrelated user changes and scope edits to workflow artifacts and authorized implementation files.
- If no repository is available, maintain the same gates in conversation and create state once a project path is provided.

## Skill Package

The package contains only:

```text
Design-Flow/
├── SKILL.md
└── agents/
    └── openai.yaml
```

No script is required because routing and approvals depend on judgment. No duplicated copies of the specialist skill instructions are bundled.

## Validation Scenarios

Validation must begin with baseline scenarios without `design-flow`, then repeat them with the skill installed.

1. A user asks for a premium landing page and pressures the agent to start coding immediately. The skill must produce and await approval of the brief first.
2. A user supplies three conflicting references. The skill must research and require selection of one direction instead of blending them.
3. A user asks to add animation before reviewing the static mobile layout. The skill must complete static QA and wait at Gate 3.
4. A returning user says `$design-flow continue`. The skill must read state and resume from the recorded next action.
5. A dashboard task should avoid forcing landing-page taste rules and unnecessary image generation.
6. A material revision after Gate 2 must invalidate dependent approvals and return to the affected stage.

Success means the agent selects the correct route, preserves the approval gates under pressure, resumes reliably, and delegates specialist work without duplicating or contradicting the source skills.

## Non-Goals

- Replacing the specialist design and animation skills.
- Automatically approving design decisions for the user.
- Requiring image generation for every project.
- Creating a project management system beyond the local workflow state.
- Publishing, deploying, or pushing project code unless the user separately authorizes it.
