import pytest

from chat_summary.games import Nerdle


@pytest.fixture
def nerdle_game():
    return Nerdle()


@pytest.mark.parametrize("number", (1, 10, 30, 200, 800, 1000))
def test_valid_message_no_guesses(number: int, nerdle_game: Nerdle):
    message = f"nerdlegame {number} X/6"
    result = nerdle_game.analyse_message(message)
    assert result == (number, False, -1)


@pytest.mark.parametrize("guesses", (1, 2, 3, 4, 5, 6))
def test_valid_message_with_guesses(guesses: int, nerdle_game: Nerdle):
    message = f"nerdlegame 456 {guesses}/6"
    result = nerdle_game.analyse_message(message)
    assert result == (456, True, guesses)


@pytest.mark.parametrize(
    "message",
    (
        "nerdlegame ahhaahahahaha",
        "nerdlegame 12a X/6",
        "nerdlegame 789 7/6",
        "nerdlegame 789 0/6",
        "nerdlegam 789 2/6",
        "nerdlgame 789 2/6",
        "nerdlegame 7 2/4",
    ),
)
def test_invalid_message(message: str, nerdle_game: Nerdle):
    result = nerdle_game.analyse_message(message)
    assert result is None
