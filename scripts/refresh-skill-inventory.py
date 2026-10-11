#!/usr/bin/env bash
# Compatibility for previous personal skill-management commands.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
exec python3 "$ROOT/my-skills/scripts/refresh-inventory.py" "$@"
