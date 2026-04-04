#!/bin/sh
set -eu

echo "Running database migrations (worker)..."
alembic upgrade head || echo "Warning: alembic migration failed, worker will retry in-process."

exec python ai_worker.py
