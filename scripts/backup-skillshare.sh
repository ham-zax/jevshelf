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
# not followed. Never include upstream .git stores, credential-shaped files,
# or backup archive files/directories (*.bundle, tarballs, zips). The
# --delete-excluded flag also removes such artifacts from the mirror when a
# previous snapshot predates an exclusion, so they leave with the next commit
# instead of lingering in the working tree.
rsync -a --delete --delete-excluded \
  --exclude='.git/' --exclude='.trash*/' --exclude='.DS_Store' \
  --exclude='.env' --exclude='.env.*' --exclude='.npmrc' --exclude='.netrc' \
  --exclude='*.pem' --exclude='*.key' --exclude='*.p12' --exclude='*.pfx' \
  --exclude='id_rsa' --exclude='id_ed25519' --exclude='credentials.json' \
  --exclude='*.bundle' --exclude='*.tar' --exclude='*.tar.gz' \
  --exclude='*.tgz' --exclude='*.zip' \
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
archive_paths=('*.bundle' '*.tar' '*.tar.gz' '*.tgz' '*.zip'
               '*.bundle/*' '*.tar/*' '*.tar.gz/*' '*.tgz/*' '*.zip/*')
# Archives must never be staged: refuse the snapshot rather than let a
# previously mirrored bundle/tarball silently reach a pending push. The git
# output is captured fully before inspection so a failed or truncated listing
# can never read as clean.
if ! staged_files=$(git -C "$CHECKOUT" ls-files -- "${archive_paths[@]}"); then
  echo 'Refusing snapshot: could not inspect staged files' >&2
  exit 3
fi
if [[ -n "$staged_files" ]]; then
  echo 'Refusing snapshot: backup mirror contains archive files' >&2
  exit 3
fi
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
  # A push uploads every unsynced object, not just the current tree: refuse
  # when pending history introduces archive blobs, even though the working
  # tree is clean. Blobs already reachable from the remote (for example an
  # archive that was synchronized before the exclusion and is now deleted)
  # are outside the pending range, so legitimate cleanup is not blocked.
  # History is never rewritten here; the operator removes the local-only
  # commits by hand (see my-skills/backups.md) and retries.
  if git -C "$CHECKOUT" show-ref --verify --quiet refs/remotes/origin/main; then
    pending_range='refs/remotes/origin/main..HEAD'
  else
    pending_range='HEAD'
  fi
  # NOTE: `rev-list --objects <range> -- <archive patterns>` cannot serve
  # here: its blob walk starts from the endpoint trees, so an archive blob
  # added mid-range and deleted later is silently omitted. Inspect each
  # pending commit's own file changes instead.
  if ! pending_commits=$(git -C "$CHECKOUT" rev-list "$pending_range"); then
    echo 'Refusing push: could not inspect pending history for archive content' >&2
    exit 3
  fi
  pending_archive=0
  for pending_commit in $pending_commits; do
    if ! commit_changes=$(git -C "$CHECKOUT" diff-tree --no-commit-id --name-status -m -r --root "$pending_commit" -- "${archive_paths[@]}"); then
      echo 'Refusing push: could not inspect pending history for archive content' >&2
      exit 3
    fi
    while IFS=$'\t' read -r change_status _; do
      [[ -n "$change_status" ]] || continue
      # A pure deletion only mentions the name; the content stays (or is
      # already) on the remote, so it must not block cleanup.
      [[ "$change_status" == D ]] && continue
      pending_archive=1
      break 2
    done <<<"$commit_changes"
  done
  if (( pending_archive )); then
    echo 'Refusing push: pending local history contains archive files; remove the unpushed commits locally (without rewriting pushed history) and retry' >&2
    exit 3
  fi
  # Every effective push destination must be a verified PRIVATE GitHub
  # repository, even on future runs. Enumerate push URLs rather than the fetch
  # URL so a separate or additional pushurl cannot bypass the check; Git
  # resolves url.*.insteadOf/pushInsteadOf rewrites in this query.
  # Supported (verified) destinations, all on github.com: HTTPS,
  # scp-like SSH (git@github.com:owner/repo) and ssh:// URLs. Anything else,
  # or any destination whose privacy cannot be established (including a
  # failing gh query), fails closed before any push.
  if ! push_url_list=$(git -C "$CHECKOUT" remote get-url --push --all origin 2>/dev/null); then
    echo 'Refusing push: could not determine push destinations for origin' >&2
    exit 3
  fi
  push_urls=()
  while IFS= read -r push_url_line; do
    [[ -n "$push_url_line" ]] && push_urls+=("$push_url_line")
  done <<<"$push_url_list"
  (( ${#push_urls[@]} > 0 )) || { echo 'Refusing push: no push destination for origin' >&2; exit 3; }
  for push_url in "${push_urls[@]}"; do
    [[ -n "$push_url" ]] || continue
    repo=''
    if [[ "$push_url" =~ ^https://github\.com/([^/]+)/([^/]+)/?$ ]]; then
      repo="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    elif [[ "$push_url" =~ ^git@github\.com:([^/]+)/([^/]+)/?$ ]]; then
      repo="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    elif [[ "$push_url" =~ ^ssh://git@github\.com(:[0-9]+)?/([^/]+)/([^/]+)/?$ ]]; then
      repo="${BASH_REMATCH[2]}/${BASH_REMATCH[3]}"
    else
      echo 'Refusing push: unsupported destination (only github.com HTTPS, git@github.com: and ssh://git@github.com/ forms are verified)' >&2
      exit 3
    fi
    repo="${repo%.git}"
    # Query the explicit github.com URL, never a short OWNER/REPO name: a
    # short name follows GH_HOST and the invoking directory, which could
    # resolve an enterprise repository of the same name instead of the
    # allowed push destination.
    visibility=$(gh repo view "https://github.com/${repo}" --json visibility --jq '.visibility') || { echo "Refusing push: could not verify privacy of '$repo'" >&2; exit 3; }
    [[ "$visibility" == PRIVATE ]] || { echo 'Refusing push: remote is not PRIVATE' >&2; exit 3; }
  done
  touch "$pending_marker"
  git -C "$CHECKOUT" push -q -u origin main
  echo 'Private GitHub backup synchronized'
fi
# Stamp only AFTER successful push (or verified no-op). A failed network push
# leaves the commit queued, so the next WSL start will retry it.
touch "$check_stamp"
rm -f "$pending_marker"
