#!/usr/bin/env python3
"""Snapshot Skillshare global source and the three optional engineering catalogs.

Read-only except for my-skills/installed.csv and my-skills/installed.md.
No network calls, no installation, and no agent configuration changes.
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "my-skills"
CSV_PATH = DOCS / "installed.csv"
MD_PATH = DOCS / "installed.md"
FIELDS = ["collection", "skill", "status", "skillshare_name", "source", "upstream_path", "notes"]
REPOS = {
    "aegis": ("aegis", "https://github.com/GanyuanRan/Aegis"),
    "matt": ("matt", "https://github.com/mattpocock/skills"),
    "addy": ("addy", "https://github.com/addyosmani/agent-skills"),
}
HIDDEN_GROUPS = {
    "vault-academic/": "academic-hidden",
    "vault-emil/": "emil-hidden",
    "vault-sentry/": "sentry-hidden",
    "vault-lassejlv/": "lassejlv-hidden",
    "vault-taste/": "taste-hidden",
}

GROUPS = {
    "aegis": "aegis/",
    "matt": "engineering-matt/",
    "addy": "engineering-addy/",
}


def skillshare_entries() -> list[dict]:
    completed = subprocess.run(
        ["skillshare", "list", "--json", "-g"],
        capture_output=True, text=True, check=True,
    )
    entries = json.loads(completed.stdout)
    if not isinstance(entries, list):
        raise ValueError("Skillshare list did not return a list")
    return entries


def catalog_skills(key: str) -> list[tuple[str, str]]:
    directory, _ = REPOS[key]
    skills_root = ROOT / "vendor" / directory / "skills"
    if not skills_root.is_dir():
        return []
    found: list[tuple[str, str]] = []
    for file in sorted(skills_root.glob("**/SKILL.md")):
        content = file.read_text(encoding="utf-8-sig")
        frontmatter = content.split("---", 2)[1] if content.startswith("---") else ""
        match = re.search(r"(?m)^name:\s*['\"]?([^'\"\r\n]+)", frontmatter)
        skill_name = match.group(1).strip() if match else file.parent.name
        found.append((skill_name, str(file.parent.relative_to(ROOT / "vendor" / directory))))
    return found


def official_matt_skills() -> set[str]:
    path = ROOT / "vendor" / "matt" / ".claude-plugin" / "plugin.json"
    if not path.exists():
        return set()
    manifest = json.loads(path.read_text())
    return {p.rstrip("/").split("/")[-1] for p in manifest["skills"]}


def public_source(value: object) -> str:
    """Keep private machine paths out of public personal catalog snapshots."""
    text = str(value)
    if text.startswith("/home/") or text.startswith("/Users/"):
        if "/shims/" in text:
            return "jevshelf:shims/" + text.split("/shims/", 1)[1]
        return "local (path redacted)"
    return text


def build_rows() -> list[dict[str, str]]:
    installed = skillshare_entries()
    active_by_group: dict[str, dict[str, dict]] = {
        k: {} for k in REPOS
    }
    rows: list[dict[str, str]] = []

    for entry in installed:
        name = str(entry["name"])
        rel = str(entry.get("relPath", ""))
        group = next((k for k, prefix in GROUPS.items() if rel.startswith(prefix)), None)
        if group:
            active_by_group[group][rel.split("/", 1)[1]] = entry
            continue
        hidden = next((value for prefix, value in HIDDEN_GROUPS.items()
                       if rel.startswith(prefix)), None)
        if hidden:
            rows.append({
                "collection": hidden, "skill": rel.split("/", 1)[1],
                "status": "managed-hidden", "skillshare_name": name,
                "source": public_source(entry.get("source") or "github"),
                "upstream_path": rel,
                "notes": "Skillshare manages/updates; excluded from all agent targets; Jev-only",
            })
            continue
        rows.append({
            "collection": "baseline",
            "skill": name,
            "status": "installed",
            "skillshare_name": name,
            "source": public_source(entry.get("source") or entry.get("type", "local")),
            "upstream_path": rel,
            "notes": "Existing skill; preserve during engineering swaps",
        })

    official_matt = official_matt_skills()
    previous: dict[tuple[str, str], dict] = {}
    if CSV_PATH.is_file():
        with CSV_PATH.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                previous[(row.get("collection", ""), row.get("skill", ""))] = row

    for key, (_, repo_url) in REPOS.items():
        discovered = catalog_skills(key)
        if not discovered:
            discovered = [
                (r["skill"], r.get("upstream_path", ""))
                for (group, _), r in previous.items() if group == key
            ]
        discovered_names = {name for name, _ in discovered}
        for name in sorted(set(active_by_group[key]) - discovered_names):
            discovered.append((name, f"skills/{name}"))
        for name, upstream_path in discovered:
            installed_entry = active_by_group[key].get(name)
            status = "installed" if installed_entry else "available-not-installed"
            note = ("official plugin skill" if name in official_matt
                    else "not in official plugin (in-progress or misc)") if key == "matt" else ""
            rows.append({
                "collection": key,
                "skill": name,
                "status": status,
                "skillshare_name": installed_entry["name"] if installed_entry else "",
                "source": public_source(installed_entry.get("source", repo_url)) if installed_entry else repo_url,
                "upstream_path": upstream_path,
                "notes": note,
            })

    return sorted(rows, key=lambda x: (
        ["baseline", "aegis", "academic-hidden", "emil-hidden", "sentry-hidden", "lassejlv-hidden", "taste-hidden", "matt", "addy"].index(x["collection"]), x["skill"]
    ))


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    rows = build_rows()
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(row["collection"] for row in rows if row["status"] == "installed")
    hidden = Counter(row["collection"] for row in rows if row["status"] == "managed-hidden")
    sources = Counter(row["collection"] for row in rows)
    active = [name for name in ("aegis", "matt", "addy") if counts[name]]
    if len(active) > 1:
        raise SystemExit("WARNING: more than one canonical engineering system installed: " + ", ".join(active))
    title = {
        "aegis": "Aegis", "matt": "Matt Pocock", "addy": "Addy Osmani",
    }
    lines = [
        "# Skill inventory",
        "",
        "Snapshot of the installed Skillshare global source and the three engineering system libraries.",
        "Regenerate with: python3 my-skills/scripts/refresh-inventory.py (requires Skillshare CLI).",
        "The companion CSV is the complete row-level ledger.",
        "",
        f"- **Current canonical engineering system:** {title[active[0]] if active else 'none'}",
        f"- **Installed Skillshare source entries:** {sum(counts.values()) + sum(hidden.values())}",
        f"- **Visible/source skills:** {sum(counts.values())} (includes 17 original, 23 Aegis, 3 additional domain shims, and jevify)",
        f"- **Managed hidden Jev leaves:** {sum(hidden.values())} (Academic {hidden['academic-hidden']}, Emil {hidden['emil-hidden']}, Sentry {hidden['sentry-hidden']}, lassejlv {hidden['lassejlv-hidden']}, Taste {hidden['taste-hidden']})",
        f"- **Aegis:** {counts['aegis']} installed of {sources['aegis']} available",
        f"- **Matt Pocock:** {counts['matt']} installed of {sources['matt']} available; 27 were in the inspected official plugin",
        f"- **Addy Osmani:** {counts['addy']} installed of {sources['addy']} available",
        "",
        "## Installed skills",
        "",
        "| Collection | Skillshare skill name | Source |",
        "|---|---|---|",
    ]
    for row in rows:
        if row["status"] != "installed":
            continue
        lines.append(f"| {row['collection']} | {row['skillshare_name']} | {row['source']} |")
    lines += [
        "", "## Skillshare-managed hidden collections (excluded from native discovery)", "",
        "| Collection | Managed leaf |", "|---|---|",
    ]
    for row in rows:
        if row["status"] == "managed-hidden":
            lines.append(f"| {row['collection']} | {row['skillshare_name']} |")
    lines += [
        "",
        "## Available but inactive engineering collections",
        "",
        "These are source-catalog candidates, not native-installed skills. No inactive",
        "engineering skill is exposed through Skillshare or agent skill discovery.",
        "",
    ]
    for key in ("aegis", "matt", "addy"):
        if counts[key]:
            continue
        members = [row for row in rows if row["collection"] == key]
        lines += [
            f"### {title[key]} — {len(members)} available",
            "",
            ", ".join(r["skill"] for r in members) + ".",
            "",
        ]
    lines += [
        "## Management notes",
        "",
        "The personal management policy, official installation layout,",
        "auditing caveats, and reversible swap prompt are in",
        "[engineering-systems.md](engineering-systems.md) and",
        "[swap-engineering-system.md](prompts/swap-engineering-system.md).",
        "",
        "Existing Marketing and Thinking collections are still behind their",
        "individual router shims and are not counted as engineering systems.",
    ]
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Recorded {len(rows)} rows; {sum(counts.values())} visible; {sum(hidden.values())} managed hidden; canonical={active}")


if __name__ == "__main__":
    main()
