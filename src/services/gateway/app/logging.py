"""Logging configuration for the Gateway service.

Re-exports shared logging utilities for convenience.
"""

from shared.logging import get_logger, setup_logging


__all__ = ["get_logger", "setup_logging"]
