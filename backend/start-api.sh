#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT_VALUE="${PORT:-8080}"

echo "[backend-api] Running database bootstrap..."
python - <<'PY'
import sys
from db_migrate import ensure_db_ready

sys.exit(0 if ensure_db_ready() else 1)
PY
echo "[backend-api] Database bootstrap succeeded."

echo "[backend-api] Launching FastAPI on port ${PORT_VALUE}."
exec python ./run_api.py --host 0.0.0.0 --port "$PORT_VALUE"
