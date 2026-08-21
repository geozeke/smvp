"""Smoke-test an installed smvp distribution artifact."""

from __future__ import annotations

import subprocess
from importlib.metadata import version

import smvp
import smvp.app


def main() -> None:
    """Verify package imports, metadata, and the console entry point."""
    package_version = version("smvp")
    assert smvp.__file__
    assert smvp.app.__file__
    result = subprocess.run(
        ("smvp", "--version"), check=True, capture_output=True, text=True
    )
    assert result.stdout.strip() == f"smvp {package_version}"


if __name__ == "__main__":
    main()
