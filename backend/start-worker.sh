#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[backend-worker] Running database bootstrap..."
python -c "from db_migrate import ensure_db_ready; ensure_db_ready()"
echo "[backend-worker] Database bootstrap succeeded."

echo "[backend-worker] Launching AI worker."
exec python ./ai_worker.py
