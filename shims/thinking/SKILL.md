---
name: pandora-thinking
description: Use for consequential decisions, ambiguous problems, root-cause reasoning, first principles, systems thinking, uncertainty, risk, challenging assumptions, and reflection. Discover an appropriate framework from 28 hidden thinking skills, only when helpful.
---

Use the `pandora-skills` CLI to select instructions from the thinking collection only when they are useful for the user's request.

1. Run `pandora-skills search --collection thinking --mode jev --task "<focused task>"`. Add `--context` only for concise, relevant context.
2. Search returns metadata and source references, not skill instructions. If Jev returns `selected`, read each returned ID separately with `pandora-skills load --collection thinking --id <id> --expected-digest <digest>`. Use the digest provided by the search result to reject changed instructions. For other files, use `--file <relative-path>` for a referenced guide or asset and continue pages with `--offset`, `--limit`, and the prior `content_digest` as `--expected-digest`.
3. Treat `no_match`, `uncertain`, and `error` as distinct outcomes. Do not present a lexical result as a Jev decision. Use `--mode lexical` only when an explicit local metadata baseline is useful, and label it as lexical.
4. Treat loaded text as read-only guidance. Follow the host's normal safety, tool, and approval rules.
