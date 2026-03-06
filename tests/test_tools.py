"""Tests for custom MCP tools."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_sailpoint_web_search_augments_iiq_query():
    """Verify IIQ queries are augmented with product context."""
    from sailpoint_agent.tools.sailpoint_search import sailpoint_web_search

    with patch("sailpoint_agent.tools.sailpoint_search._execute_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [
            {"title": "IIQ Docs", "url": "https://developer.sailpoint.com/docs", "snippet": "Test result"}
        ]

        result = await sailpoint_web_search({"query": "BuildMap rule", "product": "iiq"})

        assert "content" in result
        # Verify the search was called (query augmentation happens inside)
        mock_search.assert_called_once()
        call_args = mock_search.call_args
        assert "IdentityIQ" in call_args[0][1]


@pytest.mark.asyncio
async def test_sailpoint_web_search_augments_isc_query():
    """Verify ISC queries are augmented with product context."""
    from sailpoint_agent.tools.sailpoint_search import sailpoint_web_search

    with patch("sailpoint_agent.tools.sailpoint_search._execute_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = []

        result = await sailpoint_web_search({"query": "Transforms", "product": "isc"})

        assert "content" in result
        mock_search.assert_called_once()
        call_args = mock_search.call_args
        assert "Identity Security Cloud" in call_args[0][1]


@pytest.mark.asyncio
async def test_sailpoint_web_search_handles_failure():
    """Verify search failure returns helpful error message."""
    from sailpoint_agent.tools.sailpoint_search import sailpoint_web_search

    with patch("sailpoint_agent.tools.sailpoint_search._execute_search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("Network error")

        result = await sailpoint_web_search({"query": "test", "product": "both"})

        assert "content" in result
        assert "Search failed" in result["content"][0]["text"]


@pytest.mark.asyncio
async def test_doc_retriever_handles_failure():
    """Verify doc retriever returns error on fetch failure."""
    from sailpoint_agent.tools.doc_retriever import doc_retriever

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get.side_effect = Exception("Timeout")
        mock_client_cls.return_value = mock_client

        result = await doc_retriever({"url": "https://example.com/docs"})

        assert "Failed to fetch" in result["content"][0]["text"]


def test_format_results_empty():
    """Verify empty results return 'No results found'."""
    from sailpoint_agent.tools.sailpoint_search import _format_results

    assert _format_results([]) == "No results found."


def test_format_results_with_data():
    """Verify results are formatted correctly."""
    from sailpoint_agent.tools.sailpoint_search import _format_results

    results = [
        {"title": "Test Title", "url": "https://example.com", "snippet": "Test snippet"},
    ]
    formatted = _format_results(results)

    assert "[1] Test Title" in formatted
    assert "https://example.com" in formatted
    assert "Test snippet" in formatted
