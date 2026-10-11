# Skill installation protocol — Skillshare + native discovery + Jev

For favorited but **not installed** skills, see [reference-skills.md](references.md). Use the list as a bookmark, not as permission to install.

**Use for:** `Add this GitHub skill`, `Install these skill(s)`, `Should this be global or project-only?`, `Update this routed collection`, and `Remove a skill`. For the engineering framework **swap**, instead read `my-skills/prompts/swap-engineering-system.md`.

**Owner:** Skillshare manages skill files and GitHub update records. **Aegis** owns the canonical engineering lifecycle. **Jev** selects specialist skills only inside the explicitly routed collections. Codex, Pi, Claude Code and the other targets retain their native skill discovery. Do not build a universal router.

## How to ask an agent

Yes: work from the manager checkout, **not** from a random repository's installation command:

```bash
cd ~/repo/jevshelf
```

Then tell the agent:

> Read `AGENTS.md` and `my-skills/installation-protocol.md`. Evaluate and, if appropriate, install `<GitHub URL or skill name>` through Skillshare. Prefer the existing Jev collection. Preserve Aegis and current target exclusions. Audit, verify loading, update inventory, commit locally, and create a restorable source backup. Do not run the author's separate agent installer as well.

For a **comparison only** or **check this skill** request, inspect and recommend **without installing**. For an app-only skill, work from the **actual app's root** using Skillshare project mode; installing with `-p` while in this manager repo would scope it to the wrong project.

## Decision — which installation class?

| Type | Install with | How agents see it | Selection rule |
|---|---|---|---|
| **Global direct** | Skillshare global source `-g` | One skill name/description in approved target(s) | Use sparingly for frequent, high-value, narrowly differentiated skills |
| **Global Jev-routed** | Skillshare global source `--into vault-<source> -g` | Only existing domain shim (e.g. `ui-craft`, `code-specialists`) | Default for optional specialist libraries and occasional skills |
| **Project-specific** | Skillshare project mode `-p` **from target project root** | Only matching project's agent session | Framework, build, app or team-specific workflow |
| **Harness-specific** | Skillshare import + target filters where possible | Only the required agent's skill directory | Use when skill assumes Codex/Pi/Claude-specific tools; verify support |
| **Plugin / runtime, not standalone SKILL.md** | Evaluate the officially documented native runtime separately | May need a host plugin, MCP, CLI, hook or workspace helper | Do not pretend a Markdown-only copy installs runtime features |

**Multiple classifications can apply.** A skill can be globally stored by Skillshare but *not* globally visible: a `vault-*` group is globally managed and deliberately excluded from agent discovery. Direct visibility should not be confused with global source management.

## Why not run the GitHub install command?

An author may recommend `npx skills add OWNER/REPO --skill NAME`, copying into `.agents/skills`, `claude plugin install`, etc. Those commands are written for users **without our Skillshare manager**. Running an official installer *and* Skillshare on the same skill can create duplicate discovery, two update authorities, and unclear backups.

**Default:** read the author's `SKILL.md` and installation notes, but install the **skills themselves** through `skillshare install`. Preserve references and scripts within the imported skill. If the installation guide actually provisions a necessary non-skill runtime (CLI, server, package, MCP, plugin hooks), document and separately evaluate that dependency; Skillshare cannot replace executable software merely by importing `SKILL.md`.

**Aegis exception:** Aegis's official method-pack Git checkout supplies workspace scripts, while its skill entries are already distributed through Skillshare. Do not run another plugin installer or introduce a second Aegis skill discovery tree.

## Required workflow

### 1. Inspect before installing

- Read the GitHub README, the exact target `SKILL.md` in full, nearby `references/`, `scripts/`, `agents/`, manifests, upstream license notices, and version/commit. Do not execute third-party scripts just to inspect them.
- Check for references escaping the skill's own directory, platform assumptions, binaries, plugins, agent personas, credential requirements, and conflicting engineering instructions.
- Compare against **Aegis**, the existing directly visible skills, and the Jev collections before choosing a destination. Avoid unrequested duplicates and automatic workflow owners.
- Determine intent: **assessment vs explicit installation**, **global vs project**, and **general-purpose vs host-specific**. A simple user request should not automatically activate multiple skills.
- Record names, upstream URL, pinned/observed revision, dependency list, destination collection, and selection rationale.

### 2. Preview and audit with Skillshare

Before global mutations, inspect both Git trees and make a source checkpoint if clean:

```bash
git -C ~/repo/jevshelf status --short
git -C ~/.config/skillshare/skills status --short
cd ~/repo/jevshelf
bash scripts/backup-skillshare.sh
```

The backup script requires a clean committed Skillshare source and makes a Git bundle of its actual contents and a snapshot of `~/.config/skillshare/config.yaml`. A target-folder backup alone cannot recover source files backed by merge-mode symlinks.

For a **routed** global skill, substitute the actual source and specific leaf names:

```bash
skillshare install OWNER/REPO --skill NAME --kind skill --into vault-SOURCE --dry-run -g
skillshare install OWNER/REPO --skill NAME --kind skill --into vault-SOURCE -g
```

Prefer `--branch <reviewed commit>` on initial install when supported. Use a stable source group with upstream GitHub provenance so `skillshare update --group vault-SOURCE -g` works. Import **only** approved leaves; do not `--all` indiscriminately.

For a **direct** global skill, install with `skillshare install OWNER/REPO --skill NAME --kind skill -g`, respecting existing target exclusions. For an actual project-specific install, `cd /path/to/the/target/project` and use `skillshare install OWNER/REPO --skill NAME --kind skill -p` followed by project-scoped sync. Do not use `-p` in this manager checkout unless that checkout itself is the target.

Never silently use `--force`, `--skip-audit`, or a lower blocking threshold. A critical scanner finding requires inspection of the exact source excerpt, a documented safety decision, and the user's authorization to override **if necessary**. Some defensive security documents deliberately quote bad instructions, which can trigger false positives; this is not permission to ignore other findings.

### 3. Route to an existing domain, without new startup noise

The standard routed groups are:

| Skillshare source | Native visible shim | Jev CLI collection |
|---|---|---|
| `vault-academic/` | `academic-research` | `academic` |
| `vault-emil/` | `ui-craft` | `emil` |
| `vault-sentry/` | `code-specialists` | `sentry` |
| `vault-lassejlv/` | **No additional shim** | Selected source skills are merged into `emil` or `sentry` by explicit allowlist |
| `vault-taste/` | **No additional shim** | `design-taste-frontend` is included in `emil` / `ui-craft` |

Existing Marketing and Thinking collections retain their current paths and shims. **Aegis remains canonical**; a Sentry, lassejlv or Emil skill can advise on a technique without requiring a new plan/ticket/commit/review lifecycle.

New `vault-*` groups must remain excluded in **every** configured Skillshare target. Check `~/.config/skillshare/config.yaml` and `skillshare sync --dry-run -g` before syncing. Do **not** add a new global shim for every leaf.

The CLI uses `_collection_roots` in `src/jevshelf/cli.py` to build a collection from specific source roots; new leaves may require an explicit allowlisted path. Update the *existing* shim description only if a new capability must be discoverable. Search returns metadata, then `load --expected-digest` returns bounded full text. Preserve scripts and reference files within the leaf's original directory; external repo resources need an explicitly safe reader, not arbitrary `../` traversal.

### 4. Verify behavior, scope and restoration

- Run `jevshelf collections`; confirm the new leaf is indexed **once** and unrelated collections remain unchanged.
- Run a focused **lexical metadata** lookup. When Jev is configured and the request authorizes a live probe, run a live `--mode jev` request on a representative task and verify `selected`, `no_match`, or `uncertain` honestly.
- Call `jevshelf load --collection NAME --id <returned id> --expected-digest <returned digest>`. Verify that referenced text scripts and files are present; only execute a helper if the user request authorizes it.
- Run focused existing project tests when implementation code changed; use a stronger integration test when the changed behavior warrants it. Do not impose blanket TDD.
- Run `skillshare sync --dry-run -g` and inspect changes, then `skillshare sync -g`. Verify allowed direct shims appeared and **no `vault-*` leaves** appeared in any target directory.
- Refresh `my-skills/installed.csv` and `my-skills/installed.md` with `python3 my-skills/scripts/refresh-inventory.py`, and update `my-skills/vault-management.md` with any new group, limitations, findings, and provenance.
- Commit only intended changes to the **project repository** and the **Skillshare source Git repository**, separately; no push without a user request. After Skillshare source commit, run `bash scripts/backup-skillshare.sh` and `git bundle verify`. The bundle must include the hidden leaves, not just the target symlinks.

### 5. Report the result and stop

Report: source and exact names, selected scope and Jev collection, installation/update/audit status, counts before/after, verification evidence, target exclusions, Git commit hashes, recoverable backup path, and any unverified runtime requirements. If an install is blocked or a runtime is missing, say what is functional and what isn't; never claim full implementation based on a successful file copy.

## For this particular repository: accepted decisions

- **One canonical engineering method:** Aegis. Matt and Addy remain offline alternatives.
- **lassejlv skills agreed for Jev routing:** `no-vibe-code` joins `emil`; `backend-security-audit` and `minimize-api-responses` join `sentry`. They are imported in `vault-lassejlv/` but only exposed through existing `ui-craft` and `code-specialists` shims.
- **`no-yak-shaving`:** worthwhile but overlaps Aegis and existing Codex principles. **Not automatically installed**. If later requested, treat as opt-in implementation/review advice rather than another mandatory lifecycle owner.
- **`create-ui-kit-from-website` and `project-roadmap`:** optional, not approved for automatic installation.

- **Jevify** (`altryne/jevify`) is an approved **direct global skill**; it supplies Jev usage patterns and helpers but is not itself a second router. **Taste** (`Leonxlnx/taste-skill/skills/taste-skill`) is an approved **Jev-hidden UI skill**, not a second global shim.
