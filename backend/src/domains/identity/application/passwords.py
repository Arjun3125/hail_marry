"""Shared password hashing helpers for non-route orchestration code."""
from __future__ import annotations

from functools import lru_cache

from passlib.context import CryptContext


@lru_cache(maxsize=1)
def get_password_context() -> CryptContext:
    import sys
    _bcrypt_rounds = 4 if "pytest" in sys.modules else 12
    return CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=_bcrypt_rounds)


def hash_password(value: str) -> str:
    return get_password_context().hash(value)

