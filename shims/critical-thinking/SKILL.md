---
name: jevshelf-critical-thinking
description: Use for critical thinking and analytical reasoning: test assumptions against evidence, identify root causes, evaluate uncertainty and risks, examine systems and tradeoffs, consider counterarguments, and make defensible decisions. Select one of 28 reasoning frameworks on demand with JevShelf; not for creative brainstorming or session retrospectives.
---

# JevShelf — Critical Thinking

This collection holds the **28 original analytical and systems-thinking frameworks** (including first principles, five whys, Cynefin, probabilistic thinking, systems thinking, red teaming, TRIZ and several other mental models). Use it to **analyze or evaluate** an actual question, not to generate divergent creative concepts or manage engineering workflows.

1. `jevshelf search --collection critical-thinking --mode jev --task "<focused analytical question>" --max-results 2` (include only essential user-provided context).
2. For a selected skill, `jevshelf load --collection critical-thinking --id <returned id> --expected-digest <returned digest>`. Use bounded `--file`, `--offset`, and previous `content_digest` when a selected skill refers to supporting materials.
3. Follow the chosen framework proportionally; preserve user intent and distinguish observed evidence from assumptions. An analytical skill never overrides Aegis or the repository's engineering rules.
4. Treat Jev `no_match`, `uncertain` and API `error` as different results. `--mode lexical` is an explicitly labeled local fallback, not Jev. Do not pretend the selection succeeded when it did not.

For **inventing new directions**, use `jevshelf-lateral-thinking`. For **interviews, wayfinding, retrospectives and handoffs**, use `jevshelf-decision-reflection`.
