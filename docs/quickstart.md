# JevShelf quickstart

## 1. Install the portable product

You need Git and [uv](https://docs.astral.sh/uv/). On Linux or WSL:

```bash
git clone https://github.com/ham-zax/jevshelf.git
cd jevshelf
bash scripts/bootstrap.sh
./bin/jevshelf init
./bin/jevshelf collections
```

`init` creates `~/.config/jevshelf/collections.json` from a safe self-contained demo containing two tiny sample skills. It does **not** install or modify your existing skill-manager configuration. To use live Jev selection, export `TYPESAFE_API_KEY` in your environment; otherwise use `--mode lexical`.

```bash
./bin/jevshelf search --collection writing --mode lexical --task 'summarize the meeting notes and identify next actions'
# Copy the `id` and `digest` values returned by search:
./bin/jevshelf load --collection writing --id '<returned-id>' --expected-digest '<returned-digest>'
```

## 2. Connect Skillshare as your source of truth

Install [Skillshare](https://github.com/runkids/skillshare) separately, follow its official setup, and use its global source library. For example, to enable one optional specialist skill hidden behind JevShelf:

```bash
# Preview and audit, then import only the selected specialist:
skillshare install emilkowalski/skills --skill break-ui --kind skill --into vault-ui --dry-run -g
skillshare install emilkowalski/skills --skill break-ui --kind skill --into vault-ui -g
```

Set the `roots` for an `ui` collection in `~/.config/jevshelf/collections.json` to `~/.config/skillshare/skills/vault-ui`. Set `vault-*` as a Skillshare **target exclusion** in every target you want kept clean (review existing exclusions and only add the new pattern; do not replace other filters):

```bash
skillshare target codex --add-exclude 'vault-*' -g
skillshare target pi --add-exclude 'vault-*' -g
# Repeat for other enabled targets, if applicable.
```

## 3. Add one portable native shim per collection

```bash
python3 scripts/create-shim.py --collection ui --name ui-specialists \
  --description 'Use for UI edge-case testing and layout stress checks' --output /tmp/ui-specialists
skillshare install /tmp/ui-specialists --name ui-specialists -g
skillshare sync --dry-run -g
skillshare sync -g
```

Start a **new** Codex/Pi/other host session. The host can now discover the `ui-specialists` shim, which calls `jevshelf search --collection ui --mode jev ...` and then loads selected text. For CLI access from any project, optionally link the launcher to your user `PATH`:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/bin/jevshelf" ~/.local/bin/jevshelf
```

**Important:** this linking step is not done automatically. A shim can only run if `jevshelf` is available to its host subprocess and that host has network access/authorization for TypeSafe. Always validate one end-to-end selection and bounded load before claiming the installation is operational.

## 4. Keep it maintainable and recoverable

Skillshare manages updates and host sync. To snapshot your source and configuration into a **private** Git repository, first create your own private GitHub repository, then supply it during the first backup:

```bash
# Example remote; substitute your own PRIVATE repository URL.
JEVSHELF_BACKUP_REMOTE=https://github.com/YOUR-ACCOUNT/my-skills-backup.git \
  bash scripts/backup-skillshare.sh
```

The script creates or reuses a local Git checkout at `~/repo/my-skills-backup/` by default (override with `JEVSHELF_BACKUP_CHECKOUT`). It copies current Skillshare skill files, metadata and selected config while excluding the original source's `.git`, common credential files, and old backup archives. It creates an incremental Git commit **only on actual changes**, and pushes only if a new commit is pending. If an upload fails, it is retried during a later invocation.

```bash
bash scripts/backup-skillshare.sh          # Force a check now; skip unchanged commits
bash scripts/backup-skillshare.sh --if-due # Respect the 48-hour throttle
```

On Linux/WSL with user systemd, install the passive scheduler:

```bash
bash scripts/install-backup-timer.sh
systemctl --user list-timers jevshelf-backup.timer
```

This is **not an always-on daemon**. A short `Type=oneshot` job runs approximately **five minutes after WSL's user systemd starts** and at 48-hour intervals while it remains running. It exits after checking. No job executes while WSL is stopped, and changes are not copied continuously. On a future WSL start it checks again after the delay. The background timer itself uses systemd's normal scheduling, not resident application memory.

**Backup storage:** The local Git checkout is in `~/repo/my-skills-backup/`; the GitHub repository must remain private. The backup's *snapshot history* is Git commits, not repeated compressed archives. The source's original `.git` history is not replicated; retain it separately if that is needed.
