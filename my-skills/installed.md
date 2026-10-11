# Skill inventory

Snapshot of the installed Skillshare global source and the three engineering system libraries.
Regenerate with: python3 my-skills/scripts/refresh-inventory.py (requires Skillshare CLI).
The companion CSV is the complete row-level ledger.

- **Current canonical engineering system:** Aegis
- **Installed Skillshare source entries:** 94
- **Visible/source skills:** 45 (includes 17 original, 23 Aegis, 4 additional domain shims, and jevify)
- **Managed hidden Jev leaves:** 49 (Academic 5, Emil 15, Sentry 4, lassejlv 3, Taste 1, Matt specialists 13, Addy specialists 7, Writing STE 1)
- **Aegis:** 23 installed of 23 available
- **Matt Pocock:** 0 installed of 38 available; 27 were in the inspected official plugin
- **Addy Osmani:** 0 installed of 25 available

## Installed skills

| Collection | Skillshare skill name | Source |
|---|---|---|
| baseline | academic-research | jevshelf:shims/academic-research |
| baseline | archify | local |
| baseline | arm-webharness | local |
| baseline | cachebeat | local |
| baseline | claive-orchestration | local |
| baseline | claive-routing-codex | local |
| baseline | code-specialists | jevshelf:shims/code-specialists |
| baseline | codebase-memory | local |
| baseline | find-skills | local |
| baseline | impeccable | local |
| baseline | jevify | github.com/altryne/jevify |
| baseline | jevshelf-marketing | jevshelf:shims/marketing |
| baseline | jevshelf-thinking | jevshelf:shims/thinking |
| baseline | jevshelf-writing | jevshelf:shims/writing |
| baseline | khiip | local |
| baseline | open-websearch | local |
| baseline | provenfast | local |
| baseline | satori | local |
| baseline | skillshare | github.com/runkids/skillshare/skills/skillshare |
| baseline | treg | local |
| baseline | ui-craft | jevshelf:shims/ui-craft |
| baseline | wh-browser | local |
| aegis | aegis__anti-entropy-governance | github.com/GanyuanRan/Aegis/skills/anti-entropy-governance |
| aegis | aegis__brainstorming | github.com/GanyuanRan/Aegis/skills/brainstorming |
| aegis | aegis__communicating-concisely | github.com/GanyuanRan/Aegis/skills/communicating-concisely |
| aegis | aegis__dispatching-parallel-agents | github.com/GanyuanRan/Aegis/skills/dispatching-parallel-agents |
| aegis | aegis__establishing-project-context | github.com/GanyuanRan/Aegis/skills/establishing-project-context |
| aegis | aegis__executing-plans | github.com/GanyuanRan/Aegis/skills/executing-plans |
| aegis | aegis__finishing-a-development-branch | github.com/GanyuanRan/Aegis/skills/finishing-a-development-branch |
| aegis | aegis__first-principles-review | github.com/GanyuanRan/Aegis/skills/first-principles-review |
| aegis | aegis__goal-framing | github.com/GanyuanRan/Aegis/skills/goal-framing |
| aegis | aegis__long-task-continuation | github.com/GanyuanRan/Aegis/skills/long-task-continuation |
| aegis | aegis__receiving-code-review | github.com/GanyuanRan/Aegis/skills/receiving-code-review |
| aegis | aegis__recording-architecture-decisions | github.com/GanyuanRan/Aegis/skills/recording-architecture-decisions |
| aegis | aegis__requesting-code-review | github.com/GanyuanRan/Aegis/skills/requesting-code-review |
| aegis | aegis__subagent-driven-development | github.com/GanyuanRan/Aegis/skills/subagent-driven-development |
| aegis | aegis__systematic-debugging | github.com/GanyuanRan/Aegis/skills/systematic-debugging |
| aegis | aegis__test-driven-development | github.com/GanyuanRan/Aegis/skills/test-driven-development |
| aegis | aegis__ui-ux-governance | github.com/GanyuanRan/Aegis/skills/ui-ux-governance |
| aegis | aegis__update-aegis | github.com/GanyuanRan/Aegis/skills/update-aegis |
| aegis | aegis__using-aegis | github.com/GanyuanRan/Aegis/skills/using-aegis |
| aegis | aegis__using-git-worktrees | github.com/GanyuanRan/Aegis/skills/using-git-worktrees |
| aegis | aegis__verification-before-completion | github.com/GanyuanRan/Aegis/skills/verification-before-completion |
| aegis | aegis__writing-plans | github.com/GanyuanRan/Aegis/skills/writing-plans |
| aegis | aegis__writing-skills | github.com/GanyuanRan/Aegis/skills/writing-skills |

## Skillshare-managed hidden collections (excluded from native discovery)

| Collection | Managed leaf |
|---|---|
| academic-hidden | vault-academic__academic-paper |
| academic-hidden | vault-academic__academic-paper-reviewer |
| academic-hidden | vault-academic__academic-pipeline |
| academic-hidden | vault-academic__deep-research |
| academic-hidden | vault-academic__sr-screener |
| emil-hidden | vault-emil__animate |
| emil-hidden | vault-emil__animate-expo |
| emil-hidden | vault-emil__animation-performance |
| emil-hidden | vault-emil__animation-vocabulary |
| emil-hidden | vault-emil__apple-design |
| emil-hidden | vault-emil__ask-sonner |
| emil-hidden | vault-emil__break-ui |
| emil-hidden | vault-emil__emil-design-eng |
| emil-hidden | vault-emil__find-animation-opportunities |
| emil-hidden | vault-emil__improve-animations |
| emil-hidden | vault-emil__mobile-native |
| emil-hidden | vault-emil__pick-ui-library |
| emil-hidden | vault-emil__prototype |
| emil-hidden | vault-emil__review-animations |
| emil-hidden | vault-emil__write-swift |
| sentry-hidden | vault-sentry__code-simplifier |
| sentry-hidden | vault-sentry__find-bugs |
| sentry-hidden | vault-sentry__security-review |
| sentry-hidden | vault-sentry__skill-scanner |
| lassejlv-hidden | vault-lassejlv__backend-security-audit |
| lassejlv-hidden | vault-lassejlv__minimize-api-responses |
| lassejlv-hidden | vault-lassejlv__no-vibe-code |
| taste-hidden | vault-taste__taste-skill |
| matt-specialist-hidden | vault-matt-review__codebase-design |
| matt-specialist-hidden | vault-matt-review__domain-modeling |
| matt-specialist-hidden | vault-matt-review__grill-with-docs |
| matt-specialist-hidden | vault-matt-review__grilling |
| matt-specialist-hidden | vault-matt-review__handoff |
| matt-specialist-hidden | vault-matt-review__improve-codebase-architecture |
| matt-specialist-hidden | vault-matt-review__retro |
| matt-specialist-hidden | vault-matt-review__to-questionnaire |
| matt-specialist-hidden | vault-matt-review__wayfinder |
| matt-specialist-hidden | vault-matt-review__writing-beats |
| matt-specialist-hidden | vault-matt-review__writing-for-agents |
| matt-specialist-hidden | vault-matt-review__writing-fragments |
| matt-specialist-hidden | vault-matt-review__writing-shape |
| addy-specialist-hidden | vault-addy-review__api-and-interface-design |
| addy-specialist-hidden | vault-addy-review__browser-testing-with-devtools |
| addy-specialist-hidden | vault-addy-review__constraint-driven-development |
| addy-specialist-hidden | vault-addy-review__context-engineering |
| addy-specialist-hidden | vault-addy-review__deprecation-and-migration |
| addy-specialist-hidden | vault-addy-review__observability-and-instrumentation |
| addy-specialist-hidden | vault-addy-review__source-driven-development |
| writing-hidden | vault-writing__asd-ste100-skill |

## Available but inactive engineering collections

The full Matt and Addy engineering method packs remain inactive and are not
exposed via native agent discovery. Curated, scoped specialists are installed
as hidden Skillshare leaves and reachable only through JevShelf.

### Matt Pocock — 38 available

ask-matt, chief-of-staff, claude-handoff, code-review, codebase-design, diagnosing-bugs, domain-modeling, git-guardrails-claude-code, grill-me, grill-with-docs, grilling, handoff, implement, implement-spec, improve-codebase-architecture, loop-me, migrate-to-shoehorn, pr, prototype, research, retro, scaffold-exercises, setup-matt-pocock-skills, setup-pre-commit, setup-ts-deep-modules, tdd, teach, to-questionnaire, to-spec, to-tickets, triage, wait-what, wayfinder, wizard, writing-beats, writing-for-agents, writing-fragments, writing-shape.

### Addy Osmani — 25 available

api-and-interface-design, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, constraint-driven-development, context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine, incremental-implementation, interview-me, observability-and-instrumentation, performance-optimization, planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development, spec-driven-development, test-driven-development, using-agent-skills.

## Management notes

The personal management policy, official installation layout,
auditing caveats, and reversible swap prompt are in
[engineering-systems.md](engineering-systems.md) and
[swap-engineering-system.md](prompts/swap-engineering-system.md).

Existing Marketing and Thinking collections are still behind their
individual router shims and are not counted as engineering systems.
