"""Bootstrap helpers for structured logging setup."""
from __future__ import annotations

from src.domains.platform.services.structured_logging import configure_structured_logging


def configure_application_logging(service_name: str = "vidyaos-api") -> None:
    configure_structured_logging(service_name=service_name)

