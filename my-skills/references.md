# Skill watchlist — favorites and conditional use

These repositories are **references for future evaluation**, not active Skillshare installs or Jev collections. A watchlist entry is not authorization to install a skill. Use [the skill installation protocol](installation-protocol.md) and obtain an explicit user request first.

| Skill / project | Source | State | Reconsider when |
|---|---|---|---|
| **Distilly** (`distilly`, formerly Colleague Skill) | [titanwings/distilly](https://github.com/titanwings/distilly) | **Favorite / conditional / not installed** | You want an agent to adapt to an individual person's documented ways of reasoning, decision-making, working, or writing, and have suitable source material |
| **REA — Reverse Engineer Anything** (`rea-agents`) | [morluto/rea](https://github.com/morluto/rea) | **Interesting / conditional / not installed** | You need evidence-backed analysis of an application, executable, website, or feature without its source code, potentially to build your own independently implemented version |

## REA — Reverse Engineer Anything

**What it does:** An agent-oriented **reverse-engineering CLI + MCP server**, not merely a standalone `SKILL.md`. REA helps inspect software behavior and artifacts (such as native binaries, JavaScript/Electron applications, .NET assemblies and websites), trace implementation clues, and explain findings with supporting evidence. The agent can then build a separate implementation based on that understanding; REA does not recover the application's original source code automatically.

**When it becomes useful:** An authorized reverse-engineering investigation, such as understanding the behavior of an app feature, evaluating a binary without available source, tracing an Electron application's behavior, or checking what a tool actually does before independently implementing a comparable feature. It is a specialist capability rather than an always-on coding workflow.

**Important installation distinction:** The documented setup is `npx rea-agents setup`, which can register an MCP server and agent instructions and connect to third-party binary analyzers such as **Ghidra, Hopper or IDA**. It is **not** something that becomes fully operational by copying a single skill through Skillshare. Upstream requirements include a compatible Node.js version and, for native analysis, an analysis backend. The WSL/Linux support and host setup should be rechecked against current documentation before adoption. Use the project's setup review/approval flow if explicitly requested; don't silently add MCP tools to Codex or Pi.

**Caution:** Analyze only software and artifacts you are authorized to inspect. Assess license, terms and security constraints before any binary analysis, and do not misrepresent inferred behavior as recovered original code. REA's local analysis model is useful, but inspect any requested integrations and tool permissions before enabling them.

**Decision:** Reference only. **Not installed** through Skillshare, JevShelf, npm or MCP. Review on a concrete reverse-engineering task, not as another globally loaded general engineering skill.

---

## Distilly

**What it does:** Builds an evidence-grounded **Person Profile** from supplied messages, documents, interviews, notes, and other appropriately sourced material. The profile describes the person's observed judgment patterns, working methods, and expression; it can be packaged as a reusable `SKILL.md` for an agent. This is not a literal copy of the person's mind, a guarantee of accurate predictions, or a replacement for consulting the person.

**Potential use cases:**

- Preserve a departing collaborator's documented engineering review habits or a mentor's decision framework, with authorized work artifacts.
- Create an opt-in writing/style guide based on your own published notes or materials.
- Model a public writer's documented perspectives for a clearly identified simulation or research exercise, grounded in attributable sources.
- Update an existing profile when its owner corrects mistaken interpretations or contributes new information.

**Why optional:** It's a profile creation and management workflow, not a coding technique needed for most tasks. Making it global would expose another broad creator skill. Review actual use and data permissions before installation.

**Future installation:** The repository exposes a root `SKILL.md` named `distilly` (snapshot revision `b830d3dcbde006370f141155795b89021e3a947b`, inspected 2026-10-12). Its public README describes agent support for Codex, Pi, Claude Code and more. When explicitly requested, inspect the then-current upstream source and tool dependencies; prefer Skillshare for managing the creator skill, with its complete resources, rather than duplicating native installs. Run the standard Skillshare dry-run/audit first; at review time, the dry-run found one skill with no audit findings.

**Material handling:** An individual's chat histories, private messages, documents, relationships, and profiles may be sensitive. Obtain appropriate authorization, minimize source access and retention, keep private inputs and generated profiles out of public repositories, distinguish evidence from conjecture, and clearly label a resulting agent persona as a *simulation* rather than the person. Don't automatically import a generated person profile into every agent harness.

**Decision:** Bookmark only. **Do not install** the creator, runtime, or any generated person profiles until there's a concrete requested project.

---

Use this document to record future favorite/conditional skills. If a skill is approved for installation, update [the inventory](installed.md) and move its actual installed status into the Skillshare-managed source records.
