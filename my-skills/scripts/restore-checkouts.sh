#!/usr/bin/env bash
# Maintain the original pinned upstream sources for the maintainer's optional collections.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
mkdir -p "$ROOT/vendor"
pin() {
  local folder="$1" url="$2" sha="$3" path="$ROOT/vendor/$1"
  if [[ ! -d "$path/.git" ]]; then
    git clone --quiet --depth 1 "$url" "$path"
    if [[ "$(git -C "$path" rev-parse HEAD)" != "$sha" ]]; then
      git -C "$path" fetch --quiet --depth 1 origin "$sha"
      git -C "$path" checkout --detach --quiet "$sha"
    fi
  fi
  local head
  head=$(git -C "$path" rev-parse HEAD)
  if [[ "$head" != "$sha" ]]; then
    echo "Source $folder is at $head, not pinned $sha; refusing to change existing checkout" >&2
    return 2
  fi
}
pin marketing https://github.com/coreyhaines31/marketingskills.git 1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff
pin thinking https://github.com/tjboudreaux/cc-thinking-skills.git 7b8fece345dfaa11773be7152ccd194589cb5437
pin academic https://github.com/Imbad0202/academic-research-skills.git d1e51716e53fc371727ea6164dd709fc8ea28c97
pin emil https://github.com/emilkowalski/skills.git 2d228630ba1446365f614a108cb8252f1feda202
pin sentry https://github.com/getsentry/skills.git d18b7aa8ba878354e5c348310230e652f7690f9c
printf 'Maintainer upstream checkouts available in %s/vendor\n' "$ROOT"
