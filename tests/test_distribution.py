"""Distribution checks: the built wheel must serve the demo without the checkout.

These tests build a real wheel from the working tree into a pytest temporary
directory (never into the repository), then drive the public ``jevshelf``
console command against the extracted wheel with the working directory outside
the checkout. They prove ``init -> collections -> lexical search ->
digest-checked load`` works for ordinary non-editable installs.
"""

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CONSOLE = Path(sys.executable).parent / "jevshelf"
DEMO_SKILLS = ("refine-writing", "summarize-notes")


def stage_scratch_project(scratch: Path) -> Path:
    """Copy the minimal build inputs to scratch; the checkout is never a cwd.

    Only files the wheel build reads are copied. Build backends write
    ``build/`` and ``*.egg-info`` next to the project directory, so invoking
    them here keeps every write inside pytest-managed temporary state.
    """
    project = scratch / "project"
    project.mkdir()
    for name in ("pyproject.toml", "MANIFEST.in", "README.md", "LICENSE"):
        shutil.copy2(REPO_ROOT / name, project / name)
    shutil.copytree(
        REPO_ROOT / "src", project / "src",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    return project


def try_uv_build(project: Path, out_dir: Path, cache_dir: Path) -> Path | None:
    """Prefer the documented ``uv build --offline`` path when its cache works."""
    if shutil.which("uv") is None:
        return None
    env = dict(os.environ)
    env["UV_CACHE_DIR"] = str(cache_dir)
    build = subprocess.run(
        ["uv", "build", "--wheel", "--offline", "--out-dir", str(out_dir)],
        cwd=project, capture_output=True, text=True, timeout=180, env=env,
    )
    if build.returncode != 0:
        return None
    wheels = sorted(out_dir.glob("jevshelf-*.whl"))
    return wheels[0] if len(wheels) == 1 else None


def setuptools_version() -> tuple[int, ...] | None:
    if shutil.which("python3") is None:
        return None
    probe = subprocess.run(
        ["python3", "-c", "import setuptools; print(setuptools.__version__)"],
        capture_output=True, text=True, timeout=60,
    )
    if probe.returncode != 0:
        return None
    try:
        return tuple(int(part) for part in probe.stdout.strip().split(".")[:2])
    except ValueError:
        return None


def try_backend_build(project: Path, out_dir: Path) -> Path | None:
    """Drive a compatible build backend directly; never accept an older one."""
    version = setuptools_version()
    if version is None:
        return None
    if version < (68,):
        pytest.skip(
            f"system setuptools {'.'.join(map(str, version))} is older than the "
            "required setuptools>=68; refusing it as packaging proof"
        )
    build = subprocess.run(
        ["python3", "-c",
         "from setuptools.build_meta import build_wheel; import sys; print(build_wheel(sys.argv[1]))",
         str(out_dir)],
        cwd=project, capture_output=True, text=True, timeout=240,
    )
    assert build.returncode == 0, build.stderr
    wheels = sorted(out_dir.glob("jevshelf-*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def build_wheel(scratch: Path) -> Path:
    """Build a real wheel offline from a scratch copy of the build inputs."""
    project = stage_scratch_project(scratch)
    out_dir = scratch / "dist"
    out_dir.mkdir()
    wheel = try_uv_build(project, out_dir, scratch / "uvcache")
    if wheel is not None:
        return wheel
    wheel = try_backend_build(project, out_dir)
    if wheel is not None:
        return wheel
    pytest.skip("no offline wheel-build capability: uv --offline cache missed and system setuptools>=68 is unavailable")


@pytest.fixture()
def wheel_site(tmp_path):
    wheel = build_wheel(tmp_path)
    site = tmp_path / "site"
    site.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(site)
    yield wheel, site


def wheel_env(site: Path, config: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(site)
    env["JEVSHELF_CONFIG"] = str(config)
    env.pop("JEV_API_KEY", None)
    env.pop("TYPESAFE_API_KEY", None)
    return env


def run_console(args: list[str], *, env: dict, cwd: Path) -> tuple[int, dict]:
    completed = subprocess.run(
        [str(CONSOLE), *args],
        capture_output=True, text=True, timeout=120, cwd=cwd, env=env,
    )
    assert "Traceback" not in completed.stderr
    return completed.returncode, json.loads(completed.stdout)


def test_wheel_contains_demo_assets(wheel_site):
    wheel, _site = wheel_site
    names = set(zipfile.ZipFile(wheel).namelist())
    assert "jevshelf/demo/collections.json" in names
    for skill in DEMO_SKILLS:
        assert f"jevshelf/demo/skills/{skill}/SKILL.md" in names


def test_demo_and_examples_skill_bodies_match():
    for skill in DEMO_SKILLS:
        shipped = (REPO_ROOT / "src" / "jevshelf" / "demo" / "skills" / skill / "SKILL.md").read_bytes()
        example = (REPO_ROOT / "examples" / "skills" / skill / "SKILL.md").read_bytes()
        assert shipped == example


def test_installed_wheel_serves_demo_without_checkout(tmp_path, wheel_site):
    _wheel, site = wheel_site
    home = tmp_path / "fake-home"
    home.mkdir()
    config = home / "collections.json"
    env = wheel_env(site, config)

    prove = subprocess.run(
        [sys.executable, "-c", "import jevshelf; print(jevshelf.__file__)"],
        capture_output=True, text=True, timeout=120, cwd=tmp_path, env=env,
    )
    assert prove.returncode == 0
    location = Path(prove.stdout.strip()).resolve()
    assert str(location).startswith(str(site.resolve())), location

    code, created = run_console(["init"], env=env, cwd=tmp_path)
    assert code == 0
    assert created["status"] == "created"
    manifest = json.loads(config.read_text())
    assert manifest["collections"]["writing"]["roots"] == ["@demo/skills"]

    code, collections = run_console(["collections"], env=env, cwd=tmp_path)
    assert code == 0
    assert collections["collections"]["writing"]["skills"] == 2

    code, found = run_console(
        ["search", "--collection", "writing", "--mode", "lexical",
         "--task", "summarize the meeting notes and identify next actions"],
        env=env, cwd=tmp_path,
    )
    assert code == 0
    assert found["status"] == "selected"
    skill = next(s for s in found["selected"] if s["name"] == "summarize-notes")

    code, loaded = run_console(
        ["load", "--collection", "writing", "--id", skill["id"],
         "--expected-digest", skill["digest"]],
        env=env, cwd=tmp_path,
    )
    assert code == 0
    assert "Summarize the notes" in loaded["content"]
