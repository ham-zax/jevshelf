#!/usr/bin/env bash
# Standalone, local recoverable Skillshare source backup. Does not upload secrets.
set -euo pipefail
umask 077
SOURCE="${SKILLSHARE_SOURCE:-$HOME/.config/skillshare/skills}"
CONFIG="${SKILLSHARE_CONFIG:-$HOME/.config/skillshare/config.yaml}"
BASE="${SKILLSHARE_BACKUP_DIR:-$HOME/.local/share/skillshare/backups}"
IF_DUE=0
INTERVAL_HOURS="${JEVSHELF_BACKUP_HOURS:-48}"
for arg in "$@"; do
  case "$arg" in
    --if-due) IF_DUE=1 ;;
    --help|-h) echo 'Usage: backup-skillshare.sh [--if-due]'; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done
[[ "$INTERVAL_HOURS" =~ ^[0-9]+$ ]] && (( INTERVAL_HOURS >= 1 )) || { echo 'Invalid JEVSHELF_BACKUP_HOURS' >&2; exit 2; }
[[ -d "$SOURCE/.git" && -f "$CONFIG" ]] || { echo 'Missing Skillshare Git source or config' >&2; exit 2; }
mkdir -p "$BASE"
chmod 700 "$BASE"
if (( IF_DUE )); then
  newest=0
  while IFS= read -r -d '' stamp; do
    epoch=$(stat -c %Y "$stamp")
    (( epoch > newest )) && newest="$epoch"
  done < <(find "$BASE" -maxdepth 2 -name backup.ok -type f -print0)
  if (( newest > 0 && $(date +%s) - newest < INTERVAL_HOURS * 3600 )); then
    echo "Backup not due (interval ${INTERVAL_HOURS}h)"
    exit 0
  fi
fi
stamp="$(date +%Y%m%d-%H%M%S)"
dest="$BASE/jevshelf-$stamp"
if [[ -e "$dest" ]]; then dest="${dest}-$$"; fi
mkdir -m 700 "$dest"
# Failure leaves an incomplete directory with NO backup.ok marker; no false success.
cp -p "$CONFIG" "$dest/config.yaml"
git -C "$SOURCE" bundle create "$dest/skillshare-source.bundle" --all
git -C "$SOURCE" bundle verify "$dest/skillshare-source.bundle" >"$dest/bundle-verification.txt" 2>&1
# Git bundles do not include uncommitted edits. Preserve exact current files, too.
tar -czf "$dest/skillshare-working-tree.tar.gz" -C "$SOURCE" --exclude='./.git' .
git -C "$SOURCE" rev-parse HEAD > "$dest/source-commit.txt"
git -C "$SOURCE" status --porcelain > "$dest/working-tree-status.txt"
# Optional extra pinned repo (e.g. academic shared resource checkout).
if [[ -n "${JEVSHELF_EXTRA_GIT_ROOT:-}" && -d "$JEVSHELF_EXTRA_GIT_ROOT/.git" ]]; then
  git -C "$JEVSHELF_EXTRA_GIT_ROOT" bundle create "$dest/extra-source.bundle" HEAD
  git -C "$JEVSHELF_EXTRA_GIT_ROOT" bundle verify "$dest/extra-source.bundle" >>"$dest/bundle-verification.txt" 2>&1
fi
(cd "$dest" && sha256sum *.bundle *.tar.gz config.yaml > SHA256SUMS)
touch "$dest/backup.ok"
printf 'JevShelf local source snapshot: %s\n' "$dest"
