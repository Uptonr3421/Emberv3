"""Centralized logging configuration for Ember project.

Importing this module sets up a standard logging configuration across the
codebase. It should be imported **once** at application startup (e.g., from
`preload.py`) to ensure consistent log formatting and levels.

The configuration defaults to INFO level but respects the standard `LOG_LEVEL`
environment variable if provided (DEBUG, INFO, WARNING, ERROR, CRITICAL).
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

class _CustomFormatter(logging.Formatter):
    """Adds timestamp and color to log output."""

    FORMATS = {
        logging.DEBUG: "\033[37m%(asctime)s [%(levelname)s] %(name)s: %(message)s\033[0m",
        logging.INFO: "\033[36m%(asctime)s [%(levelname)s] %(name)s: %(message)s\033[0m",
        logging.WARNING: "\033[33m%(asctime)s [%(levelname)s] %(name)s: %(message)s\033[0m",
        logging.ERROR: "\033[31m%(asctime)s [%(levelname)s] %(name)s: %(message)s\033[0m",
        logging.CRITICAL: "\033[41m%(asctime)s [%(levelname)s] %(name)s: %(message)s\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def _configure_root_logger() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_CustomFormatter())

    logging.basicConfig(level=LOG_LEVEL, handlers=[handler], force=True)
    logging.getLogger("requests").setLevel(logging.WARNING)


# Activate configuration on import
_configure_root_logger()