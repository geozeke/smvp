"""Support the local dependency upgrade commit workflow.

This helper extracts first-order dependency names from project metadata,
extracts locked package versions from ``uv.lock``, compares before and
after snapshots, and renders the dependency upgrade commit message.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

try:
    from packaging.requirements import Requirement
except ModuleNotFoundError:  # pragma: no cover - fallback for no-dev envs
    Requirement = None


COMMIT_SUBJECT = "deps: Dependency Upgrades"
NAME_PATTERN = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
NORMALIZE_PATTERN = re.compile(r"[-_.]+")
OUTDATED_TREE_PATTERN = re.compile(
    r"^[\s│]*[├└]── (?P<name>[A-Za-z0-9_.-]+) v\S+ .*latest:"
)


def normalize_package_name(name: str) -> str:
    """Normalize a Python package name for comparison.

    Parameters
    ----------
    name : str
        Package name to normalize.

    Returns
    -------
    str
        PEP 503-style normalized package name.
    """
    return NORMALIZE_PATTERN.sub("-", name).lower()


def parse_requirement_name(requirement: str) -> str:
    """Extract a package name from a dependency requirement string.

    Parameters
    ----------
    requirement : str
        PEP 508 dependency requirement string.

    Returns
    -------
    str
        Normalized dependency package name.

    Raises
    ------
    ValueError
        If no package name can be found.
    """
    if Requirement:
        return normalize_package_name(Requirement(requirement).name)

    match = NAME_PATTERN.match(requirement)
    if not match:
        msg = f"Unable to parse dependency requirement: {requirement}"
        raise ValueError(msg)
    return normalize_package_name(match.group(1))


def load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML file.

    Parameters
    ----------
    path : Path
        TOML file path.

    Returns
    -------
    dict[str, Any]
        Parsed TOML data.
    """
    with path.open("rb") as file:
        return tomllib.load(file)


def first_order_dependency_names(pyproject_path: Path) -> set[str]:
    """Read first-order dependencies from project metadata.

    Parameters
    ----------
    pyproject_path : Path
        Path to ``pyproject.toml``.

    Returns
    -------
    set[str]
        Normalized first-order runtime and dependency-group names.
    """
    pyproject = load_toml(pyproject_path)
    dependencies = pyproject.get("project", {}).get("dependencies", [])

    dependency_groups = pyproject.get("dependency-groups", {})
    for group_dependencies in dependency_groups.values():
        dependencies.extend(group_dependencies)

    return {parse_requirement_name(dependency) for dependency in dependencies}


def locked_versions(lock_path: Path) -> dict[str, str]:
    """Read locked package versions from a uv lockfile.

    Parameters
    ----------
    lock_path : Path
        Path to ``uv.lock``.

    Returns
    -------
    dict[str, str]
        Normalized package names mapped to locked versions.
    """
    lock = load_toml(lock_path)
    versions: dict[str, str] = {}

    for package in lock.get("package", []):
        source = package.get("source", {})
        if isinstance(source, dict) and source.get("editable"):
            continue

        name = package.get("name")
        version = package.get("version")
        if name and version:
            versions[normalize_package_name(name)] = version

    return versions


def first_order_locked_versions(
    pyproject_path: Path,
    lock_path: Path,
) -> dict[str, str]:
    """Read locked versions for first-order dependencies only.

    Parameters
    ----------
    pyproject_path : Path
        Path to ``pyproject.toml``.
    lock_path : Path
        Path to ``uv.lock``.

    Returns
    -------
    dict[str, str]
        First-order dependency names mapped to locked versions.
    """
    dependency_names = first_order_dependency_names(pyproject_path)
    versions = locked_versions(lock_path)
    return {
        name: versions[name] for name in sorted(dependency_names) if name in versions
    }


def changed_versions(
    before_versions: dict[str, str],
    after_versions: dict[str, str],
) -> dict[str, tuple[str, str]]:
    """Compare first-order dependency snapshots.

    Parameters
    ----------
    before_versions : dict[str, str]
        Locked versions before an upgrade.
    after_versions : dict[str, str]
        Locked versions after an upgrade.

    Returns
    -------
    dict[str, tuple[str, str]]
        Changed dependency names mapped to old and new versions.
    """
    changes: dict[str, tuple[str, str]] = {}
    for name in sorted(before_versions):
        before_version = before_versions[name]
        after_version = after_versions.get(name)
        if after_version and after_version != before_version:
            changes[name] = (before_version, after_version)
    return changes


def render_commit_message(changes: dict[str, tuple[str, str]]) -> str:
    """Render the dependency upgrade commit message.

    Parameters
    ----------
    changes : dict[str, tuple[str, str]]
        Changed dependency names mapped to old and new versions.

    Returns
    -------
    str
        Full commit message, or an empty string when no changes exist.
    """
    if not changes:
        return ""

    lines = [COMMIT_SUBJECT, ""]
    for name, (old_version, new_version) in sorted(changes.items()):
        lines.append(f"- {name}: {old_version} -> {new_version}")
    return "\n".join(lines) + "\n"


def outdated_first_order_packages(
    dependency_names: set[str],
    tree_output: str,
) -> list[str]:
    """Read outdated first-order packages from uv tree output.

    Parameters
    ----------
    dependency_names : set[str]
        Normalized first-order dependency names.
    tree_output : str
        Output from ``uv tree --outdated --depth=1``.

    Returns
    -------
    list[str]
        Outdated first-order package names for ``uv sync
        --upgrade-package``.
    """
    packages: list[str] = []
    seen: set[str] = set()
    for line in tree_output.splitlines():
        match = OUTDATED_TREE_PATTERN.match(line)
        if not match:
            continue

        package_name = normalize_package_name(match.group("name"))
        if package_name not in dependency_names or package_name in seen:
            continue

        seen.add(package_name)
        packages.append(package_name)
    return packages


def snapshot(lock_path: Path) -> str:
    """Render a JSON snapshot of locked versions.

    Parameters
    ----------
    lock_path : Path
        Path to ``uv.lock``.

    Returns
    -------
    str
        JSON snapshot text.
    """
    versions = locked_versions(lock_path)
    return json.dumps(versions, indent=2, sort_keys=True) + "\n"


def build_commit_message(
    before_path: Path,
    pyproject_path: Path,
    lock_path: Path,
) -> str:
    """Build a commit message from a saved snapshot and current files.

    Parameters
    ----------
    before_path : Path
        JSON snapshot file created before the dependency upgrade.
    pyproject_path : Path
        Path to ``pyproject.toml``.
    lock_path : Path
        Path to ``uv.lock``.

    Returns
    -------
    str
        Full commit message, or an empty string when no direct
        dependency versions changed.
    """
    before_versions = json.loads(before_path.read_text(encoding="utf-8"))
    after_versions = first_order_locked_versions(pyproject_path, lock_path)
    return render_commit_message(changed_versions(before_versions, after_versions))


def write_snapshot(args: argparse.Namespace) -> int:
    """Write a locked-version snapshot.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Process exit code.
    """
    args.output.write_text(snapshot(args.lockfile), encoding="utf-8")
    return 0


def write_commit_message(args: argparse.Namespace) -> int:
    """Write a dependency upgrade commit message.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Process exit code. Returns ``1`` when no direct dependency
        versions changed.
    """
    message = build_commit_message(args.before, args.pyproject, args.lockfile)
    if not message:
        return 1

    args.output.write_text(message, encoding="utf-8")
    return 0


def write_outdated_packages(args: argparse.Namespace) -> int:
    """Write outdated first-order packages from uv tree output.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Process exit code.
    """
    dependency_names = first_order_dependency_names(args.pyproject)
    tree_output = sys.stdin.read()
    for package_name in outdated_first_order_packages(dependency_names, tree_output):
        print(package_name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Build dependency upgrade commit messages.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--lockfile", type=Path, default=Path("uv.lock"))
    snapshot_parser.add_argument("--output", type=Path, required=True)
    snapshot_parser.set_defaults(func=write_snapshot)

    message_parser = subparsers.add_parser(
        "message",
        help="Write a dependency upgrade commit message.",
    )
    message_parser.add_argument(
        "--pyproject",
        type=Path,
        default=Path("pyproject.toml"),
    )
    message_parser.add_argument(
        "--lockfile",
        type=Path,
        default=Path("uv.lock"),
    )
    message_parser.add_argument(
        "--before",
        type=Path,
        required=True,
        help="JSON snapshot created before the upgrade.",
    )
    message_parser.add_argument("--output", type=Path, required=True)
    message_parser.set_defaults(func=write_commit_message)

    outdated_parser = subparsers.add_parser(
        "outdated",
        help="Print outdated first-order packages from uv tree output.",
    )
    outdated_parser.add_argument(
        "--pyproject",
        type=Path,
        default=Path("pyproject.toml"),
    )
    outdated_parser.set_defaults(func=write_outdated_packages)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the dependency upgrade helper.

    Parameters
    ----------
    argv : list[str] | None
        Optional command-line arguments.

    Returns
    -------
    int
        Process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
