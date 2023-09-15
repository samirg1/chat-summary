import pytest

from chat_summary.games import Connections


@pytest.fixture
def connections_game():
    return Connections()


@pytest.mark.parametrize(
    "message",
    (
        "🟪🟪🟪🟪\n🟪🟪🟪🟪\n🟪🟦🟪🟪\n🟪🟪🟪🟪",
        "🟩🟪🟪🟪\n🟪🟩🟦🟪\n🟪🟪🟦🟪\n🟪🟪🟪🟪",
        "🟪🟦🟪🟪\n🟪🟪🟩🟪\n🟪🟩🟪🟪\n🟪🟪🟪🟪\nWoohoo!!",
        "🟪🟪🟪🟪\n🟪🟦🟪🟪\n🟪🟪🟪🟪\n🟪🟪🟪🟪\nSome other text",
    ),
)
def test_valid_message_correct(message: str, connections_game: Connections):
    message = f"Connections \nPuzzle #123\n{message}"
    result = connections_game.analyse_message(message)
    assert result == (123, True, 4)


@pytest.mark.parametrize("number", (123, 12, 1, 1234, 200, 400))
def test_puzzle_number(number: int, connections_game: Connections):
    message = f"Connections \nPuzzle #{number}\n🟪🟪🟪🟪\n🟪🟪🟪🟪\n🟪🟦🟪🟪\n🟪🟪🟪🟪"
    result = connections_game.analyse_message(message)
    assert result == (number, True, 4)


@pytest.mark.parametrize("guesses", (4, 5, 6, 7))
def test_guesses(guesses: int, connections_game: Connections):
    message = f"Connections \nPuzzle #123" + "\n🟪🟪🟪🟪" * guesses
    result = connections_game.analyse_message(message)
    assert result == (123, True, guesses)


def test_valid_message_incorrect(connections_game: Connections):
    message = "Connections \nPuzzle #456\n🟪🟪🟪🟪\n🟪🟪🟪🟪\n🟪🟪🟪🟪\n🟪🟪🟪🟩"
    result = connections_game.analyse_message(message)
    assert result == (456, False, -1)


@pytest.mark.parametrize(
    "message",
    (
        "Invalid message format",
        "Connections \nPuzzle #12a",
        "Connections \nPuzzle #  12",
        "Connections \nPuzzle # 12",
        "Connections \nPuzzle #",
        "Connections \n",
    ),
)
def test_invalid_message(message: str, connections_game: Connections):
    result = connections_game.analyse_message(message)
    assert result is None
