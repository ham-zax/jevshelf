---
name: jevshelf-writing
description: Use for serious writing work, planning and composing articles, exploring raw ideas, refining narrative structure, creating stakeholder questionnaires, writing clear agent-facing documentation, or making technical English unambiguous. Select an on-demand writing specialist with JevShelf. For marketing and conversion copy, prefer the existing marketing collection.
---

Before searching, frame a neutral current question and provide `--context` with the product purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar names. Name a preferred framework only when the user explicitly requested it. Request up to three recommendations and load only useful instructions; fewer or none is valid. For an explicitly named skill, `--mode lexical --task "<exact skill name>"` is a local lookup. Keep lexical fallback explicit; never silently replace Jev no-match, uncertainty or error.

# JevShelf Writing — on-demand specialists

Choose only the writing method relevant to the current user's request. Aegis remains the canonical engineering lifecycle; this shim is a writing companion, not a process framework.

The six hidden source skills are:

- **`writing-fragments`** (Matt, experimental) — explore raw material without forcing structure; user-directed writing session.
- **`writing-shape`** (Matt, experimental) — turn existing raw notes into a shaped article.
- **`writing-beats`** (Matt, experimental) — assemble raw material into a sequence of narrative beats, with decisions made interactively.
- **`writing-for-agents`** (Matt) — write precise `SKILL.md`, `AGENTS.md`, instructions and agent-consumed documents. This is also the companion reference for `retro` in `jevshelf-decision-reflection`.
- **`to-questionnaire`** (Matt) — draft an evidence-seeking questionnaire for a specific recipient to resolve open decisions. It may need the user's knowledge of the recipient; do not invent answers.
- **`asd-ste100-skill`** (danyuchn) — simplify ambiguous technical, tool, error, and inter-agent English. Strict STE is *not* the right style for creative fiction or brand copy. Its linter checks structure, not semantic equivalence or certified ASD-STE100 compliance.

1. When the user has a relevant writing task, run `jevshelf search --collection writing --mode jev --task "<focused task>" --context "<brief situation and evidence>" --max-results 3`. This only returns ranked metadata.
2. Load the selected expert's full guidance using `jevshelf load --collection writing --id <selected id> --expected-digest <selected digest>`. Load referenced skill-local resources with the file/offset/digest options as needed.
3. Respect explicit invocation gates: experimental interview/narrative workflows should be selected only when the user asks for exploration, collaborative writing or document production. Do not create files or run scripts merely because this shim was discovered. Use the host's ordinary writing UI for straightforward drafting.
4. If Jev is unavailable, report that and optionally use `--mode lexical` for an explicitly labeled local metadata selection. Do not claim lexical search was semantic Jev selection.
5. Do not load marketing, engineering process, or personal-data profiling skills merely because the request involves writing. Preserve facts, style, user intent and appropriate privacy.
