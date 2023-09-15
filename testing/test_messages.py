import os
import sqlite3
import sys
from typing import Any

import pandas
import pytest

from chat_summary.chat import MESSAGE
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

    def f2():
        class f:
            def close(self) -> None:
                pass

        return f()

    funcs = {0: f0, 1: f1, 2: f2}

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
    class _iloc:
        def __init__(self, len: int) -> None:
            self.len = len

        def __getitem__(self, v: tuple[int, slice]):
            if self.len == 3:
                return f"{v[0]}", f"{v[0]}", "0123"
            return f"{v[0]}", "0123"

    def __init__(self, *, getitem: dict[str, Any] | None = None, len: int = 3) -> None:
        self.getitem = getitem
        self.len = len
        self.iloc = self._iloc(len)

    def __getitem__(self, value: str):  # type: ignore
        return self.getitem[value]  # type: ignore

    def __len__(self) -> int:
        return self.len


@pytest.mark.parametrize("mock_listdir", ([[""]]), indirect=True)
def test_no_user_found(mock_listdir: None, capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        MessagesDB("user", "", False)
    assert sys_exit.value.code == 1
    assert capture_std_err["err"].startswith("user not found, user should be one of: ")


@pytest.mark.parametrize(("mock_listdir", "mock_sql_connect"), [([["user"]], [0])], indirect=True)
def test_operational_error(mock_listdir: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        MessagesDB("user", "", False)
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "could not connect to messages database, ensure you have the right permissions to access file\n"


@pytest.mark.parametrize(
    ("mock_listdir", "mock_read_sql_query", "mock_sql_connect"),
    [
        ([["user"]], [MockObj(getitem={"ROWID": [], "display_name": []})], [1]),
    ],
    indirect=True,
)
def test_failed_chat_name(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    messagedb = MessagesDB("user", "chat-name", False)
    with pytest.raises(SystemExit) as sys_exit:
        messagedb.get_messages_members_from_chat()
    assert sys_exit.value.code == 1
    assert capture_std_err["err"].startswith("chat name not found, should be one of: ")


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
        ([["user"], []], [MockObj(getitem={"ROWID": [0], "display_name": ["1"]}), MockObj(getitem={"id": []}), SystemExit()], [1]),
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
        ([["user"], []], [MockObj(getitem={"ROWID": [0], "display_name": ["1"]}), MockObj(getitem={"id": []}), SystemExit()], [1]),
    ],
    indirect=True,
)
def test_addressbook_fail_silenced(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    m = MessagesDB("user", "1", True)
    with pytest.raises(SystemExit):
        m.get_messages_members_from_chat()
    assert capture_std_err["err"] == ""


@pytest.mark.parametrize(
    ("mock_listdir", "mock_read_sql_query", "mock_sql_connect"),
    [
        ([["user"], ["x"], ["AddressBook-v22.abcddb"]], [MockObj(getitem={"id": ["+61123", "345"]}), MockObj(getitem={"id": ["0123", "345"]})], [1, 2]),
    ],
    indirect=True,
)
def test_chat_members(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None):
    m = MessagesDB("user", "1", False)
    members = m._get_chat_members(1)  # pyright: ignore[reportPrivateUsage]
    assert members[0].name == "0" and members[0].number == "+61123"
    assert members[1].name == "345" and members[1].number == "345"
    assert members[2].name == "user" and members[2].number == ""


@pytest.mark.parametrize(
    ("mock_listdir", "mock_read_sql_query", "mock_sql_connect"),
    [
        ([["user"], []], [MockObj(getitem={"ROWID": [0], "display_name": ["1"]}), MockObj(getitem={"id": []}), MockObj(len=2)], [1]),
    ],
    indirect=True,
)
def test_full_runthrough(mock_listdir: None, mock_read_sql_query: None, mock_sql_connect: None, capture_std_err: dict[str, str]):
    m = MessagesDB("user", "1", False)

    res = m.get_messages_members_from_chat()
    assert list(res[0]) == [MESSAGE("0", "0123"), MESSAGE("1", "0123")]
    assert len(res[1]) == 1 and res[1][0].name == "user" and res[1][0].number == ""
