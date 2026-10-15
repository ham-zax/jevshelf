# How JevShelf works

A **skill library** can hold dozens or hundreds of specialist `SKILL.md` files without advertising all of them to each agent. Skillshare and JevShelf are complementary, not competing managers:

```text
                    Skill author repos
                           |
                    Skillshare source Git
                (audit • update • snapshot)
                           |
                +----------+------------+
                |                       |
         Visible domain shim      Hidden source skills
         (one SKILL.md)           (vault-*/SKILL.md)
                |                       |
     Skillshare sync to hosts            |
     Codex • Pi • Claude Code...         |
                |                       |
       Agent chooses domain             |
                |                       |
       jevshelf search ─── TypeSafe Jev + local metadata
                |                       |
       chosen ID + SHA-256 ──────────────+
                |
       jevshelf load (bounded, read-only)
                |
       coding agent handles task
```

## What is and is not lazy

Native coding agents can see the **name and description of each visible shim** from the start; they don't receive every hidden specialist's complete instructions. JevShelf's `search` returns only metadata with digests, and the caller separately retrieves selected instructions through `load` (read-size bound, SHA-256 continuity). Jev may inspect bounded excerpts for shortlisted candidates during ranking. A selected skill does **not** automatically get executed or override the host's safety rules.

The skill discovery step is the host's native behavior. Skillshare makes the shim visible to each configured target. It does *not* inject the skill into a running model, nor guarantee that any model will activate the shim for every relevant prompt. Start a new agent session after sync.

## Selection contract

For the common global instruction section, request examples and cross-host update procedure, see [GLOBAL_AGENT_GUIDANCE.md](GLOBAL_AGENT_GUIDANCE.md).

The host supplies a neutral current question and a concise situation brief: product purpose, current step, observed evidence, unknowns and constraints. Define unfamiliar product/model names. Naming a framework is appropriate when the user requests it, but otherwise biases discovery. Jev receives no implicit conversation history.

Jev ranks collection metadata, then verifies up to six candidates per ranking batch with independent applicability and usefulness questions. Verification considers the supplied task/context and bounded source excerpts containing capability and exclusion sections when available. Excerpts retain the 900-character default and conservative JSON-byte preflight bound; they are samples, not complete documents. The host digest-loads any selected skill before applying its instructions. Final recommendations remain capped at three and can be fewer or empty. Six is an initial coverage setting, not a measured optimum.

These JevShelf-specific judgments and excerpts live in tracked `src/jevshelf/selection.py`; the CLI selects `jev-preview` for live search and plan output. The pinned upstream router still owns transport, retries, request/time limits, ranking, statuses and usage accounting. Search and plan output use the same six-candidate setting. The ignored dependency checkout is not patched.

Lexical mode resolves an exact normalized skill name locally; other queries retain metadata BM25. Exact matches do not fill spare result slots with unrelated skills. Lexical results are explicitly labeled and never silently substitute for Jev errors, uncertainty or no-match. There is no automatic hybrid or embedding retrieval.

- **Jev**: optional hosted semantic selection, requiring a valid TypeSafe key. The task, the collection metadata, and bounded excerpts may be sent to TypeSafe. Use lexical mode for local BM25 matching; label it as lexical, not Jev.
- **Skillshare**: source management, provenance, updates, audit, target filters and symlink sync. These functions are not implemented by JevShelf itself.
- **JevShelf**: portable collection configuration, selection interface and safe bounded reads, plus a shim generator.
- **Agent host**: tools, approvals, permissions, reasoning, implementation, tests and final answers. Existing skills and methods still take precedence when applicable.

## Canonical workflow and specialist choice

The host honors activation rules, chooses the applicable configured engineering
workflow and retains its fast path before specialist discovery. A relevant workflow and a useful specialist
can coexist: one owns the process; the other contributes expertise to a step.
Non-engineering tasks do not require an engineering workflow.

The host considers directly available specialist descriptions first. It searches
JevShelf when extra expertise would help, the choice is ambiguous, or the user
requests it, then compares returned descriptions with useful direct candidates.
Only useful instructions are loaded. A sufficient direct skill can avoid a
hosted call; no-match or uncertainty never requires forcing another workflow.

Engineering search context should identify the active workflow, current step and
needed contribution. Jev sees only supplied context and the configured collection;
it cannot discover all native host skills or choose the canonical owner. The host
retains planning, artifact, verification, completion and permission boundaries.
This is instruction-level routing, not runtime enforcement of model behavior.

## Portability

JevShelf is a Python CLI, not a Claude-specific plugin or a universal agent hook. Configure collections using a JSON manifest, then make one ordinary portable `SKILL.md` shim per domain. Skillshare handles distribution to configured supported hosts. The product neither installs Skillshare nor changes its targets automatically. One user's source paths, collection selection and installed skills are never required by another user's installation.

## Dependencies and limits

- Git, Python 3.13 via uv (the bootstrap installs it), and the pinned MIT-licensed `jev-skill-router` 0.4.1 library.
- A TypeSafe Jev key for live semantic selection; no key required for installation, `collections`, `init`, lexical search or bounded loads.
- Local accessible skill source files. Shared resources outside a skill directory may need additional project-specific safe access; an academic-only resource reader exists for the maintainer's opt-in integration.
- Shell scripts and the systemd timer are Linux/WSL-specific. Generic CLI and SKILL.md discovery are portable to other systems with the necessary dependencies.
- External third-party skills are subject to their own licenses and audit decisions; they're not bundled in the public package.
