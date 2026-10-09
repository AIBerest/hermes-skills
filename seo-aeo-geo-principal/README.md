# SEO / AEO / GEO Principal+

Version 2.1.0 merges the original installed toolkit with the supplied Chip 2.0 derivative.
The installed name remains seo-aeo-geo-principal; existing invocations keep working.

## What it does

- Audits a bounded same-origin sample across sitemap indexes and robots-declared sitemaps.
- Reports coverage and stops on 403/429 or repeated failures; public requests default to a 2-second pause.
- Separates main-content structure from site navigation, while retaining SEO link/image checks.
- Observes robots policies separately for search, training and user-fetch bots; WAF remains unmeasured.
- Saves hashed local snapshots and compares all 12 dimensions, regressions and sample warnings.
- Labels scores as advisory readiness. Optional llms.txt/agent files do not change the score.
- Offers optional read-only MCP tools: seo_audit, seo_score, seo_compare.

## Run

Python 3.10+:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/seo_audit_cli.py audit --base https://example.com --max-pages 5 --output before.json
.venv/bin/python scripts/seo_audit_cli.py report --input before.json --output report.md
.venv/bin/python scripts/seo_audit_cli.py snapshot --input before.json --history-dir history
.venv/bin/python scripts/seo_audit_cli.py compare --before before.json --after after.json
```

Use --allow-local only for a loopback preview such as http://127.0.0.1:3000.
The CLI exits 2 after writing an aborted/partial audit so automation can detect incomplete results.
Do not compare old stored totals directly: the score formula changed; compare recomputes both
audits under the current model and reports sample differences.

Package verification: PATH="$PWD/.venv/bin:$PATH" bash scripts/test.sh.
Optional MCP installation and verification are in AGENT_HANDOFF.md.

## Limits

Static HTML only; no browser rendering, automatic fixes, private analytics, paid citation
measurements or deployments. A sample is not full coverage. Score changes do not establish
ranking/traffic/citation improvements. Network guards are not a hardened remote fetch proxy.
Read references/measurement-truth.md for measurement boundaries and provider documentation.
