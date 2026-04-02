#!/bin/bash
set -euo pipefail

BASE_URL="${1:-http://localhost}"

echo "Running basic smoke checks against ${BASE_URL}"
curl -fsS "${BASE_URL}/health" >/dev/null
echo "Health check passed."
