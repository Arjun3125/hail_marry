#!/bin/sh
set -eu

if [ -f "./backend/start-api.sh" ]; then
  exec sh ./backend/start-api.sh
fi

if [ -f "./start-api.sh" ]; then
  exec sh ./start-api.sh
fi

echo "[railway-api] Startup failed: could not find start-api.sh in repo root or backend/." >&2
exit 1
