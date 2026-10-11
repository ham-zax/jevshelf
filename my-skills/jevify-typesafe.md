# Jevify and the existing TypeSafe API key

**Verified in WSL on 2026-10-12:** The existing TypeSafe credential is now exported in the interactive login shell under **both** `JEV_API_KEY` and `TYPESAFE_API_KEY`, without duplicating the key literal. [Jevify](https://github.com/altryne/jevify) can read `TYPESAFE_API_KEY` directly. No new key or OpenRouter account is needed.

## Configured shell variables (preferred)

The existing key is declared only **once** in `~/.bashrc` as `JEV_API_KEY`. The next line exports `TYPESAFE_API_KEY` from the same value:

```bash
export TYPESAFE_API_KEY="$JEV_API_KEY"
```

Both variables are available in a fresh interactive login shell and inherited by commands launched from it, including Jevify's unmodified Python scripts. You can now run Jevify directly:

```bash
python3 ~/.config/skillshare/skills/jevify/scripts/scan.py notes.txt \
  --query "Find the relevant design evidence" --output /tmp/jevify-notes.json --top 8
```

The optional `jevify-typesafe` wrapper remains installed for agent subprocesses that were launched without the key in their inherited environment. It checks the current environment first, then attempts to load the existing login-shell key. It never writes or prints the secret and never silently falls back to OpenRouter.

This does not alter any key value, copy a key into the repository, or automatically authorize sending private text to an external service.

## Verification without exposing secrets

```bash
command -v jevify-typesafe
bash -n ~/repo/jevshelf/bin/jevify-typesafe

# Inspect availability **only**; do not echo keys
bash -lic 'test -n "${TYPESAFE_API_KEY:-${JEV_API_KEY:-}}" && echo "TypeSafe credential available"' 2>/dev/null

# Safe single-document live smoke test
printf 'Relevant design evidence.\nUnrelated example.\n' >/tmp/jevify-check.txt
jevify-typesafe scan /tmp/jevify-check.txt \
  --query "Find design evidence" --output /tmp/jevify-check-report.json --top 1
```

A live run uses the user's existing TypeSafe API quota and may send selected text to TypeSafe; do not put private or unrelated information into test inputs. Do not confuse a dry-run with a successful authenticated call.

## Updates and rollback

The Skillshare-sourced `jevify/SKILL.md` has a **documented local integration note**. A future `skillshare update jevify -g` can replace it. Before updating: checkpoint the Skillshare source Git tree, review the upstream diff/audit, and reinstate or revalidate the local note and wrapper. Commit Skillshare source changes, sync, and execute `bash scripts/backup-skillshare-vault.sh`. The wrapper itself lives in the management repository, separately committed, and its `~/.local/bin` symlink can be recreated from this document.

Credential configuration in the interactive shell remains the existing user's responsibility; this setup changes **no** `.bashrc`, `.profile`, `.env`, or credential file.
