import asyncio
import json
from unittest.mock import patch

from strands_tools import parallel

QUERIES = ["Strands Agents SDK documentation", "Strands harness quickstart guide", "Strands SDK official tools"]


def test_search_maps_intent_and_queries():
    with patch.object(parallel, "_invoke", return_value={"status": "success"}) as invoke:
        assert asyncio.run(parallel.parallel_search("Find official docs", QUERIES, "session-one")) == {
            "status": "success"
        }
    invoke.assert_called_once_with(
        "web_search",
        {
            "objective": "Find official docs",
            "search_queries": QUERIES,
            "session_id": "session-one",
        },
    )


def test_extract_preserves_full_content_and_goal():
    with patch.object(parallel, "_invoke", return_value={"status": "success"}) as invoke:
        asyncio.run(parallel.parallel_extract(["https://example.com"], "session-one", True, "Read the setup steps"))
    invoke.assert_called_once_with(
        "web_fetch",
        {
            "urls": ["https://example.com"],
            "session_id": "session-one",
            "full_content": True,
            "objective": "Read the setup steps",
        },
    )


def test_invalid_queries_and_urls_do_not_send_requests():
    with patch.object(parallel, "_invoke") as invoke:
        assert asyncio.run(parallel.parallel_search("goal", ["one"], "session"))["status"] == "error"
        assert asyncio.run(parallel.parallel_extract(["file:///secret"], "session"))["status"] == "error"
    invoke.assert_not_called()


def test_client_auth_and_partial_extraction_errors():
    payload = {
        "results": [{"url": "https://example.com", "excerpts": ["text"]}],
        "errors": [{"url": "https://missing.com", "error_type": "fetch_error"}],
    }

    class Client:
        def __init__(self, **kwargs):
            assert kwargs["headers"] == {"Authorization": "Bearer test-key"}
            assert kwargs["url"].endswith("?mode=fast")

        def start(self):
            pass

        def stop(self, *args):
            pass

        def call_tool_sync(self, **kwargs):
            return {"status": "success", "structuredContent": payload}

    with patch.object(parallel, "MCPClient", Client), patch.dict(parallel.os.environ, {"PARALLEL_API_KEY": "test-key"}):
        result = asyncio.run(parallel.parallel_extract(["https://example.com"], "session"))
    assert json.loads(result["content"][0]["text"]) == payload


def test_errors_do_not_expose_credentials():
    with patch.object(parallel, "_call", side_effect=RuntimeError("Bearer secret-key")):
        result = asyncio.run(parallel.parallel_search("goal", QUERIES, "session"))
    assert result["status"] == "error"
    assert "secret-key" not in result["content"][0]["text"]
