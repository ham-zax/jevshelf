---
name: jevshelf-lateral-thinking
description: Use for lateral thinking, creative problem reframing, original product ideas, stuck brainstorming, assumption inversion, provocation, random stimuli, concept fans, analogy, SCAMPER, Six Thinking Hats, and reverse brainstorming. Select one of nine hidden Danium creativity skills on demand, not for debugging or implementing code.
---

Before searching, frame a neutral current question and provide `--context` with the product purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar names. Name a preferred framework only when the user explicitly requested it. Request up to three recommendations and load only useful instructions; fewer or none is valid. For an explicitly named skill, `--mode lexical --task "<exact skill name>"` is a local lookup. Keep lexical fallback explicit; never silently replace Jev no-match, uncertainty or error.

# JevShelf — Lateral Thinking

This collection exposes the **`lateral` router and eight creative techniques** from `danium/lateral-thinking`: `random-stimulus`, `provocation`, `inversion`, `concept-fan`, `analogy`, `scamper`, `six-hats`, and `worst-idea`. Choose **one technique per creative exploration**. These methods expand possibilities, not establish facts or authorize implementation.

1. `jevshelf search --collection lateral-thinking --mode jev --task "<focused creative challenge>" --context "<brief situation and evidence>" --max-results 3`.
2. `jevshelf load --collection lateral-thinking --id <selected id> --expected-digest <selected digest>` for the chosen instructions.
3. The upstream `lateral` router recommends reading `../<technique>/SKILL.md`, but JevShelf deliberately forbids sibling traversal. When `lateral` chooses a technique, issue a **second** search in `lateral-thinking` naming that exact technique, then digest-load its own returned ID. Never guess IDs, cross directories or run a second technique in the same pass. If no matching technique is returned, explain the limitation instead of silently substituting one.
4. Preserve honest abandonments and leave selection of ideas to the user. Do not use creativity instructions as a substitute for debugging, code review, security analysis or production engineering. Treat API errors and `uncertain`/`no_match` honestly; label any `--mode lexical` fallback.

For evidence-based reasoning use `jevshelf-critical-thinking`. For strategic interviews and retrospectives use `jevshelf-decision-reflection`.
