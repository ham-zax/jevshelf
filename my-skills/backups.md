# My Skills — private change-based backup

**Remote:** [My Skills Backup](https://github.com/ham-zax/my-skills-backup), a **PRIVATE** GitHub repository, with its complete local working checkout at **`~/repo/my-skills-backup/`**. This location is independent of system configuration and other skill sources.

## What is actually backed up

- `skills/`: all Skillshare-managed source files (including hidden `vault-*` specialist skills), references, scripts, and Skillshare metadata. Its internal `.git` directory is not copied.
- `config/skillshare.yaml`: target synchronization rules and exclusions.
- `config/collections.json`: the JevShelf collection manifest.

Each changed snapshot becomes a normal Git commit and is pushed to the **private** backup repository. Git reuses existing objects: unchanged files are not re-uploaded as a new archive, and an unchanged library generates no new commit or push. Uncommitted modifications in the original Skillshare source are included through the file mirror. Credential-shaped files and local archive directories are excluded; nevertheless, keep the repository private and review sources before installing unfamiliar skills.

The original Skillshare source Git history is **not** replicated into the remote. The remote records the library contents at each change-based snapshot, with its own history. Historical `.bundle` and `.tar.gz` snapshots from previous backup workflows remain local; they are not uploaded.

## WSL-friendly schedule: no resident process

The user `systemd` timer is passive. It starts a one-shot service **five minutes after WSL's systemd user session starts**, and approximately every **48 hours after its last invocation** while the distro remains running. The backup process exits immediately. If the instance is stopped for a week, the startup trigger checks again on the next session, not seven times to catch up.

The script skips a check when the last successful check was under 48 hours ago (unless a previous push remains pending), and skips all Git commits and network uploads if file contents have not changed. A failed push remains queued and is retried when the next check runs.

```bash
bash scripts/install-backup-timer.sh
systemctl --user list-timers jevshelf-backup.timer
systemctl --user status jevshelf-backup.timer
journalctl --user -u jevshelf-backup.service --since '14 days ago'
```

No separate polling service, daemon, or Python process stays resident between invocations. WSL must be started for a check to occur.

## Manual commands and recovery

Run the same backup logic immediately (independent of the interval):

```bash
bash scripts/backup-skillshare.sh
# Or obey the 48-hour check interval:
bash scripts/backup-skillshare.sh --if-due
cd ~/repo/my-skills-backup
git status -sb
git log -5 --oneline
```

**Recover:** Clone the private Git repository into a separate staging location, inspect a selected snapshot, restore approved contents from `skills/` to `~/.config/skillshare/skills/` and the manifest/config into their proper paths, then run `skillshare sync --dry-run -g` before actual synchronization. Do not blindly overwrite a live Skillshare installation. Consider restoring the source's dedicated `.git` separately if you need its original upstream history.

**Earlier local archives:** `bash scripts/list-backups.sh` lists older `~/.local/share/skillshare/backups/jevshelf-*` directories. Those bundles remain available for recovery, but the new scheduled backup no longer generates them.

**First verified remote backup:** commit `d4fb9f1` on October 12, 2026, synchronized to `ham-zax/my-skills-backup` on `main`. The local Git checkout was moved into `~/repo/my-skills-backup/` and a no-change check verified it was still synchronized after the move.
