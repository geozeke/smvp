import argparse
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import smvp
import smvp.app
import smvp.utilities
from smvp.app import email_type
from smvp.app import font_family
from smvp.app import font_size
from smvp.app import main


@pytest.mark.parametrize("value", ["2", "12", "100"])
def test_font_size_accepts_range(value: str) -> None:
    assert font_size(value) == value


@pytest.mark.parametrize("value", ["1", "101", "-1", "12.5", "abc"])
def test_font_size_rejects_invalid_inputs(value: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        font_size(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("trebuchet ms", "Trebuchet MS"),
        ("  sans-serif  ", "sans-serif"),
        ("COURIER NEW", "Courier New"),
    ],
)
def test_font_family_normalizes_supported_values(value: str, expected: str) -> None:
    assert font_family(value) == expected


def test_font_family_rejects_unknown_values() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        font_family("Papyrus")


@pytest.mark.parametrize(
    "address",
    [
        "a@b.co",
        "user.name+tag@example-domain.com",
        "test_123@example.org",
    ],
)
def test_email_type_accepts_valid_addresses(address: str) -> None:
    assert email_type(address) == address


@pytest.mark.parametrize(
    "address", ["bad@", "user@@example.com", "x y@z.com", "@z.com"]
)
def test_email_type_rejects_invalid_addresses(address: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        email_type(address)


def test_main_parses_values_and_calls_task_runner(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_task_runner(*, args: argparse.Namespace) -> None:
        captured["args"] = args

    monkeypatch.setattr(smvp.utilities, "task_runner", fake_task_runner)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smvp",
            "friend@example.com",
            "Hello There",
            str(input_file),
            "--content-type",
            "html",
            "--font_family",
            "verdana",
            "--font_size",
            "14",
        ],
    )

    main()
    args = captured["args"]
    assert isinstance(args, argparse.Namespace)
    assert args.recipient == "friend@example.com"
    assert args.subject == "Hello There"
    assert args.file == input_file
    assert args.content_type == "html"
    assert args.font_family == "Verdana"
    assert args.font_size == "14"


def test_package_main_exports_app_main() -> None:
    assert smvp.main is smvp.app.main


def test_module_main_delegates_to_app_main(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr("smvp.app.main", fake_main)

    runpy.run_module("smvp.__main__", run_name="__main__")

    assert called["value"] is True


def test_help_works_without_smtp_environment(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("SMVP_USER", raising=False)
    monkeypatch.delenv("SMVP_TOKEN", raising=False)
    monkeypatch.delenv("SMVP_SERVER", raising=False)
    monkeypatch.setattr(sys, "argv", ["smvp", "-h"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "usage: smvp" in captured.out


def test_version_works_without_smtp_environment(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("SMVP_USER", raising=False)
    monkeypatch.delenv("SMVP_TOKEN", raising=False)
    monkeypatch.delenv("SMVP_SERVER", raising=False)
    monkeypatch.setattr(sys, "argv", ["smvp", "--version"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert captured.out.startswith("smvp ")


def test_python_module_help_succeeds() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "smvp", "-h"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage: smvp" in result.stdout


def test_console_command_help_succeeds_when_available() -> None:
    command = shutil.which("smvp")
    if not command:
        pytest.skip("smvp console command is not available on PATH")

    result = subprocess.run(
        [command, "-h"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage: smvp" in result.stdout
