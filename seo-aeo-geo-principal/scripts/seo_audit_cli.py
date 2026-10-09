#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from seo_scorecard import compute_scorecard
    from report_generator import write_report, render_markdown
    from seo_live_audit import CrawlPolicy, audit as live_audit
    from snapshots import compare, save_snapshot
except ImportError:  # pragma: no cover
    from scripts.seo_scorecard import compute_scorecard
    from scripts.report_generator import write_report, render_markdown
    from scripts.seo_live_audit import CrawlPolicy, audit as live_audit
    from scripts.snapshots import compare, save_snapshot


def cmd_audit(args: argparse.Namespace) -> int:
    discovery = args.discovery_path or ["/robots.txt", "/sitemap.xml", "/llms.txt"]
    policy = CrawlPolicy.for_base(args.base, request_delay=getattr(args, "request_delay", None),
        max_errors=getattr(args, "max_errors", 3), allow_local=getattr(args, "allow_local", False))
    result = live_audit(args.base, discovery, args.max_pages, policy=policy)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": args.output, "score": result["score"]["score"], "pages": result["ok_html_count"]}, ensure_ascii=False))
    return 0 if result.get("crawl_status", "complete") == "complete" else 2


def cmd_score(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    score = compute_scorecard(data)
    print(json.dumps(score, ensure_ascii=False, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    write_report(args.input, args.output, title=args.title)
    print(args.output)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    print(json.dumps(compare(before, after), ensure_ascii=False, indent=2))
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(json.dumps(save_snapshot(data, args.history_dir), ensure_ascii=False))
    return 0


def cmd_fixture_report(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    print(render_markdown(data, title=f"Fixture report: {Path(args.fixture).stem}", source=args.fixture))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SEO/AEO/GEO Principal+ CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("audit")
    p.add_argument("--base", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--max-pages", type=int, default=None)
    p.add_argument("--discovery-path", action="append", default=None)
    p.add_argument("--request-delay", type=float, default=None)
    p.add_argument("--max-errors", type=int, default=3)
    p.add_argument("--allow-local", action="store_true", help="Allow loopback preview only")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("score")
    p.add_argument("--input", required=True)
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("report")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--title", default="SEO/AEO/GEO audit")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("compare")
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("fixture-report")
    p.add_argument("--fixture", required=True)
    p.set_defaults(func=cmd_fixture_report)

    p = sub.add_parser("snapshot")
    p.add_argument("--input", required=True)
    p.add_argument("--history-dir", required=True)
    p.set_defaults(func=cmd_snapshot)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
