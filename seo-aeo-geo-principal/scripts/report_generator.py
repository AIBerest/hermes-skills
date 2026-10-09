#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from seo_scorecard import compute_scorecard
except ImportError:  # pragma: no cover - package import path in tests
    from scripts.seo_scorecard import compute_scorecard


def render_markdown(audit: dict[str, Any], *, title: str = "SEO/AEO/GEO audit", source: str = "audit-json") -> str:
    score = compute_scorecard(audit)
    priorities = score.get("priorities") or []
    lines = [
        f"# {title}",
        "",
        f"Source: `{source}`",
        f"Base: `{audit.get('base', 'fixture')}`",
        f"Score: **{score['score']}/100**",
        f"Model: `{score.get('model_version', 'unknown')}`",
        "Metric: advisory readiness, NOT rankings, indexing, traffic or citation probability.",
        f"Coverage: `{audit.get('coverage', 'fixture/provided evidence')}`",
        f"Crawl status: `{audit.get('crawl_status', 'provided evidence')}`; abort reason: `{audit.get('abort_reason') or 'none'}`",
        "",
        "## Scorecard",
        "",
        "| Criterion | Score | Evidence tier | Confidence | Impact | Effort | Priority | Residual gap |",
        "|---|---:|---|---|---|---|---:|---|",
    ]
    for row in score["scorecard"]:
        lines.append("| {criterion} | {score} | {evidence_tier} | {confidence} | {impact} | {effort} | {priority} | {residual_gap} |".format(**row))
    lines += ["", "## Top priorities", ""]
    for row in priorities[:5]:
        lines.append(f"- `{row['criterion']}` - priority `{row['priority']}`, gap `{row['residual_gap']}`, evidence `{row['evidence']}`")
    lines += ["", "## Residual measurement gaps", ""]
    gaps = [r for r in score["scorecard"] if r.get("residual_gap") and r["residual_gap"] != "none"]
    if gaps:
        for row in gaps:
            lines.append(f"- {row['criterion']}: {row['residual_gap']} ({row['evidence_tier']}, confidence {row['confidence']})")
    else:
        lines.append("- none")
    if audit.get("crawler_access"):
        lines += ["", "## Crawler purpose and access", ""]
        for bot, state in audit["crawler_access"].items():
            lines.append(f"- {bot}: purpose={state['purpose']}; robots={state['robots_allowed']}; WAF={state['waf_access']}")
    if audit.get("pages"):
        lines += ["", "## Content extraction hints (not measured citations)", ""]
        for page in audit["pages"]:
            if page.get("extractability"):
                lines.append(f"- `{page['url']}`: `{page['extractability']}`")
    return "\n".join(lines) + "\n"


def write_report(audit_path: str | Path, output_path: str | Path, *, title: str = "SEO/AEO/GEO audit") -> Path:
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(audit, title=title, source=str(audit_path)), encoding="utf-8")
    return out
