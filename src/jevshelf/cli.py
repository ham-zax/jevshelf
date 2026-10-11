from __future__ import annotations

import argparse
import hashlib
import shutil
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path, PureWindowsPath
from typing import Iterator

from jev_skill_router.catalog import BLOCKED_NAMES, TEXT_SUFFIXES, Catalog
from jev_skill_router.config import Config, RouterError
from jev_skill_router.jev import RequestBudget
from jev_skill_router.retrieval import MetadataIndex
from jev_skill_router.router import Router


COLLECTIONS = ("marketing", "thinking", "academic", "emil", "sentry")
# Only specialist Sentry capabilities are automatically routable; the whole
# upstream repository remains intact outside agent discovery.
SENTRY_SPECIALISTS = ("find-bugs", "code-simplifier", "security-review", "skill-scanner")
MAX_JEV_RESULTS = 3


def _config_file() -> Path:
    return Path(os.environ.get("JEVSHELF_CONFIG", "~/.config/jevshelf/collections.json")).expanduser().absolute()


def _specs() -> dict:
    """Read a user-owned collection manifest; no user's skills ship by default."""
    # Legacy per-collection override vars are used by older shims and tests.
    # A user-selected manifest always takes precedence.
    if not os.environ.get("JEVSHELF_CONFIG") and any(
        key.startswith("PANDORA_") and (key.endswith("_ROOT") or key == "PANDORA_SKILLS_SOURCE_DIR")
        for key in os.environ
    ):
        return {}
    path = _config_file()
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        collections = value.get("collections", {})
        if not isinstance(collections, dict) or any(
            not isinstance(name, str) or not isinstance(spec, dict)
            or not isinstance(spec.get("roots"), list)
            or not all(isinstance(root, str) and root.strip() for root in spec["roots"])
            for name, spec in collections.items()
        ):
            raise ValueError("Invalid collections mapping")
        return collections
    except (OSError, ValueError) as exc:
        raise RouterError(f"Invalid JevShelf configuration at {path}: {exc}") from exc


def _root_path(raw: str) -> Path:
    if raw.startswith("@repo/"):
        return (Path(__file__).resolve().parents[2] / raw[6:]).absolute()
    if raw.startswith("~/") or raw.startswith("/"):
        return Path(raw).expanduser().absolute()
    return (_config_file().parent / raw).absolute()


def _collection_names() -> tuple[str, ...]:
    configured = _specs()
    # Legacy collections remain supported for old local deployments and tests.
    if configured:
        return tuple(configured)
    if any(key.startswith("PANDORA_") for key in os.environ):
        return COLLECTIONS
    return ()


def _init_config() -> dict:
    target = _config_file()
    if target.exists():
        return {"status": "exists", "config": str(target), "collections": list(_specs())}
    target.parent.mkdir(parents=True, exist_ok=True)
    sample = Path(__file__).resolve().parents[2] / "examples" / "collections.json"
    shutil.copyfile(sample, target)
    return {"status": "created", "config": str(target), "collections": list(_specs())}


def _collection_root(name: str) -> Path:
    if name in _specs():
        roots = _specs()[name]["roots"]
        if not roots:
            raise RouterError(f"Collection '{name}' needs at least one root")
        return _root_path(roots[0])
    env_name = f"PANDORA_{name.upper()}_ROOT"
    configured = os.environ.get(env_name)
    if configured:
        return Path(configured).expanduser().absolute()
    project_root = Path(__file__).resolve().parents[2]
    skillshare_vault = {
        "academic": "vault-academic",
        "emil": "vault-emil",
        "sentry": "vault-sentry",
    }.get(name)
    if skillshare_vault:
        source = Path(os.environ.get("PANDORA_SKILLS_SOURCE_DIR", "~/.config/skillshare/skills")).expanduser()
        return (source / skillshare_vault).absolute()
    return (project_root / "vendor" / name / "skills").absolute()


def _collection_roots(name: str) -> list[str]:
    if name in _specs():
        return [str(_root_path(path)) for path in _specs()[name]["roots"]]
    root = _collection_root(name)
    if name in ("emil", "sentry"):
        skillshare_source = Path(
            os.environ.get("PANDORA_SKILLS_SOURCE_DIR", "~/.config/skillshare/skills")
        ).expanduser().absolute()
        shared = skillshare_source / "vault-lassejlv"
        additions = {
            "emil": ("no-vibe-code",),
            "sentry": ("backend-security-audit", "minimize-api-responses"),
        }[name]
        primary = ([str(root / skill) for skill in SENTRY_SPECIALISTS]
                   if name == "sentry" else [str(root)])
        specialist_roots = primary + [str(shared / skill) for skill in additions]
        if name == "emil":
            specialist_roots.append(str(skillshare_source / "vault-taste" / "taste-skill"))
        return specialist_roots
    return [str(root)]


def _catalog(name: str) -> Catalog:
    return Catalog(_collection_roots(name))


def _source_reference(skill, root: Path, name: str = "") -> str:
    """Do not leak absolute paths; distinguish skills in the shared managed vault."""
    try:
        return skill.source.relative_to(root.resolve()).as_posix()
    except ValueError:
        if name in _specs():
            for idx, configured_root in enumerate(_collection_roots(name)):
                base = Path(configured_root).resolve()
                try:
                    return f"root{idx}:" + skill.source.relative_to(base.parent).as_posix()
                except ValueError:
                    pass
        skillshare_source = Path(
            os.environ.get("PANDORA_SKILLS_SOURCE_DIR", "~/.config/skillshare/skills")
        ).expanduser().absolute().resolve()
        try:
            return "skillshare:" + skill.source.relative_to(skillshare_source).as_posix()
        except ValueError as exc:
            raise RouterError("Selected skill does not belong to the approved collection") from exc


def _metadata(skill, root: Path, name: str) -> dict:
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "source": _source_reference(skill, root, name),
        "digest": skill.digest,
    }


def _json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False))


def _collections() -> dict:
    entries = {}
    for name in _collection_names():
        root = _collection_root(name)
        catalog = _catalog(name)
        entries[name] = {"skills": len(catalog.skills), "path": str(root), "warnings": catalog.warnings}
    return {"collections": entries}


def _lexical_search(name: str, task: str, context: str, max_results: int) -> dict:
    started = time.perf_counter()
    root = _collection_root(name)
    catalog = _catalog(name)
    skills = list(catalog.skills.values())
    candidates = MetadataIndex(skills).search(f"{task}\n{context}", max_results)
    selected = [_metadata(catalog.skills[skill_id], root, name) for skill_id in candidates.ids]
    return {
        "collection": name,
        "mode": "lexical",
        "method": "metadata_bm25",
        "status": "selected" if selected else "no_match",
        "selected": selected,
        "matched_skills": candidates.matched_count,
        "catalog_size": len(skills),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


@contextmanager
def _mapped_api_key() -> Iterator[None]:
    """Temporarily expose the login-shell JEV_API_KEY to the upstream client."""
    current = os.environ.get("TYPESAFE_API_KEY")
    jev_key = os.environ.get("JEV_API_KEY")
    if (not current or not current.strip()) and jev_key is not None:
        os.environ["TYPESAFE_API_KEY"] = jev_key
        try:
            yield
        finally:
            if current is None:
                os.environ.pop("TYPESAFE_API_KEY", None)
            else:
                os.environ["TYPESAFE_API_KEY"] = current
    else:
        yield


def _client_metrics(router: Router, budget: RequestBudget) -> dict:
    client = router.client
    metrics = client.metrics_snapshot() if client is not None else {}
    usage = None
    if metrics.get("http_requests", 0) and not metrics.get("unreported_requests", 0):
        usage = {
            "input_tokens": metrics.get("input_tokens", 0),
            "output_tokens": metrics.get("output_tokens", 0),
        }
    return {
        "api_calls": metrics.get("api_calls", 0),
        "http_requests": metrics.get("http_requests", budget.used),
        "retry_requests": metrics.get("retry_requests", 0),
        "usage": usage,
    }


def _jev_search(name: str, task: str, context: str, max_results: int) -> dict:
    if not any(
        os.environ.get(key, "").strip()
        for key in ("JEV_API_KEY", "TYPESAFE_API_KEY")
    ):
        raise RouterError("Set JEV_API_KEY or TYPESAFE_API_KEY for live Jev search")
    if max_results > MAX_JEV_RESULTS:
        raise RouterError(f"Jev supports at most {MAX_JEV_RESULTS} selected skills per search")

    root = _collection_root(name)
    config = Config(roots=_collection_roots(name), mode="live", max_skills=max_results)
    router = Router(config)
    started = time.perf_counter()
    budget = RequestBudget(
        config.max_api_calls,
        time.monotonic() + config.route_timeout_seconds,
    )
    try:
        router.catalog.refresh()
        state = router._state(task, context)
        with _mapped_api_key():
            result = router._live(state, budget)
        metrics = _client_metrics(router, budget)
        selected = []
        for entry in result["selected"]:
            skill = router.catalog.skills[entry["id"]]
            selected.append(
                {
                    **_metadata(skill, root, name),
                    "fit": entry["fit"],
                    "score": entry["score"],
                    "confidence": entry["confidence"],
                }
            )
        return {
            "collection": name,
            "mode": "jev",
            "status": result["status"],
            "selected": selected,
            "catalog_size": result["catalog_size"],
            "shortlisted": result["shortlisted"],
            "models": result["models"],
            "retrieval": result["retrieval"],
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            **metrics,
        }
    except RouterError as exc:
        return {
            "collection": name,
            "mode": "jev",
            "status": "error",
            "selected": [],
            "error": str(exc),
            "catalog_size": len(router.catalog.skills),
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            **_client_metrics(router, budget),
        }
    finally:
        router.close()


def _search(args: argparse.Namespace) -> dict:
    if not args.task.strip():
        raise RouterError("task must be nonempty text")
    if args.mode == "lexical":
        return _lexical_search(args.collection, args.task, args.context, args.max_results)
    return _jev_search(args.collection, args.task, args.context, args.max_results)


def _load(args: argparse.Namespace) -> dict:
    if args.offset > 0 and args.expected_digest is None:
        raise RouterError("Continuation requires --expected-digest from the previous page")
    catalog = _catalog(args.collection)
    if args.id not in catalog.skills:
        raise RouterError("Unknown skill ID in the selected collection")
    return catalog.read(
        args.id,
        path=args.file,
        offset=args.offset,
        limit=args.limit,
        expected_digest=args.expected_digest,
    )



def _load_resource(args: argparse.Namespace) -> dict:
    """Read a pinned academic repository resource without escaping its root.

    Academic skills refer to shared/references and sibling agents/scripts.
    Those files cannot be read with the per-skill loader, which intentionally
    forbids parent traversal. This is an independent, read-only access path.
    """
    if args.collection != "academic":
        raise RouterError("Repository resources are supported only for academic")
    # Academic shared references and scripts live outside the five individual
    # skill folders. The pinned source checkout supplies them read-only.
    root = Path(os.environ.get(
        "PANDORA_ACADEMIC_RESOURCE_ROOT",
        str(Path(__file__).resolve().parents[2] / "vendor" / "academic"),
    )).expanduser().absolute()
    # Skillshare independently updates installed skills, so refuse stale or
    # mismatched shared resources rather than mixing incompatible repo versions.
    for installed_skill in _catalog("academic").skills.values():
        original = root / installed_skill.name / "SKILL.md"
        if not original.is_file() or original.read_bytes() != installed_skill.source.read_bytes():
            raise RouterError(
                "Academic Skillshare skills and pinned shared resources differ; align their upstream revisions"
            )
    requested = args.file
    relative = Path(requested)
    allowed_top = {
        "shared", "scripts", "agents", "academic-paper",
        "academic-paper-reviewer", "academic-pipeline",
        "deep-research", "sr-screener",
    }
    if (
        not requested or "\\" in requested or relative.is_absolute()
        or PureWindowsPath(requested).drive
        or len(relative.parts) < 2 or relative.parts[0] not in allowed_top
        or any(part in (".", "..") or part.startswith(".") for part in relative.parts)
        or any(part.lower() in BLOCKED_NAMES for part in relative.parts)
        or relative.suffix.lower() not in TEXT_SUFFIXES
    ):
        raise RouterError("Only allowed academic repository-relative text files are supported")
    if args.offset < 0 or not 1 <= args.limit <= 50000:
        raise RouterError("Invalid read range")
    if args.offset and not args.expected_digest:
        raise RouterError("Continuation requires --expected-digest from the previous page")
    if args.expected_digest is not None and (
        len(args.expected_digest) != 64
        or any(c not in "0123456789abcdef" for c in args.expected_digest)
    ):
        raise RouterError("expected_digest must be a lowercase SHA-256 digest")
    target = root / relative
    Catalog._no_symlinks(target)
    if not target.resolve().is_relative_to(root.resolve()):
        raise RouterError("Path escapes the academic repository")
    content = Catalog._text(target)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if args.expected_digest and args.expected_digest != digest:
        raise RouterError("File changed since it was read; restart reading")
    if args.offset > len(content):
        raise RouterError("Offset is beyond the end of the file")
    end = min(len(content), args.offset + args.limit)
    return {
        "collection": args.collection,
        "path": requested,
        "content": content[args.offset:end],
        "content_digest": digest,
        "offset": args.offset,
        "next_offset": end if end < len(content) else None,
        "total_chars": len(content),
        "base_directory": str(root.resolve()),
    }


def _plan(args: argparse.Namespace) -> dict:
    if not args.task.strip():
        raise RouterError("task must be nonempty text")
    root = _collection_root(args.collection)
    router = Router(Config(roots=_collection_roots(args.collection), mode="live"))
    try:
        return {"collection": args.collection, **router.plan(args.task, args.context)}
    finally:
        router.close()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jevshelf")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("collections", help="List configured collections and skill counts")
    commands.add_parser("init", help="Create an example collection config in your home directory")

    search = commands.add_parser("search", help="Search one collection without loading skill bodies")
    search.add_argument("--collection", choices=_collection_names(), required=True)
    search.add_argument("--mode", choices=("lexical", "jev"), required=True)
    search.add_argument("--task", required=True)
    search.add_argument("--context", default="")
    search.add_argument("--max-results", type=int, default=3)

    load = commands.add_parser("load", help="Read a bounded page from one skill")
    load.add_argument("--collection", choices=_collection_names(), required=True)
    load.add_argument("--id", required=True)
    load.add_argument("--file", default="SKILL.md")
    load.add_argument("--offset", type=int, default=0)
    load.add_argument("--limit", type=int, default=12000)
    load.add_argument("--expected-digest")

    resource = commands.add_parser(
        "load-resource", help="Read a bounded academic repository-level reference"
    )
    resource.add_argument("--collection", choices=("academic",), required=True)
    resource.add_argument("--file", required=True)
    resource.add_argument("--offset", type=int, default=0)
    resource.add_argument("--limit", type=int, default=12000)
    resource.add_argument("--expected-digest")

    plan = commands.add_parser("plan", help="Plan a Jev request without authentication or network access")
    plan.add_argument("--collection", choices=_collection_names(), required=True)
    plan.add_argument("--task", required=True)
    plan.add_argument("--context", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            _json(_init_config())
            return 0
        if args.command == "collections":
            _json(_collections())
            return 0
        if args.command == "search":
            result = _search(args)
            _json(result)
            return 2 if result["status"] == "error" else 0
        if args.command == "load":
            _json(_load(args))
            return 0
        if args.command == "load-resource":
            _json(_load_resource(args))
            return 0
        if args.command == "plan":
            _json(_plan(args))
            return 0
    except RouterError as exc:
        error = {"status": "error", "error": str(exc)}
        if getattr(args, "collection", None):
            error["collection"] = args.collection
        if getattr(args, "mode", None):
            error["mode"] = args.mode
        _json(error)
        return 2
    except OSError:
        _json({"status": "error", "error": "Local file operation failed"})
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
