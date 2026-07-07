# Human20 SEO/AEO/GEO SuperGoal planning

Use when Chip asks for SEO, AEO, GEO, AI-search readiness, citation readiness, or a SuperGoal for `human20.app` discoverability.

## Class-level workflow

1. Treat the task as a live readiness audit, not a generic SEO explainer or post draft, unless Chip explicitly asks for copy.
2. Load `project/human20-app`, `project/human20-prod-verification`, `chip-url-first`, and this SuperGoal skill. Use `telegram-chip` for Telegram source links.
3. Start with public evidence from `https://human20.app`:
   - `/`, `/about`, `/faq`, `/articles`, representative article, `/skills`, `/lessons`, `/agent`, `/launch`, `/sitemap.xml`, `/robots.txt`, `/release.json`.
   - Extract title, description, canonical, H1/H2, OG image, JSON-LD types, sitemap count, private-path leakage, and route weight flags.
4. Score separately:
   - classic SEO: metadata, sitemap, crawlability, canonicals, structured data, page hygiene;
   - AEO: direct answers, FAQ blocks, question headings, snippet-friendly definitions;
   - GEO: entity pages, author/person/org graph, evergreen knowledge pages, comparisons, original evidence, external mention strategy.
5. If Chip provides a Telegram source for author bio/profile facts, fetch the exact message first. If it is `MessageMediaUnsupported`, public embed only says “open Telegram”, or media download fails, mark a source-lock. Do **not** invent bio facts from an inaccessible post. Use public-safe profile facts only with provenance in internal reports.
6. For a SuperGoal package, include phases for:
   - source-lock + baseline audit;
   - deterministic SEO/AEO audit tooling;
   - entity/schema foundation;
   - homepage/about AEO pass;
   - `/knowledge/*` pillar pages;
   - comparison/use-case pages;
   - article/skills/agent hardening;
   - discovery surfaces: sitemap, robots, llms.txt, IndexNow if safe;
   - local lint/test/build/audit;
   - fresh `origin/prod` merge, canonical RF deploy, live smoke.
7. Preserve Human20 copy rules:
   - visible RU site copy says `Человек 2.0`, not `Human20`, except technical identifiers;
   - exact branded phrase `Среда внедрения ИИ`;
   - keep existing hero/features unless explicit.
8. Production deploys must use the RF SEO/AEO deploy reference: clean fresh `origin/prod` worktree, 3-way merge, preserve prod-only fixes, run local gates, deploy with `scripts/deploy_prod_rf.sh origin/prod`, then verify `/release.json` SHA and live routes.

## Output shape for Chip

Lead with a short scorecard, then evidence:

```text
SEO: x/10
AEO: x/10
GEO: x/10

➊ что уже готово
➋ что мешает
➌ что делать первым
```

For SuperGoals, explicitly state that the planner wrote files and did not yet change/deploy the site.