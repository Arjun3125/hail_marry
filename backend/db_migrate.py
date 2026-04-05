"""
Shared database migration + seeding utility.

Both the API lifespan and the worker call this on startup.

Handles two scenarios:
1. FRESH database (no tables): Uses Base.metadata.create_all() to build
   the full schema from ORM models, then stamps alembic to "head" so
   incremental migrations won't re-run.
2. EXISTING database: Runs alembic upgrade head for incremental changes.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("db-migrate")


def _is_fresh_database() -> bool:
    """Check if the database has no application tables at all."""
    from sqlalchemy import inspect
    from database import get_engine

    inspector = inspect(get_engine())
    tables = inspector.get_table_names()
    # If core tables don't exist, it's a fresh database
    core_tables = {"users", "tenants", "classes", "subjects"}
    return not core_tables.intersection(set(tables))


def _create_schema_from_models() -> None:
    """Create all tables from ORM models (for fresh databases)."""
    import models  # noqa: F401 — register all ORM models
    from database import Base, get_engine

    logger.info("Fresh database detected — creating full schema from ORM models...")
    Base.metadata.create_all(bind=get_engine())
    logger.info("Schema created successfully from ORM models.")


def _stamp_alembic_head() -> None:
    """Mark alembic as fully up-to-date (all migrations applied)."""
    from alembic import command

    alembic_cfg = _get_alembic_config()
    logger.info("Stamping alembic to 'head' (schema already matches latest models)...")
    command.stamp(alembic_cfg, "head")
    logger.info("Alembic stamped to head.")


def _get_alembic_config():
    """Build alembic config with DATABASE_URL override."""
    from alembic.config import Config

    alembic_cfg = Config("alembic.ini")

    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    return alembic_cfg


def _fix_postgresql_boolean_columns() -> None:
    """
    On PostgreSQL, columns like is_active must be BOOLEAN, not INTEGER,
    otherwise 'column = true' queries fail. This function auto-converts them.
    """
    from sqlalchemy import text
    from database import get_engine

    engine = get_engine()

    if "postgresql" not in str(engine.url):
        return

    tables_to_fix = {
        "tenants": ["is_active"],
        "billing_plans": ["is_active"],
        "fee_structures": ["is_active"],
    }

    logger.info("Checking PostgreSQL column types for boolean compatibility...")
    with engine.connect() as conn:
        for table, columns in tables_to_fix.items():
            for col in columns:
                try:
                    # Check if column is integer
                    res = conn.execute(text(
                        f"SELECT data_type FROM information_schema.columns "
                        f"WHERE table_name = '{table}' AND column_name = '{col}'"
                    )).scalar()
                    
                    if res == "integer":
                        logger.info(f"Converting {table}.{col} from INTEGER to BOOLEAN...")
                        # PostgreSQL requires explicit conversion: USING (col::boolean)
                        conn.execute(text(
                            f"ALTER TABLE {table} ALTER COLUMN {col} TYPE BOOLEAN "
                            f"USING ({col}::boolean)"
                        ))
                        # Also fix default if it was '1'
                        conn.execute(text(
                            f"ALTER TABLE {table} ALTER COLUMN {col} SET DEFAULT true"
                        ))
                        conn.commit()
                        logger.info(f"Successfully converted {table}.{col}.")
                except Exception as e:
                    logger.warning(f"Could not fix column {table}.{col}: {e}")


def run_migrations() -> bool:
    """Run database migrations. Returns True on success."""
    try:
        if _is_fresh_database():
            # Fresh DB: create everything from ORM, then stamp alembic
            _create_schema_from_models()
            _stamp_alembic_head()
        else:
            # Existing DB: run incremental alembic migrations
            from alembic import command
            alembic_cfg = _get_alembic_config()
            logger.info("Running database migrations (alembic upgrade head)...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully.")
        
        # After migrations/creation, ensure PostgreSQL types are correct
        _fix_postgresql_boolean_columns()
        
        return True
    except Exception as exc:
        logger.error("Database migration failed: %s", exc)
        return False


def seed_if_empty() -> bool:
    """Seed the database with CBSE demo data if no tenants exist."""
    try:
        from database import SessionLocal
        from src.domains.identity.models.tenant import Tenant
        import models  # noqa: F401

        db = SessionLocal()
        try:
            tenant_count = db.query(Tenant).count()
        finally:
            db.close()

        if tenant_count > 0:
            logger.info("Database already has %d tenant(s), skipping seed.", tenant_count)
            return True

        logger.info("Database is empty — running canonical Class 11 CBSE demo seeder...")
        try:
            from seed_cbse_demo import seed_demo_data

            seed_demo_data(skip_embeddings=False)
            logger.info("CBSE demo seeding completed successfully.")
            return True
        except Exception as seed_exc:
            logger.error("CBSE demo seeder failed: %s", seed_exc)
            return False
    except Exception as exc:
        logger.error("Seed check failed: %s", exc)
        return False


def ensure_db_ready() -> bool:
    """Run migrations + seed. Called by both API and worker on startup."""
    migration_ok = run_migrations()
    if migration_ok:
        seed_if_empty()
    return migration_ok
