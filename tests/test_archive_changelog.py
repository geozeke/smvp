from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "archive_changelog.py"
SPEC = importlib.util.spec_from_file_location("archive_changelog", SCRIPT_PATH)
assert SPEC is not None
archive_changelog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = archive_changelog
SPEC.loader.exec_module(archive_changelog)


def test_patch_bump_does_not_archive_existing_old_sections(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    original = """## 0.4.3 (2026-05-09)

### Fixed

- Patch release.

## 0.4.2 (2026-05-08)

### Fixed

- Previous patch.

## [0.3.2][0.3.2] - 2026-04-17

### Changed

- Older minor entry.

[0.3.2]: https://example.test/releases/v0.3.2
"""
    changelog.write_text(original, encoding="utf-8")

    changed = archive_changelog.archive_changelog("v0.4.3", changelog, archive_dir)

    assert not changed
    assert changelog.read_text(encoding="utf-8") == original
    assert not archive_dir.exists()


def test_minor_bump_archives_old_sections_and_moves_links(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 0.5.0 (2026-05-09)

### Added

- Current minor entry.

## 0.4.2 (2026-05-08)

### Fixed

- Previous minor entry.

## [0.3.2][0.3.2] - 2026-04-17

### Changed

- Older linked entry using [pkg][pkg].

[0.3.2]: https://example.test/releases/v0.3.2
[pkg]: https://example.test/pkg
""",
        encoding="utf-8",
    )

    changed = archive_changelog.archive_changelog("0.5.0", changelog, archive_dir)

    assert changed
    active = changelog.read_text(encoding="utf-8")
    assert "## 0.5.0" in active
    assert "## 0.4.2" not in active
    assert "[pkg]:" not in active

    archive_04 = (archive_dir / "v0.4.x.md").read_text(encoding="utf-8")
    assert "## 0.4.2" in archive_04

    archive_03 = (archive_dir / "v0.3.x.md").read_text(encoding="utf-8")
    assert "## [0.3.2][0.3.2]" in archive_03
    assert "[0.3.2]: https://example.test/releases/v0.3.2" in archive_03
    assert "[pkg]: https://example.test/pkg" in archive_03


def test_force_archives_for_initial_cleanup(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 0.4.2 (2026-05-08)

### Fixed

- Current patch.

## 0.4.1 (2026-04-24)

### Changed

- Current minor patch.

## 0.3.2 (2026-04-17)

### Added

- Previous minor.
""",
        encoding="utf-8",
    )

    changed = archive_changelog.archive_changelog(
        "0.4.2",
        changelog,
        archive_dir,
        force=True,
    )

    assert changed
    active = changelog.read_text(encoding="utf-8")
    assert "## 0.4.2" in active
    assert "## 0.4.1" in active
    assert "## 0.3.2" not in active
    assert "## 0.3.2" in (archive_dir / "v0.3.x.md").read_text(encoding="utf-8")


def test_archived_releases_are_newest_first(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 0.5.0 (2026-05-09)

## 0.4.0 (2026-04-20)

## 0.4.2 (2026-05-08)

## 0.4.1 (2026-04-24)
""",
        encoding="utf-8",
    )

    archive_changelog.archive_changelog("0.5.0", changelog, archive_dir)

    archive = (archive_dir / "v0.4.x.md").read_text(encoding="utf-8")
    assert archive.index("## 0.4.2") < archive.index("## 0.4.1")
    assert archive.index("## 0.4.1") < archive.index("## 0.4.0")


def test_non_release_second_level_headings_stay_in_section(tmp_path: Path) -> None:
    changelog = tmp_path / "CHANGELOG.md"
    archive_dir = tmp_path / "changelogs"
    changelog.write_text(
        """## 0.5.0 (2026-05-09)

## 0.3.0 (2026-03-06)

## What's Changed

- Historical notes.
""",
        encoding="utf-8",
    )

    archive_changelog.archive_changelog("0.5.0", changelog, archive_dir)

    archive = (archive_dir / "v0.3.x.md").read_text(encoding="utf-8")
    assert "## What's Changed" in archive
    assert "- Historical notes." in archive
