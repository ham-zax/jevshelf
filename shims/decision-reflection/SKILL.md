---
name: jevshelf-decision-reflection
description: Use when explicitly asked to grill or deeply clarify decisions, examine a design through an interview, plan a multi-session initiative with wayfinding, reflect on a completed coding session (retro), or produce an agent handoff. Select from six on-demand Matt Pocock decision and reflection skills without activating his full engineering lifecycle.
---

Before searching, frame a neutral current question and provide `--context` with the product purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar names. Name a preferred framework only when the user explicitly requested it. Request up to three recommendations and load only useful instructions; fewer or none is valid. For an explicitly named skill, `--mode lexical --task "<exact skill name>"` is a local lookup. Keep lexical fallback explicit; never silently replace Jev no-match, uncertainty or error.

# JevShelf — Decision & Reflection

Six optional Matt Pocock specialists: `grilling`, `grill-with-docs`, `domain-modeling`, `wayfinder`, `retro`, and `handoff`. These guide **interactive design decisions and reflection**, not every code-writing task. Aegis remains the sole canonical engineering workflow.

1. `jevshelf search --collection decision-reflection --mode jev --task "<focused interview, planning, reflection or handoff task>" --context "<brief situation and evidence>" --max-results 3`.
2. Load each selected ID using `jevshelf load --collection decision-reflection --id <id> --expected-digest <digest>`, optionally bounded pages of skill-local references.
3. `grill-with-docs` depends on `grilling` and `domain-modeling`; `wayfinder` uses `grilling`, `domain-modeling` and a configured issue tracker. Search/load the required skills independently in this collection. Do not create tickets or separate `GLOSSARY.md` if Aegis already has authoritative project context without approval.
4. `retro` reviews the current or specified session and **proposes** environment, navigation and guardrail improvements, using `writing-for-agents` from the separate Writing collection if appropriate. Reflection **never authorizes** automatic changes to global skills, CI, project rules, or self-modification; review suggestions with the user first. `handoff` should be concise and omit secrets.
5. Distinguish Jev errors and low confidence from selected results. Label `--mode lexical` clearly if used.

For analytical frameworks use `jevshelf-critical-thinking`; for creative idea generation use `jevshelf-lateral-thinking`.
