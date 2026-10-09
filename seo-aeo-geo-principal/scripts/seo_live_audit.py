#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from html import unescape
from typing import Any, Callable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    from seo_scorecard import compute_scorecard
    from fetch_safety import validate_url, MAX_BYTES, MAX_REDIRECTS
except ImportError:
    from scripts.seo_scorecard import compute_scorecard
    from scripts.fetch_safety import validate_url, MAX_BYTES, MAX_REDIRECTS
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET


@dataclass
class FetchResult:
    url: str
    final_url: str | None = None
    status: int | None = None
    content_type: str = ""
    bytes_len: int = 0
    text: str = ""
    error: str | None = None
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class CrawlPolicy:
    request_delay: float = 2.0
    max_errors: int = 3
    stop_statuses: tuple[int, ...] = (403, 429)
    allow_local: bool = False

    @classmethod
    def for_base(cls, base: str, *, request_delay: float | None = None,
                 max_errors: int = 3, allow_local: bool = False) -> "CrawlPolicy":
        local = (urlparse(base).hostname or "").lower() in {"localhost", "127.0.0.1", "::1"}
        delay = 0.0 if local else 2.0
        return cls(request_delay=delay if request_delay is None else max(0.0, request_delay),
                   max_errors=max(1, max_errors), allow_local=allow_local)


def fetch(session: requests.Session, url: str, timeout: int = 15, origin: str | None = None,
          *, allow_local: bool = False) -> FetchResult:
    current = url
    try:
        for _ in range(MAX_REDIRECTS + 1):
            validate_url(current, origin, allow_local=allow_local)
            session.cookies.clear()
            with session.get(current, timeout=timeout, allow_redirects=False, stream=True) as r:
                if 300 <= r.status_code < 400 and r.headers.get('location'):
                    current = urljoin(current, r.headers['location'])
                    continue
                data = bytearray()
                for chunk in r.iter_content(16384):
                    data.extend(chunk)
                    if len(data) > MAX_BYTES:
                        raise ValueError('Response size limit exceeded')
                ctype = r.headers.get('content-type', '')
                text = bytes(data).decode('utf-8', errors='replace') if any(x in ctype for x in ('text', 'html', 'xml', 'json')) else ''
                headers = {k.lower(): v for k, v in r.headers.items() if k.lower() in ('content-type', 'x-robots-tag', 'last-modified')}
                return FetchResult(url=url, final_url=current, status=r.status_code, content_type=ctype, bytes_len=len(data), text=text, headers=headers)
        raise ValueError('Redirect limit exceeded')
    except Exception as exc:
        # Exception text may contain signed URLs or provider headers; export only its class.
        return FetchResult(url=url, error=type(exc).__name__, headers={})


def jsonld_types(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        typ = value.get("@type")
        if isinstance(typ, str):
            out.append(typ)
        elif isinstance(typ, list):
            out.extend(str(x) for x in typ)
        for v in value.values():
            out.extend(jsonld_types(v))
    elif isinstance(value, list):
        for item in value:
            out.extend(jsonld_types(item))
    return out


def norm_attr(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value or "")


def is_meaningful_img_missing_alt(img: Any) -> bool:
    aria_hidden = norm_attr(img.get("aria-hidden")).strip().lower()
    role = norm_attr(img.get("role")).strip().lower()
    alt = norm_attr(img.get("alt")).strip()
    if aria_hidden == "true" or role in {"presentation", "none"}:
        return False
    return not alt


def analyze_html(item: FetchResult, public_netloc: str) -> dict[str, Any]:
    if item.status != 200 or "text/html" not in item.content_type:
        return {
            "url": item.url,
            "final_url": item.final_url,
            "status": item.status,
            "content_type": item.content_type,
            "bytes": item.bytes_len,
            "error": item.error,
        }

    soup = BeautifulSoup(item.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    for tag in soup.select('[hidden], [aria-hidden="true"]'):
        if tag.parent is not None:
            tag.decompose()
    content = BeautifulSoup(str(soup), "html.parser")
    for tag in content.select('nav, footer, [role="navigation"]'):
        if tag.parent is not None:
            tag.decompose()

    # Re-parse scripts from original HTML for JSON-LD because we removed scripts above for text extraction.
    soup_scripts = BeautifulSoup(item.text, "html.parser")
    jsonld: list[dict[str, Any]] = []
    for script in soup_scripts.find_all("script", type="application/ld+json"):
        raw = script.get_text(strip=True)
        try:
            parsed = json.loads(raw)
            jsonld.append({"types": jsonld_types(parsed), "chars": len(raw), "ok": True})
        except Exception as exc:
            jsonld.append({"ok": False, "error": type(exc).__name__, "chars": len(raw)})

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    canonical_tag = soup.find("link", rel="canonical")
    robots_meta = soup.find("meta", attrs={"name": re.compile("robots", re.I)})
    h1 = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
    h2 = [h.get_text(" ", strip=True) for h in soup.find_all("h2")]
    imgs = soup.find_all("img")

    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(item.final_url or item.url, norm_attr(a.get("href"))).split("#")[0]
        if urlparse(href).netloc == public_netloc:
            links.append(href)

    og = {}
    for meta in BeautifulSoup(item.text, "html.parser").find_all("meta"):
        key = norm_attr(meta.get("property") or meta.get("name"))
        if key.startswith("og:") or key.startswith("twitter:"):
            og[key] = norm_attr(meta.get("content"))

    text = unescape(content.get_text(" ", strip=True))
    meaningful_missing = []
    for img in imgs:
        if is_meaningful_img_missing_alt(img):
            meaningful_missing.append({
                "src": norm_attr(img.get("src"))[:220],
                "class": norm_attr(img.get("class"))[:160],
            })

    return {
        "url": item.url,
        "final_url": item.final_url,
        "status": item.status,
        "content_type": item.content_type,
        "bytes": item.bytes_len,
        "title": title,
        "title_len": len(title),
        "description": norm_attr(desc_tag.get("content")) if desc_tag else "",
        "description_len": len(norm_attr(desc_tag.get("content"))) if desc_tag else 0,
        "canonical": norm_attr(canonical_tag.get("href")) if canonical_tag else "",
        "robots_meta": (norm_attr(robots_meta.get("content")) if robots_meta else "") + ' ' + (item.headers or {}).get('x-robots-tag', ''),
        "extractability": {
            "method": "html_structure_heuristics_not_citation_measurement",
            "answer_sections": sum(1 for h in content.find_all(['h2', 'h3'])
                                   if '?' in h.get_text() and h.find_next_sibling(['p', 'ul', 'ol'])),
            "external_source_links": sum(1 for a in content.find_all('a', href=True)
                if urlparse(urljoin(item.url, norm_attr(a.get('href')))).scheme in ('http', 'https')
                and urlparse(urljoin(item.url, norm_attr(a.get('href')))).netloc != public_netloc),
            "paragraphs": len(content.find_all('p')),
            "lists": len(content.find_all(['ul', 'ol'])),
            "dated_elements": len(content.find_all('time')),
        },
        "h1": h1,
        "h1_count": len(h1),
        "h2_sample": h2[:10],
        "jsonld": jsonld,
        "jsonld_types": sorted({t for block in jsonld for t in block.get("types", [])}),
        "jsonld_count": len(jsonld),
        "jsonld_parse_errors": [b for b in jsonld if not b.get("ok")],
        "og": og,
        "og_count": len(og),
        "img_count": len(imgs),
        "img_without_alt_raw": sum(1 for img in imgs if not norm_attr(img.get("alt")).strip()),
        "meaningful_img_without_alt": len(meaningful_missing),
        "meaningful_img_without_alt_items": meaningful_missing,
        "text_chars": len(text),
        "internal_links_unique": len(set(links)),
        "question_mark_count": text.count("?"),
    }


def sitemap_urls_from_text(text: str) -> list[str]:
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        return []
    try:
        root = ET.fromstring(text)
        return [node.text.strip() for node in root.iter() if node.tag.split('}')[-1] == 'loc' and node.text]
    except ET.ParseError:
        return []


def normalize_sitemap_urls(base: str, urls: list[str]) -> tuple[list[str], list[dict[str, str]]]:
    """Normalize candidate scope; actual network/DNS checks happen at fetch time."""
    parsed_base = urlparse(base)
    accepted, skipped, seen = [], [], set()
    for raw in urls:
        url = unescape(str(raw).strip())
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            skipped.append({"url": url, "reason": "unsupported_scheme"})
        elif (parsed.scheme, parsed.hostname, parsed.port) != (parsed_base.scheme, parsed_base.hostname, parsed_base.port):
            skipped.append({"url": url, "reason": "external_hostname"})
        elif url not in seen:
            seen.add(url)
            accepted.append(url)
    return accepted, skipped


def collect_sitemap_urls(session: requests.Session, base: str, first: str, limit: int,
                         *, fetcher=None, stopped=lambda: False, allow_local=False,
                         extra_sitemaps=None, allowed=lambda url: True) -> tuple[list[str], list[dict]]:
    getter = fetcher or (lambda url: fetch(session, url, origin=base, allow_local=allow_local))
    queue = [(base + "/sitemap.xml", first)] if first else []
    seen, scheduled, urls, skipped = set(), {url for url, _ in queue}, [], []
    for url in extra_sitemaps or []:
        try:
            validate_url(url, base, allow_local=allow_local)
        except (ValueError, OSError):
            skipped.append({"reason": "outside_public_scope"})
            continue
        if url not in scheduled and len(scheduled) < 10 and not stopped():
            scheduled.add(url)
            item = getter(url)
            if item.status == 200:
                queue.append((url, item.text))
    while queue and len(seen) < 10 and len(urls) < limit and not stopped():
        sitemap_url, text = queue.pop(0)
        if sitemap_url in seen:
            continue
        seen.add(sitemap_url)
        try:
            root = ET.fromstring(text) if "<!DOCTYPE" not in text.upper() and "<!ENTITY" not in text.upper() else None
        except ET.ParseError:
            root = None
        if root is None:
            skipped.append({"reason": "invalid_sitemap"})
            continue
        is_index = root.tag.split("}")[-1] == "sitemapindex"
        for url in sitemap_urls_from_text(text)[:1000]:
            if stopped():
                break
            try:
                validate_url(url, base, allow_local=allow_local)
            except (ValueError, OSError):
                skipped.append({"reason": "outside_public_scope"})
                continue
            if is_index:
                if url in scheduled:
                    continue
                if len(scheduled) >= 10:
                    skipped.append({"reason": "sitemap_budget"})
                    continue
                scheduled.add(url)
                if not allowed(url):
                    skipped.append({"reason": "robots_disallowed"})
                    continue
                item = getter(url)
                if item.status == 200:
                    queue.append((url, item.text))
            elif url not in urls:
                urls.append(url)
                if len(urls) >= limit:
                    break
    return urls, skipped


def audit(base: str, discovery_paths: list[str], max_pages: int | None = 20, *,
          policy: CrawlPolicy | None = None, fetcher: Callable | None = None,
          sleeper: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    crawl_policy = policy or CrawlPolicy.for_base(base)
    validate_url(base, allow_local=crawl_policy.allow_local)
    limit = 20 if max_pages is None else max_pages
    if not 1 <= limit <= 100:
        raise ValueError("max_pages must be between 1 and 100")
    base = base.rstrip("/")
    parsed = urlparse(base)
    if parsed.path:
        raise ValueError("base must be a site origin, without path")
    public_netloc = parsed.netloc
    session = requests.Session()
    session.trust_env = False
    session.headers.update({"User-Agent": "SEOAEOAudit/2.1 (polite; sequential)"})
    request_count, error_count = 0, 0
    crawl_status, abort_reason = "complete", None
    cache = {}
    paths = list(dict.fromkeys(["/robots.txt", *discovery_paths]))
    if len(paths) > 20:
        raise ValueError("At most 20 discovery paths")
    optional_urls = {base + path for path in paths}

    def stopped():
        return crawl_status == "aborted"

    def paced_fetch(url):
        nonlocal request_count, error_count, crawl_status, abort_reason
        if url in cache:
            return cache[url]
        if stopped():
            return FetchResult(url=url, error="crawl_aborted", headers={})
        if request_count and crawl_policy.request_delay:
            sleeper(crawl_policy.request_delay)
        request_count += 1
        item = fetcher(session, url) if fetcher else fetch(session, url, origin=base, allow_local=crawl_policy.allow_local)
        cache[url] = item
        if item.status in crawl_policy.stop_statuses:
            error_count += 1
            crawl_status, abort_reason = "aborted", f"http_{item.status}"
        elif item.status is None or (item.status >= 400 and not (item.status == 404 and url in optional_urls)):
            error_count += 1
            if error_count >= crawl_policy.max_errors:
                crawl_status, abort_reason = "aborted", "error_limit"
        return item

    robots_item = paced_fetch(base + "/robots.txt")
    robots = RobotFileParser()
    robots.parse((robots_item.text or "").splitlines() if robots_item.status == 200 else [])
    def allowed(url):
        return robots_item.status == 404 or (robots_item.status == 200 and robots.can_fetch("SEOAEOAudit", url))

    discovery = {base + "/robots.txt": asdict(robots_item)}
    skipped = []
    if robots_item.status not in (200, 404):
        skipped.append({"reason": "robots_unavailable"})
    else:
        for path in paths:
            if stopped():
                break
            url = base + path
            if path != "/robots.txt" and not allowed(url):
                skipped.append({"reason": "robots_disallowed"})
                continue
            discovery[url] = asdict(paced_fetch(url))
    sitemap_item = discovery.get(base + "/sitemap.xml", {})
    sitemap_text = sitemap_item.get("text", "") if sitemap_item.get("status") == 200 else ""
    sitemap_urls = []
    if robots_item.status in (200, 404) and not stopped():
        extra = [url for url in (robots.site_maps() or []) if allowed(url)] if robots_item.status == 200 else []
        sitemap_urls, sitemap_skipped = collect_sitemap_urls(
            session, base, sitemap_text, limit, fetcher=paced_fetch, stopped=stopped,
            allow_local=crawl_policy.allow_local, extra_sitemaps=extra, allowed=allowed)
        skipped.extend(sitemap_skipped)
    bots = {"OAI-SearchBot": "search", "GPTBot": "training", "ChatGPT-User": "user_fetch",
            "Claude-SearchBot": "search", "ClaudeBot": "training", "Claude-User": "user_fetch",
            "PerplexityBot": "search", "Googlebot": "search", "Google-Extended": "training_policy"}
    crawler_access = {bot: {"purpose": purpose,
        "robots_allowed": robots.can_fetch(bot, base + "/") if robots_item.status == 200 else (True if robots_item.status == 404 else None),
        "observed_url": base + "/", "waf_access": "unmeasured"} for bot, purpose in bots.items()}
    crawler_access["ChatGPT-User"]["policy_note"] = "User-initiated requests: robots.txt may not apply; not a search inclusion control"
    crawl_urls = []
    for url in sitemap_urls:
        if allowed(url):
            crawl_urls.append(url)
        else:
            skipped.append({"reason": "robots_disallowed"})
    if not sitemap_urls and allowed(base + "/") and not stopped():
        crawl_urls = [base + "/"]
    pages = []
    for url in crawl_urls:
        if stopped():
            break
        pages.append(analyze_html(paced_fetch(url), public_netloc))
    for item in discovery.values():
        item.pop("text", None)
    ok_html = [p for p in pages if p.get("status") == 200 and "text/html" in p.get("content_type", "")]

    missing_jsonld = [p["url"] for p in ok_html if p.get("jsonld_count", 0) == 0]
    thin_pages = [{"url": p["url"], "text_chars": p.get("text_chars", 0)} for p in ok_html if p.get("text_chars", 0) < 1500]
    raw_alt_debt = [{"url": p["url"], "img_count": p.get("img_count", 0), "img_without_alt_raw": p.get("img_without_alt_raw", 0)} for p in ok_html if p.get("img_without_alt_raw", 0) > 0]
    meaningful_alt_debt = [{"url": p["url"], "items": p.get("meaningful_img_without_alt_items", [])} for p in ok_html if p.get("meaningful_img_without_alt", 0) > 0]

    result: dict[str, Any] = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base": base,
        "schema_version": "2.1",
        "crawl_status": crawl_status if ok_html or stopped() else "partial",
        "abort_reason": abort_reason,
        "request_count": request_count,
        "request_delay": crawl_policy.request_delay,
        "error_count": error_count,
        "remaining_url_count": max(0, len(crawl_urls) - len(pages)),
        "coverage": {"mode": "local_preview_sample" if crawl_policy.allow_local else "bounded_public_sample", "max_pages": limit, "selected_pages": len(crawl_urls), "fetched_pages": len(pages), "successful_html_pages": len(ok_html), "limit_reached": len(sitemap_urls) >= limit, "skipped_count": len(skipped), "complete_site_crawl": False},
        "skipped": skipped,
        "crawler_access": crawler_access,
        "sitemap_url_count": len(sitemap_urls),
        "ok_html_count": len(ok_html),
        "non_200": [p for p in pages if p.get("status") != 200],
        "missing_title": [p["url"] for p in ok_html if not p.get("title")],
        "missing_description": [p["url"] for p in ok_html if not p.get("description")],
        "missing_canonical": [p["url"] for p in ok_html if not p.get("canonical")],
        "bad_h1": [{"url": p["url"], "h1_count": p.get("h1_count"), "h1": p.get("h1")} for p in ok_html if p.get("h1_count") != 1],
        "noindex": [p["url"] for p in ok_html if "noindex" in str(p.get("robots_meta", "")).lower()],
        "missing_jsonld": missing_jsonld,
        "thin_pages_under_1500": thin_pages,
        "img_alt_debt_raw": raw_alt_debt,
        "meaningful_image_alt_debt": meaningful_alt_debt,
        "text_chars_median": statistics.median([p.get("text_chars", 0) for p in ok_html]) if ok_html else 0,
        "html_bytes_median": statistics.median([p.get("bytes", 0) for p in ok_html]) if ok_html else 0,
        "pages": pages,
        "discovery": discovery,
    }
    result["score"] = compute_scorecard(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Live SEO/AEO/GEO audit crawler")
    parser.add_argument("--base", required=True, help="Base URL, e.g. https://example.com")
    parser.add_argument("--output", required=True, help="Path to write JSON audit")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit sitemap crawl for smoke tests")
    parser.add_argument("--summary", action="store_true", help="Print compact summary")
    parser.add_argument("--discovery-path", action="append", default=None, help="Extra or replacement discovery path; repeatable. Defaults cover common SEO/GEO endpoints")
    parser.add_argument("--request-delay", type=float, default=None)
    parser.add_argument("--max-errors", type=int, default=3)
    parser.add_argument("--allow-local", action="store_true", help="Explicitly allow loopback preview; private LANs remain excluded")
    args = parser.parse_args()

    discovery_paths = args.discovery_path or [
        "/robots.txt",
        "/sitemap.xml",
        "/llms.txt",
    ]
    policy = CrawlPolicy.for_base(args.base, request_delay=args.request_delay,
                                  max_errors=args.max_errors, allow_local=args.allow_local)
    result = audit(args.base, discovery_paths, args.max_pages, policy=policy)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if args.summary:
        summary = {
            "fetched_at": result["fetched_at"],
            "base": result["base"],
            "score": result["score"]["score"],
            "sitemap_url_count": result["sitemap_url_count"],
            "ok_html_count": result["ok_html_count"],
            "non_200": len(result["non_200"]),
            "missing_jsonld": len(result["missing_jsonld"]),
            "thin_pages_under_1500": len(result["thin_pages_under_1500"]),
            "meaningful_image_alt_debt_pages": len(result["meaningful_image_alt_debt"]),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(args.output)
    return 0 if result["crawl_status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
