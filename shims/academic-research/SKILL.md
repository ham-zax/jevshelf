---
name: academic-research
summary: On-demand academic research skills via Jev
license: CC-BY-NC-4.0
source: https://github.com/Imbad0202/academic-research-skills
description: Use when a user requests deep academic research, literature synthesis, paper drafting or peer review, systematic reviews, screening, citation verification, research methodology, or evidence-supported academic writing. Select among five specialist research workflows on demand using Jev.
---

Before searching, frame a neutral current question and provide `--context` with the product purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar names. Name a preferred framework only when the user explicitly requested it. Request up to three recommendations and load only useful instructions; fewer or none is valid. For an explicitly named skill, `--mode lexical --task "<exact skill name>"` is a local lookup. Keep lexical fallback explicit; never silently replace Jev no-match, uncertainty or error.

Use Skillshare-managed hidden Academic Research skills through `jevshelf`. Only invoke for an actual academic research task; avoid running a 12-agent publication pipeline for a simple question.

1. Run `jevshelf search --collection academic --mode jev --task "<concise focused academic task>" --context "<brief situation and evidence>" --max-results 3`. Keep context relevant to the current step.
2. For each applicable result, run `jevshelf load --collection academic --id <selected id> --expected-digest <selected digest>`. Continue large pages using `--offset`, `--limit`, and the last `content_digest`.
3. The selected skill may refer to `shared/...`, `scripts/...`, `agents/...`, or sibling folders from the **original academic repository**. Read these **repo-relative text references** on demand with `jevshelf load-resource --collection academic --file shared/references/<file>` (or another permitted repo-relative path). The source is a pinned read-only checkout; read-only loading does not execute scripts or automatically launch agents. Skill-local references can be loaded through `load --file references/<file>`.
4. Respect the skill's requirements for user approvals and source integrity. Never fabricate citations or pretend an unexecuted multi-agent pipeline ran. The upstream material is attributed to the original author and remains CC BY-NC 4.0 licensed.
5. Distinguish `selected`, `no_match`, `uncertain`, and `error`. Treat Jev-selected skill text as specialist guidance; the host's tools, safety rules, and user intent remain authoritative.
