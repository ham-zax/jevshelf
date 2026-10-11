# My Skills

This folder is the **maintainer's example configuration and operating notebook**. It is separate from the portable **JevShelf product** documented in [the repository root](../README.md). You do not need these skills, frameworks, backups, or named collections to use JevShelf yourself.

## How I use the system

1. **Skillshare** owns the global source library: installation, per-source audit, upstream provenance, target exclusions, updates, and symlink synchronization.
2. **JevShelf + TypeSafe Jev** keep occasional specialist skills behind five visible domain shims, selecting and loading only the relevant leaf when needed.
3. **Aegis** is my one canonical engineering process. Matt Pocock and Addy Osmani are evaluated alternatives that remain uninstalled.
4. **Codex, Pi and other configured agents** receive consistent visible Skillshare shims (with existing host-specific exclusions). The model decides whether to invoke a domain shim; JevShelf does not force host calls.
5. **Local Git and periodic source snapshots** protect skills, metadata, source revisions, backups and rollback capabilities. Source archives never live in the public GitHub repository.

## Current Skillshare library

<small>Recorded 12 October 2026; regenerate the snapshot after installation changes.</small>

| Category | Source skills | Visibility |
|---|---:|---|
| Original global skills | 17 | Direct native discovery, subject to host filters |
| Canonical Aegis engineering skills | 23 | Direct native discovery |
| Additional collection shims | 3 | Direct native discovery |
| `jevify` | 1 | Direct native discovery |
| Academic Research | 5 | Jev-only |
| Emil UI | 15 | Jev-only |
| Sentry specialist tools | 4 | Jev-only |
| lassejlv additions | 3 | Jev-only |
| Taste frontend aesthetics | 1 | Jev-only |
| **Total in Skillshare source** | **72** | **44 visible source skills + 28 hidden leaf skills** |

The five routed collections are **Marketing 50, Thinking 28, Academic 5, UI 17, and Code Specialists 6**. Marketing and Thinking are backed by read-only upstream checkouts, while the newer specialist leaves are held in Skillshare-managed hidden `vault-*` source groups. Native agents see only their domain entry points.

**Current full list:** [installed.md](installed.md) and [machine-readable installed.csv](installed.csv). The inventory also tracks the 38 Matt Pocock and 25 Addy Osmani candidate skills as **not installed**.

**Active collection roots:** [collections.json](collections.json) is the optional manifest for this machine. To configure a compatible JevShelf installation with my selection:

```bash
mkdir -p ~/.config/jevshelf
cp my-skills/collections.json ~/.config/jevshelf/collections.json
jevshelf collections
```

Those commands work only after acquiring the underlying Skillshare sources. They do not fetch my skills or overwrite other people's source libraries.

## Maintenance, updates, and swaps

| Action | Where | Why |
|---|---|---|
| Review/install new skill | [installation-protocol.md](installation-protocol.md) | Scope: direct vs routed vs project-specific, audits, safe updates |
| Change active engineering pack | [swap-engineering-system prompt](prompts/swap-engineering-system.md) | Reversible **user-approved** Aegis/Matt/Addy switch, never two simultaneously |
| Read canonical engineering policy | [engineering-systems.md](engineering-systems.md) | Aegis ownership and host compatibility constraints |
| Update specialist vaults | [vault-management.md](vault-management.md) | Per-group Skillshare updates, audit caveats, rollback |
| Rebuild original source checkouts | [restore-checkouts.sh](scripts/restore-checkouts.sh) | Pinned upstreams, not installed automatically for other users |
| Refresh inventory | `python3 my-skills/scripts/refresh-inventory.py` | Rewrites only `installed.md` and `installed.csv` |
| Jevify and TypeSafe key | [jevify-typesafe.md](jevify-typesafe.md) | Existing environment credentials, no stored keys |

Skillshare **v0.25.5** is installed as of 12 October 2026. Keeping it current is a **separate deliberate step**: check `skillshare --version`, review `skillshare upgrade --help`, take a source backup, upgrade the CLI, run `skillshare doctor` and `skillshare sync --dry-run -g`. I don't automatically install unreviewed third-party skill updates just because an upstream repository moved.

## Favorites and references

- [reference skills](references.md): **Distilly** — reserved for opt-in, consent-based Person Profiles, **not installed**.
- **Haft** — considered for long-term engineering decision memory; **not installed**.
- **No Yak Shaving** — reviewed, useful optional proportionality advice; **not installed**.

## Local backup snapshots

The real archives are *not in GitHub*. See [backups.md](backups.md) for the schedule, restore details, and latest snapshot metadata. View all snapshots on this machine with:

```bash
bash scripts/list-backups.sh
bash scripts/backup-skillshare-vault.sh            # Back up now
bash scripts/backup-skillshare-vault.sh --if-due   # Back up if >= 48h since previous success
systemctl --user status jevshelf-backup.timer      # See automatic timer
```

The timer is configured for **03:00 and 15:00 daily**, taking a new source snapshot when at least **48 hours** have elapsed since the last successful snapshot. Missed systemd calendar checks catch up when WSL is next running; no job executes while WSL is stopped.
