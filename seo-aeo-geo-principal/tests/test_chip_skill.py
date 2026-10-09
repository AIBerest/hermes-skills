import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.fetch_safety import validate_url, MAX_BYTES
from scripts.seo_live_audit import audit, FetchResult, analyze_html, fetch, sitemap_urls_from_text
from scripts.seo_scorecard import compute_scorecard
from scripts.snapshots import compare, save_snapshot
from scripts.validate_skill import validate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DNS = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))]

class ChipTests(unittest.TestCase):
    def test_private_addresses_rejected(self):
        for url in ['http://127.0.0.1', 'http://169.254.169.254', 'http://[::1]', 'http://10.0.0.1']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_loopback_explicit_opt_in_only(self):
        self.assertEqual(validate_url('http://127.0.0.1:3000/', allow_local=True), 'http://127.0.0.1:3000/')
        with self.assertRaises(ValueError):
            validate_url('http://10.0.0.1/', allow_local=True)

    def test_content_excludes_navigation_links(self):
        html = '<nav><a href="https://other.example">Menu</a></nav><main><h2>Why?</h2><p>Answer</p><a href="https://source.example">Source</a></main>'
        page = analyze_html(FetchResult(url='https://example.com/', status=200, content_type='text/html', text=html), 'example.com')
        self.assertEqual(page['extractability']['external_source_links'], 1)

    def test_optional_endpoints_do_not_change_score(self):
        data = json.loads((ROOT/'fixtures/clean-site.json').read_text())
        original = compute_scorecard(data)['score']
        data.setdefault('discovery', {})['/llms.txt'] = {'status': 404}
        self.assertEqual(compute_scorecard(data)['score'], original)

    def test_compare_warns_on_partial_different_samples(self):
        before = json.loads((ROOT/'fixtures/clean-site.json').read_text())
        after = dict(before, pages=[], crawl_status='aborted')
        self.assertEqual(len(compare(before, after)['comparison_warnings']), 2)

    @patch('scripts.seo_live_audit.validate_url')
    @patch('scripts.seo_live_audit.fetch')
    def test_nested_sitemap_pages_are_bounded_and_paced(self, get, _):
        def fixture(session, url, **kwargs):
            if url.endswith('robots.txt'):
                return FetchResult(url=url, status=200, text='User-agent: *\nAllow: /')
            if url.endswith('sitemap.xml'):
                return FetchResult(url=url, status=200, text='<sitemapindex><sitemap><loc>https://example.com/child.xml</loc></sitemap></sitemapindex>')
            if url.endswith('child.xml'):
                return FetchResult(url=url, status=200, text='<urlset><url><loc>https://example.com/a</loc></url><url><loc>https://example.com/b</loc></url></urlset>')
            return FetchResult(url=url, status=200, content_type='text/html', text='<h1>Article</h1><p>Answer</p>')
        get.side_effect = fixture
        sleeps = []
        result = audit('https://example.com', ['/sitemap.xml'], 1, sleeper=sleeps.append)
        self.assertEqual(result['ok_html_count'], 1)
        self.assertEqual(result['pages'][0]['url'], 'https://example.com/a')
        self.assertEqual(sleeps, [2.0, 2.0, 2.0])
        self.assertFalse(result['coverage']['complete_site_crawl'])

    @patch('scripts.seo_live_audit.validate_url')
    @patch('scripts.seo_live_audit.fetch')
    def test_nested_sitemaps_share_stop_policy(self, get, _):
        def fixture(session, url, **kwargs):
            if url.endswith('robots.txt'):
                return FetchResult(url=url, status=404, text='')
            if url.endswith('sitemap.xml'):
                return FetchResult(url=url, status=200, text='<sitemapindex><sitemap><loc>https://example.com/child.xml</loc></sitemap></sitemapindex>')
            return FetchResult(url=url, status=429, text='')
        get.side_effect = fixture
        result = audit('https://example.com', ['/robots.txt', '/sitemap.xml'], 5, sleeper=lambda _: None)
        self.assertEqual(result['crawl_status'], 'aborted')
        self.assertEqual(result['request_count'], 3)
        self.assertEqual(result['ok_html_count'], 0)

    def test_url_scope(self):
        for url in ['file:///secret', 'https://u:p@example.com', 'https://example.com/admin', 'https://example.com/?token=x', 'https://example.com/#x']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    @patch('scripts.fetch_safety.socket.getaddrinfo', return_value=PUBLIC_DNS)
    def test_public_same_origin(self, _):
        self.assertEqual(validate_url('https://example.com/a', 'https://example.com'), 'https://example.com/a')
        with self.assertRaises(ValueError):
            validate_url('https://other.example/a', 'https://example.com')

    @patch('scripts.fetch_safety.socket.getaddrinfo', return_value=[(2, 1, 6, '', ('10.0.0.1', 443))])
    def test_private_dns_rejected(self, _):
        with self.assertRaises(ValueError):
            validate_url('https://example.com')

    def test_sitemap_entities_and_xml(self):
        self.assertEqual(sitemap_urls_from_text('<!DOCTYPE urlset><urlset/>'), [])
        self.assertEqual(sitemap_urls_from_text('<urlset><url><loc>https://example.com/a</loc></url></urlset>'), ['https://example.com/a'])
        self.assertEqual(sitemap_urls_from_text('not xml'), [])

    def test_empty_audit_not_green(self):
        result = compute_scorecard({})
        self.assertEqual(result['score'], 0)
        self.assertTrue(all(r['confidence'] == 'low' for r in result['scorecard']))

    def test_hidden_text_and_http_noindex(self):
        page = analyze_html(FetchResult(url='https://example.com', status=200, content_type='text/html', text='<h1>Title</h1><nav>menu</nav><p hidden>hidden</p><h2>How?</h2><p>Answer.</p>', headers={'x-robots-tag':'noindex'}), 'example.com')
        self.assertIn('noindex', page['robots_meta'])
        self.assertEqual(page['extractability']['answer_sections'], 1)
        self.assertLess(page['text_chars'], 30)

    def test_contract_and_negative(self):
        self.assertEqual(validate(ROOT), [])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'SKILL.md').write_text('---\nname: wrong-name\ndescription: Example\n---\n')
            self.assertIn('frontmatter/name', validate(root))

    def test_snapshot_explicit_and_hashed(self):
        data={'base':'https://example.com','fetched_at':'2026-01-01T00:00:00Z','ok_html_count':1}
        with tempfile.TemporaryDirectory() as directory:
            result=save_snapshot(data,directory)
            self.assertTrue(Path(result['snapshot']).is_file())
            self.assertEqual(len(result['sha256']),64)
            self.assertEqual(Path(result['snapshot']).stat().st_mode & 0o777,0o600)

    def test_compare_regressions_ignore_stale_score(self):
        before=json.loads((ROOT/'fixtures/clean-site.json').read_text())
        after=json.loads((ROOT/'fixtures/schema-missing-site.json').read_text())
        after['score']={'score':100}
        result=compare(before,after)
        self.assertLess(result['delta'],0)
        self.assertTrue(result['regressions'])
        self.assertIn('not_search_visibility',result['metric'])

    def test_compare_different_origins_blocked(self):
        with self.assertRaises(ValueError):
            compare({'base':'https://example.com'},{'base':'https://other.example'})

    def test_max_budget_rejected(self):
        with patch('scripts.seo_live_audit.validate_url'), self.assertRaises(ValueError):
            audit('https://example.com',[],101)

    @patch('scripts.seo_live_audit.validate_url')
    def test_redirect_private_never_requested(self, check):
        check.side_effect=[None,ValueError('private')]
        session=MagicMock(); response=session.get.return_value.__enter__.return_value
        response.status_code=302; response.headers={'location':'http://127.0.0.1/'}
        result=fetch(session,'https://example.com',origin='https://example.com')
        self.assertEqual(result.error,'ValueError')
        self.assertEqual(session.get.call_count,1)

    @patch('scripts.seo_live_audit.validate_url')
    def test_response_bound(self, _):
        session=MagicMock(); response=session.get.return_value.__enter__.return_value
        response.status_code=200; response.headers={'content-type':'text/html'}
        response.iter_content.return_value=[b'x'*(MAX_BYTES+1)]
        self.assertEqual(fetch(session,'https://example.com').error,'ValueError')

    @patch('scripts.seo_live_audit.validate_url')
    @patch('scripts.seo_live_audit.fetch')
    def test_missing_sitemap_falls_back_to_home(self, get, _):
        def fixture(session,url,**kwargs):
            if url.endswith('/'):
                return FetchResult(url=url,status=200,content_type='text/html',text='<h1>Home</h1>')
            return FetchResult(url=url,status=404,content_type='text/html',text='<h1>Not found</h1>')
        get.side_effect=fixture
        result=audit('https://example.com',['/robots.txt','/sitemap.xml'],5, sleeper=lambda _: None)
        self.assertEqual(result['ok_html_count'],1)
        self.assertEqual(result['pages'][0]['url'],'https://example.com/')

    @patch('scripts.seo_live_audit.validate_url')
    @patch('scripts.seo_live_audit.fetch')
    def test_robots_and_no_raw_discovery(self, get, _):
        def fixture(session,url,**kwargs):
            text='User-agent: *\nDisallow: /blocked' if url.endswith('robots.txt') else '<urlset><url><loc>https://example.com/blocked</loc></url></urlset>'
            return FetchResult(url=url,status=200,content_type='text/plain',text=text,headers={})
        get.side_effect=fixture
        result=audit('https://example.com',['/robots.txt','/sitemap.xml'],5, sleeper=lambda _: None)
        self.assertEqual(result['ok_html_count'],0)
        self.assertEqual(result['score']['score'],0)
        self.assertFalse(result['coverage']['complete_site_crawl'])
        self.assertTrue(all('text' not in x for x in result['discovery'].values()))
        self.assertEqual(result['crawler_access']['ClaudeBot']['purpose'],'training')
        self.assertEqual(result['crawler_access']['Google-Extended']['purpose'],'training_policy')
        self.assertIn({'reason':'robots_disallowed'},result['skipped'])

if __name__ == '__main__': unittest.main()
