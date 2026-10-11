#!/usr/bin/env bash
# Install a passive, zero-polling systemd timer for a short one-shot backup.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
command -v systemctl >/dev/null || { echo 'systemd user services required' >&2; exit 2; }
systemctl --user is-system-running >/dev/null 2>&1 || {
  echo 'systemd --user unavailable; run scripts/backup-skillshare.sh manually' >&2; exit 2;
}
# Quote one ExecStart word using systemd unit syntax: double quotes keep
# whitespace in the executable path intact, and '%' is doubled so a checkout
# path cannot trigger systemd.unit "%" specifier interpolation (both verified
# with systemd-analyze verify). Characters systemd cannot represent in the
# executable word are refused BEFORE any unit is written instead of emitting
# an invalid unit: '$' (the first argument may not be a variable, per
# systemd.service, so '$$' would not collapse back), '"' and '\' (no proven
# executable-word escape round-trip), and newline (would break the unit line).
systemd_quote() {
  local word="$1"
  case "$word" in
    *'$'* | *'"'* | *\\* | *$'\n'*)
      echo "install-backup-timer: refusing to write unit: executable path contains characters unsupported by systemd ExecStart: $word" >&2
      return 1
      ;;
  esac
  word=${word//%/%%}
  printf '"%s"' "$word"
}
units="$HOME/.config/systemd/user"
exe=$(systemd_quote "$ROOT/scripts/backup-skillshare.sh") || exit 2
mkdir -p "$units"
cat > "$units/jevshelf-backup.service" <<UNIT
[Unit]
Description=Check for changed Skillshare files and push private backup
[Service]
Type=oneshot
ExecStart=$exe --if-due
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
