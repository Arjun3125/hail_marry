#!/bin/sh
set -eu

echo "[railway] Generic launcher is deprecated; routing to worker launcher." >&2
exec sh ./start-railway-worker.sh
