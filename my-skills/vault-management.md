# Skillshare-managed Jev collections

**Current configuration:** Five Jev collections: Marketing 50, Thinking 28, Academic Research 5, UI 17 (Emil + lassejlv + Taste), code specialists 6 (Sentry + lassejlv). Aegis remains the sole active engineering lifecycle system; Haft, Matt Pocock, and Addy Osmani are not installed as competing workflows.

## Source of truth and exposure

The 28 managed hidden leaves reside directly under the Skillshare source library, with remote GitHub provenance recorded in Skillshare's metadata:

| Collection / CLI name | Managed Skillshare source group | Source | Pinned bootstrap revision |
|---|---|---|---|
| `academic` | `vault-academic/` | Imbad0202/academic-research-skills | `d1e51716e53fc371727ea6164dd709fc8ea28c97` |
| `emil` | `vault-emil/` | emilkowalski/skills | `2d228630ba1446365f614a108cb8252f1feda202` |
| `sentry` | `vault-sentry/` | getsentry/skills | `d18b7aa8ba878354e5c348310230e652f7690f9c` |
| `emil` and `sentry` | `vault-lassejlv/` | lassejlv/skills | `07d8ada0d9cc14baa814525e29fabc4682c7c370` |
| `emil` | `vault-taste/` | Leonxlnx/taste-skill | `717446e07a78d4e6d7918b1fde1a263378eebac9` |

All seven existing Skillshare targets have an extra **`vault-*`** exclusion. Original exclusions remain intact. Only the three discoverable, locally managed shims `academic-research`, `ui-craft`, and `code-specialists` were added to target skills. The previous `pandora-marketing` and `pandora-thinking` shims remain as before. The command `pandora-skills` uses Skillshare's *source* group to read metadata and selected skill bodies, not a separately copied hidden vault.

The original Sentry subset remains exactly `find-bugs`, `code-simplifier`, `security-review`, and `skill-scanner`. The other Sentry skills are not routed. The `sentry` Jev collection additionally includes `backend-security-audit` and `minimize-api-responses` from Skillshare group `vault-lassejlv`; `emil` adds `no-vibe-code` from that group and `design-taste-frontend` from `vault-taste/`. **There is no additional native Jev shim; none of these four supplementary routed leaves is directly installed.**

## Managed updates

These are ordinary Skillshare-installed, source-provenanced skills; no plugins or host-specific agents were installed. Update one collection at a time after reviewing upstream changes:

```bash
skillshare update --group vault-emil --dry-run -g
skillshare update --group vault-emil -g
skillshare audit --group vault-emil -g --no-tui
skillshare sync --dry-run -g
skillshare sync -g
python3 ~/repo/jevshelf/scripts/refresh-skill-inventory.py
```

Apply the same steps to `vault-sentry`, `vault-academic`, `vault-lassejlv`, or `vault-taste`. If an update adds new Sentry skills, **do not** add them: the router only permits the original four. No default auto-update has been enabled.

### Academic supporting files

Academic's five Skillshare-managed skill folders reference shared resource trees (`shared/`, `scripts/`, `agents/`, and sibling academic skill files). Skillshare's per-skill installer does not carry the whole repository tree. The original **pinned** Git checkout at `~/repo/jevshelf/vendor/academic` therefore remains the read-only resource provider. Run `pandora-skills load-resource --collection academic --file shared/references/<name>.md` to page safely through these text resources, and continue with the returned content digest. This command does not execute scripts or dispatch agents.

Every academic resource read first verifies that all five installed `SKILL.md` source files exactly match that checkout. If Skillshare updates academic leaf files while the pinned checkout stays old, this check fails explicitly. Align the checkout to the same reviewed upstream revision (and update the pinned SHA in `scripts/bootstrap.sh`) before resuming shared resource reads. This prevents mixing incompatible versions. The GitHub repo and recorded SHA make these resources recoverable even if a local checkout disappears.

### Reviewed audit findings

Security scans flagged **six** skills (not the three shims). The exact blocked passages were manually examined before accepting individual findings. They describe *attacks to ignore or detect* and are examples inside defensive guidance, not an attempt by the source author to override agent instructions:

- Academic: `academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md` and other reviewer agents quote unsafe directives as *untrusted manuscript data*. Audit accepted 8 finding records (9 CRITICAL occurrences).
- Emil: `break-ui`, `find-animation-opportunities`, `improve-animations` include the example `ignore previous instructions` to tell agents to treat repository content as data. One CRITICAL finding acceptance each.
- Sentry: `security-review/references/modern-threats.md` quotes a vulnerable prompt injection example; `skill-scanner/references/prompt-injection-patterns.md` lists malicious patterns for *detection*. 1 and 14 accepted finding records respectively.

Only these six selected installs used Skillshare's `--force` reviewed acceptance. Other leaves installed under the unchanged standard CRITICAL threshold. **The findings remain visible, and they can include additional HIGH or lower-severity findings that have not been fully analyzed.** Acceptance is not a certification that source code is harmless; scripts from skill files are not automatically executed by the router. Reassess new or changed findings before upgrades. No global audit threshold changes, blanket ignore rules, or unattended execution permissions were applied.

## Backups and restoration

For new skills, follow [the installation protocol](installation-protocol.md) and the repository root `AGENTS.md`.

**Important:** `skillshare backup` snapshots **local target folders**, not the real contents of Skillshare's source symlinks in merge mode. Thus a target backup alone is *not* a backup of Jev source collections.

The durable Skillshare-managed source is Git-tracked under `~/.config/skillshare/skills`. After a successful installation, commit `.metadata.json`, the three shim directories, and the `vault-*/` source groups. Keep a separate **Git bundle** of the committed source under `~/.local/share/skillshare/backups/`, along with a snapshot of `~/.config/skillshare/config.yaml` (which records the target filters). Keep the project Git checkout and pinned vendor repository SHAs for the full research support tree.

Suggested post-update recovery checkpoint (or simply run `bash scripts/backup-skillshare-vault.sh` after committing the Skillshare source):

```bash
stamp=$(date +%Y%m%d-%H%M%S)
backup="$HOME/.local/share/skillshare/backups/jev-vault-$stamp"
mkdir -p "$backup"
cp -p "$HOME/.config/skillshare/config.yaml" "$backup/config.yaml"
git -C "$HOME/.config/skillshare/skills" bundle create "$backup/skillshare-source.bundle" --all
git -C "$HOME/.config/skillshare/skills" bundle verify "$backup/skillshare-source.bundle"
```

To restore, inspect/clone the bundle into a *separate* staging directory, inspect `.metadata.json` and skill content, then deliberately restore the desired committed source and config snapshot; run `skillshare sync -g`. Don't run destructive Git resets or blanket overwrites on a dirty Skillshare tree. Academic resource checkout is recreated using `bash scripts/bootstrap.sh` from the pinned upstream commit. A bundle of the academic checkout is optional for fully offline recovery.

## Verification evidence (2026-10-12)

- The initial catalog indexed 50/28/5/15/4 skills; after importing three lassejlv leaves, it indexes **50/28/5/17/6** (Marketing/Thinking/Academic/UI/Code Specialists).
- Live Jev calls selected `sr-screener`, `break-ui`, `skill-scanner` from the three new collections.
- Each selected skill passed SHA-256-checked bounded `load`.
- An academic shared resource was read and content-digest pagination worked.
- The initial Skillshare sync linked only three additional shims to all seven agent targets; after the lassejlv import, **28** leaves remain in source only.
- Existing Aegis and baseline Skillshare skills and exclusions were retained.

## lassejlv additions (2026-10-12)

The official repository `https://github.com/lassejlv/skills` recommended `npx skills add`. We imported only `no-vibe-code`, `backend-security-audit`, and `minimize-api-responses` using Skillshare's own `install --skill ... --into vault-lassejlv` instead, pinned initially to commit `07d8ada0`. The source skill directories (including `slop-check.mjs` and security audit references) stay intact. The Skillshare audit did not block these imports; only LOW/INFO findings were reported. They are managed using `skillshare update --group vault-lassejlv -g` and backed up in the Skillshare source Git bundle.

The `vault-*` exclusion already covers the new group in all seven targets. The `ui-craft` shim now advertises design-quality review and the `code-specialists` shim now advertises API response minimization and backend audits, without introducing more native skills.

The `no-yak-shaving` skill was inspected in full, but not installed; its proportional engineering approach overlaps Aegis and the existing global engineering guidelines. It may be added as **optional advice** upon explicit request, not as a mandatory second engineering system.

## Jevify (direct) and Taste (Jev-routed) — 2026-10-12

- **Jevify** (`jevify`) installed normally through Skillshare from `https://github.com/altryne/jevify`, pinned import commit `11f36f8d548cf5020a20e5eb548f21c3d7181a17`. It is one additional globally visible skill, with its original `scripts/`, `references/`, `assets/` and metadata intact. It is not a universal prompt router or host hook. It instructs agents when bulk semantic scanning may be appropriate and includes a Python standard-library-only helper. It does not require a second plugin installation.
- **Taste** (`design-taste-frontend`) installed from `https://github.com/Leonxlnx/taste-skill`, pinned to `717446e07a78d4e6d7918b1fde1a263378eebac9`, under hidden source group `vault-taste/taste-skill/`. Only the original `taste-skill` v2 (experimental) leaf was imported, **not the other 12 skills in that repository**. It joins Jev `emil` / visible shim `ui-craft` for aesthetic direction of landing pages, portfolios and redesigns. The source excludes dense dashboards, admin panels, and multi-step forms.
- Skillshare's first Jevify install was **blocked by two CRITICAL prompt-injection matches** in quoted adversarial evaluation examples (`assets/question-cases.json:36`, `references/worked-question-pack.md:106`). After examining both excerpts, those two specific finding records were accepted through a reviewed `--force` import. Audit also reported a HIGH synthetic-key assignment in `scripts/test_jev_client.py` and lower-severity URL/command findings. The global CRITICAL threshold was **not** changed; an acceptance is not proof that all scripts are safe.
- Taste imported under the normal audit policy with two HIGH findings (`SKILL.md:133` DNS heuristic and `SKILL.md:892` agent directive heuristic) and an INFO interpreter warning. These were not blocking and remain visible for review.
- `vault-*` exclusions already protect all seven targets. Aegis remains canonical. Updating uses `skillshare update --group vault-taste -g` for Taste and `skillshare update jevify -g` for Jevify, with dry-run, audit, test and Git backup.

**Jevify TypeSafe environment:** See [Jevify TypeSafe setup](jevify-typesafe.md). The login shell exports both `JEV_API_KEY` and `TYPESAFE_API_KEY` with the same value, using one key declaration in `~/.bashrc`. Jevify helpers may run directly. The `jevify-typesafe` wrapper remains optional for processes that did not inherit the environment. No key value is committed to the project or Skillshare source. After updates, recheck the local skill note.
