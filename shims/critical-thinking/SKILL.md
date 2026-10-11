---
name: jevshelf-critical-thinking
description: Use for critical thinking and analytical reasoning: test assumptions against evidence, identify root causes, evaluate uncertainty and risks, examine systems and tradeoffs, consider counterarguments, and make defensible decisions. Select one of 28 reasoning frameworks on demand with JevShelf; not for creative brainstorming or session retrospectives.
---

Before searching, frame a neutral current question and provide `--context` with the product purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar names. Name a preferred framework only when the user explicitly requested it. Request up to three recommendations and load only useful instructions; fewer or none is valid. For an explicitly named skill, `--mode lexical --task "<exact skill name>"` is a local lookup. Keep lexical fallback explicit; never silently replace Jev no-match, uncertainty or error.

# JevShelf — Critical Thinking

This collection holds the **28 original analytical and systems-thinking frameworks** (including first principles, five whys, Cynefin, probabilistic thinking, systems thinking, red teaming, TRIZ and several other mental models). Use it to **analyze or evaluate** an actual question, not to generate divergent creative concepts or manage engineering workflows.

1. `jevshelf search --collection critical-thinking --mode jev --task "<focused analytical question>" --context "<brief situation and evidence>" --max-results 3` (include relevant user context and verified observations).
2. For a selected skill, `jevshelf load --collection critical-thinking --id <returned id> --expected-digest <returned digest>`. Use bounded `--file`, `--offset`, and previous `content_digest` when a selected skill refers to supporting materials.
3. Follow the chosen framework proportionally; preserve user intent and distinguish observed evidence from assumptions. An analytical skill never overrides Aegis or the repository's engineering rules.
4. Treat Jev `no_match`, `uncertain` and API `error` as different results. `--mode lexical` is an explicitly labeled local fallback, not Jev. Do not pretend the selection succeeded when it did not.

For **inventing new directions**, use `jevshelf-lateral-thinking`. For **interviews, wayfinding, retrospectives and handoffs**, use `jevshelf-decision-reflection`.
