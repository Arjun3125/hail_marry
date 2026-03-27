"""
Database engine, session factory, and base model.
Supports PostgreSQL (production) and SQLite (demo mode).
"""
import os
import uuid
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
from sqlalchemy.ext.compiler import compiles
from config import settings


# ── SQLite ↔ PostgreSQL type compatibility ──
# Compiler overrides let PostgreSQL-specific column types work on SQLite
# without modifying any model code.

@compiles(PG_UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(32)"

@compiles(PG_JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


# Register Python uuid.UUID adapter at the sqlite3 driver level.
# This ensures uuid objects are automatically serialized as hex strings.
sqlite3.register_adapter(uuid.UUID, lambda u: u.hex)
sqlite3.register_converter("CHAR(32)", lambda b: uuid.UUID(b.decode()))


_db_url = os.getenv("DATABASE_URL", settings.database.url)
if _db_url and _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

_db_url_ro = os.getenv("DATABASE_URL_RO", getattr(settings.database, "url_ro", "")) or _db_url
if _db_url_ro and _db_url_ro.startswith("postgres://"):
    _db_url_ro = _db_url_ro.replace("postgres://", "postgresql://", 1)

# Async database URL - convert postgresql:// to postgresql+asyncpg://
_async_db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
if "sqlite" in _db_url:
    _async_db_url = _db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

if "sqlite" in _db_url:
    engine = create_engine(
        _db_url,
        echo=settings.database.echo,
        connect_args={"check_same_thread": False},
    )
    engine_ro = create_engine(
        _db_url_ro,
        echo=settings.database.echo,
        connect_args={"check_same_thread": False},
    )
    # Disable RETURNING clause — pysqlite can't handle it with server_default timestamps
    engine.dialect.insert_returning = False
    engine.dialect.update_returning = False
    engine_ro.dialect.insert_returning = False
    engine_ro.dialect.update_returning = False
    
    # Async engine for SQLite
    async_engine = create_async_engine(
        _async_db_url,
        echo=settings.database.echo,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        _db_url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    engine_ro = create_engine(
        _db_url_ro,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    # Async engine for PostgreSQL
    async_engine = create_async_engine(
        _async_db_url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocalRO = sessionmaker(autocommit=False, autoflush=False, bind=engine_ro)

# Async session factory
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_ro():
    """FastAPI dependency that yields a read-only database session."""
    db = SessionLocalRO()
    try:
        yield db
    finally:
        db.close()


async def get_async_session():
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
