#!/bin/bash
set -euo pipefail

# Compatibility launcher.
# Canonical file: deploy/scripts/run-demo.sh

exec "$(dirname "$0")/deploy/scripts/run-demo.sh" "$@"
