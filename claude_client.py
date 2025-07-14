"""Simple Claude (Anthropic) API wrapper for Ember.

This module provides a thin abstraction over the official `anthropic` Python SDK
while gracefully falling back to a raw HTTPS call if the SDK is unavailable.

Usage:
    from claude_client import ClaudeClient
    client = ClaudeClient()
    reply = client.chat("Hello Claude!")
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
import json
import os
import logging
import importlib
import requests
from requests import RequestException

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
API_URL = "https://api.anthropic.com/v1/chat/completions"

class ClaudeClient:  # pylint: disable=too-few-public-methods
    """High-level client for chatting with Claude models."""

    def __init__(self, api_key: Optional[str] = None, model: str | None = None, timeout: int = 60) -> None:
        self.api_key: str | None = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required for Claude access. Set it in the environment or pass explicitly."
            )
        self.model: str = model or DEFAULT_MODEL
        self.timeout = timeout

        # Placeholder for SDK client instance
        self._sdk_client: Any = None

        # Attempt to import the official SDK dynamically.
        try:
            self._anthropic = importlib.import_module("anthropic")  # type: ignore[attr-defined]
            self._sdk_client = self._anthropic.Anthropic(api_key=self.api_key)
            logger.debug("Using anthropic SDK for ClaudeClient")
        except ModuleNotFoundError:
            self._anthropic = None
            self._sdk_client = None
            logger.debug("anthropic SDK not found; falling back to raw HTTP API")

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def chat(
        self,
        prompt: str,
        messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate a completion for *prompt* and return the assistant response text.

        Any unexpected errors are logged and re-raised for upstream handling.
        """
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        try:
            if self._sdk_client is not None:
                return self._chat_with_sdk(messages, max_tokens, temperature)
            return self._chat_with_http(messages, max_tokens, temperature)
        except Exception as err:  # pylint: disable=broad-except
            logger.error("Claude chat failed: %s", err, exc_info=True)
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _chat_with_sdk(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Use official SDK streaming for best performance."""
        try:
            response = self._sdk_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
            # The SDK returns an object whose `.content[0].text` holds the assistant reply.
            return response.content[0].text  # type: ignore[attr-defined]
        except Exception as err:  # pylint: disable=broad-except
            logger.error("anthropic SDK request failed: %s", err, exc_info=True)
            raise

    def _chat_with_http(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Minimal HTTP fallback for environments without the SDK installed."""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except RequestException as err:
            logger.error("HTTP request to Anthropic failed: %s", err, exc_info=True)
            raise