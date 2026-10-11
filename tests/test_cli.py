import json
import os

import pytest
from pathlib import Path

from jev_skill_router.router import Router

from jevshelf import cli


@pytest.fixture(autouse=True)
def isolated_manifest(tmp_path, monkeypatch):
    manifest = tmp_path / "collections.json"
    manifest.write_text(json.dumps({"collections": {}}))
    monkeypatch.setenv("JEVSHELF_CONFIG", str(manifest))


def configure_collection(name: str, roots: list[Path], **extra) -> None:
    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    payload = json.loads(manifest.read_text())
    payload["collections"][name] = {"roots": [str(p) for p in roots], **extra}
    manifest.write_text(json.dumps(payload))


def configure_vault(source: Path) -> None:
    configure_collection("academic", [source / "vault-academic"])
    configure_collection("emil", [source / "vault-emil", source / "vault-lassejlv/no-vibe-code", source / "vault-taste/taste-skill"])
    configure_collection("sentry", [source / f"vault-sentry/{name}" for name in (
        "find-bugs", "code-simplifier", "security-review", "skill-scanner"
    )] + [source / "vault-lassejlv/backend-security-audit", source / "vault-lassejlv/minimize-api-responses"])


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
    configure_collection("marketing", [marketing])
    configure_collection("thinking", [thinking])

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
    configure_collection("marketing", [marketing])
    configure_collection("thinking", [thinking])

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
    configure_collection("marketing", [marketing])
    configure_collection("thinking", [thinking])
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
    configure_collection("marketing", [root])
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
    configure_collection("marketing", [marketing])
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
    configure_vault(source)
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
    configure_vault(source)
    configure_collection("academic", [academic_source], resources_root=str(repo),
                         resources_allowlist=["shared", "scripts", "agents", "academic-paper"],
                         verify_resources_against_skills=True)
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
    configure_vault(source)
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
        assert chosen["source"].startswith("root") and chosen["source"].endswith("SKILL.md")
        code, loaded = invoke(capsys, ["load", "--collection", collection,
                                       "--id", chosen["id"], "--expected-digest", chosen["digest"]])
        assert code == 0
        assert loaded["name"] == name
        assert "Skillshare-managed specialist guidance." in loaded["content"]


def test_taste_skill_joins_ui_collection_without_new_native_leaf(tmp_path, monkeypatch, capsys):
    src = tmp_path / 'skillshare'
    configure_vault(src)
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
    assert skill['source'] == 'root2:SKILL.md'
    code, loaded = invoke(capsys, ['load', '--collection', 'emil', '--id', skill['id'],
                                    '--expected-digest', skill['digest']])
    assert code == 0
    assert loaded['name'] == 'design-taste-frontend'
    assert 'Taste design direction.' in loaded['content']


def test_user_manifest_is_independent_and_labels_mixed_roots(tmp_path, monkeypatch, capsys):
    """Public users can configure arbitrary collections and receive accurate source refs."""
    base = tmp_path / 'sources'
    write_skill(base / 'alpha', 'alpha-skill', 'alpha-skill', 'Review architecture decisions.', 'Alpha guidance.')
    write_skill(base / 'beta', 'beta-skill', 'beta-skill', 'Audit interface edge cases.', 'Beta guidance.')
    manifest = tmp_path / 'collections.json'
    manifest.write_text(json.dumps({'collections': {'custom': {'roots': [str(base / 'alpha'), str(base / 'beta')]}}}))
    monkeypatch.setenv('JEVSHELF_CONFIG', str(manifest))
    code, info = invoke(capsys, ['collections'])
    assert code == 0
    assert list(info['collections']) == ['custom']
    assert info['collections']['custom']['skills'] == 2
    code, found = invoke(capsys, ['search', '--collection', 'custom', '--mode', 'lexical',
                                  '--task', 'audit interface edge cases', '--max-results', '2'])
    assert code == 0
    selected = next(s for s in found['selected'] if s['name'] == 'beta-skill')
    assert selected['source'] == 'root1:beta-skill/SKILL.md'
    code, result = invoke(capsys, ['load', '--collection', 'custom', '--id', selected['id'],
                                   '--expected-digest', selected['digest']])
    assert code == 0 and 'Beta guidance.' in result['content']


def test_no_implicit_user_collections_and_first_time_init(tmp_path, monkeypatch, capsys):
    """Public installation has no personal collection defaults or hidden roots."""
    path = tmp_path / "first-config.json"
    monkeypatch.setenv("JEVSHELF_CONFIG", str(path))
    code, before = invoke(capsys, ["collections"])
    assert code == 0 and before["collections"] == {}
    code, result = invoke(capsys, ["init"])
    assert code == 0 and result["status"] == "created"
    code, after = invoke(capsys, ["collections"])
    assert code == 0 and after["collections"]["writing"]["skills"] == 2


@pytest.mark.parametrize("payload", [
    "{invalid",
    "[]",
    "null",
    "NaN",
    '{"collections": []}',
    '{"collections": null}',
    '{"collections": {"demo": {"roots": []}}}',
    '{"collections": {"demo": 7}}',
])
def test_malformed_manifest_is_safe_json_error(tmp_path, monkeypatch, capsys, payload):
    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text(payload)
    code, result = invoke(capsys, ["collections"])
    assert code == 2
    assert result["status"] == "error"
    assert "Invalid JevShelf configuration" in result["error"]
    code, result = invoke(
        capsys,
        ["search", "--collection", "anything", "--mode", "lexical", "--task", "hi"],
    )
    assert code == 2
    assert result["status"] == "error"
    assert "Invalid JevShelf configuration" in result["error"]


def test_repo_roots_stay_compatible(tmp_path, monkeypatch, capsys):
    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text(json.dumps({"collections": {"demo": {"roots": ["@repo/examples/skills"]}}}))
    code, result = invoke(capsys, ["collections"])
    assert code == 0
    assert result["collections"]["demo"]["skills"] == 2


def test_unreadable_manifest_is_safe_json_error(tmp_path, monkeypatch, capsys):
    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text(json.dumps({"collections": {}}))
    manifest.chmod(0o000)
    try:
        try:
            manifest.read_text()
        except OSError:
            pass
        else:
            pytest.skip("manifest remains readable under this user")
        code, result = invoke(capsys, ["collections"])
        assert code == 2
        assert result["status"] == "error"
        assert "Invalid JevShelf configuration" in result["error"]
    finally:
        manifest.chmod(0o600)


def test_init_never_overwrites_invalid_config(tmp_path, monkeypatch, capsys):
    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text("{invalid")
    code, result = invoke(capsys, ["init"])
    assert code == 2
    assert result["status"] == "error"
    assert manifest.read_text() == "{invalid"


def test_init_reports_existing_config_without_changes(tmp_path, monkeypatch, capsys):
    root = tmp_path / "skills"
    write_skill(root, "s", "s", "Do things.", "Body.")
    configure_collection("custom", [root])
    code, result = invoke(capsys, ["init"])
    assert code == 0
    assert result["status"] == "exists"
    assert result["collections"] == ["custom"]


def test_unknown_collection_is_rejected_as_json_error(tmp_path, monkeypatch, capsys):
    configure_collection("marketing", [tmp_path / "marketing"])
    cases = [
        ["search", "--collection", "nope", "--mode", "lexical", "--task", "hi"],
        ["load", "--collection", "nope", "--id", "whatever"],
        ["load-resource", "--collection", "nope", "--file", "shared/x.md"],
        ["plan", "--collection", "nope", "--task", "hi"],
    ]
    for argv in cases:
        code, result = invoke(capsys, argv)
        assert code == 2
        assert result["status"] == "error"
        assert "Unknown collection" in result["error"]


def test_help_and_usage_do_not_require_a_valid_config(tmp_path, monkeypatch, capsys):
    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text("{invalid")
    with pytest.raises(SystemExit) as top:
        cli.main(["--help"])
    assert top.value.code == 0
    with pytest.raises(SystemExit) as search_help:
        cli.main(["search", "--help"])
    assert search_help.value.code == 0
    capsys.readouterr()


def test_subprocess_reports_config_errors_without_traceback(tmp_path, monkeypatch):
    import subprocess
    import sys

    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text("null")
    console = Path(sys.executable).parent / "jevshelf"
    completed = subprocess.run(
        [str(console), "collections"],
        capture_output=True, text=True, timeout=120,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert payload["status"] == "error"
    assert "Traceback" not in completed.stderr


def test_subprocess_help_works_with_broken_config(tmp_path, monkeypatch):
    import subprocess
    import sys

    manifest = Path(os.environ["JEVSHELF_CONFIG"])
    manifest.write_text("{invalid")
    console = Path(sys.executable).parent / "jevshelf"
    completed = subprocess.run(
        [str(console), "--help"],
        capture_output=True, text=True, timeout=120,
    )
    assert completed.returncode == 0
    assert "usage" in completed.stdout


def test_init_writes_portable_demo_manifest(tmp_path, monkeypatch, capsys):
    path = tmp_path / "fresh" / "collections.json"
    monkeypatch.setenv("JEVSHELF_CONFIG", str(path))
    code, result = invoke(capsys, ["init"])
    assert code == 0
    assert result["status"] == "created"
    payload = json.loads(path.read_text())
    assert payload["collections"]["writing"]["roots"] == ["@demo/skills"]

    code, after = invoke(capsys, ["collections"])
    assert code == 0
    assert after["collections"]["writing"]["skills"] == 2

    code, found = invoke(
        capsys,
        ["search", "--collection", "writing", "--mode", "lexical",
         "--task", "summarize the meeting notes and identify next actions"],
    )
    assert code == 0
    assert found["status"] == "selected"
    skill = next(s for s in found["selected"] if s["name"] == "summarize-notes")
    code, loaded = invoke(
        capsys,
        ["load", "--collection", "writing", "--id", skill["id"],
         "--expected-digest", skill["digest"]],
    )
    assert code == 0
    assert "Summarize the notes" in loaded["content"]


def test_jev_search_with_missing_root_is_explicit_error(tmp_path, monkeypatch, capsys):
    configure_collection("broken", [tmp_path / "does-not-exist"])
    monkeypatch.setenv("JEV_API_KEY", "fixture-key")

    def forbidden_live(self, state, budget):
        raise AssertionError("empty catalogs must not reach Jev inference")

    monkeypatch.setattr(Router, "_live", forbidden_live)
    code, result = invoke(
        capsys,
        ["search", "--collection", "broken", "--mode", "jev", "--task", "summarize notes"],
    )
    assert code == 2
    assert result["status"] == "error"
    assert result["mode"] == "jev"
    assert result["selected"] == []
    assert result["catalog_size"] == 0
    assert result["warnings"]
    assert result["http_requests"] == 0
    assert "No valid skills" in result["error"]


def test_jev_search_with_only_rejected_skills_is_explicit_error(tmp_path, monkeypatch, capsys):
    root = tmp_path / "broken-skills"
    bad = root / "bad-skill"
    bad.mkdir(parents=True)
    (bad / "SKILL.md").write_text("no frontmatter here", encoding="utf-8")
    configure_collection("broken", [root])
    monkeypatch.setenv("JEV_API_KEY", "fixture-key")

    def forbidden_live(self, state, budget):
        raise AssertionError("empty catalogs must not reach Jev inference")

    monkeypatch.setattr(Router, "_live", forbidden_live)
    code, result = invoke(
        capsys,
        ["search", "--collection", "broken", "--mode", "jev", "--task", "summarize notes"],
    )
    assert code == 2
    assert result["status"] == "error"
    assert result["selected"] == []
    assert result["catalog_size"] == 0
    assert result["warnings"]
    assert result["http_requests"] == 0


def test_jev_semantic_no_match_stays_success(tmp_path, monkeypatch, capsys):
    root = tmp_path / "marketing"
    write_skill(root, "ads", "ads", "Plan paid advertising campaigns.", "Private ad instructions.")
    configure_collection("marketing", [root])
    monkeypatch.setenv("JEV_API_KEY", "fixture-key")

    def evaluated_no_match(self, state, budget):
        return {
            "status": "no_match",
            "selected": [],
            "catalog_size": len(self.catalog.skills),
            "shortlisted": 1,
            "models": ["test-model"],
            "retrieval": {"considered_skills": len(self.catalog.skills)},
        }

    monkeypatch.setattr(Router, "_live", evaluated_no_match)
    code, result = invoke(
        capsys,
        ["search", "--collection", "marketing", "--mode", "jev",
         "--task", "quantum cryptography"],
    )
    assert code == 0
    assert result["status"] == "no_match"
    assert result["selected"] == []
    assert result["catalog_size"] == 1


def test_jev_search_without_key_reports_credentials(tmp_path, monkeypatch, capsys):
    root = tmp_path / "marketing"
    write_skill(root, "ads", "ads", "Plan paid advertising campaigns.", "Body.")
    configure_collection("marketing", [root])
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    code, result = invoke(
        capsys,
        ["search", "--collection", "marketing", "--mode", "jev",
         "--task", "plan a paid advertising campaign"],
    )
    assert code == 2
    assert result["status"] == "error"
    assert "JEV_API_KEY" in result["error"]
