# hermes-skills

Portable Agent Skills used with Codex and other compatible coding agents. Each
top-level skill directory is reviewable and can be copied into an agent's skill
discovery path.

## Design and motion stack

| Repository directory | Canonical skill | Purpose | Upstream |
| --- | --- | --- | --- |
| `Design-Taste-Frontend/` | `design-taste-frontend` | Anti-slop frontend direction and implementation rules | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) |
| `Impeccable/` | `impeccable` | Design context, audits, polish, live browser iteration, and deterministic detectors | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| `Animate/` | `animate` | Build purposeful web UI animations | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Animate-Expo/` | `animate-expo` | Motion and gestures for React Native and Expo | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Animation-Vocabulary/` | `animation-vocabulary` | Precise language for describing motion | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Apple-Design/` | `apple-design` | Apple interface and fluid-motion principles adapted for the web | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Ask-Sonner/` | `ask-sonner` | Sonner toast setup, styling, recipes, and fixes | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Emil-Design-Eng/` | `emil-design-eng` | General design-engineering and motion guidance | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Find-Animation-Opportunities/` | `find-animation-opportunities` | Find UI states that benefit from motion and reject gratuitous motion | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Improve-Animations/` | `improve-animations` | Audit a codebase and produce prioritized motion-improvement plans | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Pick-UI-Library/` | `pick-ui-library` | Select a maintained accessible component library | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Prototype/` | `prototype` | Build and compare several UI variants | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| `Review-Animations/` | `review-animations` | Strict review of animation and motion code | [emilkowalski/skills](https://github.com/emilkowalski/skills) |

The design stack is intended to be layered: Taste defines the broad visual
direction, Impeccable supplies project context and systematic design passes,
and Emil Kowalski's focused skills make and review motion.

## Imported revisions

The copies added on 2026-08-20 came from these upstream commits:

- Impeccable: `f88b2837a7d7c3182e46307bbbb091a1ed547571`
- Emil Kowalski skills: `e879241fab3cdb22e8d95587cdbf40b57a88d7da`

`Design-Taste-Frontend/` was already current when these skills were imported
and was intentionally left unchanged.

Each imported directory includes the applicable upstream license; Impeccable
also includes its upstream `NOTICE.md`. The vendored Impeccable snapshot differs
from upstream only by whitespace normalization in files reported by
`git diff --check`; its executable content is otherwise unchanged.

## Global Codex installation

Install the current official Emil collection:

```bash
npx skills@latest add emilkowalski/skills -g -y
```

The official interactive Impeccable installer is:

```bash
npx impeccable install --providers=codex --scope=global --no-hooks
```

To install this repository's reviewed Impeccable snapshot without enabling a
project hook:

```bash
mkdir -p ~/.agents/skills
cp -R Impeccable ~/.agents/skills/impeccable
```

New skills are available to Codex on the next turn or after restarting the
agent surface if it caches skill discovery.

## Hooks and executable scripts

Impeccable includes scripts used by its skill commands, live mode, and optional
detectors. This repository does not install a project `.codex/hooks.json`.
Enable a hook only inside a frontend project where automatic checks are wanted,
after reviewing the hook definition and trusting that project.

## Updating snapshots

Update global installations from their official sources first, inspect the
changes, then replace the corresponding portable directory and update the
revision above. Do not copy caches, screenshots, `.env` files, local runtime
configuration, or project hook manifests into this repository.

Third-party files retain their upstream provenance and licenses. Consult the
license bundled with each directory and the linked repositories before
redistribution or modification.
