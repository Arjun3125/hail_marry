#!/bin/sh
set -eu

PORT_VALUE="${PORT:-8000}"

echo "Running database migrations..."
alembic upgrade head

echo "Running demo seed script..."
python seed_cbse_demo.py || echo "Warning: Seeding script encountered an error but continuing boot."

exec uvicorn main:app --host 0.0.0.0 --port "$PORT_VALUE"
