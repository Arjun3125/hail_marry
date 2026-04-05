#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT_VALUE="${PORT:-8080}"

echo "[backend-api] Running database bootstrap..."
python -c "from db_migrate import ensure_db_ready; ensure_db_ready()"
echo "[backend-api] Database bootstrap succeeded."

echo "[backend-api] Launching FastAPI on port ${PORT_VALUE}."
exec python ./run_api.py --host 0.0.0.0 --port "$PORT_VALUE"
