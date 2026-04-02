"""Shared password hashing helpers for non-route orchestration code."""
from __future__ import annotations

from functools import lru_cache

from passlib.context import CryptContext


@lru_cache(maxsize=1)
def get_password_context() -> CryptContext:
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(value: str) -> str:
    return get_password_context().hash(value)

