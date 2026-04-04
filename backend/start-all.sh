#!/bin/sh
set -eu

PORT_VALUE="${PORT:-8000}"

echo "Running database bootstrap (combined)..."
python -c "from db_migrate import ensure_db_ready; ensure_db_ready()" || echo "Warning: DB bootstrap failed, will retry in-process."

echo "Starting AI Worker in the background..."
python ai_worker.py &
WORKER_PID=$!

echo "Starting Web API..."
exec uvicorn main:app --host 0.0.0.0 --port "$PORT_VALUE"
