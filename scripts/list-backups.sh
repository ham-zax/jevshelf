#!/usr/bin/env bash
set -euo pipefail
BASE="${SKILLSHARE_BACKUP_DIR:-$HOME/.local/share/skillshare/backups}"
printf '%-30s %-8s %s\n' 'SNAPSHOT' 'STATUS' 'FILES'
if [[ ! -d "$BASE" ]]; then exit 0; fi
while IFS= read -r dir; do
  [[ -n "$dir" ]] || continue
  name="${dir##*/}"
  if [[ -f "$dir/backup.ok" ]]; then
    printf '%-30s %-8s %s\n' "$name" 'complete' "$(du -sh "$dir" | cut -f1)"
  else
    printf '%-30s %-8s %s\n' "$name" 'incomplete' "$(du -sh "$dir" | cut -f1)"
  fi
done < <(find "$BASE" -maxdepth 1 -mindepth 1 -type d -name 'jevshelf-*' | sort -r)
