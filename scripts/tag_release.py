"""Validate, create, and push the current annotated smvp release tag."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .changelog_tools import extract_release_notes
from .changelog_tools import validate_changelog_collection
from .changelog_tools import validate_project_version

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    """Run Git from the project root and return stripped standard output.

    Parameters
    ----------
    *args
        Git arguments to execute.

    Returns
    -------
    str
        Command standard output without surrounding whitespace.
    """
    return subprocess.run(
        ("git", *args), cwd=PROJECT_ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def main() -> None:
    """Validate release state, create the annotated tag, and push it.

    Raises
    ------
    SystemExit
        If the branch, worktree, metadata, or tag state is invalid.
    """
    if git("branch", "--show-current") != "main":
        raise SystemExit("Release tags can only be created from main")
    if git("status", "--porcelain=v1", "--untracked-files=all"):
        raise SystemExit("Working tree must be clean before tagging a release")
    git("fetch", "origin", "main", "--tags")
    if git("rev-parse", "main") != git("rev-parse", "origin/main"):
        raise SystemExit("Local main must exactly match origin/main")
    version = validate_project_version(PROJECT_ROOT, "")
    validate_changelog_collection(
        PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs", version
    )
    tag = f"v{version}"
    extract_release_notes(
        tag, PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs"
    )
    if git("tag", "--list", tag) or git(
        "ls-remote", "--tags", "origin", f"refs/tags/{tag}"
    ):
        raise SystemExit(f"Release tag {tag} already exists")
    git("tag", "--annotate", tag, "--message", f"smvp {tag}")
    git("push", "origin", f"refs/tags/{tag}")


if __name__ == "__main__":
    main()
