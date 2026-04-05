"""Bootstrap helpers for structured logging setup."""
from __future__ import annotations

import logging

from config import settings
from src.domains.platform.services.structured_logging import configure_structured_logging

SERVER_LOGGERS = (
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "gunicorn",
    "gunicorn.access",
    "gunicorn.error",
)


def configure_application_logging(service_name: str = "vidyaos-api") -> None:
    configure_structured_logging(service_name=service_name)
    _bridge_server_loggers_to_root()


def _bridge_server_loggers_to_root() -> None:
    """Force server/framework loggers to reuse the root stdout handler."""
    level_name = settings.observability.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    for logger_name in SERVER_LOGGERS:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(level)
