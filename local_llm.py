"""Local Jordan 7B GGUF model client for Ember.

This module wraps `llama-cpp-python` to provide a drop-in chat interface that
mirrors `ClaudeClient.chat()` so higher-level code can swap between local and
cloud models easily.

If the model file is missing or `llama_cpp` is unavailable, initialization will
raise a descriptive `RuntimeError`.
"""
from __future__ import annotations

from typing import List, Dict, Optional
import os
import logging
import importlib

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = os.getenv(
    "MODEL_PATH", r"C:\Ember\Models\uncensored-jordan-7b.Q4_K_M.gguf"
)
DEFAULT_CTX_SIZE = int(os.getenv("MODEL_CTX", "4096"))
DEFAULT_TOP_P = float(os.getenv("MODEL_TOP_P", "0.95"))
DEFAULT_TOP_K = int(os.getenv("MODEL_TOP_K", "40"))
DEFAULT_REPEAT_PENALTY = float(os.getenv("MODEL_REPEAT_PENALTY", "1.1"))

# Attempt dynamic import to keep dependency optional during cold starts
try:
    llama_cpp = importlib.import_module("llama_cpp")  # type: ignore
    Llama = llama_cpp.Llama  # type: ignore[attr-defined]
except ModuleNotFoundError as exc:  # pragma: no cover
    raise RuntimeError(
        "`llama-cpp-python` is required for local Jordan model usage.\n"
        "Install it via `pip install llama-cpp-python` and ensure you have a CUDA/Metal or CPU build."
    ) from exc


class LocalJordanClient:  # pylint: disable=too-few-public-methods
    """Lightweight wrapper around llama-cpp that supports a simple chat API."""

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        ctx_size: int = DEFAULT_CTX_SIZE,
        temperature: float = 0.7,
    ) -> None:
        if not os.path.isfile(model_path):
            raise RuntimeError(
                f"Local model file not found at '{model_path}'. Set MODEL_PATH or pass model_path explicitly."
            )

        # Show summary log before heavy load
        logger.info("Loading local Jordan model from %s (ctx=%s)…", model_path, ctx_size)

        # `Llama` will mmap the GGUF model; this can be slow the first time.
        self._llm = Llama(model_path=model_path, n_ctx=ctx_size, verbose=False)
        self.temperature = temperature
        self.top_p = DEFAULT_TOP_P
        self.top_k = DEFAULT_TOP_K
        self.repeat_penalty = DEFAULT_REPEAT_PENALTY

        logger.info("Local Jordan model loaded successfully.")

    # ------------------------------------------------------------------
    # Public chat helper
    # ------------------------------------------------------------------

    def chat(
        self,
        prompt: str,
        messages: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 1024,
    ) -> str:  # noqa: D401
        """Return a completion string for *prompt* using a simple chat format."""
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        # Build a conversation text in a very simple format
        conversation = "".join(
            f"{m['role'].capitalize()}: {m['content'].strip()}\n" for m in messages
        )
        conversation += "Assistant:"

        try:
            output = self._llm(
                conversation,
                max_tokens=max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                repeat_penalty=self.repeat_penalty,
                stop=["User:", "Assistant:"],
            )
            return output["choices"][0]["text"].strip()
        except Exception as err:  # pylint: disable=broad-except
            logger.error("Local Jordan generation failed: %s", err, exc_info=True)
            raise RuntimeError("Local model could not generate a response. See logs for details.") from err