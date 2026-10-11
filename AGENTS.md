# JevShelf repository instructions

This repository contains **two independent surfaces**:

- **Portable product** (`src/jevshelf`, `docs`, `examples`, `scripts`, `bin/jevshelf`): general-purpose Jev skill selection and Skillshare interoperability. Do not hard-code the maintainer's collection names, user paths or TypeSafe keys into product defaults.
- **My Skills** (`my-skills`): an optional real-world configuration, inventory, reference list, and engineering swap procedure. Never treat this personal setup as a dependency for other users.

Before installing new skills or switching the maintainer's active engineering pack, read `my-skills/installation-protocol.md` and `my-skills/prompts/swap-engineering-system.md` respectively. An exploratory skill review does not authorize installation. Keep Aegis the current maintainer's canonical engineering method unless explicitly asked to switch.

Keep Skillshare the installation/audit/update/sync authority, and use JevShelf only for lazy specialist selection. Never push API keys or the actual local Skillshare source Git bundle or working-tree backup archives. Commit or publish changes only when requested. Follow repository-local tests and the task's stated verification requirements; use only the public `jevshelf` CLI entry point.
