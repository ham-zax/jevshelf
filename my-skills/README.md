# My Skills

This folder is the **maintainer's example configuration and operating notebook**. It is separate from the portable **JevShelf product** documented in [the repository root](../README.md). You do not need these skills, frameworks, backups, or named collections to use JevShelf yourself.

## How I use the system

1. **Skillshare** owns the global source library: installation, per-source audit, upstream provenance, target exclusions, updates, and symlink synchronization.
2. **JevShelf + TypeSafe Jev** keep occasional specialist skills behind five visible domain shims, selecting and loading only the relevant leaf when needed.
3. **Aegis** is my one canonical engineering process. Matt Pocock and Addy Osmani are evaluated alternatives that remain uninstalled.
4. **Codex, Pi and other configured agents** receive consistent visible Skillshare shims (with existing host-specific exclusions). The model decides whether to invoke a domain shim; JevShelf does not force host calls.
5. **A private, change-based Git backup** protects installed skills, metadata and target configuration. The backup lives in a separate private repository; it is never published to the public JevShelf repository.

## Current Skillshare library

<small>Recorded 12 October 2026; regenerate the snapshot after installation changes.</small>

| Category | Source skills | Visibility |
|---|---:|---|
| Original global skills | 17 | Direct native discovery, subject to host filters |
| Canonical Aegis engineering skills | 23 | Direct native discovery |
| Additional collection shims | 6 | Direct native discovery |
| `jevify` | 1 | Direct native discovery |
| Academic Research | 5 | Jev-only |
| Emil UI | 15 | Jev-only |
| Sentry specialist tools | 4 | Jev-only |
| lassejlv additions | 3 | Jev-only |
| Matt Pocock curated specialists | 13 | Jev-only (not a second engineering lifecycle) |
| Addy Osmani curated specialists | 7 | Jev-only (not a second engineering lifecycle) |
| ASD-STE100 technical writing | 1 | Jev-only |
| Danium lateral-thinking toolkit | 9 | Jev-only (8 techniques + router) |
| **Total in Skillshare source** | **104** | **47 visible source skills + 57 hidden leaf skills** |

The eight routed collections are **Marketing 50, Critical Thinking 28, Lateral Thinking 9, Decision & Reflection 6, Academic 5, UI 16, Code Specialists 16, and Writing 6**. The former 43-skill Thinking collection is divided into three independently routed domains; see [the thinking collection map](thinking-collections.md). Marketing and Critical Thinking use read-only upstream checkouts, while additional specialist leaves are held in hidden Skillshare `vault-*` groups. Agents discover only the domain entry points.

**Current full list:** [installed.md](installed.md) and [machine-readable installed.csv](installed.csv). The inventory also catalogs all 38 Matt Pocock and 25 Addy Osmani skills: **13 Matt and 7 Addy specialists are hidden Jev leaves**, while their full engineering systems remain inactive.

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
| Use curated Matt, Addy and writing specialists | [engineering-specialists.md](engineering-specialists.md) | On-demand architecture analysis, reflection, quality gates, writing and dependencies |
| Navigate Critical, Lateral, and Decision/Reflection skills | [thinking-collections.md](thinking-collections.md) | Three independent domains, exact counts, purposes and routing commands |
| Update specialist vaults | [vault-management.md](vault-management.md) | Per-group Skillshare updates, audit caveats, rollback |
| Rebuild original source checkouts | [restore-checkouts.sh](scripts/restore-checkouts.sh) | Pinned upstreams, not installed automatically for other users |
| Refresh inventory | `python3 my-skills/scripts/refresh-inventory.py` | Rewrites only `installed.md` and `installed.csv` |
| Jevify and TypeSafe key | [typesafe-api.md](typesafe-api.md) | Existing environment credentials, no stored keys |

Skillshare **v0.25.5** is installed as of 12 October 2026. Keeping it current is a **separate deliberate step**: check `skillshare --version`, review `skillshare upgrade --help`, take a source backup, upgrade the CLI, run `skillshare doctor` and `skillshare sync --dry-run -g`. I don't automatically install unreviewed third-party skill updates just because an upstream repository moved.

## Favorites and references

- [reference skills](references.md): **Distilly** — reserved for opt-in, consent-based Person Profiles, **not installed**.
- **Haft** — considered for long-term engineering decision memory; **not installed**.
- **No Yak Shaving** — reviewed, useful optional proportionality advice; **not installed**.
