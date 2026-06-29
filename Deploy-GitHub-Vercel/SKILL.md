---
name: deploy-github-vercel
description: Automate publishing of the current local git project to GitHub and Vercel via API. Use when the user asks to publish/deploy a site with commands like `/deploy github` (GitHub only) or `/deploy all` (GitHub + GitHub App access + Vercel + deployment checks).
---

# Deploy GitHub + Vercel

## Command Routing

- Parse the user command strictly.
- Run GitHub-only flow for `/deploy github`.
- Run full flow for `/deploy all`.
- Ask one short clarification question if the user sends `/deploy` without a mode.

## Runner (Cross-Platform)

1. Use a script from `scripts/` as the primary runner.
2. Execute it for the current project directory (do not change the project working directory):
- Preferred: `python3 <skill_dir>/scripts/deploy.py github --repo-path "$PWD"` or `all`.
- Python fallback: `python <skill_dir>/scripts/deploy.py github --repo-path "$PWD"` or `all`.
- Node fallback: `node <skill_dir>/scripts/deploy.js github --repo-path "$PWD"` or `all`.
3. If both Python and Node.js are unavailable, execute the same workflow steps manually with shell/API in the current repository directory.

## Required Inputs

1. Read `.env` from the current repository root.
2. Validate variables from `references/.env.example`.
3. Require these keys for both modes:
- `GITHUB_USERNAME`
- `GITHUB_TOKEN`
4. Require these keys additionally for `/deploy all`:
- `GITHUB_APP_INSTALLATION_ID`
- `VERCEL_TOKEN`
5. Treat `VERCEL_TEAM_ID` and `REPO_NAME` as optional.

If required variables are missing, stop and return the exact missing keys.

## Execution Rules

1. Work fully automatically with shell/API calls.
2. Do not require browser actions from the user.
3. Run in the user's current repository directory only (do not switch to another project directory).
4. Keep actions idempotent where possible:
- Reuse repository/project if they already exist.
- Update `origin` URL if it points elsewhere.
5. Before workflow steps, run preflight checks:
- Git is available and writable in repo/.git.
- Network access to GitHub API is available.
- Broken proxy env values do not block API calls.
6. Stop immediately on permission/auth failures and show:
- endpoint,
- HTTP status,
- short API error body.

## Workflow

1. Read `references/workflow.md` and follow the step order exactly.
2. For `/deploy github`, execute only steps 1-4.
3. For `/deploy all`, execute full steps 1-11.
4. Respect the stop condition from step 6 when GitHub App access fails.

## Final Response Format

After execution, return:

1. Mode (`github` or `all`).
2. `REPO_NAME` and GitHub repo URL.
3. For `/deploy all`: Vercel project id/name, deployment URL, deployment status, and site health-check result.
4. Any skipped step with the reason.
