#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR"

echo "Starting VidyaOS demo on localhost..."

# Backend
(
  cd "$ROOT/backend"
  export DEMO_MODE=true
  export APP_ENV=local
  export APP_DEBUG=true
  export STARTUP_CHECKS_ENABLED=false
  export DATABASE_URL="sqlite:///./vidyaos_demo.db"
  python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
) &

# Frontend
(
  cd "$ROOT/frontend"
  export NEXT_PUBLIC_DEMO_MODE=true
  export NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true
  export NEXT_PUBLIC_API_URL=http://localhost:8080
  npm run dev -- -p 7125
) &

echo ""
echo "Frontend:  http://localhost:7125"
echo "Demo page: http://localhost:7125/demo"
echo "Backend:   http://localhost:8080"
echo "API docs:  http://localhost:8080/docs"
echo ""

sleep 8

# Try to open browser on macOS or Linux
if command -v open &>/dev/null; then
  open http://localhost:7125/demo
elif command -v xdg-open &>/dev/null; then
  xdg-open http://localhost:7125/demo
fi

wait
