"""Tests for SemVer changelog parsing, validation, and note extraction."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.changelog_tools import extract_release_notes
from scripts.changelog_tools import parse_version
from scripts.changelog_tools import validate_changelog_collection


def test_parse_version_orders_prereleases_before_stable() -> None:
    """Require beta, RC, and stable releases to use SemVer ordering."""
    versions = [
        parse_version("0.5.0"),
        parse_version("0.5.0-beta.1"),
        parse_version("0.5.0-rc.1"),
    ]

    assert sorted(versions, key=lambda version: version.sort_key()) == [
        versions[1],
        versions[2],
        versions[0],
    ]


def test_extract_and_validate_archived_release_notes(tmp_path: Path) -> None:
    """Find a formatted release in its corresponding minor archive."""
    changelog = tmp_path / "CHANGELOG.md"
    archives = tmp_path / "changelogs"
    archives.mkdir()
    changelog.write_text(
        "# Changelog\n\n## [0.5.0] - 2026-08-21\n\n"
        "[View release tag](https://example.test/v0.5.0)\n\n### Added\n\n- Current.\n",
        encoding="utf-8",
    )
    (archives / "v0.4.x.md").write_text(
        "# Changelog archive: 0.4.x\n\n"
        "Archived smvp releases for the 0.4.x minor version line.\n\n"
        "## [0.4.7] - 2026-08-20\n\n"
        "[View release tag](https://example.test/v0.4.7)\n\n### Fixed\n\n- Archived.\n",
        encoding="utf-8",
    )

    validate_changelog_collection(changelog, archives, "0.4.7")

    assert extract_release_notes("v0.4.7", changelog, archives) == (
        "[View release tag](https://example.test/v0.4.7)\n\n### Fixed\n\n- Archived.\n"
    )


def test_validate_rejects_unknown_changelog_category(tmp_path: Path) -> None:
    """Reject categories outside the public release-note vocabulary."""
    changelog = tmp_path / "CHANGELOG.md"
    archives = tmp_path / "changelogs"
    archives.mkdir()
    changelog.write_text(
        "# Changelog\n\n## [0.4.7] - 2026-08-21\n\n### Other\n\n- No.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported changelog category"):
        validate_changelog_collection(changelog, archives, "0.4.7")
