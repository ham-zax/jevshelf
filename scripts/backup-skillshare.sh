#!/usr/bin/env bash
# Deduplicated, on-demand Git backup of the actual Skillshare source and configs.
# Runs once and exits. On no changes, makes no commit and sends nothing.
set -euo pipefail
umask 077

SOURCE="${SKILLSHARE_SOURCE:-$HOME/.config/skillshare/skills}"
CONFIG="${SKILLSHARE_CONFIG:-$HOME/.config/skillshare/config.yaml}"
COLLECTIONS="${JEVSHELF_COLLECTIONS_CONFIG:-$HOME/.config/jevshelf/collections.json}"
CHECKOUT="${JEVSHELF_BACKUP_CHECKOUT:-$HOME/repo/my-skills-backup}"
STATE_DIR="${JEVSHELF_BACKUP_STATE_DIR:-$HOME/.local/share/jevshelf}"
REMOTE="${JEVSHELF_BACKUP_REMOTE:-}"
INTERVAL_HOURS="${JEVSHELF_BACKUP_HOURS:-48}"
DUE=0
for option in "$@"; do
  case "$option" in
    --if-due) DUE=1 ;;
    --help|-h) echo 'Usage: backup-skillshare.sh [--if-due]'; exit 0 ;;
    *) echo "Unknown argument: $option" >&2; exit 2 ;;
  esac
done
[[ "$INTERVAL_HOURS" =~ ^[0-9]+$ ]] && (( INTERVAL_HOURS >= 1 )) || { echo 'Invalid backup interval' >&2; exit 2; }
[[ -d "$SOURCE/.git" && -f "$CONFIG" ]] || { echo 'Missing Skillshare source Git or configuration' >&2; exit 2; }

mkdir -p "$(dirname "$CHECKOUT")" "$STATE_DIR"
lock="$STATE_DIR/.my-skills-backup.lock"
exec 9>"$lock"
flock -n 9 || { echo 'A skill backup is already running'; exit 0; }

check_stamp="$STATE_DIR/.last-successful-backup-check"
pending_marker="$STATE_DIR/.pending-private-push"
if (( DUE )) && [[ -f "$check_stamp" && ! -e "$pending_marker" ]]; then
  now=$(date +%s)
  last=$(stat -c %Y "$check_stamp")
  if (( now - last < INTERVAL_HOURS * 3600 )); then
    echo "Backup check not due (last successful check within ${INTERVAL_HOURS}h)"
    exit 0
  fi
fi

if [[ ! -d "$CHECKOUT/.git" ]]; then
  [[ -n "$REMOTE" ]] || { echo 'Set JEVSHELF_BACKUP_REMOTE to a private Git repository URL on first use' >&2; exit 2; }
  mkdir -p "$CHECKOUT"
  git -C "$CHECKOUT" init -q -b main
  git -C "$CHECKOUT" remote add origin "$REMOTE"
fi
existing_remote=$(git -C "$CHECKOUT" remote get-url origin)
if [[ -n "$REMOTE" && "$existing_remote" != "$REMOTE" ]]; then
  echo 'Refusing to change the existing private backup remote' >&2
  exit 2
fi

mkdir -p "$CHECKOUT/skills" "$CHECKOUT/config"
# rsync mirrors exactly what is installed; symlinks are saved as symlinks,
# not followed. Never include upstream .git stores or credential-shaped files.
rsync -a --delete \
  --exclude='.git/' --exclude='.trash*/' --exclude='.DS_Store' \
  --exclude='.env' --exclude='.env.*' --exclude='.npmrc' --exclude='.netrc' \
  --exclude='*.pem' --exclude='*.key' --exclude='*.p12' --exclude='*.pfx' \
  --exclude='id_rsa' --exclude='id_ed25519' --exclude='credentials.json' \
  "$SOURCE/" "$CHECKOUT/skills/"
cp -p "$CONFIG" "$CHECKOUT/config/skillshare.yaml"
if [[ -f "$COLLECTIONS" ]]; then
  cp -p "$COLLECTIONS" "$CHECKOUT/config/collections.json"
else
  rm -f "$CHECKOUT/config/collections.json"
fi
cat > "$CHECKOUT/README.md" <<'BACKUP_README'
# My Skills Backup

Private, incremental Skillshare skills and JevShelf configuration backup.

- `skills/`: installed Skillshare source, including hidden routed skills, metadata and helpers.
- `config/skillshare.yaml`: Skillshare target configuration.
- `config/collections.json`: JevShelf collection manifest, when available.

Every changed snapshot is a Git commit. Unchanged checks produce no commit or push.
This does not contain prior local archive files, installed API credentials, or the
original Skillshare repository's internal `.git` history. Restore the files to
the appropriate locations and run `skillshare sync -g`. Review before restoring.
BACKUP_README

git -C "$CHECKOUT" add -A
if ! git -C "$CHECKOUT" diff --cached --quiet || ! git -C "$CHECKOUT" rev-parse --verify HEAD >/dev/null 2>&1; then
  git -C "$CHECKOUT" -c user.name='JevShelf Backup' \
    -c user.email='jevshelf-backup@users.noreply.github.com' \
    commit -q -m "Skill library snapshot $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo 'Skill contents changed; created one incremental Git snapshot'
else
  echo 'No changes to Skillshare or JevShelf configuration'
fi

# Push only if a local commit has not reached origin. Skips all network access
# for an unchanged, already-synchronized source.
if ! git -C "$CHECKOUT" show-ref --verify --quiet refs/remotes/origin/main || \
   [[ "$(git -C "$CHECKOUT" rev-parse HEAD)" != "$(git -C "$CHECKOUT" rev-parse origin/main)" ]]; then
  # GitHub backup destinations must remain PRIVATE, even on future runs.
  if [[ "$existing_remote" =~ ^https://github\.com/([^/]+)/([^/]+)(\.git)?$ ]]; then
    repo="${BASH_REMATCH[1]}/${BASH_REMATCH[2]%.git}"
    visibility=$(gh repo view "$repo" --json visibility --jq '.visibility')
    [[ "$visibility" == PRIVATE ]] || { echo 'Refusing push: remote is not PRIVATE' >&2; exit 3; }
  fi
  touch "$pending_marker"
  git -C "$CHECKOUT" push -q -u origin main
  echo 'Private GitHub backup synchronized'
fi
# Stamp only AFTER successful push (or verified no-op). A failed network push
# leaves the commit queued, so the next WSL start will retry it.
touch "$check_stamp"
rm -f "$pending_marker"
