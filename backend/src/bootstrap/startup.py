"""Startup, lifespan, and demo compatibility helpers."""
from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from database import Base
from src.domains.platform.services.feature_flags import init_feature_flags
from src.domains.platform.services.runtime_scheduler import run_digest_loop, run_doc_watch_loop
from src.domains.platform.services.startup_checks import enforce_startup_dependencies


def create_lifespan(container):
    @asynccontextmanager
    async def lifespan(_app):
        db_session = container.session_local()
        try:
            init_feature_flags(db_session)
        finally:
            db_session.close()

        if not os.environ.get("TESTING"):
            try:
                enforce_startup_dependencies("api")
            except Exception as exc:
                import logging
                logging.getLogger("startup").warning(
                    "Startup dependency checks failed (continuing in demo mode): %s", exc
                )

        stop_event = asyncio.Event()
        tasks: list[asyncio.Task] = []
        if not os.environ.get("TESTING"):
            if container.settings.doc_watch.enabled:
                tasks.append(asyncio.create_task(run_doc_watch_loop(stop_event)))
            if container.settings.digest_email.enabled:
                tasks.append(asyncio.create_task(run_digest_loop(stop_event)))
        yield
        stop_event.set()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    return lifespan


def _apply_demo_schema_compatibility_fixes(engine) -> None:
    """Keep demo DB snapshots compatible with newer model columns."""

    def ensure_column(connection, table_name: str, column_name: str, ddl: str, table_names: set[str]) -> None:
        if table_name not in table_names:
            return
        existing_columns = {
            row[1]
            for row in connection.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
        }
        if column_name not in existing_columns:
            connection.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")

    with engine.begin() as connection:
        table_names = {
            row[0]
            for row in connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        ensure_column(connection, "ai_queries", "notebook_id", "notebook_id CHAR(32)", table_names)
        ensure_column(connection, "documents", "notebook_id", "notebook_id CHAR(32)", table_names)
        ensure_column(connection, "kg_concepts", "notebook_id", "notebook_id CHAR(32)", table_names)


def initialize_demo_mode(container) -> None:
    if not container.settings.app.demo_mode:
        return

    import models  # noqa: F401
    from src.domains.identity.models.user import User

    Base.metadata.create_all(bind=container.engine)
    _apply_demo_schema_compatibility_fixes(container.engine)
    try:
        db_session = container.session_local()
        init_feature_flags(db_session)
        if db_session.query(User).count() == 0:
            # Prefer rich CBSE seeder; fall back to lightweight demo_seed
            try:
                from seed_cbse_demo import seed as seed_cbse
                seed_cbse(skip_embeddings=True)  # skip NVIDIA API during auto-start
            except Exception as cbse_exc:
                print(f"CBSE seeder failed ({cbse_exc}), falling back to lightweight demo_seed.")
                from demo_seed import seed_demo_data
                seed_demo_data(db_session)
        db_session.close()
    except Exception as exc:  # pragma: no cover - demo-only compatibility path
        print(f"Warning: demo seed check failed: {exc}")

