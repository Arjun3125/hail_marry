"""Structured JSON logging helpers for backend services."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import settings


class JsonLogFormatter(logging.Formatter):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in ("trace_id", "tenant_id", "user_id", "path", "method", "status_code", "duration_ms", "event"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_structured_logging(service_name: str | None = None) -> None:
    if not settings.observability.enabled:
        return

    name = service_name or settings.observability.service_name
    root = logging.getLogger()
    if getattr(root, "_vidyaos_structured_logging", None) == name:
        return

    level_name = settings.observability.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    root.setLevel(level)
    root.handlers.clear()

    formatter = JsonLogFormatter(service_name=name)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    if settings.observability.log_path:
        log_path = Path(settings.observability.log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    root._vidyaos_structured_logging = name
