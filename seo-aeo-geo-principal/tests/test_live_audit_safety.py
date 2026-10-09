import argparse
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from seo_audit_cli import cmd_audit
from seo_live_audit import (
    CrawlPolicy,
    FetchResult,
    audit,
    normalize_sitemap_urls,
)


def sitemap(*urls: str) -> str:
    items = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
    return f'<?xml version="1.0"?><urlset>{items}</urlset>'


def html(url: str, status: int = 200) -> FetchResult:
    return FetchResult(
        url=url,
        final_url=url,
        status=status,
        content_type="text/html; charset=utf-8",
        text="<html><head><title>Page</title></head><body><h1>Page</h1></body></html>",
    )


class LiveAuditSafetyTests(unittest.TestCase):
    def setUp(self):
        # Fake HTTP tests never depend on real DNS.
        check = patch('seo_live_audit.validate_url')
        check.start()
        self.addCleanup(check.stop)

    def test_public_targets_are_paced_and_local_targets_are_fast(self):
        self.assertEqual(CrawlPolicy.for_base("https://example.com").request_delay, 2.0)
        self.assertEqual(CrawlPolicy.for_base("http://127.0.0.1:8080").request_delay, 0.0)
        self.assertEqual(CrawlPolicy.for_base("http://localhost:8080").request_delay, 0.0)
        self.assertEqual(CrawlPolicy.for_base("http://[::1]:8080").request_delay, 0.0)

    def test_normalizes_scope_and_deduplicates_sitemap_urls(self):
        accepted, skipped = normalize_sitemap_urls(
            "https://example.com",
            [
                "https://example.com/a",
                "https://example.com/a",
                "https://other.test/b",
                "ftp://example.com/c",
            ],
        )

        self.assertEqual(accepted, ["https://example.com/a"])
        self.assertEqual(
            skipped,
            [
                {"url": "https://other.test/b", "reason": "external_hostname"},
                {"url": "ftp://example.com/c", "reason": "unsupported_scheme"},
            ],
        )

    def test_public_audit_sleeps_between_requests_but_not_before_first(self):
        base = "https://example.com"
        responses = {
            base + "/robots.txt": FetchResult(url=base + "/robots.txt", status=404),
            base + "/sitemap.xml": FetchResult(
                url=base + "/sitemap.xml",
                final_url=base + "/sitemap.xml",
                status=200,
                content_type="application/xml",
                text=sitemap(base + "/a", base + "/b"),
            ),
            base + "/a": html(base + "/a"),
            base + "/b": html(base + "/b"),
        }
        requested = []
        sleeps = []

        def fake_fetch(_session, url):
            requested.append(url)
            return responses[url]

        result = audit(
            base,
            ["/sitemap.xml"],
            policy=CrawlPolicy(request_delay=0.25),
            fetcher=fake_fetch,
            sleeper=sleeps.append,
        )

        self.assertEqual(requested, [base + "/robots.txt", base + "/sitemap.xml", base + "/a", base + "/b"])
        self.assertEqual(sleeps, [0.25, 0.25, 0.25])
        self.assertEqual(result["crawl_status"], "complete")
        self.assertEqual(result["request_count"], 4)

    def test_http_429_aborts_immediately_and_keeps_partial_evidence(self):
        base = "https://example.com"
        sitemap_url = base + "/sitemap.xml"
        page_urls = [base + f"/{name}" for name in ("a", "b", "c")]
        requested = []

        def fake_fetch(_session, url):
            requested.append(url)
            if url == base + "/robots.txt":
                return FetchResult(url=url, status=404)
            if url == sitemap_url:
                return FetchResult(
                    url=url,
                    final_url=url,
                    status=200,
                    content_type="application/xml",
                    text=sitemap(*page_urls),
                )
            return html(url, status=429)

        result = audit(
            base,
            ["/sitemap.xml"],
            policy=CrawlPolicy(request_delay=0),
            fetcher=fake_fetch,
            sleeper=lambda _: None,
        )

        self.assertEqual(requested, [base + "/robots.txt", sitemap_url, page_urls[0]])
        self.assertEqual(result["crawl_status"], "aborted")
        self.assertEqual(result["abort_reason"], "http_429")
        self.assertEqual(result["request_count"], 3)
        self.assertEqual(result["remaining_url_count"], 2)
        self.assertEqual(result["pages"][0]["status"], 429)

    def test_three_http_errors_abort_before_remaining_sitemap_urls(self):
        base = "https://example.com"
        sitemap_url = base + "/sitemap.xml"
        page_urls = [base + f"/{name}" for name in ("a", "b", "c", "d")]
        statuses = iter((404, 500, 404, 200))
        requested = []

        def fake_fetch(_session, url):
            requested.append(url)
            if url == base + "/robots.txt":
                return FetchResult(url=url, status=404)
            if url == sitemap_url:
                return FetchResult(
                    url=url,
                    final_url=url,
                    status=200,
                    content_type="application/xml",
                    text=sitemap(*page_urls),
                )
            return html(url, status=next(statuses))

        result = audit(
            base,
            ["/sitemap.xml"],
            policy=CrawlPolicy(request_delay=0, max_errors=3),
            fetcher=fake_fetch,
            sleeper=lambda _: None,
        )

        self.assertEqual(requested, [base + "/robots.txt", sitemap_url, *page_urls[:3]])
        self.assertEqual(result["crawl_status"], "aborted")
        self.assertEqual(result["abort_reason"], "error_limit")
        self.assertEqual(result["error_count"], 3)
        self.assertEqual(result["remaining_url_count"], 1)

    def test_cli_returns_two_after_writing_an_aborted_report(self):
        aborted = {
            "crawl_status": "aborted",
            "score": {"score": 0},
            "ok_html_count": 0,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "audit.json"
            args = argparse.Namespace(
                base="https://example.com",
                output=str(output),
                max_pages=None,
                discovery_path=["/sitemap.xml"],
                request_delay=None,
                max_errors=3,
            )
            with patch("seo_audit_cli.live_audit", return_value=aborted):
                status = cmd_audit(args)

            self.assertEqual(status, 2)
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
