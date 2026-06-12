from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "dependency_upgrade_commit.py"
)
SPEC = importlib.util.spec_from_file_location("dependency_upgrade_commit", SCRIPT_PATH)
assert SPEC is not None
dependency_upgrade_commit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = dependency_upgrade_commit
SPEC.loader.exec_module(dependency_upgrade_commit)


def write_pyproject(path: Path) -> None:
    path.write_text(
        """[project]
name = "example"
dependencies = [
    "Rich>=14.0.0",
    "my_package[extra]>=1.0 ; python_version >= '3.10'",
]

[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "types-Requests>=2.0.0",
]
""",
        encoding="utf-8",
    )


def write_lock(path: Path) -> None:
    path.write_text(
        """version = 1

[[package]]
name = "example"
version = "0.1.0"
source = { editable = "." }

[[package]]
name = "rich"
version = "14.0.0"

[[package]]
name = "my-package"
version = "1.0.1"

[[package]]
name = "pytest"
version = "8.3.5"

[[package]]
name = "types-requests"
version = "2.32.0.20250515"

[[package]]
name = "transitive"
version = "5.0.0"
""",
        encoding="utf-8",
    )


def test_discovers_runtime_and_grouped_dependencies(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    write_pyproject(pyproject)

    names = dependency_upgrade_commit.first_order_dependency_names(pyproject)

    assert names == {"my-package", "pytest", "rich", "types-requests"}


def test_extracts_lockfile_versions_and_ignores_editable_package(
    tmp_path: Path,
) -> None:
    lockfile = tmp_path / "uv.lock"
    write_lock(lockfile)

    versions = dependency_upgrade_commit.locked_versions(lockfile)

    assert versions["rich"] == "14.0.0"
    assert versions["pytest"] == "8.3.5"
    assert "example" not in versions


def test_first_order_locked_versions_ignore_transitive_packages(
    tmp_path: Path,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "uv.lock"
    write_pyproject(pyproject)
    write_lock(lockfile)

    versions = dependency_upgrade_commit.first_order_locked_versions(
        pyproject, lockfile
    )

    assert versions == {
        "my-package": "1.0.1",
        "pytest": "8.3.5",
        "rich": "14.0.0",
        "types-requests": "2.32.0.20250515",
    }


def test_outdated_first_order_packages_ignore_transitive_packages() -> None:
    dependency_names = {"coverage", "pytest-cov", "rich"}
    tree_output = """Resolved 48 packages in 3ms
coverage[toml] v7.10.6 (group: dev) (latest: v7.11.3)
smvp v0.4.2
├── rich v14.0.0 (latest: v15.0.0)
│   └── pygments v2.19.0 (latest: v2.20.0)
├── pytest-cov v6.2.1 (latest: v7.1.0) (group: dev)
└── ruff v0.15.12
"""

    packages = dependency_upgrade_commit.outdated_first_order_packages(
        dependency_names,
        tree_output,
    )

    assert packages == ["coverage", "rich", "pytest-cov"]


def test_render_commit_message_uses_exact_subject_and_version_pairs() -> None:
    message = dependency_upgrade_commit.render_commit_message(
        {
            "pytest": ("8.3.5", "9.0.3"),
            "rich": ("14.0.0", "15.0.0"),
        }
    )

    assert message == (
        "deps: DEPS-See commit msg for list\n"
        "\n"
        "- pytest: 8.3.5 -> 9.0.3\n"
        "- rich: 14.0.0 -> 15.0.0\n"
    )


def test_transitive_only_lockfile_update_produces_no_commit_message() -> None:
    before_versions = {
        "pytest": "8.3.5",
        "rich": "14.0.0",
    }
    after_versions = {
        "pytest": "8.3.5",
        "rich": "14.0.0",
    }

    changes = dependency_upgrade_commit.changed_versions(
        before_versions, after_versions
    )

    assert changes == {}
    assert dependency_upgrade_commit.render_commit_message(changes) == ""
