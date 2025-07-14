#!/usr/bin/env python3
"""
Ember LLM Preloader
Preloads environment variables and initializes the quantized LLM for better performance.
"""

import os
import sys
import importlib
import log_setup  # noqa: F401 (sets up logging)
import logging

logger = logging.getLogger(__name__)

# Attempt to import python-dotenv; provide a no-op fallback if missing so linting passes.
try:
    from dotenv import load_dotenv  # type: ignore
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs):  # pylint: disable=unused-argument
        """Fallback noop when python-dotenv is unavailable."""
        return None

# Attempt to load Rich for pretty console output; fall back to plain prints if unavailable.
try:
    Console = importlib.import_module("rich.console").Console  # type: ignore[attr-defined]
except ModuleNotFoundError:
    class Console:  # fallback minimal console
        def print(self, *args, **kwargs):  # pylint: disable=unused-argument
            print(*args)

# Load environment variables from .env file
load_dotenv()
console = Console()

def initialize():
    """
    Placeholder function to initialize the LLM and other components.
    This function will be called to warm up the model before processing.
    """
    console.print("🔥 [bold]Ember LLM preloader initializing...[/]")
    logger.info("Ember LLM preloader initializing...")
    
    # Check if required environment variables are loaded
    api_key = os.getenv('API_KEY')
    model_name = os.getenv('MODEL_NAME', 'dolphin-2.9-llama3-8b')
    model_path = os.getenv('MODEL_PATH', r'C:\Ember\Models\uncensored-jordan-7b.Q4_K_M.gguf')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    claude_model = os.getenv('CLAUDE_MODEL', 'claude-3-haiku-20240307')
    
    if api_key:
        console.print(f"✅ API key loaded: [green]{api_key[:8]}...[/]")
        logger.info("API key loaded: %s...", api_key[:8])
    else:
        console.print("⚠️  [yellow]No API key found in environment[/]")
        logger.warning("No API key found in environment")
    
    console.print(f"🤖 Model configured: [cyan]{model_name}[/]")
    logger.info("Model configured: %s", model_name)
    console.print(f"📂 Model path: [magenta]{model_path}[/]")
    logger.info("Model path: %s", model_path)
    if anthropic_key:
        console.print(f"🧠 Claude integration: [green]enabled[/] with model [blue]{claude_model}[/]")
        logger.info("Claude integration enabled with model %s", claude_model)
    else:
        console.print("🧠 Claude integration: [yellow]disabled (no ANTHROPIC_API_KEY)[/]")
        logger.warning("Claude integration disabled (no ANTHROPIC_API_KEY)")
    console.print("✅ [bold green]Ember preloader ready![/]")
    logger.info("Ember preloader ready!")

if __name__ == "__main__":
    initialize()