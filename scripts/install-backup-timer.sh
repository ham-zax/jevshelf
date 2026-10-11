#!/usr/bin/env bash
# Install a passive, zero-polling systemd timer for a short one-shot backup.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
command -v systemctl >/dev/null || { echo 'systemd user services required' >&2; exit 2; }
systemctl --user is-system-running >/dev/null 2>&1 || {
  echo 'systemd --user unavailable; run scripts/backup-skillshare.sh manually' >&2; exit 2;
}
units="$HOME/.config/systemd/user"
mkdir -p "$units"
cat > "$units/jevshelf-backup.service" <<UNIT
[Unit]
Description=Check for changed Skillshare files and push private backup
[Service]
Type=oneshot
ExecStart=$ROOT/scripts/backup-skillshare.sh --if-due
UNIT
cat > "$units/jevshelf-backup.timer" <<'UNIT'
[Unit]
Description=One-shot Skillshare backup check after WSL start and every 48 hours
[Timer]
OnStartupSec=5min
OnUnitInactiveSec=48h
AccuracySec=2min
Unit=jevshelf-backup.service
[Install]
WantedBy=timers.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now jevshelf-backup.timer
systemctl --user restart jevshelf-backup.timer
systemctl --user list-timers --all --no-pager jevshelf-backup.timer
