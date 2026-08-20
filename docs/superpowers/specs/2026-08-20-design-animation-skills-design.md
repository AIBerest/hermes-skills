# Design and animation skills installation

## Goal

Install Impeccable and the complete official Emil Kowalski skills collection for Codex, then preserve portable copies in `AIBerest/hermes-skills` for review, backup, and reuse.

## Scope

- Keep the existing, current `Design-Taste-Frontend/` copy unchanged.
- Install the complete `emilkowalski/skills` collection at user scope.
- Install Impeccable at user scope for Codex.
- Do not attach an Impeccable hook to the `hermes-skills` repository. Hooks are executable, project-specific integration and must be enabled separately in an actual frontend project.
- Add one top-level directory per portable skill to `hermes-skills`.
- Update the root README with the installed skills, upstream repositories, and update instructions.
- Commit the imported files on `codex/add-design-animation-skills` and push that branch to `origin`.

## Repository layout

Impeccable will live in `Impeccable/`. Each Emil Kowalski skill will use a readable top-level directory based on its canonical skill name. The canonical `name:` value inside each `SKILL.md` remains unchanged so Codex activation continues to work.

Only files required by a skill are copied: `SKILL.md`, referenced standards, recipes, templates, scripts, and assets. Repository metadata, caches, generated output, unrelated demos, and project hooks are excluded.

## Installation and provenance

Official upstream sources are the only accepted sources:

- `https://github.com/pbakaus/impeccable`
- `https://github.com/emilkowalski/skills`
- Existing Taste copy: `https://github.com/Leonxlnx/taste-skill`

Global installation follows each upstream project's documented installer. The vendored copy is taken from the same downloaded revision. README provenance records the upstream URL and the revision used when practical.

## Safety and error handling

- Abort before modifying the repository if an installer or upstream download fails.
- Preserve any pre-existing global skill directory; do not overwrite unrelated user content silently.
- Inspect installer output for hooks or executable integrations.
- Exclude secrets, local configuration, caches, screenshots, and runtime state.
- Stage only the explicitly added skill directories, README, and this specification.
- Push only after validating the staged diff.

## Verification

Before the final commit and push:

1. Confirm every imported directory contains a readable `SKILL.md` with valid frontmatter and a canonical `name:`.
2. Confirm every relative file referenced by an imported `SKILL.md` exists in its directory.
3. Confirm global Codex discovery finds Impeccable and every Emil skill.
4. Compare vendored skill files with the installed or downloaded upstream revision.
5. Scan the staged diff for secrets, runtime output, hooks, and unexpected binaries.
6. Confirm the branch is pushed and its remote commit matches local `HEAD`.

## Completion criteria

The work is complete when Impeccable and the full Emil collection are discoverable by Codex, portable copies and provenance documentation are committed in `hermes-skills`, no project hook was added, and the feature branch is present on `origin`.
