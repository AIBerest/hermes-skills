"""Optional read-only stdio MCP. No file-write, credential, fix or deployment tools."""
from mcp.server.fastmcp import FastMCP
try:
    from seo_live_audit import audit
    from seo_scorecard import compute_scorecard
    from snapshots import compare
except ImportError:
    from scripts.seo_live_audit import audit
    from scripts.seo_scorecard import compute_scorecard
    from scripts.snapshots import compare

mcp = FastMCP("seo-aeo-geo-principal")

@mcp.tool()
def seo_audit(base_url: str, max_pages: int = 20) -> dict:
    """Read bounded public same-origin HTML. No cookies, private URLs or changes."""
    return audit(base_url, ["/robots.txt", "/sitemap.xml", "/llms.txt"], max_pages)

@mcp.tool()
def seo_score(audit_json: dict) -> dict:
    """Compute advisory readiness from supplied audit evidence, not real visibility."""
    return compute_scorecard(audit_json)

@mcp.tool()
def seo_compare(before: dict, after: dict) -> dict:
    """Recompute before/after scorecards and show dimension regressions."""
    return compare(before, after)

if __name__ == "__main__":
    mcp.run(transport="stdio")
