# My Skills — backup snapshots

**Backup policy:** Local-only archives under `~/.local/share/skillshare/backups/`. Never commit or upload the actual archives, which contain skill code, metadata and potentially private local paths.

## What each JevShelf snapshot contains

- `skillshare-source.bundle`: full Git history of the Skillshare library at backup time.
- `skillshare-working-tree.tar.gz`: current source files **including uncommitted edits** (Git bundles alone miss these).
- `config.yaml`: Skillshare target filters and configuration as backed up.
- `extra-source.bundle`: optional pinned academic shared-resource repository (on this machine).
- `SHA256SUMS`, `backup.ok`, `source-commit.txt`, and `working-tree-status.txt` for verification and recovery.

Only a completed directory with `backup.ok` counts toward the two-day interval. Archives are created with restrictive local permissions. There is no automatic remote upload or unbounded cloud retention policy.

## Snapshot examples / current checkpoints

| Date (local) | Snapshot | Notes |
|---|---|---|
| 2026-10-12 | `jevshelf-20261012-013914` | Verified v0.2.0 clean migration: new JevShelf shims, all 28 hidden skills, full Git and working-tree archives |
| 2026-10-12 | `jevshelf-20261012-012513` | Most recent snapshot after upgrading Skillshare to v0.25.5 |
| 2026-10-12 | `jevshelf-20261012-011734` | New Git + working-tree snapshot format; includes academic resource bundle |
| 2026-10-12 | `jev-vault-20261012-010901` | Previous verified Git-bundle-only format, before productization |
| 2026-10-12 | `jev-vault-20261012-005924` | Previous verified state, before the later API-key bridge adjustments |

The GitHub table is a **metadata index**, not the snapshot archives themselves. For the live list, run `bash scripts/list-backups.sh` on the WSL machine. Automatically created future snapshots appear there without requiring Git commits.

## Automatic backup

```bash
bash scripts/install-backup-timer.sh
systemctl --user list-timers jevshelf-backup.timer
systemctl --user status jevshelf-backup.timer
journalctl --user -u jevshelf-backup.service --since '14 days ago'
```

Timer is calendar-based with `Persistent=true` and is safe to reinstall. It checks twice daily and creates a snapshot only after the 48-hour minimum interval has elapsed. WSL must be started for scheduled work to run; missed calendar events resume at next start. If the Skillshare library is dirty, the backup still saves the working tree so changes are not lost.

## Manual backup and recovery

```bash
bash scripts/backup-skillshare.sh
bash scripts/list-backups.sh
```

To verify a backup, run `(cd "$SNAPSHOT" && sha256sum -c SHA256SUMS)` and clone `skillshare-source.bundle` into **a fresh staging directory**. Use `tar -tzf skillshare-working-tree.tar.gz` to inspect uncommitted source content before restoring it. Do not blindly overwrite a live Skillshare library. Restore the audited source, reinstall the snapshot's target `config.yaml` if needed, and run `skillshare sync -g`. After a full recovery, recheck JevShelf collection paths and live TypeSafe authorization.
