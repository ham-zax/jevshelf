#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
command -v systemctl >/dev/null || { echo 'This installer needs systemd user services' >&2; exit 2; }
systemctl --user is-system-running >/dev/null 2>&1 || {
  echo 'systemd --user is unavailable. Use your OS scheduler with scripts/backup-skillshare.sh --if-due.' >&2; exit 2;
}
units="$HOME/.config/systemd/user"
mkdir -p "$units"
cat > "$units/jevshelf-backup.service" <<UNIT
[Unit]
Description=JevShelf recoverable local Skillshare backup
[Service]
Type=oneshot
ExecStart=$ROOT/scripts/backup-skillshare-vault.sh --if-due
UNIT
cat > "$units/jevshelf-backup.timer" <<'UNIT'
[Unit]
Description=Check every 12 hours whether 48-hour Skillshare backup is due
[Timer]
OnCalendar=*-*-* 03,15:00:00
Persistent=true
Unit=jevshelf-backup.service
[Install]
WantedBy=timers.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now jevshelf-backup.timer
printf 'Installed and enabled jevshelf-backup.timer\n'
systemctl --user list-timers --all --no-pager jevshelf-backup.timer
