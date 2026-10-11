#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT"
command -v git >/dev/null || { echo 'git is required' >&2; exit 2; }
command -v uv >/dev/null || { echo 'uv is required: https://docs.astral.sh/uv/' >&2; exit 2; }
mkdir -p vendor
upstream=https://github.com/himomohi/jev-skill-router.git
revision=b3be6ec9545fc2526abaa8be135fbe0bd34b78e9
if [[ ! -d vendor/router/.git ]]; then
  git clone --quiet --depth 1 "$upstream" vendor/router
fi
if [[ "$(git -C vendor/router rev-parse HEAD)" != "$revision" ]]; then
  git -C vendor/router fetch --quiet --depth 1 origin "$revision"
  git -C vendor/router checkout --quiet --detach "$revision"
fi
if [[ "$(git -C vendor/router rev-parse HEAD)" != "$revision" ]]; then
  echo 'Failed to align the pinned Jev router dependency' >&2; exit 2
fi
if [[ ! -x .venv/bin/python ]] || ! .venv/bin/python -c 'import sys; assert sys.version_info[:2] == (3,13)' >/dev/null 2>&1; then
  uv venv --clear --python 3.13 .venv
fi
export UV_CACHE_DIR="$ROOT/.uv-cache"
uv pip install --python .venv/bin/python -e ./vendor/router -e . pytest
printf '\nJevShelf installed: %s/.venv/bin/jevshelf\n' "$ROOT"
printf 'Configure collections with: %s/.venv/bin/jevshelf init\n' "$ROOT"
printf 'Optional portable shortcut: ln -s %s/bin/jevshelf "$HOME/.local/bin/jevshelf"\n' "$ROOT"
