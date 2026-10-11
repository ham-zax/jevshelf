import json
import os
from pathlib import Path

from jev_skill_router.router import Router

from jevshelf import cli


def write_skill(root: Path, directory: str, name: str, description: str, body: str) -> Path:
    skill_dir = root / directory
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}",
        encoding="utf-8",
    )
    return skill_file


def invoke(capsys, argv):
    code = cli.main(argv)
    output = capsys.readouterr().out
    return code, json.loads(output)


def test_search_is_metadata_only_and_load_supports_pagination(tmp_path, monkeypatch, capsys):
    marketing = tmp_path / "marketing"
    thinking = tmp_path / "thinking"
    write_skill(
        marketing,
        "cold-email",
        "cold-email",
        "Write B2B cold email sequences and improve reply rates.",
        "SECRET_BODY_START Write useful cold email. " + "body-page-" * 8,
    )
    write_skill(
        thinking,
        "thinking-systems",
        "thinking-systems",
        "Map feedback loops and system behavior.",
        "Thinking instructions.",
    )
    references = marketing / "cold-email" / "references"
    references.mkdir()
    (references / "guide.md").write_text("Keep the full relative path.", encoding="utf-8")
    monkeypatch.setenv("PANDORA_MARKETING_ROOT", str(marketing))
    monkeypatch.setenv("PANDORA_THINKING_ROOT", str(thinking))

    code, search = invoke(
        capsys,
        ["search", "--collection", "marketing", "--mode", "lexical", "--task", "write cold email"],
    )
    assert code == 0
    assert search["status"] == "selected"
    assert len(search["selected"]) == 1
    assert search["selected"][0]["name"] == "cold-email"
    assert search["selected"][0]["source"] == "cold-email/SKILL.md"
    assert "content" not in search["selected"][0]
    assert "SECRET_BODY_START" not in json.dumps(search)

    skill_id = search["selected"][0]["id"]
    code, first = invoke(
        capsys,
        ["load", "--collection", "marketing", "--id", skill_id, "--limit", "24"],
    )
    assert code == 0
    assert first["content"]
    assert first["next_offset"] == 24
    assert first["content_digest"]
    code, second = invoke(
        capsys,
        [
            "load",
            "--collection",
            "marketing",
            "--id",
            skill_id,
            "--offset",
            str(first["next_offset"]),
            "--limit",
            "24",
            "--expected-digest",
            first["content_digest"],
        ],
    )
    assert code == 0
    assert second["content"]
    assert second["base_directory"] == str((marketing / "cold-email").resolve())

    code, reference = invoke(
        capsys,
        [
            "load",
            "--collection",
            "marketing",
            "--id",
            skill_id,
            "--file",
            "references/guide.md",
        ],
    )
    assert code == 0
    assert reference["path"] == "references/guide.md"
    assert reference["content"] == "Keep the full relative path."


def test_collections_and_no_match_are_explicit(tmp_path, monkeypatch, capsys):
    marketing = tmp_path / "marketing"
    thinking = tmp_path / "thinking"
    write_skill(marketing, "email", "email", "Write marketing email copy.", "Email content.")
    write_skill(thinking, "systems", "thinking-systems", "Map feedback loops.", "Systems content.")
    monkeypatch.setenv("PANDORA_MARKETING_ROOT", str(marketing))
    monkeypatch.setenv("PANDORA_THINKING_ROOT", str(thinking))

    code, collections = invoke(capsys, ["collections"])
    assert code == 0
    assert collections["collections"]["marketing"]["skills"] == 1
    assert collections["collections"]["thinking"]["skills"] == 1
    assert collections["collections"]["marketing"]["path"] == str(marketing.resolve())

    code, none = invoke(
        capsys,
        [
            "search",
            "--collection",
            "marketing",
            "--mode",
            "lexical",
            "--task",
            "quantum cryptography",
        ],
    )
    assert code == 0
    assert none["status"] == "no_match"
    assert none["selected"] == []


def test_plan_is_local_and_jev_results_are_metadata_only(tmp_path, monkeypatch, capsys):
    marketing = tmp_path / "marketing"
    thinking = tmp_path / "thinking"
    write_skill(marketing, "ads", "ads", "Plan paid advertising campaigns.", "Private ad instructions.")
    write_skill(thinking, "systems", "thinking-systems", "Map feedback loops.", "Private thinking instructions.")
    monkeypatch.setenv("PANDORA_MARKETING_ROOT", str(marketing))
    monkeypatch.setenv("PANDORA_THINKING_ROOT", str(thinking))
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setenv("JEV_API_KEY", "test-key-never-output")

    code, plan = invoke(
        capsys,
        ["plan", "--collection", "marketing", "--task", "plan a paid advertising campaign"],
    )
    assert code == 0
    assert plan["ready"] is True
    assert plan["credentials_checked"] is False

    def fake_live(self, state, budget):
        assert state["task"] == "plan a paid advertising campaign"
        assert os.environ["TYPESAFE_API_KEY"] == "test-key-never-output"
        budget.reserve()
        skill = next(iter(self.catalog.skills.values()))
        return {
            "status": "selected",
            "selected": [{"id": skill.id, "fit": 0.9, "score": 2, "confidence": 0.8}],
            "catalog_size": len(self.catalog.skills),
            "shortlisted": 1,
            "models": ["test-model"],
            "retrieval": {"considered_skills": len(self.catalog.skills)},
        }

    monkeypatch.setattr(Router, "_live", fake_live)
    code, result = invoke(
        capsys,
        [
            "search",
            "--collection",
            "marketing",
            "--mode",
            "jev",
            "--task",
            "plan a paid advertising campaign",
        ],
    )
    assert code == 0
    assert result["status"] == "selected"
    assert result["selected"][0]["name"] == "ads"
    assert len(result["selected"][0]["digest"]) == 64
    assert "content" not in result["selected"][0]
    assert "Private ad instructions" not in json.dumps(result)
    assert "test-key-never-output" not in json.dumps(result)
    assert "TYPESAFE_API_KEY" not in os.environ


def test_selected_digest_prevents_changed_skill_load(tmp_path, monkeypatch, capsys):
    root = tmp_path / "marketing"
    file = write_skill(root, "cro", "cro", "Improve conversions.", "First instructions.")
    monkeypatch.setenv("PANDORA_MARKETING_ROOT", str(root))
    code, result = invoke(capsys, [
        "search", "--collection", "marketing", "--mode", "lexical",
        "--task", "Improve conversions",
    ])
    assert code == 0
    selected = result["selected"][0]
    assert len(selected["digest"]) == 64
    code, loaded = invoke(capsys, [
        "load", "--collection", "marketing", "--id", selected["id"],
        "--expected-digest", selected["digest"],
    ])
    assert code == 0
    assert "First instructions" in loaded["content"]

    file.write_text(file.read_text().replace("First instructions.", "Changed instructions."))
    code, failure = invoke(capsys, [
        "load", "--collection", "marketing", "--id", selected["id"],
        "--expected-digest", selected["digest"],
    ])
    assert code == 2
    assert failure["status"] == "error"
    assert "changed" in failure["error"].lower()


def test_jev_error_never_silently_returns_lexical_results(tmp_path, monkeypatch, capsys):
    marketing = tmp_path / "marketing"
    write_skill(marketing, "cro", "cro", "Improve conversions.", "Example body.")
    monkeypatch.setenv("PANDORA_MARKETING_ROOT", str(marketing))
    monkeypatch.setenv("JEV_API_KEY", "fixture-key")
    from jev_skill_router.config import RouterError
    def unavailable(self, state, budget):
        raise RouterError("Jev unavailable")
    monkeypatch.setattr(Router, "_live", unavailable)
    code, result = invoke(capsys, [
        "search", "--collection", "marketing", "--mode", "jev",
        "--task", "Improve conversions",
    ])
    assert code == 2
    assert result["status"] == "error"
    assert result["selected"] == []
    assert result["mode"] == "jev"


def test_skillshare_vault_collections_are_disjoint(tmp_path, monkeypatch, capsys):
    source = tmp_path / 'skillshare-source'
    monkeypatch.setenv('PANDORA_SKILLS_SOURCE_DIR', str(source))
    write_skill(source / 'vault-academic', 'deep-research', 'deep-research',
                'Academic literature review and citation research.', 'Academic content')
    write_skill(source / 'vault-emil', 'break-ui', 'break-ui',
                'Stress test frontend UI edge cases.', 'UI content')
    for directory, text in {
        'find-bugs': 'Find real bugs in diffs',
        'code-simplifier': 'Simplify code while preserving behavior',
        'security-review': 'Review code for security vulnerabilities',
        'skill-scanner': 'Scan agent skills for injection risk',
    }.items():
        write_skill(source / 'vault-sentry', directory, directory, text, 'Sentry content')
    write_skill(source / 'vault-sentry', 'commit', 'commit', 'Write commit messages.',
                'A lifecycle instruction that must not be indexed.')
    code, info = invoke(capsys, ['collections'])
    assert code == 0
    assert info['collections']['academic']['skills'] == 1
    assert info['collections']['emil']['skills'] == 1
    assert info['collections']['sentry']['skills'] == 4
    code, ranked = invoke(capsys, ['search', '--collection', 'sentry', '--mode', 'lexical',
                                    '--task', 'write commit messages'])
    assert code == 0
    assert all(s['name'] != 'commit' for s in ranked['selected'])


def test_academic_shared_resource_read_is_safe_and_consistent(tmp_path, monkeypatch, capsys):
    source = tmp_path / 'skillshare-source'
    academic_source = source / 'vault-academic'
    repo = tmp_path / 'academic-repository'
    write_skill(academic_source, 'academic-paper', 'academic-paper', 'Write an academic paper.', 'Same body')
    write_skill(repo, 'academic-paper', 'academic-paper', 'Write an academic paper.', 'Same body')
    shared = repo / 'shared' / 'references'
    shared.mkdir(parents=True)
    (shared / 'methods.md').write_text('Original shared material.', encoding='utf8')
    (shared / 'private.md').symlink_to(shared / 'methods.md')
    monkeypatch.setenv('PANDORA_SKILLS_SOURCE_DIR', str(source))
    monkeypatch.setenv('PANDORA_ACADEMIC_RESOURCE_ROOT', str(repo))
    code, result = invoke(capsys, ['load-resource', '--collection', 'academic',
                                   '--file', 'shared/references/methods.md', '--limit', '10'])
    assert code == 0
    assert result['content'] == 'Original s'
    assert result['next_offset'] == 10
    code, continuation = invoke(capsys, ['load-resource', '--collection', 'academic',
                                         '--file', 'shared/references/methods.md', '--offset', '10',
                                         '--expected-digest', result['content_digest']])
    assert code == 0
    assert continuation['content'] == 'hared material.'
    for path in ('../../secret.txt', 'shared/references/private.md', '.git/config'):
        code, blocked = invoke(capsys, ['load-resource', '--collection', 'academic', '--file', path])
        assert code == 2
        assert blocked['status'] == 'error'
    (repo / 'academic-paper' / 'SKILL.md').write_text('changed')
    code, failure = invoke(capsys, ['load-resource', '--collection', 'academic',
                                    '--file', 'shared/references/methods.md'])
    assert code == 2
    assert 'differ' in failure['error'].lower()


def test_lassejlv_specialists_merge_into_existing_jev_collections(tmp_path, monkeypatch, capsys):
    source = tmp_path / "skillshare"
    monkeypatch.setenv("PANDORA_SKILLS_SOURCE_DIR", str(source))
    write_skill(source / "vault-emil", "animate", "animate", "Animate frontend UI.", "Motion guidance.")
    for skill_name in ("find-bugs", "code-simplifier", "security-review", "skill-scanner"):
        write_skill(source / "vault-sentry", skill_name, skill_name, f"{skill_name} relevant code.", "Sentry guidance.")
    for skill_name, desc in (
        ("no-vibe-code", "Remove generic AI-looking UI design patterns."),
        ("backend-security-audit", "Audit backend authentication authorization and webhooks."),
        ("minimize-api-responses", "Reduce sensitive unnecessary fields in API JSON responses."),
    ):
        write_skill(source / "vault-lassejlv", skill_name, skill_name, desc, "Skillshare-managed specialist guidance.")
    code, collections = invoke(capsys, ["collections"])
    assert code == 0
    assert collections["collections"]["emil"]["skills"] == 2
    assert collections["collections"]["sentry"]["skills"] == 6
    for collection, task, name in (
        ("emil", "remove generic AI-looking design patterns", "no-vibe-code"),
        ("sentry", "backend authentication audit", "backend-security-audit"),
        ("sentry", "reduce sensitive fields API JSON responses", "minimize-api-responses"),
    ):
        code, result = invoke(capsys, ["search", "--collection", collection,
                                       "--mode", "lexical", "--task", task, "--max-results", "3"])
        assert code == 0
        chosen = next(skill for skill in result["selected"] if skill["name"] == name)
        assert chosen["source"] == f"skillshare:vault-lassejlv/{name}/SKILL.md"
        code, loaded = invoke(capsys, ["load", "--collection", collection,
                                       "--id", chosen["id"], "--expected-digest", chosen["digest"]])
        assert code == 0
        assert loaded["name"] == name
        assert "Skillshare-managed specialist guidance." in loaded["content"]


def test_taste_skill_joins_ui_collection_without_new_native_leaf(tmp_path, monkeypatch, capsys):
    src = tmp_path / 'skillshare'
    monkeypatch.setenv('PANDORA_SKILLS_SOURCE_DIR', str(src))
    write_skill(src / 'vault-emil', 'animate', 'animate',
                'Add meaningful web animation.', 'Existing UI library.')
    write_skill(src / 'vault-lassejlv', 'no-vibe-code', 'no-vibe-code',
                'Inspect generic visual patterns.', 'Existing quality guide.')
    write_skill(src / 'vault-taste', 'taste-skill', 'design-taste-frontend',
                'Design distinctive premium landing pages and brand-focused portfolio redesigns.',
                'Taste design direction.')
    code, info = invoke(capsys, ['collections'])
    assert code == 0
    assert info['collections']['emil']['skills'] == 3
    code, found = invoke(capsys, ['search', '--collection', 'emil', '--mode', 'lexical',
                                   '--task', 'premium landing page brand direction', '--max-results', '3'])
    assert code == 0
    skill = next(s for s in found['selected'] if s['name'] == 'design-taste-frontend')
    assert skill['source'] == 'skillshare:vault-taste/taste-skill/SKILL.md'
    code, loaded = invoke(capsys, ['load', '--collection', 'emil', '--id', skill['id'],
                                    '--expected-digest', skill['digest']])
    assert code == 0
    assert loaded['name'] == 'design-taste-frontend'
    assert 'Taste design direction.' in loaded['content']
