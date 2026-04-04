"""
Shared database migration + seeding utility.

Both the API lifespan and the worker call this on startup.
Alembic's `upgrade head` is idempotent — running it from multiple
processes is safe (the first one wins, subsequent calls are no-ops).
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("db-migrate")


def run_migrations() -> bool:
    """Run Alembic migrations. Returns True on success."""
    try:
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")

        # Ensure DATABASE_URL from env overrides alembic.ini default
        db_url = os.getenv("DATABASE_URL", "")
        if db_url:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)

        logger.info("Running database migrations (alembic upgrade head)...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")
        return True
    except Exception as exc:
        logger.error("Database migration failed: %s", exc)
        return False


def seed_if_empty() -> bool:
    """Seed the database with CBSE demo data if no tenants exist. Returns True on success."""
    try:
        from database import SessionLocal
        from src.domains.identity.models.tenant import Tenant
        import models  # noqa: F401 — register all ORM models

        db = SessionLocal()
        try:
            tenant_count = db.query(Tenant).count()
        finally:
            db.close()

        if tenant_count > 0:
            logger.info("Database already has %d tenant(s), skipping seed.", tenant_count)
            return True

        logger.info("Database is empty — running CBSE Demo seeder...")
        try:
            from seed_cbse_demo import seed as seed_cbse
            seed_cbse(skip_embeddings=False)
            logger.info("CBSE Demo seeding completed successfully.")
            return True
        except Exception as seed_exc:
            logger.error("CBSE seeder failed: %s", seed_exc)
            # Try lightweight fallback
            try:
                db = SessionLocal()
                from demo_seed import seed_demo_data
                seed_demo_data(db)
                db.close()
                logger.info("Lightweight demo seed completed as fallback.")
                return True
            except Exception as fallback_exc:
                logger.error("Fallback seeder also failed: %s", fallback_exc)
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
