#!/bin/bash
# ========================================
#  VidyaOS Demo Launcher — One-Click Start
# ========================================
#  No PostgreSQL, Redis, or Google OAuth needed.
#  Uses SQLite + auto-seeded demo data.
# ========================================

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   VidyaOS — Investor Demo Launcher    ║"
echo "║   No database config needed         ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Set demo environment
export DEMO_MODE=true
export APP_ENV=local
export NEXT_PUBLIC_DEMO_MODE=true
export NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Trap to kill background processes on exit
trap 'kill $(jobs -p) 2>/dev/null; exit' INT TERM

echo "[1/3] Starting backend (FastAPI + SQLite)..."
cd "$(dirname "$0")/backend"
DEMO_MODE=true python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

echo "[2/3] Waiting for backend..."
sleep 3

echo "[3/3] Starting frontend (Next.js)..."
cd "$(dirname "$0")/frontend"
NEXT_PUBLIC_DEMO_MODE=true NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true npm run dev &

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  Demo is starting!                  ║"
echo "║                                      ║"
echo "║  Frontend: http://localhost:3000     ║"
echo "║  Demo:     http://localhost:3000/demo║"
echo "║  Backend:  http://localhost:8000     ║"
echo "║                                      ║"
echo "║  Press Ctrl+C to stop both servers   ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Open browser
sleep 5
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000/demo
elif command -v open &> /dev/null; then
    open http://localhost:3000/demo
fi

wait
