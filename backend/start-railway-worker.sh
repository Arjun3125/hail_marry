#!/bin/sh
set -eu

if [ -f "./start-worker.sh" ]; then
  exec sh ./start-worker.sh
fi

if [ -f "./backend/start-worker.sh" ]; then
  exec sh ./backend/start-worker.sh
fi

echo "[railway-worker] Startup failed: could not find start-worker.sh in current directory or backend/." >&2
exit 1
