import os
import sqlite3
import sys
from os import listdir
from sqlite3 import connect
from typing import Any

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
def mock_connect_raise(monkeypatch: pytest.MonkeyPatch):
    buffer = {"err": ""}

    def cap(s: str):
        raise sqlite3.OperationalError

    monkeypatch.setattr(sqlite3, "connect", cap)

    return buffer


@pytest.fixture
def mock_listdir(monkeypatch: pytest.MonkeyPatch):
    buffer = {"err": ""}

    def cap(s: str) -> list[str]:
        return [listdir("/Users")[-1]]

    monkeypatch.setattr(os, "listdir", cap)

    return buffer


def test_failed_connection(capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        MessagesDB("definetly_not_a_real_user", "", False)
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "invalid user, user not found\n"


def test_operational_error(mock_connect_raise: dict[str, str], capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        MessagesDB(listdir("/Users")[-1], "", False)
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "could not connect to messages database, ensure you have the right permissions to access file\n"


def test_failed_chat_name(capture_std_err: dict[str, str]):
    with pytest.raises(SystemExit) as sys_exit:
        messagedb = MessagesDB(listdir("/Users")[-1], "definetly-not-a-chat-name", False)
        messagedb.get_messages_members_from_chat()
    assert sys_exit.value.code == 1
    assert capture_std_err["err"] == "chat name not found\n"


def test_addressbook_path(mock_listdir: dict[str, str]):
    m = MessagesDB(listdir("/Users")[-1], "definetly-not-a-chat-name", False)
    with pytest.raises(FileNotFoundError):
        m._get_addressbook_db_path()  # pyright: ignore[reportPrivateUsage]


@pytest.fixture
def mock_sql_connect(monkeypatch: pytest.MonkeyPatch):
    def f1(a: str):
        return connect(a)

    def f2(a: str):
        raise FileNotFoundError

    info = [f2, f1]

    def mock_connect(s: str):
        return info.pop()(s)

    monkeypatch.setattr(sqlite3, "connect", mock_connect)


def test_full():
    messagedb = MessagesDB(listdir("/Users")[-1], "Wordle Crew", False)
    messagedb.get_messages_members_from_chat()


def test_addressbook_fail(mock_sql_connect: Any, capture_std_err: dict[str, str]):
    messagedb = MessagesDB(listdir("/Users")[-1], "Wordle Crew", False)
    messagedb.get_messages_members_from_chat()
    assert capture_std_err["err"] == "unable to find contacts\n"
