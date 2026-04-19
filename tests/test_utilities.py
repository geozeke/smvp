import argparse
import io
from email import message_from_string

import pytest

from smvp import utilities


class DummySMTP:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.started_tls = False
        self.logged_in_with: tuple[str, str] | None = None
        self.sent: tuple[str, str, str] | None = None
        self.quit_called = False

    def starttls(self, context) -> None:  # noqa: ANN001
        self.started_tls = True

    def login(self, user: str, token: str) -> None:
        self.logged_in_with = (user, token)

    def sendmail(self, from_addr: str, to_addrs: str, msg: str) -> None:
        self.sent = (from_addr, to_addrs, msg)

    def quit(self) -> None:
        self.quit_called = True


class BrokenTextFile:
    name = "broken.txt"

    def __enter__(self) -> "BrokenTextFile":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None

    def read(self) -> str:
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")


def _build_args(*, content: str, font_family: str = "Courier New", font_size: int = 12):
    text_file = io.StringIO(content)
    text_file.name = "input.txt"  # type: ignore[attr-defined]
    return argparse.Namespace(
        recipient="friend@example.com",
        subject="Test Subject",
        file=text_file,
        font_family=font_family,
        font_size=font_size,
    )


def test_file_is_html_detects_common_cases() -> None:
    assert utilities.file_is_html("<!DOCTYPE html><html><body>ok</body></html>")
    assert utilities.file_is_html("<div>Hello</div>")
    assert not utilities.file_is_html("plain text with no tags")


def test_validate_environment_requires_all_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMVP_USER", "sender@example.com")
    monkeypatch.setenv("SMVP_TOKEN", "token")
    monkeypatch.setenv("SMVP_SERVER", "smtp.example.com")
    assert utilities.validate_environment() is True

    monkeypatch.delenv("SMVP_TOKEN")
    assert utilities.validate_environment() is False


def test_task_runner_exits_when_environment_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(utilities, "validate_environment", lambda: False)
    args = _build_args(content="hello")
    with pytest.raises(SystemExit) as excinfo:
        utilities.task_runner(args)
    assert excinfo.value.code == 1


def test_task_runner_exits_on_unicode_decode_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SMVP_USER", "sender@example.com")
    monkeypatch.setenv("SMVP_TOKEN", "token")
    monkeypatch.setenv("SMVP_SERVER", "smtp.example.com")
    args = argparse.Namespace(
        recipient="friend@example.com",
        subject="Test Subject",
        file=BrokenTextFile(),
        font_family="Courier New",
        font_size=12,
    )
    with pytest.raises(SystemExit) as excinfo:
        utilities.task_runner(args)
    assert excinfo.value.code == 1


def test_task_runner_sends_multipart_message_for_html_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SMVP_USER", "sender@example.com")
    monkeypatch.setenv("SMVP_TOKEN", "token")
    monkeypatch.setenv("SMVP_SERVER", "smtp.example.com")

    sent_servers: list[DummySMTP] = []

    def smtp_factory(host: str, port: int) -> DummySMTP:
        server = DummySMTP(host, port)
        sent_servers.append(server)
        return server

    monkeypatch.setattr(utilities.smtplib, "SMTP", smtp_factory)
    args = _build_args(content="<html><body><p>Hello</p></body></html>")
    utilities.task_runner(args)

    assert len(sent_servers) == 1
    server = sent_servers[0]
    assert server.host == "smtp.example.com"
    assert server.port == 587
    assert server.started_tls is True
    assert server.logged_in_with == ("sender@example.com", "token")
    assert server.quit_called is True
    assert server.sent is not None

    from_addr, to_addr, raw_message = server.sent
    assert from_addr == "sender@example.com"
    assert to_addr == "friend@example.com"

    parsed = message_from_string(raw_message)
    assert parsed["Subject"] == "Test Subject"
    assert parsed.is_multipart()
    parts = parsed.get_payload()
    assert len(parts) == 2
    assert parts[0].get_content_type() == "text/plain"
    assert parts[0].get_payload(decode=True).decode().strip() == "Hello"
    assert parts[1].get_content_type() == "text/html"
    html_payload = parts[1].get_payload(decode=True).decode()
    assert "font-family: Courier New !important" in html_payload
    assert "font-size: 12px !important" in html_payload


def test_task_runner_plaintext_uses_ansi_converter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMVP_USER", "sender@example.com")
    monkeypatch.setenv("SMVP_TOKEN", "token")
    monkeypatch.setenv("SMVP_SERVER", "smtp.example.com")

    class DummyConverter:
        instances: list["DummyConverter"] = []

        def __init__(self, dark_bg: bool) -> None:
            self.dark_bg = dark_bg
            self.called_with_full = False
            DummyConverter.instances.append(self)

        def convert(self, text: str, full: bool) -> str:
            assert text == "plain"
            self.called_with_full = full
            return (
                "<html><body><pre class='ansi2html-content' "
                "style='color: #AAAAAA'>plain</pre></body></html>"
            )

    sent_servers: list[DummySMTP] = []
    monkeypatch.setattr(utilities, "Ansi2HTMLConverter", DummyConverter)
    monkeypatch.setattr(
        utilities.smtplib,
        "SMTP",
        lambda host, port: sent_servers.append(DummySMTP(host, port)) or sent_servers[-1],
    )

    args = _build_args(content="plain", font_family="Verdana", font_size=14)
    utilities.task_runner(args)

    assert len(DummyConverter.instances) == 1
    converter = DummyConverter.instances[0]
    assert converter.dark_bg is False
    assert converter.called_with_full is True

    server = sent_servers[0]
    assert server.sent is not None
    parsed = message_from_string(server.sent[2])
    html_payload = parsed.get_payload()[1].get_payload(decode=True).decode()
    assert "color: #AAAAAA" not in html_payload
    assert "font-family: Verdana !important" in html_payload
    assert "font-size: 14px !important" in html_payload


def test_task_runner_prints_smtp_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("SMVP_USER", "sender@example.com")
    monkeypatch.setenv("SMVP_TOKEN", "token")
    monkeypatch.setenv("SMVP_SERVER", "smtp.example.com")

    class FailingSMTP(DummySMTP):
        def sendmail(self, from_addr: str, to_addrs: str, msg: str) -> None:
            raise RuntimeError("smtp send failed")

    sent_servers: list[FailingSMTP] = []

    def smtp_factory(host: str, port: int) -> FailingSMTP:
        server = FailingSMTP(host, port)
        sent_servers.append(server)
        return server

    monkeypatch.setattr(utilities.smtplib, "SMTP", smtp_factory)

    args = _build_args(content="<html><body><p>Hello</p></body></html>")
    utilities.task_runner(args)

    captured = capsys.readouterr()
    assert "smtp send failed" in captured.out
    assert sent_servers[0].quit_called is True
