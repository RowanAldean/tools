"""Parallel Fast search and page extraction through the hosted Search MCP.

No key is needed for light use. PARALLEL_API_KEY enables higher limits.
Use one session_id per conversation and reuse it for related search and extract calls.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from datetime import timedelta
from typing import Any

from strands import tool
from strands.tools.mcp import MCPClient

_MCP_URL = "https://search.parallel.ai/mcp?mode=fast"
_TIMEOUT = timedelta(seconds=30)


def _call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    key = os.environ.get("PARALLEL_API_KEY")
    client = MCPClient(url=_MCP_URL, headers={"Authorization": f"Bearer {key}"} if key else None)
    try:
        client.start()
        result = client.call_tool_sync(tool_use_id=name, name=name, arguments=arguments, read_timeout_seconds=_TIMEOUT)
        if result.get("status") == "error" or result.get("isError"):
            raise RuntimeError("Parallel MCP returned an error")
        payload = result.get("structuredContent")
        if payload is None:
            payload = json.loads(
                "\n".join(c["text"] for c in result.get("content", []) if isinstance(c.get("text"), str))
            )
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise RuntimeError("Parallel MCP returned an invalid response")
        return payload
    finally:
        with contextlib.suppress(Exception):
            client.stop(None, None, None)


async def _invoke(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = await asyncio.to_thread(_call, name, arguments)
        return {"status": "success", "content": [{"text": json.dumps(payload)}]}
    except Exception:
        # Provider errors may include request metadata; return an actionable message without credentials.
        return {
            "status": "error",
            "content": [
                {
                    "text": (
                        "Parallel request failed. Check your connection and free-tier limits. "
                        "Set PARALLEL_API_KEY for higher limits, or check the key and account balance."
                    )
                }
            ],
        }


def _session_valid(session_id: str) -> bool:
    return bool(session_id.strip()) and len(session_id) <= 100


@tool
async def parallel_search(objective: str, search_queries: list[str], session_id: str) -> dict[str, Any]:
    """Search with Parallel Fast and return ranked URLs, titles and excerpts.

    Args:
        objective: One self-contained research goal, at most 5000 characters.
        search_queries: Exactly three diverse 3-6 word keyword queries, at most 200 characters each.
        session_id: Stable conversation ID, at most 100 characters. Reuse for related calls.
    """
    if not objective.strip() or len(objective) > 5000 or not _session_valid(session_id):
        return {"status": "error", "content": [{"text": "Provide a non-empty objective and stable session_id."}]}
    if len(search_queries) != 3 or any(not q.strip() or len(q) > 200 for q in search_queries):
        return {
            "status": "error",
            "content": [{"text": "Provide exactly three non-empty queries, at most 200 characters each."}],
        }
    return await _invoke(
        "web_search", {"objective": objective, "search_queries": search_queries, "session_id": session_id}
    )


@tool
async def parallel_extract(
    urls: list[str], session_id: str, full_content: bool = False, objective: str | None = None
) -> dict[str, Any]:
    """Extract page excerpts or full markdown from known public URLs.

    Args:
        urls: One to twenty HTTP or HTTPS URLs.
        session_id: Stable conversation ID, at most 100 characters. Reuse the conversation ID for related calls.
        full_content: Return full page markdown as well as excerpts when needed.
        objective: Optional extraction goal, at most 200 characters.
    """
    if (
        not _session_valid(session_id)
        or not 1 <= len(urls) <= 20
        or any(not url.startswith(("http://", "https://")) for url in urls)
    ):
        return {"status": "error", "content": [{"text": "Provide 1-20 HTTP(S) URLs and a stable session_id."}]}
    if objective is not None and len(objective) > 200:
        return {"status": "error", "content": [{"text": "objective must be at most 200 characters."}]}
    arguments: dict[str, Any] = {"urls": urls, "session_id": session_id, "full_content": full_content}
    if objective is not None:
        arguments["objective"] = objective
    return await _invoke("web_fetch", arguments)
