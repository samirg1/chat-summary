import subprocess

import pytest

from chat_summary.send_message import send_message


@pytest.fixture
def mock_check_call(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> dict[str, list[str]]:
    buffer: dict[str, list[str]] = {"args": []}

    def check_call(args: list[str]) -> None:
        if request.param:
            raise subprocess.CalledProcessError(1, "")
        buffer["args"] += args

    monkeypatch.setattr(subprocess, "check_call", check_call)

    return buffer


def test_empty_message(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as sys_exit:
        send_message("", "")
    assert sys_exit.value.code == 1
    assert capsys.readouterr().err == "empty message, no message sent\n"


@pytest.mark.parametrize("mock_check_call", [False], indirect=True)
def test_working_messages(capsys: pytest.CaptureFixture[str], mock_check_call: dict[str, list[str]]) -> None:
    send_message("chat", "message")
    assert mock_check_call["args"] == ["osascript", "-e", f'tell application "Messages"\nsend "message" to chat "chat"\n end tell']
    assert capsys.readouterr().out == "message sent successfully!\n"


@pytest.mark.parametrize("mock_check_call", [True], indirect=True)
def test_error_case(capsys: pytest.CaptureFixture[str], mock_check_call: dict[str, list[str]]) -> None:
    with pytest.raises(SystemExit) as sys_exit:
        send_message("chat", "message")
    assert sys_exit.value.code == 1
    assert capsys.readouterr().err == "unable to send message to group chat\n"
