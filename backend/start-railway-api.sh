#!/bin/sh
set -eu

if [ -f "./start-api.sh" ]; then
  exec sh ./start-api.sh
fi

if [ -f "./backend/start-api.sh" ]; then
  exec sh ./backend/start-api.sh
fi

echo "[railway-api] Startup failed: could not find start-api.sh in current directory or backend/." >&2
exit 1
