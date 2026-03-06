"""
Database engine, session factory, and base model.
Supports PostgreSQL (production) and SQLite (demo mode).
"""
import os
import uuid
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
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


# In DEMO_MODE, use SQLite for zero-config operation
if settings.app.demo_mode:
    _db_url = os.getenv("DATABASE_URL", "sqlite:///./demo.db")
    engine = create_engine(
        _db_url,
        echo=settings.database.echo,
        connect_args={"check_same_thread": False} if "sqlite" in _db_url else {},
    )
    # Disable RETURNING clause — pysqlite can't handle it with server_default timestamps
    engine.dialect.insert_returning = False
    engine.dialect.update_returning = False
else:
    engine = create_engine(
        settings.database.url,
        echo=settings.database.echo,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
