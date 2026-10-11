from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import unicodedata
from contextlib import contextmanager
from importlib import resources as _resources
from pathlib import Path, PureWindowsPath
from typing import Iterator

from jev_skill_router.catalog import BLOCKED_NAMES, TEXT_SUFFIXES, Catalog
from jev_skill_router.config import Config, RouterError
from jev_skill_router.jev import RequestBudget
from jev_skill_router.retrieval import MetadataIndex
from .selection import Router, VERIFICATION_CANDIDATES


MAX_JEV_RESULTS = 3


def _config_file() -> Path:
    return Path(os.environ.get("JEVSHELF_CONFIG", "~/.config/jevshelf/collections.json")).expanduser().absolute()


def _reject_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant {value}")


def _specs() -> dict:
    """Read only the user's explicit collection manifest."""
    path = _config_file()
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
        if not isinstance(value, dict):
            raise ValueError("Top-level JSON must be an object")
        collections = value.get("collections", {})
        if not isinstance(collections, dict) or any(
            not isinstance(name, str) or not isinstance(spec, dict)
            or not isinstance(spec.get("roots"), list)
            or not spec["roots"]
            or not all(isinstance(root, str) and root.strip() for root in spec["roots"])
            for name, spec in collections.items()
        ):
            raise ValueError("Invalid collections mapping")
        return collections
    except (OSError, ValueError) as exc:
        raise RouterError(f"Invalid JevShelf configuration at {path}: {exc}") from exc


def _demo_root(raw: str) -> Path:
    """Resolve an @demo/ path against demo assets shipped inside the package.

    This is independent of the source checkout and the working directory, so
    ordinary wheel installations can serve the demo collection. The local
    catalog still validates the resolved directory before indexing it.
    """
    rest = "" if raw == "@demo" else raw[len("@demo/"):]
    if "\\" in rest or Path(rest).is_absolute() or ".." in Path(rest).parts:
        raise RouterError(f"Invalid demo path {raw!r}")
    try:
        base = _resources.files("jevshelf") / "demo"
        with _resources.as_file(base) as demo_dir:
            return (demo_dir / rest).absolute()
    except RouterError:
        raise
    except Exception as exc:
        raise RouterError(f"Demo assets are unavailable: {exc}") from exc


def _demo_template() -> str:
    """Read the packaged demo manifest, independent of the checkout."""
    try:
        text = (_resources.files("jevshelf") / "demo" / "collections.json").read_text(encoding="utf-8")
    except RouterError:
        raise
    except Exception as exc:
        raise RouterError(f"Demo assets are unavailable: {exc}") from exc
    value = json.loads(text)
    if not isinstance(value, dict) or "writing" not in value.get("collections", {}):
        raise RouterError("Demo assets are unavailable")
    return text


def _root_path(raw: str) -> Path:
    if raw == "@demo" or raw.startswith("@demo/"):
        return _demo_root(raw)
    if raw.startswith("@repo/"):
        return (Path(__file__).resolve().parents[2] / raw[6:]).absolute()
    if raw.startswith("~/") or raw.startswith("/"):
        return Path(raw).expanduser().absolute()
    return (_config_file().parent / raw).absolute()


def _collection_names() -> tuple[str, ...]:
    return tuple(_specs())


def _init_config() -> dict:
    target = _config_file()
    if target.exists():
        return {"status": "exists", "config": str(target), "collections": list(_specs())}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_demo_template(), encoding="utf-8")
    return {"status": "created", "config": str(target), "collections": list(_specs())}


def _collection_root(name: str) -> Path:
    configured = _specs().get(name)
    if configured is None:
        raise RouterError(f"Unknown collection '{name}'; configure it in {_config_file()}")
    return _root_path(configured["roots"][0])


def _collection_roots(name: str) -> list[str]:
    configured = _specs().get(name)
    if configured is None:
        raise RouterError(f"Unknown collection '{name}'")
    return [str(_root_path(path)) for path in configured["roots"]]


def _catalog(name: str) -> Catalog:
    return Catalog(_collection_roots(name))


def _source_reference(skill, root: Path, name: str) -> str:
    """Return source locations relative to approved configured roots only."""
    try:
        return skill.source.relative_to(root.resolve()).as_posix()
    except ValueError:
        for idx, configured_root in enumerate(_collection_roots(name)):
            base = Path(configured_root).resolve()
            try:
                return f"root{idx}:" + skill.source.relative_to(base).as_posix()
            except ValueError:
                continue
        raise RouterError("Selected skill does not belong to the approved collection")


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
    # Exact names are local identifiers, not a semantic relevance judgment.
    normalize = lambda value: unicodedata.normalize("NFKC", value).strip().casefold()
    exact = sorted((s for s in skills if normalize(s.name) == normalize(task)), key=lambda s: s.id)
    if exact:
        if not 1 <= max_results <= 10000:
            raise RouterError("Retrieval needs a candidate limit from 1 to 10000")
        selected = [_metadata(skill, root, name) for skill in exact[:max_results]]
        method, matched_count = "exact_name", len(exact)
    else:
        candidates = MetadataIndex(skills).search(f"{task}\n{context}", max_results)
        selected = [_metadata(catalog.skills[skill_id], root, name) for skill_id in candidates.ids]
        method, matched_count = "metadata_bm25", candidates.matched_count
    return {
        "collection": name,
        "mode": "lexical",
        "method": method,
        "status": "selected" if selected else "no_match",
        "selected": selected,
        "matched_skills": matched_count,
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
    config = Config(roots=_collection_roots(name), mode="live", max_skills=max_results, shortlist=VERIFICATION_CANDIDATES)
    router = Router(config)
    started = time.perf_counter()
    budget = RequestBudget(
        config.max_api_calls,
        time.monotonic() + config.route_timeout_seconds,
    )
    try:
        router.catalog.refresh()
        if not router.catalog.skills:
            raise RouterError("No valid skills found; check roots and warnings")
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
            "warnings": list(router.catalog.warnings),
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
    """Read explicitly allowed repository-level resources without directory escape."""
    spec = _specs().get(args.collection)
    if spec is None:
        raise RouterError(f"Unknown collection '{args.collection}'; configure it in {_config_file()}")
    raw_root = spec.get("resources_root")
    allowed = spec.get("resources_allowlist")
    if not isinstance(raw_root, str) or not isinstance(allowed, list) or not allowed:
        raise RouterError("This collection does not configure repository resources")
    if not all(isinstance(v, str) and v and "/" not in v and v not in (".", "..") for v in allowed):
        raise RouterError("Invalid collection resource allowlist")
    root = _root_path(raw_root)
    requested = args.file
    relative = Path(requested)
    if (
        not requested or "\\" in requested or relative.is_absolute()
        or PureWindowsPath(requested).drive
        or len(relative.parts) < 2 or relative.parts[0] not in allowed
        or any(part in (".", "..") or part.startswith(".") for part in relative.parts)
        or any(part.lower() in BLOCKED_NAMES for part in relative.parts)
        or relative.suffix.lower() not in TEXT_SUFFIXES
    ):
        raise RouterError("Only allowlisted repository-relative text files are supported")
    if args.offset < 0 or not 1 <= args.limit <= 50000:
        raise RouterError("Invalid read range")
    if args.offset and not args.expected_digest:
        raise RouterError("Continuation requires --expected-digest from the previous page")
    if args.expected_digest is not None and (
        len(args.expected_digest) != 64
        or any(c not in "0123456789abcdef" for c in args.expected_digest)
    ):
        raise RouterError("expected_digest must be a lowercase SHA-256 digest")
    if spec.get("verify_resources_against_skills", False):
        for installed_skill in _catalog(args.collection).skills.values():
            original = root / installed_skill.name / "SKILL.md"
            if not original.is_file() or original.read_bytes() != installed_skill.source.read_bytes():
                raise RouterError("Collection skill files and repository resources differ; align their revisions")
    target = root / relative
    Catalog._no_symlinks(target)
    if not target.resolve().is_relative_to(root.resolve()):
        raise RouterError("Path escapes the configured resource repository")
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
    router = Router(Config(roots=_collection_roots(args.collection), mode="live", shortlist=VERIFICATION_CANDIDATES))
    try:
        return {"collection": args.collection, **router.plan(args.task, args.context)}
    finally:
        router.close()


def _parser() -> argparse.ArgumentParser:
    # Parser construction must not read the user manifest: collection names
    # are validated after parsing so --help stays usable with a broken config.
    parser = argparse.ArgumentParser(prog="jevshelf")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("collections", help="List configured collections and skill counts")
    commands.add_parser("init", help="Create an example collection config in your home directory")

    search = commands.add_parser("search", help="Search one collection without loading skill bodies")
    search.add_argument("--collection", required=True)
    search.add_argument("--mode", choices=("lexical", "jev"), required=True)
    search.add_argument("--task", required=True)
    search.add_argument("--context", default="")
    search.add_argument("--max-results", type=int, default=3)

    load = commands.add_parser("load", help="Read a bounded page from one skill")
    load.add_argument("--collection", required=True)
    load.add_argument("--id", required=True)
    load.add_argument("--file", default="SKILL.md")
    load.add_argument("--offset", type=int, default=0)
    load.add_argument("--limit", type=int, default=12000)
    load.add_argument("--expected-digest")

    resource = commands.add_parser(
        "load-resource", help="Read an explicitly configured, bounded repository-level reference"
    )
    resource.add_argument("--collection", required=True)
    resource.add_argument("--file", required=True)
    resource.add_argument("--offset", type=int, default=0)
    resource.add_argument("--limit", type=int, default=12000)
    resource.add_argument("--expected-digest")

    plan = commands.add_parser("plan", help="Plan a Jev request without authentication or network access")
    plan.add_argument("--collection", required=True)
    plan.add_argument("--task", required=True)
    plan.add_argument("--context", default="")
    return parser


def _require_collection(args: argparse.Namespace) -> None:
    if args.command in ("search", "load", "load-resource", "plan"):
        if args.collection not in _specs():
            raise RouterError(f"Unknown collection '{args.collection}'; configure it in {_config_file()}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        _require_collection(args)
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
