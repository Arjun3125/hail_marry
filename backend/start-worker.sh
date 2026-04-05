#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running database bootstrap (worker)..."
python -c "from db_migrate import ensure_db_ready; ensure_db_ready()" || echo "Warning: DB bootstrap failed, worker will retry in-process."

exec python ./ai_worker.py
