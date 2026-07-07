# Skill maintenance

Use when a SuperGoal edits, validates, packages, or publishes Hermes skills.

## Live path first

Resolve the live `skill_dir` before trusting old paths. User-local skills may be flat or category-backed; repo-backed copies may be stale. Do not create duplicate skills because a hard-coded path failed.

## Validation

For changed skills:

- parse frontmatter
- keep root concise and directive
- move heavy detail to references
- verify linked files load
- run helper guards when available
- run focused tests/probes
- scan changed files for secrets/private runtime residue
- verify `skill_view` loads the edited skill

## Principal+ rule

New incident lessons should update canonical references and tests. Root `SKILL.md` only changes for new invariants, public markers, or dispatch rules.

## User-story coverage ledgers

When auditing a skill feature-by-feature, keep one canonical ledger under the skill/repo (for example `docs/<skill>-user-stories.csv`) with stable IDs, source files, user story, expected behaviour, status, evidence, errors, fix notes, and retest status.

Add a deterministic harness (for example `scripts/test-user-stories.py`) that reads the ledger and verifies each expected behaviour against real skill files. If the harness writes status back to CSV, force LF line endings (`lineterminator='\n'`) and re-stage the CSV after the harness runs; otherwise `git diff --check` may fail on CRLF/trailing-whitespace noise introduced by Python's default CSV writer.

If the live skill path is separate from the git repo, sync the ledger and harness into the live skill as well as the repo, then run both repo and live validations before reporting completion.


## Feature/user-story audit

When auditing a skill itself, use `references/skill-feature-audit-user-stories.md`: create one canonical CSV in the repo/worktree, derive rows from actual loaded code/docs, add a deterministic test harness for row-level assertions, patch the smallest canonical source, sync live skill and repo copy if they differ, rerun both the row harness and normal skill tests, then verify `skill_view` loads the changed live file.

## Repo/private delivery gate

If the user says `git push`, `private repo`, `publish skill`, or names a GitHub target, done requires:

1. identify the canonical working tree and whether the live skill dir is itself a git repo;
2. commit relevant changes when repo-backed;
3. push to the requested private remote/branch;
4. verify remote HEAD matches local HEAD (`git ls-remote` / fresh clone / `gh repo view` as applicable);
5. report clean `git status` or explicitly say local-only/uncommitted and why.

Never report a repo-backed skill as delivered from a non-git live skill dir without either syncing to the canonical repo or declaring the boundary.
