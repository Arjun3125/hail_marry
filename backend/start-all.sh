#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT_VALUE="${PORT:-8080}"

echo "Running database bootstrap (combined)..."
python - <<'PY'
import sys
from db_migrate import ensure_db_ready

sys.exit(0 if ensure_db_ready() else 1)
PY

echo "Starting AI Worker in the background..."
# Explicitly force the queue on, just in case Railway holds a stale variable
export AI_QUEUE_ENABLED=true
# Explicitly disable the worker health uvicorn server to prevent port collision
WORKER_HEALTH_ENABLED=false python ./ai_worker.py &
WORKER_PID=$!

echo "Starting Web API..."
exec python ./run_api.py --host 0.0.0.0 --port "$PORT_VALUE"
