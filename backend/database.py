"""
Database engine, session factory, and base model.
Supports PostgreSQL (production) and SQLite (demo mode).
"""
import os
import sqlite3
import uuid
from typing import AsyncGenerator

from sqlalchemy.inspection import _inspects, inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


# ── SQLite ↔ PostgreSQL type compatibility ──
# Compiler overrides let PostgreSQL-specific column types work on SQLite
# without modifying any model code.

def _setup_compilers():
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, ARRAY as PG_ARRAY
    from sqlalchemy import ARRAY as SA_ARRAY
    from sqlalchemy.ext.compiler import compiles

    @compiles(PG_UUID, "sqlite")
    def compile_uuid_sqlite(type_, compiler, **kw):
        return "CHAR(32)"

    @compiles(PG_JSONB, "sqlite")
    def compile_jsonb_sqlite(type_, compiler, **kw):
        return "TEXT"

    @compiles(PG_ARRAY, "sqlite")
    def compile_array_sqlite(type_, compiler, **kw):
        return "TEXT"

    @compiles(SA_ARRAY, "sqlite")
    def compile_sa_array_sqlite(type_, compiler, **kw):
        return "TEXT"


# Register Python uuid.UUID adapter at the sqlite3 driver level.
# This ensures uuid objects are automatically serialized as hex strings.
sqlite3.register_adapter(uuid.UUID, lambda u: u.hex)
sqlite3.register_converter("CHAR(32)", lambda b: uuid.UUID(b.decode()))


_engine = None
_engine_ro = None
_async_engine = None
_SessionLocal = None
_SessionLocalRO = None
_AsyncSessionLocal = None


def _is_truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_postgres_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _resolve_database_url(env_name: str, fallback: str) -> str:
    if _is_truthy_env("TESTING"):
        test_env_name = f"TEST_{env_name}"
        test_url = os.getenv(test_env_name)
        if test_url:
            return _normalize_postgres_url(test_url)
    return _normalize_postgres_url(os.getenv(env_name, fallback))


def _get_db_urls() -> tuple[str, str, str]:
    """Resolve database URLs from environment and settings."""
    from config import settings
    url = _resolve_database_url("DATABASE_URL", settings.database.url)
    url_ro = (
        _resolve_database_url("DATABASE_URL_RO", getattr(settings.database, "url_ro", ""))
        or url
    )

    # Async database URL - convert postgresql:// to postgresql+asyncpg://
    async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if "sqlite" in url:
        async_url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url, url_ro, async_url


def _reset_lazy_proxy(proxy) -> None:
    if hasattr(proxy, "_instance"):
        object.__setattr__(proxy, "_instance", None)


def reset_database_state(dispose: bool = True) -> None:
    global _engine, _engine_ro, _async_engine
    global _SessionLocal, _SessionLocalRO, _AsyncSessionLocal

    if dispose:
        for candidate in (_engine, _engine_ro):
            if candidate is not None:
                candidate.dispose()
        if _async_engine is not None:
            sync_engine = getattr(_async_engine, "sync_engine", None)
            if sync_engine is not None:
                sync_engine.dispose()

    _engine = None
    _engine_ro = None
    _async_engine = None
    _SessionLocal = None
    _SessionLocalRO = None
    _AsyncSessionLocal = None

    for proxy in (engine, engine_ro, async_engine, SessionLocal, SessionLocalRO, AsyncSessionLocal):
        _reset_lazy_proxy(proxy)


def get_engine():
    global _engine
    if _engine is None:
        from sqlalchemy import create_engine
        from config import settings
        _setup_compilers()
        url, _, _ = _get_db_urls()
        if "sqlite" in url:
            _engine = create_engine(
                url,
                echo=settings.database.echo,
                connect_args={"check_same_thread": False},
            )
            # Disable RETURNING clause — pysqlite can't handle it with server_default timestamps
            _engine.dialect.insert_returning = False
            _engine.dialect.update_returning = False
        else:
            _engine = create_engine(
                url,
                echo=settings.database.echo,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
    return _engine


def get_engine_ro():
    global _engine_ro
    if _engine_ro is None:
        from sqlalchemy import create_engine
        from config import settings
        _setup_compilers()
        _, url_ro, _ = _get_db_urls()
        if "sqlite" in url_ro:
            _engine_ro = create_engine(
                url_ro,
                echo=settings.database.echo,
                connect_args={"check_same_thread": False},
            )
            _engine_ro.dialect.insert_returning = False
            _engine_ro.dialect.update_returning = False
        else:
            _engine_ro = create_engine(
                url_ro,
                echo=settings.database.echo,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
    return _engine_ro


def get_async_engine():
    global _async_engine
    if _async_engine is None:
        from sqlalchemy.ext.asyncio import create_async_engine
        from config import settings
        _setup_compilers()
        url, _, async_url = _get_db_urls()
        if "sqlite" in url:
            _async_engine = create_async_engine(
                async_url,
                echo=settings.database.echo,
                connect_args={"check_same_thread": False},
            )
            _async_engine.sync_engine.dialect.insert_returning = False
            _async_engine.sync_engine.dialect.update_returning = False
        else:
            _async_engine = create_async_engine(
                async_url,
                echo=settings.database.echo,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
    return _async_engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        from sqlalchemy.orm import sessionmaker
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_session_local_ro():
    global _SessionLocalRO
    if _SessionLocalRO is None:
        from sqlalchemy.orm import sessionmaker
        _SessionLocalRO = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine_ro()
        )
    return _SessionLocalRO


def get_async_session_local():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
        _AsyncSessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=get_async_engine(), class_=AsyncSession
        )
    return _AsyncSessionLocal


class _LazyProxy:
    """A minimal proxy to defer engine/session initialization until accessed."""

    def __init__(self, factory):
        object.__setattr__(self, "_factory", factory)
        object.__setattr__(self, "_instance", None)

    def _get_instance(self):
        if object.__getattribute__(self, "_instance") is None:
            object.__setattr__(
                self, "_instance", object.__getattribute__(self, "_factory")()
            )
        return object.__getattribute__(self, "_instance")

    def __getattr__(self, name):
        return getattr(self._get_instance(), name)

    def __setattr__(self, name, value):
        setattr(self._get_instance(), name, value)

    def __call__(self, *args, **kwargs):
        return self._get_instance()(*args, **kwargs)

    def __repr__(self):
        return f"<LazyProxy for {object.__getattribute__(self, '_factory').__name__}>"


@_inspects(_LazyProxy)
def _inspect_lazy_proxy(subject: _LazyProxy):
    """Delegate SQLAlchemy inspection APIs to the resolved proxied object."""
    return sa_inspect(subject._get_instance())


engine = _LazyProxy(get_engine)
engine_ro = _LazyProxy(get_engine_ro)
async_engine = _LazyProxy(get_async_engine)
SessionLocal = _LazyProxy(get_session_local)
SessionLocalRO = _LazyProxy(get_session_local_ro)
AsyncSessionLocal = _LazyProxy(get_async_session_local)


class Base(DeclarativeBase):
    """Base class for all models."""
    __allow_unmapped__ = True


def get_db():
    """FastAPI dependency that yields a database session."""
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def get_db_ro():
    """FastAPI dependency that yields a read-only database session."""
    db = get_session_local_ro()()
    try:
        yield db
    finally:
        db.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with get_async_session_local()() as session:
        yield session
