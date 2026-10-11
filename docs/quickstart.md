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

Skillshare handles audits, updates and host sync. For a recoverable local source snapshot, run:

```bash
bash scripts/backup-skillshare.sh
```

For a Linux/WSL user-systemd timer that checks twice daily and captures the source approximately once every 48 hours while systemd is running:

```bash
bash scripts/install-backup-timer.sh
systemctl --user status jevshelf-backup.timer
```

Backups live under `~/.local/share/skillshare/backups/jevshelf-*` by default, with a full source Git bundle **and** a working-tree archive (including uncommitted files), plus target config. **No backups are pushed to GitHub.** If WSL is shut down, the persistent timer will catch up on the next systemd user session; no job can run while the distro is stopped.

To uninstall a routed source, use **scoped** Skillshare uninstall commands and sync; don't erase unrelated libraries. If you need a separate project-only skill, install with Skillshare project mode from the *target application's* directory instead of JevShelf.
