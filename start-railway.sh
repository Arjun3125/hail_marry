#!/bin/sh
set -eu

if [ -f "./backend/start-all.sh" ]; then
  exec sh ./backend/start-all.sh
fi

if [ -f "./start-all.sh" ]; then
  exec sh ./start-all.sh
fi

echo "Railway startup failed: could not find start-all.sh in repo root or backend/." >&2
exit 1
