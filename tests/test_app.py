import io
import sys
from pathlib import Path

import argparse

import pytest

import smvp
from smvp.app import email_type
from smvp.app import font_family
from smvp.app import font_size
from smvp.app import process_args


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


@pytest.mark.parametrize("address", ["bad@", "user@@example.com", "x y@z.com", "@z.com"])
def test_email_type_rejects_invalid_addresses(address: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        email_type(address)


def test_process_args_parses_values_and_calls_task_runner(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("hello", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_task_runner(*, args: argparse.Namespace) -> None:
        captured["args"] = args

    monkeypatch.setattr("smvp.app.task_runner", fake_task_runner)
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

    process_args()
    args = captured["args"]
    assert isinstance(args, argparse.Namespace)
    assert args.recipient == "friend@example.com"
    assert args.subject == "Hello There"
    assert isinstance(args.file, io.TextIOWrapper)
    assert args.file.name == str(input_file)
    assert args.content_type == "html"
    assert args.font_family == "Verdana"
    assert args.font_size == "14"


def test_main_calls_process_args(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}

    def fake_process_args() -> None:
        called["value"] = True

    monkeypatch.setattr(smvp, "process_args", fake_process_args)
    smvp.main()
    assert called["value"] is True
