"""Write one smvp release's notes from the active or archived changelog."""

from __future__ import annotations

import argparse
from pathlib import Path

from .changelog_tools import extract_release_notes

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Extract release notes for a tag into an output Markdown file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        extract_release_notes(
            args.tag, PROJECT_ROOT / "CHANGELOG.md", PROJECT_ROOT / "changelogs"
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
