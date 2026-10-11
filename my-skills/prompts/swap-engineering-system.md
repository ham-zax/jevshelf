# Reversible engineering system swap — agent prompt

Use this prompt only when the user explicitly asks to change the canonical engineering system to **aegis**, **matt**, or **addy**. Reading this file is not authorization to switch. Read my-skills/engineering-systems.md and my-skills/installed.md first.

## Objective

Exactly ONE of the three engineering systems should be active in Skillshare's global source and all seven synced agent targets. Keep the 17 baseline skills, existing target exclusions, Claive and the Marketing/Thinking shims unchanged. Keep upstream clones outside agent discovery; do not add duplicate native plugins/hooks.

## Step 1 — Inspect and prepare

- Check: skillshare status ; skillshare list --json -g ; skillshare sync --dry-run -g
- Check both local Git working trees: ~/.config/skillshare/skills and ~/repo/jevshelf. Don't overwrite unrelated changes.
- Record current engineering group(s), source Git HEAD, target symlinks, and a backup or rollback path.
- Only three engineering group names are in scope: aegis, engineering-matt, engineering-addy.
- NEVER run skillshare uninstall --all, --force, --skip-audit, git reset --hard, git clean, or delete arbitrary agent directories.
- If the target is already the only active group, check it and stop rather than reinstalling.

## Step 2 — Preview exact target install

**Aegis** (23 upstream skills; official root separately supplies helper scripts):

~~~bash
skillshare install GanyuanRan/Aegis --all --kind skill --into aegis --dry-run -g
~~~

**Matt Pocock** (the officially exposed 27 skill paths in the checked-in plugin manifest, not all 38 repository files):

~~~bash
manifest="$HOME/repo/jevshelf/vendor/matt/.claude-plugin/plugin.json"
# If missing, obtain a fresh official checkout outside agent skill directories first.
names="$(python3 - "$manifest" <<'PY'
import json,sys
print(','.join(x.rstrip('/').split('/')[-1] for x in json.load(open(sys.argv[1]))['skills']))
PY
)"
skillshare install mattpocock/skills --kind skill --skill "$names" --into engineering-matt --dry-run -g
~~~

**Addy Osmani** (25 skills only; not agents, hooks, or lifecycle plugin commands):

~~~bash
skillshare install addyosmani/agent-skills --all --kind skill --into engineering-addy --dry-run -g
~~~

Review the correct skill counts and source versions. For Addy, check references to repo-level shared checklists and retain the corresponding read-only source checkout. If audit blocks, STOP. Do not bypass.

## Step 3 — Remove old system and activate chosen one

1. Preview uninstall for each installed *opposing* group, e.g. skillshare uninstall --group aegis --dry-run -g, or engineering-matt / engineering-addy. Never uninstall outside those groups.
2. Remove only the opposing group(s) using skillshare uninstall --group GROUP -g. This moves files to Skillshare trash with rollback support.
3. Repeat the *chosen* installation command from Step 2 without --dry-run. For Matt reuse the manifest-derived names.
4. Run skillshare sync --dry-run -g, inspect expected removals/additions, then skillshare sync -g.
5. Verify source has one active engineering group and all seven configured target directories contain only that engineering system. Confirm no duplicate native plugin, package or symlink exposes the old one.
6. If switching TO Aegis, keep the Git method-pack checkout at ~/.codex/aegis, checking out the version consistent with the Skillshare imported skills. From that checkout run:
~~~bash
python3 scripts/aegis-doctor.py --write-config --json --discovery-root ~/.codex/skills --discovery-name-prefix aegis__
~~~
Require ok=true, workspaceSupport=available, configStatus=configured. Do not ALSO create ~/.agents/skills/aegis, which would expose duplicates.
7. If switching AWAY from Aegis, the inactive Git checkout/config may remain for rollback, but it must not be in any skill-discovery path. Do not invoke its updater while inactive.
8. With Matt, use setup-matt-pocock-skills when an actual project needs issue tracker and ticket label conventions. With Addy, its full lifecycle takes over new specs, implementations and reviews. Never combine two different task workflow authorities. Existing in-flight tickets/docs keep their prior format unless the user explicitly authorizes migration.

## Step 4 — Verify, document, commit

~~~bash
skillshare status
skillshare list --json -g
skillshare sync --dry-run -g
skillshare audit --group ACTIVE_GROUP --no-tui -g
~~~

Update my-skills/engineering-systems.md with the new chosen canonical system, my-skills/installed.csv with actual installed and inactive entries, and my-skills/installed.md with the status summary. Commit the project files and the global Skillshare source repository as separate *local* Git commits. Do NOT push.

If any step fails, restore the previous group using Skillshare backup/trash or recorded source metadata, re-sync and recheck before claiming success. Report: before → after, exact skill counts, removed groups, preservation of baseline 17, warnings and audit outcome, target link verification, Aegis doctor if applicable, rollback path, and both commit hashes.
