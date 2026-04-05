#!/bin/sh
set -eu

if [ -f "./start-all.sh" ]; then
  exec sh ./start-all.sh
fi

if [ -f "./backend/start-all.sh" ]; then
  exec sh ./backend/start-all.sh
fi

echo "Railway startup failed: could not find start-all.sh in current directory or backend/." >&2
exit 1
