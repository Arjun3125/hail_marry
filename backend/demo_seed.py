"""
Legacy compatibility wrapper for demo seeding.

The canonical demo dataset lives in ``seed_cbse_demo.py`` and represents the
Class 11 CBSE showcase tenant with six months of synthetic history for
student, parent, teacher, and admin journeys.
"""
from __future__ import annotations

from typing import Any


def seed_demo_data(db: Any | None = None, *, skip_embeddings: bool = True) -> bool:
    """Forward legacy demo-seed entrypoints to the canonical CBSE seeder."""
    from seed_cbse_demo import seed_demo_data as seed_cbse_demo_data

    seeded = seed_cbse_demo_data(skip_embeddings=skip_embeddings)
    if db is not None:
        try:
            db.expire_all()
        except Exception:
            pass
    return seeded


if __name__ == "__main__":
    seed_demo_data(skip_embeddings=False)
