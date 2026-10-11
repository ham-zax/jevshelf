"""Regression tests for the systemd backup timer installer.

Runs a fixture copy of scripts/install-backup-timer.sh from checkout
paths with spaces and literal '%' (a systemd "%" specifier character)
using a fake systemctl and fake HOME, and checks the emitted unit keeps
the backup script as one executable word. Paths with characters systemd
cannot represent in ExecStart ('$', '"', '\\', newline) must be refused
BEFORE any unit is written. Never touches real home directories, real
units, or the service manager. systemd-analyze verify is the
authoritative oracle where it can run; sandboxed environments without a
user manager skip that check after a control unit proves it unavailable.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = REPO_ROOT / "scripts" / "install-backup-timer.sh"

SUPPORTED_NAMES = ["my repo", "percent %n repo"]
REFUSED_NAMES = ["dollar $HOME", 'quote "q"', "backslash \\ end", "multi\nline"]


def run_installer_fixture(tmp_path, checkout_name):
    repo = tmp_path / checkout_name
    scripts = repo / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(INSTALLER, scripts / "install-backup-timer.sh")
    backup = scripts / "backup-skillshare.sh"
    shutil.copy(REPO_ROOT / "scripts" / "backup-skillshare.sh", backup)
    backup.chmod(0o755)
    fakebin = tmp_path / "fakebin"
    fakebin.mkdir()
    systemctl = fakebin / "systemctl"
    systemctl.write_text("#!/usr/bin/env bash\nexit 0\n")
    systemctl.chmod(0o755)
    home = tmp_path / "fakehome"
    home.mkdir()
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PATH"] = str(fakebin) + os.pathsep + env.get("PATH", "")
    proc = subprocess.run(
        ["bash", str(scripts / "install-backup-timer.sh")],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc, backup, home / ".config" / "systemd" / "user"


def read_exec_argv(service_text):
    """Read the single ExecStart line for the supported subset only: one
    double-quoted executable word plus arguments, undoing the '%%'
    literal-percent escape. Anything outside that shape fails loudly
    instead of modelling unsupported systemd behavior."""
    starts = [line for line in service_text.splitlines() if line.startswith("ExecStart=")]
    assert len(starts) == 1
    command = starts[0][len("ExecStart="):]
    assert command.startswith('"'), f"executable word must be quoted: {command!r}"
    end = command.find('"', 1)
    assert end > 1, f"unterminated executable word: {command!r}"
    word, rest = command[1:end], command[end + 1:]
    assert "\\" not in word, f"unsupported escape in executable word: {command!r}"
    assert re.search(r"(?<!%)%(?!%)", word) is None, f"bare % specifier: {command!r}"
    assert rest == " --if-due", f"unexpected ExecStart arguments: {command!r}"
    return word.replace("%%", "%"), ["--if-due"]


def systemd_analyze_usable(tmp_path):
    exe = shutil.which("systemd-analyze")
    if exe is None:
        return None
    control = tmp_path / "control.service"
    control.write_text(
        "[Unit]\nDescription=control\n[Service]\nType=oneshot\nExecStart=/bin/true\n"
    )
    proc = subprocess.run(
        [exe, "verify", "--man=no", str(control)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return exe if proc.returncode == 0 else None


@pytest.mark.parametrize("checkout_name", SUPPORTED_NAMES)
def test_execstart_points_at_backup_script(tmp_path, checkout_name):
    proc, backup, units = run_installer_fixture(tmp_path, checkout_name)
    assert proc.returncode == 0, proc.stderr
    service = (units / "jevshelf-backup.service").read_text()
    assert "Type=oneshot" in service
    exe, args = read_exec_argv(service)
    assert exe == str(backup)
    assert args == ["--if-due"]
    assert os.access(exe, os.X_OK)
    timer = (units / "jevshelf-backup.timer").read_text()
    assert "OnStartupSec=5min" in timer
    assert "OnUnitInactiveSec=48h" in timer


@pytest.mark.parametrize("checkout_name", REFUSED_NAMES)
def test_unsupported_checkout_path_refused_before_writing_units(tmp_path, checkout_name):
    proc, _, units = run_installer_fixture(tmp_path, checkout_name)
    assert proc.returncode != 0
    assert "refusing to write unit" in proc.stderr
    assert not (units / "jevshelf-backup.service").exists()
    assert not (units / "jevshelf-backup.timer").exists()


@pytest.mark.parametrize("checkout_name", SUPPORTED_NAMES)
def test_emitted_service_passes_systemd_analyze_verify(tmp_path, checkout_name):
    proc, _, units = run_installer_fixture(tmp_path, checkout_name)
    assert proc.returncode == 0, proc.stderr
    analyzer = systemd_analyze_usable(tmp_path)
    if analyzer is None:
        pytest.skip("systemd-analyze verify cannot run in this environment")
    service = units / "jevshelf-backup.service"
    proc = subprocess.run(
        [analyzer, "verify", "--man=no", str(service)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr + service.read_text()


def test_installer_is_valid_shell():
    bash = shutil.which("bash")
    assert bash is not None
    proc = subprocess.run(
        [bash, "-n", str(INSTALLER)], capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0, proc.stderr
