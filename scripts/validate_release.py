"""Validate the tag, metadata, and notes for an smvp release."""

from __future__ import annotations

import argparse
from pathlib import Path

from .changelog_tools import extract_release_notes
from .changelog_tools import parse_version
from .changelog_tools import validate_changelog_collection
from .changelog_tools import validate_project_version

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Validate one release tag and optionally write GitHub outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    version = parse_version(args.tag)
    validate_project_version(PROJECT_ROOT, version.text)
    validate_changelog_collection(
        PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs", version.text
    )
    extract_release_notes(
        args.tag, PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs"
    )
    if args.github_output:
        args.github_output.write_text(
            f"version={version.text}\nprerelease={str(version.prerelease is not None).lower()}\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
