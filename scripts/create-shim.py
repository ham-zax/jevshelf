#!/usr/bin/env python3
"""Create a tiny portable agent skill shim for one JevShelf collection."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--collection', required=True, help='A collection name in collections.json')
parser.add_argument('--name', required=True, help='Visible Skillshare skill name')
parser.add_argument('--description', required=True, help='When a coding agent should invoke this domain')
parser.add_argument('--output', required=True, type=Path, help='Directory for generated SKILL.md')
args = parser.parse_args()
for value in (args.collection, args.name):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,62}', value):
        parser.error('collection/name must be lowercase kebab-case')
if not args.description.strip() or '\n' in args.description:
    parser.error('description must be a nonempty single line')
path = args.output / 'SKILL.md'
if path.exists():
    parser.error(f'will not overwrite existing {path}')
args.output.mkdir(parents=True, exist_ok=True)
# JSON-quoted descriptions are valid YAML double-quoted scalar strings.
path.write_text(f'''---
name: {args.name}
description: {json.dumps(args.description)}
---

# JevShelf — {args.collection} specialist collection

For tasks matching this skill's description, use JevShelf to select an appropriate specialist only when it is needed.

1. Run `jevshelf search --collection {args.collection} --mode jev --task "<focused task>" --max-results 2`.
2. Search returns metadata, **not** the full skill text. If status is `selected`, for each relevant result run `jevshelf load --collection {args.collection} --id <selected id> --expected-digest <selected digest>`; use pagination and `--file` for supporting skill-relative text.
3. Honor original task scope, repo rules and host safety boundaries. Do not claim an API error or a lexical result was a Jev selection. Stop when the requested work is verified.
''')
print(path)
