# My Skills — TypeSafe Jev credentials

The WSL login shell exports **both** `JEV_API_KEY` and `TYPESAFE_API_KEY` with the same existing value. The key is declared once in `~/.bashrc`; the second variable is assigned by reference:

```bash
export TYPESAFE_API_KEY="$JEV_API_KEY"
```

There is **no credential wrapper, adapter, compatibility alias, or duplicate key file**. JevShelf and the upstream `jevify` script can read `TYPESAFE_API_KEY` directly when launched from a shell that inherited this environment.

For agents launched without your shell variables, configure their normal approved environment mechanism or launch them from a login shell. Do not commit the key, print it in logs, or add alternate credential loaders.

```bash
bash -lic '[[ -n "$TYPESAFE_API_KEY" && "$JEV_API_KEY" == "$TYPESAFE_API_KEY" ]] && echo "TypeSafe environment configured"'
python3 ~/.config/skillshare/skills/jevify/scripts/scan.py --help
```

Live Jev requests send selected task content to TypeSafe and consume API quota. Only send content you're authorized to process.
