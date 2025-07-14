"""Unit tests for web_utils.search"""
from __future__ import annotations

import os
from unittest import mock

import web_utils


def test_duckduckgo_search_parses_results() -> None:
    """Ensure search() returns parsed titles/links from DuckDuckGo HTML."""
    sample_html = """
    <html><body>
        <a class='result__a' href='https://example.com'>Example Domain</a>
        <a class='result__a' href='https://foo.com'>Foo</a>
    </body></html>
    """

    # Ensure SerpAPI key is absent so DDG path is chosen
    if "SEARCH_API_KEY" in os.environ:
        del os.environ["SEARCH_API_KEY"]

    with mock.patch("requests.post") as mock_post:
        mock_resp = mock.Mock()
        mock_resp.text = sample_html
        mock_resp.raise_for_status = mock.Mock(return_value=None)
        mock_post.return_value = mock_resp

        results = web_utils.search("example", max_results=2)

    assert results == [
        {"title": "Example Domain", "href": "https://example.com"},
        {"title": "Foo", "href": "https://foo.com"},
    ]