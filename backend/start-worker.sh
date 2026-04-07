#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[backend-worker] Running database bootstrap..."
python - <<'PY'
import sys
from db_migrate import ensure_db_ready

sys.exit(0 if ensure_db_ready() else 1)
PY
echo "[backend-worker] Database bootstrap succeeded."

echo "[backend-worker] Launching AI worker."
exec python ./ai_worker.py
