"""Shared runtime container for app bootstrap."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import settings
from database import SessionLocal, engine


@dataclass(frozen=True)
class RuntimeContainer:
    settings: Any
    engine: Any
    session_local: Any


def build_runtime_container() -> RuntimeContainer:
    return RuntimeContainer(
        settings=settings,
        engine=engine,
        session_local=SessionLocal,
    )

