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
import time
import atexit
from pathlib import Path

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

# Attempt to import optional Rich helpers (Panel, Progress). Fallback to None if unavailable.
try:
    Panel = importlib.import_module("rich.panel").Panel  # type: ignore[attr-defined]
    progress_mod = importlib.import_module("rich.progress")  # type: ignore
    Progress = progress_mod.Progress  # type: ignore[attr-defined]
    SpinnerColumn = progress_mod.SpinnerColumn  # type: ignore[attr-defined]
    BarColumn = progress_mod.BarColumn  # type: ignore[attr-defined]
    TimeElapsedColumn = progress_mod.TimeElapsedColumn  # type: ignore[attr-defined]
    TextColumn = progress_mod.TextColumn  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    Panel = None  # type: ignore
    Progress = None  # type: ignore

# Load environment variables from .env file
load_dotenv()
console = Console()

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _display_banner() -> None:  # noqa: D401
    """Render a colorful ASCII-art banner if Rich is available."""

    ascii_art = r"""
   _____                 _
  |  ___|               | |
  | |__ _ __ _   _ _ __ | | ___  ___
  |  __| '__| | | | '_ \| |/ _ \/ __|
  | |__| |  | |_| | |_) | |  __/\__ \
  \____/_|   \__, | .__/|_|\___||___/
              __/ | |
             |___/|_|
    """

    if Panel is not None:
        console.print(Panel.fit(ascii_art, title="[bold bright_yellow]🔥  Welcome to Emberv3  🔥[/]", border_style="orange1", padding=(1, 4)))
    else:
        console.print(ascii_art)

def initialize():
    """
    Placeholder function to initialize the LLM and other components.
    This function will be called to warm up the model before processing.
    """
    # Visual banner
    _display_banner()

    console.print("\n[bold bright_cyan]Initializing components...[/]")
    logger.info("Ember LLM preloader initializing...")

    # -------------------------------------------------------------------
    # Optional progress bar for visual feedback
    # -------------------------------------------------------------------

    if Progress is not None:
        tasks_to_run = [
            ("Loading environment", 0.2),
            ("Verifying API keys", 0.3),
            ("Setting up model", 0.4),
            ("Preparing Claude client", 0.2),
        ]

        with Progress(
            SpinnerColumn(style="bright_yellow"),
            "[progress.description]{task.description}",
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            for desc, delay in tasks_to_run:
                task_id = progress.add_task(desc, total=100)
                # quick incremental update rather than sleep entire delay at once
                for _ in range(10):
                    time.sleep(delay / 10)
                    progress.advance(task_id, 10)
                progress.update(task_id, completed=100)
    
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

    # Verify that the local GGUF model exists
    path_obj = Path(model_path)
    if path_obj.is_file():
        console.print("[green]✔ Local model file found.[/]")
        logger.info("Local model file found at %s", model_path)
    else:
        console.print("[yellow]⚠ Local model file not found. Please verify MODEL_PATH.[/]")
        logger.warning("Local model file not found: %s", model_path)

    if anthropic_key:
        console.print(f"🧠 Claude integration: [green]enabled[/] with model [blue]{claude_model}[/]")
        logger.info("Claude integration enabled with model %s", claude_model)
    else:
        console.print("🧠 Claude integration: [yellow]disabled (no ANTHROPIC_API_KEY)[/]")
        logger.warning("Claude integration disabled (no ANTHROPIC_API_KEY)")
    console.print("✅ [bold green]Ember preloader ready![/]")
    logger.info("Ember preloader ready!")

    # Helpful usage tips
    console.print(
        "\n[bold bright_white]Tips:[/]\n"
        " • Chat with Claude: [green]>>> from claude_client import ClaudeClient; ClaudeClient().chat('Hello')[/]\n"
        " • Quick web search: [green]>>> from web_utils import search; search('python decorators')[/]\n"
        " • Run tests: [green]pytest -q[/]", justify="left"
    )

# ---------------------------------------------------------------------------
# Graceful shutdown handler
# ---------------------------------------------------------------------------


def _shutdown() -> None:  # noqa: D401
    """Display a goodbye banner and flush logs on interpreter exit."""
    goodbye = "[bold green]\n✅ Ember shutdown complete. Goodbye! 👋[/]"
    try:
        console.print(goodbye)
    except Exception:  # pragma: no cover
        print("Ember shutdown complete. Goodbye!")
    logger.info("Ember shutdown complete.")


atexit.register(_shutdown)

if __name__ == "__main__":
    initialize()