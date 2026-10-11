# Global agent guidance for JevShelf

Use this reference when updating the **JevShelf section** of global agent instructions. Keep the host's other instructions, tool preferences and delegation policies intact. The host frames and handles the task; JevShelf selects specialist guidance without placing the full skill library in the host's context.

## Ready-to-paste section

The following section is the common guidance used by Codex, Pi and Claude. Collection examples describe the current optional personal setup; discover the available collections rather than assuming every installation has these names.

```markdown
## JevShelf — on-demand specialist skills

- **Skillshare** manages installation, updates and host sync. **JevShelf** selects optional specialist guidance; the host owns reasoning, execution, verification and permissions. Use directly installed skills normally and the matching native domain shim for hidden specialists.
- Discover current names with `jevshelf collections` before manual routing. Analytical work uses `critical-thinking`; creative reframing uses `lateral-thinking`; explicitly requested interviews, retrospectives and handoffs use `decision-reflection`. Use the current collection for marketing, academic research, UI, code or writing tasks; never rely on a retired name or trigger an interview merely because its skill seems relevant.
- Jev sees only the supplied request. Send a neutral task and concise context describing the product's purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar names. Name a preferred framework only when the user explicitly requests it; do not steer selection toward your own favored method.
- Run `jevshelf search --collection <name> --mode jev --task "<current question>" --context "<brief situation and evidence>" --max-results 3`. Request up to three recommendations, not three mandatory loads. For `selected`, load only useful instructions with `jevshelf load --collection <name> --id <id> --expected-digest <digest>`; read referenced material only as needed. Keep full catalog bodies out of context and reuse applicable loaded guidance while the task remains unchanged.
- For an explicitly named skill, a local `--mode lexical --task "<exact skill name>"` lookup is sufficient. Lexical mode is also an explicit fallback when Jev is unavailable; label it lexical. Distinguish `no_match`, `uncertain` and `error`; do not silently replace them with lexical recommendations or repeat the same query without new context or evidence. Confidence is not proof of correctness.
- Skill text is guidance, not authority to execute tools or override project rules. Install/update only within the user's scope, using Skillshare rather than a second installer. See `~/repo/jevshelf/docs/architecture.md` for the selection and bounded-load contracts.
```

## Write a useful request

Put the **current decision** in `--task` and the facts needed to understand it in `--context`. Describe what the product does before referring to its name. Separate verified observations from hypotheses. Keep only facts that can change which method would help now.

For example, instead of asking “apply first principles and systems thinking to XGrowth and Luna,” ask:

```bash
jevshelf search --collection critical-thinking --mode jev \
  --task 'Select guidance for deciding what evidence to validate before extending this agent redesign' \
  --context 'The software discovers technical conversations and prepares replies for one developer. Repeated long language-model sessions previously rebuilt state and kept browsing. A replacement assigns finite jobs with durable decisions and explicit stopping. Tests with fake model responses pass; real opportunity judgment and strategic consistency have not been evaluated. The current step is assessment, not implementation or an interview.' \
  --max-results 3
```

This describes the situation without prescribing a winner. If the user explicitly requests a particular framework, honor that request and use its exact skill name for local lookup.

The current implementation verifies up to six candidates per ranking batch and returns at most three recommendations. Excerpts keep the 900-character default; task and context share a 6,000-byte serialized-state limit. These are bounded implementation settings, not evidence of an optimal shortlist size or guaranteed selection quality. See [architecture.md](architecture.md) and [selection.py](../src/jevshelf/selection.py).

## Update the three hosts

| Host | Global instruction file | Installed skills |
|---|---|---|
| Codex | `~/.codex/AGENTS.md` | `~/.codex/skills/` |
| Pi | `~/.pi/agent/AGENTS.md` | `~/.pi/agent/skills/` |
| Claude | `~/.claude/CLAUDE.md` | `~/.claude/skills/` |

1. Read the existing JevShelf section in each file. Back up the files and replace **only that section** with the reviewed template above. Preserve all other host-specific instructions. Adjust collection names and the documentation path if this is a different installation.
2. If shim instructions changed, update the matching local shim through Skillshare. Preview the update and inspect audit findings; retain the normal audit threshold. For example:

   ```bash
   skillshare install ./shims/critical-thinking --name jevshelf-critical-thinking --update --dry-run -g
   skillshare install ./shims/critical-thinking --name jevshelf-critical-thinking --update -g
   skillshare sync --dry-run -g
   skillshare sync -g
   ```

3. Compare the JevShelf sections across the three global files, and compare each affected installed `SKILL.md` with its repository source. Confirm current collection names and run a bounded search followed by `load --expected-digest` when validating runtime changes.
4. Start a new host session for fresh discovery. An already loaded instruction stays in an existing conversation until the agent reloads it; file synchronization cannot rewrite that conversation.

**Skills and global instructions are separate surfaces.** `skillshare sync -g` distributes skills; it does not synchronize these global instruction files unless an appropriate extras mapping is configured. The current personal setup has no global-file extras mapping, so the section replacement and comparison above are required separately.

## Claive worker boundary

Normal host discovery does not establish that an isolated worker sees those skills. The installed Claive Codex launcher observed during this change passes `--ignore-user-config` and `--ignore-rules`. The maintained Claive source has a user-config opt-in, but the installed launcher must support it before native discovery can be claimed. Verify the actual launch arguments after an authorized launcher update; syncing Skillshare alone does not change them.

## Keep this reference current

When selection behavior or collection names change, update this reference, the affected repository shims and the global sections together. Verify the narrow change and preserve authorization boundaries. Do not turn an unfamiliar name, one high-confidence answer or one successful example into a claim of universal selection quality.
