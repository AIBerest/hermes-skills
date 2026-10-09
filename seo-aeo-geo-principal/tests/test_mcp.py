"""Actual stdio initialize/list/call, skipped only when optional MCP is absent."""
import asyncio
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(importlib.util.find_spec('mcp'), 'optional MCP dependency not installed')
class MCPTests(unittest.TestCase):
    def test_real_stdio_tools_and_score(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        async def run():
            params = StdioServerParameters(command=sys.executable, args=[str(ROOT/'scripts/mcp_server.py')])
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    self.assertEqual({t.name for t in tools.tools}, {'seo_audit','seo_score','seo_compare'})
                    data=json.loads((ROOT/'fixtures/clean-site.json').read_text())
                    result=await session.call_tool('seo_score', {'audit_json':data})
                    self.assertFalse(result.isError)
                    content=json.loads(result.content[0].text)
                    self.assertGreater(content['score'],80)
                    self.assertEqual(content['metric'],'advisory_readiness_not_search_visibility')
                    bad=await session.call_tool('seo_audit', {'base_url':'http://127.0.0.1','max_pages':1})
                    self.assertTrue(bad.isError)
        asyncio.run(run())
