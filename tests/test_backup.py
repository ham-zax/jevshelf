"""Regression tests for scripts/backup-skillshare.sh findings 1 and 2.

Privacy gate: every effective push destination (separate/multiple pushurls,
Git URL rewrites) must resolve to a gh-verified PRIVATE github.com repository
over HTTPS, scp-like SSH, or ssh:// forms; anything else fails closed.
Archive exclusion: *.bundle/*.tar(*.gz)/*.tgz/*.zip must never enter the
mirror snapshot while normal skill content does.

All fixtures use dummy local Git repositories. Network is never touched: the
`gh` CLI is faked per test and `git push` is intercepted by a shim that only
records the attempt. No real push is executed.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKUP_SCRIPT = REPO_ROOT / "scripts" / "backup-skillshare.sh"
REAL_GIT = shutil.which("git")
assert REAL_GIT, "git must be on PATH for backup tests"


FAKE_GH = """#!/usr/bin/env bash
repo=""
for a in "$@"; do
  case "$a" in
    */*) repo="$a" ;;
  esac
done
# The script must pin the query to the explicit github.com URL so GH_HOST or
# the invoking directory cannot redirect it; refuse anything else outright.
case "$repo" in
  https://github.com/?*/?*) short="${repo#https://github.com/}" ;;
  *) echo "unpinned-query:${repo:-unknown}" >> "${GH_CALL_LOG:-/dev/null}"; exit 4 ;;
esac
short="${short%.git}"
echo "$short" >> "${GH_CALL_LOG:-/dev/null}"
code="${FAKE_GH_EXIT:-0}"
if (( code != 0 )); then exit "$code"; fi
vis="${FAKE_GH_VISIBILITY:-PRIVATE}"
if [[ -n "${FAKE_GH_MAP:-}" ]]; then
  for pair in $FAKE_GH_MAP; do
    if [[ "$pair" == "$short="* ]]; then vis="${pair#*=}"; fi
  done
fi
echo "$vis"
exit 0
"""

# Intercepts only `git push` (records it); every other git invocation runs
# the real binary. The backup script pushes solely via `git ... push ...`.
GIT_SHIM = """#!/usr/bin/env bash
for a in "$@"; do
  if [[ "$a" == "push" ]]; then
    echo "push $*" >> "${GIT_PUSH_LOG:-/dev/null}"
    exit 0
  fi
done
exec "$REAL_GIT" "$@"
"""


@pytest.fixture()
def harness(tmp_path, monkeypatch):
    """Dummy Skillshare source/config plus faked gh and push interception."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "gh").write_text(FAKE_GH, encoding="utf-8")
    (bindir / "git").write_text(GIT_SHIM, encoding="utf-8")
    for tool in ("gh", "git"):
        path = bindir / tool
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    source = tmp_path / "source"
    source.mkdir()
    run([REAL_GIT, "init", "-q", "-b", "main"], cwd=source)
    write_skill(source, "hello", "normal skill body")
    config = tmp_path / "skillshare.yaml"
    config.write_text("targets: []\n", encoding="utf-8")

    checkout = tmp_path / "checkout"
    state = tmp_path / "state"
    state.mkdir()
    push_log = tmp_path / "push.log"
    gh_log = tmp_path / "gh.log"

    env = {
        "SKILLSHARE_SOURCE": str(source),
        "SKILLSHARE_CONFIG": str(config),
        "JEVSHELF_COLLECTIONS_CONFIG": str(tmp_path / "no-collections.json"),
        "JEVSHELF_BACKUP_CHECKOUT": str(checkout),
        "JEVSHELF_BACKUP_STATE_DIR": str(state),
        "JEVSHELF_BACKUP_REMOTE": "https://github.com/test-owner/private-backup.git",
        "GIT_PUSH_LOG": str(push_log),
        "GH_CALL_LOG": str(gh_log),
        "REAL_GIT": REAL_GIT,
        "FAKE_GH_VISIBILITY": "PRIVATE",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("PATH", str(bindir) + os.pathsep + os.environ["PATH"])
    monkeypatch.delenv("FAKE_GH_EXIT", raising=False)
    monkeypatch.delenv("FAKE_GH_MAP", raising=False)
    return {
        "source": source,
        "config": config,
        "checkout": checkout,
        "push_log": push_log,
        "gh_log": gh_log,
        "mp": monkeypatch,
    }


def run(argv, **kwargs):
    return subprocess.run(argv, capture_output=True, text=True, **kwargs)


def write_skill(source: Path, name: str, body: str) -> Path:
    skill_dir = source / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(f"# {name}\n\n{body}\n", encoding="utf-8")
    return skill_file


def run_backup(harness, **overrides):
    monkeypatch = harness["mp"]
    for key, value in overrides.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    return run(["bash", str(BACKUP_SCRIPT)])


def pushes(harness):
    if not harness["push_log"].exists():
        return []
    return harness["push_log"].read_text(encoding="utf-8").splitlines()


def gh_calls(harness):
    if not harness["gh_log"].exists():
        return []
    return harness["gh_log"].read_text(encoding="utf-8").splitlines()


def set_origin_push_url(harness, *pushurls):
    checkout = harness["checkout"]
    run([REAL_GIT, "-C", str(checkout), "config", "--unset-all",
         "remote.origin.pushurl"], check=False)
    for url in pushurls:
        run([REAL_GIT, "-C", str(checkout), "config", "--add",
             "remote.origin.pushurl", url], check=True)


def test_private_https_push_succeeds(harness):
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 0, result.stderr
    assert len(pushes(harness)) == 1
    assert gh_calls(harness) == ["test-owner/private-backup"]


def test_public_https_push_refused(harness):
    result = run_backup(harness, FAKE_GH_VISIBILITY="PUBLIC")
    assert result.returncode == 3
    assert "not PRIVATE" in result.stderr
    assert pushes(harness) == []


def test_scp_like_ssh_url_is_checked(harness, monkeypatch):
    run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    monkeypatch.setenv(
        "JEVSHELF_BACKUP_REMOTE", "git@github.com:ssh-owner/ssh-backup.git")
    shutil.rmtree(harness["checkout"])
    harness["push_log"].unlink()
    harness["gh_log"].unlink()
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 0, result.stderr
    assert gh_calls(harness) == ["ssh-owner/ssh-backup"]
    assert len(pushes(harness)) == 1


def test_ssh_scheme_url_is_checked(harness, monkeypatch):
    run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    monkeypatch.setenv(
        "JEVSHELF_BACKUP_REMOTE", "ssh://git@github.com/ssh-owner/ssh-backup.git")
    shutil.rmtree(harness["checkout"])
    harness["push_log"].unlink()
    harness["gh_log"].unlink()
    result = run_backup(harness, FAKE_GH_VISIBILITY="PUBLIC")
    assert result.returncode == 3
    assert "not PRIVATE" in result.stderr
    assert gh_calls(harness) == ["ssh-owner/ssh-backup"]
    assert pushes(harness) == []


def test_separate_public_pushurl_refused(harness):
    assert run_backup(harness).returncode == 0
    set_origin_push_url(harness, "https://github.com/other/public-mirror.git")
    head = run([REAL_GIT, "-C", str(harness["checkout"]), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(harness["checkout"]), "update-ref",
         "refs/remotes/origin/main", head], check=True)
    write_skill(harness["source"], "another", "new content")
    result = run_backup(
        harness, FAKE_GH_MAP="other/public-mirror=PUBLIC")
    assert result.returncode == 3
    assert "not PRIVATE" in result.stderr
    assert len(pushes(harness)) == 1  # only the earlier private push


def test_all_pushurls_must_be_private(harness):
    assert run_backup(harness).returncode == 0
    set_origin_push_url(
        harness,
        "https://github.com/test-owner/private-backup.git",
        "git@github.com:other/public-mirror.git",
    )
    head = run([REAL_GIT, "-C", str(harness["checkout"]), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(harness["checkout"]), "update-ref",
         "refs/remotes/origin/main", head], check=True)
    write_skill(harness["source"], "another", "new content")
    result = run_backup(
        harness,
        FAKE_GH_MAP="test-owner/private-backup=PRIVATE other/public-mirror=PUBLIC",
    )
    assert result.returncode == 3
    assert len(pushes(harness)) == 1
    calls = gh_calls(harness)
    assert "test-owner/private-backup" in calls
    assert "other/public-mirror" in calls


def test_all_private_pushurls_succeed(harness):
    assert run_backup(harness).returncode == 0
    set_origin_push_url(
        harness,
        "https://github.com/test-owner/private-backup.git",
        "git@github.com:test-owner/second-private.git",
    )
    head = run([REAL_GIT, "-C", str(harness["checkout"]), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(harness["checkout"]), "update-ref",
         "refs/remotes/origin/main", head], check=True)
    write_skill(harness["source"], "another", "new content")
    result = run_backup(
        harness,
        FAKE_GH_MAP="test-owner/private-backup=PRIVATE test-owner/second-private=PRIVATE",
    )
    assert result.returncode == 0, result.stderr
    assert len(pushes(harness)) == 2


def test_push_insteadOf_rewrite_is_validated(harness):
    assert run_backup(harness).returncode == 0
    checkout = harness["checkout"]
    # A rewrite that redirects pushes to a public repo must be caught even
    # though the configured fetch URL looks private.
    run([REAL_GIT, "-C", str(checkout), "config",
         "url.https://github.com/other/public-mirror.git.pushInsteadOf",
         "https://github.com/test-owner/private-backup.git"], check=True)
    head = run([REAL_GIT, "-C", str(checkout), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(checkout), "update-ref",
         "refs/remotes/origin/main", head], check=True)
    write_skill(harness["source"], "another", "new content")
    result = run_backup(
        harness, FAKE_GH_MAP="other/public-mirror=PUBLIC")
    assert result.returncode == 3
    assert gh_calls(harness)[-1] == "other/public-mirror"
    assert len(pushes(harness)) == 1


def test_unknown_host_refused_without_gh(harness, monkeypatch):
    monkeypatch.setenv(
        "JEVSHELF_BACKUP_REMOTE", "https://gitlab.com/someone/mirror.git")
    shutil.rmtree(harness["checkout"], ignore_errors=True)
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 3
    assert "unsupported destination" in result.stderr
    assert pushes(harness) == []
    assert gh_calls(harness) == []


def test_gh_failure_fails_closed(harness):
    result = run_backup(harness, FAKE_GH_EXIT="1")
    assert result.returncode == 3
    assert "could not verify" in result.stderr
    assert pushes(harness) == []


def test_gh_host_override_still_queries_github(harness):
    # A hostile GH_HOST must not redirect the privacy query to an
    # enterprise host: the script pins the explicit github.com URL. The
    # fake gh exits 4 on any unpinned query, which the script turns into
    # a refusal, so success here proves the pin. No network is used.
    result = run_backup(
        harness,
        FAKE_GH_VISIBILITY="PRIVATE",
        GH_HOST="ghe.example.com",
        GH_ENTERPRISE_TOKEN="dummy-token",
    )
    assert result.returncode == 0, result.stderr
    assert gh_calls(harness) == ["test-owner/private-backup"]
    assert len(pushes(harness)) == 1


def test_noop_performs_no_network(harness):
    assert run_backup(harness).returncode == 0
    assert len(pushes(harness)) == 1
    head = run([REAL_GIT, "-C", str(harness["checkout"]), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(harness["checkout"]), "update-ref",
         "refs/remotes/origin/main", head], check=True)
    harness["gh_log"].unlink()
    harness["push_log"].unlink()
    result = run_backup(harness)
    assert result.returncode == 0, result.stderr
    assert "No changes" in result.stdout
    assert pushes(harness) == []
    assert gh_calls(harness) == []


def test_archives_excluded_from_mirror_and_commit(harness):
    source = harness["source"]
    (source / "history.bundle").write_text("bundle-data", encoding="utf-8")
    (source / "snapshot.tar.gz").write_text("tar-data", encoding="utf-8")
    backups = source / "backups"
    backups.mkdir()
    (backups / "working.zip").write_text("zip-data", encoding="utf-8")
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 0, result.stderr
    checkout = harness["checkout"]
    assert (checkout / "skills" / "hello" / "SKILL.md").is_file()
    assert not (checkout / "skills" / "history.bundle").exists()
    assert not (checkout / "skills" / "snapshot.tar.gz").exists()
    assert not (checkout / "skills" / "backups" / "working.zip").exists()
    tree = run([REAL_GIT, "-C", str(checkout), "ls-tree", "-r", "--name-only",
                "HEAD"], check=True).stdout.splitlines()
    assert "skills/hello/SKILL.md" in tree
    assert not any(name.endswith((".bundle", ".tar.gz", ".zip")) for name in tree)


def pending_history(checkout):
    return run([REAL_GIT, "-C", str(checkout), "rev-list", "--objects",
                "HEAD", "--not", "refs/remotes/origin/main"],
               check=True).stdout


def mark_synced(checkout):
    head = run([REAL_GIT, "-C", str(checkout), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(checkout), "update-ref",
         "refs/remotes/origin/main", head], check=True)


@pytest.mark.parametrize("archive_path", ["history.bundle", "archive.zip/tree.md"])
def test_unsynced_legacy_archive_refuses_push(harness, archive_path):
    assert run_backup(harness).returncode == 0
    checkout = harness["checkout"]
    mark_synced(checkout)
    # A local-only commit from before the exclusion, never pushed.
    legacy = checkout / "skills" / archive_path
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("dummy-archive-only", encoding="utf-8")
    run([REAL_GIT, "-C", str(checkout), "add", "-A"], check=True)
    run([REAL_GIT, "-C", str(checkout), "-c", "user.name=t", "-c",
         "user.email=t@t", "commit", "-qm", "legacy unsynced archive"],
        check=True)
    harness["push_log"].write_text("", encoding="utf-8")
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 3
    assert "pending local history contains archive files" in result.stderr
    assert pushes(harness) == []
    assert f"skills/{archive_path}" in pending_history(checkout)


def test_synced_archive_cleanup_is_not_blocked(harness):
    assert run_backup(harness).returncode == 0
    checkout = harness["checkout"]
    # The archive reached the remote before the exclusion existed; deleting
    # it locally must remain pushable.
    legacy = checkout / "skills" / "history.bundle"
    legacy.write_text("dummy-archive-only", encoding="utf-8")
    run([REAL_GIT, "-C", str(checkout), "add", "-A"], check=True)
    run([REAL_GIT, "-C", str(checkout), "-c", "user.name=t", "-c",
         "user.email=t@t", "commit", "-qm", "legacy synced archive"],
        check=True)
    mark_synced(checkout)
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 0, result.stderr
    assert not legacy.exists()
    assert len(pushes(harness)) == 2


def test_previously_mirrored_archive_is_removed(harness):
    # The archive lives in the source tree, as in pre-exclusion snapshots.
    (harness["source"] / "history.bundle").write_text("bundle-data", encoding="utf-8")
    assert run_backup(harness).returncode == 0
    checkout = harness["checkout"]
    # Simulate a snapshot from before the exclusion existed.
    legacy = checkout / "skills" / "history.bundle"
    legacy.write_text("bundle-data", encoding="utf-8")
    run([REAL_GIT, "-C", str(checkout), "add", "-A"], check=True)
    run([REAL_GIT, "-C", str(checkout), "-c", "user.name=t", "-c",
         "user.email=t@t", "commit", "-q", "-m", "legacy"], check=True)
    head = run([REAL_GIT, "-C", str(checkout), "rev-parse", "HEAD"],
               check=True).stdout.strip()
    run([REAL_GIT, "-C", str(checkout), "update-ref",
         "refs/remotes/origin/main", head], check=True)
    result = run_backup(harness, FAKE_GH_VISIBILITY="PRIVATE")
    assert result.returncode == 0, result.stderr
    assert not legacy.exists()
    tracked = run([REAL_GIT, "-C", str(checkout), "ls-files"],
                  check=True).stdout.splitlines()
    assert "skills/history.bundle" not in tracked
