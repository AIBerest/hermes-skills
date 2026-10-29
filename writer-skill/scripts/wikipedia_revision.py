"""Stable Wikipedia revision monitor for the Sunday writer-skill review.

Only a revision change wakes the agent; content still needs editorial review.
"""
import re
import sys
from urllib.request import Request, urlopen

URL = "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing"
request = Request(URL, headers={"User-Agent": "WriterSkillMaintenance/0.1 (https://github.com/AIBerest/hermes-skills)"})
try:
    with urlopen(request, timeout=25) as response:
        page = response.read().decode("utf-8")
except Exception as exc:
    print(f"Wikipedia fetch failed: {type(exc).__name__}", file=sys.stderr)
    raise SystemExit(1)
revision = re.search(r'"wgRevisionId":(\d+)', page)
if not revision:
    print("Wikipedia revision ID missing; will not treat page as unchanged", file=sys.stderr)
    raise SystemExit(1)
print(f"Wikipedia:Signs_of_AI_writing revision={revision.group(1)}")
