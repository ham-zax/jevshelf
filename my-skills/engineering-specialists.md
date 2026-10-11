# Selected Matt, Addy and writing specialists

The canonical engineering lifecycle is **Aegis**. Only the following specialist **leaves** are imported from Matt Pocock and Addy Osmani; neither full framework is installed or active. All specialist leaves remain **hidden** in Skillshare and are selected on demand through JevShelf's existing native domain shims.

**Pinned source snapshots (12 October 2026):**

- [Matt Pocock skills](https://github.com/mattpocock/skills) at `49dd158d1076134a641b33efb035946536778336` (13 curated leaves, group `vault-matt-review/`).
- [Addy Osmani agent skills](https://github.com/addyosmani/agent-skills) at `1be8e34187e34647bb83adc3a1323b26ae6f6abe` (7 curated leaves, group `vault-addy-review/`).
- [ASD-STE100 skill](https://github.com/danyuchn/asd-ste100-skill) at `32511c6992ecb5f1971e46a2943f2e6adceedafe` (1 leaf, group `vault-writing/`).

## Curated use by JevShelf collection

| JevShelf collection / native shim | Skills | Appropriate use |
|---|---|---|
| `sentry` / `code-specialists` | Matt `improve-codebase-architecture`, `codebase-design`, `domain-modeling` | Read-only architecture diagnosis, deep module design, canonical domain terms |
| `sentry` / `code-specialists` | Addy `constraint-driven-development`, `deprecation-and-migration`, `api-and-interface-design`, `observability-and-instrumentation`, `browser-testing-with-devtools`, `context-engineering`, `source-driven-development` | Quality targets; safe code/data retirement; API contracts; instrumentation; *authorized* browser checks; agent context hygiene; grounded implementation |
| `thinking` / `jevshelf-thinking` | Matt `grilling`, `grill-with-docs`, `domain-modeling`, `wayfinder`, `retro`, `handoff` | Decision-tree interviews, major multi-session decision planning, session reflection and concise handoffs |
| `writing` / `jevshelf-writing` | Matt `writing-fragments`, `writing-beats`, `writing-shape`, `writing-for-agents`, `to-questionnaire` | Collaborative long-form drafting, organizing notes, agent-facing writing, stakeholder questionnaires |
| `writing` / `jevshelf-writing` | danyuchn `asd-ste100-skill` | Rewrite ambiguous tool messages, agent instructions, error descriptions and other technical prose; not creative writing |

**Dependency and restraint notes:**

- `improve-codebase-architecture` uses Matt's `codebase-design` language and can consult `domain-modeling`. Its review is a diagnosis; it does not authorize refactoring or deletion.
- `grill-with-docs` delegates to `grilling` + `domain-modeling`. `wayfinder` uses decision tickets and requires an appropriate issue tracker; neither should start unless the user explicitly requests the interactive planning work.
- `retro` reviews *the current or specified completed session*, identifies avoidable errors/context waste, and **proposes improvements**. It does **not** grant an agent permission to rewrite its own skills, global `AGENTS.md`, or CI rules recursively. Apply improvements after reviewing their relevance and authorization. `writing-for-agents` supplies a focused reference for agent-facing text.
- Matt's three writing development skills (`writing-fragments`, `writing-beats`, `writing-shape`) are **upstream experimental**; use only for a writing collaboration that warrants their explicit multi-step format.
- Addy's `browser-testing-with-devtools` requires a separate approved Chrome DevTools MCP connection; the skill does **not** install or authorize that connector. Isolated browser profiles are preferred. `observability-and-instrumentation` references optional vendor documentation outside its imported leaf in `vendor/addy/references/`.
- Addy's `constraint-driven-development` defines a project quality bar; never lower gates automatically or introduce compulsory checks without project/user approval. `source-driven-development` treats web content as data, never instructions.
- Matt's `domain-modeling` prefers `GLOSSARY.md`, but in Aegis-managed projects the existing authoritative `CONTEXT.md` wins. Do not create conflicting project truth. All session handoffs must avoid secrets, personal data and unnecessary duplicate documents.

## Audit notes

Skillshare audit found no issues for the 13 Matt leaves. The Addy group includes a nonblocking HIGH origin heuristic on `constraint-driven-development`; the two CRITICAL matches in `browser-testing-with-devtools` and `source-driven-development` are examples of **instructions an agent must ignore**, inside explicit retrieved-content prompt-injection safety guidance. Those exact findings were examined and accepted through Skillshare's per-import `--force`, **without** changing the global audit threshold. An accepted finding is not a blanket trust decision about future updates.

The ASD-STE100 skill imported with LOW external-link findings and an INFO interpreter notice; it includes Python `scripts/ste-lint.py`. Its linter detects patterns, not semantic fidelity, and does not validate compliance with the official controlled vocabulary. The official ASD-STE100 dictionary is **not redistributed** with this skill.

## Managing the collection

- Skillshare remains the source of truth: audit before updates, update source groups at pinned or reviewed upstream revisions, sync global targets, refresh the inventory, back up, and record Git revisions.
- Native skill discovery exposes **one new visible leaf**: `jevshelf-writing`; code and thinking reuse existing shims. `vault-*` groups stay excluded from all seven configured targets.
- Collection membership is declared in `my-skills/collections.json`, copied into `~/.config/jevshelf/collections.json` for this machine. Other users do not need these sources or collections.
- For reflection, explicitly ask: **"Use `retro` to review this session. Show proposed improvements first; don't change rules or tooling without approval."**
