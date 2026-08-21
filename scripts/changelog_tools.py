"""Validate, archive, and extract smvp release changelog sections."""

from __future__ import annotations

import re

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from dataclasses import dataclass
from pathlib import Path

VERSION_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)(?:-(?P<label>beta|rc)\."
    r"(?P<number>0|[1-9]\d*))?$"
)
HEADING_RE = re.compile(
    r"^## \[(?P<label>Unreleased|(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\."
    r"(?:0|[1-9]\d*)(?:-(?:beta|rc)\.(?:0|[1-9]\d*))?)\]"
    r"(?: - (?P<date>\d{4}-\d{2}-\d{2}))?$"
)
GROUP_RE = re.compile(r"^### (?P<group>.+)$")
GROUPS = (
    "Breaking Changes",
    "Security",
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Performance",
    "Deployment & Operations",
    "Documentation",
    "Dependencies",
    "Reverted",
)
COMMIT_TITLE_RE = re.compile(
    r"^(?P<type>feat|change|deprecate|remove|fix|security|perf|deploy|docs|"
    r"build|chore|ci|refactor|style|test|revert)"
    r"(?:\([a-z0-9][a-z0-9._/-]*\))?(?:!)?: [^\s].*$"
)


@dataclass(frozen=True)
class Version:
    """Represent an smvp semantic release version.

    Parameters
    ----------
    text
        Canonical version text without a leading ``v``.
    major, minor, patch
        Numeric semantic-version components.
    prerelease
        Prerelease rank and number, or ``None`` for a stable version.
    """

    text: str
    major: int
    minor: int
    patch: int
    prerelease: tuple[int, int] | None

    def sort_key(self) -> tuple[int, int, int, int, int, int]:
        """Return a key that orders stable releases after prereleases.

        Returns
        -------
        tuple[int, int, int, int, int, int]
            Sortable semantic-version components.
        """
        if self.prerelease is None:
            return self.major, self.minor, self.patch, 1, 0, 0
        return self.major, self.minor, self.patch, 0, *self.prerelease


@dataclass(frozen=True)
class Section:
    """Represent one second-level changelog section.

    Parameters
    ----------
    label
        ``Unreleased`` or a canonical release version.
    text
        Complete Markdown content for the section.
    """

    label: str
    text: str

    @property
    def version(self) -> Version | None:
        """Return the parsed release version, if this is not Unreleased.

        Returns
        -------
        Version | None
            Parsed release version, or ``None`` for Unreleased.
        """
        return None if self.label == "Unreleased" else parse_version(self.label)


def parse_version(text: str) -> Version:
    """Parse a supported smvp SemVer version without a leading ``v``.

    Parameters
    ----------
    text
        Version in stable, beta, or release-candidate form.

    Returns
    -------
    Version
        Parsed semantic release version.

    Raises
    ------
    ValueError
        If the version is not supported by smvp's release workflow.
    """
    match = VERSION_RE.fullmatch(text.removeprefix("v"))
    if not match:
        raise ValueError(f"Expected X.Y.Z, X.Y.Z-beta.N, or X.Y.Z-rc.N: {text}")
    label = match.group("label")
    ranks = {"beta": 0, "rc": 1}
    prerelease = None if not label else (ranks[label], int(match.group("number")))
    return Version(
        match.group(),
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease,
    )


def validate_commit_title(title: str) -> None:
    """Validate a project Conventional Commit title.

    Parameters
    ----------
    title
        Pull-request title to validate.

    Raises
    ------
    ValueError
        If ``title`` does not use a supported Conventional Commit type.
    """
    if not COMMIT_TITLE_RE.fullmatch(title):
        raise ValueError(
            "Expected '<type>(optional-scope): description' using a documented "
            "Conventional Commit type"
        )


def split_changelog(text: str) -> tuple[str, list[Section]]:
    """Split changelog Markdown into its preamble and release sections.

    Parameters
    ----------
    text
        Full changelog Markdown.

    Returns
    -------
    tuple[str, list[Section]]
        Preamble text and ordered release sections.
    """
    lines = text.splitlines()
    headings = [index for index, line in enumerate(lines) if HEADING_RE.fullmatch(line)]
    if not headings:
        return text.strip(), []
    sections: list[Section] = []
    for position, start in enumerate(headings):
        end = headings[position + 1] if position + 1 < len(headings) else len(lines)
        match = HEADING_RE.fullmatch(lines[start])
        assert match is not None
        sections.append(
            Section(match.group("label"), "\n".join(lines[start:end]).strip())
        )
    return "\n".join(lines[: headings[0]]).strip(), sections


def format_changelog(preamble: str, sections: list[Section]) -> str:
    """Return normalized changelog Markdown with a terminal newline.

    Parameters
    ----------
    preamble
        Text preceding the first release section.
    sections
        Ordered release sections to render.

    Returns
    -------
    str
        Normalized Markdown ending in one newline.
    """
    parts = [preamble.strip(), *(section.text.strip() for section in sections)]
    return "\n\n".join(part for part in parts if part).strip() + "\n"


def archive_changelog(version: str, changelog_path: Path, archive_dir: Path) -> None:
    """Archive releases outside the target version's minor release line.

    Parameters
    ----------
    version
        Target release version.
    changelog_path
        Active changelog file.
    archive_dir
        Directory containing archived minor-version changelogs.
    """
    target = parse_version(version)
    preamble, sections = split_changelog(changelog_path.read_text(encoding="utf-8"))
    active: list[Section] = []
    archived: dict[tuple[int, int], list[Section]] = {}
    for section in sections:
        parsed = section.version
        if parsed is None or (parsed.major, parsed.minor) == (
            target.major,
            target.minor,
        ):
            active.append(section)
        else:
            archived.setdefault((parsed.major, parsed.minor), []).append(section)
    archive_dir.mkdir(parents=True, exist_ok=True)
    for (major, minor), moved in archived.items():
        path = archive_dir / f"v{major}.{minor}.x.md"
        existing = (
            split_changelog(path.read_text(encoding="utf-8"))[1]
            if path.exists()
            else []
        )
        merged = {
            section.label: section for section in [*existing, *moved] if section.version
        }
        ordered = sorted(
            merged.values(),
            key=lambda section: section.version.sort_key(),
            reverse=True,
        )
        archive_preamble = (
            f"# Changelog archive: {major}.{minor}.x\n\n"
            f"Archived smvp releases for the {major}.{minor}.x minor version line."
        )
        path.write_text(format_changelog(archive_preamble, ordered), encoding="utf-8")
    changelog_path.write_text(format_changelog(preamble, active), encoding="utf-8")


def extract_release_notes(tag: str, changelog_path: Path, archive_dir: Path) -> str:
    """Return one release section without its heading.

    Parameters
    ----------
    tag
        Release tag with a leading ``v``.
    changelog_path
        Active changelog file.
    archive_dir
        Directory containing archived minor-version changelogs.

    Returns
    -------
    str
        Release notes without the release heading.

    Raises
    ------
    ValueError
        If exactly one populated release section cannot be found.
    """
    version = parse_version(tag)
    candidates = [
        changelog_path,
        archive_dir / f"v{version.major}.{version.minor}.x.md",
    ]
    matches = [
        section
        for path in candidates
        if path.exists()
        for section in split_changelog(path.read_text(encoding="utf-8"))[1]
        if section.label == version.text
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one changelog section for {version.text}")
    notes = "\n".join(matches[0].text.splitlines()[1:]).strip()
    if not notes:
        raise ValueError(f"Release notes for {version.text} are empty")
    return notes + "\n"


def validate_changelog_collection(
    changelog_path: Path, archive_dir: Path, expected: str
) -> None:
    """Validate the active and archived changelog collection.

    Parameters
    ----------
    changelog_path
        Active changelog file.
    archive_dir
        Directory containing archived minor-version changelogs.
    expected
        Release version that must occur exactly once.

    Raises
    ------
    ValueError
        If formatting, ordering, categories, or release presence is invalid.
    """
    paths = [changelog_path, *sorted(archive_dir.glob("v*.x.md"))]
    seen: set[str] = set()
    for path in paths:
        preamble, sections = split_changelog(path.read_text(encoding="utf-8"))
        if not preamble.startswith("# Changelog") or not sections:
            raise ValueError(f"{path} is not a formatted changelog")
        versions = [section.version for section in sections]
        if any(version is None for version in versions):
            raise ValueError(f"{path} contains an Unreleased section")
        parsed = [version for version in versions if version]
        if parsed != sorted(parsed, key=Version.sort_key, reverse=True):
            raise ValueError(f"{path} is not newest first")
        for section, version in zip(sections, parsed, strict=True):
            if not HEADING_RE.fullmatch(section.text.splitlines()[0]).group("date"):
                raise ValueError(f"{section.label} is missing a release date")
            if section.label in seen:
                raise ValueError(f"Duplicate changelog section: {section.label}")
            seen.add(section.label)
            groups = [
                match.group("group")
                for line in section.text.splitlines()
                if (match := GROUP_RE.fullmatch(line))
            ]
            if any(group not in GROUPS for group in groups):
                raise ValueError(f"Unsupported changelog category in {section.label}")
            if groups != sorted(groups, key=GROUPS.index):
                raise ValueError(
                    f"Changelog categories are out of order in {section.label}"
                )
    if expected not in seen:
        raise ValueError(f"Changelog section for {expected} was not found")


def validate_project_version(project_root: Path, expected: str = "") -> str:
    """Require synchronized project and lockfile versions for a release.

    Parameters
    ----------
    project_root
        Repository root containing project metadata.
    expected
        Optional expected release version.

    Returns
    -------
    str
        Synchronized project version.

    Raises
    ------
    ValueError
        If project metadata and lockfile versions do not agree.
    """
    with (project_root / "pyproject.toml").open("rb") as handle:
        project_version = tomllib.load(handle)["project"]["version"]
    with (project_root / "uv.lock").open("rb") as handle:
        packages = tomllib.load(handle)["package"]
    locked = next(
        package["version"] for package in packages if package["name"] == "smvp"
    )
    if project_version != locked:
        raise ValueError("pyproject.toml and uv.lock versions must match")
    if expected and project_version != parse_version(expected).text:
        raise ValueError("Tag, pyproject.toml, and uv.lock versions must match")
    return project_version
