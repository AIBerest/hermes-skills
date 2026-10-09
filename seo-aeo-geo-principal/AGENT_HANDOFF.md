# Installation and optional MCP

Install as seo-aeo-geo-principal, replacing its previous copy rather than adding a duplicate
chip-seo-geo-aeo root. Keep backups outside discoverable skill directories.
Source: AIBerest/hermes-skills, seo-aeo-geo-principal directory.
Use Python 3.10+ and an isolated environment for requirements.txt.

## Optional MCP

The CLI works without MCP. To expose audit, score and compare as tools:

```bash
.venv/bin/python -m pip install -r requirements-mcp.txt
.venv/bin/python scripts/mcp_server.py
```

Configure a local stdio MCP client with absolute interpreter/script paths. The public MCP
audit does not enable local/private networks, fixes, deployments or credentialed analytics.
Verify initialize, list_tools and a fixture seo_score call before reporting it connected.
Installing this skill does not automatically register an MCP server.

## Verification

PATH="$PWD/.venv/bin:$PATH" bash scripts/test.sh runs offline behavior regressions and the
real stdio handshake when MCP is installed. Live HTTP smoke is a separate bounded check.
Generated audits, snapshots, credentials and virtual environments must not be committed.
