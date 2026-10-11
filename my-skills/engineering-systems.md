# Engineering system policy and switching guide

**Current selection (2026-10-11): Aegis.** Keep exactly one of Aegis, Matt Pocock, and Addy Osmani active at a time. The other two are documented candidates, not competing agent instructions.

See [skill-inventory.md](installed.md) and [skill-inventory.csv](installed.csv) for the complete recorded inventory, and [swap-engineering-system.md](prompts/swap-engineering-system.md) for the agent-executable swap request. The swap prompt is **instructions only**; reading it does not authorize a switch. The user must explicitly request a target.

## Responsibilities

- **Skillshare** is the manager: imports audited skill directories from GitHub, stores them in `~/.config/skillshare/skills`, handles group updates and sync to 7 configured targets. Use it for every active engineering system; do not also install a native plugin for the same pack (duplicate discovery).
- **Aegis/Matt/Addy**: exactly one is allowed to direct the engineering lifecycle (requirements → design → implementation → review → completion). Other specialist skills may inform individual steps without replacing the canonical owner's artifacts or handoffs.
- **Claive** remains the worker/model orchestration mechanism; it is not one of these three engineering methods. Existing `claive-orchestration` and `claive-routing-codex` are left intact.
- **Pandora's existing Marketing/Thinking shims** stay independent. This phase does not rename or move them. Jev is not used to mix the three whole engineering frameworks at runtime.
- User/project instructions outrank all optional skill-method suggestions. A small task need not become a lengthy plan, automatic TDD, or mandatory review.

## Current Aegis installation

Upstream: https://github.com/GanyuanRan/Aegis/ (MIT); installed **23** skill directories.

**Official method-pack root:** `~/.codex/aegis` is a Git checkout of Aegis. The official method-pack doctor wrote `~/.config/aegis/config.toml` with `method_pack_root` and `workspace_helper`. The root supplies repo-wide helper scripts/resources. The documented Codex guide normally exposes `~/.agents/skills/aegis → ~/.codex/aegis/skills`; **we instead use Skillshare-generated direct-child symlinks** under every target, because duplicating both views would expose every Aegis skill twice. The Aegis doctor explicitly supports this direct-child compatibility view. Installed skill directory names are prefixed `aegis__`, while skill frontmatter retains its upstream name.

**Skillshare authority:** `~/.config/skillshare/skills/aegis/<skill>/SKILL.md` contains GitHub-sourced skill copies; `~/.codex/skills/aegis__<skill>`, `~/.pi/agent/skills/aegis__<skill>`, and equivalent target paths are symlinks into those copies. Source metadata supports `skillshare update --group aegis -g`. Neither Matt nor Addy is installed in the Skillshare source or host skill directories.

Installed via audited `skillshare install GanyuanRan/Aegis --all --into aegis -g` and `skillshare sync -g`. The **tracked entire Git repository** route was blocked by Skillshare's security audit for script/test helper findings; it was NOT forced or audit-skipped. The regular per-skill installation completed; audit summary: no CRITICAL, 3 HIGH, 2 MEDIUM, 9 LOW, 6 INFO findings (23 skill scan). Treat those warnings as real review items on updates; threshold `CRITICAL` is the user's preexisting policy, not a new relaxation.

Verification:
```bash
cd ~/.codex/aegis
python3 scripts/aegis-doctor.py --write-config --json \
  --discovery-root ~/.codex/skills --discovery-name-prefix aegis__
skillshare status -g
skillshare audit --group aegis -g --no-tui
```
Doctor returned `ok: true`, `workspaceSupport: available`, `configStatus: configured`, `discoveryShapeStatus: current`, and `compatibilityExposureStatus: generated-copy-view-current`.

**Operating Aegis:** Agents discover `using-aegis`, `systematic-debugging`, `writing-plans`, and the other 20 skills through native matching. Aegis owns task framing, code-change governance, reviews and completion when applicable. Aegis `tdd_mode = "off"` by default; TDD and multi-agent workflows are not default blanket requirements. For simple tasks, its fast-path guidance permits direct execution. Aegis's independent `aegis:update` workflow is NOT the manager of these Skillshare copies; prefer the coordinated Skillshare update below.

**Updating both coordinated views:** There are two distinct installed representations (official method-pack Git root and Skillshare-distributed copies). Update in one maintenance window: back up, `git -C ~/.codex/aegis pull --ff-only`, `skillshare update --group aegis --dry-run -g`, `skillshare update --group aegis -g`, then `skillshare sync -g` and rerun the doctor with the prefix. If the doctor detects content mismatch, the installs are from different upstream revisions; do not declare an update successful until aligned. Updates should be deliberately reviewed, not auto-installed behind the user's back.

## Alternative 1: Matt Pocock

Upstream: https://github.com/mattpocock/skills (MIT). At the inspected revision: **38** SKILL.md files in the repository, **27** included in the official plugin manifest. The production/plugin subset is preferable for a fair swap; the remaining 11 include in-progress and miscellaneous skills.

Matt's natural workflow is `setup-matt-pocock-skills` (configure issue tracker/labels/docs) → `grill-with-docs` or `to-spec` → `to-tickets`/triage → `implement` or `implement-spec` → `code-review`/`pr`. Particularly suitable when work is tracked as granular issues, with explicit dependency edges and durable handoffs. Note: `implement` asks for `tdd`, review, and a commit; `to-tickets` assumes the issue tracker setup. These are *this system's* conventions, and would replace—not combine with—Aegis lifecycle conventions.

If chosen, install its **27 manifest skills** via Skillshare in `engineering-matt/` with `--skill` names from `vendor/matt/.claude-plugin/plugin.json` (or read the current upstream manifest); do not add the native Matt plugin separately. The private clone remains available as source/reference, not a second active installation. The first run per codebase may need `setup-matt-pocock-skills`.

## Alternative 2: Addy Osmani

Upstream: https://github.com/addyosmani/agent-skills (MIT). At the inspected revision: **25** skills. Full engineering lifecycle: DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP, with standalone APIs, UI, security, observability, source verification, code simplification and other specialists.

Addy's default lifecycle is more prescriptive, especially spec-driven implementation, test-first work, and pre-merge review. It includes `using-agent-skills`, `spec-driven-development`, `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development`, `code-review-and-quality`, and `shipping-and-launch`. If it becomes canonical, its handoff and gates replace Aegis/Matt rules; do not stack mandatory lifecycle skills from other systems.

If chosen, install all **25 skill** definitions via audited `skillshare install addyosmani/agent-skills --all --kind skill --into engineering-addy -g`, then sync. This deliberately avoids installing its separate plugin commands/hooks/agents; those are not included when Skillshare imports only skills. **Some Addy skills reference repo-level `references/`; the agent performing a swap must check these and arrange read-only access to the source repository or dependencies without enabling duplicate plugins.**

## Switching ownership: non-negotiable boundaries

Only an explicit user request may switch the canonical system. Follow [the swap prompt](prompts/swap-engineering-system.md) to: snapshot and backup → inspect target's official manifest/dependencies → dry-run install/audit → remove old **group** via Skillshare, not individual random symlinks → install one target group → sync all seven targets → verify there is no competing active engineering group → update this inventory and README → commit changes. Keep prior work artifacts; never silently rewrite existing tickets, specs, or PRs into the new system's format. The active system owns **new** lifecycle artifacts; in-flight tasks keep their originating contract unless the user explicitly requests migration. If a stage fails, use Skillshare's trash/backup or recorded Git commit for rollback; do not force past security checks.

## Other installed skills

The 17 original source skills are retained unchanged. Three additional domain shims are now visible (`academic-research`, `ui-craft`, `code-specialists`), while their 24 leaf skills are **Skillshare-managed but hidden from native discovery** under `vault-*/`. See [Jev vault management](vault-management.md). None is an additional canonical engineering system. Candidate Git checkouts remain outside agent discovery.
