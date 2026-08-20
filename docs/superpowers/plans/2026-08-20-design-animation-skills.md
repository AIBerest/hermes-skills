# Design and Animation Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install Impeccable and all official Emil Kowalski skills globally for Codex, preserve portable upstream copies in `hermes-skills`, document provenance, and push the reviewed branch.

**Architecture:** Official upstream repositories are cloned at fixed revisions into a temporary directory. Their documented installers provide the global Codex installation, while only self-contained skill payloads are copied into top-level repository directories; Impeccable project hooks and runtime state are intentionally excluded.

**Tech Stack:** Agent Skills (`SKILL.md`), `npx skills`, Impeccable CLI, Git, POSIX shell.

---

## File map

- Create: `Impeccable/`
- Create: `Animate/`
- Create: `Animate-Expo/`
- Create: `Animation-Vocabulary/`
- Create: `Apple-Design/`
- Create: `Ask-Sonner/`
- Create: `Emil-Design-Eng/`
- Create: `Find-Animation-Opportunities/`
- Create: `Improve-Animations/`
- Create: `Pick-UI-Library/`
- Create: `Prototype/`
- Create: `Review-Animations/`
- Modify: `README.md`
- Keep unchanged: `Design-Taste-Frontend/`

### Task 1: Acquire and identify official sources

- [ ] Clone `pbakaus/impeccable` and `emilkowalski/skills` with `--depth 1` into a new `mktemp -d` directory.
- [ ] Record both source commit hashes with `git rev-parse HEAD`.
- [ ] Confirm Impeccable contains `.agents/skills/impeccable/SKILL.md` and Emil contains exactly these eleven skill directories: `animate`, `animate-expo`, `animation-vocabulary`, `apple-design`, `ask-sonner`, `emil-design-eng`, `find-animation-opportunities`, `improve-animations`, `pick-ui-library`, `prototype`, `review-animations`.
- [ ] Abort if either repository, expected payload, or canonical skill list is missing.

### Task 2: Install globally for Codex

- [ ] Inspect `npx impeccable --help` and `npx skills@latest add --help` before mutation.
- [ ] Install Impeccable globally for Codex with hooks disabled using the supported equivalent of `npx impeccable install --providers=codex --scope=global --no-hooks`.
- [ ] Install the complete Emil collection with `npx skills@latest add emilkowalski/skills -g -y`.
- [ ] Enumerate global discovery paths and confirm `impeccable` plus all eleven Emil canonical `name:` values are present.
- [ ] Preserve any unrelated pre-existing global skill directories.

### Task 3: Add portable repository copies

- [ ] Copy `.agents/skills/impeccable/` from the fixed Impeccable clone into `Impeccable/`.
- [ ] Remove or exclude project hook manifests, runtime caches, screenshots, local config, and generated state; retain the skill's own referenced scripts, agents, and reference material.
- [ ] Copy each fixed Emil `skills/<canonical-name>/` payload into the matching directory from the file map.
- [ ] Confirm the existing `Design-Taste-Frontend/` tree and hash remain unchanged.

### Task 4: Document provenance and operation

- [ ] Replace the minimal root README with a catalog that explains activation, upstream sources, fixed source revisions, global install commands, update commands, the no-hook policy, and the existing Taste installation.
- [ ] List all twelve newly imported canonical skill names and their repository directory names.
- [ ] State that imported third-party files retain their upstream licenses and source provenance.

### Task 5: Validate imported payloads

- [ ] Parse every new `SKILL.md` frontmatter and verify the canonical `name:` is non-empty and unique.
- [ ] Search new payloads for broken relative Markdown links and fail on a missing local target.
- [ ] Compare every imported directory recursively with its corresponding directory in the fixed upstream clone, allowing only explicitly documented exclusions.
- [ ] Scan new files for private keys, tokens, local home paths, `.env` files, hooks, caches, screenshots, and unexpected binaries.
- [ ] Run `git diff --check` and inspect `git status --short`.

### Task 6: Commit and publish

- [ ] Stage only the twelve new skill directories, `README.md`, and this plan.
- [ ] Inspect the complete cached diff and file statistics before committing.
- [ ] Commit with a message describing the Impeccable and Emil skill import.
- [ ] Push `codex/add-design-animation-skills` to `origin` with upstream tracking.
- [ ] Verify `git rev-parse HEAD` equals `git rev-parse origin/codex/add-design-animation-skills` and the worktree is clean.
