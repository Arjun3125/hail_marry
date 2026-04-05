#!/bin/sh
set -eu

PORT_VALUE="${PORT:-8000}"

echo "Running database bootstrap (API)..."
python -c "from db_migrate import ensure_db_ready; ensure_db_ready()" || echo "Warning: DB bootstrap failed, API will retry in-process."

exec python run_api.py --host 0.0.0.0 --port "$PORT_VALUE"
