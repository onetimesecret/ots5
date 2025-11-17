"""
Logging Configuration

Structured logging for the application.
"""

import logging
import sys
from typing import Optional

from onetimesecret.config import settings


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (default: root logger)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)

    # Set level from config
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Create handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, settings.log_level.upper()))

        # Format
        if settings.log_format == "json":
            # JSON format for production
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
            )
        else:
            # Human-readable format for development
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
