from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "release_tags.sh"
pytestmark = pytest.mark.skipif(
    os.name == "nt",
    reason="release tag script uses Linux-only Bash tooling",
)


def copy_release_script(tmp_path: Path, version: str) -> Path:
    project_root = tmp_path / "project"
    script_dir = project_root / "scripts"
    script_dir.mkdir(parents=True)
    script_path = script_dir / "release_tags.sh"
    shutil.copy2(SCRIPT_PATH, script_path)
    (project_root / "pyproject.toml").write_text(
        f'[project]\nversion = "{version}"\n',
        encoding="utf-8",
    )
    return script_path


def write_fake_git(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    git_path = bin_dir / "git"
    git_path.write_text(
        '#!/usr/bin/env bash\necho "$@" >> "$FAKE_GIT_LOG"\nexit 42\n',
        encoding="utf-8",
    )
    git_path.chmod(0o755)
    return bin_dir


def run_release_script(
    script_path: Path,
    bin_dir: Path,
    git_log: Path,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["FAKE_GIT_LOG"] = str(git_log)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    return subprocess.run(
        ["bash", str(script_path), *args],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )


@pytest.mark.parametrize(
    "version",
    ["0.4.5-alpha.1", "0.4.5-beta.1", "0.4.5-rc.1"],
)
def test_latest_refuses_prerelease_before_git(
    tmp_path: Path,
    version: str,
) -> None:
    script_path = copy_release_script(tmp_path, version)
    bin_dir = write_fake_git(tmp_path)
    git_log = tmp_path / "git.log"

    result = run_release_script(script_path, bin_dir, git_log, "--latest")

    assert result.returncode == 1
    assert (
        result.stdout
        == f"Error: Refusing to move 'latest' for prerelease version '{version}'.\n"
        "Use 'just tag-release' for beta and release candidate versions.\n"
    )
    assert not git_log.exists()


def test_version_tag_allows_prerelease_to_reach_git(tmp_path: Path) -> None:
    script_path = copy_release_script(tmp_path, "0.4.5-rc.1")
    bin_dir = write_fake_git(tmp_path)
    git_log = tmp_path / "git.log"

    result = run_release_script(script_path, bin_dir, git_log)

    assert result.returncode == 42
    assert git_log.read_text(encoding="utf-8").startswith("-C ")
