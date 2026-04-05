#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo ""
echo "========================================"
echo " VidyaOS Demo Launcher"
echo "========================================"
echo ""

export DEMO_MODE=true
export APP_ENV=local
export NEXT_PUBLIC_DEMO_MODE=true
export NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true
export NEXT_PUBLIC_API_URL=http://localhost:8000

cleanup() {
  kill "$(jobs -p)" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "[1/3] Starting backend..."
cd "$ROOT_DIR/backend"
DEMO_MODE=true python run_api.py --host 0.0.0.0 --port 8000 --reload &

echo "[2/3] Waiting for backend..."
sleep 3

echo "[3/3] Starting frontend..."
cd "$ROOT_DIR/frontend"
NEXT_PUBLIC_DEMO_MODE=true NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true npm run dev &

echo ""
echo "Frontend:  http://localhost:3000"
echo "Demo page: http://localhost:3000/demo"
echo "Backend:   http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

wait
