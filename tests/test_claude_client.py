"""Unit tests for ClaudeClient."""
from __future__ import annotations

import os
from unittest.mock import patch

import responses  # type: ignore

from claude_client import ClaudeClient, API_URL


def _mock_anthropic_import(module_name: str):  # pylint: disable=unused-argument
    """Always raise ModuleNotFoundError to force HTTP fallback."""
    raise ModuleNotFoundError


@responses.activate
def test_claude_chat_http() -> None:
    """ClaudeClient should return assistant content via raw HTTP fallback."""
    # Prepare fake HTTP response
    responses.add(
        responses.POST,
        API_URL,
        json={"choices": [{"message": {"content": "Hi there!"}}]},
        status=200,
    )

    # Ensure environment key is set for client init
    os.environ["ANTHROPIC_API_KEY"] = "test-key"

    with patch("claude_client.importlib.import_module", side_effect=_mock_anthropic_import):
        client = ClaudeClient(model="claude-3-haiku-20240307")
        reply = client.chat("Hello")

    assert reply == "Hi there!"