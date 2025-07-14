"""Integration test for LocalJordanClient.

Skips automatically if the Jordan 7B GGUF file is absent or llama-cpp-python is
not installed in the environment to avoid CI failures.
"""
from __future__ import annotations

import os
import logging
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_local_jordan_generation() -> None:  # noqa: D401
    """Load the local model (if present) and verify it returns a response."""
    from pathlib import Path

    model_path = os.getenv("MODEL_PATH", r"C:\Ember\Models\uncensored-jordan-7b.Q4_K_M.gguf")
    path = Path(model_path)

    if not path.is_file():
        pytest.skip("Local model file not found; skipping integration test.")

    try:
        from local_llm import LocalJordanClient  # pylint: disable=import-error
    except RuntimeError as err:
        pytest.skip(f"LocalJordanClient unavailable: {err}")

    llm = LocalJordanClient(model_path=str(path), temperature=0.0, ctx_size=1024)
    reply = llm.chat("Say 'hello'", max_tokens=10)

    logger.info("Jordan model reply: %s", reply)
    assert "hello".lower() in reply.lower()