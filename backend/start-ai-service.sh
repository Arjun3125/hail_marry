#!/bin/sh
set -eu

PORT_VALUE="${PORT:-8001}"

exec uvicorn ai_service_app:app --host 0.0.0.0 --port "$PORT_VALUE"
