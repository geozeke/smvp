"""Prepare an smvp version, generated changelog, and synchronized lockfile."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from .changelog_tools import archive_changelog
from .changelog_tools import format_changelog
from .changelog_tools import parse_version
from .changelog_tools import split_changelog
from .changelog_tools import validate_changelog_collection
from .changelog_tools import validate_project_version

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    """Run a release command from the project root.

    Parameters
    ----------
    *args
        Command and arguments to execute.
    """
    subprocess.run(args, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    """Generate and validate the requested release version.

    Raises
    ------
    SystemExit
        If release preparation prerequisites are not satisfied.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    args = parser.parse_args()
    version = parse_version(args.version).text
    if subprocess.run(
        ("git", "status", "--porcelain"),
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout:
        parser.error("Working tree must be clean before preparing a release")
    generated = subprocess.run(
        ("git-cliff", "--unreleased", "--tag", f"v{version}"),
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    preamble, generated_sections = split_changelog(generated)
    if len(generated_sections) != 1 or generated_sections[0].label != version:
        parser.error("git-cliff did not generate exactly one target release section")
    _existing_preamble, existing_sections = split_changelog(
        (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    )
    retained = [section for section in existing_sections if section.label != version]
    (PROJECT_ROOT / "CHANGELOG.md").write_text(
        format_changelog(preamble, [generated_sections[0], *retained]),
        encoding="utf-8",
    )
    run("uv", "version", version, "--no-sync")
    run("uv", "lock")
    archive_changelog(
        version, PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs"
    )
    validate_project_version(PROJECT_ROOT, version)
    validate_changelog_collection(
        PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs", version
    )


if __name__ == "__main__":
    main()
