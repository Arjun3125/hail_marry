#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT_VALUE="${PORT:-8000}"

echo "Running database bootstrap (combined)..."
python -c "from db_migrate import ensure_db_ready; ensure_db_ready()" || echo "Warning: DB bootstrap failed, will retry in-process."

echo "Starting AI Worker in the background..."
# Explicitly force the queue on, just in case Railway holds a stale variable
export AI_QUEUE_ENABLED=true
# Explicitly disable the worker health uvicorn server to prevent port collision
WORKER_HEALTH_ENABLED=false python ./ai_worker.py &
WORKER_PID=$!

echo "Starting Web API..."
exec python ./run_api.py --host 0.0.0.0 --port "$PORT_VALUE"
