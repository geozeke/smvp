from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "extract_release_notes.sh"
)


def copy_release_notes_script(tmp_path: Path, changelog_text: str) -> Path:
    project_root = tmp_path / "project"
    script_dir = project_root / "scripts"
    script_dir.mkdir(parents=True)
    script_path = script_dir / "extract_release_notes.sh"
    shutil.copy2(SCRIPT_PATH, script_path)
    (project_root / "CHANGELOG.md").write_text(changelog_text, encoding="utf-8")
    return script_path


def run_release_notes_script(
    script_path: Path,
    tag: str,
    output_path: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(script_path), tag, str(output_path)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_extract_release_notes_preserves_non_release_second_level_headings(
    tmp_path: Path,
) -> None:
    script_path = copy_release_notes_script(
        tmp_path,
        """# Changelog

## 0.4.5 (2026-06-12)

## What's Changed

- Keep this text.

## 0.4.4 (2026-06-01)

- Exclude this text.
""",
    )
    output_path = tmp_path / "release-notes.md"

    result = run_release_notes_script(script_path, "v0.4.5", output_path)

    assert result.returncode == 0
    notes = output_path.read_text(encoding="utf-8")
    assert "## What's Changed" in notes
    assert "- Keep this text." in notes
    assert "## 0.4.4" not in notes


def test_extract_release_notes_falls_back_to_minor_archive(tmp_path: Path) -> None:
    script_path = copy_release_notes_script(
        tmp_path,
        """# Changelog

## 0.5.0 (2026-06-12)

- Current release.
""",
    )
    archive_dir = script_path.parents[1] / "changelogs"
    archive_dir.mkdir()
    (archive_dir / "v0.4.x.md").write_text(
        """# Archived Changelog

## 0.4.5 (2026-06-01)

- Archived release.
""",
        encoding="utf-8",
    )
    output_path = tmp_path / "release-notes.md"

    result = run_release_notes_script(script_path, "v0.4.5", output_path)

    assert result.returncode == 0
    assert "- Archived release." in output_path.read_text(encoding="utf-8")
