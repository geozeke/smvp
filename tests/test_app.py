import argparse

import pytest

from smvp.app import email_type
from smvp.app import font_family
from smvp.app import font_size


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
