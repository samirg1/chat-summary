import pytest

from chat_summary.chat import MESSAGE, ChatMember, ChatSummary
from chat_summary.game import RESULT, Game


@pytest.fixture
def chat_member():
    return ChatMember("John", "1234567890")


def test_chat_member_initialization(chat_member: ChatMember):
    assert chat_member.name == "John"
    assert chat_member.number == "1234567890"
    assert isinstance(chat_member.game_scores, dict)
    assert len(chat_member.game_scores) == 0


def test_chat_member_representation(chat_member: ChatMember):
    assert repr(chat_member) == "(John, 1234567890)"


@pytest.fixture
def chat_summary():
    members = [ChatMember("John", "1234567890"), ChatMember("Alice", "9876543210"), ChatMember("Jake", "123")]
    games = (Game1(), Game2(), Game3())
    return ChatSummary(members, games)


class Game1(Game):
    prev = 1

    def _get_regex(self) -> str:
        return "Game1"

    def analyse_message(self, message: str) -> RESULT | None:
        res = RESULT(self.prev, True, 3)
        self._update_range(self.prev)
        self.prev += 1
        return res


class Game2(Game):
    prev = 1

    def _get_regex(self) -> str:
        return "Game2"

    def analyse_message(self, message: str) -> RESULT | None:
        if self.prev == 1:
            self.prev += 1
            return None
        if self.prev == 3:
            self.prev += 1
            return RESULT(self.prev, False)
        res = RESULT(self.prev, True, 2)
        self._update_range(self.prev)
        self.prev += 1
        return res


class Game3(Game):
    def _get_regex(self) -> str:
        return ""

    def analyse_message(self, message: str) -> RESULT | None:
        return None


@pytest.fixture
def get_captured_display(capfd: pytest.CaptureFixture[str], chat_summary: ChatSummary) -> str:
    messages = [
        MESSAGE("Game1 message", "1234567890"),
        MESSAGE("Game1 message", "1234567890"),
        MESSAGE("Game2 message", "9876543210"),
        MESSAGE("Game2 message", "9876543210"),
        MESSAGE("Game2 message", "9876543210"),
        MESSAGE("Game2 message", "9876543210"),
        MESSAGE("Invalid message", "5555555555"),
    ]
    chat_summary.populate(messages)

    return chat_summary.get_display()


@pytest.mark.parametrize("text", ("GAME1", "GAME2", "John", "Alice", "3/4", "2/2", "2.00", "3.00"))
def test_chat_summary_display_in(text: str, get_captured_display: str):
    assert text in get_captured_display


@pytest.mark.parametrize("text", ("Game1", "Game2", "Jake"))
def test_chat_summary_display_not_in(text: str, get_captured_display: str):
    assert text not in get_captured_display
