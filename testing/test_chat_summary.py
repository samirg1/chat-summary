import io
import subprocess
from typing import Any

import pytest

from chat_summary.chat_summary import main


class MockMessagesDB:
    def __init__(self, user: str, chat_name: str, silence: bool) -> None:
        self.user = user
        self.chat_name = chat_name
        self.silence = silence

    def get_messages_members_from_chat(self) -> tuple[list[Any], list[Any]]:
        return [], []


@pytest.fixture
def mock_messagesdb(monkeypatch: pytest.MonkeyPatch):
    value: dict[str, MockMessagesDB] = {}

    def mock(user: str, chat_name: str, silence: bool):
        obj = MockMessagesDB(user, chat_name, silence)
        value["obj"] = obj
        return obj

    monkeypatch.setattr("chat_summary.messages.MessagesDB", mock)

    return value


@pytest.fixture
def mock_check_call(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> dict[str, list[str]]:
    buffer: dict[str, list[str]] = {"args": []}

    def check_call(args: list[str]) -> None:
        if request.param:
            raise subprocess.CalledProcessError(1, "")
        buffer["args"] += args

    monkeypatch.setattr(subprocess, "check_call", check_call)

    return buffer


@pytest.mark.parametrize(
    ("user", "chat_name", "options"),
    (
        ("user1", "chat1", ["-W", "-C", "-N"]),
        ("user2", "chat2", ["--Wordle", "-C", "-N"]),
        ("user3", "chat1", ["-W", "--Connections", "-N"]),
        ("user1", "chat2", ["-C", "-N", "-W"]),
        ("user1", "chat2", ["-W", "-C", "-N", "-N", "-W"]),
        ("user1", "chat3", ["-W", "-C", "--Nerdle", "-N"]),
    ),
)
def test_chat_summary(user: str, chat_name: str, options: list[str], mock_messagesdb: dict[str, MockMessagesDB], capsys: pytest.CaptureFixture[str], mock_check_call: dict[str, list[str]]):
    main([user, chat_name, *options])
    assert capsys.readouterr().out == "🟥 no 'Connections' messages found 🟥\n🟥 no 'Nerdle' messages found 🟥\n🟥 no 'Wordle' messages found 🟥\n\n"
    assert mock_messagesdb["obj"].chat_name == chat_name
    assert mock_messagesdb["obj"].user == user
    assert mock_messagesdb["obj"].silence == False
    assert mock_check_call["args"] == []


@pytest.mark.parametrize(("options", "expected"), ((["--silence-contacts"], True), ([], False)))
def test_silence(options: str, expected: bool, mock_messagesdb: dict[str, MockMessagesDB]):
    main(["user", "chat_name", *options])
    assert mock_messagesdb["obj"].silence == expected


@pytest.mark.parametrize("option", ("-w", "-Nerdle", "-q", "-silence-contacts"))
def test_invalid_options(option: str, mock_messagesdb: dict[str, MockMessagesDB]):
    with pytest.raises(SystemExit):
        main(["user", "chat_name", option])


def expected_out_from_combination(options: list[str]) -> str:
    out = ""
    for option in sorted(options):
        name = "Connections" if option == "-C" else "Wordle" if option == "-W" else "Nerdle"
        out += f"🟥 no '{name}' messages found 🟥\n"

    return out + "\n"


@pytest.mark.parametrize(
    "options",
    (
        ["-W", "-C", "-N"],
        ["-W", "-C"],
        ["-W"],
        ["-C", "-N"],
        ["-N"],
        ["-C"],
        ["-W", "-N"],
        [],
    ),
)
def test_different_combination_of_options(options: list[str], mock_messagesdb: dict[str, MockMessagesDB], capsys: pytest.CaptureFixture[str]):
    main(["user", "chat_name", *options])
    assert capsys.readouterr().out == expected_out_from_combination(options)


@pytest.mark.parametrize("mock_check_call", [False], indirect=True)
def test_send_message_confirm(mock_messagesdb: dict[str, MockMessagesDB], mock_check_call: dict[str, list[str]], capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("Y"))
    main(["user", "chat_name", "-W", "--send-message"])
    assert capsys.readouterr().out == "are you sure you want to send the message? (Y): message sent successfully!\n"
    assert mock_check_call["args"]
    assert "chat_name" in mock_check_call["args"][2]


@pytest.mark.parametrize("mock_check_call", [False], indirect=True)
def test_send_message_decline(mock_messagesdb: dict[str, MockMessagesDB], mock_check_call: dict[str, list[str]], capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("not Y"))
    main(["user", "chat_name", "-W", "--send-message"])
    assert capsys.readouterr().out == "are you sure you want to send the message? (Y): "
    assert not mock_check_call["args"]
