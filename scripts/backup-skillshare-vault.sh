#!/usr/bin/env bash
# Compatibility for existing personal workflows and older documentation.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
if [[ -d "$ROOT/vendor/academic/.git" ]]; then
  export JEVSHELF_EXTRA_GIT_ROOT="$ROOT/vendor/academic"
fi
exec "$ROOT/scripts/backup-skillshare.sh" "$@"
