# Skill watchlist — favorites and conditional use

These repositories are **references for future evaluation**, not active Skillshare installs or Jev collections. A watchlist entry is not authorization to install a skill. Use [the skill installation protocol](installation-protocol.md) and obtain an explicit user request first.

| Skill / project | Source | State | Reconsider when |
|---|---|---|---|
| **Distilly** (`distilly`, formerly Colleague Skill) | [titanwings/distilly](https://github.com/titanwings/distilly) | **Favorite / conditional / not installed** | You want an agent to adapt to an individual person's documented ways of reasoning, decision-making, working, or writing, and have suitable source material |

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
