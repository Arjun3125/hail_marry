#!/bin/bash
# Start both backend API and frontend dev server for E2E testing
set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Start backend in background
echo "[E2E Setup] Starting backend API on port 8000..."
cd backend
PORT=8000 python ./run_api.py --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready (max 30 seconds)
echo "[E2E Setup] Waiting for backend to start..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:8000/api/health > /dev/null 2>&1; then
    echo "[E2E Setup] Backend is ready!"
    break
  fi
  echo "[E2E Setup] Waiting... ($i/30)"
  sleep 1
done

# Start frontend in foreground
echo "[E2E Setup] Starting frontend dev server on port 3000..."
cd frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null || true" EXIT INT TERM
