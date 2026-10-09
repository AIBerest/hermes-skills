"""Local explicit snapshot history; never imports operator data or credentials."""
from __future__ import annotations
import json
import hashlib
from pathlib import Path
from urllib.parse import urlsplit
try:
    from seo_scorecard import compute_scorecard
except ImportError:
    from scripts.seo_scorecard import compute_scorecard


def compare(before: dict, after: dict) -> dict:
    if before.get('base') and after.get('base') and before['base'].rstrip('/') != after['base'].rstrip('/'):
        raise ValueError('Comparison requires the same site origin')
    bs = compute_scorecard(before); ass = compute_scorecard(after)
    old = {r['criterion']: r for r in bs['scorecard']}
    warnings = []
    before_urls = {p.get('url') for p in before.get('pages', []) if p.get('url')}
    after_urls = {p.get('url') for p in after.get('pages', []) if p.get('url')}
    if before_urls != after_urls:
        warnings.append('Different page samples; dimension deltas do not isolate the effect of fixes')
    if any(x.get('crawl_status', 'complete') != 'complete' for x in (before, after)):
        warnings.append('At least one crawl is partial/aborted; resolve coverage gaps before drawing conclusions')
    changes = [{'criterion': r['criterion'], 'before': old[r['criterion']]['score'], 'after': r['score'], 'delta': r['score'] - old[r['criterion']]['score'], 'evidence': r['evidence']} for r in ass['scorecard']]
    return {'before': bs['score'], 'after': ass['score'], 'delta': ass['score'] - bs['score'], 'regressions': [r for r in changes if r['delta'] < 0], 'changes': changes, 'model_version': ass['model_version'], 'comparison_warnings': warnings, 'metric': 'advisory_readiness_not_search_visibility', 'coverage_before': before.get('coverage'), 'coverage_after': after.get('coverage')}


def save_snapshot(data: dict, directory: str) -> dict:
    base = data.get('base', '')
    if not urlsplit(base).hostname or not data.get('fetched_at'):
        raise ValueError('Snapshot needs a site origin and collection time')
    # Incoming snapshots are explicit audit files, not arbitrary provider state.
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    folder = Path(directory) / hashlib.sha256(base.rstrip('/').encode()).hexdigest()[:16]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (digest[:16] + '.json')
    path.write_bytes(encoded); path.chmod(0o600)
    return {'snapshot': str(path), 'sha256': digest, 'base': base, 'fetched_at': data['fetched_at']}
