#!/bin/sh
set -eu

echo "[railway] Generic launcher is deprecated; routing to API launcher." >&2
exec sh ./start-railway-api.sh
