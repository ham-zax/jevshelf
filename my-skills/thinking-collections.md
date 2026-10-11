# Thinking skills — three focused JevShelf collections

The former one-size-fits-all `thinking` collection (43 skills) is **split, not duplicated**. A user or host chooses one small domain shim and JevShelf only searches the relevant source roots. The actual specialist files remain in their existing read-only source checkout or hidden Skillshare vaults. Aegis remains the canonical engineering framework; no separate thinking lifecycle is required.

| Collection | Native discovery shim | Source and membership | Use when |
|---|---|---|---|
| `critical-thinking` | `jevshelf-critical-thinking` | **28** original `vendor/thinking/skills` frameworks | Evaluate evidence, challenge assumptions, find root causes, reason about risks and systems, reach defensible conclusions |
| `lateral-thinking` | `jevshelf-lateral-thinking` | **9** hidden `vault-lateral` leaves: `lateral` router plus eight techniques | Generate novel options, reframe creative challenges, escape repetitive brainstorming |
| `decision-reflection` | `jevshelf-decision-reflection` | **6** hidden Matt Pocock leaves: `grilling`, `grill-with-docs`, `domain-modeling`, `wayfinder`, `retro`, `handoff` | Explicit interactive interviews, long-range decision planning, end-of-session reflections, handoffs |
| **Total** | **3 native shims** | **43 distinct specialists** | The correct domain determines which small catalog is searched |

## Selection examples

Use only the relevant collection; the full instructions are loaded **after** semantic selection, with a digest that guards against changes between the two reads.

```bash
jevshelf search --collection critical-thinking --mode jev --task 'Evaluate competing root causes and uncertainty'
jevshelf search --collection lateral-thinking --mode jev --task 'Use concept fan to rethink our product onboarding'
jevshelf search --collection decision-reflection --mode jev --task 'Conduct a retrospective of this coding session and propose improvements'
# Then read the chosen skill using the returned id and digest:
jevshelf load --collection <one-of-the-three> --id <returned-id> --expected-digest <returned-digest>
```

The `lateral` router is itself one of the nine skills. When it chooses a technique, request that technique with a second search **within `lateral-thinking`** and digest-load its skill body; do not follow upstream `../` sibling-relative references. Its unrelated `post` writing skill is not installed.

`retro` proposes improvements to tooling, agent instructions and guardrails, but **does not autonomously rewrite its own rules**. `wayfinder` and `grill-with-docs` remain explicit-invocation workflows. Do not substitute creative divergence for debugging, reviewing code or implementing a fix.

The old `jevshelf-thinking` shim and `thinking` collection name were retired in the clean migration. Start a new host session after Skillshare sync so native skill discovery refreshes. The source inventory and counts are recorded in [installed.md](installed.md) and the local configuration in [collections.json](collections.json).
