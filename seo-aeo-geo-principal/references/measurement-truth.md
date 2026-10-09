# Measurement truth and integration policy

Access != crawl != index != impression != mention != citation != conversion.
Every claim needs its own dated evidence. A successful IndexNow submission is not indexing.

The inherited 12-dimension score is a labelled **advisory readiness heuristic**.
It is neither probability of citation nor Google's ranking score. Character-count,
FAQ-type and entity-type thresholds require editorial interpretation; do not force
FAQ, Person or Course markup on pages where they do not match visible content.
Missing llms.txt does not establish an AI-search failure. Optional agent endpoints
are not SEO requirements. Before changing crawler policies consult current sources:

* https://developers.google.com/search/docs/appearance/ai-features
* https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers
* https://developers.openai.com/api/docs/bots
* https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler

ClaudeBot is training; Claude-SearchBot is search; Claude-User is user fetch.
ChatGPT-User is user-initiated; OpenAI says robots.txt rules may not apply.
Its robots result is a policy hint, not proof of blocked user-requested access.
Google-Extended is a training/product-use policy token, not AI Overviews access.
Audit robots decisions separately from CDN/WAF observations; this crawler does NOT
prove that vendor-controlled bot IPs can pass a WAF.

Real citations: fixed query set, language/region, provider/model, collection time,
repeat count, and actual source URLs. Separate web-grounded citation runs from
ungrounded model knowledge. Paid provider requests need explicit authorization.
This release ships no automatic paid citation calls. Measurement adapters retained
from the workshop are mocks/context adapters, not live analytics connections.

Protected lessons, member projects, customer data and admin APIs never belong in
sitemap, llms.txt, discovery files, examples or public exports. Authenticated/private
analytics need separate scope. Use the host's available browser tools for rendered-page checks.

Fetcher scope: operator-side public audit, not an internet-facing proxy. DNS addresses
are checked before requests but not connection-pinned; do NOT expose this MCP to
untrusted users or rely on it as a complete DNS-rebinding/SSRF security boundary.
Browser-rendered/CWV/accessibility and schema-to-visible-text validation require
separate evidence. No auto-fix or deployment tool is included.
