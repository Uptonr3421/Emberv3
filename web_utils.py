"""Minimal web search helper utilities for Ember.

Currently implements a lightweight DuckDuckGo HTML scraping fallback that works
without API keys, plus an optional SerpAPI integration if `SEARCH_API_KEY` is
provided in the environment.

Example:
    from web_utils import search
    results = search("python list comprehension")
"""
from __future__ import annotations

from typing import List, Dict
import os
import logging
import requests
from bs4 import BeautifulSoup

# Optional Rich status spinner
try:
    from rich.console import Console as _RichConsole  # type: ignore
except ModuleNotFoundError:
    _RichConsole = None  # type: ignore
_console = _RichConsole() if _RichConsole else None

logger = logging.getLogger(__name__)

_SERP_API_KEY = os.getenv("SEARCH_API_KEY")

HEADERS = {"User-Agent": "Mozilla/5.0 (Ember Assistant)"}

def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Return a list of search results dicts with `title` and `href` keys."""
    if _SERP_API_KEY:
        try:
            return _search_with_serpapi(query, max_results)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("SerpAPI search failed (%s); falling back to DuckDuckGo", exc)
    return _search_with_duckduckgo(query, max_results)

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _search_with_serpapi(query: str, max_results: int) -> List[Dict[str, str]]:
    params = {"api_key": _SERP_API_KEY, "engine": "google", "q": query, "num": max_results}
    try:
        if _console:
            with _console.status("[bold cyan]Searching web via SerpAPI…[/]", spinner="earth"):
                resp = requests.get("https://serpapi.com/search", params=params, headers=HEADERS, timeout=20)
        else:
            resp = requests.get("https://serpapi.com/search", params=params, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as err:
        logger.error("SerpAPI HTTP error: %s", err, exc_info=True)
        raise RuntimeError("Search request failed. Please check your network or API limits.") from err
    results = []
    for item in data.get("organic_results", [])[:max_results]:
        results.append({"title": item.get("title", ""), "href": item.get("link", "")})
    return results

def _search_with_duckduckgo(query: str, max_results: int) -> List[Dict[str, str]]:
    try:
        if _console:
            with _console.status("[bold cyan]Searching web via DuckDuckGo…[/]", spinner="earth"):
                resp = requests.post("https://duckduckgo.com/html/", data={"q": query}, headers=HEADERS, timeout=20)
        else:
            resp = requests.post("https://duckduckgo.com/html/", data={"q": query}, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as err:
        logger.error("DuckDuckGo HTTP error: %s", err, exc_info=True)
        raise RuntimeError("DuckDuckGo search failed. Please check your network connection.") from err
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for a in soup.select("a.result__a")[:max_results]:
        results.append({"title": a.get_text(strip=True), "href": a.get("href", "")})
    return results