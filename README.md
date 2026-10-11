<div align="center">

# JevShelf

**One skill library. Small agent context. Any supported coding harness.**

*A portable, Skillshare-compatible skill shelf with on-demand TypeSafe Jev selection.*

JevShelf **v0.2.0** uses only its own CLI and explicit collection manifests: no old command aliases or implicit personal skill defaults.

[Get started](docs/quickstart.md) · [How it works](docs/architecture.md) · [My Skills](my-skills/README.md) · [Backup guide](my-skills/backups.md)

</div>

---

## Why JevShelf exists

Agent skills are useful until you have too many of them. Different repositories suggest different installers, every coding harness maintains its own discovery directory, and dumping every skill's instructions into context is wasteful. Moving between Codex, Pi, Claude Code, or other Skillshare-enabled hosts should not mean duplicating your entire library, losing backups, or maintaining several copies of the same skill.

**JevShelf separates three jobs:**

| Responsibility | Tool | What happens |
|---|---|---|
| **Own the library** | [Skillshare](https://github.com/runkids/skillshare) | Install/audit/update skills once; sync only the desired native entry points to your configured agents |
| **Find the relevant specialist** | **JevShelf + TypeSafe Jev** | Search one configured collection, receive selected metadata and digests, then lazily read the selected skill |
| **Do the work** | Your coding agent | Follow the selected guidance when applicable, with the user's scope, tool permissions, and verification requirements intact |

### How much context do you save?

Instead of directly exposing 20, 50 or 100 specialist `SKILL.md` files for a domain, expose **one small router skill** (for example, `ui-specialists`). Native discovery gets its name and description. When a relevant request arrives, the agent can call JevShelf to rank only that collection and load the selected instructions with a SHA-256 digest check.

This is **lazy skill loading**, not zero context: agents still see the router's short description, and TypeSafe may receive task text, skill metadata and bounded excerpts during live ranking. JevShelf does **not** silently intercept every prompt or guarantee automatic activation in every model. Your host's native skill discovery is what makes the shim available.

## Run it yourself

```bash
git clone https://github.com/ham-zax/jevshelf.git
cd jevshelf
bash scripts/bootstrap.sh    # Git + uv; installs an isolated Python environment
./bin/jevshelf init         # Create an independent two-skill demo configuration
./bin/jevshelf collections
./bin/jevshelf search --collection writing --mode lexical --task 'summarize meeting notes'
```

The CLI also supports **TypeSafe Jev ranking** using `--mode jev` when `TYPESAFE_API_KEY` or `JEV_API_KEY` is configured. Search returns metadata only. Call `jevshelf load --collection ... --id ... --expected-digest ...` to retrieve the selected skill in bounded pages. Nothing modifies your existing agent skill installation during this demo.

**Bring your own skills:** edit `~/.config/jevshelf/collections.json` to point at one or more local skill directories (including Skillshare-managed source groups). No named collection or personal skill inventory is required by the product.

**Expose it across agents:** generate a small domain shim, import that shim through Skillshare, and sync. Hidden Skillshare source groups such as `vault-*` stay excluded from native target discovery. [Full installation walkthrough →](docs/quickstart.md)

```bash
python3 scripts/create-shim.py --collection ui --name ui-specialists \
  --description 'Use for UI testing and design specialists' --output /tmp/ui-specialists
skillshare install /tmp/ui-specialists --name ui-specialists -g
skillshare sync -g
```

See the walkthrough for prerequisites, target exclusions and ensuring the `jevshelf` command is on the agent's `PATH` **before** syncing. JevShelf's agent instructions are standard `SKILL.md` files; there is no Claude-only plugin to run.

## What you get

- **One configuration per person or project:** a JSON mapping from collection names to one or more directories. Your collections are independent of the maintainer's collections.
- **Two retrieval options:** local lexical/BM25 matching, or semantic TypeSafe Jev selection. Search results are metadata; full skill text is not returned until a separate load.
- **Bounded reads:** file checks, paths and SHA-256 content continuity reject stale skill selections and limit unnecessary instruction loading.
- **Host neutrality:** one portable CLI and ordinary `SKILL.md` shims; let Skillshare deliver links to supported target folders.
- **Backup and recovery:** a command that archives the current Skillshare source (including dirty working files), a Git bundle of committed history, and a target config snapshot. Optional **48-hour** WSL/systemd scheduling.
- **No new process framework:** JevShelf chooses specialist instructions; it doesn't impose TDD, ticket formats, agents, commits, or lifecycle steps on your engineering workflow.

**Backup now:**

```bash
bash scripts/backup-skillshare.sh
```

**Automatic, approximately every other day (Linux/WSL with systemd user services):**

```bash
bash scripts/install-backup-timer.sh
systemctl --user status jevshelf-backup.timer
```

The timer checks twice daily, backing up once at least 48 hours have elapsed. Actual archives are local and **never committed or pushed**. See [the quickstart](docs/quickstart.md#4-keep-it-maintainable-and-recoverable) for details and WSL suspend limitations.

## Product vs. My Skills

This repository intentionally contains **two separate things**:

| | Product: JevShelf | [My Skills →](my-skills/README.md) |
|---|---|---|
| Audience | Anyone with local agent skills | My own working configuration and reference notes |
| Install | `scripts/bootstrap.sh` + `jevshelf init` | Opt-in `my-skills/collections.json` and existing Skillshare source |
| Collections | Any names and any source directories | Marketing, Thinking, Academic, UI, Code Specialists |
| Engineering method | **None required** | Aegis active; Matt / Addy available for swap |
| Storage | Your own local directories | My Skillshare source Git and private local backup snapshots |
| Support docs | [Quickstart](docs/quickstart.md), [architecture](docs/architecture.md) | [Installed catalog](my-skills/installed.md), [favorites](my-skills/references.md), [swap instructions](my-skills/prompts/swap-engineering-system.md), [backups](my-skills/backups.md) |

The **My Skills** folder is a transparent real-world example—not a required preset. It documents my current skill inventory, reference ideas (including Distilly), Skillshare update practices, Aegis swaps, source provenance and snapshots. It contains **no API keys, personal conversation archives, or backup archive contents**.

## Scope and privacy

JevShelf is a CLI and source-loading bridge. It does not install Skillshare, discover credentials automatically on behalf of every user, or change your agent's safety rules. Use TypeSafe Jev only for data you are authorized to send to that service. The original selected third-party skills retain their own licenses and dependencies; they are **not bundled** with this product.

Python 3.13 is used for the provided bootstrap; the core package targets Python 3.11+. Linux/WSL scripts are for that environment; other users can invoke the CLI and build appropriate host adapters on their platforms.

JevShelf uses the pinned [jev-skill-router](https://github.com/himomohi/jev-skill-router) library and is independent of, and not endorsed by, TypeSafe or Skillshare.

**License:** MIT · [Read it](LICENSE).
