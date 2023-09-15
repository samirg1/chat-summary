import os
import sqlite3
import sys
from typing import Any

import pandas
import pytest

from chat_summary.messages import MessagesDB


@pytest.fixture
def capture_std_err(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    buffer = {"err": ""}

    def cap(s: str):
        buffer["err"] += s

    monkeypatch.setattr(sys.stderr, "write", cap)

    return buffer


@pytest.fixture
def mock_sql_connect(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest):
    def f0():
        raise sqlite3.OperationalError

    def f1():
        return "connections obj"

    funcs = {0: f0, 1: f1}

    info = [funcs[n] for n in reversed(request.param)]

    def mock_connect(s: str):
        return info.pop()()

    monkeypatch.setattr(sqlite3, "connect", mock_connect)


@pytest.fixture
def mock_listdir(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest):
    r: list[list[str]] = request.param[::-1]

    def list_dir(_: str) -> list[str]:
        return r.pop()

    monkeypatch.setattr(os, "listdir", list_dir)


@pytest.fixture
def mock_read_sql_query(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest):
    data = request.param[::-1]

    def read_sql(*_: Any):
        datum = data.pop()
        if isinstance(datum, BaseException):
            raise datum
        return datum

    monkeypatch.setattr(pandas, "read_sql_query", read_sql)


class MockObj:
    def __init__(self, empty: bool = False, getitem: dict[str, Any] | None = None) -> None:
        self.is_empty = empty
        self.getitem = getitem

    @property
    def empty(self) -> bool:
        return self.is_empty
    
    def __getitem__(self, value: str): # type: ignore
        return self.getitem[value] # type: ignore


@pytest.mark.parametrize("mock_listdir", ([[""]]), indirect=True)
def test_no_user_found(mock_listdir: None, capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        MessagesDB("user", "", False)
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "invalid user, user not found\n"


@pytest.mark.parametrize(("mock_listdir", "mock_sql_connect"), [([["user"]], [0])], indirect=True)
def test_operational_error(mock_listdir: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        MessagesDB("user", "", False)
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "could not connect to messages database, ensure you have the right permissions to access file\n"


@pytest.mark.parametrize(
    ("mock_listdir", "mock_read_sql_query", "mock_sql_connect"),
    [
        ([["user"]], [MockObj(True)], [1]),
    ],
    indirect=True,
)
def test_failed_chat_name(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    messagedb = MessagesDB("user", "chat-name", False)
    with pytest.raises(SystemExit) as sys_exit:
        messagedb.get_messages_members_from_chat()
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "chat name not found\n"


@pytest.mark.parametrize(
    ("mock_listdir", "mock_sql_connect"),
    [
        ([["user"], []], [1]),
    ],
    indirect=True,
)
def test_addressbook_path_not_found(mock_listdir: None, mock_sql_connect: None):
    m = MessagesDB("user", "", False)
    with pytest.raises(FileNotFoundError):
        m._get_addressbook_db_path()  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize(
    ("mock_listdir", "mock_sql_connect"),
    [
        ([["user"], ["x"], ["AddressBook-v22.abcddb"]], [1]),
    ],
    indirect=True,
)
def test_addressbook_path(mock_listdir: None, mock_sql_connect: None):
    m = MessagesDB("user", "", False)
    assert m._get_addressbook_db_path() == "/Users/user/Library/Application Support/AddressBook/Sources/x/AddressBook-v22.abcddb"  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize(
    ("mock_listdir", "mock_read_sql_query", "mock_sql_connect"),
    [
        ([["user"], []], [MockObj(getitem={"ROWID": [0]}), MockObj(getitem={"id": []}), SystemExit()], [1]),
    ],
    indirect=True,
)
def test_addressbook_fail(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    m = MessagesDB("user", "1", False)
    with pytest.raises(SystemExit):
        m.get_messages_members_from_chat()
    assert capture_std_err["err"] == "unable to find contacts\n"


@pytest.mark.parametrize(
    ("mock_listdir", "mock_read_sql_query", "mock_sql_connect"),
    [
        ([["user"], []], [MockObj(getitem={"ROWID": [0]}), MockObj(getitem={"id": []}), SystemExit()], [1]),
    ],
    indirect=True,
)
def test_addressbook_fail_silenced(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    m = MessagesDB("user", "1", True)
    with pytest.raises(SystemExit):
        m.get_messages_members_from_chat()
    assert capture_std_err["err"] == ""
