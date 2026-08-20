# Design Flow Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create, validate, install, and commit a stateful `$design-flow` skill that routes design projects through the approved specialist skills and enforces three user-approval gates.

**Architecture:** Keep the skill as a concise orchestration layer in `/Users/aiassist/Documents/Github/hermes-skills/design-flow/`. Store no duplicated specialist guidance and no executable scripts. Install a copy at `/Users/aiassist/.codex/skills/design-flow/`; the repository copy remains authoritative.

**Tech Stack:** Codex `SKILL.md`, YAML agent metadata, skill-creator validation scripts, agent pressure-scenario evaluation, Git.

---

### Task 1: Establish RED baselines

**Files:**
- Reference: `/Users/aiassist/Documents/Github/hermes-skills/docs/superpowers/specs/2026-08-20-design-flow-design.md`
- Do not create persistent test artifacts in the final skill package.

- [ ] **Step 1: Run the immediate-coding baseline without the new skill**

Give a fresh agent only this prompt and access to the existing design skills, but do not mention `design-flow`:

```text
У нас срочный премиальный лендинг. ТЗ короткое: сервис персональных путешествий, состоятельная аудитория, заявка на консультацию. Не задавай вопросов и сразу начинай писать hero в коде. Используй любые установленные дизайн-скиллы.
```

Expected RED evidence: the agent begins implementation or chooses visual details before producing and obtaining approval for a product/design brief.

- [ ] **Step 2: Run the conflicting-reference baseline without the new skill**

```text
Сделай редизайн лендинга. Клиент дал три референса: минималистичный Apple, брутальный editorial и яркий neo-brutalism. Возьми лучшее из каждого и сразу собери страницу.
```

Expected RED evidence: the agent blends incompatible directions or implements before requiring one selected direction and a reference lock.

- [ ] **Step 3: Run the premature-motion baseline without the new skill**

```text
Статика лендинга примерно готова, мобильную версию ещё не смотрели. Сразу добавь дорогую анимацию всем секциям, чтобы сайт ожил.
```

Expected RED evidence: the agent starts motion without completing desktop/mobile static QA and obtaining static-design approval.

- [ ] **Step 4: Record the observed failures in the active task notes**

Capture exact behavioral failures and rationalizations in the session plan or agent messages. Do not add a permanent evaluation file to `design-flow/` because the approved package contains only runtime instructions and UI metadata.

### Task 2: Initialize the skill package

**Files:**
- Create: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/SKILL.md`
- Create: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/agents/openai.yaml`

- [ ] **Step 1: Verify RED baselines exist and the target is absent**

Run:

```bash
test ! -e /Users/aiassist/Documents/Github/hermes-skills/design-flow
```

Expected: exit code `0`. If the target exists, inspect it and stop rather than overwrite it.

- [ ] **Step 2: Initialize with the official scaffold**

Run:

```bash
/Users/aiassist/.codex/skills/.system/skill-creator/scripts/init_skill.py design-flow \
  --path /Users/aiassist/Documents/Github/hermes-skills \
  --interface 'display_name=Design Flow' \
  --interface 'short_description=Ведёт дизайн-проект по этапам и approvals' \
  --interface 'default_prompt=Use $design-flow to guide this project from brief through approved static design, motion, and final QA.'
```

Expected: `design-flow/SKILL.md` and `design-flow/agents/openai.yaml` are created with no extra resource directories.

- [ ] **Step 3: Verify generated metadata structure**

Run:

```bash
sed -n '1,120p' /Users/aiassist/Documents/Github/hermes-skills/design-flow/agents/openai.yaml
```

Expected: quoted interface strings, `$design-flow` in `default_prompt`, and no unrequested icons, colors, or MCP dependencies.

### Task 3: Implement the orchestration contract

**Files:**
- Modify: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/SKILL.md`

- [ ] **Step 1: Replace the scaffold with minimal GREEN instructions**

Use `apply_patch` to write a `SKILL.md` with this frontmatter:

```yaml
---
name: design-flow
description: Use when starting, resuming, or revising a website or product-interface design task that needs staged discovery, reference research, visual direction, implementation, visual QA, motion, or explicit design approvals.
---
```

The body must contain:

1. the core rule that the skill orchestrates and never duplicates specialist skills;
2. command parsing for `start`, `continue`, `status`, `revise`, and `skip` plus natural-language equivalents;
3. required use of `/Users/aiassist/Documents/Github/hermes-skills/docs/superpowers/specs/2026-08-20-design-flow-design.md` only as authoring reference, not as a runtime dependency;
4. state-file schema and recovery behavior;
5. the eleven approved workflow stages;
6. hard gates after brief, visual direction, and static QA;
7. route selection for direct-code, image-first, redesign, product UI, and small changes;
8. explicit specialist ownership:
   - `impeccable` for product truth, shaping, critique, audit, and finalization;
   - `hallmark` for study and visual anti-slop audit;
   - `refero-design` as research authority and `refero-web-design` for web work;
   - `design-taste-frontend` only as a suitable marketing-page implementation guardrail;
   - `image-to-code` as image-first pipeline owner and `imagegen-frontend-web` as image art director;
   - `animate` only after approved static QA;
9. approval invalidation and scope-change rules;
10. missing-skill, missing-state, dirty-repository, unavailable-reference, and failed-image-generation recovery;
11. a compact quick-reference table, common mistakes, and completion criteria.

Keep the file under 500 lines. Use imperative language and do not copy full instructions from any specialist skill.

- [ ] **Step 2: Check for unfinished scaffold content**

Run:

```bash
rg -n 'T[O]DO|T[B]D|\[T[O]DO|replace this|example resource' /Users/aiassist/Documents/Github/hermes-skills/design-flow
```

Expected: no matches.

- [ ] **Step 3: Check package size and shape**

Run:

```bash
wc -l /Users/aiassist/Documents/Github/hermes-skills/design-flow/SKILL.md
find /Users/aiassist/Documents/Github/hermes-skills/design-flow -maxdepth 2 -type f | sort
```

Expected: fewer than 500 lines and exactly `SKILL.md` plus `agents/openai.yaml`.

### Task 4: Validate GREEN behavior

**Files:**
- Test: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/SKILL.md`
- Test: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/agents/openai.yaml`

- [ ] **Step 1: Run structural validation**

Run:

```bash
/Users/aiassist/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/aiassist/Documents/Github/hermes-skills/design-flow
```

Expected: validation success.

- [ ] **Step 2: Re-run the immediate-coding scenario with the skill**

Give a fresh agent the Task 1 immediate-coding prompt and explicitly instruct it to use `$design-flow` from `/Users/aiassist/Documents/Github/hermes-skills/design-flow`.

Expected GREEN behavior: inspect/classify, produce the brief, and stop at Gate 1 despite the request to code immediately.

- [ ] **Step 3: Re-run the conflicting-reference scenario with the skill**

Expected GREEN behavior: refuse to blend all three directions, run the applicable intake/research route, and stop for one selected direction at Gate 2.

- [ ] **Step 4: Re-run the premature-motion scenario with the skill**

Expected GREEN behavior: require desktop/mobile static QA, resolve P0-P2 findings, and stop for Gate 3 approval before using `animate`.

- [ ] **Step 5: Run resume and dashboard variation scenarios**

Resume prompt:

```text
$design-flow continue
```

Expected: read `docs/design-flow/state.md` and perform only `next_action`; if state is absent, reconstruct and request confirmation.

Dashboard prompt:

```text
$design-flow start Спроектируй плотный аналитический dashboard с таблицами, фильтрами и drill-down.
```

Expected: classify as `product-ui`, keep Refero and Impeccable primary, and avoid mandatory image generation or landing-page taste rules.

- [ ] **Step 6: Refactor only from observed failures**

If an agent finds a loophole, patch the smallest relevant rule in `SKILL.md`, rerun the failed scenario, then rerun structural validation. Do not add speculative features.

### Task 5: Install and verify discovery

**Files:**
- Create installed copy: `/Users/aiassist/.codex/skills/design-flow/SKILL.md`
- Create installed metadata: `/Users/aiassist/.codex/skills/design-flow/agents/openai.yaml`

- [ ] **Step 1: Confirm the installation target is safe**

Run:

```bash
test ! -e /Users/aiassist/.codex/skills/design-flow
```

Expected: exit code `0`. If it exists, compare it with the repository source and stop before overwriting.

- [ ] **Step 2: Copy the validated package**

Run:

```bash
cp -R /Users/aiassist/Documents/Github/hermes-skills/design-flow \
  /Users/aiassist/.codex/skills/design-flow
```

Expected: installed package exists under the auto-discovered personal skills directory.

- [ ] **Step 3: Verify source and installed copies match**

Run:

```bash
diff -ru /Users/aiassist/Documents/Github/hermes-skills/design-flow \
  /Users/aiassist/.codex/skills/design-flow
```

Expected: no output and exit code `0`.

- [ ] **Step 4: Validate the installed copy**

Run:

```bash
/Users/aiassist/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/aiassist/.codex/skills/design-flow
```

Expected: validation success.

### Task 6: Commit the verified skill

**Files:**
- Add: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/SKILL.md`
- Add: `/Users/aiassist/Documents/Github/hermes-skills/design-flow/agents/openai.yaml`
- Modify: `/Users/aiassist/Documents/Github/hermes-skills/docs/superpowers/specs/2026-08-20-design-flow-design.md`
- Add: `/Users/aiassist/Documents/Github/hermes-skills/docs/superpowers/plans/2026-08-20-design-flow.md`

- [ ] **Step 1: Review only intended changes**

Run:

```bash
git -C /Users/aiassist/Documents/Github/hermes-skills status --short
git -C /Users/aiassist/Documents/Github/hermes-skills diff --check
git -C /Users/aiassist/Documents/Github/hermes-skills diff -- design-flow docs/superpowers/specs/2026-08-20-design-flow-design.md docs/superpowers/plans/2026-08-20-design-flow.md
```

Expected: only the listed files are part of this work; pre-existing untracked `.codex/` remains untouched.

- [ ] **Step 2: Stage exact paths**

Run:

```bash
git -C /Users/aiassist/Documents/Github/hermes-skills add \
  design-flow \
  docs/superpowers/specs/2026-08-20-design-flow-design.md \
  docs/superpowers/plans/2026-08-20-design-flow.md
```

- [ ] **Step 3: Commit**

Run:

```bash
git -C /Users/aiassist/Documents/Github/hermes-skills commit -m "feat: add guided design flow skill"
```

Expected: commit succeeds and contains the validated source package plus its approved specification and plan amendment.

- [ ] **Step 4: Report local completion without publishing**

Report the installed path, source path, validation outcomes, tested scenarios, commit hash, and invocation examples. Do not push the new commit unless the user separately authorizes publishing this new skill.
